// Example React component for displaying hyperlocal context
// Add this to your frontend

import React, { useEffect, useState } from 'react';
import axios from 'axios';

const HyperlocalContext = () => {
  const [context, setContext] = useState(null);
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHyperlocalData();
  }, []);

  const fetchHyperlocalData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch hyperlocal context
      const contextRes = await axios.get('http://localhost:8000/api/hyperlocal-context', { headers });
      setContext(contextRes.data);

      // Fetch success stories
      const storiesRes = await axios.get('http://localhost:8000/api/success-stories?limit=5', { headers });
      setStories(storiesRes.data.stories);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching hyperlocal data:', error);
      setLoading(false);
    }
  };

  const reportPest = async (pestName, crop, severity) => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        'http://localhost:8000/api/report-pest-outbreak',
        null,
        {
          headers: { Authorization: `Bearer ${token}` },
          params: { pest_name: pestName, crop, severity }
        }
      );
      
      if (response.data.outbreak_alert) {
        alert(`⚠️ Outbreak Alert! ${response.data.nearby_reports} reports in your area`);
      } else {
        alert('✅ Pest report submitted successfully');
      }
    } catch (error) {
      console.error('Error reporting pest:', error);
    }
  };

  if (loading) return <div>Loading hyperlocal data...</div>;

  return (
    <div className="hyperlocal-container">
      {/* Location Context Card */}
      {context?.has_data && (
        <div className="context-card">
          <h3>📍 Your Location Context</h3>
          <p><strong>Location:</strong> {context.location}</p>
          <p><strong>Soil Type:</strong> {context.soil_type}</p>
          <p><strong>Rainfall:</strong> {context.rainfall}</p>
          <p><strong>Current Season:</strong> {context.current_season}</p>
          
          <div className="recommended-crops">
            <h4>🌾 Recommended Crops</h4>
            <ul>
              {context.recommended_crops.map((crop, idx) => (
                <li key={idx}>{crop}</li>
              ))}
            </ul>
          </div>

          {context.pest_alerts.length > 0 && (
            <div className="pest-alerts">
              <h4>⚠️ Pest Alerts</h4>
              <ul>
                {context.pest_alerts.map((alert, idx) => (
                  <li key={idx} className="alert-item">{alert}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Success Stories */}
      {stories.length > 0 && (
        <div className="success-stories">
          <h3>🏆 Nearby Farmer Success Stories</h3>
          {stories.map((story, idx) => (
            <div key={idx} className="story-card">
              <h4>{story.farmer}</h4>
              <p className="location">{story.location}</p>
              <p className="achievement">✨ {story.achievement}</p>
              <p className="method"><strong>Method:</strong> {story.method}</p>
            </div>
          ))}
        </div>
      )}

      {/* Pest Report Button */}
      <button 
        className="report-pest-btn"
        onClick={() => reportPest('Fall Armyworm', 'Maize', 'high')}
      >
        🐛 Report Pest Issue
      </button>
    </div>
  );
};

export default HyperlocalContext;

/* CSS Styles */
const styles = `
.hyperlocal-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.context-card, .success-stories {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.context-card h3, .success-stories h3 {
  color: #2d5016;
  margin-bottom: 15px;
}

.recommended-crops, .pest-alerts {
  margin-top: 15px;
}

.pest-alerts .alert-item {
  color: #d32f2f;
  font-weight: 500;
}

.story-card {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
}

.story-card h4 {
  color: #2d5016;
  margin-bottom: 5px;
}

.story-card .location {
  color: #666;
  font-size: 0.9em;
}

.story-card .achievement {
  margin: 10px 0;
  font-weight: 500;
}

.report-pest-btn {
  background: #d32f2f;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  width: 100%;
}

.report-pest-btn:hover {
  background: #b71c1c;
}
`;
