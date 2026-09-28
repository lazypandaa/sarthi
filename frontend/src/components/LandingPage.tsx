import React from "react";

interface LandingPageProps {
  onGetStarted: () => void;
  onLogin: () => void;
  onTryDemo: () => void;
}

export function LandingPage({ onGetStarted, onLogin, onTryDemo }: LandingPageProps) {
  const scrollTo = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="landing-wrapper">
      {/* ── Fixed Navigation Bar ────────────────────────────────────────── */}
      <header className="landing-navbar">
        <div className="landing-nav-inner">
          <div className="landing-brand" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
            <div className="landing-brand-logo">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4">
                <path d="M11 20A7 7 0 0 1 9.8 6.1C15 3 21 4 21 4s1 6-2.1 11.2A7 7 0 0 1 11 20Z" />
                <path d="M2 21c0-3 1.85-5.36 5.08-6.94 2.03-.99 4.27-1.29 6.92-.86" />
              </svg>
            </div>
            <div>
              <span className="landing-brand-title">SARTHI</span>
              <span className="landing-brand-tag">AI AGRONOMIST</span>
            </div>
          </div>

          <nav className="landing-nav-links">
            <button type="button" onClick={() => scrollTo("features")}>Features</button>
            <button type="button" onClick={() => scrollTo("ground-truth")}>Data Grounding</button>
            <button type="button" onClick={() => scrollTo("hindsight")}>Hindsight AI</button>
            <button type="button" onClick={() => scrollTo("how-it-works")}>How It Works</button>
          </nav>

          <div className="landing-nav-actions">
            <button type="button" className="landing-btn-ghost" onClick={onLogin}>
              Sign In
            </button>
            <button type="button" className="landing-btn-primary" onClick={onGetStarted}>
              Launch App
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M5 12h14M13 6l6 6-6 6" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* ── Hero Section ───────────────────────────────────────────────── */}
      <section className="landing-hero-section">
        <div className="landing-hero-bg-overlay" />
        <div className="landing-hero-content">
          <div className="landing-hero-badge">
            <span className="landing-pulse-dot" />
            <span>Empowering 140M+ Indian Farmers · 9 Regional Languages</span>
          </div>

          <h1 className="landing-hero-title">
            Empowering Rural India with <br />
            <span className="landing-title-highlight">Hyperlocal AI Voice</span> Technology
          </h1>

          <p className="landing-hero-desc">
            India's first voice-native agricultural copilot. Built for farmers to speak in their regional dialect,
            track village pest outbreaks on interactive GIS maps, inspect real-time APMC mandi prices, and follow
            crop calendars personalized by long-term Hindsight Memory.
          </p>

          <div className="landing-hero-buttons">
            <button type="button" className="landing-btn-hero-primary" onClick={onGetStarted}>
              <span>Launch Sarthi App</span>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M5 12h14M13 6l6 6-6 6" />
              </svg>
            </button>
            <button type="button" className="landing-btn-hero-secondary" onClick={onTryDemo}>
              <span>⚡ Try Live Demo Account</span>
            </button>
          </div>

          <div className="landing-apk-pill">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="5" y="2" width="14" height="20" rx="3" />
              <line x1="12" y1="18" x2="12.01" y2="18" strokeWidth="3" />
            </svg>
            <span>Android APK v1.4 available for field deployment</span>
          </div>

          {/* Key Metrics Strip */}
          <div className="landing-stats-grid">
            <div className="landing-stat-card">
              <div className="landing-stat-val">9+</div>
              <div className="landing-stat-label">Indian Languages</div>
              <div className="landing-stat-sub">Hindi, Telugu, Tamil, Marathi, etc.</div>
            </div>
            <div className="landing-stat-card">
              <div className="landing-stat-val">100%</div>
              <div className="landing-stat-label">Voice & Speech Enabled</div>
              <div className="landing-stat-sub">Natural dialetical voice I/O</div>
            </div>
            <div className="landing-stat-card">
              <div className="landing-stat-val">702</div>
              <div className="landing-stat-label">Districts Grounded</div>
              <div className="landing-stat-sub">Real Soil Health Card chemistry</div>
            </div>
            <div className="landing-stat-card">
              <div className="landing-stat-val">₹44,000+</div>
              <div className="landing-stat-label">Seasonal Savings</div>
              <div className="landing-stat-sub">Via Hindsight Memory guidance</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Core Features Grid ─────────────────────────────────────────── */}
      <section id="features" className="landing-section-container">
        <div className="landing-section-header">
          <span className="landing-section-tag">ENGINEERED FOR PROGRESSIVE FARMERS</span>
          <h2 className="landing-section-title">Everything a Farmer Needs, One Voice Tap Away</h2>
          <p className="landing-section-subtitle">
            From localized soil chemistry to community disease radar, Sarthi replaces generic guesswork with authoritative, actionable science.
          </p>
        </div>

        <div className="landing-features-grid">
          <div className="landing-feature-card">
            <div className="landing-feature-icon" style={{ background: "rgba(9,107,71,0.12)", color: "#096b47" }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="9" y="2" width="6" height="12" rx="3" />
                <path d="M5 10a7 7 0 0 0 14 0M12 17v5" />
              </svg>
            </div>
            <h3>Multilingual Voice Agronomist</h3>
            <p>
              Speak naturally in Hindi, Telugu, Marathi, or English. Sarthi processes rural dialects and streams back intelligent advice with natural voice synthesis.
            </p>
          </div>

          <div className="landing-feature-card">
            <div className="landing-feature-icon" style={{ background: "rgba(201,79,79,0.12)", color: "#c94f4f" }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6Z" />
                <path d="M9 3v15M15 6v15" />
              </svg>
            </div>
            <h3>Community Outbreak Radar</h3>
            <p>
              Interactive GIS OpenStreetMap visualizing live pest and disease outbreaks reported by neighboring farms. Automatically alerts you before infection spreads to your acreage.
            </p>
          </div>

          <div className="landing-feature-card">
            <div className="landing-feature-icon" style={{ background: "rgba(217,155,36,0.12)", color: "#d99b24" }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="5" width="18" height="16" rx="2" />
                <path d="M16 3v4M8 3v4M3 10h18" />
              </svg>
            </div>
            <h3>Dynamic Kharif 2026 Calendar</h3>
            <p>
              Synchronized with ICAR agronomy cycles for Chilli, Soybean, Sugarcane, Cotton, and Groundnut. Provides day-by-day critical operations, fertigation, and harvest indicators.
            </p>
          </div>

          <div className="landing-feature-card">
            <div className="landing-feature-icon" style={{ background: "rgba(19,133,91,0.12)", color: "#13855b" }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9.5 4A3.5 3.5 0 0 0 6 7.5v.7a3.5 3.5 0 0 0-1 6.7v.6A3.5 3.5 0 0 0 9.5 19H12V4H9.5ZM14.5 4A3.5 3.5 0 0 1 18 7.5v.7a3.5 3.5 0 0 1 1 6.7v.6a3.5 3.5 0 0 1-4.5 3.5H12V4h2.5Z" />
                <path d="M8 9h4M12 15h4" />
              </svg>
            </div>
            <h3>Hindsight Long-Term Memory</h3>
            <p>
              Learns your farm's unique profile over time: soil hardpan depths, borewell salinity, and past crop losses. Sarthi avoids recurring errors and compounds wisdom season after season.
            </p>
          </div>

          <div className="landing-feature-card">
            <div className="landing-feature-icon" style={{ background: "rgba(59,130,246,0.12)", color: "#2563eb" }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
                <polyline points="17 6 23 6 23 12" />
              </svg>
            </div>
            <h3>Live APMC Mandi Prices</h3>
            <p>
              Real-time daily modal prices from 2,800+ APMC mandis across India with MSP benchmarks, mandi distance calculations, and optimal selling window suggestions.
            </p>
          </div>

          <div className="landing-feature-card">
            <div className="landing-feature-icon" style={{ background: "rgba(16,185,129,0.12)", color: "#10b981" }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              </svg>
            </div>
            <h3>Zero-Hallucination Ground Truth</h3>
            <p>
              The LLM never hallucinates agriculture data. Every advice is strictly grounded in DA&FW Soil Health Cards, ICAR crop packages, and IMD meteorological stations.
            </p>
          </div>
        </div>
      </section>

      {/* ── Data Grounding & Architectural Superiority ─────────────────── */}
      <section id="ground-truth" className="landing-section-container landing-alt-bg">
        <div className="landing-section-header">
          <span className="landing-section-tag">AUTHORITATIVE GROUND TRUTH</span>
          <h2 className="landing-section-title">Why Sarthi Outperforms Generic AI Chatbots</h2>
          <p className="landing-section-subtitle">
            Generic LLMs guess soil chemistry and fabricate planting dates. Sarthi grounds every response in real Indian agricultural infrastructure.
          </p>
        </div>

        <div className="landing-comparison-table-wrapper">
          <table className="landing-comparison-table">
            <thead>
              <tr>
                <th>Farming Domain</th>
                <th>Standard Generic AI Chatbot</th>
                <th className="highlight-col">Sarthi Autonomous Agronomist</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><b>Soil Health & Nutrients</b></td>
                <td>Guesses standard NPK ratios from generic internet text</td>
                <td className="highlight-col"><b>702 Districts Soil Health Cards</b> (pH, Organic Carbon, Available N, P, K)</td>
              </tr>
              <tr>
                <td><b>Crop Selection & Timing</b></td>
                <td>Suggests generic seasons without checking rainfall or frost</td>
                <td className="highlight-col"><b>ICAR Kharif 2026 Norms</b> synchronized with agro-climatic zones</td>
              </tr>
              <tr>
                <td><b>Pest Management</b></td>
                <td>Recommends banned or random chemicals</td>
                <td className="highlight-col"><b>Community Radar & Central Insecticide Board</b> approved schedules</td>
              </tr>
              <tr>
                <td><b>Long-Term Farm Memory</b></td>
                <td>Forgets everything when session closes</td>
                <td className="highlight-col"><b>Self-Evolving Hindsight Memory</b> persisted in Azure Table Storage</td>
              </tr>
              <tr>
                <td><b>Commodity Prices</b></td>
                <td>Hallucinates outdated or fictional rates</td>
                <td className="highlight-col"><b>Live Agmarknet Mandi Feeds</b> with daily modal rates & MSP</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* ── Hindsight Memory Section ───────────────────────────────────── */}
      <section id="hindsight" className="landing-section-container">
        <div className="landing-hindsight-split">
          <div className="landing-hindsight-text">
            <span className="landing-section-tag">SELF-EVOLVING INTELLIGENCE</span>
            <h2>The Hindsight Memory Bank</h2>
            <p>
              Most farming apps treat every interaction as day zero. Sarthi builds a cumulative, evolving memory of your land:
            </p>
            <div className="landing-hindsight-points">
              <div className="landing-point">
                <span className="point-icon">💡</span>
                <div>
                  <b>Remembers Costly Failures</b>
                  <p>If Tomato failed due to Bacterial Wilt last year, Sarthi flags crop rotation and restricts nightshades.</p>
                </div>
              </div>
              <div className="landing-point">
                <span className="point-icon">💧</span>
                <div>
                  <b>Adapts to Water & Soil Realities</b>
                  <p>Tracks your borewell discharge and soil hardpan to avoid recommending high-water crops like Sugarcane if water is scarce.</p>
                </div>
              </div>
              <div className="landing-point">
                <span className="point-icon">📈</span>
                <div>
                  <b>Compounds Seasonal Profits</b>
                  <p>Optimizes harvest dates based on historical price surges in nearby APMC mandis.</p>
                </div>
              </div>
            </div>
            <div style={{ marginTop: "24px" }}>
              <button type="button" className="landing-btn-primary" onClick={onTryDemo}>
                Inspect Live Memory Bank
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M5 12h14M13 6l6 6-6 6" />
                </svg>
              </button>
            </div>
          </div>

          <div className="landing-hindsight-card">
            <div className="hindsight-card-header">
              <div className="hindsight-tag">🧠 Live Hindsight Active</div>
              <div className="hindsight-score">Confidence 96%</div>
            </div>
            <div className="hindsight-dialogue">
              <div className="hindsight-msg farmer">
                <div className="msg-sender">Farmer Ramesh (Voice)</div>
                <div className="msg-bubble">"Should I plant Chilli in Plot 2 this Kharif?"</div>
              </div>
              <div className="hindsight-msg sarthi">
                <div className="msg-sender">Sarthi AI Agronomist</div>
                <div className="msg-bubble">
                  <b>"Avoid Chilli in Plot 2.</b> I remember in July 2025 you experienced an 85% loss from Black Thrips in that exact plot. 
                  Rotating with <b>Black Gram (Urad)</b> will break the thrips soil pupation cycle and add 24 kg/ha biological nitrogen. 
                  Expected net profit: <b>₹38,500/acre</b>."
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── How It Works ───────────────────────────────────────────────── */}
      <section id="how-it-works" className="landing-section-container landing-alt-bg">
        <div className="landing-section-header">
          <span className="landing-section-tag">SEAMLESS USER EXPERIENCE</span>
          <h2 className="landing-section-title">How Sarthi Works in 4 Steps</h2>
          <p className="landing-section-subtitle">
            Zero technical friction. Designed for Indian farmers of all literacy levels.
          </p>
        </div>

        <div className="landing-steps-grid">
          <div className="landing-step-card">
            <div className="step-num">01</div>
            <h4>Tap & Speak</h4>
            <p>Press the green mic button and speak in your language. Sarthi auto-detects your dialect and GPS coordinates.</p>
          </div>
          <div className="landing-step-card">
            <div className="step-num">02</div>
            <h4>Data Grounding</h4>
            <p>Sarthi scans your district's Soil Health Card, live APMC prices, IMD weather, and neighbor pest reports.</p>
          </div>
          <div className="landing-step-card">
            <div className="step-num">03</div>
            <h4>Hindsight Cross-Check</h4>
            <p>Your farm's historical memory bank filters the recommendation to prevent known mistakes and repeat failures.</p>
          </div>
          <div className="landing-step-card">
            <div className="step-num">04</div>
            <h4>Voice Response & Action</h4>
            <p>Sarthi answers with a clear, concise voice summary and step-by-step guidance on your screen.</p>
          </div>
        </div>
      </section>

      {/* ── Call to Action Banner ───────────────────────────────────────── */}
      <section className="landing-cta-banner">
        <div className="landing-cta-inner">
          <h2>Ready to Transform Your Farm with Sarthi?</h2>
          <p>
            Experience AI precision grounded in authoritative Indian agriculture science. Try the live demo account or sign in to start your farm advisory.
          </p>
          <div className="landing-cta-actions">
            <button type="button" className="landing-btn-hero-primary" onClick={onGetStarted}>
              Launch Sarthi Now
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M5 12h14M13 6l6 6-6 6" />
              </svg>
            </button>
            <button type="button" className="landing-btn-hero-secondary" onClick={onTryDemo}>
              Try Demo Farmer (Sehore, MP)
            </button>
          </div>
        </div>
      </section>

      {/* ── Footer ─────────────────────────────────────────────────────── */}
      <footer className="landing-footer">
        <div className="landing-footer-inner">
          <div className="landing-footer-col">
            <div className="landing-brand">
              <div className="landing-brand-logo">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <path d="M11 20A7 7 0 0 1 9.8 6.1C15 3 21 4 21 4s1 6-2.1 11.2A7 7 0 0 1 11 20Z" />
                  <path d="M2 21c0-3 1.85-5.36 5.08-6.94 2.03-.99 4.27-1.29 6.92-.86" />
                </svg>
              </div>
              <span className="landing-brand-title">SARTHI</span>
            </div>
            <p className="landing-footer-desc">
              Voice-First Agricultural Intelligence for Rural India. Grounded in ICAR, Soil Health Cards, and Agmarknet data.
            </p>
          </div>

          <div className="landing-footer-col">
            <h4>Platform</h4>
            <ul>
              <li><button type="button" onClick={onGetStarted}>Web Application</button></li>
              <li><a href="https://github.com/lazypandaa/sarthi/raw/main/Sarthi-v1.4.apk" target="_blank" rel="noreferrer">Download Android APK</a></li>
              <li><button type="button" onClick={onTryDemo}>Demo Credentials</button></li>
            </ul>
          </div>

          <div className="landing-footer-col">
            <h4>Authoritative Sources</h4>
            <ul>
              <li>Soil Health Card (DA&FW)</li>
              <li>Agmarknet APMC Daily Feeds</li>
              <li>India Meteorological Dept (IMD)</li>
              <li>ICAR Agronomy Packages</li>
            </ul>
          </div>
        </div>

        <div className="landing-footer-bottom">
          <div>© 2026 Sarthi. Built for Hack with HYD 2026. Empowering Indian Farmers.</div>
          <div>All recommendations grounded in official Government of India datasets.</div>
        </div>
      </footer>
    </div>
  );
}
