import React, { useState, useRef, useEffect } from 'react'
import { Mic, MicOff, Play, Pause, Loader, LogOut, User, Award, Users, Calendar, Brain, Sparkles, TrendingUp, CheckCircle, ArrowRight, ShieldCheck } from 'lucide-react'
import axios from 'axios'
import Auth from './Auth'
import ProfileNew from './ProfileNew'
import Landing from './Landing'
import Advisor from './Advisor'
import Community from './Community'
import CropCalendar from './CropCalendar'
import MemoryDashboard from './MemoryDashboard'
import MemoryInfluenceCard from './MemoryInfluenceCard'
import EnhancedFeedbackModal from './EnhancedFeedbackModal'
import Navbar from './Navbar'
import JudgeSandbox from './JudgeSandbox'
import WeatherCard from './WeatherCard'
import AdvisoryCard from './AdvisoryCard'
import AiRecommendationCard from './AiRecommendationCard'
import { API_URL } from './config'
import { getTranslation } from './translations'

function App() {
  const [showLanding, setShowLanding] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingStatusText, setProcessingStatusText] = useState('')
  const [response, setResponse] = useState('')
  const [error, setError] = useState('')
  const [audioUrl, setAudioUrl] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [textInput, setTextInput] = useState('')
  const [inputMode, setInputMode] = useState('voice')
  const [language, setLanguage] = useState('en')
  const [uiLanguage, setUiLanguage] = useState('en')
  const [showModal, setShowModal] = useState(false)
  const [modalType, setModalType] = useState('')
  const [modalInput, setModalInput] = useState('')
  const [modalLocation, setModalLocation] = useState('')
  const [showProfile, setShowProfile] = useState(false)
  const [showAdvisor, setShowAdvisor] = useState(false)
  const [showCommunity, setShowCommunity] = useState(false)
  const [showCalendar, setShowCalendar] = useState(false)
  const [showMemory, setShowMemory] = useState(false)
  const [showJudge, setShowJudge] = useState(false)
  const [showFeedbackModal, setShowFeedbackModal] = useState(false)
  const [feedbackModalMode, setFeedbackModalMode] = useState('simple')
  const [currentQueryId, setCurrentQueryId] = useState(null)
  const [feedbackText, setFeedbackText] = useState('')
  const [authDemoCreds, setAuthDemoCreds] = useState(null)
  const [homeWeather, setHomeWeather] = useState(null)
  const [homeWeatherLoading, setHomeWeatherLoading] = useState(false)
  const [homeNews, setHomeNews] = useState([])
  const [homeNewsLoading, setHomeNewsLoading] = useState(false)
  const [lastWeatherUpdated, setLastWeatherUpdated] = useState('Updated just now')

  const mediaRecorderRef = useRef(null)
  const audioRef = useRef(null)
  const chunksRef = useRef([])
  const recorderMimeTypeRef = useRef('')

  const encodeWav = (audioBuffer) => {
    const numChannels = 1
    const sampleRate = audioBuffer.sampleRate
    const format = 1
    const bitDepth = 16

    const samples = audioBuffer.getChannelData(0)
    const blockAlign = numChannels * (bitDepth / 8)
    const byteRate = sampleRate * blockAlign
    const dataSize = samples.length * (bitDepth / 8)

    const buffer = new ArrayBuffer(44 + dataSize)
    const view = new DataView(buffer)

    const writeString = (offset, str) => {
      for (let i = 0; i < str.length; i += 1) {
        view.setUint8(offset + i, str.charCodeAt(i))
      }
    }

    writeString(0, 'RIFF')
    view.setUint32(4, 36 + dataSize, true)
    writeString(8, 'WAVE')
    writeString(12, 'fmt ')
    view.setUint32(16, 16, true)
    view.setUint16(20, format, true)
    view.setUint16(22, numChannels, true)
    view.setUint32(24, sampleRate, true)
    view.setUint32(28, byteRate, true)
    view.setUint16(32, blockAlign, true)
    view.setUint16(34, bitDepth, true)
    writeString(36, 'data')
    view.setUint32(40, dataSize, true)

    let offset = 44
    for (let i = 0; i < samples.length; i += 1, offset += 2) {
      let s = Math.max(-1, Math.min(1, samples[i]))
      s = s < 0 ? s * 0x8000 : s * 0x7fff
      view.setInt16(offset, s, true)
    }

    return buffer
  }

  const convertToWav = async (audioBlob) => {
    const arrayBuffer = await audioBlob.arrayBuffer()
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const decodedBuffer = await audioContext.decodeAudioData(arrayBuffer)

    const targetSampleRate = 16000
    const offlineContext = new OfflineAudioContext(1, Math.ceil(decodedBuffer.duration * targetSampleRate), targetSampleRate)
    const source = offlineContext.createBufferSource()
    source.buffer = decodedBuffer
    source.connect(offlineContext.destination)
    source.start(0)
    const renderedBuffer = await offlineContext.startRendering()

    const wavBuffer = encodeWav(renderedBuffer)
    return new Blob([wavBuffer], { type: 'audio/wav' })
  }

  useEffect(() => {
    checkAuthStatus()
  }, [])

  useEffect(() => {
    // Auto-play audio when audioUrl changes
    if (audioUrl && audioRef.current) {
      const audio = audioRef.current
      audio.muted = false
      audio.volume = 1.0
      
      const attemptPlay = () => {
        audio.load()
        const playPromise = audio.play()
        
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              console.log('Audio playing successfully')
              setIsPlaying(true)
            })
            .catch(error => {
              console.log('Autoplay prevented, will retry:', error)
              // Try again after a short delay
              setTimeout(() => {
                audio.play()
                  .then(() => setIsPlaying(true))
                  .catch(e => console.log('Retry also failed:', e))
              }, 300)
            })
        }
      }
      
      // Wait for audio to be ready
      if (audio.readyState >= 2) {
        attemptPlay()
      } else {
        audio.addEventListener('canplay', attemptPlay, { once: true })
      }
      
      return () => {
        audio.removeEventListener('canplay', attemptPlay)
      }
    }
  }, [audioUrl])

  useEffect(() => {
    // Regenerate response when language changes
    if (response && response.transcript && uiLanguage !== language) {
      setLanguage(uiLanguage)
      // Regenerate the last response in new language
      const regenerateResponse = async () => {
        setIsProcessing(true)
        try {
          const token = localStorage.getItem('token')
          const res = await axios.post(`${API_URL}/process-text`, {
            text: response.transcript,
            language: uiLanguage
          }, {
            headers: { 
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
          })
          setResponse({
            transcript: response.transcript,
            response_text: res.data.response_text || res.data,
            query_id: res.data.query_id,
            memory_context: res.data.memory_context,
            relevant_memories: res.data.relevant_memories,
            memory_influence: res.data.memory_influence
          })
          if (res.data.audio_data) {
            const audioBlob = new Blob([Uint8Array.from(atob(res.data.audio_data), c => c.charCodeAt(0))], { type: 'audio/wav' })
            const audioUrl = URL.createObjectURL(audioBlob)
            setAudioUrl(audioUrl)
          }
        } catch (err) {
          console.error('Error regenerating response:', err)
        } finally {
          setIsProcessing(false)
        }
      }
      regenerateResponse()
    } else {
      setLanguage(uiLanguage)
    }
  }, [uiLanguage])

  const fetchHomeWeather = async () => {
    setHomeWeatherLoading(true)
    try {
      const token = localStorage.getItem('token')
      const wRes = await axios.get(`${API_URL}/api/weather-advisory`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      const wData = wRes.data || {}
      const rainVal = parseFloat(wData.rainfall) || 0
      setHomeWeather({
        location: wData.location || user?.location?.split(',')[0] || 'Guntur',
        temperature: wData.temperature !== undefined ? wData.temperature : 28,
        humidity: wData.humidity !== undefined ? wData.humidity : 65,
        rainfall: wData.rainfall || '0 mm',
        description: wData.condition || wData.description || 'Clear skies',
        hasRain: rainVal > 0,
        warnings: wData.warnings || [],
        soilContext: wData.soil_context || null
      })
      setLastWeatherUpdated('Updated just now')
    } catch (err) {
      console.warn('Weather advisory fetch error:', err)
      setHomeWeather({
        location: user?.location?.split(',')[0] || 'Guntur',
        temperature: 28,
        humidity: 68,
        rainfall: '0 mm',
        description: 'Partly cloudy',
        hasRain: false,
        warnings: ['High humidity window — optimal for organic foliar spray']
      })
    } finally {
      setHomeWeatherLoading(false)
    }
  }

  const fetchHomeNews = async () => {
    setHomeNewsLoading(true)
    try {
      const token = localStorage.getItem('token')
      const nRes = await axios.get(`${API_URL}/api/agriculture-news`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setHomeNews(nRes.data || [])
    } catch (err) {
      console.warn('Home news error:', err)
    } finally {
      setHomeNewsLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated && user) {
      fetchHomeWeather()
      fetchHomeNews()
    }
  }, [isAuthenticated, user?.location])

  const t = (key) => getTranslation(uiLanguage, key)

  const checkAuthStatus = async () => {
    const token = localStorage.getItem('token')
    if (token) {
      try {
        const response = await axios.get(`${API_URL}/api/me`, {
          headers: { Authorization: `Bearer ${token}` }
        })
        setUser(response.data)
        setLanguage(response.data.language)
        setUiLanguage(response.data.language)
        setIsAuthenticated(true)
      } catch (error) {
        localStorage.removeItem('token')
        setIsAuthenticated(false)
      }
    }
  }

  const handleLogin = async (token) => {
    try {
      const response = await axios.get(`${API_URL}/api/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUser(response.data)
      setLanguage(response.data.language)
      setUiLanguage(response.data.language)
      setIsAuthenticated(true)
    } catch (error) {
      localStorage.removeItem('token')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setIsAuthenticated(false)
    setUser(null)
    setResponse('')
    setError('')
    setAudioUrl(null)
  }

  const startRecording = async () => {
    try {
      setError('')
      setResponse('')
      setAudioUrl(null)
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

      const preferredTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/ogg;codecs=opus',
        'audio/ogg'
      ]
      const supportedType = preferredTypes.find((type) => MediaRecorder.isTypeSupported(type))
      const recorderOptions = supportedType ? { mimeType: supportedType } : undefined

      mediaRecorderRef.current = recorderOptions ? new MediaRecorder(stream, recorderOptions) : new MediaRecorder(stream)
      recorderMimeTypeRef.current = mediaRecorderRef.current.mimeType || supportedType || ''
      chunksRef.current = []
      mediaRecorderRef.current.ondataavailable = (event) => {
        chunksRef.current.push(event.data)
      }
      mediaRecorderRef.current.onstop = async () => {
        const chunkType = chunksRef.current[0]?.type
        const mimeType = recorderMimeTypeRef.current || chunkType || 'audio/webm'
        const audioBlob = new Blob(chunksRef.current, { type: mimeType })
        const wavBlob = await convertToWav(audioBlob)
        await processAudio(wavBlob)
        stream.getTracks().forEach(track => track.stop())
      }
      mediaRecorderRef.current.start()
      setIsRecording(true)
    } catch (err) {
      setError('Microphone access denied. Please allow microphone access and try again.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
    }
  }

  const processAudio = async (audioBlob) => {
    setIsProcessing(true)
    setError('')
    try {
      setIsProcessing(true)
      setProcessingStatusText("Finding relevant past experience...")
      const token = localStorage.getItem('token')
      const formData = new FormData()
      formData.set('file', audioBlob, 'recording.wav')

      console.log('Sending audio with language:', language)
      
      const response = await axios.post(`${API_URL}/process-audio?language=${language}`, formData, {
        headers: { 
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        },
      })
      setResponse({
        transcript: response.data.transcript,
        response_text: response.data.response_text,
        query_id: response.data.query_id,
        memory_context: response.data.memory_context,
        relevant_memories: response.data.relevant_memories,
        memory_influence: response.data.memory_influence,
        retained_learning: response.data.retained_learning
      })
      setCurrentQueryId(response.data.query_id)
      setTimeout(() => setShowFeedbackModal(true), 2000)
      if (response.data.audio_data) {
        const audioBlob = new Blob([Uint8Array.from(atob(response.data.audio_data), c => c.charCodeAt(0))], { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        setAudioUrl(audioUrl)
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to process audio'
      setError(errorMessage)
      console.error('Error processing audio:', err)
    } finally {
      setIsProcessing(false)
      setProcessingStatusText('')
    }
  }

  const processText = async (textOverride = null) => {
    const rawText = typeof textOverride === 'string' ? textOverride : textInput
    if (!rawText || !rawText.trim()) {
      setError('Please enter some text to process.')
      return
    }
    setTextInput(rawText)
    setIsProcessing(true)
    const hasConstraintOrFailure = /(?:failed|died|water|irrigation|borewell|prefer|tried|loss|pest)/i.test(rawText)
    setProcessingStatusText(hasConstraintOrFailure ? "Recalling farm history & soil telemetry..." : "Finding relevant past experience...")
    setError('')
    setResponse('')
    setAudioUrl(null)

    const timer = setTimeout(() => {
      setProcessingStatusText("Personalizing your recommendation...")
    }, 1200)

    try {
      const token = localStorage.getItem('token')
      const response = await axios.post(`${API_URL}/process-text`, {
        text: rawText.trim(),
        language
      }, {
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
      })
      setResponse({
        transcript: rawText,
        response_text: response.data.response_text || response.data,
        query_id: response.data.query_id,
        memory_context: response.data.memory_context,
        relevant_memories: response.data.relevant_memories,
        memory_influence: response.data.memory_influence,
        retained_learning: response.data.retained_learning
      })
      setCurrentQueryId(response.data.query_id)
      setTimeout(() => setShowFeedbackModal(true), 2000)
      if (response.data.audio_data) {
        const audioBlob = new Blob([Uint8Array.from(atob(response.data.audio_data), c => c.charCodeAt(0))], { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        setAudioUrl(audioUrl)
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to process text. Please try again.'
      setError(errorMessage)
      console.error('Error processing text:', err)
    } finally {
      clearTimeout(timer)
      setIsProcessing(false)
      setProcessingStatusText('')
    }
  }

  const playAudio = async () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
        setIsPlaying(false)
      } else {
        try {
          await audioRef.current.play()
          setIsPlaying(true)
        } catch (err) {
          console.error('Audio play error:', err)
          // Retry once after a short delay
          setTimeout(async () => {
            try {
              await audioRef.current.play()
              setIsPlaying(true)
            } catch (retryErr) {
              console.error('Audio retry failed:', retryErr)
            }
          }, 200)
        }
      }
    }
  }

  const handleAudioEnded = () => setIsPlaying(false)

  const handleAudioError = (e) => {
    console.error('Audio error:', e)
    setIsPlaying(false)
  }

  const submitFeedback = async (helpful) => {
    try {
      const token = localStorage.getItem('token')
      await axios.post(`${API_URL}/api/feedback`, {
        query_id: currentQueryId,
        helpful,
        feedback_text: feedbackText
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      setShowFeedbackModal(false)
      setFeedbackText('')
    } catch (err) {
      console.error('Feedback error:', err)
    }
  }

  // -------------------- Modal Handlers --------------------
  const openModal = (type) => {
    setModalType(type)
    // Pre-fill user's city for weather
    if (type === 'weather' && user?.location) {
      const city = user.location.split(',')[0].trim()
      setModalInput(city)
    } else {
      setModalInput('')
    }
    // Pre-fill user's location for crop prices
    if (type === 'crop' && user?.location) {
      setModalLocation(user.location)
    } else {
      setModalLocation('')
    }
    setShowModal(true)
  }

  // Quick access functions that use user's location automatically
  const getMyWeather = async () => {
    setIsProcessing(true)
    setError('')
    setResponse('')
    setAudioUrl(null)
    
    try {
      const token = localStorage.getItem('token')
      const res = await axios.post(`${API_URL}/api/weather`, { 
        city: 'current',
        language 
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      setResponse({ 
        transcript: `Weather for my location (${user?.location})`, 
        response_text: res.data.text 
      })
      
      if (res.data.audio_data) {
        const audioBlob = new Blob([Uint8Array.from(atob(res.data.audio_data), c => c.charCodeAt(0))], { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        setAudioUrl(audioUrl)
      }
    } catch (err) {
      setError('Unable to fetch weather information for your location.')
    } finally {
      setIsProcessing(false)
    }
  }

  const getCropPricesForMyArea = (cropName) => {
    return async () => {
      setIsProcessing(true)
      setError('')
      setResponse('')
      setAudioUrl(null)
      
      try {
        const token = localStorage.getItem('token')
        const res = await axios.post(`${API_URL}/api/crop-prices`, { 
          crop: cropName,
          language 
        }, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        
        setResponse({ 
          transcript: `${cropName} prices in my area (${user?.location})`, 
          response_text: res.data.text 
        })
        
        if (res.data.audio_data) {
          const audioBlob = new Blob([Uint8Array.from(atob(res.data.audio_data), c => c.charCodeAt(0))], { type: 'audio/wav' })
          const audioUrl = URL.createObjectURL(audioBlob)
          setAudioUrl(audioUrl)
        }
      } catch (err) {
        setError(`Unable to fetch ${cropName} prices for your area.`)
      } finally {
        setIsProcessing(false)
      }
    }
  }

  const closeModal = () => {
    setShowModal(false)
    setModalInput('')
    setModalLocation('')
  }

  const handleModalSubmit = async () => {
    if (!modalInput.trim()) return
    setShowModal(false)
    setIsProcessing(true)
    
    try {
      const token = localStorage.getItem('token')
      let res
      if (modalType === 'weather') {
        res = await axios.post(`${API_URL}/api/weather`, { city: modalInput, language }, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      } else if (modalType === 'crop') {
        res = await axios.post(`${API_URL}/api/crop-prices`, { 
          crop: modalInput, 
          market: modalLocation || undefined,
          language 
        }, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      } else if (modalType === 'schemes') {
        res = await axios.post(`${API_URL}/api/gov-schemes`, { topic: modalInput, language }, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      }
      setResponse({ transcript: modalInput, response_text: res.data.text })
      if (res.data.audio_data) {
        const audioBlob = new Blob([Uint8Array.from(atob(res.data.audio_data), c => c.charCodeAt(0))], { type: 'audio/wav' })
        const audioUrl = URL.createObjectURL(audioBlob)
        setAudioUrl(audioUrl)
      }
    } catch {
      setError(`Unable to fetch ${modalType} information.`)
    } finally {
      setIsProcessing(false)
      setModalInput('')
      setModalLocation('')
    }
  }

  if (showLanding && !isAuthenticated) {
    return (
      <Landing 
        onGetStarted={(creds) => {
          if (creds) setAuthDemoCreds(creds)
          setShowLanding(false)
        }} 
        onLogin={handleLogin} 
        isAuthenticated={isAuthenticated} 
      />
    )
  }

  if (!isAuthenticated) {
    return <Auth onLogin={handleLogin} demoCredentials={authDemoCreds} />
  }

  if (!user) {
    return <div className="container"><div className="main-card">Loading...</div></div>
  }

  const handleNavigate = (page) => {
    setShowProfile(page === 'profile')
    setShowAdvisor(page === 'advisor')
    setShowCommunity(page === 'community')
    setShowCalendar(page === 'calendar')
    setShowMemory(page === 'memory')
    setShowJudge(page === 'judge')
  }

  if (showJudge) {
    return (
      <JudgeSandbox
        user={user}
        onNavigate={handleNavigate}
        onLogout={handleLogout}
        language={uiLanguage}
      />
    )
  }

  if (showMemory) {
    return (
      <MemoryDashboard
        user={user}
        onNavigate={handleNavigate}
        onLogout={handleLogout}
        language={uiLanguage}
      />
    )
  }

  if (showProfile) {
    return (
      <ProfileNew 
        user={user} 
        onBack={() => setShowProfile(false)}
        onUserUpdate={(updatedUser) => {
          setUser({...user, ...updatedUser})
          setUiLanguage(updatedUser.language)
        }}
        onLogout={handleLogout}
        onNavigate={handleNavigate}
      />
    )
  }

  if (showAdvisor) {
    return (
      <Advisor 
        user={user}
        onNavigate={handleNavigate}
        onLogout={handleLogout}
        onOpenVoiceAssistant={() => setShowAdvisor(false)}
      />
    )
  }

  if (showCommunity) {
    return (
      <Community 
        user={user}
        onBack={() => setShowCommunity(false)}
        onLogout={handleLogout}
        onNavigate={handleNavigate}
      />
    )
  }

  if (showCalendar) {
    return (
      <div className="container">
        <Navbar user={user} activePage="calendar" onNavigate={handleNavigate} onLogout={handleLogout} language={uiLanguage} />
        <CropCalendar language={uiLanguage} key={uiLanguage} />
      </div>
    )
  }

  return (
    <div className="container" key={user?.language}>
      <Navbar user={user} activePage="home" onNavigate={handleNavigate} onLogout={handleLogout} language={uiLanguage} />

      {/* Personalized Mobile-First Farm Feed */}
      <div style={{ maxWidth: '100%', margin: '0 auto', paddingBottom: '20px' }}>
        
        {/* 1. Personalized Greeting & Context Header */}
        <div style={{ marginBottom: '14px', padding: '0 4px' }}>
          <div style={{ 
            fontSize: 'clamp(1.25rem, 4.5vw, 1.65rem)', 
            fontWeight: 800, 
            color: '#0f172a', 
            letterSpacing: '-0.02em', 
            display: 'flex', 
            alignItems: 'center', 
            gap: '6px' 
          }}>
            <span>Good morning, {user?.name || user?.location?.split(',')[0] || 'Farmer'} 🌾</span>
          </div>
          <div style={{ fontSize: '0.84rem', color: '#64748b', fontWeight: 500, marginTop: '2px' }}>
            Here's what matters for your farm today in {user?.location || 'your district'}.
          </div>
        </div>

        {/* 2. Real-time Agricultural Telemetry HUD Strip */}
        <div style={{
          background: 'linear-gradient(90deg, #0f172a 0%, #1e293b 100%)',
          borderRadius: '12px',
          padding: '8px 12px',
          marginBottom: '10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '6px',
          color: '#e2e8f0',
          fontSize: '0.74rem',
          border: '1px solid #334155',
          boxShadow: '0 2px 6px rgba(0,0,0,0.06)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '7px', height: '7px', borderRadius: '50%', background: '#10b981', display: 'inline-block', boxShadow: '0 0 6px #10b981' }} />
            <span style={{ fontWeight: 600, color: '#38bdf8' }}>Hindsight Cloud:</span>
            <span style={{ color: '#4ade80', fontWeight: 600 }}>CONNECTED (Active Bank)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <span>🏛️ <strong>702 Districts</strong> Soil Ground Truth</span>
            <span>⚡ DB: <strong style={{ color: '#38bdf8' }}>&lt;8ms</strong></span>
            <span>📍 <strong>{user?.location?.split(',')[0] || 'Guntur'}</strong> ({user?.soil_type || 'Sandy Clay Loam'})</span>
          </div>
        </div>

        {/* 3. Live APMC Mandi Ticker Ribbon */}
        <div style={{
          background: '#ffffff',
          border: '1px solid #e2e8f0',
          borderRadius: '10px',
          padding: '6px 10px',
          marginBottom: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '0.76rem',
          overflowX: 'auto',
          whiteSpace: 'nowrap',
          boxShadow: '0 1px 3px rgba(0,0,0,0.03)'
        }}>
          <span style={{ 
            background: '#059669', 
            color: 'white', 
            padding: '2px 6px', 
            borderRadius: '4px', 
            fontWeight: 700,
            fontSize: '0.68rem',
            letterSpacing: '0.04em'
          }}>
            LIVE APMC
          </span>
          <span style={{ color: '#334155' }}>
            🌶️ <strong>Chilli (Guntur):</strong> ₹20,800/Qtl <span style={{ color: '#059669', fontWeight: 600 }}>(+₹450)</span>
          </span>
          <span style={{ color: '#cbd5e1' }}>•</span>
          <span style={{ color: '#334155' }}>
            🌾 <strong>Paddy (IR-64):</strong> ₹2,350/Qtl <span style={{ color: '#059669', fontWeight: 600 }}>(Steady)</span>
          </span>
          <span style={{ color: '#cbd5e1' }}>•</span>
          <span style={{ color: '#334155' }}>
            🧅 <strong>Onion:</strong> ₹1,850/Qtl
          </span>
          <span style={{ color: '#cbd5e1' }}>•</span>
          <span style={{ color: '#0369a1' }}>
            🌤️ <strong>IMD Agromet:</strong> 48hr dry window — optimal for foliar spray
          </span>
        </div>

        {/* 4. Horizontal Quick Action Chips (Judge Hub & Test Chips) */}
        <div className="horizontal-chip-scroll" style={{ marginBottom: '12px' }}>
          <button
            type="button"
            className="chip-pill interactive-tap active"
            onClick={() => handleNavigate('judge')}
            style={{
              background: 'linear-gradient(135deg, #065f46 0%, #059669 100%)',
              border: 'none',
              color: '#ffffff'
            }}
          >
            <Sparkles size={14} color="#fde047" />
            <span>Judge Sandbox ⚡ (60-Sec Proof)</span>
          </button>

          <button
            type="button"
            className="chip-pill interactive-tap"
            onClick={() => {
              setInputMode('text')
              processText("What should I plant this season for maximum profit?")
            }}
            disabled={isProcessing}
          >
            <span>🌱</span>
            <span>Test Memory Recall</span>
          </button>

          <button
            type="button"
            className="chip-pill interactive-tap"
            onClick={() => {
              setInputMode('text')
              processText("My borewell dried up completely yesterday, I only have 1 hour of drip water now.")
            }}
            disabled={isProcessing}
          >
            <span>💧</span>
            <span>Test New Learning</span>
          </button>

          <button
            type="button"
            className="chip-pill interactive-tap"
            onClick={() => {
              setInputMode('text')
              processText("Check Chilli market prices in Guntur APMC and advisory")
            }}
            disabled={isProcessing}
          >
            <span>💰</span>
            <span>Check APMC Rates</span>
          </button>
        </div>

        {/* 5. Compact Mobile Weather Card */}
        <WeatherCard 
          weather={homeWeather} 
          loading={homeWeatherLoading} 
          onRefresh={fetchHomeWeather}
          lastUpdatedText={lastWeatherUpdated}
        />

        {/* 6. Sarthi AI Farm Insight (Hindsight Recommendation) */}
        <AiRecommendationCard 
          user={user} 
          onAskFollowup={() => setInputMode('voice')} 
          onViewMemory={() => handleNavigate('memory')}
        />

        {/* 7. Voice & AI Assistant Primary Card */}
        <div className="card-shell" style={{ marginBottom: '14px', padding: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ fontSize: '1.2rem' }}>🤖</span>
              <span style={{ fontSize: '0.94rem', fontWeight: 700, color: '#0f172a' }}>
                Ask Sarthi AI in {uiLanguage.toUpperCase()}
              </span>
            </div>

            <div className="input-mode-selector" style={{ margin: 0, maxWidth: '140px', padding: '2px', background: '#f1f5f9' }}>
              <button 
                className={`mode-button ${inputMode === 'voice' ? 'active' : ''}`} 
                onClick={() => setInputMode('voice')}
                style={{ padding: '4px 10px', fontSize: '0.74rem', minHeight: '30px' }}
              >
                🎤 Voice
              </button>
              <button 
                className={`mode-button ${inputMode === 'text' ? 'active' : ''}`} 
                onClick={() => setInputMode('text')}
                style={{ padding: '4px 10px', fontSize: '0.74rem', minHeight: '30px' }}
              >
                ✍ Text
              </button>
            </div>
          </div>

          {inputMode === 'voice' ? (
            <div className="voice-section" style={{ textAlign: 'center', padding: '10px 0' }}>
              <button 
                className={`voice-button interactive-tap ${isRecording ? 'recording' : ''}`} 
                onClick={isRecording ? stopRecording : startRecording} 
                disabled={isProcessing}
                style={{
                  width: '5.2rem',
                  height: '5.2rem',
                  background: isRecording ? '#dc2626' : 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
                  boxShadow: isRecording ? '0 0 20px rgba(220, 38, 38, 0.5)' : '0 4px 16px rgba(5, 150, 105, 0.35)',
                  margin: '0 auto 10px'
                }}
                aria-label={isRecording ? 'Stop Recording' : 'Start Recording'}
              >
                {isProcessing ? <Loader className="loading" size={32} /> : isRecording ? <MicOff size={32} /> : <Mic size={32} />}
              </button>

              <div className="status-text" style={{ fontSize: '0.84rem', fontWeight: 600, color: '#334155', minHeight: '22px' }}>
                {isRecording ? `🎤 ${t('listening')} (Speak now...)` :
                  isProcessing ? `🤖 ${processingStatusText || t('processing')}` :
                    `👆 Tap mic to ask Sarthi in your language`}
              </div>
            </div>
          ) : (
            <div className="text-section" style={{ marginTop: '6px' }}>
              <textarea 
                value={textInput} 
                onChange={(e) => setTextInput(e.target.value)} 
                placeholder={t('typeMessage')} 
                className="text-input" 
                rows={2} 
                disabled={isProcessing}
                style={{ fontSize: '0.88rem', padding: '10px', minHeight: '64px' }}
              />
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '8px' }}>
                <button 
                  className="submit-button interactive-tap" 
                  onClick={processText} 
                  disabled={isProcessing || !textInput.trim()}
                  style={{ width: 'auto', padding: '8px 18px', fontSize: '0.82rem' }}
                >
                  {isProcessing ? <><Loader className="loading" size={14} /> {processingStatusText || t('processing')}</> : t('send')}
                </button>
              </div>
            </div>
          )}

          {error && (
            <div className="error-message" style={{ marginTop: '10px', fontSize: '0.82rem' }}>
              {error}
            </div>
          )}

          {/* AI Response Box */}
          {response && (
            <div className="response-section" style={{ marginTop: '14px', paddingTop: '12px', borderTop: '1px solid #f1f5f9' }}>
              {/* Subtle Learning Confirmation Banner (Section 12) */}
              {response.retained_learning && (
                <div style={{
                  padding: '8px 12px',
                  background: '#ecfdf5',
                  border: '1px solid #a7f3d0',
                  borderRadius: '8px',
                  marginBottom: '10px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '0.78rem',
                  color: '#065f46',
                  fontWeight: 600
                }}>
                  <CheckCircle size={15} color="#059669" />
                  <span>✓ Learned: Sarthi saved this farm constraint into memory for future advice.</span>
                </div>
              )}

              <h4 style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0f172a', margin: '0 0 6px' }}>
                📝 {response.transcript}
              </h4>
              <p className="response-text" style={{ fontSize: '0.84rem', lineHeight: 1.5, color: '#334155', margin: '0 0 10px' }}>
                {response.response_text}
              </p>
              
              <MemoryInfluenceCard
                memoryContext={response.memory_context}
                relevantMemories={response.relevant_memories}
                memoryInfluence={response.memory_influence}
                retainedLearning={response.retained_learning}
                onOpenCorrection={() => {
                  setFeedbackModalMode('correction')
                  setShowFeedbackModal(true)
                }}
              />

              {audioUrl && (
                <div className="audio-controls" style={{ marginTop: '8px' }}>
                  <button 
                    className="play-button interactive-tap" 
                    onClick={playAudio}
                    style={{ padding: '6px 14px', fontSize: '0.8rem' }}
                  >
                    {isPlaying ? <Pause size={16} /> : <Play size={16} />}
                    {isPlaying ? t('pause') : t('playAudio')}
                  </button>
                  <audio 
                    ref={audioRef} 
                    src={audioUrl} 
                    onEnded={handleAudioEnded} 
                    onError={handleAudioError} 
                    preload="auto"
                    playsInline
                  />
                </div>
              )}
            </div>
          )}
        </div>

        {/* 8. Today's Agricultural Advisory Card Feed */}
        {homeNews.length > 0 && (
          <div style={{ marginBottom: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px', padding: '0 4px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <TrendingUp size={16} color="#059669" />
                <span style={{ fontSize: '0.94rem', fontWeight: 800, color: '#0f172a' }}>
                  Today's Farm Advisory
                </span>
              </div>
              <button
                type="button"
                onClick={() => handleNavigate('advisor')}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#0284c7',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '2px'
                }}
              >
                <span>View all</span>
                <ArrowRight size={13} />
              </button>
            </div>

            <AdvisoryCard 
              advisory={homeNews[0]} 
              onSelect={() => handleNavigate('advisor')} 
            />
          </div>
        )}

        {/* 9. Crop Calendar Insight Card */}
        <div 
          className="card-shell interactive-tap" 
          onClick={() => handleNavigate('calendar')}
          style={{ marginBottom: '14px', padding: '14px', cursor: 'pointer' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Calendar size={16} color="#059669" />
              <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0f172a' }}>
                Crop Calendar • Rabi Season
              </span>
            </div>
            <span style={{
              fontSize: '0.7rem',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: '10px',
              background: '#ecfdf5',
              color: '#047857',
              border: '1px solid #a7f3d0'
            }}>
              WHEAT (GW-322)
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: '#475569', marginBottom: '6px' }}>
            <span>Sowing: Nov – Dec</span>
            <span>Harvest: Mar – Apr</span>
            <span style={{ fontWeight: 600, color: '#059669' }}>32 days to harvest</span>
          </div>

          <div style={{ width: '100%', height: '6px', background: '#e2e8f0', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{ width: '68%', height: '100%', background: 'linear-gradient(90deg, #10b981, #059669)', borderRadius: '3px' }} />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px', fontSize: '0.76rem' }}>
            <span style={{ color: '#64748b' }}>💧 Moderate water • 🌱 Loamy soil</span>
            <span style={{ color: '#0284c7', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '3px' }}>
              Full Calendar <ArrowRight size={12} />
            </span>
          </div>
        </div>

        {/* 10. What Sarthi Remembers (Hindsight Memory Preview) */}
        <div 
          className="card-shell interactive-tap" 
          onClick={() => handleNavigate('memory')}
          style={{ marginBottom: '14px', padding: '14px', cursor: 'pointer' }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Brain size={16} color="#059669" />
              <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0f172a' }}>
                What Sarthi Remembers About Your Farm
              </span>
            </div>
            <span style={{ color: '#0284c7', fontSize: '0.76rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '2px' }}>
              Memory Hub <ArrowRight size={12} />
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '8px 10px', fontSize: '0.74rem' }}>
              <div style={{ color: '#64748b', fontWeight: 600 }}>💧 Water Constraint</div>
              <div style={{ color: '#0f172a', fontWeight: 700, marginTop: '2px' }}>1 hr/day borewell limit</div>
            </div>

            <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '8px 10px', fontSize: '0.74rem' }}>
              <div style={{ color: '#64748b', fontWeight: 600 }}>🌱 Ground-Truth Soil</div>
              <div style={{ color: '#0f172a', fontWeight: 700, marginTop: '2px' }}>{user?.soil_type || 'Sandy Clay Loam'}</div>
            </div>
          </div>
        </div>

        {/* 11. Quick Action Services */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(3, 1fr)', 
          gap: '8px', 
          marginTop: '6px',
          marginBottom: '10px' 
        }}>
          <button 
            type="button"
            className="card-shell interactive-tap" 
            onClick={() => openModal('weather')}
            style={{ 
              padding: '12px 6px', 
              textAlign: 'center', 
              cursor: 'pointer',
              marginBottom: 0,
              border: '1px solid #e2e8f0'
            }}
          >
            <div style={{ fontSize: '1.4rem', marginBottom: '4px' }}>🌍</div>
            <div style={{ fontSize: '0.76rem', fontWeight: 700, color: '#0f172a' }}>Other City</div>
            <div style={{ fontSize: '0.66rem', color: '#64748b' }}>Check Weather</div>
          </button>

          <button 
            type="button"
            className="card-shell interactive-tap" 
            onClick={() => openModal('crop')}
            style={{ 
              padding: '12px 6px', 
              textAlign: 'center', 
              cursor: 'pointer',
              marginBottom: 0,
              border: '1px solid #e2e8f0'
            }}
          >
            <div style={{ fontSize: '1.4rem', marginBottom: '4px' }}>💰</div>
            <div style={{ fontSize: '0.76rem', fontWeight: 700, color: '#0f172a' }}>Crop Prices</div>
            <div style={{ fontSize: '0.66rem', color: '#64748b' }}>APMC Rates</div>
          </button>

          <button 
            type="button"
            className="card-shell interactive-tap" 
            onClick={() => openModal('schemes')}
            style={{ 
              padding: '12px 6px', 
              textAlign: 'center', 
              cursor: 'pointer',
              marginBottom: 0,
              border: '1px solid #e2e8f0'
            }}
          >
            <div style={{ fontSize: '1.4rem', marginBottom: '4px' }}>🏛</div>
            <div style={{ fontSize: '0.76rem', fontWeight: 700, color: '#0f172a' }}>Gov Schemes</div>
            <div style={{ fontSize: '0.66rem', color: '#64748b' }}>Subsidies</div>
          </button>
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                {modalType === 'weather' && '🌤 Weather Information'}
                {modalType === 'crop' && '💰 Crop Prices'}
                {modalType === 'schemes' && '🏛 Government Schemes'}
              </h3>
              <button className="close-button" onClick={closeModal}>×</button>
            </div>
            <div className="modal-body">
              <label>
                {modalType === 'weather' && 'Enter city name:'}
                {modalType === 'crop' && 'Enter crop name:'}
                {modalType === 'schemes' && 'Enter topic (e.g., irrigation, fertilizer):'}
              </label>
              <input
                type="text"
                value={modalInput}
                onChange={(e) => setModalInput(e.target.value)}
                placeholder={
                  modalType === 'weather' ? 'e.g., Delhi, Mumbai, Bangalore' :
                  modalType === 'crop' ? 'e.g., Rice, Wheat, Cotton, Sugarcane' :
                  'e.g., Irrigation, Seeds, Fertilizer, Loan'
                }
                onKeyPress={(e) => e.key === 'Enter' && handleModalSubmit()}
                autoFocus
              />
              {modalType === 'crop' && (
                <>
                  <label style={{marginTop: '15px', display: 'block'}}>
                    Location (market):
                  </label>
                  <input
                    type="text"
                    value={modalLocation}
                    onChange={(e) => setModalLocation(e.target.value)}
                    placeholder="e.g., Delhi, Mumbai (defaults to your location)"
                    onKeyPress={(e) => e.key === 'Enter' && handleModalSubmit()}
                  />
                </>
              )}
              {modalType === 'weather' && (
                <p style={{fontSize: '12px', color: '#666', marginTop: '8px'}}>
                  💡 Tip: Use "My Weather" button above for your location ({user?.location})
                </p>
              )}
              {modalType === 'crop' && (
                <p style={{fontSize: '12px', color: '#666', marginTop: '8px'}}>
                  💡 Location defaults to: {user?.location || 'your profile location'}
                </p>
              )}
            </div>
            <div className="modal-footer">
              <button className="cancel-button" onClick={closeModal}>Cancel</button>
              <button className="submit-button" onClick={handleModalSubmit} disabled={!modalInput.trim()}>Get Information</button>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Feedback & Learning Modal (Phase 5) */}
      <EnhancedFeedbackModal
        isOpen={showFeedbackModal}
        onClose={() => {
          setShowFeedbackModal(false)
          setFeedbackModalMode('simple')
        }}
        queryId={currentQueryId}
        initialMode={feedbackModalMode}
      />
    </div>
  )
}

export default App
