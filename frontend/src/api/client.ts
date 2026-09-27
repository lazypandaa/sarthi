import type {
  UserProfile,
  AuthResponse,
  WeatherData,
  EnvironmentalProfile,
  CropRecommendationItem,
  CropCalendarResponse,
  AgriNewsItem,
  MarketItem,
  CommunityReport,
  OutbreakMapResponse,
  LeaderboardItem,
  MemorySummaryResponse,
  RecommendationResponse,
  VoiceAssistantResponse,
  QueryHistoryItem,
} from "./types";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const TOKEN_KEY = "sarthi_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY) || localStorage.getItem("token");
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem("token", token);
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem("token");
}

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const token = getToken();

  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const res = await fetch(url, {
      ...options,
      headers,
    });

    if (res.status === 401) {
      clearToken();
      window.dispatchEvent(new CustomEvent("sarthi:unauthorized"));
      throw new ApiError("Session expired or unauthorized. Please sign in again.", 401);
    }

    if (!res.ok) {
      let errorMsg = `Request failed (${res.status})`;
      let errorData: any = null;
      try {
        errorData = await res.json();
        if (errorData?.detail) {
          if (Array.isArray(errorData.detail)) {
            errorMsg = errorData.detail.map((d: any) => d.msg || JSON.stringify(d)).join(", ");
          } else {
            errorMsg = errorData.detail;
          }
        } else if (errorData?.message) {
          errorMsg = errorData.message;
        }
      } catch {
        // non-json error
      }
      throw new ApiError(errorMsg, res.status, errorData);
    }

    return (await res.json()) as T;
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(err?.message || "Network error. Please check your connection.", 0);
  }
}

