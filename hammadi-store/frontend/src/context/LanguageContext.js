import React, { createContext, useState, useContext, useEffect } from 'react';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

const translations = {
  ar: {
    // Header
    appName: 'حمّادي ستور',
    appNameEn: 'Hammadi Store',
    
    // Auth
    login: 'تسجيل الدخول',
    register: 'تسجيل جديد',
    email: 'البريد الإلكتروني',
    password: 'كلمة المرور',
    logout: 'تسجيل الخروج',
    
    // Dashboard
    dashboard: 'لوحة التحكم',
    balance: 'الرصيد الحالي',
    totalSpent: 'إجمالي الإنفاق',
    accountLevel: 'مستوى الحساب',
    newOrder: 'طلب جديد',
    myOrders: 'طلباتي',
    recharge: 'شحن الرصيد',
    clickToRecharge: 'للشحن اضغط هنا',
    
    // Orders
    selectCategory: 'اختر الفئة',
    selectService: 'اختر الخدمة',
    enterLink: 'أدخل الرابط',
    enterQuantity: 'أدخل الكمية',
    quantity: 'الكمية',
    price: 'السعر',
    totalPrice: 'السعر الإجمالي',
    submitOrder: 'إرسال الطلب',
    orderStatus: 'حالة الطلب',
    pending: 'قيد الانتظار',
    processing: 'قيد التنفيذ',
    completed: 'مكتمل',
    canceled: 'ملغي',
    
    // Payment
    paymentMethod: 'طريقة الدفع',
    libyana: 'ليبيانا',
    madar: 'مدار',
    phoneNumber: 'رقم الهاتف',
    amount: 'المبلغ',
    submitPayment: 'إرسال طلب الشحن',
    paymentInstructions: 'تعليمات الدفع',
    transferTo: 'حوّل إلى',
    waitingApproval: 'بانتظار التأكيد من الإدارة',
    
    // Admin
    adminPanel: 'لوحة الإدارة',
    users: 'المستخدمين',
    orders: 'الطلبات',
    payments: 'طلبات الشحن',
    services: 'الخدمات',
    providers: 'المزودين',
    statistics: 'الإحصائيات',
    approve: 'موافقة',
    reject: 'رفض',
    cancel: 'إلغاء',
    
    // Levels
    bronze: 'برونزي',
    silver: 'فضي',
    gold: 'ذهبي',
    
    // Categories
    instagram: 'إنستغرام',
    tiktok: 'تيك توك',
    youtube: 'يوتيوب',
    snapchat: 'سناب شات',
    telegram: 'تيلغرام',
    twitter: 'تويتر',
    facebook: 'فيسبوك',
    whatsapp: 'واتساب',
    
    // Messages
    orderSuccess: 'تم إنشاء الطلب بنجاح',
    orderError: 'فشل إنشاء الطلب',
    paymentSuccess: 'تم إرسال طلب الشحن بنجاح',
    paymentError: 'فشل إرسال طلب الشحن',
    insufficientBalance: 'رصيد غير كافٍ',
    
    // Footer
    contactUs: 'تواصل معنا',
    followUs: 'تابعنا',
  },
  en: {
    // Header
    appName: 'Hammadi Store',
    appNameEn: 'Hammadi Store',
    
    // Auth
    login: 'Login',
    register: 'Register',
    email: 'Email',
    password: 'Password',
    logout: 'Logout',
    
    // Dashboard
    dashboard: 'Dashboard',
    balance: 'Current Balance',
    totalSpent: 'Total Spent',
    accountLevel: 'Account Level',
    newOrder: 'New Order',
    myOrders: 'My Orders',
    recharge: 'Recharge',
    clickToRecharge: 'Click to Recharge',
    
    // Orders
    selectCategory: 'Select Category',
    selectService: 'Select Service',
    enterLink: 'Enter Link',
    enterQuantity: 'Enter Quantity',
    quantity: 'Quantity',
    price: 'Price',
    totalPrice: 'Total Price',
    submitOrder: 'Submit Order',
    orderStatus: 'Order Status',
    pending: 'Pending',
    processing: 'Processing',
    completed: 'Completed',
    canceled: 'Canceled',
    
    // Payment
    paymentMethod: 'Payment Method',
    libyana: 'Libyana',
    madar: 'Madar',
    phoneNumber: 'Phone Number',
    amount: 'Amount',
    submitPayment: 'Submit Payment',
    paymentInstructions: 'Payment Instructions',
    transferTo: 'Transfer to',
    waitingApproval: 'Waiting for admin approval',
    
    // Admin
    adminPanel: 'Admin Panel',
    users: 'Users',
    orders: 'Orders',
    payments: 'Payments',
    services: 'Services',
    providers: 'Providers',
    statistics: 'Statistics',
    approve: 'Approve',
    reject: 'Reject',
    cancel: 'Cancel',
    
    // Levels
    bronze: 'Bronze',
    silver: 'Silver',
    gold: 'Gold',
    
    // Categories
    instagram: 'Instagram',
    tiktok: 'TikTok',
    youtube: 'YouTube',
    snapchat: 'Snapchat',
    telegram: 'Telegram',
    twitter: 'Twitter',
    facebook: 'Facebook',
    whatsapp: 'WhatsApp',
    
    // Messages
    orderSuccess: 'Order created successfully',
    orderError: 'Failed to create order',
    paymentSuccess: 'Payment request submitted successfully',
    paymentError: 'Failed to submit payment request',
    insufficientBalance: 'Insufficient balance',
    
    // Footer
    contactUs: 'Contact Us',
    followUs: 'Follow Us',
  },
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState(localStorage.getItem('language') || 'ar');

  useEffect(() => {
    document.documentElement.lang = language;
    document.documentElement.dir = language === 'ar' ? 'rtl' : 'ltr';
    localStorage.setItem('language', language);
  }, [language]);

  const toggleLanguage = () => {
    setLanguage((prev) => (prev === 'ar' ? 'en' : 'ar'));
  };

  const t = (key) => {
    return translations[language][key] || key;
  };

  const value = {
    language,
    setLanguage,
    toggleLanguage,
    t,
    isRTL: language === 'ar',
  };

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
};
