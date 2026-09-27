import React from 'react'

export function WeatherSkeleton() {
  return (
    <div className="weather-card-mobile" style={{ opacity: 0.9 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div className="skeleton skeleton-circle" style={{ width: '24px', height: '24px' }} />
          <div className="skeleton" style={{ width: '120px', height: '18px' }} />
        </div>
        <div className="skeleton" style={{ width: '60px', height: '14px', borderRadius: '12px' }} />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', margin: '14px 0 8px' }}>
        <div className="skeleton" style={{ width: '70px', height: '40px', borderRadius: '8px' }} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <div className="skeleton" style={{ width: '100px', height: '14px' }} />
          <div className="skeleton" style={{ width: '140px', height: '12px' }} />
        </div>
      </div>

      <div className="weather-stats-row">
        <div className="skeleton" style={{ height: '42px', borderRadius: '8px' }} />
        <div className="skeleton" style={{ height: '42px', borderRadius: '8px' }} />
        <div className="skeleton" style={{ height: '42px', borderRadius: '8px' }} />
      </div>
    </div>
  )
}

export function AdvisorySkeleton() {
  return (
    <div className="advisory-feed-card" style={{ opacity: 0.9 }}>
      <div className="skeleton" style={{ width: '100%', height: '120px' }} />
      <div style={{ padding: '14px' }}>
        <div className="skeleton" style={{ width: '90px', height: '16px', borderRadius: '10px', marginBottom: '8px' }} />
        <div className="skeleton" style={{ width: '85%', height: '18px', marginBottom: '6px' }} />
        <div className="skeleton" style={{ width: '100%', height: '13px', marginBottom: '4px' }} />
        <div className="skeleton" style={{ width: '70%', height: '13px', marginBottom: '10px' }} />
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <div className="skeleton" style={{ width: '80px', height: '12px' }} />
          <div className="skeleton" style={{ width: '60px', height: '12px' }} />
        </div>
      </div>
    </div>
  )
}

export function RecommendationSkeleton() {
  return (
    <div className="ai-recommendation-card" style={{ opacity: 0.9 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
        <div className="skeleton skeleton-circle" style={{ width: '20px', height: '20px', background: 'rgba(255,255,255,0.2)' }} />
        <div className="skeleton" style={{ width: '150px', height: '14px', background: 'rgba(255,255,255,0.2)' }} />
      </div>
      <div className="skeleton" style={{ width: '90%', height: '22px', background: 'rgba(255,255,255,0.25)', marginBottom: '8px' }} />
      <div className="skeleton" style={{ width: '100%', height: '14px', background: 'rgba(255,255,255,0.15)', marginBottom: '12px' }} />
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <div className="skeleton" style={{ width: '75%', height: '14px', background: 'rgba(255,255,255,0.2)' }} />
        <div className="skeleton" style={{ width: '80%', height: '14px', background: 'rgba(255,255,255,0.2)' }} />
      </div>
    </div>
  )
}

export function CropCardSkeleton() {
  return (
    <div className="crop-card-mobile" style={{ opacity: 0.9 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
        <div className="skeleton" style={{ width: '110px', height: '18px' }} />
        <div className="skeleton" style={{ width: '60px', height: '16px', borderRadius: '10px' }} />
      </div>
      <div className="skeleton" style={{ width: '100%', height: '50px', borderRadius: '8px', marginBottom: '8px' }} />
      <div style={{ display: 'flex', gap: '6px' }}>
        <div className="skeleton" style={{ width: '70px', height: '22px', borderRadius: '6px' }} />
        <div className="skeleton" style={{ width: '70px', height: '22px', borderRadius: '6px' }} />
      </div>
    </div>
  )
}