export const api = {
  // Authentication
  async login(phone_number: string, password: string): Promise<AuthResponse> {
    const data = await request<AuthResponse>("/api/login", {
      method: "POST",
      body: JSON.stringify({ phone_number, password }),
    });
    if (data.access_token) {
      setToken(data.access_token);
    }
    return data;
  },

  async signup(payload: {
    phone_number: string;
    password: string;
    language: string;
    location: string;
  }): Promise<AuthResponse> {
    const data = await request<AuthResponse>("/api/signup", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    if (data.access_token) {
      setToken(data.access_token);
    }
    return data;
  },

  async getMe(): Promise<UserProfile> {
    return request<UserProfile>("/api/me");
  },

  async updateProfile(payload: { language?: string; location?: string }): Promise<UserProfile> {
    return request<UserProfile>("/api/profile", {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  },

  logout(): void {
    clearToken();
    window.dispatchEvent(new CustomEvent("sarthi:logout"));
  },

  // Location
  async getLocation(): Promise<{ location: string }> {
    return request<{ location: string }>("/api/location");
  },

  async reverseGeocode(latitude: number, longitude: number): Promise<{ address: string }> {
    return request<{ address: string }>("/api/reverse-geocode", {
      method: "POST",
      body: JSON.stringify({ latitude, longitude }),
    });
  },

  // Weather
  async getWeather(location?: string): Promise<WeatherData> {
    const loc = location ? `?location=${encodeURIComponent(location)}` : "";
    return request<WeatherData>(`/api/weather${loc}`);
  },

  async postWeather(city: string, language: string = "en"): Promise<{ text: string; audio_data?: string | null }> {
    return request<{ text: string; audio_data?: string | null }>("/api/weather", {
      method: "POST",
      body: JSON.stringify({ city, language }),
    });
  },

  // Agricultural Profile & Recommendations
  async getEnvironmentalProfile(location?: string): Promise<EnvironmentalProfile> {
    const loc = location ? `?location=${encodeURIComponent(location)}` : "";
    return request<EnvironmentalProfile>(`/api/environmental-profile${loc}`);
  },

  async getCropRecommendations(location?: string): Promise<CropRecommendationItem[]> {
    const loc = location ? `?location=${encodeURIComponent(location)}` : "";
    return request<CropRecommendationItem[]>(`/api/crop-recommendations${loc}`);
  },

  async getPersonalizedRecommendation(payload: {
    query: string;
    crop?: string;
    season?: string;
    location?: string;
    language?: string;
  }): Promise<RecommendationResponse> {
    return request<RecommendationResponse>("/api/recommendation", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async compareMemory(payload: {
    query?: string;
    location?: string;
    language?: string;
  }): Promise<{
    farmer_id: string;
    query: string;
    location: string;
    without_memory: {
      recommendation: string;
      type?: string;
      memories_used?: number;
      description?: string;
    };
    with_memory: {
      recommendation: string;
      type?: string;
      memories_used?: number;
      memory_context?: { memory_count: number; types: string[] };
      relevant_memories?: any[];
      memory_influence?: any[];
      description?: string;
    };
    differences?: string[];
  }> {
    return request("/api/memory/compare", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  // Hindsight Long-term Memory
  async getMemorySummary(): Promise<MemorySummaryResponse> {
    return request<MemorySummaryResponse>("/api/memory/summary");
  },

  async retainMemory(payload: {
    memory_type: string;
    content: string;
    metadata?: Record<string, any>;
    source?: string;
    crop?: string;
    location?: string;
    season?: string;
    confidence?: number;
  }): Promise<{ status: string; memory_id?: string }> {
    return request("/api/memory/retain", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async resetDemoMemory(): Promise<{ status: string; message: string }> {
    return request("/api/memory/demo/reset", {
      method: "POST",
    });
  },

  // Crop Calendar
  async getCropCalendar(crop?: string, location?: string): Promise<CropCalendarResponse> {
    const params = new URLSearchParams();
    if (crop) params.append("crop", crop);
    if (location) params.append("location", location);
    const query = params.toString() ? `?${params.toString()}` : "";
    return request<CropCalendarResponse>(`/api/crop-calendar${query}`);
  },

  // Agricultural Advisories & News
  async getAgriNews(): Promise<AgriNewsItem[]> {
    return request<AgriNewsItem[]>("/api/agriculture-news");
  },

  // Mandi Markets & Crop Prices
  async getMarkets(district?: string): Promise<{ markets: MarketItem[]; count: number }> {
    const d = district ? `?district=${encodeURIComponent(district)}` : "";
    return request<{ markets: MarketItem[]; count: number }>(`/api/markets${d}`);
  },

  async getCropPrices(crop: string, market?: string, language: string = "en"): Promise<{ text: string }> {
    return request<{ text: string }>("/api/crop-prices", {
      method: "POST",
      body: JSON.stringify({ crop, market, language }),
    });
  },

  async getGovSchemes(topic: string, language: string = "en"): Promise<{ text: string }> {
    return request<{ text: string }>("/api/gov-schemes", {
      method: "POST",
      body: JSON.stringify({ topic, language }),
    });
  },

  // Community Reports & Outbreaks
  async getCommunityReports(limit: number = 20): Promise<{ reports: CommunityReport[]; count: number }> {
    return request<{ reports: CommunityReport[]; count: number }>(`/api/community-reports?limit=${limit}`);
  },

  async submitCommunityReport(payload: {
    report_type: string;
    crop?: string;
    description: string;
    severity?: string;
    language?: string;
  }): Promise<{ status: string; message: string; report_id?: string }> {
    return request("/api/community-report", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async validateCommunityReport(reportId: string, helpful: boolean = true): Promise<any> {
    return request(`/api/validate-report/${reportId}`, {
      method: "POST",
      body: JSON.stringify({ helpful }),
    });
  },

  async getOutbreakMap(language: string = "en"): Promise<OutbreakMapResponse> {
    return request<OutbreakMapResponse>(`/api/outbreak-map?language=${language}`);
  },

  async getVillageLeaderboard(): Promise<{ leaderboard: LeaderboardItem[]; total_villages: number }> {
    return request<{ leaderboard: LeaderboardItem[]; total_villages: number }>("/api/village-leaderboard");
  },

  // Voice Assistant / Natural Language
  async processText(text: string, language: string = "en"): Promise<VoiceAssistantResponse> {
    return request<VoiceAssistantResponse>("/process-text", {
      method: "POST",
      body: JSON.stringify({ text, language }),
    });
  },

  async processAudio(audioBlob: Blob, language: string = "en"): Promise<VoiceAssistantResponse> {
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.wav");
    formData.append("language", language);

    return request<VoiceAssistantResponse>("/process-audio", {
      method: "POST",
      body: formData,
    });
  },

  // Feedback (triggers Phase 4 Hindsight Retain loop!)
  async submitFeedback(payload: {
    query_id: string;
    helpful: boolean;
    feedback_text?: string;
    feedback_type?: "general" | "accepted" | "rejected" | "corrected" | "outcome_reported" | string;
    crop?: string;
    outcome_result?: "success" | "failure" | "partial" | string;
    outcome_reason?: string;
    correction_previous?: string;
    correction_new?: string;
  }): Promise<{ status: string; message: string; memory_retained: boolean; memory_id?: string | null }> {
    return request("/api/feedback", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  // Query History
  async getQueryHistory(): Promise<{ queries: QueryHistoryItem[]; count: number }> {
    return request<{ queries: QueryHistoryItem[]; count: number }>("/api/query-history");
  },
};
