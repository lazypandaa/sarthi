import { useState, useEffect } from "react";
import { api } from "../api";
import type { UserProfile } from "../api/types";

interface AuthScreenProps {
  onSuccess: (user: UserProfile) => void;
}

export function AuthScreen({ onSuccess }: AuthScreenProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [phone, setPhone] = useState("+919999999001");
  const [password, setPassword] = useState("demoPassword123!");
  const [language, setLanguage] = useState("hi");
  const [location, setLocation] = useState("Sehore, Madhya Pradesh, India");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detectingLoc, setDetectingLoc] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  const handleUseDemo = (demoPhone = "+919999999001", demoPass = "demoPassword123!") => {
    setIsLogin(true);
    setPhone(demoPhone);
    setPassword(demoPass);
    setError(null);
  };

  const handleDetectLocation = async () => {
    setDetectingLoc(true);
    setStatusMsg("Accessing GPS location...");
    try {
      if (navigator.geolocation) {
        const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
          navigator.geolocation.getCurrentPosition(resolve, reject, {
            enableHighAccuracy: true,
            timeout: 8000,
          });
        });
        const { latitude, longitude } = pos.coords;
        setStatusMsg("Resolving village address via backend...");
        const res = await api.reverseGeocode(latitude, longitude);
        if (res.address) {
          setLocation(res.address);
          setStatusMsg("GPS location detected!");
          setTimeout(() => setStatusMsg(null), 2500);
          return;
        }
      }
    } catch (e) {
      console.warn("GPS failed, falling back to IP location:", e);
    }

    try {
      setStatusMsg("Using regional location lookup...");
      const ipRes = await api.getLocation();
      if (ipRes.location && ipRes.location !== "Location not available") {
        setLocation(ipRes.location);
        setStatusMsg("Location detected!");
      } else {
        setLocation("Sehore, Madhya Pradesh, India");
        setStatusMsg("Defaulted to Sehore, MP");
      }
    } catch {
      setLocation("Sehore, Madhya Pradesh, India");
    } finally {
      setDetectingLoc(false);
      setTimeout(() => setStatusMsg(null), 2500);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isLogin) {
        await api.login(phone.trim(), password);
      } else {
        await api.signup({
          phone_number: phone.trim(),
          password,
          language,
          location: location.trim(),
        });
      }
      const me = await api.getMe();
      onSuccess(me);
    } catch (err: any) {
      console.error("Auth error:", err);
      setError(err?.message || "Authentication failed. Please verify credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card-box">
        {/* Brand Header */}
        <div className="auth-brand">
          <div className="auth-logo-badge">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M11 20A7 7 0 0 1 9.8 6.1C15 3 21 4 21 4s1 6-2.1 11.2A7 7 0 0 1 11 20Z" />
              <path d="M2 21c0-3 1.85-5.36 5.08-6.94 2.03-.99 4.27-1.29 6.92-.86" />
            </svg>
          </div>
          <h1>S A R T H I</h1>
          <p>Autonomous AI Agronomist with Hindsight Long-Term Memory</p>
        </div>

        {/* Demo Farmer Fast-Access Banner */}
        <div className="demo-credentials-banner">
          <div className="demo-info">
            <b>Seeded Demo Farmer</b>
            <small>+919999999001 (11 Hindsight Memories)</small>
          </div>
          <button
            type="button"
            className="demo-btn"
            onClick={() => handleUseDemo("+919999999001", "demoPassword123!")}
          >
            Fill Demo
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="auth-tabs">
          <button
            type="button"
            className={`auth-tab ${isLogin ? "active" : ""}`}
            onClick={() => {
              setIsLogin(true);
              setError(null);
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            className={`auth-tab ${!isLogin ? "active" : ""}`}
            onClick={() => {
              setIsLogin(false);
              setError(null);
            }}
          >
            Register New Farmer
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="auth-error-banner" role="alert">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        {statusMsg && (
          <div className="auth-status-banner">
            <span>{statusMsg}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="auth-form-fields">
          <div className="field-group">
            <label htmlFor="auth-phone">Mobile Phone Number</label>
            <div className="input-with-icon">
              <span className="field-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect width="14" height="20" x="5" y="2" rx="2" ry="2" />
                  <path d="M12 18h.01" />
                </svg>
              </span>
              <input
                id="auth-phone"
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+919999999001"
                required
                autoComplete="tel"
              />
            </div>
          </div>

          <div className="field-group">
            <label htmlFor="auth-password">Password</label>
            <div className="input-with-icon">
              <span className="field-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
              </span>
              <input
                id="auth-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                required
                autoComplete={isLogin ? "current-password" : "new-password"}
              />
            </div>
          </div>

          {!isLogin && (
            <>
              <div className="field-group">
                <label htmlFor="auth-language">Preferred Language</label>
                <select
                  id="auth-language"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="auth-select-field"
                >
                  <option value="hi">हिन्दी (Hindi)</option>
                  <option value="te">తెలుగు (Telugu)</option>
                  <option value="en">English (Indian)</option>
                  <option value="ta">தமிழ் (Tamil)</option>
                  <option value="kn">ಕನ್ನಡ (Kannada)</option>
                  <option value="mr">मराठी (Marathi)</option>
                </select>
              </div>

              <div className="field-group">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <label htmlFor="auth-location">Farm Village & District</label>
                  <button
                    type="button"
                    className="locate-btn"
                    onClick={handleDetectLocation}
                    disabled={detectingLoc}
                  >
                    {detectingLoc ? "Detecting..." : "Auto-Locate GPS"}
                  </button>
                </div>
                <div className="input-with-icon">
                  <span className="field-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" />
                      <circle cx="12" cy="10" r="3" />
                    </svg>
                  </span>
                  <input
                    id="auth-location"
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="Sehore, Madhya Pradesh, India"
                    required
                  />
                </div>
              </div>
            </>
          )}

          <button type="submit" className="auth-submit-btn" disabled={loading}>
            {loading ? (
              <span className="btn-spinner">Connecting to Sarthi...</span>
            ) : isLogin ? (
              "Sign In to Your Farm"
            ) : (
              "Register & Initialize Sarthi AI"
            )}
          </button>
        </form>

        <div className="auth-footer-note">
          <small>
            Protected by Azure Table Storage & Hindsight Memory Graph. Data is private and isolated to your farmer account.
          </small>
        </div>
      </div>
    </div>
  );
}
