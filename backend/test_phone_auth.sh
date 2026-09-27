#!/bin/bash

echo "🔍 Testing Backend with Phone Number..."
echo ""

# Test signup
echo "1️⃣ Testing Signup..."
curl -X POST http://localhost:8000/api/signup \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543210",
    "password": "test123",
    "language": "hi",
    "location": "Mumbai, Maharashtra"
  }' \
  -w "\nStatus: %{http_code}\n\n"

echo ""
echo "2️⃣ Testing Login..."
curl -X POST http://localhost:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+919876543210",
    "password": "test123"
  }' \
  -w "\nStatus: %{http_code}\n\n"

echo ""
echo "✅ Test complete!"
