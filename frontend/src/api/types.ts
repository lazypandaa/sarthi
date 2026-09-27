export interface UserProfile {
  phone_number: string;
  language: string;
  location: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface WeatherData {
  temperature: number;
  humidity: number;
  rainfall: number;
  condition: string;
  alert: string | null;
  cached_at?: string;
  source?: string;
}

export interface EnvironmentalProfile {
  user_phone?: string;
  location: string;
  district: string;
  state: string;
  soil_type: string;
  temperature: number;
  humidity: number;
  rainfall: string;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  soil_ph: number;
  organic_carbon: number;
  recommended_amendments: string;
}

export interface CropRecommendationItem {
  crop_id: string;
  crop_name: string;
  scientific_name?: string;
  category: string;
  soil_compatibility: number;
  climate_match: string;
  water_requirement: string;
  duration_days: number;
  explanation: string;
  key_pests: string[];
  key_diseases: string[];
  source: string;
}

export interface CropCalendarItem {
  id: string;
  name: string;
  season: string;
  planting: { start: string; end: string };
  harvesting: { start: string; end: string };
  duration_days: number;
  soil_type: string;
  rainfall: string;
  tips: string;
  critical_operations: string[];
}

export interface CropCalendarResponse {
  current_season: string;
  user_location: string;
  weather?: { temp: number; humidity: number; description: string };
  recommended_crops: CropCalendarItem[];
}

export interface AgriNewsItem {
  id: string;
  title: string;
  summary: string;
  crop?: string;
  category: string;
  source: string;
  link?: string;
  image?: string;
  published_at?: string;
}

export interface MarketItem {
  record_id: string;
  market: string;
  district: string;
  state: string;
  commodity: string;
  variety?: string;
  arrival_tonnes?: number;
  min_price: number;
  max_price: number;
  modal_price: number;
  unit: string;
  date: string;
  source?: string;
  source_url?: string;
  verified?: boolean;
}

export interface CommunityReport {
  report_id: string;
  user_phone: string;
  village_id: string;
  crop?: string;
  report_type: "pest" | "disease" | "weather" | "success" | string;
  severity: "low" | "medium" | "high" | string;
  description: string;
  description_english?: string;
  language?: string;
  timestamp: string;
  validation_count: number;
  validators: string[];
  verified: boolean;
}

export interface OutbreakVillage {
  village: string;
  state: string;
  coordinates: { lat: number; lng: number };
  pest_count: number;
  disease_count: number;
  total_reports: number;
  alert_level: "low" | "medium" | "high";
  crops_affected: string[];
  recent_reports: Array<{
    type: string;
    crop?: string;
    description: string;
    severity: string;
    timestamp: string;
  }>;
}

export interface OutbreakMapResponse {
  outbreaks: OutbreakVillage[];
  total_reports: number;
  affected_villages: number;
}

export interface LeaderboardItem {
  rank: number;
  village_id: string;
  trust_score: number;
  total_responses: number;
  helpful_count: number;
  tier: string;
  tier_icon: string;
  last_updated?: string;
}

export interface HindsightMemoryItem {
  id?: string;
  text: string;
  type: string;
  source?: string;
  crop?: string | null;
  result?: string | null;
  reason?: string | null;
  timestamp?: string | null;
}

export interface MemorySummaryResponse {
  farmer_id: string;
  has_memory: boolean;
  memory_count: number;
  service_status: { available: boolean; configured: boolean };
  sections: {
    profile: HindsightMemoryItem[];
    preferences: HindsightMemoryItem[];
    past_experience: HindsightMemoryItem[];
    learned_from_you: HindsightMemoryItem[];
  };
  what_changed: Array<{ trigger: string; summary: string; impact: string }>;
  profile_memories: HindsightMemoryItem[];
  constraint_memories: HindsightMemoryItem[];
  preference_memories: HindsightMemoryItem[];
}

export interface RecommendationResponse {
  recommendation_id: string;
  farmer_id: string;
  query: string;
  recommendation: string;
  memory_context: {
    used: boolean;
    memory_count: number;
    types: string[];
  };
  relevant_memories: HindsightMemoryItem[];
  memory_influence: Array<{ memory: string; influence: string }>;
  assembled_context?: Record<string, any>;
}

export interface VoiceAssistantResponse {
  query_id: string;
  recommendation_id?: string;
  response_text: string;
  audio_data?: string | null;
  retained_learning?: any;
  memory_context?: {
    used: boolean;
    memory_count: number;
    types: string[];
  };
  relevant_memories?: HindsightMemoryItem[];
  memory_influence?: Array<{ memory: string; influence: string }>;
}

export interface QueryHistoryItem {
  query_id: string;
  user_phone?: string;
  query: string;
  response: string;
  timestamp: string;
  language?: string;
  helpful?: boolean;
  feedback_text?: string;
}
