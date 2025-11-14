import requests
from models import APIProvider, Service, Order, db
from datetime import datetime

class SMSAPIService:
    """Service for interacting with external SMM API providers"""
    
    @staticmethod
    def get_active_provider():
        """Get the highest priority active provider"""
        return APIProvider.query.filter_by(is_active=True).order_by(APIProvider.priority.desc()).first()
    
    @staticmethod
    def fetch_services(provider_id):
        """Fetch services from an API provider"""
        provider = APIProvider.query.get(provider_id)
        if not provider or not provider.is_active:
            return {'error': 'Provider not found or inactive'}
        
        try:
            response = requests.post(
                provider.api_url,
                data={
                    'key': provider.api_key,
                    'action': 'services'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'API returned status code {response.status_code}'}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def create_order(order_id):
        """Submit an order to the external API provider"""
        order = Order.query.get(order_id)
        if not order:
            return {'error': 'Order not found'}
        
        service = Service.query.get(order.service_id)
        if not service or not service.api_provider:
            return {'error': 'Service or provider not configured'}
        
        provider = service.api_provider
        if not provider.is_active:
            return {'error': 'Provider is inactive'}
        
        try:
            response = requests.post(
                provider.api_url,
                data={
                    'key': provider.api_key,
                    'action': 'add',
                    'service': service.external_service_id,
                    'link': order.link,
                    'quantity': order.quantity
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'order' in result:
                    order.external_order_id = str(result['order'])
                    order.status = 'processing'
                    db.session.commit()
                    return {'success': True, 'external_order_id': result['order']}
                else:
                    return {'error': result.get('error', 'Unknown error')}
            else:
                return {'error': f'API returned status code {response.status_code}'}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def check_order_status(order_id):
        """Check the status of an order from the external API"""
        order = Order.query.get(order_id)
        if not order or not order.external_order_id:
            return {'error': 'Order not found or not submitted to API'}
        
        service = Service.query.get(order.service_id)
        if not service or not service.api_provider:
            return {'error': 'Service or provider not configured'}
        
        provider = service.api_provider
        
        try:
            response = requests.post(
                provider.api_url,
                data={
                    'key': provider.api_key,
                    'action': 'status',
                    'order': order.external_order_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Update order status
                if 'status' in result:
                    status_map = {
                        'Pending': 'pending',
                        'In progress': 'processing',
                        'Processing': 'processing',
                        'Completed': 'completed',
                        'Partial': 'partial',
                        'Canceled': 'canceled',
                        'Cancelled': 'canceled'
                    }
                    order.status = status_map.get(result['status'], 'processing')
                    
                if 'start_count' in result:
                    order.start_count = result['start_count']
                    
                if 'remains' in result:
                    order.remains = result['remains']
                
                order.updated_at = datetime.utcnow()
                db.session.commit()
                
                return {'success': True, 'status': order.status}
            else:
                return {'error': f'API returned status code {response.status_code}'}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def sync_services_from_provider(provider_id, category_mapping):
        """
        Sync services from an external provider
        category_mapping: dict mapping external category names to internal category IDs
        """
        services_data = SMSAPIService.fetch_services(provider_id)
        
        if 'error' in services_data:
            return {'error': services_data['error']}
        
        synced_count = 0
        
        for service_data in services_data:
            try:
                # Map to internal category
                external_category = service_data.get('category', '')
                category_id = category_mapping.get(external_category)
                
                if not category_id:
                    continue
                
                # Check if service already exists
                existing_service = Service.query.filter_by(
                    api_provider_id=provider_id,
                    external_service_id=str(service_data['service'])
                ).first()
                
                if existing_service:
                    # Update existing service
                    existing_service.name_en = service_data['name']
                    existing_service.name_ar = service_data['name']
                    existing_service.price_per_1000 = float(service_data['rate'])
                    existing_service.min_quantity = int(service_data.get('min', 100))
                    existing_service.max_quantity = int(service_data.get('max', 100000))
                else:
                    # Create new service
                    new_service = Service(
                        category_id=category_id,
                        name_ar=service_data['name'],
                        name_en=service_data['name'],
                        price_per_1000=float(service_data['rate']),
                        min_quantity=int(service_data.get('min', 100)),
                        max_quantity=int(service_data.get('max', 100000)),
                        api_provider_id=provider_id,
                        external_service_id=str(service_data['service'])
                    )
                    db.session.add(new_service)
                
                synced_count += 1
            except Exception as e:
                print(f"Error syncing service: {e}")
                continue
        
        db.session.commit()
        return {'success': True, 'synced_count': synced_count}
