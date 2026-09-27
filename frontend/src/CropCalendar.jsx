import { useState, useEffect } from 'react';
import axios from 'axios';

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
    tips: 'Important Tips',
    loading: 'Loading...',
    error: 'Cannot load data',
    noData: 'No crops available for your area',
    to: 'to'
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
    tips: 'महत्वपूर्ण सुझाव',
    loading: 'लोड हो रहा है...',
    error: 'डेटा लोड नहीं हो सका',
    noData: 'आपके क्षेत्र के लिए कोई फसल उपलब्ध नहीं',
    to: 'से'
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
    tips: 'ముఖ్యమైన చిట్కాలు',
    loading: 'లోడ్ అవుతోంది...',
    error: 'డేటా లోడ్ చేయలేకపోయింది',
    noData: 'మీ ప్రాంతానికి పంటలు అందుబాటులో లేవు',
    to: 'నుండి'
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
    to: 'முதல்'
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
    to: 'ರಿಂದ'
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
    to: 'മുതൽ'
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
    to: 'থেকে'
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
    to: 'થી'
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
    to: 'ते'
  }
};

const CropCalendar = ({ language = 'en' }) => {
  const [calendarData, setCalendarData] = useState(null);
  const [loading, setLoading] = useState(true);
  const t = (key) => translations[language]?.[key] || translations.en[key];

  useEffect(() => {
    fetchCalendar();
  }, [language]);

  const fetchCalendar = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:8000/api/crop-calendar?language=${language}&t=${Date.now()}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      console.log('Calendar data received:', response.data);
      setCalendarData(response.data);
    } catch (error) {
      console.error('Calendar fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={{textAlign: 'center', padding: '40px', fontSize: '20px'}}>{t('loading')}</div>;
  }

  if (!calendarData) {
    return <div style={{textAlign: 'center', padding: '40px', fontSize: '20px', color: 'red'}}>{t('error')}</div>;
  }

  return (
    <div style={{maxWidth: '1200px', margin: '0 auto', padding: '20px', paddingTop: window.innerWidth <= 768 ? '100px' : '90px', paddingBottom: window.innerWidth <= 768 ? '120px' : '100px'}} className="crop-calendar-container">
      {/* Header Info Box */}
      <div style={{
        background: 'linear-gradient(135deg, #2e7d32 0%, #4caf50 100%)',
        color: 'white',
        padding: window.innerWidth <= 768 ? '20px' : '30px',
        borderRadius: '15px',
        marginBottom: '30px',
        boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
      }}>
        <h1 style={{fontSize: window.innerWidth <= 768 ? '24px' : '32px', fontWeight: 'bold', marginBottom: '20px', textAlign: 'center'}}>
          🌾 {t('title')}
        </h1>
        
        <div style={{display: 'grid', gridTemplateColumns: window.innerWidth <= 768 ? '1fr' : 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginTop: '20px'}}>
          <div style={{background: 'rgba(255,255,255,0.2)', padding: '15px', borderRadius: '10px', textAlign: 'center'}}>
            <div style={{fontSize: '14px', opacity: 0.9, marginBottom: '5px'}}>📅 {t('season')}</div>
            <div style={{fontSize: window.innerWidth <= 768 ? '20px' : '24px', fontWeight: 'bold'}}>{calendarData.current_season.toUpperCase()}</div>
          </div>
          
          <div style={{background: 'rgba(255,255,255,0.2)', padding: '15px', borderRadius: '10px', textAlign: 'center'}}>
            <div style={{fontSize: '14px', opacity: 0.9, marginBottom: '5px'}}>📍 {t('location')}</div>
            <div style={{fontSize: window.innerWidth <= 768 ? '16px' : '18px', fontWeight: 'bold'}}>{calendarData.user_location}</div>
          </div>
          
          {calendarData.weather && (
            <>
              <div style={{background: 'rgba(255,255,255,0.2)', padding: '15px', borderRadius: '10px', textAlign: 'center'}}>
                <div style={{fontSize: '14px', opacity: 0.9, marginBottom: '5px'}}>🌡️ {t('temp')}</div>
                <div style={{fontSize: window.innerWidth <= 768 ? '20px' : '24px', fontWeight: 'bold'}}>{calendarData.weather.temp}°C</div>
              </div>
              
              <div style={{background: 'rgba(255,255,255,0.2)', padding: '15px', borderRadius: '10px', textAlign: 'center'}}>
                <div style={{fontSize: '14px', opacity: 0.9, marginBottom: '5px'}}>💧 {t('humidity')}</div>
                <div style={{fontSize: window.innerWidth <= 768 ? '20px' : '24px', fontWeight: 'bold'}}>{calendarData.weather.humidity}%</div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Crops Table */}
      {calendarData.recommended_crops.length > 0 ? (
        <div style={{background: 'white', borderRadius: '15px', overflow: window.innerWidth <= 768 ? 'auto' : 'hidden', boxShadow: '0 2px 10px rgba(0,0,0,0.1)'}}>
          <div style={{overflowX: 'auto', WebkitOverflowScrolling: 'touch'}}>
          <table style={{width: '100%', borderCollapse: 'collapse', fontSize: window.innerWidth <= 768 ? '14px' : '16px', minWidth: window.innerWidth <= 768 ? '800px' : 'auto'}}>
            <thead>
              <tr style={{background: '#4caf50', color: 'white'}}>
                <th style={{padding: window.innerWidth <= 768 ? '15px 10px' : '20px', textAlign: 'left', fontWeight: 'bold', fontSize: window.innerWidth <= 768 ? '16px' : '18px'}}>🌱 {t('cropName')}</th>
                <th style={{padding: window.innerWidth <= 768 ? '15px 10px' : '20px', textAlign: 'left', fontWeight: 'bold', fontSize: window.innerWidth <= 768 ? '16px' : '18px'}}>📅 {t('planting')}</th>
                <th style={{padding: window.innerWidth <= 768 ? '15px 10px' : '20px', textAlign: 'left', fontWeight: 'bold', fontSize: window.innerWidth <= 768 ? '16px' : '18px'}}>🌾 {t('harvest')}</th>
                <th style={{padding: window.innerWidth <= 768 ? '15px 10px' : '20px', textAlign: 'left', fontWeight: 'bold', fontSize: window.innerWidth <= 768 ? '16px' : '18px'}}>⏱️ {t('duration')}</th>
                <th style={{padding: window.innerWidth <= 768 ? '15px 10px' : '20px', textAlign: 'left', fontWeight: 'bold', fontSize: window.innerWidth <= 768 ? '16px' : '18px'}}>💡 {t('tips')}</th>
              </tr>
            </thead>
            <tbody>
              {calendarData.recommended_crops.map((crop, index) => (
                <tr key={crop.id} style={{
                  background: index % 2 === 0 ? '#f9f9f9' : 'white',
                  borderBottom: '1px solid #e0e0e0'
                }}>
                  <td style={{padding: window.innerWidth <= 768 ? '15px 10px' : '20px', fontWeight: 'bold', fontSize: window.innerWidth <= 768 ? '16px' : '18px', color: '#2e7d32'}}>
                    {crop.name}
                    {crop.hindi && <div style={{fontSize: '14px', color: '#666', fontWeight: 'normal', marginTop: '5px'}}>{crop.hindi}</div>}
                  </td>
                  <td style={{padding: window.innerWidth <= 768 ? '15px 10px' : '20px'}}>
                    {crop.planting ? (
                      <div>
                        <div style={{fontWeight: 'bold', color: '#1976d2', fontSize: window.innerWidth <= 768 ? '14px' : '16px'}}>{crop.planting.start}</div>
                        <div style={{fontSize: window.innerWidth <= 768 ? '12px' : '14px', color: '#666'}}>{t('to')} {crop.planting.end}</div>
                      </div>
                    ) : '-'}
                  </td>
                  <td style={{padding: window.innerWidth <= 768 ? '15px 10px' : '20px'}}>
                    {crop.harvesting ? (
                      <div>
                        <div style={{fontWeight: 'bold', color: '#f57c00', fontSize: window.innerWidth <= 768 ? '14px' : '16px'}}>{crop.harvesting.start}</div>
                        <div style={{fontSize: window.innerWidth <= 768 ? '12px' : '14px', color: '#666'}}>{t('to')} {crop.harvesting.end}</div>
                      </div>
                    ) : '-'}
                  </td>
                  <td style={{padding: window.innerWidth <= 768 ? '15px 10px' : '20px'}}>
                    {crop.duration_days ? (
                      <div style={{fontWeight: 'bold', fontSize: window.innerWidth <= 768 ? '16px' : '18px', color: '#7b1fa2'}}>
                        {crop.duration_days} {t('days')}
                      </div>
                    ) : '-'}
                  </td>
                  <td style={{padding: window.innerWidth <= 768 ? '15px 10px' : '20px', fontSize: window.innerWidth <= 768 ? '13px' : '14px', lineHeight: '1.6'}}>
                    {crop.tips && <div style={{marginBottom: '8px'}}>{crop.tips}</div>}
                    {crop.soil_type && (
                      <div style={{background: '#fff3e0', padding: '8px', borderRadius: '5px', marginBottom: '5px'}}>
                        <strong>🏞️ {t('soil')}:</strong> {crop.soil_type}
                      </div>
                    )}
                    {crop.rainfall && (
                      <div style={{background: '#e3f2fd', padding: '8px', borderRadius: '5px', marginBottom: '5px'}}>
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
      ) : (
        <div style={{
          textAlign: 'center',
          padding: '60px',
          background: 'white',
          borderRadius: '15px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
        }}>
          <div style={{fontSize: '48px', marginBottom: '20px'}}>🌾</div>
          <div style={{fontSize: '20px', color: '#666', marginBottom: '10px'}}>{t('noData')}</div>
        </div>
      )}
    </div>
  );
};

export default CropCalendar;
