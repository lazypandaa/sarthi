import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_URL } from './config';

const translations = {
  en: {
    title: 'Crop Calendar',
    season: 'Current Season',
    location: 'Your Location',
    temp: 'Temperature',
    humidity: 'Humidity',
    cropName: 'Crop Name',
    planting: 'When to Plant',
    harvest: 'When to Harvest',
    duration: 'Growing Time',
    days: 'days',
    soil: 'Soil Type',
    rainfall: 'Water Needed',
    tips: 'Important Tips & Operations',
    loading: 'Loading agricultural calendar...',
    error: 'Cannot load calendar data',
    noData: 'No crops available for your area or filter',
    to: 'to',
    allSeasons: 'All Seasons',
    filterBySeason: 'Filter by Season',
    searchCrop: 'Search crop...'
  },
  hi: {
    title: 'फसल कैलेंडर',
    season: 'वर्तमान मौसम',
    location: 'आपका स्थान',
    temp: 'तापमान',
    humidity: 'नमी',
    cropName: 'फसल का नाम',
    planting: 'बुवाई का समय',
    harvest: 'कटाई का समय',
    duration: 'बढ़ने का समय',
    days: 'दिन',
    soil: 'मिट्टी का प्रकार',
    rainfall: 'पानी की जरूरत',
    tips: 'महत्वपूर्ण सुझाव एवं क्रियाएं',
    loading: 'लोड हो रहा है...',
    error: 'डेटा लोड नहीं हो सका',
    noData: 'आपके क्षेत्र के लिए कोई फसल उपलब्ध नहीं',
    to: 'से',
    allSeasons: 'सभी मौसम',
    filterBySeason: 'मौसम अनुसार फिल्टर',
    searchCrop: 'फसल खोजें...'
  },
  te: {
    title: 'పంట క్యాలెండర్',
    season: 'ప్రస్తుత సీజన్',
    location: 'మీ స్థానం',
    temp: 'ఉష్ణోగ్రత',
    humidity: 'తేమ',
    cropName: 'పంట పేరు',
    planting: 'విత్తే సమయం',
    harvest: 'కోసే సమయం',
    duration: 'పెరిగే సమయం',
    days: 'రోజులు',
    soil: 'నేల రకం',
    rainfall: 'నీటి అవసరం',
    tips: 'ముఖ్యమైన చిట్కాలు & పనులు',
    loading: 'లోడ్ అవుతోంది...',
    error: 'డేటా లోడ్ చేయలేకపోయింది',
    noData: 'మీ ప్రాంతానికి పంటలు అందుబాటులో లేవు',
    to: 'నుండి',
    allSeasons: 'అన్ని సీజన్లు',
    filterBySeason: 'సీజన్ ద్వారా ఫిల్టర్',
    searchCrop: 'పంటను శోధించండి...'
  },
  ta: {
    title: 'பயிர் நாட்காட்டி',
    season: 'தற்போதைய பருவம்',
    location: 'உங்கள் இடம்',
    temp: 'வெப்பநிலை',
    humidity: 'ஈரப்பதம்',
    cropName: 'பயிர் பெயர்',
    planting: 'விதைக்கும் நேரம்',
    harvest: 'அறுவடை நேரம்',
    duration: 'வளரும் நேரம்',
    days: 'நாட்கள்',
    soil: 'மண் வகை',
    rainfall: 'நீர் தேவை',
    tips: 'முக்கிய குறிப்புகள்',
    loading: 'ஏற்றுகிறது...',
    error: 'தரவை ஏற்ற முடியவில்லை',
    noData: 'உங்கள் பகுதிக்கு பயிர்கள் கிடைக்கவில்லை',
    to: 'முதல்',
    allSeasons: 'அனைத்து பருவங்கள்',
    filterBySeason: 'பருவத்தின்படி வடிகட்டு',
    searchCrop: 'பயிரைத் தேடுங்கள்...'
  },
  kn: {
    title: 'ಬೆಳೆ ಕ್ಯಾಲೆಂಡರ್',
    season: 'ಪ್ರಸ್ತುತ ಋತು',
    location: 'ನಿಮ್ಮ ಸ್ಥಳ',
    temp: 'ತಾಪಮಾನ',
    humidity: 'ತೇವಾಂಶ',
    cropName: 'ಬೆಳೆ ಹೆಸರು',
    planting: 'ಬಿತ್ತನೆ ಸಮಯ',
    harvest: 'ಕೊಯ್ಲು ಸಮಯ',
    duration: 'ಬೆಳೆಯುವ ಸಮಯ',
    days: 'ದಿನಗಳು',
    soil: 'ಮಣ್ಣಿನ ಪ್ರಕಾರ',
    rainfall: 'ನೀರಿನ ಅವಶ್ಯಕತೆ',
    tips: 'ಪ್ರಮುಖ ಸಲಹೆಗಳು',
    loading: 'ಲೋಡ್ ಆಗುತ್ತಿದೆ...',
    error: 'ಡೇಟಾ ಲೋಡ್ ಮಾಡಲು ಸಾಧ್ಯವಿಲ್ಲ',
    noData: 'ನಿಮ್ಮ ಪ್ರದೇಶಕ್ಕೆ ಬೆಳೆಗಳು ಲಭ್ಯವಿಲ್ಲ',
    to: 'ರಿಂದ',
    allSeasons: 'ಎಲ್ಲಾ ಋತುಗಳು',
    filterBySeason: 'ಋತುವಿನ ಪ್ರಕಾರ ಫಿಲ್ಟರ್',
    searchCrop: 'ಬೆಳೆ ಹುಡುಕಿ...'
  },
  ml: {
    title: 'വിള കലണ്ടർ',
    season: 'നിലവിലെ സീസൺ',
    location: 'നിങ്ങളുടെ സ്ഥലം',
    temp: 'താപനില',
    humidity: 'ഈർപ്പം',
    cropName: 'വിള പേര്',
    planting: 'നടുന്ന സമയം',
    harvest: 'വിളവെടുപ്പ് സമയം',
    duration: 'വളരുന്ന സമയം',
    days: 'ദിവസങ്ങൾ',
    soil: 'മണ്ണിന്റെ തരം',
    rainfall: 'ജല ആവശ്യം',
    tips: 'പ്രധാന നുറുങ്ങുകൾ',
    loading: 'ലോഡ് ചെയ്യുന്നു...',
    error: 'ഡാറ്റ ലോഡ് ചെയ്യാൻ കഴിയില്ല',
    noData: 'നിങ്ങളുടെ പ്രദേശത്തിന് വിളകൾ ലഭ്യമല്ല',
    to: 'മുതൽ',
    allSeasons: 'എല്ലാ സീസണുകളും',
    filterBySeason: 'സീസൺ അനുസരിച്ച് ഫിൽട്ടർ',
    searchCrop: 'വിള തിരയുക...'
  },
  bn: {
    title: 'ফসল ক্যালেন্ডার',
    season: 'বর্তমান মৌসুম',
    location: 'আপনার অবস্থান',
    temp: 'তাপমাত্রা',
    humidity: 'আর্দ্রতা',
    cropName: 'ফসলের নাম',
    planting: 'রোপণের সময়',
    harvest: 'ফসল কাটার সময়',
    duration: 'বৃদ্ধির সময়',
    days: 'দিন',
    soil: 'মাটির ধরন',
    rainfall: 'জলের প্রয়োজন',
    tips: 'গুরুত্বপূর্ণ টিপস',
    loading: 'লোড হচ্ছে...',
    error: 'ডেটা লোড করা যায়নি',
    noData: 'আপনার এলাকার জন্য কোনো ফসল নেই',
    to: 'থেকে',
    allSeasons: 'সব ঋতু',
    filterBySeason: 'ঋতু অনুযায়ী ফিল্টার',
    searchCrop: 'ফসল খুঁজুন...'
  },
  gu: {
    title: 'પાક કેલેન્ડર',
    season: 'વર્તમાન મોસમ',
    location: 'તમારું સ્થાન',
    temp: 'તાપમાન',
    humidity: 'ભેજ',
    cropName: 'પાકનું નામ',
    planting: 'વાવણીનો સમય',
    harvest: 'કાપણીનો સમય',
    duration: 'વૃદ્ધિનો સમય',
    days: 'દિવસો',
    soil: 'માટીનો પ્રકાર',
    rainfall: 'પાણીની જરૂર',
    tips: 'મહત્વપૂર્ણ સૂચનો',
    loading: 'લોડ થઈ રહ્યું છે...',
    error: 'ડેટા લોડ કરી શકાયો નહીં',
    noData: 'તમારા વિસ્તાર માટે કોઈ પાક ઉપલબ્ધ નથી',
    to: 'થી',
    allSeasons: 'બધી ઋતુઓ',
    filterBySeason: 'ઋતુ મુજબ ફિલ્ટર',
    searchCrop: 'પાક શોધો...'
  },
  mr: {
    title: 'पीक कॅलेंडर',
    season: 'सध्याचा हंगाम',
    location: 'तुमचे स्थान',
    temp: 'तापमान',
    humidity: 'आर्द्रता',
    cropName: 'पिकाचे नाव',
    planting: 'लागवडीची वेळ',
    harvest: 'कापणीची वेळ',
    duration: 'वाढीची वेळ',
    days: 'दिवस',
    soil: 'मातीचा प्रकार',
    rainfall: 'पाण्याची गरज',
    tips: 'महत्त्वाच्या सूचना',
    loading: 'लोड होत आहे...',
    error: 'डेटा लोड करता आला नाही',
    noData: 'तुमच्या क्षेत्रासाठी कोणतीही पिके उपलब्ध नाहीत',
    to: 'ते',
    allSeasons: 'सर्व हंगाम',
    filterBySeason: 'हंगामानुसार फिल्टर',
    searchCrop: 'पीक शोधा...'
  }
};

