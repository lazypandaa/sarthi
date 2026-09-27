import React, { useState } from 'react'
import { ThumbsUp, ThumbsDown, Edit3, Sprout, CheckCircle2, X, Send } from 'lucide-react'
import axios from 'axios'
import { API_URL } from './config'
import './Memory.css'

export default function EnhancedFeedbackModal({
  isOpen,
  onClose,
  queryId,
  initialMode = 'simple',
  onSuccess
}) {
  const [feedbackMode, setFeedbackMode] = useState(initialMode) // 'simple' | 'correction' | 'outcome'
  const [helpful, setHelpful] = useState(null)
  const [feedbackText, setFeedbackText] = useState('')
  const [correctionText, setCorrectionText] = useState('')
  const [crop, setCrop] = useState('')
  const [outcomeResult, setOutcomeResult] = useState('success') // 'success' | 'failure' | 'partial'
  const [outcomeReason, setOutcomeReason] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submittedSuccess, setSubmittedSuccess] = useState(false)

  if (!isOpen) return null

  const handleSubmit = async (overrideHelpful = null) => {
    setIsSubmitting(true)
    try {
      const token = localStorage.getItem('token')
      const chosenHelpful = overrideHelpful !== null ? overrideHelpful : (helpful !== null ? helpful : true)

      const payload = {
        query_id: queryId || 'general_query',
        helpful: chosenHelpful,
        feedback_type: feedbackMode === 'correction' ? 'corrected' : feedbackMode === 'outcome' ? 'outcome_reported' : 'general',
        feedback_text: feedbackText || '',
        crop: crop.trim() || undefined,
        outcome_result: feedbackMode === 'outcome' ? outcomeResult : undefined,
        outcome_reason: feedbackMode === 'outcome' ? outcomeReason.trim() : undefined,
        correction_new: feedbackMode === 'correction' ? correctionText.trim() : undefined,
      }

      await axios.post(`${API_URL}/api/feedback`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      })

      setSubmittedSuccess(true)
      setTimeout(() => {
        setSubmittedSuccess(false)
        if (onSuccess) onSuccess()
        onClose()
      }, 1500)
    } catch (err) {
      console.error('Error submitting feedback:', err)
      onClose()
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="feedback-modal-enhanced">
      <div className="feedback-modal-header">
        <h4>
          <span>🌾 Farm Feedback & Learning</span>
        </h4>
        <button type="button" className="feedback-close-btn" onClick={onClose}>
          <X size={18} />
        </button>
      </div>

      <div className="feedback-modal-body">
        {submittedSuccess ? (
          <div className="feedback-toast-success">
            <CheckCircle2 size={20} color="#059669" />
            <div>
              <strong>Recorded to Farm Memory!</strong>
              <div style={{ fontSize: '0.8rem', fontWeight: 400 }}>Your feedback will guide future recommendations.</div>
            </div>
          </div>
        ) : (
          <>
            {/* Mode Selector Tabs */}
            <div className="feedback-mode-selector">
              <button
                type="button"
                className={`feedback-mode-btn ${feedbackMode === 'simple' ? 'active' : ''}`}
                onClick={() => setFeedbackMode('simple')}
              >
                Helpful?
              </button>
              <button
                type="button"
                className={`feedback-mode-btn ${feedbackMode === 'correction' ? 'active' : ''}`}
                onClick={() => setFeedbackMode('correction')}
              >
                ✏️ Correction
              </button>
              <button
                type="button"
                className={`feedback-mode-btn ${feedbackMode === 'outcome' ? 'active' : ''}`}
                onClick={() => setFeedbackMode('outcome')}
              >
                🌾 Report Outcome
              </button>
            </div>

            {/* MODE 1: SIMPLE HELPFUL / NOT HELPFUL */}
            {feedbackMode === 'simple' && (
              <>
                <p style={{ margin: '0 0 12px 0', fontSize: '0.88rem', color: '#475569' }}>
                  Was this advice practical and helpful for your field?
                </p>
                <div className="feedback-simple-actions">
                  <button
                    type="button"
                    className={`feedback-action-choice helpful ${helpful === true ? 'selected' : ''}`}
                    onClick={() => { setHelpful(true); handleSubmit(true); }}
                  >
                    <ThumbsUp size={18} />
                    <span>Helpful / Accepted</span>
                  </button>
                  <button
                    type="button"
                    className={`feedback-action-choice not-helpful ${helpful === false ? 'selected' : ''}`}
                    onClick={() => setHelpful(false)}
                  >
                    <ThumbsDown size={18} />
                    <span>Not Helpful</span>
                  </button>
                </div>
                {helpful === false && (
                  <textarea
                    className="feedback-input-field"
                    rows={2}
                    placeholder="Tell us why (e.g. 'I don't have enough water for this crop')"
                    value={feedbackText}
                    onChange={(e) => setFeedbackText(e.target.value)}
                  />
                )}
              </>
            )}

            {/* MODE 2: FARMER CORRECTION */}
            {feedbackMode === 'correction' && (
              <>
                <p style={{ margin: '0 0 10px 0', fontSize: '0.85rem', color: '#475569' }}>
                  Correct an outdated fact or advice. Sarthi will prioritize your correction over past assumptions.
                </p>
                <textarea
                  className="feedback-input-field"
                  rows={3}
                  placeholder="e.g. 'My farm has less water than this', 'I don't grow tomato anymore', or 'I installed a drip system'"
                  value={correctionText}
                  onChange={(e) => setCorrectionText(e.target.value)}
                  autoFocus
                />
              </>
            )}

            {/* MODE 3: REPORT OUTCOME */}
            {feedbackMode === 'outcome' && (
              <>
                <p style={{ margin: '0 0 10px 0', fontSize: '0.85rem', color: '#475569' }}>
                  What was the actual result of this crop or recommendation?
                </p>
                <div className="feedback-outcome-grid">
                  <button
                    type="button"
                    className={`feedback-outcome-btn ${outcomeResult === 'success' ? 'active-success' : ''}`}
                    onClick={() => setOutcomeResult('success')}
                  >
                    ✅ Successful Yield
                  </button>
                  <button
                    type="button"
                    className={`feedback-outcome-btn ${outcomeResult === 'failure' ? 'active-failure' : ''}`}
                    onClick={() => setOutcomeResult('failure')}
                  >
                    ❌ Crop Failed / Poor
                  </button>
                  <button
                    type="button"
                    className={`feedback-outcome-btn ${outcomeResult === 'partial' ? 'active-partial' : ''}`}
                    onClick={() => setOutcomeResult('partial')}
                  >
                    ⚖️ Partial
                  </button>
                </div>
                <input
                  type="text"
                  className="feedback-input-field"
                  placeholder="Crop Name (e.g. Tomato, Groundnut, Cotton)"
                  value={crop}
                  onChange={(e) => setCrop(e.target.value)}
                />
                <input
                  type="text"
                  className="feedback-input-field"
                  placeholder="Reason / Details (e.g. Borewell water shortage, pest attack)"
                  value={outcomeReason}
                  onChange={(e) => setOutcomeReason(e.target.value)}
                />
              </>
            )}
          </>
        )}
      </div>

      {!submittedSuccess && (
        <div className="feedback-modal-footer">
          <button type="button" className="feedback-cancel-btn" onClick={onClose}>
            Cancel
          </button>
          <button
            type="button"
            className="feedback-submit-btn"
            onClick={() => handleSubmit()}
            disabled={isSubmitting || (feedbackMode === 'correction' && !correctionText.trim())}
          >
            {isSubmitting ? 'Saving...' : 'Submit Feedback'}
          </button>
        </div>
      )}
    </div>
  )
}
