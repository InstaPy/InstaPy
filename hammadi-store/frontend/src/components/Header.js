import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

const Header = () => {
  const { user, logout, isAdmin } = useAuth();
  const { t, toggleLanguage, language } = useLanguage();

  return (
    <header className="bg-dark-card shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4 space-x-reverse">
            <h1 className="text-2xl font-bold text-primary">
              {language === 'ar' ? 'حمّادي ستور' : 'Hammadi Store'}
            </h1>
            {isAdmin && (
              <span className="badge bg-red-600 text-white">Admin</span>
            )}
          </div>

          <div className="flex items-center gap-4">
            {user && (
              <div className="text-sm">
                <span className="text-gray-400">{user.email}</span>
              </div>
            )}
            
            <button
              onClick={toggleLanguage}
              className="px-3 py-1 bg-dark-hover rounded-lg text-sm hover:bg-dark-bg transition-colors"
            >
              {language === 'ar' ? 'EN' : 'عربي'}
            </button>

            {user && (
              <button
                onClick={logout}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-sm font-semibold transition-colors"
              >
                {t('logout')}
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