const CropCalendar = ({ language = 'en' }) => {
  const [calendarData, setCalendarData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isMobile, setIsMobile] = useState(typeof window !== 'undefined' ? window.innerWidth <= 768 : false);
  const [selectedSeason, setSelectedSeason] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const t = (key) => translations[language]?.[key] || translations.en[key];

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    fetchCalendar();
  }, [language]);

  const fetchCalendar = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/crop-calendar?language=${language}&t=${Date.now()}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCalendarData(response.data);
    } catch (error) {
      console.error('Calendar fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px', fontSize: '18px', color: '#2e7d32' }}>
        <div style={{ fontSize: '36px', marginBottom: '15px' }}>🌾</div>
        {t('loading')}
      </div>
    );
  }

  if (!calendarData) {
    return (
      <div style={{ textAlign: 'center', padding: '60px 20px', fontSize: '18px', color: '#c62828' }}>
        <div style={{ fontSize: '36px', marginBottom: '15px' }}>⚠️</div>
        {t('error')}
      </div>
    );
  }

  const rawCrops = calendarData.recommended_crops || [];
  const filteredCrops = rawCrops.filter(crop => {
    const matchesSearch = !searchQuery || 
      crop.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (crop.hindi && crop.hindi.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesSeason = selectedSeason === 'ALL' || 
      (crop.season && crop.season.toUpperCase() === selectedSeason.toUpperCase());
    return matchesSearch && matchesSeason;
  });

  return (
    <div style={{
      maxWidth: '1200px', 
      margin: '0 auto', 
      padding: isMobile ? '12px' : '24px', 
      paddingTop: isMobile ? '80px' : '90px', 
      paddingBottom: isMobile ? '100px' : '90px'
    }} className="crop-calendar-container">
      
      {/* Header Info Box */}
      <div style={{
        background: 'linear-gradient(135deg, #1b5e20 0%, #388e3c 100%)',
        color: 'white',
        padding: isMobile ? '20px 16px' : '30px',
        borderRadius: '16px',
        marginBottom: '24px',
        boxShadow: '0 4px 20px rgba(27, 94, 32, 0.25)'
      }}>
        <h1 style={{
          fontSize: isMobile ? '22px' : '30px', 
          fontWeight: 'bold', 
          marginBottom: '16px', 
          textAlign: 'center',
          letterSpacing: '-0.5px'
        }}>
          🌾 {t('title')}
        </h1>
        
        <div style={{
          display: 'grid', 
          gridTemplateColumns: isMobile ? '1fr 1fr' : 'repeat(auto-fit, minmax(180px, 1fr))', 
          gap: isMobile ? '10px' : '16px', 
          marginTop: '16px'
        }}>
          <div style={{ background: 'rgba(255,255,255,0.18)', padding: '12px 14px', borderRadius: '12px', textAlign: 'center' }}>
            <div style={{ fontSize: '12px', opacity: 0.9, marginBottom: '4px' }}>📅 {t('season')}</div>
            <div style={{ fontSize: isMobile ? '17px' : '22px', fontWeight: 'bold' }}>{calendarData.current_season?.toUpperCase()}</div>
          </div>
          
          <div style={{ background: 'rgba(255,255,255,0.18)', padding: '12px 14px', borderRadius: '12px', textAlign: 'center' }}>
            <div style={{ fontSize: '12px', opacity: 0.9, marginBottom: '4px' }}>📍 {t('location')}</div>
            <div style={{ fontSize: isMobile ? '14px' : '17px', fontWeight: 'bold', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {calendarData.user_location}
            </div>
          </div>
          
          {calendarData.weather && (
            <>
              <div style={{ background: 'rgba(255,255,255,0.18)', padding: '12px 14px', borderRadius: '12px', textAlign: 'center' }}>
                <div style={{ fontSize: '12px', opacity: 0.9, marginBottom: '4px' }}>🌡️ {t('temp')}</div>
                <div style={{ fontSize: isMobile ? '17px' : '22px', fontWeight: 'bold' }}>{calendarData.weather.temp}°C</div>
              </div>
              
              <div style={{ background: 'rgba(255,255,255,0.18)', padding: '12px 14px', borderRadius: '12px', textAlign: 'center' }}>
                <div style={{ fontSize: '12px', opacity: 0.9, marginBottom: '4px' }}>💧 {t('humidity')}</div>
                <div style={{ fontSize: isMobile ? '17px' : '22px', fontWeight: 'bold' }}>{calendarData.weather.humidity}%</div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '12px',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '20px',
        background: '#ffffff',
        padding: '12px 16px',
        borderRadius: '12px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.06)'
      }}>
        {/* Season Filter Tabs */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {['ALL', 'RABI', 'KHARIF', 'ZAID'].map((s) => (
            <button
              key={s}
              onClick={() => setSelectedSeason(s)}
              style={{
                padding: '6px 14px',
                borderRadius: '20px',
                border: 'none',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: selectedSeason === s ? 'bold' : 'normal',
                background: selectedSeason === s ? '#2e7d32' : '#e8f5e9',
                color: selectedSeason === s ? '#ffffff' : '#2e7d32',
                transition: 'all 0.2s ease'
              }}
            >
              {s === 'ALL' ? t('allSeasons') : s}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div style={{ minWidth: isMobile ? '100%' : '240px' }}>
          <input
            type="text"
            placeholder={`🔍 ${t('searchCrop')}`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 14px',
              borderRadius: '8px',
              border: '1px solid #c8e6c9',
              fontSize: '14px',
              outline: 'none',
              boxSizing: 'border-box'
            }}
          />
        </div>
      </div>

      {/* Mobile Card Layout vs Desktop Table */}
      {filteredCrops.length > 0 ? (
        isMobile ? (
          /* Responsive Cards for Mobile View (Section 23 compliant) */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {filteredCrops.map((crop) => (
              <div 
                key={crop.id}
                style={{
                  background: '#ffffff',
                  borderRadius: '14px',
                  padding: '16px',
                  boxShadow: '0 2px 10px rgba(0,0,0,0.07)',
                  border: '1px solid #e8f5e9',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '10px'
                }}
              >
                {/* Card Title & Season */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold', color: '#1b5e20' }}>
                      🌱 {crop.name}
                    </h3>
                    {crop.hindi && (
                      <span style={{ fontSize: '13px', color: '#555', fontWeight: 'normal' }}>
                        {crop.hindi}
                      </span>
                    )}
                  </div>
                  {crop.season && (
                    <span style={{
                      fontSize: '11px',
                      fontWeight: 'bold',
                      textTransform: 'uppercase',
                      padding: '3px 8px',
                      borderRadius: '10px',
                      background: '#e8f5e9',
                      color: '#2e7d32'
                    }}>
                      {crop.season}
                    </span>
                  )}
                </div>

                {/* Sowing and Harvesting Dates */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', background: '#f9fbe7', padding: '10px', borderRadius: '10px' }}>
                  <div>
                    <div style={{ fontSize: '11px', color: '#555', fontWeight: 'bold' }}>📅 {t('planting')}</div>
                    <div style={{ fontSize: '13px', color: '#1565c0', fontWeight: '600', marginTop: '2px' }}>
                      {crop.planting ? `${crop.planting.start} ${t('to')} ${crop.planting.end}` : '-'}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '11px', color: '#555', fontWeight: 'bold' }}>🌾 {t('harvest')}</div>
                    <div style={{ fontSize: '13px', color: '#e65100', fontWeight: '600', marginTop: '2px' }}>
                      {crop.harvesting ? `${crop.harvesting.start} ${t('to')} ${crop.harvesting.end}` : '-'}
                    </div>
                  </div>
                </div>

                {/* Duration and Conditions */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', fontSize: '12px' }}>
                  {crop.duration_days && (
                    <span style={{ background: '#f3e5f5', color: '#6a1b9a', padding: '4px 10px', borderRadius: '6px', fontWeight: '600' }}>
                      ⏱️ {crop.duration_days} {t('days')}
                    </span>
                  )}
                  {crop.rainfall && (
                    <span style={{ background: '#e1f5fe', color: '#0277bd', padding: '4px 10px', borderRadius: '6px' }}>
                      💧 {crop.rainfall}
                    </span>
                  )}
                  {crop.soil_type && (
                    <span style={{ background: '#fff8e1', color: '#f57f17', padding: '4px 10px', borderRadius: '6px' }}>
                      🏞️ {crop.soil_type}
                    </span>
                  )}
                </div>

                {/* Tips & Critical Operations */}
                {crop.tips && (
                  <div style={{
                    fontSize: '12px',
                    color: '#37474f',
                    lineHeight: '1.5',
                    background: '#fafafa',
                    padding: '8px 10px',
                    borderRadius: '8px',
                    borderLeft: '3px solid #4caf50'
                  }}>
                    💡 {crop.tips}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          /* Desktop Table View */
          <div style={{ background: 'white', borderRadius: '15px', overflow: 'hidden', boxShadow: '0 2px 10px rgba(0,0,0,0.08)' }}>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '15px' }}>
                <thead>
                  <tr style={{ background: '#2e7d32', color: 'white' }}>
                    <th style={{ padding: '16px 20px', textAlign: 'left', fontWeight: 'bold' }}>🌱 {t('cropName')}</th>
                    <th style={{ padding: '16px 20px', textAlign: 'left', fontWeight: 'bold' }}>📅 {t('planting')}</th>
                    <th style={{ padding: '16px 20px', textAlign: 'left', fontWeight: 'bold' }}>🌾 {t('harvest')}</th>
                    <th style={{ padding: '16px 20px', textAlign: 'left', fontWeight: 'bold' }}>⏱️ {t('duration')}</th>
                    <th style={{ padding: '16px 20px', textAlign: 'left', fontWeight: 'bold' }}>💡 {t('tips')}</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCrops.map((crop, index) => (
                    <tr key={crop.id} style={{
                      background: index % 2 === 0 ? '#fafafa' : 'white',
                      borderBottom: '1px solid #e0e0e0'
                    }}>
                      <td style={{ padding: '16px 20px', fontWeight: 'bold', color: '#1b5e20' }}>
                        {crop.name}
                        {crop.hindi && <div style={{ fontSize: '13px', color: '#666', fontWeight: 'normal', marginTop: '3px' }}>{crop.hindi}</div>}
                        {crop.season && (
                          <span style={{ fontSize: '10px', background: '#e8f5e9', color: '#2e7d32', padding: '2px 6px', borderRadius: '4px', textTransform: 'uppercase' }}>
                            {crop.season}
                          </span>
                        )}
                      </td>
                      <td style={{ padding: '16px 20px' }}>
                        {crop.planting ? (
                          <div>
                            <div style={{ fontWeight: 'bold', color: '#1565c0' }}>{crop.planting.start}</div>
                            <div style={{ fontSize: '13px', color: '#666' }}>{t('to')} {crop.planting.end}</div>
                          </div>
                        ) : '-'}
                      </td>
                      <td style={{ padding: '16px 20px' }}>
                        {crop.harvesting ? (
                          <div>
                            <div style={{ fontWeight: 'bold', color: '#e65100' }}>{crop.harvesting.start}</div>
                            <div style={{ fontSize: '13px', color: '#666' }}>{t('to')} {crop.harvesting.end}</div>
                          </div>
                        ) : '-'}
                      </td>
                      <td style={{ padding: '16px 20px' }}>
                        {crop.duration_days ? (
                          <div style={{ fontWeight: 'bold', color: '#6a1b9a' }}>
                            {crop.duration_days} {t('days')}
                          </div>
                        ) : '-'}
                      </td>
                      <td style={{ padding: '16px 20px', fontSize: '13px', lineHeight: '1.6' }}>
                        {crop.tips && <div style={{ marginBottom: '6px' }}>{crop.tips}</div>}
                        {crop.soil_type && (
                          <div style={{ background: '#fff8e1', padding: '6px 8px', borderRadius: '5px', marginBottom: '4px' }}>
                            <strong>🏞️ {t('soil')}:</strong> {crop.soil_type}
                          </div>
                        )}
                        {crop.rainfall && (
                          <div style={{ background: '#e1f5fe', padding: '6px 8px', borderRadius: '5px' }}>
                            <strong>💧 {t('rainfall')}:</strong> {crop.rainfall}
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )
      ) : (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          background: 'white',
          borderRadius: '16px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.06)'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🌾</div>
          <div style={{ fontSize: '18px', color: '#666' }}>{t('noData')}</div>
        </div>
      )}
    </div>
  );
};

export default CropCalendar;

