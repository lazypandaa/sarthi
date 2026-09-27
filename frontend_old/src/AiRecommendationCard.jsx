import React from 'react'
import { Sparkles, Brain, CheckCircle, ArrowRight, Mic } from 'lucide-react'

function AiRecommendationCard({ 
  user, 
  onAskFollowup, 
  onViewMemory,
  recommendation = null 
}) {
  const defaultRec = {
    title: "Groundnut (GG-20) for Upcoming Rabi Cycle",
    insight: "Recommended over water-thirsty crops given your borewell depth & sandy clay soil.",
    reasons: [
      "Requires 40% less water than paddy / sugarcane",
      `Matches ground-truth soil (${user?.soil_type || 'Sandy Clay Loam'})`,
      "Protects farm against previous fungal root-rot risk"
    ]
  }

  const rec = recommendation || defaultRec

  return (
    <div className="ai-recommendation-card">
      {/* Badge Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Sparkles size={16} color="#34d399" />
          <span style={{ 
            fontSize: '0.72rem', 
            fontWeight: 800, 
            letterSpacing: '0.06em', 
            textTransform: 'uppercase', 
            color: '#a7f3d0' 
          }}>
            SARTHI AI • FARM INSIGHT
          </span>
        </div>

        <span style={{
          fontSize: '0.66rem',
          background: 'rgba(16, 185, 129, 0.25)',
          border: '1px solid rgba(16, 185, 129, 0.4)',
          color: '#6ee7b7',
          padding: '2px 8px',
          borderRadius: '12px',
          fontWeight: 600,
          display: 'flex',
          alignItems: 'center',
          gap: '4px'
        }}>
          <Brain size={11} /> Memory Influenced
        </span>
      </div>

      {/* Main Title & Insight */}
      <h3 style={{ fontSize: '1.08rem', fontWeight: 800, color: '#ffffff', margin: '0 0 6px', lineHeight: 1.35 }}>
        {rec.title}
      </h3>
      <p style={{ fontSize: '0.82rem', color: '#d1fae5', margin: '0 0 12px', lineHeight: 1.45 }}>
        {rec.insight}
      </p>

      {/* Why Checklist (Hindsight Influence) */}
      <div style={{
        background: 'rgba(0, 0, 0, 0.2)',
        borderRadius: '10px',
        padding: '10px 12px',
        marginBottom: '14px',
        border: '1px solid rgba(255, 255, 255, 0.08)'
      }}>
        <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#6ee7b7', textTransform: 'uppercase', marginBottom: '6px' }}>
          Why Sarthi recommends this:
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
          {rec.reasons.map((reason, idx) => (
            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: '#f0fdf4' }}>
              <CheckCircle size={13} color="#34d399" style={{ flexShrink: 0 }} />
              <span>{reason}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <button
          type="button"
          onClick={onAskFollowup}
          className="interactive-tap"
          style={{
            flex: 1,
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            color: '#ffffff',
            border: 'none',
            borderRadius: '8px',
            padding: '8px 12px',
            fontSize: '0.8rem',
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            boxShadow: '0 2px 6px rgba(0,0,0,0.2)'
          }}
        >
          <Mic size={14} /> Ask Sarthi
        </button>

        <button
          type="button"
          onClick={onViewMemory}
          className="interactive-tap"
          style={{
            background: 'rgba(255, 255, 255, 0.12)',
            color: '#d1fae5',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '8px',
            padding: '8px 12px',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}
        >
          <span>Memory Hub</span>
          <ArrowRight size={13} />
        </button>
      </div>
    </div>
  )
}

export default AiRecommendationCard
