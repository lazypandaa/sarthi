import React, { useState, useEffect } from 'react'
import { Edit2, Save, X, User, Mail, MapPin, Globe, Calendar, MessageSquare, TrendingUp, Activity } from 'lucide-react'
import axios from 'axios'
import { getTranslation } from './translations'
import Navbar from './Navbar'
import './ProfileMobile.css'

function Profile({ user, onBack, onUserUpdate, onLogout, onNavigate }) {
  const t = (key) => getTranslation(user?.language || 'en', key)
  const [isEditing, setIsEditing] = useState(false)
  const [editData, setEditData] = useState({
    phone_number: user?.phone_number || '',
    language: user?.language || 'en',
    location: user?.location || ''
  })
  const [queries, setQueries] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [stats, setStats] = useState({ total: 0, thisWeek: 0, types: {} })

  useEffect(() => {
    fetchUserQueries()
  }, [])

  const fetchUserQueries = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get('http://localhost:8000/api/query-history', {
        headers: { Authorization: `Bearer ${token}` }
      })
      const queriesData = response.data.queries || []
      setQueries(queriesData)
      calculateStats(queriesData)
    } catch (err) {
      console.error('Failed to fetch queries:', err)
    }
  }

  const calculateStats = (queriesData) => {
    const now = new Date()
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    const thisWeek = queriesData.filter(q => new Date(q.timestamp) > weekAgo).length
    const types = queriesData.reduce((acc, q) => {
      acc[q.type] = (acc[q.type] || 0) + 1
      return acc
    }, {})
    setStats({ total: queriesData.length, thisWeek, types })
  }

  const handleSave = async () => {
    setLoading(true)
    setError('')
    try {
      const token = localStorage.getItem('token')
      await axios.put('http://localhost:8000/api/profile', editData, {
        headers: { Authorization: `Bearer ${token}` }
      })
      onUserUpdate(editData)
      setIsEditing(false)
    } catch (err) {
      setError('Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setEditData({
      phone_number: user?.phone_number || '',
      language: user?.language || 'en',
      location: user?.location || ''
    })
    setIsEditing(false)
    setError('')
  }

  const handleNavigate = (page) => {
    if (onNavigate) {
      onNavigate(page)
    }
  }

  const getTypeColor = (type) => {
    const colors = {
      voice: '#8b5cf6',
      text: '#06b6d4',
      weather: '#f59e0b',
      crop: '#10b981',
      schemes: '#ef4444'
    }
    return colors[type] || '#6b7280'
  }

  return (
    <div className="profile-container">
      <Navbar user={user} activePage="profile" onNavigate={handleNavigate} onLogout={onLogout} language={user?.language || 'en'} />
      
      <div className="profile-content-wrapper">
        {/* Profile Header */}
        <div className="profile-header">
          <div className="profile-avatar">
            <User size={32} />
          </div>
          <h1 className="profile-header-title">{t('myProfile')}</h1>
          <p className="profile-header-subtitle">Manage your personal details</p>
          
          {!isEditing && (
            <button onClick={() => setIsEditing(true)} className="profile-edit-button">
              <Edit2 size={16} />
              Edit Profile
            </button>
          )}
        </div>

        {error && <div className="profile-error">{error}</div>}

        {/* Desktop 2-Column Grid */}
        <div className="profile-main-grid">
          {/* Left Column - User Information */}
          <div className="profile-left-column">
            {/* Profile Details List */}
            <div className="profile-list">
          {/* Phone Number */}
          <div className={`profile-list-item ${isEditing ? 'editing' : ''}`}>
            <div className="profile-item-icon">
              <User size={20} />
            </div>
            <div className="profile-item-content">
              <p className="profile-item-label">{t('phoneNumber')}</p>
              <p className="profile-item-value">{user?.phone_number}</p>
            </div>
          </div>

          {/* Language */}
          <div className={`profile-list-item ${isEditing ? 'editing' : ''}`}>
            <div className="profile-item-icon">
              <Globe size={20} />
            </div>
            <div className="profile-item-content">
              <p className="profile-item-label">{t('language')}</p>
              {isEditing ? (
                <select
                  value={editData.language}
                  onChange={(e) => setEditData({...editData, language: e.target.value})}
                  className="field-select"
                >
                  <option value="en">🇺🇸 English</option>
                  <option value="hi">🇮🇳 Hindi</option>
                  <option value="ta">🇮🇳 Tamil</option>
                  <option value="te">🇮🇳 Telugu</option>
                  <option value="kn">🇮🇳 Kannada</option>
                  <option value="ml">🇮🇳 Malayalam</option>
                  <option value="bn">🇮🇳 Bengali</option>
                  <option value="gu">🇮🇳 Gujarati</option>
                  <option value="mr">🇮🇳 Marathi</option>
                </select>
              ) : (
                <p className="profile-item-value">
                  {editData.language === 'en' && '🇺🇸 English'}
                  {editData.language === 'hi' && '🇮🇳 Hindi'}
                  {editData.language === 'ta' && '🇮🇳 Tamil'}
                  {editData.language === 'te' && '🇮🇳 Telugu'}
                  {editData.language === 'kn' && '🇮🇳 Kannada'}
                  {editData.language === 'ml' && '🇮🇳 Malayalam'}
                  {editData.language === 'bn' && '🇮🇳 Bengali'}
                  {editData.language === 'gu' && '🇮🇳 Gujarati'}
                  {editData.language === 'mr' && '🇮🇳 Marathi'}
                </p>
              )}
            </div>
          </div>

          {/* Location */}
          <div className={`profile-list-item ${isEditing ? 'editing' : ''}`}>
            <div className="profile-item-icon">
              <MapPin size={20} />
            </div>
            <div className="profile-item-content">
              <p className="profile-item-label">{t('location')}</p>
              {isEditing ? (
                <input
                  type="text"
                  value={editData.location}
                  onChange={(e) => setEditData({...editData, location: e.target.value})}
                  placeholder="City, State"
                  className="field-input"
                />
              ) : (
                <p className="profile-item-value">📍 {user?.location}</p>
              )}
            </div>
          </div>
        </div>

            {/* Edit Actions */}
            {isEditing && (
              <div className="profile-edit-actions">
                <button onClick={handleSave} disabled={loading} className="profile-save-button">
                  <Save size={16} />
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
                <button onClick={handleCancel} className="profile-cancel-button">
                  <X size={16} />
                </button>
              </div>
            )}
          </div>

          {/* Right Column - Activity & Stats */}
          <div className="profile-right-column">
            {/* Activity Stats */}
            <div className="profile-activity-section">
          <h2 className="profile-section-title">{t('activityStats')}</h2>
          
          <div className="profile-stats-grid">
            <div className="profile-stat-card">
              <div className="profile-stat-icon">
                <Activity size={20} />
              </div>
              <div className="profile-stat-number">{stats.total}</div>
              <div className="profile-stat-label">{t('totalQueries')}</div>
            </div>
            
            <div className="profile-stat-card">
              <div className="profile-stat-icon">
                <Calendar size={20} />
              </div>
              <div className="profile-stat-number">{stats.thisWeek}</div>
              <div className="profile-stat-label">{t('thisWeek')}</div>
            </div>
          </div>
        </div>
          </div>
        </div>

        {/* Question Feed - Full Width */}
        <div className="profile-question-feed">
          {/* Query History */}
          <div className="profile-activity-section">
          <h2 className="profile-section-title">{t('queryHistory')}</h2>
          
          {queries.length === 0 ? (
            <div className="profile-empty-state">
              <div className="profile-empty-icon">💬</div>
              <h4 className="profile-empty-title">{t('noQueries')}</h4>
              <p className="profile-empty-text">Start asking questions to see your history here!</p>
            </div>
          ) : (
            <div className="profile-query-list">
              {queries.slice(0, 10).map((query, index) => (
                <div key={index} className="profile-query-item">
                  <div className="profile-query-header">
                    <span 
                      className="profile-query-type" 
                      style={{backgroundColor: getTypeColor(query.type), color: 'white'}}
                    >
                      {query.type}
                    </span>
                    <span className="profile-query-time">
                      {new Date(query.timestamp).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                  <p className="profile-query-text">{query.query}</p>
                  {query.response && (
                    <p className="profile-query-response">
                      {query.response.length > 120 ? 
                        `${query.response.substring(0, 120)}...` : 
                        query.response
                      }
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
        </div>
      </div>
    </div>
  )
}

export default Profile
