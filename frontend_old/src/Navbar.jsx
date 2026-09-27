import React, { useState } from 'react'
import { Home, Users, User, LogOut, Lightbulb, Calendar, Brain, Sparkles, MoreHorizontal, ChevronRight, X } from 'lucide-react'
import MobileHeader from './MobileHeader'
import BottomSheet from './BottomSheet'

function Navbar({ 
  user, 
  activePage, 
  onNavigate, 
  onLogout, 
  language = 'en', 
  onLanguageChange,
  showBackButton = false,
  onBack 
}) {
  const [showMoreSheet, setShowMoreSheet] = useState(false)

  const t = (key) => {
    const translations = {
      en: { home: 'Home', advisor: 'Advisory', memory: 'Memory', community: 'Community', calendar: 'Calendar', profile: 'Profile', judge: 'Judge Hub', more: 'More' },
      hi: { home: 'होम', advisor: 'सलाहकार', memory: 'स्मृति', community: 'समुदाय', calendar: 'कैलेंडर', profile: 'प्रोफ़ाइल', judge: 'जज हब', more: 'अधिक' },
      te: { home: 'హోమ్', advisor: 'సలహాదారు', memory: 'జ్ఞాపకాలు', community: 'కమ్యూనిటీ', calendar: 'క్యాలెండర్', profile: 'ప్రొఫైల్', judge: 'జడ్జ్ హబ్', more: 'మరిన్ని' },
      ta: { home: 'முகப்பு', advisor: 'ஆலோசகர்', memory: 'நினைவகம்', community: 'சமூகம்', calendar: 'நாட்காட்டி', profile: 'சுயவிவரம்', judge: 'நீதிபதி மையம்', more: 'மேலும்' },
      kn: { home: 'ಮುಖಪುಟ', advisor: 'ಸಲಹೆಗಾರ', memory: 'ನೆನಪು', community: 'ಸಮುದಾಯ', calendar: 'ಕ್ಯಾಲೆಂಡರ್', profile: 'ಪ್ರೊಫೈಲ್', judge: 'ಜಡ್ಜ್ ಹಬ್', more: 'ಇನ್ನಷ್ಟು' },
      ml: { home: 'ഹോം', advisor: 'ഉപദേശകൻ', memory: 'ഓർമ്മ', community: 'കമ്മ്യൂണിറ്റി', calendar: 'കലണ്ടർ', profile: 'പ്രൊഫൈൽ', judge: 'ജഡ്ജ് ഹബ്', more: 'കൂടുതൽ' },
      bn: { home: 'হোম', advisor: 'উপদেষ্টা', memory: 'স্মৃতি', community: 'কমিউনিটি', calendar: 'ক্যালেন্ডার', profile: 'প্রোফাইল', judge: 'জাজ হাব', more: 'আরও' },
      gu: { home: 'હોમ', advisor: 'સલાહકાર', memory: 'સ્મૃતિ', community: 'સમુદાય', calendar: 'કેલેન્ડર', profile: 'પ્રોફાઇલ', judge: 'જજ હબ', more: 'વધુ' },
      mr: { home: 'होम', advisor: 'सल्लागार', memory: 'स्मृती', community: 'समुदाय', calendar: 'कॅलेंडर', profile: 'प्रोफाइल', judge: 'जज हब', more: 'अधिक' }
    }
    return translations[language]?.[key] || translations.en[key]
  }

  const isMoreActive = ['calendar', 'judge', 'profile'].includes(activePage)

  return (
    <>
      {/* Mobile Top Contextual Header */}
      <MobileHeader
        user={user}
        activePage={activePage}
        onNavigate={onNavigate}
        language={language}
        onLanguageChange={onLanguageChange}
        showBackButton={showBackButton}
        onBack={onBack}
      />

      {/* Desktop Navigation Bar (hidden on mobile via CSS) */}
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
            <button 
              className={`nav-item ${activePage === 'judge' ? 'active' : ''}`} 
              onClick={() => onNavigate('judge')}
              style={{
                background: activePage === 'judge' ? '#065f46' : 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
                color: 'white',
                fontWeight: 700,
                borderRadius: '20px',
                padding: '6px 14px',
                boxShadow: '0 2px 8px rgba(5,150,105,0.3)',
                border: 'none',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <Sparkles size={16} color="#fde047" />
              <span>Judge Hub ⚡</span>
            </button>
            <button className={`nav-item ${activePage === 'profile' ? 'active' : ''}`} onClick={() => onNavigate('profile')}>
              <User size={18} />
              <span>{t('profile')}</span>
            </button>
            <div className="nav-divider"></div>
            <div className="nav-user-info">
              <span className="nav-location">📍 {user?.location?.split(',')[0]}</span>
            </div>
            <button className="nav-logout" onClick={onLogout} title="Sign Out">
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </nav>
      
      {/* Mobile Bottom Navigation - 5 Core Touch Targets */}
      <div className="mobile-bottom-nav">
        <button 
          className={`mobile-nav-item interactive-tap ${activePage === 'home' ? 'active' : ''}`} 
          onClick={() => onNavigate('home')}
        >
          <Home size={20} />
          <span>{t('home')}</span>
        </button>

        <button 
          className={`mobile-nav-item interactive-tap ${activePage === 'advisor' ? 'active' : ''}`} 
          onClick={() => onNavigate('advisor')}
        >
          <Lightbulb size={20} />
          <span>{t('advisor')}</span>
        </button>

        <button 
          className={`mobile-nav-item interactive-tap ${activePage === 'memory' ? 'active' : ''}`} 
          onClick={() => onNavigate('memory')}
        >
          <Brain size={20} />
          <span>{t('memory')}</span>
        </button>

        <button 
          className={`mobile-nav-item interactive-tap ${activePage === 'community' ? 'active' : ''}`} 
          onClick={() => onNavigate('community')}
        >
          <Users size={20} />
          <span>{t('community')}</span>
        </button>

        <button 
          className={`mobile-nav-item interactive-tap ${isMoreActive ? 'active' : ''}`} 
          onClick={() => setShowMoreSheet(true)}
        >
          <MoreHorizontal size={20} />
          <span>{t('more')}</span>
        </button>
      </div>

      {/* Mobile "More" Drawer Bottom Sheet */}
      <BottomSheet 
        isOpen={showMoreSheet} 
        onClose={() => setShowMoreSheet(false)}
        title="More Agricultural Services"
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <button
            type="button"
            className="interactive-tap"
            onClick={() => {
              setShowMoreSheet(false)
              onNavigate('calendar')
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px 14px',
              background: activePage === 'calendar' ? '#ecfdf5' : '#f8fafc',
              border: activePage === 'calendar' ? '1px solid #10b981' : '1px solid #e2e8f0',
              borderRadius: '12px',
              cursor: 'pointer',
              textAlign: 'left'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ background: '#e0f2fe', color: '#0369a1', padding: '8px', borderRadius: '10px' }}>
                <Calendar size={20} />
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#0f172a' }}>{t('calendar')}</div>
                <div style={{ fontSize: '0.78rem', color: '#64748b' }}>Seasonal sowing & harvest schedules</div>
              </div>
            </div>
            <ChevronRight size={18} color="#94a3b8" />
          </button>

          <button
            type="button"
            className="interactive-tap"
            onClick={() => {
              setShowMoreSheet(false)
              onNavigate('judge')
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px 14px',
              background: activePage === 'judge' ? '#ecfdf5' : '#f8fafc',
              border: activePage === 'judge' ? '1px solid #10b981' : '1px solid #e2e8f0',
              borderRadius: '12px',
              cursor: 'pointer',
              textAlign: 'left'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ background: '#dcfce7', color: '#15803d', padding: '8px', borderRadius: '10px' }}>
                <Sparkles size={20} color="#059669" />
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#0f172a' }}>{t('judge')} ⚡</div>
                <div style={{ fontSize: '0.78rem', color: '#64748b' }}>60-Sec Before vs After Hindsight proof</div>
              </div>
            </div>
            <ChevronRight size={18} color="#94a3b8" />
          </button>

          <button
            type="button"
            className="interactive-tap"
            onClick={() => {
              setShowMoreSheet(false)
              onNavigate('profile')
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px 14px',
              background: activePage === 'profile' ? '#ecfdf5' : '#f8fafc',
              border: activePage === 'profile' ? '1px solid #10b981' : '1px solid #e2e8f0',
              borderRadius: '12px',
              cursor: 'pointer',
              textAlign: 'left'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ background: '#f1f5f9', color: '#475569', padding: '8px', borderRadius: '10px' }}>
                <User size={20} />
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: '0.95rem', color: '#0f172a' }}>{t('profile')}</div>
                <div style={{ fontSize: '0.78rem', color: '#64748b' }}>Soil type, location & phone settings</div>
              </div>
            </div>
            <ChevronRight size={18} color="#94a3b8" />
          </button>

          <div style={{ margin: '8px 0', borderTop: '1px solid #e2e8f0' }} />

          <button
            type="button"
            className="interactive-tap"
            onClick={() => {
              setShowMoreSheet(false)
              onLogout && onLogout()
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '12px 14px',
              background: '#fef2f2',
              color: '#dc2626',
              border: '1px solid #fecaca',
              borderRadius: '12px',
              fontWeight: 700,
              fontSize: '0.9rem',
              cursor: 'pointer'
            }}
          >
            <LogOut size={18} />
            <span>Sign Out</span>
          </button>
        </div>
      </BottomSheet>
    </>
  )
}

export default Navbar
