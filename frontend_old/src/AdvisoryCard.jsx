import React from 'react'
import { MapPin, Calendar, ExternalLink, ArrowRight } from 'lucide-react'

function AdvisoryCard({ advisory, onSelect }) {
  if (!advisory) return null

  const categoryColor = {
    'weather': { bg: '#eff6ff', text: '#1d4ed8', border: '#bfdbfe' },
    'disease': { bg: '#fef2f2', text: '#b91c1c', border: '#fecaca' },
    'market': { bg: '#f0fdf4', text: '#15803d', border: '#bbf7d0' },
    'schemes': { bg: '#fdf4ff', text: '#86198f', border: '#f5d0fe' }
  }[advisory.category?.toLowerCase()] || { bg: '#f1f5f9', text: '#475569', border: '#e2e8f0' }

  return (
    <div 
      className="advisory-feed-card interactive-tap"
      onClick={() => onSelect ? onSelect(advisory) : (advisory.url && advisory.url !== '#' && window.open(advisory.url, '_blank'))}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && (onSelect ? onSelect(advisory) : (advisory.url && window.open(advisory.url, '_blank')))}
    >
      {advisory.image && (
        <img 
          src={advisory.image} 
          alt={advisory.title} 
          className="advisory-card-img" 
          loading="lazy"
          onError={(e) => {
            e.target.style.display = 'none'
          }}
        />
      )}

      <div className="advisory-card-body">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
          <span style={{
            fontSize: '0.68rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            padding: '2px 8px',
            borderRadius: '6px',
            background: categoryColor.bg,
            color: categoryColor.text,
            border: `1px solid ${categoryColor.border}`
          }}>
            {advisory.category || 'Agricultural Advisory'}
          </span>

          <span style={{ fontSize: '0.72rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '3px' }}>
            <Calendar size={12} />
            {advisory.date ? new Date(advisory.date).toLocaleDateString() : 'Today'}
          </span>
        </div>

        <h4 style={{ 
          fontSize: '0.98rem', 
          fontWeight: 700, 
          color: '#0f172a', 
          lineHeight: 1.35, 
          margin: '0 0 6px' 
        }}>
          {advisory.title}
        </h4>

        <p style={{ 
          fontSize: '0.82rem', 
          color: '#475569', 
          lineHeight: 1.45, 
          margin: '0 0 10px',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden'
        }}>
          {advisory.summary}
        </p>

        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between', 
          paddingTop: '6px', 
          borderTop: '1px solid #f1f5f9',
          fontSize: '0.74rem'
        }}>
          <span style={{ color: '#059669', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}>
            <MapPin size={12} />
            {advisory.source || 'ICAR / Agromet'}
          </span>

          <span style={{ color: '#0284c7', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '3px' }}>
            Read Advisory <ArrowRight size={13} />
          </span>
        </div>
      </div>
    </div>
  )
}

export default AdvisoryCard
