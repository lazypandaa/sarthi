import React, { useState, useEffect } from 'react'
import { MapPin, Droplets, Wind, CloudRain, AlertTriangle, Sprout, TrendingUp, ExternalLink, ChevronDown, User, Users, LogOut } from 'lucide-react'
import axios from 'axios'
import Navbar from './Navbar'
import { getTranslation } from './translations'
import './Advisor.css'

function Advisor({ user, onLogout, onNavigate, onOpenVoiceAssistant }) {
  const t = (key) => getTranslation(user?.language || 'en', key)
  const [loading, setLoading] = useState(true)
  const [weather, setWeather] = useState(null)
  const [crops, setCrops] = useState([])
  const [strategies, setStrategies] = useState([])
  const [news, setNews] = useState([])
  const [showAllCrops, setShowAllCrops] = useState(false)
  const [showAllStrategies, setShowAllStrategies] = useState(false)
  const [showAllNews, setShowAllNews] = useState(false)
  const [loadingNews, setLoadingNews] = useState(false)
  const [loadingQuote] = useState(() => {
    const quotes = [
      'Farming is a profession of hope.',
      'The farmer is the backbone of our nation.',
      'Good farming is 90% observation.',
      'The land never lies.'
    ]
    return quotes[Math.floor(Math.random() * quotes.length)]
  })
  const [loadingMessage] = useState(() => {
    const messages = [
      'Analyzing your farm conditions...',
      'Preparing personalized farming insights...'
    ]
    return messages[Math.floor(Math.random() * messages.length)]
  })

  const handleNavigate = (page) => {
    if (onNavigate) {
      onNavigate(page)
    }
  }

  useEffect(() => {
    fetchAdvisorData()
    fetchNews()
  }, [])

  const fetchAdvisorData = async () => {
    try {
      const token = localStorage.getItem('token')
      
      // Fetch weather
      const weatherRes = await axios.get('http://localhost:8000/api/weather', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setWeather({
        location: user?.location?.split(',')[0] || t('yourLocation'),
        temperature: weatherRes.data.temperature,
        humidity: weatherRes.data.humidity,
        rainfall: weatherRes.data.rainfall || t('none'),
        description: weatherRes.data.condition,
        hasRain: weatherRes.data.rainfall > 0
      })
      
      // Fetch crops
      const cropsRes = await axios.get('http://localhost:8000/api/crop-recommendations', {
        headers: { Authorization: `Bearer ${token}` }
      })
      const cropsData = cropsRes.data.map(crop => ({
        name: crop.crop_name,
        explanation: crop.climate_match,
        water_requirement: crop.water_requirement,
        yield_potential: t('high')
      }))
      setCrops(cropsData)
      
      // Fetch strategies
      const stratRes = await axios.get('http://localhost:8000/api/optimization-strategies', {
        headers: { Authorization: `Bearer ${token}` }
      })
      const stratData = stratRes.data.map((s, idx) => {
        const icons = ['💧', '🌱', '🚜', '📊', '🌾', '⚡']
        return {
          icon: icons[idx % icons.length],
          title: s.strategy_name,
          benefit: `${t('impact')}: ${s.impact_level} | ${t('difficulty')}: ${s.difficulty}`,
          reason: `${t('costEffectiveness')}: ${s.cost_effectiveness}`,
          link: 'https://agricoop.gov.in'
        }
      })
      setStrategies(stratData)
      
    } catch (err) {
      console.error('Advisor data error:', err)
      setWeather({
        location: user?.location?.split(',')[0] || 'Your Area',
        temperature: 28,
        humidity: 65,
        rainfall: 'None',
        description: 'partly cloudy',
        hasRain: false
      })
    } finally {
      setLoading(false)
    }
  }

  const displayedCrops = showAllCrops ? crops : crops.slice(0, 3)
  const displayedStrategies = showAllStrategies ? strategies : strategies.slice(0, 3)
  const displayedNews = showAllNews ? news : news.slice(0, 3)

  const fetchNews = async () => {
    setLoadingNews(true)
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get('http://localhost:8000/api/agriculture-news', {
        headers: { Authorization: `Bearer ${token}` }
      })
      const newsData = response.data.map(n => ({
        title: n.title,
        summary: n.summary,
        source: n.source,
        url: n.link,
        image: n.image || `https://source.unsplash.com/400x200/?agriculture,farming,${encodeURIComponent(n.title.split(' ')[0])}`
      }))
      setNews(newsData)
    } catch (err) {
      console.error('News fetch error:', err)
    } finally {
      setLoadingNews(false)
    }
  }

  if (loading) {
    return (
      <div className="advisor-container">
        <Navbar user={user} activePage="advisor" onNavigate={handleNavigate} onLogout={onLogout} language={user.language} />
        <div className="advisor-loading">
          <div className="loading-logo">🌾</div>
          <div className="loading-quote">"{loadingQuote}"</div>
          <div className="loading-message">{loadingMessage}</div>
          <div className="loading-spinner"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="advisor-container">
      <Navbar user={user} activePage="advisor" onNavigate={handleNavigate} onLogout={onLogout} language={user.language} />

      <div className="advisor-content">
        <div className="advisor-header">
          <h1>🌾 {t('farmAdvisor')}</h1>
          <p>{t('personalizedRecommendations')}</p>
        </div>

        {/* Weather & Alerts Section */}
        <section className="advisor-section">
          <h2>
            <CloudRain size={24} />
            {t('weatherAlerts')}
          </h2>
          
          {weather && (
            <div className="weather-card">
              <div className="weather-header">
                <MapPin size={20} />
                <h3>{t('weatherIn')} {weather.location}</h3>
              </div>
              
              <div className="weather-stats">
                <div className="weather-stat">
                  <Wind size={20} />
                  <div>
                    <div className="stat-value">{weather.temperature}°C</div>
                    <div className="stat-label">{t('temperature')}</div>
                  </div>
                </div>
                
                <div className="weather-stat">
                  <Droplets size={20} />
                  <div>
                    <div className="stat-value">{weather.humidity}%</div>
                    <div className="stat-label">{t('humidity')}</div>
                  </div>
                </div>
                
                <div className="weather-stat">
                  <CloudRain size={20} />
                  <div>
                    <div className="stat-value">{weather.rainfall}</div>
                    <div className="stat-label">{t('rainfall')}</div>
                  </div>
                </div>
              </div>

              {weather.hasRain && (
                <div className="weather-alert">
                  <AlertTriangle size={20} />
                  <div>
                    <strong>{t('rainExpected')}</strong>
                    <p>{t('postponeFertilizer')}</p>
                  </div>
                </div>
              )}

              {weather.humidity > 70 && (
                <div className="weather-impact">
                  <p>⚠️ {t('highHumidityWarning')}</p>
                </div>
              )}
            </div>
          )}
        </section>

        {/* Agriculture News Section */}
        <section className="advisor-section">
          <h2>
            <TrendingUp size={24} />
            {t('agricultureNews')}
          </h2>
          
          {loadingNews ? (
            <div className="news-loading">{t('loadingNews')}</div>
          ) : (
            <>
              <div className="news-grid">
                {displayedNews.map((article, index) => (
                  <div key={index} className="news-card">
                    {article.image && (
                      <img src={article.image} alt={article.title} className="news-image" />
                    )}
                    <h3>{article.title}</h3>
                    <p className="news-summary">{article.summary}</p>
                    <div className="news-footer">
                      <span className="news-source">{article.source}</span>
                      <a href={article.url} target="_blank" rel="noopener noreferrer" className="news-link">
                        {t('readMore')} <ExternalLink size={14} />
                      </a>
                    </div>
                  </div>
                ))}
              </div>

              {news.length > 3 && (
                <button 
                  className="explore-more-btn"
                  onClick={() => setShowAllNews(!showAllNews)}
                >
                  {showAllNews ? t('showLess') : t('exploreMore')}
                  <ChevronDown size={18} style={{ transform: showAllNews ? 'rotate(180deg)' : 'none' }} />
                </button>
              )}
            </>
          )}
        </section>

        {/* Crop Recommendations Section */}
        <section className="advisor-section">
          <h2>
            <Sprout size={24} />
            {t('cropRecommendations')}
          </h2>
          
          <div className="crops-grid">
            {displayedCrops.map((crop, index) => (
              <div key={index} className="crop-card">
                <h3>{crop.name}</h3>
                <p className="crop-explanation">{crop.explanation}</p>
                
                <div className="crop-details">
                  <div className="crop-detail">
                    <Droplets size={16} />
                    <span>{t('water')}: {crop.water_requirement}</span>
                  </div>
                  <div className="crop-detail">
                    <TrendingUp size={16} />
                    <span>{t('yield')}: {crop.yield_potential}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {crops.length > 3 && (
            <button 
              className="explore-more-btn"
              onClick={() => setShowAllCrops(!showAllCrops)}
            >
              {showAllCrops ? t('showLess') : t('exploreMore')}
              <ChevronDown size={18} style={{ transform: showAllCrops ? 'rotate(180deg)' : 'none' }} />
            </button>
          )}
        </section>

        {/* Farming Strategies Section */}
        <section className="advisor-section">
          <h2>
            <TrendingUp size={24} />
            {t('farmingStrategies')}
          </h2>
          
          <div className="strategies-grid">
            {displayedStrategies.map((strategy, index) => (
              <div key={index} className="strategy-card">
                <div className="strategy-icon">{strategy.icon}</div>
                <h3>{strategy.title}</h3>
                <p className="strategy-benefit">{strategy.benefit}</p>
                <p className="strategy-reason">{strategy.reason}</p>
                {strategy.link && (
                  <a href={strategy.link} target="_blank" rel="noopener noreferrer" className="strategy-link">
                    {t('learnMore')} <ExternalLink size={14} />
                  </a>
                )}
              </div>
            ))}
          </div>

          {strategies.length > 3 && (
            <button 
              className="explore-more-btn"
              onClick={() => setShowAllStrategies(!showAllStrategies)}
            >
              {showAllStrategies ? t('showLess') : t('exploreMore')}
              <ChevronDown size={18} style={{ transform: showAllStrategies ? 'rotate(180deg)' : 'none' }} />
            </button>
          )}
        </section>
      </div>
    </div>
  )
}

export default Advisor
