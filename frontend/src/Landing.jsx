import React from 'react'
import { ArrowRight, Mic, Globe, Cloud, TrendingUp, Shield, Zap, CheckCircle, Users, Award } from 'lucide-react'

function Landing({ onGetStarted }) {
  return (
    <div className="landing-container">
      {/* Navigation */}
      <nav className="landing-nav">
        <div className="nav-content">
          <div className="nav-logo">
            <span className="nav-icon">🌾</span>
            <span className="nav-title">Sarthi</span>
          </div>
          <button className="nav-cta" onClick={onGetStarted}>
            Launch App <ArrowRight size={18} />
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="landing-hero">
        <div className="hero-content">
          <h1 className="hero-title">Empowering Rural India with AI Voice Technology</h1>
          <p className="hero-description">
            Connect farmers with real-time information through multilingual AI assistance.
            Get weather updates, crop prices, and government schemes in your local language.
          </p>
          <div className="hero-buttons">
            <button className="btn-primary" onClick={onGetStarted}>
              Get Started <ArrowRight size={20} />
            </button>
            <button className="btn-secondary" onClick={onGetStarted}>
              Try Demo
            </button>
          </div>
          <div className="hero-stats">
            <div className="stat">
              <div className="stat-number" style={{color: '#ffffff'}}>9+</div>
              <div className="stat-label" style={{color: '#e5e7eb'}}>Languages</div>
            </div>
            <div className="stat">
              <div className="stat-number" style={{color: '#ffffff'}}>100%</div>
              <div className="stat-label" style={{color: '#e5e7eb'}}>Voice Enabled</div>
            </div>
            <div className="stat">
              <div className="stat-number" style={{color: '#ffffff'}}>24/7</div>
              <div className="stat-label" style={{color: '#e5e7eb'}}>Available</div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="landing-section features-section">
        <div className="section-header">
          <h2>Bridging Technology & Agriculture</h2>
          <p>Comprehensive AI-powered solutions for rural communities</p>
        </div>
        <div className="features-grid-modern">
          <div className="feature-modern">
            <div className="feature-modern-icon">
              <Mic size={28} />
            </div>
            <h3>Voice & Text Input</h3>
            <p>Speak or type in your local language with advanced voice recognition</p>
          </div>
          <div className="feature-modern">
            <div className="feature-modern-icon">
              <Globe size={28} />
            </div>
            <h3>9 Indian Languages</h3>
            <p>Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Gujarati, Marathi, English</p>
          </div>
          <div className="feature-modern">
            <div className="feature-modern-icon">
              <Cloud size={28} />
            </div>
            <h3>Real-time Weather</h3>
            <p>Accurate weather forecasts for informed farming decisions</p>
          </div>
          <div className="feature-modern">
            <div className="feature-modern-icon">
              <TrendingUp size={28} />
            </div>
            <h3>Market Prices</h3>
            <p>Live crop prices to maximize your profits</p>
          </div>
          <div className="feature-modern">
            <div className="feature-modern-icon">
              <Shield size={28} />
            </div>
            <h3>Govt Schemes</h3>
            <p>Access information about agricultural benefits</p>
          </div>
          <div className="feature-modern">
            <div className="feature-modern-icon">
              <Zap size={28} />
            </div>
            <h3>AI-Powered</h3>
            <p>Intelligent responses with voice output</p>
          </div>
        </div>
      </div>

      {/* Technology Section */}
      <div className="landing-section tech-modern-section">
        <div className="tech-modern-grid">
          <div className="tech-modern-content">
            <h2>Built with Cutting-Edge Technology</h2>
            <p>Leveraging the best AI and cloud technologies to serve rural India</p>
            <div className="tech-list">
              <div className="tech-list-item">
                <CheckCircle size={20} />
                <span>Amazon Bedrock (Claude 3) for intelligent responses</span>
              </div>
              <div className="tech-list-item">
                <CheckCircle size={20} />
                <span>Amazon Polly for natural voice synthesis</span>
              </div>
              <div className="tech-list-item">
                <CheckCircle size={20} />
                <span>Amazon Transcribe for accurate speech recognition</span>
              </div>
              <div className="tech-list-item">
                <CheckCircle size={20} />
                <span>Amazon Translate for multilingual support</span>
              </div>
              <div className="tech-list-item">
                <CheckCircle size={20} />
                <span>AWS DynamoDB & MongoDB for scalable data storage</span>
              </div>
            </div>
          </div>
          <div className="tech-modern-image">
            <div className="tech-badge">
              <Users size={24} />
              <div>
                <div className="tech-badge-number">1000+</div>
                <div className="tech-badge-label">Potential Users</div>
              </div>
            </div>
            <div className="tech-badge">
              <Award size={24} />
              <div>
                <div className="tech-badge-number">100%</div>
                <div className="tech-badge-label">Accuracy</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="landing-cta-modern">
        <div className="cta-modern-content">
          <h2>Ready to Transform Rural Communication?</h2>
          <p>Join us in empowering farmers with AI-powered voice assistance</p>
          <button className="btn-cta-large" onClick={onGetStarted}>
            Launch Sarthi <ArrowRight size={24} />
          </button>
        </div>
      </div>

      {/* Footer */}
      <div className="landing-footer-modern">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="footer-logo">
              <span className="footer-icon">🌾</span>
              <span className="footer-title">Sarthi</span>
            </div>
            <p>AI Voice Assistant for Rural India</p>
          </div>
          <div className="footer-info">
            <p>Empowering Rural Communities with Technology</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Landing
