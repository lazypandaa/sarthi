import React from 'react'
import { Home, Users, User, LogOut, Lightbulb, Calendar, Brain } from 'lucide-react'

function Navbar({ user, activePage, onNavigate, onLogout, language }) {
  const t = (key) => {
    const translations = {
      en: { home: 'Home', advisor: 'Advisor', memory: 'Memory', community: 'Community', calendar: 'Calendar', profile: 'Profile' },
      hi: { home: 'होम', advisor: 'सलाहकार', memory: 'स्मृति', community: 'समुदाय', calendar: 'कैलेंडर', profile: 'प्रोफ़ाइल' },
      te: { home: 'హోమ్', advisor: 'సలహాదారు', memory: 'జ్ఞాపకాలు', community: 'కమ్యూనిటీ', calendar: 'క్యాలెండర్', profile: 'ప్రొఫైల్' },
      ta: { home: 'முகப்பு', advisor: 'ஆலோசகர்', memory: 'நினைவகம்', community: 'சமூகம்', calendar: 'நாட்காட்டி', profile: 'சுயவிவரம்' },
      kn: { home: 'ಮುಖಪುಟ', advisor: 'ಸಲಹೆಗಾರ', memory: 'ನೆನಪು', community: 'ಸಮುದಾಯ', calendar: 'ಕ್ಯಾಲೆಂಡರ್', profile: 'ಪ್ರೊಫೈಲ್' },
      ml: { home: 'ഹോം', advisor: 'ഉപദേശകൻ', memory: 'ഓർമ്മ', community: 'കമ്മ്യൂണിറ്റി', calendar: 'കലണ്ടർ', profile: 'പ്രൊഫൈൽ' },
      bn: { home: 'হোম', advisor: 'উপদেষ্টা', memory: 'স্মৃতি', community: 'কমিউনিটি', calendar: 'ক্যালেন্ডার', profile: 'প্রোফাইল' },
      gu: { home: 'હોમ', advisor: 'સલાહકાર', memory: 'સ્મૃતિ', community: 'સમુદાય', calendar: 'કેલેન્ડર', profile: 'પ્રોફાઇલ' },
      mr: { home: 'होम', advisor: 'सल्लागार', memory: 'स्मृती', community: 'समुदाय', calendar: 'कॅलेंडर', profile: 'प्रोफाइल' }
    }
    return translations[language]?.[key] || translations.en[key]
  }

  return (
    <>
      <nav className="app-navbar">
        <div className="navbar-content">
          <div className="navbar-brand" onClick={() => onNavigate('home')}>
            <span className="navbar-icon">🌾</span>
            <span className="navbar-title">Sarthi</span>
          </div>
          <div className="navbar-menu">
            <button className={`nav-item ${activePage === 'home' ? 'active' : ''}`} onClick={() => onNavigate('home')}>
              <Home size={18} />
              <span>{t('home')}</span>
            </button>
            <button className={`nav-item ${activePage === 'advisor' ? 'active' : ''}`} onClick={() => onNavigate('advisor')}>
              <Lightbulb size={18} />
              <span>{t('advisor')}</span>
            </button>
            <button className={`nav-item ${activePage === 'memory' ? 'active' : ''}`} onClick={() => onNavigate('memory')}>
              <Brain size={18} />
              <span>{t('memory')}</span>
            </button>
            <button className={`nav-item ${activePage === 'community' ? 'active' : ''}`} onClick={() => onNavigate('community')}>
              <Users size={18} />
              <span>{t('community')}</span>
            </button>
            <button className={`nav-item ${activePage === 'calendar' ? 'active' : ''}`} onClick={() => onNavigate('calendar')}>
              <Calendar size={18} />
              <span>{t('calendar')}</span>
            </button>
            <button className={`nav-item ${activePage === 'profile' ? 'active' : ''}`} onClick={() => onNavigate('profile')}>
              <User size={18} />
              <span>{t('profile')}</span>
            </button>
            <div className="nav-divider"></div>
            <div className="nav-user-info">
              <span className="nav-location">📍 {user?.location?.split(',')[0]}</span>
            </div>
            <button className="nav-logout" onClick={onLogout}>
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </nav>
      
      {/* Mobile Bottom Navigation */}
      <div className="mobile-bottom-nav">
        <button className={`mobile-nav-item ${activePage === 'home' ? 'active' : ''}`} onClick={() => onNavigate('home')}>
          <Home size={22} />
          <span>{t('home')}</span>
        </button>
        <button className={`mobile-nav-item ${activePage === 'advisor' ? 'active' : ''}`} onClick={() => onNavigate('advisor')}>
          <Lightbulb size={22} />
          <span>{t('advisor')}</span>
        </button>
        <button className={`mobile-nav-item ${activePage === 'memory' ? 'active' : ''}`} onClick={() => onNavigate('memory')}>
          <Brain size={22} />
          <span>{t('memory')}</span>
        </button>
        <button className={`mobile-nav-item ${activePage === 'community' ? 'active' : ''}`} onClick={() => onNavigate('community')}>
          <Users size={22} />
          <span>{t('community')}</span>
        </button>
        <button className={`mobile-nav-item ${activePage === 'calendar' ? 'active' : ''}`} onClick={() => onNavigate('calendar')}>
          <Calendar size={22} />
          <span>{t('calendar')}</span>
        </button>
        <button className={`mobile-nav-item ${activePage === 'profile' ? 'active' : ''}`} onClick={() => onNavigate('profile')}>
          <User size={22} />
          <span>{t('profile')}</span>
        </button>
      </div>
    </>
  )
}

export default Navbar
