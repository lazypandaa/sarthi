import React, { useState } from 'react'
import { Brain, ChevronDown, ChevronUp, ShieldCheck, Edit3, Sparkles } from 'lucide-react'
import './Memory.css'

export default function MemoryInfluenceCard({
  memoryContext,
  relevantMemories = [],
  memoryInfluence = [],
  onOpenCorrection
}) {
  const isUsed = Boolean(memoryContext?.used || (relevantMemories && relevantMemories.length > 0) || (memoryInfluence && memoryInfluence.length > 0))
  const [expanded, setExpanded] = useState(isUsed)

  const memoryCount = memoryContext?.memory_count || relevantMemories?.length || memoryInfluence?.length || 0

  if (!isUsed && (!relevantMemories || relevantMemories.length === 0)) {
    return (
      <div className="memory-influence-card" style={{ background: '#f8fafc', borderColor: '#e2e8f0' }}>
        <div className="memory-influence-header" onClick={() => setExpanded(!expanded)}>
          <div className="memory-influence-badge" style={{ color: '#64748b' }}>
            <Sparkles size={16} color="#059669" />
            <span>Standard Regional Advisory (No specific past constraints applied)</span>
          </div>
          <button className="memory-influence-toggle-btn" type="button">
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        </div>
        {expanded && (
          <div className="memory-influence-details">
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#64748b' }}>
              This advice was computed from regional weather, soil, and crop data. As you share feedback, report crop outcomes, or teach the system constraints (e.g. water limits), future advice will automatically adapt.
            </p>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="memory-influence-card">
      <div className="memory-influence-header" onClick={() => setExpanded(!expanded)}>
        <div className="memory-influence-badge">
          <Brain size={18} color="#10b981" />
          <span>Personalized using your past experience</span>
          <span style={{
            fontSize: '0.78rem',
            background: '#d1fae5',
            color: '#065f46',
            padding: '2px 8px',
            borderRadius: '12px',
            fontWeight: 700
          }}>
            {memoryCount} {memoryCount === 1 ? 'memory' : 'memories'} recalled
          </span>
        </div>
        <button className="memory-influence-toggle-btn" type="button">
          {expanded ? 'Hide Details' : 'Why this recommendation?'}
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {expanded && (
        <div className="memory-influence-details">
          {/* Section: Based on what I remember */}
          <div className="memory-subheading">
            <span>🌾 Based on what I remember:</span>
          </div>
          <ul className="memory-recalled-bullets">
            {relevantMemories && relevantMemories.length > 0 ? (
              relevantMemories.map((mem, idx) => (
                <li key={mem.id || idx}>
                  <span className="memory-bullet-dot">•</span>
                  <span>
                    <strong>[{mem.type?.toUpperCase() || 'NOTE'}]:</strong> {mem.summary}
                  </span>
                </li>
              ))
            ) : memoryInfluence && memoryInfluence.length > 0 ? (
              memoryInfluence.map((inf, idx) => (
                <li key={idx}>
                  <span className="memory-bullet-dot">•</span>
                  <span>
                    <strong>[{inf.type?.toUpperCase()}]:</strong> {inf.summary}
                  </span>
                </li>
              ))
            ) : null}
          </ul>

          {/* Section: Why this recommendation */}
          {memoryInfluence && memoryInfluence.length > 0 && (
            <>
              <div className="memory-subheading" style={{ marginTop: '12px' }}>
                <span>🎯 Why this recommendation:</span>
              </div>
              <div className="memory-reasoning-box">
                {memoryInfluence.map((inf, idx) => (
                  <p key={idx} style={{ marginBottom: idx < memoryInfluence.length - 1 ? '6px' : '0' }}>
                    <strong>{inf.type === 'constraint' ? '⚠️ Farm Constraint' : inf.type === 'crop_history' ? '🌾 Past Experience' : '💡 Memory Factor'}:</strong>{' '}
                    {inf.impact}
                  </p>
                ))}
              </div>
            </>
          )}

          {/* Privacy & Correction Action */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px', marginTop: '10px' }}>
            <div className="memory-privacy-footnote">
              <ShieldCheck size={14} color="#10b981" />
              <span>Memories are strictly isolated and private to your phone number.</span>
            </div>
            {onOpenCorrection && (
              <button
                type="button"
                onClick={onOpenCorrection}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#059669',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: 0
                }}
              >
                <Edit3 size={13} />
                <span>Correct or update this memory</span>
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
