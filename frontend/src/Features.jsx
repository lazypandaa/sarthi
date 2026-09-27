import React from 'react'
import { 
  Database, Globe, MessageSquare, TrendingUp, Shield, Zap, 
  Users, BarChart3, Award, CheckCircle, ArrowRight, Sparkles, User, LogOut 
} from 'lucide-react'
import './Features.css'

function Features({ onBack, user, onLogout, onNavigate }) {
  const features = [
    {
      icon: <Globe size={32} />,
      title: "Multi-Language AI Assistant",
      description: "Supports 9 Indian languages with real-time translation to English for RAG processing",
      tech: ["Azure OpenAI GPT-4o", "Azure Speech Services", "Amazon Polly"],
      color: "#3b82f6"
    },
    {
      icon: <Database size={32} />,
      title: "DynamoDB Architecture",
      description: "Scalable NoSQL database with phone-based authentication and session tracking",
      tech: ["AWS DynamoDB", "Global Secondary Indexes", "Pay-per-request"],
      color: "#8b5cf6"
    },
    {
      icon: <MessageSquare size={32} />,
      title: "Voice & Text Queries",
      description: "Dual-mode interaction with Amazon Transcribe for speech-to-text",
      tech: ["Amazon Transcribe", "WebRTC", "Real-time Processing"],
      color: "#06b6d4"
    },
    {
      icon: <TrendingUp size={32} />,
      title: "Village Trust Index",
      description: "Community-driven feedback system calculating trust scores per village",
      tech: ["Feedback Analytics", "Trust Scoring", "Village Metrics"],
      color: "#10b981"
    },
    {
      icon: <Shield size={32} />,
      title: "Secure Authentication",
      description: "Phone number-based auth with bcrypt hashing and JWT tokens",
      tech: ["JWT", "bcrypt", "IAM Authentication"],
      color: "#f59e0b"
    },
    {
      icon: <Zap size={32} />,
      title: "Context-Aware Sessions",
      description: "Tracks user sessions and query patterns for personalized responses",
      tech: ["Session Management", "Query Mapping", "Context Tracking"],
      color: "#ef4444"
    }
  ]

  const stats = [
    { label: "Languages Supported", value: "9", icon: <Globe size={24} /> },
    { label: "Response Time", value: "<2s", icon: <Zap size={24} /> },
    { label: "Database Tables", value: "4", icon: <Database size={24} /> },
    { label: "API Endpoints", value: "15+", icon: <BarChart3 size={24} /> }
  ]

  const architecture = [
    {
      layer: "Frontend",
      tech: ["React", "Vite", "Axios", "Lucide Icons"],
      color: "#3b82f6"
    },
    {
      layer: "Backend",
      tech: ["FastAPI", "Python", "Uvicorn", "Pydantic"],
      color: "#10b981"
    },
    {
      layer: "AI Services",
      tech: ["Azure OpenAI", "Azure Speech", "Amazon Polly", "Amazon Transcribe"],
      color: "#8b5cf6"
    },
    {
      layer: "Database",
      tech: ["AWS DynamoDB", "Global Secondary Indexes", "Session Tracking"],
      color: "#f59e0b"
    }
  ]

  const dataFlow = [
    "User Query (9 Languages)",
    "Translation to English",
    "AI Processing (GPT-4o)",
    "Response Generation",
    "Text-to-Speech",
    "Feedback Collection",
    "Trust Score Update"
  ]

  return (
    <div className="features-page">
      <nav className="app-navbar">
        <div className="navbar-content">
          <div className="navbar-brand" onClick={() => onNavigate('home')}>
            <span className="navbar-icon">🌾</span>
            <span className="navbar-title">Sarthi</span>
          </div>
          <div className="navbar-menu">
            <button className="nav-item" onClick={() => onNavigate('home')}>
              <span>Home</span>
            </button>
            <button className="nav-item active">
              <Award size={18} />
              <span>Features</span>
            </button>
            <button className="nav-item" onClick={() => onNavigate('profile')}>
              <User size={18} />
              <span>Profile</span>
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
      <div className="features-content">
      {/* Hero Section */}
      <div className="features-hero">
        <div className="hero-badge">
          <Sparkles size={16} />
          <span>Hackathon Project 2026</span>
        </div>
        <h1 className="hero-title">
          Sarthi
          <span className="gradient-text"> AI Voice Assistant</span>
        </h1>
        <p className="hero-subtitle">
          Empowering Rural India with Multi-Language AI, Voice Interaction, and Community Trust Metrics
        </p>
        <div className="hero-stats">
          {stats.map((stat, index) => (
            <div key={index} className="stat-card">
              <div className="stat-icon">{stat.icon}</div>
              <div className="stat-value">{stat.value}</div>
              <div className="stat-label">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Features Grid */}
      <div className="features-section">
        <div className="section-header">
          <h2>Core Features</h2>
          <p>Industry-grade architecture with cutting-edge AI technologies</p>
        </div>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card" style={{'--feature-color': feature.color}}>
              <div className="feature-icon" style={{backgroundColor: feature.color}}>
                {feature.icon}
              </div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
              <div className="tech-stack">
                {feature.tech.map((tech, i) => (
                  <span key={i} className="tech-badge">{tech}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Architecture */}
      <div className="architecture-section">
        <div className="section-header">
          <h2>System Architecture</h2>
          <p>Scalable, secure, and production-ready infrastructure</p>
        </div>
        <div className="architecture-layers">
          {architecture.map((layer, index) => (
            <div key={index} className="arch-layer">
              <div className="layer-header" style={{backgroundColor: layer.color}}>
                <h3>{layer.layer}</h3>
              </div>
              <div className="layer-tech">
                {layer.tech.map((tech, i) => (
                  <div key={i} className="tech-item">
                    <CheckCircle size={16} />
                    <span>{tech}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Data Flow */}
      <div className="dataflow-section">
        <div className="section-header">
          <h2>Data Flow Pipeline</h2>
          <p>End-to-end processing with feedback loop</p>
        </div>
        <div className="dataflow-container">
          {dataFlow.map((step, index) => (
            <React.Fragment key={index}>
              <div className="flow-step">
                <div className="step-number">{index + 1}</div>
                <div className="step-content">{step}</div>
              </div>
              {index < dataFlow.length - 1 && (
                <div className="flow-arrow">
                  <ArrowRight size={24} />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Key Highlights */}
      <div className="highlights-section">
        <div className="section-header">
          <h2>Technical Highlights</h2>
          <p>What makes this solution industry-ready</p>
        </div>
        <div className="highlights-grid">
          <div className="highlight-card">
            <Award size={32} />
            <h3>Scalable Architecture</h3>
            <p>DynamoDB auto-scaling handles millions of users without manual intervention</p>
          </div>
          <div className="highlight-card">
            <Users size={32} />
            <h3>Village Trust Index</h3>
            <p>Novel approach to measure community satisfaction and response quality</p>
          </div>
          <div className="highlight-card">
            <Database size={32} />
            <h3>Smart Data Storage</h3>
            <p>Stores queries in native language + English translation for RAG training</p>
          </div>
          <div className="highlight-card">
            <Shield size={32} />
            <h3>Production Security</h3>
            <p>Phone-based auth, JWT tokens, bcrypt hashing, IAM roles</p>
          </div>
        </div>
      </div>

      {/* Tech Stack Summary */}
      <div className="techstack-section">
        <div className="section-header">
          <h2>Complete Tech Stack</h2>
        </div>
        <div className="techstack-grid">
          <div className="tech-category">
            <h4>Frontend</h4>
            <div className="tech-list">
              <span>React 18</span>
              <span>Vite</span>
              <span>Axios</span>
              <span>Lucide Icons</span>
            </div>
          </div>
          <div className="tech-category">
            <h4>Backend</h4>
            <div className="tech-list">
              <span>FastAPI</span>
              <span>Python 3.12</span>
              <span>Uvicorn</span>
              <span>Pydantic</span>
            </div>
          </div>
          <div className="tech-category">
            <h4>AI/ML</h4>
            <div className="tech-list">
              <span>Azure OpenAI GPT-4o</span>
              <span>Azure Speech</span>
              <span>Amazon Polly</span>
              <span>Amazon Transcribe</span>
            </div>
          </div>
          <div className="tech-category">
            <h4>Database</h4>
            <div className="tech-list">
              <span>AWS DynamoDB</span>
              <span>Global Secondary Indexes</span>
              <span>Pay-per-request</span>
            </div>
          </div>
          <div className="tech-category">
            <h4>Security</h4>
            <div className="tech-list">
              <span>JWT</span>
              <span>bcrypt</span>
              <span>IAM</span>
              <span>CORS</span>
            </div>
          </div>
          <div className="tech-category">
            <h4>DevOps</h4>
            <div className="tech-list">
              <span>Git</span>
              <span>GitHub</span>
              <span>Environment Variables</span>
            </div>
          </div>
        </div>
      </div>
      </div>
    </div>
  )
}

export default Features
