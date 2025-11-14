import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, isAdmin } = useAuth();
  const { t } = useLanguage();

  const getLevelBadgeClass = (level) => {
    switch (level) {
      case 'Gold':
        return 'badge-gold';
      case 'Silver':
        return 'badge-silver';
      default:
        return 'badge-bronze';
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg">
      <div className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8 animate-fadeIn">
          <h2 className="text-3xl font-bold mb-2">
            {t('dashboard')}
          </h2>
          <p className="text-gray-400">مرحباً بك في حمّادي ستور</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Balance Card */}
          <div className="card bg-gradient-to-br from-blue-600 to-blue-800 animate-fadeIn">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm mb-1">{t('balance')}</p>
                <p className="text-3xl font-bold">{user?.balance?.toFixed(2)} د.ل</p>
              </div>
              <div className="text-5xl opacity-20">💰</div>
            </div>
          </div>

          {/* Total Spent Card */}
          <div className="card bg-gradient-to-br from-purple-600 to-purple-800 animate-fadeIn" style={{ animationDelay: '0.1s' }}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm mb-1">{t('totalSpent')}</p>
                <p className="text-3xl font-bold">{user?.total_spent?.toFixed(2)} د.ل</p>
              </div>
              <div className="text-5xl opacity-20">📊</div>
            </div>
          </div>

          {/* Account Level Card */}
          <div className="card bg-gradient-to-br from-orange-600 to-orange-800 animate-fadeIn" style={{ animationDelay: '0.2s' }}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100 text-sm mb-1">{t('accountLevel')}</p>
                <p className="text-3xl font-bold">{t(user?.level?.toLowerCase() || 'bronze')}</p>
              </div>
              <div className="text-5xl opacity-20">
                {user?.level === 'Gold' ? '🥇' : user?.level === 'Silver' ? '🥈' : '🥉'}
              </div>
            </div>
          </div>
        </div>

        {/* Recharge Button */}
        <div className="card mb-8 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 cursor-pointer transition-all animate-fadeIn" 
             style={{ animationDelay: '0.3s' }}
             onClick={() => navigate('/recharge')}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold mb-1">{t('recharge')}</h3>
              <p className="text-green-100">{t('clickToRecharge')}</p>
            </div>
            <div className="text-5xl">⚡</div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <button
            onClick={() => navigate('/new-order')}
            className="card hover:scale-105 transition-transform cursor-pointer bg-gradient-to-br from-primary to-blue-700 animate-fadeIn"
            style={{ animationDelay: '0.4s' }}
          >
            <div className="flex items-center justify-between">
              <div className="text-right">
                <h3 className="text-2xl font-bold mb-1">{t('newOrder')}</h3>
                <p className="text-blue-100">ابدأ طلب جديد الآن</p>
              </div>
              <div className="text-5xl">🛒</div>
            </div>
          </button>

          <button
            onClick={() => navigate('/orders')}
            className="card hover:scale-105 transition-transform cursor-pointer bg-gradient-to-br from-indigo-600 to-indigo-800 animate-fadeIn"
            style={{ animationDelay: '0.5s' }}
          >
            <div className="flex items-center justify-between">
              <div className="text-right">
                <h3 className="text-2xl font-bold mb-1">{t('myOrders')}</h3>
                <p className="text-indigo-100">تتبع طلباتك</p>
              </div>
              <div className="text-5xl">📦</div>
            </div>
          </button>
        </div>

        {/* Admin Panel Button */}
        {isAdmin && (
          <button
            onClick={() => navigate('/admin')}
            className="w-full card hover:scale-105 transition-transform cursor-pointer bg-gradient-to-br from-red-600 to-red-800 animate-fadeIn"
            style={{ animationDelay: '0.6s' }}
          >
            <div className="flex items-center justify-between">
              <div className="text-right">
                <h3 className="text-2xl font-bold mb-1">{t('adminPanel')}</h3>
                <p className="text-red-100">إدارة الموقع والمستخدمين</p>
              </div>
              <div className="text-5xl">⚙️</div>
            </div>
          </button>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
