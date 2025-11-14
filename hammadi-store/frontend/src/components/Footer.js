import React, { useEffect, useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { configAPI } from '../services/api';

const Footer = () => {
  const { t } = useLanguage();
  const [config, setConfig] = useState({
    whatsapp_number: '0910882830',
    telegram_channel: 'https://t.me/hammadi_store'
  });

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await configAPI.get();
      setConfig(response.data);
    } catch (error) {
      console.error('Failed to load config:', error);
    }
  };

  const socialIcons = [
    { name: 'Instagram', icon: '📷', color: 'from-purple-600 to-pink-600' },
    { name: 'TikTok', icon: '🎵', color: 'from-black to-cyan-500' },
    { name: 'YouTube', icon: '▶️', color: 'from-red-600 to-red-700' },
    { name: 'Snapchat', icon: '👻', color: 'from-yellow-400 to-yellow-500' },
    { name: 'Telegram', icon: '✈️', color: 'from-blue-400 to-blue-500' },
    { name: 'Twitter', icon: '🐦', color: 'from-blue-400 to-blue-600' },
    { name: 'Facebook', icon: '👥', color: 'from-blue-600 to-blue-700' },
    { name: 'WhatsApp', icon: '💬', color: 'from-green-500 to-green-600' },
  ];

  return (
    <footer className="bg-dark-card mt-12 border-t border-gray-700">
      <div className="container mx-auto px-4 py-8">
        {/* Social Icons */}
        <div className="flex justify-center gap-4 mb-8 flex-wrap">
          {socialIcons.map((social) => (
            <div
              key={social.name}
              className={`w-12 h-12 rounded-full bg-gradient-to-br ${social.color} flex items-center justify-center text-2xl hover:scale-110 transition-transform cursor-pointer shadow-lg`}
              title={social.name}
            >
              {social.icon}
            </div>
          ))}
        </div>

        {/* Contact Section */}
        <div className="text-center mb-6">
          <h3 className="text-xl font-bold mb-4">{t('contactUs')}</h3>
          <div className="flex justify-center gap-6 flex-wrap">
            <a
              href={`https://wa.me/${config.whatsapp_number}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg transition-colors shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              <span className="text-2xl">💬</span>
              <div className="text-right">
                <div className="text-xs text-green-100">WhatsApp</div>
                <div className="font-bold">{config.whatsapp_number}</div>
              </div>
            </a>

            <a
              href={config.telegram_channel}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-6 py-3 bg-blue-500 hover:bg-blue-600 rounded-lg transition-colors shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              <span className="text-2xl">✈️</span>
              <div className="text-right">
                <div className="text-xs text-blue-100">Telegram</div>
                <div className="font-bold">@hammadi_store</div>
              </div>
            </a>
          </div>
        </div>

        {/* Copyright */}
        <div className="text-center text-gray-400 text-sm border-t border-gray-700 pt-6">
          <p>© 2024 حمّادي ستور | Hammadi Store - جميع الحقوق محفوظة</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
