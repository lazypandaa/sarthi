import React, { useState, useEffect } from 'react'
import { Users, TrendingUp, AlertTriangle, Award, CheckCircle, X, Send, MapPin } from 'lucide-react'
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
  const [showReportModal, setShowReportModal] = useState(false)
  const [newReport, setNewReport] = useState({
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
        const res = await axios.get(`${API_URL}/api/community-reports`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        setReports(res.data.reports || [])
      } else if (activeTab === 'outbreaks') {
        const res = await axios.get(`${API_URL}/api/outbreak-map?language=${user?.language || 'en'}`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        setOutbreaks(res.data.outbreaks || [])
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
      setNewReport({ report_type: 'pest', crop: '', description: '', severity: 'medium', language: user?.language || 'en' })
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

  return (
    <div className="community-container">
      <Navbar user={user} activePage="community" onNavigate={handleNavigate} onLogout={onLogout} language={user?.language || 'en'} />

      <div className="community-content">
        <div className="community-header">
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
          </button>
          <button className={`tab ${activeTab === 'outbreaks' ? 'active' : ''}`} onClick={() => setActiveTab('outbreaks')}>
            <AlertTriangle size={18} />
            {t('outbreakMap')}
          </button>
        </div>

        <div className="community-body">
          {activeTab === 'reports' && (
            <div className="reports-grid">
              {reports.length === 0 ? (
                <div className="empty-state">
                  <p>No reports yet. Be the first to share!</p>
                </div>
              ) : (
                reports.map(report => (
                  <div key={report.report_id} className="report-card">
                    <div className="report-header">
                      <span className={`report-type ${report.report_type}`}>
                        {report.report_type === 'pest' && '🐛'}
                        {report.report_type === 'disease' && '🦠'}
                        {report.report_type === 'weather' && '🌦️'}
                        {report.report_type === 'success' && '✅'}
                        {report.report_type}
                      </span>
                      <span className={`severity ${report.severity}`}>{t(report.severity)}</span>
                    </div>
                    <p className="report-crop">{t('crop')}: {report.crop}</p>
                    <p className="report-desc">{report.description}</p>
                    <div className="report-footer">
                      <span className="report-time">{new Date(report.timestamp).toLocaleDateString()}</span>
                      {report.verified && <span className="verified">✓ {t('verified')}</span>}
                      <div className="validation-actions">
                        <button onClick={() => validateReport(report.report_id, true)}>👍 {t('validate')}</button>
                        <button onClick={() => validateReport(report.report_id, false)}>👎</button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'outbreaks' && (
            <div className="outbreaks-grid">
              {outbreaks.length === 0 ? (
                <div className="empty-state">
                  <p>✅ {t('noOutbreaks')}</p>
                </div>
              ) : (
                outbreaks.map((outbreak, idx) => (
                  <div key={idx} className={`outbreak-card ${outbreak.alert_level}`}>
                    <div className="outbreak-header">
                      <h3>⚠️ {outbreak.village}</h3>
                      <span className={`alert-badge ${outbreak.alert_level}`}>{t(outbreak.alert_level)}</span>
                    </div>
                    <div className="outbreak-stats">
                      <span>🐛 {outbreak.pest_count} {t('pestReports')}</span>
                      <span>🦠 {outbreak.disease_count} {t('diseaseReports')}</span>
                    </div>
                    <p className="outbreak-total">{outbreak.total_reports} {t('totalReportsLast7Days')}</p>
                  </div>
                ))
              )}
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
                placeholder="e.g., Tomato, Wheat, Rice"
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
                placeholder="Describe what you observed..."
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
