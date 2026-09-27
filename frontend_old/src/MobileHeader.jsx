import React from 'react'
import { MapPin, Sparkles, Globe, User, ArrowLeft } from 'lucide-react'

function MobileHeader({ 
  user, 
  activePage = 'home', 
  onNavigate, 
  language = 'en', 
  onLanguageChange,
  showBackButton = false,
  onBack 
}) {
  const titles = {
    home: { title: 'Sarthi', subtitle: 'Your farm, today' },
    advisor: { title: 'Advisory 🌾', subtitle: 'Personalized farm guidance' },
    memory: { title: 'Memory Hub 🧠', subtitle: 'What Sarthi remembers' },
    community: { title: 'Community 👥', subtitle: 'Hyperlocal farm alerts' },
    calendar: { title: 'Crop Calendar 📅', subtitle: 'Sowing & harvest guide' },
    judge: { title: 'Judge Hub ⚡', subtitle: '60-Sec Hindsight proof' },
    profile: { title: 'Farm Profile 👤', subtitle: 'Soil & district settings' }
  }

  const current = titles[activePage] || titles.home
  const locationText = user?.location ? user.location.split(',')[0] : 'Farm'

  return (
    <header className="mobile-header-shell" style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      height: '56px',
      background: 'rgba(255, 255, 255, 0.96)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
      borderBottom: '1px solid #e2e8f0',
      zIndex: 99998,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 14px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
      transform: 'translateZ(0)'
    }}>
      {/* Left: Brand / Back Button */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {showBackButton && onBack ? (
          <button 
            type="button"
            onClick={onBack}
            className="interactive-tap"
            style={{
              background: '#f1f5f9',
              border: 'none',
              borderRadius: '50%',
              width: '34px',
              height: '34px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              color: '#334155'
            }}
            aria-label="Go back"
          >
            <ArrowLeft size={18} />
          </button>
        ) : (
          <div 
            onClick={() => onNavigate && onNavigate('home')} 
            style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}
          >
            <span style={{ fontSize: '1.4rem' }}>🌾</span>
            <div>
              <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#0f172a', lineHeight: 1.1 }}>
                {activePage === 'home' ? 'Sarthi' : current.title}
              </div>
              <div style={{ fontSize: '0.68rem', color: '#64748b', fontWeight: 500 }}>
                {activePage === 'home' ? current.subtitle : locationText}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Center: Location Chip (if Home or Advisor) */}
      {activePage === 'home' && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          background: '#f1f5f9',
          padding: '4px 10px',
          borderRadius: '20px',
          fontSize: '0.74rem',
          color: '#334155',
          fontWeight: 600,
          maxWidth: '140px',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap'
        }}>
          <MapPin size={12} color="#059669" style={{ flexShrink: 0 }} />
          <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{locationText}</span>
        </div>
      )}

      {/* Right: Actions (Judge Hub Quick Chip, Language, Profile) */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        {activePage !== 'judge' && (
          <button
            type="button"
            onClick={() => onNavigate && onNavigate('judge')}
            className="interactive-tap"
            style={{
              background: 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '16px',
              padding: '4px 8px',
              fontSize: '0.68rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '3px',
              boxShadow: '0 2px 6px rgba(5,150,105,0.25)'
            }}
          >
            <Sparkles size={11} color="#fde047" />
            <span>Judge</span>
          </button>
        )}

        {onLanguageChange && (
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <select
              value={language}
              onChange={(e) => onLanguageChange(e.target.value)}
              style={{
                fontSize: '0.72rem',
                fontWeight: 600,
                color: '#334155',
                background: '#f8fafc',
                border: '1px solid #cbd5e1',
                borderRadius: '8px',
                padding: '4px 6px',
                cursor: 'pointer',
                outline: 'none'
              }}
              aria-label="Select Language"
            >
              <option value="en">EN</option>
              <option value="hi">HI (हिंदी)</option>
              <option value="te">TE (తెలుగు)</option>
              <option value="ta">TA (தமிழ்)</option>
              <option value="kn">KN (ಕನ್ನಡ)</option>
              <option value="ml">ML (മലയാളം)</option>
              <option value="bn">BN (বাংলা)</option>
              <option value="gu">GU (ગુજરાતી)</option>
              <option value="mr">MR (मराठी)</option>
            </select>
          </div>
        )}

        <button
          type="button"
          onClick={() => onNavigate && onNavigate('profile')}
          className="interactive-tap"
          style={{
            background: activePage === 'profile' ? '#059669' : '#f1f5f9',
            color: activePage === 'profile' ? '#ffffff' : '#475569',
            border: 'none',
            borderRadius: '50%',
            width: '30px',
            height: '30px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer'
          }}
          aria-label="Open profile"
        >
          <User size={15} />
        </button>
      </div>
    </header>
  )
}

export default MobileHeader
