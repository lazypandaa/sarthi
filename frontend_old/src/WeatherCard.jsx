import React from 'react'
import { MapPin, Droplets, CloudRain, Wind, AlertTriangle, RefreshCw, ShieldCheck } from 'lucide-react'
import { WeatherSkeleton } from './Skeletons'

function WeatherCard({ 
  weather, 
  loading = false, 
  onRefresh, 
  lastUpdatedText = 'Updated just now',
  isRefreshing = false 
}) {
  if (loading && !weather) {
    return <WeatherSkeleton />
  }

  if (!weather) return null

  const temp = weather.temperature !== undefined ? `${weather.temperature}°C` : '28°C'
  const humidity = weather.humidity !== undefined ? `${weather.humidity}%` : '65%'
  const rainfall = weather.rainfall || '0 mm'
  const location = weather.location || 'Your Farm'
  const description = weather.description || 'Clear skies'
  const warnings = weather.warnings || []
  const soilContext = weather.soilContext

  return (
    <div className="weather-card-mobile">
      {/* Top Header: Location, Updated Status, Refresh */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <MapPin size={16} color="#059669" />
          <span style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0f172a' }}>
            {location}
          </span>
          <span style={{ 
            fontSize: '0.68rem', 
            color: '#64748b', 
            background: '#f1f5f9', 
            padding: '2px 6px', 
            borderRadius: '4px' 
          }}>
            {lastUpdatedText}
          </span>
        </div>

        {onRefresh && (
          <button 
            type="button" 
            onClick={onRefresh}
            disabled={isRefreshing}
            className="interactive-tap"
            style={{
              background: 'transparent',
              border: 'none',
              padding: '4px',
              cursor: 'pointer',
              color: '#64748b',
              display: 'flex',
              alignItems: 'center'
            }}
            title="Refresh weather"
            aria-label="Refresh weather data"
          >
            <RefreshCw size={14} className={isRefreshing ? 'loading-spin' : ''} />
          </button>
        )}
      </div>

      {/* Main Temp & Condition */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', margin: '10px 0 6px' }}>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
          <span style={{ fontSize: '2.1rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.03em' }}>
            {temp}
          </span>
          <span style={{ fontSize: '0.86rem', color: '#475569', fontWeight: 500, textTransform: 'capitalize' }}>
            {description}
          </span>
        </div>
        <div style={{ fontSize: '1.8rem' }}>
          {weather.hasRain ? '🌧️' : humidity > 70 ? '⛅' : '☀️'}
        </div>
      </div>

      {/* 3-Column Weather Stats */}
      <div className="weather-stats-row">
        <div className="weather-stat-cell">
          <Droplets size={16} color="#0284c7" />
          <span className="stat-val">{humidity}</span>
          <span className="stat-lbl">Humidity</span>
        </div>
        <div className="weather-stat-cell">
          <CloudRain size={16} color="#059669" />
          <span className="stat-val">{rainfall}</span>
          <span className="stat-lbl">Rainfall</span>
        </div>
        <div className="weather-stat-cell">
          <Wind size={16} color="#64748b" />
          <span className="stat-val">12 km/h</span>
          <span className="stat-lbl">Wind</span>
        </div>
      </div>

      {/* Agricultural Agromet Alerts */}
      {warnings.length > 0 && (
        <div style={{
          marginTop: '10px',
          padding: '8px 12px',
          background: '#fffbeb',
          border: '1px solid #fef3c7',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '8px',
          fontSize: '0.78rem',
          color: '#92400e'
        }}>
          <AlertTriangle size={15} color="#d97706" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <strong>Agromet Advisory Alert:</strong> {warnings.join(' • ')}
          </div>
        </div>
      )}

      {/* Humidity Risk if High */}
      {weather.humidity > 75 && warnings.length === 0 && (
        <div style={{
          marginTop: '8px',
          padding: '6px 10px',
          background: '#fff7ed',
          border: '1px solid #fed7aa',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '0.76rem',
          color: '#c2410c'
        }}>
          <span>⚠️</span>
          <span><strong>High Humidity Alert:</strong> Risk of fungal leaf spot. Inspect crop leaves before foliar spray.</span>
        </div>
      )}

      {/* Soil Ground Truth Strip */}
      {soilContext && (
        <div style={{
          marginTop: '8px',
          padding: '6px 10px',
          background: '#f0fdf4',
          border: '1px solid #bbf7d0',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '0.74rem',
          color: '#166534'
        }}>
          <ShieldCheck size={14} color="#16a34a" />
          <span><strong>Soil Baseline ({location}):</strong> {soilContext.soil_type || 'Fertile Loam'} • pH {soilContext.ph || '6.8'} • NPK Balanced</span>
        </div>
      )}
    </div>
  )
}

export default WeatherCard
