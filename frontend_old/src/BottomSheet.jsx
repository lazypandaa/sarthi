import React, { useEffect } from 'react'
import { X } from 'lucide-react'

function BottomSheet({ isOpen, onClose, title, children }) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="bottom-sheet-backdrop" onClick={onClose} role="dialog" aria-modal="true">
      <div 
        className="bottom-sheet-content" 
        onClick={(e) => e.stopPropagation()}
      >
        <div className="bottom-sheet-handle" />
        
        {title && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '14px',
            paddingBottom: '8px',
            borderBottom: '1px solid #f1f5f9'
          }}>
            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700, color: '#0f172a' }}>
              {title}
            </h3>
            <button 
              onClick={onClose}
              style={{
                background: '#f1f5f9',
                border: 'none',
                borderRadius: '50%',
                width: '32px',
                height: '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                color: '#64748b'
              }}
              aria-label="Close"
            >
              <X size={18} />
            </button>
          </div>
        )}

        <div>
          {children}
        </div>
      </div>
    </div>
  )
}

export default BottomSheet
