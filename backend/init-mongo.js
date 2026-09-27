// MongoDB initialization script for Gram Vaani
db = db.getSiblingDB('gramvaani');

// Create collections
db.createCollection('users');
db.createCollection('queries');

// Create indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.queries.createIndex({ "user_email": 1 });
db.queries.createIndex({ "timestamp": 1 });

// Insert test user
db.users.insertOne({
    email: "test@example.com",
    password: "$2b$12$LQv3c1yqBwlVHpPjrCyeNOSBKtdXRWWM4fowHpzs4Cdquzk5p6tXO", // password123
    language: "en",
    location: "Delhi, India",
    created_at: new Date()
});

print("MongoDB initialized successfully for Gram Vaani!");