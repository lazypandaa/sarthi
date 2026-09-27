#!/bin/bash

echo "🌾 Setting up Gram Vaani AI Voice Assistant with Authentication..."

# Backend setup
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt

# Frontend setup
echo "🎨 Installing frontend dependencies..."
cd ../frontend
npm install

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "1. Start backend: cd backend && uvicorn main:app --reload"
echo "2. Start frontend: cd frontend && npm run dev"
echo ""
echo "🔐 Authentication features:"
echo "- User signup with email, password, language, and location"
echo "- Auto-location detection using IP geolocation"
echo "- JWT-based authentication"
echo "- Protected API endpoints"
echo "- User session management"