import React, { useState, useEffect } from 'react'
import { Users, TrendingUp, AlertTriangle, Award, CheckCircle, X, Send, MapPin, Search, Filter, ShieldCheck, Flame } from 'lucide-react'
import axios from 'axios'
import { API_URL } from './config'
import { getTranslation } from './translations'
import Navbar from './Navbar'
import './Community.css'

function Community({ user, onBack, onLogout, onNavigate }) {
  const t = (key) => getTranslation(user?.language || 'en', key)
  const [activeTab, setActiveTab] = useState('reports')
  const [reports, setReports] = useState([])
  const [leaderboard, setLeaderboard] = useState([])
  const [outbreaks, setOutbreaks] = useState([])
  const [summaryStats, setSummaryStats] = useState({ totalReports: 0, affectedVillages: 0 })
  const [filterCategory, setFilterCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [showReportModal, setShowReportModal] = useState(false)
  const [newReport, setNewReport] = useState({
    village_id: user?.location ? user.location.split(',')[0].trim() : 'Sehore',
    report_type: 'pest',
    crop: '',
    description: '',
    severity: 'medium',
    language: user?.language || 'en'
  })

  const handleNavigate = (page) => {
    if (onNavigate) {
      onNavigate(page)
    }
  }

  useEffect(() => {
    fetchCommunityData()
  }, [activeTab])

  const fetchCommunityData = async () => {
    const token = localStorage.getItem('token')
    try {
      if (activeTab === 'reports') {
        const res = await axios.get(`${API_URL}/api/community-reports?limit=50`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        setReports(res.data.reports || [])
      } else if (activeTab === 'outbreaks') {
        const res = await axios.get(`${API_URL}/api/outbreak-map?language=${user?.language || 'en'}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        setOutbreaks(res.data.outbreaks || [])
        setSummaryStats({
          totalReports: res.data.total_reports || 0,
          affectedVillages: res.data.affected_villages || 0
        })
      } else if (activeTab === 'leaderboard') {
        const res = await axios.get(`${API_URL}/api/village-leaderboard`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        setLeaderboard(res.data.leaderboard || [])
      }
    } catch (err) {
      console.error('Fetch error:', err)
    }
  }

  const submitReport = async () => {
    if (!newReport.description.trim()) return
    
    const token = localStorage.getItem('token')
    try {
      const res = await axios.post(`${API_URL}/api/community-report`, newReport, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (res.data.outbreak_alert) {
        alert(`⚠️ Outbreak Alert! ${res.data.similar_reports} similar reports in your area.`)
      }
      
      setShowReportModal(false)
      setNewReport({
        village_id: user?.location ? user.location.split(',')[0].trim() : 'Sehore',
        report_type: 'pest',
        crop: '',
        description: '',
        severity: 'medium',
        language: user?.language || 'en'
      })
      fetchCommunityData()
    } catch (err) {
      console.error('Submit error:', err)
    }
  }

  const validateReport = async (reportId, helpful) => {
    const token = localStorage.getItem('token')
    try {
      await axios.post(`${API_URL}/api/validate-report/${reportId}`, { helpful }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      fetchCommunityData()
    } catch (err) {
      console.error('Validation error:', err)
    }
  }

  // Filter and search reports
  const filteredReports = reports.filter(r => {
    const matchesCategory = filterCategory === 'all' || r.report_type === filterCategory
    const q = searchQuery.toLowerCase().trim()
    const matchesSearch = !q ||
      (r.crop && r.crop.toLowerCase().includes(q)) ||
      (r.village_id && r.village_id.toLowerCase().includes(q)) ||
      (r.description && r.description.toLowerCase().includes(q)) ||
      (r.description_english && r.description_english.toLowerCase().includes(q))
    return matchesCategory && matchesSearch
  })

  // Counts for tabs/pills
  const pestCount = reports.filter(r => r.report_type === 'pest').length
  const diseaseCount = reports.filter(r => r.report_type === 'disease').length
  const weatherCount = reports.filter(r => r.report_type === 'weather').length
  const successCount = reports.filter(r => r.report_type === 'success').length

  return (
    <div className="community-container">
      <Navbar user={user} activePage="community" onNavigate={handleNavigate} onLogout={onLogout} language={user?.language || 'en'} />

      <div className="community-content">
        <div className="community-header">
          <div className="community-header-badge">
            <ShieldCheck size={16} /> Verified Agricultural Intelligence
          </div>
          <h1>🌾 {t('communityTitle')}</h1>
          <p>{t('communitySubtitle')}</p>
          <button className="report-btn" onClick={() => setShowReportModal(true)}>
            <Send size={18} />
            {t('submitReport')}
          </button>
        </div>

        <div className="community-tabs">
          <button className={`tab ${activeTab === 'reports' ? 'active' : ''}`} onClick={() => setActiveTab('reports')}>
            <MapPin size={18} />
            {t('villageReports')}
            <span className="tab-pill-count">{reports.length}</span>
          </button>
          <button className={`tab ${activeTab === 'outbreaks' ? 'active' : ''}`} onClick={() => setActiveTab('outbreaks')}>
            <AlertTriangle size={18} />
            {t('outbreakMap')}
            <span className="tab-pill-pulse">LIVE</span>
          </button>
          <button className={`tab ${activeTab === 'leaderboard' ? 'active' : ''}`} onClick={() => setActiveTab('leaderboard')}>
            <Award size={18} />
            {t('leaderboard')}
          </button>
        </div>

        <div className="community-body">
          {/* TAB 1: VILLAGE REPORTS */}
          {activeTab === 'reports' && (
            <div className="reports-section">
              {/* Filter and Search Bar */}
              <div className="reports-toolbar">
                <div className="search-box">
                  <Search size={18} className="search-icon" />
                  <input
                    type="text"
                    placeholder="Search by crop, pest, or village (e.g. Soybean, Guntur, Thrips)..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  {searchQuery && (
                    <button className="clear-search-btn" onClick={() => setSearchQuery('')}>×</button>
                  )}
                </div>

                <div className="category-pills">
                  <button
                    className={`filter-pill ${filterCategory === 'all' ? 'active' : ''}`}
                    onClick={() => setFilterCategory('all')}
                  >
                    All ({reports.length})
                  </button>
                  <button
                    className={`filter-pill pest ${filterCategory === 'pest' ? 'active' : ''}`}
                    onClick={() => setFilterCategory('pest')}
                  >
                    🐛 Pests ({pestCount})
                  </button>
                  <button
                    className={`filter-pill disease ${filterCategory === 'disease' ? 'active' : ''}`}
                    onClick={() => setFilterCategory('disease')}
                  >
                    🦠 Diseases ({diseaseCount})
                  </button>
                  <button
                    className={`filter-pill weather ${filterCategory === 'weather' ? 'active' : ''}`}
                    onClick={() => setFilterCategory('weather')}
                  >
                    🌦️ Weather ({weatherCount})
                  </button>
                  <button
                    className={`filter-pill success ${filterCategory === 'success' ? 'active' : ''}`}
                    onClick={() => setFilterCategory('success')}
                  >
                    ✅ Success Stories ({successCount})
                  </button>
                </div>
              </div>

              {filteredReports.length === 0 ? (
                <div className="empty-state">
                  <p>No reports matching your filter or search query.</p>
                </div>
              ) : (
                <div className="reports-grid">
                  {filteredReports.map(report => (
                    <div key={report.report_id} className={`report-card ${report.report_type}`}>
                      <div className="report-header">
                        <div className="report-header-left">
                          <span className={`report-type ${report.report_type}`}>
                            {report.report_type === 'pest' && '🐛 Pest Sighting'}
                            {report.report_type === 'disease' && '🦠 Crop Disease'}
                            {report.report_type === 'weather' && '🌦️ Weather Alert'}
                            {report.report_type === 'success' && '✅ Farmer Success'}
                          </span>
                          <span className="village-badge">
                            📍 {report.village_id}
                          </span>
                        </div>
                        <span className={`severity ${report.severity}`}>{t(report.severity)}</span>
                      </div>

                      <div className="report-crop-row">
                        <span className="crop-label">Crop:</span>
                        <span className="crop-name">{report.crop || 'Field Observation'}</span>
                      </div>

                      <p className="report-desc">{report.description_english || report.description}</p>

                      <div className="report-footer">
                        <div className="report-meta">
                          <span className="report-time">
                            {new Date(report.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                          </span>
                          {report.verified ? (
                            <span className="verified-pill">✓ Verified</span>
                          ) : (
                            <span className="unverified-pill">⏳ Peer review</span>
                          )}
                        </div>

                        <div className="validation-section">
                          <span className="validation-count" title="Number of farmer peer endorsements">
                            👍 {report.validation_count || 0}
                          </span>
                          <div className="validation-actions">
                            <button
                              className="val-btn up"
                              title="Helpful & Accurate"
                              onClick={() => validateReport(report.report_id, true)}
                            >
                              👍
                            </button>
                            <button
                              className="val-btn down"
                              title="Not Accurate"
                              onClick={() => validateReport(report.report_id, false)}
                            >
                              👎
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 2: OUTBREAK MAP & HOTSPOTS */}
          {activeTab === 'outbreaks' && (
            <div className="outbreaks-section">
              {/* Outbreak Intelligence KPI Cards */}
              <div className="outbreak-kpis">
                <div className="kpi-card danger">
                  <div className="kpi-icon"><Flame size={24} /></div>
                  <div className="kpi-details">
                    <span className="kpi-number">{outbreaks.filter(o => o.alert_level === 'high').length}</span>
                    <span className="kpi-label">High-Risk Outbreak Zones</span>
                  </div>
                </div>

                <div className="kpi-card warning">
                  <div className="kpi-icon"><AlertTriangle size={24} /></div>
                  <div className="kpi-details">
                    <span className="kpi-number">{outbreaks.length}</span>
                    <span className="kpi-label">Active Regional Clusters</span>
                  </div>
                </div>

                <div className="kpi-card info">
                  <div className="kpi-icon"><ShieldCheck size={24} /></div>
                  <div className="kpi-details">
                    <span className="kpi-number">{summaryStats.totalReports || reports.length || 25}</span>
                    <span className="kpi-label">Monitored Field Points</span>
                  </div>
                </div>
              </div>

              {outbreaks.length === 0 ? (
                <div className="empty-state">
                  <p>✅ {t('noOutbreaks')}</p>
                </div>
              ) : (
                <div className="outbreaks-grid">
                  {outbreaks.map((outbreak, idx) => (
                    <div key={idx} className={`outbreak-card ${outbreak.alert_level}`}>
                      <div className="outbreak-header">
                        <div>
                          <h3>⚠️ {outbreak.village}</h3>
                          <span className="outbreak-state">{outbreak.state || 'India'}</span>
                        </div>
                        <span className={`alert-badge ${outbreak.alert_level}`}>
                          {outbreak.alert_level === 'high' ? '🚨 High Alert' : outbreak.alert_level === 'medium' ? '⚠️ Medium Risk' : 'ℹ️ Monitored'}
                        </span>
                      </div>

                      <div className="outbreak-stats">
                        <div className="stat-pill pest">
                          <span className="stat-num">{outbreak.pest_count}</span>
                          <span className="stat-text">Pest Alerts</span>
                        </div>
                        <div className="stat-pill disease">
                          <span className="stat-num">{outbreak.disease_count}</span>
                          <span className="stat-text">Disease Alerts</span>
                        </div>
                        <div className="stat-pill total">
                          <span className="stat-num">{outbreak.total_reports}</span>
                          <span className="stat-text">Total Sightings</span>
                        </div>
                      </div>

                      {outbreak.crops_affected && outbreak.crops_affected.length > 0 && (
                        <div className="outbreak-crops">
                          <span className="crops-label">Crops Threatened:</span>
                          <div className="crop-pills">
                            {outbreak.crops_affected.map((c, i) => (
                              <span key={i} className="crop-pill-tag">🌱 {c}</span>
                            ))}
                          </div>
                        </div>
                      )}

                      {outbreak.recent_reports && outbreak.recent_reports.length > 0 && (
                        <div className="outbreak-recent">
                          <span className="recent-title">Recent Threats Logged:</span>
                          <ul className="threat-list">
                            {outbreak.recent_reports.slice(0, 3).map((r, ri) => (
                              <li key={ri} className="threat-item">
                                <span className={`threat-icon ${r.type}`}>
                                  {r.type === 'pest' ? '🐛' : '🦠'}
                                </span>
                                <div className="threat-text">
                                  <strong>{r.crop}:</strong> {r.description}
                                </div>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: VILLAGE TRUST LEADERBOARD */}
          {activeTab === 'leaderboard' && (
            <div className="leaderboard-section">
              <div className="leaderboard-explainer">
                <ShieldCheck size={20} className="explainer-icon" />
                <div>
                  <strong>Village Agricultural Reliability Index:</strong> Community trust scores are calculated dynamically from verified field sightings, multi-farmer peer validations, and advisory outcomes across regions.
                </div>
              </div>

              <div className="leaderboard-list">
                {leaderboard.length === 0 ? (
                  <div className="empty-state">
                    <p>Loading village trust scores...</p>
                  </div>
                ) : (
                  leaderboard.map((item, index) => (
                    <div key={index} className={`leaderboard-item ${item.tier ? item.tier.toLowerCase() : 'bronze'}`}>
                      <div className="rank">#{item.rank || index + 1}</div>
                      <div className="tier-icon">{item.tier_icon || '🥇'}</div>
                      <div className="village-info">
                        <h3>{item.village_id}</h3>
                        <p>{item.total_responses || item.helpful_count} total validated community interactions</p>
                        <div className="trust-meter-wrapper">
                          <div
                            className="trust-meter-fill"
                            style={{ width: `${Math.min(100, Math.max(0, item.trust_score || 90))}%` }}
                          />
                        </div>
                      </div>
                      <div className="leaderboard-score">
                        <div className="score-number">{Number(item.trust_score || 0).toFixed(1)}%</div>
                        <span className="tier-badge">{item.tier || 'Gold'} Trust</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {showReportModal && (
        <div className="modal-overlay" onClick={() => setShowReportModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>📝 {t('submitReport')}</h3>
              <button className="close-button" onClick={() => setShowReportModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <label>Village / District</label>
              <input
                type="text"
                value={newReport.village_id}
                onChange={(e) => setNewReport({...newReport, village_id: e.target.value})}
                placeholder="e.g., Sehore, Guntur, Nashik"
              />

              <label>{t('reportType')}</label>
              <select value={newReport.report_type} onChange={(e) => setNewReport({...newReport, report_type: e.target.value})}>
                <option value="pest">🐛 Pest Sighting</option>
                <option value="disease">🦠 Crop Disease</option>
                <option value="weather">🌦️ Weather Observation</option>
                <option value="success">✅ Success Story</option>
              </select>

              <label>{t('crop')} (optional)</label>
              <input
                type="text"
                value={newReport.crop}
                onChange={(e) => setNewReport({...newReport, crop: e.target.value})}
                placeholder="e.g., Soybean, Chilli, Onion, Wheat"
              />

              <label>{t('severity')}</label>
              <select value={newReport.severity} onChange={(e) => setNewReport({...newReport, severity: e.target.value})}>
                <option value="low">{t('low')}</option>
                <option value="medium">{t('medium')}</option>
                <option value="high">{t('high')}</option>
              </select>

              <label>{t('description')}</label>
              <textarea
                value={newReport.description}
                onChange={(e) => setNewReport({...newReport, description: e.target.value})}
                placeholder="Describe what you observed in the field..."
                rows={4}
              />
            </div>
            <div className="modal-footer">
              <button className="cancel-button" onClick={() => setShowReportModal(false)}>{t('cancel')}</button>
              <button className="submit-button" onClick={submitReport}>{t('submitReport')}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Community
