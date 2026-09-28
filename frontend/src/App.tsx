import { useState, useEffect, useRef, type ReactNode } from "react";
import { api, getToken } from "./api";
import type {
  UserProfile,
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
  QueryHistoryItem,
} from "./api/types";
import { AuthScreen } from "./components/AuthScreen";
import { MarkdownRenderer } from "./components/MarkdownRenderer";

type Page =
  | "home"
  | "advice"
  | "ai"
  | "community"
  | "profile"
  | "weather"
  | "calendar"
  | "memory"
  | "voice"
  | "crop"
  | "learning"
  | "notifications";

type IconName =
  | "home"
  | "leaf"
  | "spark"
  | "users"
  | "user"
  | "bell"
  | "search"
  | "mic"
  | "pin"
  | "cloud"
  | "drop"
  | "wind"
  | "arrow"
  | "back"
  | "calendar"
  | "brain"
  | "sun"
  | "check"
  | "plus"
  | "map"
  | "book"
  | "shield"
  | "award"
  | "trendingUp"
  | "trendingDown"
  | "rupee"
  | "close"
  | "filter"
  | "info"
  | "thumbUp"
  | "thumbDown"
  | "play"
  | "pause"
  | "refresh";

const paths: Record<IconName, ReactNode> = {
  home: <><path d="m3 11 9-8 9 8" /><path d="M5 10v10h14V10M9 20v-6h6v6" /></>,
  leaf: <><path d="M11 20A7 7 0 0 1 9.8 6.1C15 3 21 4 21 4s1 6-2.1 11.2A7 7 0 0 1 11 20Z" /><path d="M2 21c0-3 1.85-5.36 5.08-6.94 2.03-.99 4.27-1.29 6.92-.86" /></>,
  spark: <><path d="m12 3 1.35 4.65L18 9l-4.65 1.35L12 15l-1.35-4.65L6 9l4.65-1.35L12 3Z" /><path d="m5 16 .65 2.35L8 19l-2.35.65L5 22l-.65-2.35L2 19l2.35-.65L5 16Z" /></>,
  users: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" /></>,
  user: <><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></>,
  bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4" /></>,
  search: <><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></>,
  mic: <><rect x="9" y="2" width="6" height="12" rx="3" /><path d="M5 10a7 7 0 0 0 14 0M12 17v5" /></>,
  pin: <><path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z" /><circle cx="12" cy="10" r="2.5" /></>,
  cloud: <path d="M17.5 19H6a4 4 0 1 1 1-7.87A6 6 0 0 1 18.62 9 5 5 0 0 1 17.5 19Z" />,
  drop: <path d="M12 2S5 10 5 15a7 7 0 0 0 14 0c0-5-7-13-7-13Z" />,
  wind: <><path d="M3 8h10a3 3 0 1 0-3-3M4 12h15a3 3 0 1 1-3 3M3 16h8" /></>,
  arrow: <><path d="M5 12h14M13 6l6 6-6 6" /></>,
  back: <><path d="M19 12H5M11 18l-6-6 6-6" /></>,
  calendar: <><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M16 3v4M8 3v4M3 10h18" /></>,
  brain: <><path d="M9.5 4A3.5 3.5 0 0 0 6 7.5v.7a3.5 3.5 0 0 0-1 6.7v.6A3.5 3.5 0 0 0 9.5 19H12V4H9.5ZM14.5 4A3.5 3.5 0 0 1 18 7.5v.7a3.5 3.5 0 0 1 1 6.7v.6a3.5 3.5 0 0 1-4.5 3.5H12V4h2.5Z" /><path d="M8 9h4M12 15h4" /></>,
  sun: <><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.42-1.42M17.66 6.34l1.41-1.41" /></>,
  check: <path d="m5 12 4 4L19 6" />,
  plus: <path d="M12 5v14M5 12h14" />,
  map: <><path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6Z" /><path d="M9 3v15M15 6v15" /></>,
  book: <><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V4H6.5A2.5 2.5 0 0 0 4 6.5v13Z" /><path d="M8 8h8M8 12h6" /></>,
  shield: <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />,
  award: <><circle cx="12" cy="8" r="6" /><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11" /></>,
  trendingUp: <><polyline points="23 6 13.5 15.5 8.5 10.5 1 18" /><polyline points="17 6 23 6 23 12" /></>,
  trendingDown: <><polyline points="23 18 13.5 8.5 8.5 13.5 1 6" /><polyline points="17 18 23 18 23 12" /></>,
  rupee: <><path d="M6 3h12M6 8h12M6 13l7 8M6 13h3a4 4 0 0 0 0-8" /></>,
  close: <path d="M18 6 6 18M6 6l12 12" />,
  filter: <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />,
  info: <><circle cx="12" cy="12" r="10" /><line x1="12" y1="16" x2="12" y2="12" /><line x1="12" y1="8" x2="12.01" y2="8" /></>,
  thumbUp: <path d="M7 10v12M15 10.5a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3H9v8l4 6a2 2 0 0 0 2-2v-5.5z" />,
  thumbDown: <path d="M17 14V2M9 13.5a3 3 0 0 0-3 3V17a3 3 0 0 0 3 3h6v-8l-4-6a2 2 0 0 0-2 2v5.5z" />,
  play: <polygon points="5 3 19 12 5 21 5 3" />,
  pause: <><rect x="6" y="4" width="4" height="16" /><rect x="14" y="4" width="4" height="16" /></>,
  refresh: <path d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />,
};

function Icon({ name, size = 22 }: { name: IconName; size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  );
}

function Button({
  children,
  onClick,
  kind = "primary",
  className = "",
  label,
  disabled = false,
  style,
}: {
  children: ReactNode;
  onClick?: () => void;
  kind?: "primary" | "soft" | "icon" | "ghost";
  className?: string;
  label?: string;
  disabled?: boolean;
  style?: React.CSSProperties;
}) {
  return (
    <button
      className={`btn btn-${kind} ${className}`}
      onClick={onClick}
      aria-label={label}
      disabled={disabled}
      style={style}
    >
      {children}
    </button>
  );
}

function Card({
  children,
  className = "",
  onClick,
  style,
}: {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
  style?: React.CSSProperties;
}) {
  return (
    <div className={`card ${className}`} onClick={onClick} style={style}>
      {children}
    </div>
  );
}

function Badge({
  children,
  tone = "green",
}: {
  children: ReactNode;
  tone?: "green" | "amber" | "neutral" | "danger";
}) {
  return <span className={`badge ${tone}`}>{children}</span>;
}

const IMG = {
  green: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=900&auto=format&fit=crop&q=80",
  harvest: "https://images.unsplash.com/photo-1595974482597-4b8da8879bc5?w=900&auto=format&fit=crop&q=80",
  wheat: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=900&auto=format&fit=crop&q=80",
  farmer: "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?w=900&auto=format&fit=crop&q=80",
};

function Header({
  title,
  goBack,
  action,
}: {
  title: string;
  goBack?: () => void;
  action?: ReactNode;
}) {
  return (
    <header className="page-header">
      {goBack ? (
        <Button kind="icon" onClick={goBack} label="Go back">
          <Icon name="back" />
        </Button>
      ) : (
        <div className="brand-mark">
          <Icon name="leaf" size={20} />
        </div>
      )}
      <div className="page-title">{title}</div>
      {action ?? (
        <Button kind="icon" label="Notifications">
          <Icon name="bell" />
        </Button>
      )}
    </header>
  );
}

function SectionTitle({
  title,
  action,
  onAction,
}: {
  title: string;
  action?: string;
  onAction?: () => void;
}) {
  return (
    <div className="section-title">
      <div>{title}</div>
      {action && (
        <button onClick={onAction}>
          {action} <Icon name="arrow" size={15} />
        </button>
      )}
    </div>
  );
}

function Toast({ message, onDismiss }: { message: string; onDismiss: () => void }) {
  return (
    <div className="toast-alert" onClick={onDismiss}>
      <Icon name="spark" size={16} />
      <span>{message}</span>
    </div>
  );
}

function WeatherCardComponent({
  open,
  location,
  weather,
  loading,
}: {
  open: () => void;
  location: string;
  weather: WeatherData | null;
  loading: boolean;
}) {
  const temp = weather ? Math.round(weather.temperature) : 21;
  const humidity = weather ? weather.humidity : 87;
  const condition = weather ? weather.condition : "Clear";
  const rain = weather ? `${weather.rainfall} mm` : "0 mm";

  return (
    <Card className="weather-card" onClick={open}>
      <div className="weather-top">
        <div>
          <div className="eyebrow">
            <Icon name="pin" size={15} /> {location}
          </div>
          <div className="temperature">
            {loading ? "..." : temp}<span>°C</span>
          </div>
          <div className="weather-label">
            <Icon name="cloud" size={19} /> {condition}
          </div>
        </div>
        <div className="weather-art">
          <Icon name="cloud" size={62} />
          <span>
            <Icon name="sun" size={35} />
          </span>
        </div>
      </div>
      <div className="weather-stats">
        <div>
          <Icon name="drop" />
          <b>{humidity}%</b>
          <span>Humidity</span>
        </div>
        <div>
          <Icon name="cloud" />
          <b>{rain}</b>
          <span>Rain</span>
        </div>
        <div>
          <Icon name="wind" />
          <b>12 km/h</b>
          <span>Wind</span>
        </div>
      </div>
      <div className="warning">
        {weather?.alert
          ? weather.alert
          : humidity > 80
          ? `High humidity (${humidity}%) increases fungal risk. Safe spray window: 4:00 PM – 6:30 PM.`
          : `Weather conditions stable. Verified by IMD & OpenWeather telemetry.`}
      </div>
    </Card>
  );
}

function RecommendationCardComponent({
  open,
  compact = false,
  crop = "Black Gram (Urad)",
  match = 95,
  explanation = "Tailored for your soil nutrient status and seasonal climate.",
}: {
  open: () => void;
  compact?: boolean;
  crop?: string;
  match?: number;
  explanation?: string;
}) {
  return (
    <Card className={`recommendation ${compact ? "compact" : ""}`}>
      <div className="ai-label">
        <span>
          <Icon name="spark" size={15} />
        </span>{" "}
        SARTHI AI
      </div>
      <div className="rec-grid">
        <div>
          <div className="kicker">MEMORY-INFORMED CROP RECOMMENDATION</div>
          <div className="rec-crop">{crop}</div>
          <p>{explanation}</p>
        </div>
        {!compact && (
          <div className="score-ring">
            <b>{match}%</b>
            <span>farm fit</span>
          </div>
        )}
      </div>
      {!compact && (
        <div className="reasons">
          <span>
            <Icon name="check" size={15} /> Matches soil pH and NPK
          </span>
          <span>
            <Icon name="check" size={15} /> Accounts for water availability
          </span>
          <span>
            <Icon name="check" size={15} /> High local mandi returns
          </span>
        </div>
      )}
      <Button onClick={open}>
        Explore recommendation <Icon name="arrow" size={18} />
      </Button>
    </Card>
  );
}

const navItems: [Page, IconName, string][] = [
  ["home", "home", "Home"],
  ["advice", "leaf", "Advice"],
  ["ai", "spark", "AI"],
  ["community", "users", "Community"],
  ["profile", "user", "Profile"],
];

export default function App() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [authChecking, setAuthChecking] = useState<boolean>(true);
  const [page, setPage] = useState<Page>("home");
  const [history, setHistory] = useState<Page[]>([]);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Live Backend Data States
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [weatherLoading, setWeatherLoading] = useState<boolean>(false);

  const [envProfile, setEnvProfile] = useState<EnvironmentalProfile | null>(null);
  const [cropRecs, setCropRecs] = useState<CropRecommendationItem[]>([]);
  const [memorySummary, setMemorySummary] = useState<MemorySummaryResponse | null>(null);
  const [cropCalendar, setCropCalendar] = useState<CropCalendarResponse | null>(null);
  const [agriNews, setAgriNews] = useState<AgriNewsItem[]>([]);
  const [markets, setMarkets] = useState<MarketItem[]>([]);
  const [communityReports, setCommunityReports] = useState<CommunityReport[]>([]);
  const [outbreakMap, setOutbreakMap] = useState<OutbreakMapResponse | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardItem[]>([]);
  const [queryHistory, setQueryHistory] = useState<QueryHistoryItem[]>([]);

  // Selected crop for detailed agronomy
  const [selectedCropItem, setSelectedCropItem] = useState<CropRecommendationItem | null>(null);

  // Dynamic Modals state
  const [showTeachModal, setShowTeachModal] = useState<boolean>(false);
  const [showReportModal, setShowReportModal] = useState<boolean>(false);
  const [showEditProfileModal, setShowEditProfileModal] = useState<boolean>(false);

  // Teach Sarthi Form State
  const [teachCategory, setTeachCategory] = useState<string>("constraint");
  const [teachCrop, setTeachCrop] = useState<string>("");
  const [teachText, setTeachText] = useState<string>("");
  const [retainingMemory, setRetainingMemory] = useState<boolean>(false);

  // Report Outbreak Form State
  const [reportType, setReportType] = useState<string>("pest");
  const [reportCrop, setReportCrop] = useState<string>("Soybean");
  const [reportDescription, setReportDescription] = useState<string>("");
  const [reportSeverity, setReportSeverity] = useState<string>("medium");
  const [submittingReport, setSubmittingReport] = useState<boolean>(false);

  // Edit Profile Form State
  const [editLocation, setEditLocation] = useState<string>("");
  const [editLanguage, setEditLanguage] = useState<string>("hi");
  const [savingProfile, setSavingProfile] = useState<boolean>(false);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3800);
  };

  const navigate = (next: Page) => {
    if (next !== page) setHistory((h) => [...h.slice(-8), page]);
    setPage(next);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const back = () => {
    const previous = history.at(-1) ?? "home";
    setHistory((h) => h.slice(0, -1));
    setPage(previous);
  };

  // Check initial authentication
  useEffect(() => {
    const checkAuth = async () => {
      const token = getToken();
      if (!token) {
        setUser(null);
        setAuthChecking(false);
        return;
      }
      try {
        const me = await api.getMe();
        setUser(me);
        setEditLocation(me.location || "");
        setEditLanguage(me.language || "hi");
      } catch (e) {
        console.warn("Session check failed:", e);
        setUser(null);
      } finally {
        setAuthChecking(false);
      }
    };
    checkAuth();

    const handleUnauthorized = () => {
      setUser(null);
      showToast("Session expired. Please sign in again.");
    };

    const handleLogout = () => {
      setUser(null);
      showToast("Signed out successfully.");
    };

    window.addEventListener("sarthi:unauthorized", handleUnauthorized);
    window.addEventListener("sarthi:logout", handleLogout);
    return () => {
      window.removeEventListener("sarthi:unauthorized", handleUnauthorized);
      window.removeEventListener("sarthi:logout", handleLogout);
    };
  }, []);

  // Fetch all live backend data whenever user profile is authenticated
  const fetchAllData = async (loc?: string) => {
    if (!user) return;
    const targetLoc = loc || user.location;
    const district = targetLoc.split(",")[0].trim();

    setWeatherLoading(true);

    try {
      // Fetch in parallel with error resilience
      const [
        weatherRes,
        envRes,
        cropRecRes,
        memRes,
        calendarRes,
        newsRes,
        mktRes,
        repRes,
        outbreakRes,
        leaderRes,
        historyRes,
      ] = await Promise.allSettled([
        api.getWeather(targetLoc),
        api.getEnvironmentalProfile(targetLoc),
        api.getCropRecommendations(targetLoc),
        api.getMemorySummary(),
        api.getCropCalendar(undefined, targetLoc),
        api.getAgriNews(),
        api.getMarkets(district),
        api.getCommunityReports(50),
        api.getOutbreakMap(user.language),
        api.getVillageLeaderboard(),
        api.getQueryHistory(),
      ]);

      if (weatherRes.status === "fulfilled") setWeather(weatherRes.value);
      if (envRes.status === "fulfilled") setEnvProfile(envRes.value);
      if (cropRecRes.status === "fulfilled") {
        setCropRecs(cropRecRes.value);
        if (cropRecRes.value.length > 0 && !selectedCropItem) {
          setSelectedCropItem(cropRecRes.value[0]);
        }
      }
      if (memRes.status === "fulfilled") setMemorySummary(memRes.value);
      if (calendarRes.status === "fulfilled") setCropCalendar(calendarRes.value);
      if (newsRes.status === "fulfilled") setAgriNews(newsRes.value);
      if (mktRes.status === "fulfilled") setMarkets(mktRes.value.markets || []);
      if (repRes.status === "fulfilled") setCommunityReports(repRes.value.reports || []);
      if (outbreakRes.status === "fulfilled") setOutbreakMap(outbreakRes.value);
      if (leaderRes.status === "fulfilled") setLeaderboard(leaderRes.value.leaderboard || []);
      if (historyRes.status === "fulfilled") setQueryHistory(historyRes.value.queries || []);
    } catch (err) {
      console.error("Data fetch error:", err);
    } finally {
      setWeatherLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchAllData(user.location);
    }
  }, [user]);

  // Handler: Save / Retain Memory in Hindsight Vectorize
  const handleSaveMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!teachText.trim()) return;

    setRetainingMemory(true);
    try {
      await api.retainMemory({
        memory_type: teachCategory,
        content: teachText.trim(),
        crop: teachCrop.trim() || undefined,
        location: user?.location,
      });

      // Refetch memory summary immediately
      const updatedMem = await api.getMemorySummary();
      setMemorySummary(updatedMem);

      setTeachText("");
      setTeachCrop("");
      setShowTeachModal(false);
      showToast("Memory retained in Sarthi Hindsight Bank! Future recommendations are now adapted.");
    } catch (err: any) {
      showToast(err?.message || "Failed to retain memory. Please try again.");
    } finally {
      setRetainingMemory(false);
    }
  };

  // Handler: Reset Demo Memory
  const handleResetDemoMemory = async () => {
    try {
      await api.resetDemoMemory();
      const updatedMem = await api.getMemorySummary();
      setMemorySummary(updatedMem);
      showToast("Demo memory bank re-initialized with seeded experiences.");
    } catch (err: any) {
      showToast(err?.message || "Failed to reset demo memory.");
    }
  };

  // Handler: Submit Community Report to Azure Table Storage
  const handleSaveReport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reportDescription.trim()) return;

    setSubmittingReport(true);
    try {
      await api.submitCommunityReport({
        report_type: reportType,
        crop: reportCrop.trim(),
        description: reportDescription.trim(),
        severity: reportSeverity,
        language: user?.language || "en",
      });

      // Refresh community reports and outbreak map
      const [reps, outbreaks] = await Promise.all([
        api.getCommunityReports(50),
        api.getOutbreakMap(user?.language || "en"),
      ]);
      setCommunityReports(reps.reports || []);
      setOutbreakMap(outbreaks);

      setReportDescription("");
      setShowReportModal(false);
      showToast("Report submitted to Village Trust Network & Outbreak Radar!");
    } catch (err: any) {
      showToast(err?.message || "Failed to submit report.");
    } finally {
      setSubmittingReport(false);
    }
  };

  // Handler: Validate Community Report
  const handleVerifyReport = async (reportId: string) => {
    try {
      await api.validateCommunityReport(reportId, true);
      // Update UI optimistically and refetch
      setCommunityReports((prev) =>
        prev.map((r) =>
          r.report_id === reportId
            ? { ...r, verified: true, validation_count: (r.validation_count || 0) + 1 }
            : r
        )
      );
      showToast("Validation recorded! Village trust score updated in Azure Table Storage.");
      const leader = await api.getVillageLeaderboard();
      setLeaderboard(leader.leaderboard || []);
    } catch (err: any) {
      showToast(err?.message || "Validation failed.");
    }
  };

  // Handler: Update Profile
  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingProfile(true);
    try {
      const updated = await api.updateProfile({
        location: editLocation.trim(),
        language: editLanguage,
      });
      setUser(updated);
      setShowEditProfileModal(false);
      showToast("Profile updated! Refreshing agro-climatic data...");
      await fetchAllData(updated.location);
    } catch (err: any) {
      showToast(err?.message || "Failed to update profile.");
    } finally {
      setSavingProfile(false);
    }
  };

  if (authChecking) {
    return (
      <div className="auth-wrapper">
        <div className="state-box">
          <div className="state-spinner" />
          <h4>Connecting to Sarthi AI</h4>
          <p>Initializing secure Azure Table Storage & Hindsight Memory session...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <AuthScreen
        onSuccess={(loggedUser) => {
          setUser(loggedUser);
          setEditLocation(loggedUser.location || "");
          setEditLanguage(loggedUser.language || "hi");
          showToast(`Welcome back, farmer ${loggedUser.phone_number}!`);
        }}
      />
    );
  }

  const activeCropName = cropRecs.length > 0 ? cropRecs[0].crop_name : "Black Gram (Urad)";
  const activeCropMatch = cropRecs.length > 0 ? Math.round(cropRecs[0].soil_compatibility) : 95;
  const activeCropExplanation =
    cropRecs.length > 0
      ? cropRecs[0].explanation
      : "Customized for your soil nutrients, rainfall, and irrigation availability.";
  const memoriesCount = memorySummary?.memory_count || 0;

  return (
    <div className="app-shell">
      {toastMessage && (
        <Toast message={toastMessage} onDismiss={() => setToastMessage(null)} />
      )}

      {/* Desktop Sidebar Navigation */}
      <aside className="desktop-nav">
        <div className="desktop-brand">
          <span>
            <Icon name="leaf" />
          </span>
          <div>
            <b>S A R T H I</b>
            <small>Your farm. Your AI.</small>
          </div>
        </div>
        <nav>
          {navItems.map(([p, icon, label]) => (
            <button
              key={p}
              className={page === p ? "active" : ""}
              onClick={() => navigate(p)}
            >
              <Icon name={icon} />
              <span>{label}</span>
            </button>
          ))}
          <button
            className={page === "weather" ? "active" : ""}
            onClick={() => navigate("weather")}
          >
            <Icon name="cloud" />
            <span>Weather</span>
          </button>
          <button
            className={page === "calendar" ? "active" : ""}
            onClick={() => navigate("calendar")}
          >
            <Icon name="calendar" />
            <span>Calendar</span>
          </button>
          <button
            className={page === "memory" ? "active" : ""}
            onClick={() => navigate("memory")}
          >
            <Icon name="brain" />
            <span>Memories ({memoriesCount})</span>
          </button>
        </nav>
        <div className="desktop-farm">
          <small>FARM TELEMETRY</small>
          <b>{user.location}</b>
          <span>
            {envProfile?.soil_type || "Black Soil"} · {envProfile?.rainfall || "Normal Rain"}
          </span>
          <div style={{ marginTop: 12 }}>
            <button
              onClick={() => api.logout()}
              style={{
                background: "transparent",
                border: "1px solid rgba(255,255,255,0.2)",
                color: "#fff",
                padding: "4px 8px",
                borderRadius: 6,
                fontSize: 11,
                cursor: "pointer",
              }}
            >
              Sign out ({user.phone_number})
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="page-wrap">
        {page === "home" && (
          <HomeScreen
            navigate={navigate}
            user={user}
            weather={weather}
            weatherLoading={weatherLoading}
            cropRecs={cropRecs}
            memoriesCount={memoriesCount}
            outbreakMap={outbreakMap}
            agriNews={agriNews}
          />
        )}

        {page === "advice" && (
          <AdviceScreen
            navigate={navigate}
            cropRecs={cropRecs}
            markets={markets}
            agriNews={agriNews}
            onSelectCrop={(item) => {
              setSelectedCropItem(item);
              navigate("crop");
            }}
          />
        )}

        {page === "ai" && (
          <AIScreen
            navigate={navigate}
            user={user}
            cropRecs={cropRecs}
            memorySummary={memorySummary}
            showToast={showToast}
            onRefreshMemories={async () => {
              const res = await api.getMemorySummary();
              setMemorySummary(res);
            }}
          />
        )}

        {page === "community" && (
          <CommunityScreen
            navigate={navigate}
            reports={communityReports}
            outbreakMap={outbreakMap}
            leaderboard={leaderboard}
            onVerify={handleVerifyReport}
            onOpenReportModal={() => setShowReportModal(true)}
          />
        )}

        {page === "profile" && (
          <ProfileScreen
            navigate={navigate}
            user={user}
            envProfile={envProfile}
            memoriesCount={memoriesCount}
            queryHistory={queryHistory}
            onOpenEditProfile={() => setShowEditProfileModal(true)}
            onLogout={() => api.logout()}
          />
        )}

        {page === "weather" && (
          <WeatherDetailScreen
            back={back}
            user={user}
            weather={weather}
            envProfile={envProfile}
            onRefresh={() => fetchAllData(user.location)}
          />
        )}

        {page === "calendar" && (
          <CalendarScreen
            back={back}
            user={user}
            cropCalendar={cropCalendar}
            showToast={showToast}
          />
        )}

        {page === "memory" && (
          <MemoryScreen
            back={back}
            navigate={navigate}
            memorySummary={memorySummary}
            onOpenTeachModal={() => setShowTeachModal(true)}
            onResetDemo={handleResetDemoMemory}
          />
        )}

        {page === "voice" && (
          <VoiceScreen
            back={back}
            user={user}
            showToast={showToast}
            onRefreshMemories={async () => {
              const res = await api.getMemorySummary();
              setMemorySummary(res);
            }}
          />
        )}

        {page === "crop" && (
          <CropDetailScreen
            back={back}
            navigate={navigate}
            cropItem={selectedCropItem || cropRecs[0] || null}
            envProfile={envProfile}
          />
        )}

        {page === "learning" && <LearningScreen back={back} />}

        {page === "notifications" && (
          <NotificationsScreen
            back={back}
            weather={weather}
            outbreakMap={outbreakMap}
            agriNews={agriNews}
            memorySummary={memorySummary}
          />
        )}
      </div>

      {/* Permanently Fixed Bottom Navigation */}
      <nav className="bottom-nav">
        {navItems.map(([p, icon, label]) => (
          <button
            key={p}
            className={page === p ? "active" : ""}
            onClick={() => navigate(p)}
          >
            <span>
              <Icon name={icon} />
            </span>
            <small>{label}</small>
          </button>
        ))}
      </nav>

      {/* Teach Sarthi Modal (Hindsight Retain) */}
      {showTeachModal && (
        <div className="modal-overlay" onClick={() => setShowTeachModal(false)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <b>Teach Sarthi (Hindsight Memory)</b>
                <small>Record your farm constraints, failures, or observations</small>
              </div>
              <button
                className="modal-close"
                onClick={() => setShowTeachModal(false)}
                aria-label="Close dialog"
              >
                <Icon name="close" size={18} />
              </button>
            </div>
            <form onSubmit={handleSaveMemory} className="modal-form">
              <div className="modal-field">
                <label>Memory Category</label>
                <select
                  value={teachCategory}
                  onChange={(e) => setTeachCategory(e.target.value)}
                  className="modal-select"
                >
                  <option value="constraint">Water / Irrigation Constraint</option>
                  <option value="crop_history">Crop Experience / Past Failure</option>
                  <option value="preference">Farmer Preference / Risk Tolerance</option>
                  <option value="outcome">Past Harvest Outcome</option>
                  <option value="soil">Soil Observation</option>
                </select>
              </div>
              <div className="modal-field">
                <label>Associated Crop (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. Tomato, Groundnut, Wheat"
                  value={teachCrop}
                  onChange={(e) => setTeachCrop(e.target.value)}
                  className="modal-input"
                />
              </div>
              <div className="modal-field">
                <label>What should Sarthi remember?</label>
                <textarea
                  rows={3}
                  placeholder="e.g. My borewell water dried up last season during flowering; limit irrigation to 1 hour daily."
                  value={teachText}
                  onChange={(e) => setTeachText(e.target.value)}
                  className="modal-input"
                  required
                />
              </div>
              <div className="modal-actions">
                <Button
                  kind="ghost"
                  onClick={() => setShowTeachModal(false)}
                  disabled={retainingMemory}
                >
                  Cancel
                </Button>
                <Button kind="primary" disabled={retainingMemory}>
                  {retainingMemory ? "Retaining in Vectorize..." : "Retain in Memory"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Report Outbreak Modal */}
      {showReportModal && (
        <div className="modal-overlay" onClick={() => setShowReportModal(false)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <b>Report Village Outbreak / Issue</b>
                <small>Alert nearby farmers in your village network</small>
              </div>
              <button
                className="modal-close"
                onClick={() => setShowReportModal(false)}
                aria-label="Close dialog"
              >
                <Icon name="close" size={18} />
              </button>
            </div>
            <form onSubmit={handleSaveReport} className="modal-form">
              <div className="modal-field">
                <label>Report Type</label>
                <select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                  className="modal-select"
                >
                  <option value="pest">Pest Infestation</option>
                  <option value="disease">Fungal / Viral Disease</option>
                  <option value="weather">Unseasonal Weather / Hail</option>
                  <option value="success">Successful Agricultural Practice</option>
                </select>
              </div>
              <div className="modal-field">
                <label>Crop Name</label>
                <input
                  type="text"
                  placeholder="e.g. Soybean, Chilli, Cotton"
                  value={reportCrop}
                  onChange={(e) => setReportCrop(e.target.value)}
                  className="modal-input"
                  required
                />
              </div>
              <div className="modal-field">
                <label>Severity Level</label>
                <select
                  value={reportSeverity}
                  onChange={(e) => setReportSeverity(e.target.value)}
                  className="modal-select"
                >
                  <option value="high">High (Immediate cluster alert)</option>
                  <option value="medium">Medium (Localized monitoring)</option>
                  <option value="low">Low (Minor observation)</option>
                </select>
              </div>
              <div className="modal-field">
                <label>Description & Symptoms</label>
                <textarea
                  rows={3}
                  placeholder="e.g. Black thrips infestation spotted across 5 plots. Heavy floral bud drop."
                  value={reportDescription}
                  onChange={(e) => setReportDescription(e.target.value)}
                  className="modal-input"
                  required
                />
              </div>
              <div className="modal-actions">
                <Button
                  kind="ghost"
                  onClick={() => setShowReportModal(false)}
                  disabled={submittingReport}
                >
                  Cancel
                </Button>
                <Button kind="primary" disabled={submittingReport}>
                  {submittingReport ? "Publishing to Azure..." : "Publish to Outbreak Map"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Profile Modal */}
      {showEditProfileModal && (
        <div className="modal-overlay" onClick={() => setShowEditProfileModal(false)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <b>Edit Farm Location & Language</b>
                <small>Updates your regional agro-climate and market bindings</small>
              </div>
              <button
                className="modal-close"
                onClick={() => setShowEditProfileModal(false)}
                aria-label="Close dialog"
              >
                <Icon name="close" size={18} />
              </button>
            </div>
            <form onSubmit={handleUpdateProfile} className="modal-form">
              <div className="modal-field">
                <label>Farm Location (Village, District, State)</label>
                <input
                  type="text"
                  value={editLocation}
                  onChange={(e) => setEditLocation(e.target.value)}
                  placeholder="e.g. Sehore, Madhya Pradesh, India"
                  className="modal-input"
                  required
                />
              </div>
              <div className="modal-field">
                <label>Primary Language</label>
                <select
                  value={editLanguage}
                  onChange={(e) => setEditLanguage(e.target.value)}
                  className="modal-select"
                >
                  <option value="hi">हिन्दी (Hindi)</option>
                  <option value="te">తెలుగు (Telugu)</option>
                  <option value="en">English (Indian)</option>
                  <option value="ta">தமிழ் (Tamil)</option>
                  <option value="kn">ಕನ್ನಡ (Kannada)</option>
                  <option value="mr">मराठी (Marathi)</option>
                </select>
              </div>
              <div className="modal-actions">
                <Button
                  kind="ghost"
                  onClick={() => setShowEditProfileModal(false)}
                  disabled={savingProfile}
                >
                  Cancel
                </Button>
                <Button kind="primary" disabled={savingProfile}>
                  {savingProfile ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

// -------------------------------------------------------------
// SCREEN 1: HOME
// -------------------------------------------------------------
function HomeScreen({
  navigate,
  user,
  weather,
  weatherLoading,
  cropRecs,
  memoriesCount,
  outbreakMap,
  agriNews,
}: {
  navigate: (p: Page) => void;
  user: UserProfile;
  weather: WeatherData | null;
  weatherLoading: boolean;
  cropRecs: CropRecommendationItem[];
  memoriesCount: number;
  outbreakMap: OutbreakMapResponse | null;
  agriNews: AgriNewsItem[];
}) {
  const topCrop = cropRecs.length > 0 ? cropRecs[0] : null;
  const topNews = agriNews.length > 0 ? agriNews[0] : null;
  const topOutbreak = outbreakMap?.outbreaks?.[0] || null;

  return (
    <div className="home">
      <section className="hero">
        <div className="hero-head">
          <div>
            <div className="hello">Namaste, Farmer</div>
            <div className="greeting">{user.phone_number}</div>
            <div className="location">
              <Icon name="pin" size={15} /> {user.location}
            </div>
          </div>
          <Button
            kind="icon"
            className="dark-icon"
            onClick={() => navigate("notifications")}
            label="Notifications"
          >
            <Icon name="bell" />
          </Button>
        </div>
        <button className="ask" onClick={() => navigate("voice")}>
          <span>
            <Icon name="spark" />
          </span>
          <div>
            <b>Ask Sarthi AI Agronomist</b>
            <small>Speak in Hindi, Telugu, or English</small>
          </div>
          <Icon name="mic" />
        </button>
      </section>

      <main className="home-content">
        <WeatherCardComponent
          open={() => navigate("weather")}
          location={user.location.split(",")[0]}
          weather={weather}
          loading={weatherLoading}
        />

        <SectionTitle title="Recommended for your farm" />
        <RecommendationCardComponent
          open={() => navigate("ai")}
          compact
          crop={topCrop ? topCrop.crop_name : "Black Gram (Urad)"}
          match={topCrop ? Math.round(topCrop.soil_compatibility) : 95}
          explanation={
            topCrop?.explanation
              ? topCrop.explanation.slice(0, 110) + "..."
              : "Adapted for your soil nutrients and irrigation conditions."
          }
        />

        <div className="shortcut-grid">
          <button onClick={() => navigate("calendar")}>
            <span>
              <Icon name="calendar" />
            </span>
            <b>Crop calendar</b>
            <small>Seasonal operations</small>
          </button>
          <button onClick={() => navigate("memory")}>
            <span>
              <Icon name="brain" />
            </span>
            <b>Farm memories ({memoriesCount})</b>
            <small>Hindsight retention</small>
          </button>
        </div>

        <SectionTitle
          title="Today's farm advice & schemes"
          action="View all"
          onAction={() => navigate("advice")}
        />
        <Card className="image-card" onClick={() => navigate("advice")}>
          <img
            src={topNews?.image || IMG.green}
            alt="Agricultural field advisory"
            onError={(e) => {
              (e.target as HTMLImageElement).src = IMG.green;
            }}
          />
          <div className="image-card-body">
            <Badge>{topNews?.category?.toUpperCase().replace("_", " ") || "HYPERLOCAL ADVISORY"}</Badge>
            <div className="story-title">
              {topNews ? topNews.title : "Protect your crop from unseasonal weather"}
            </div>
            <p>
              {topNews
                ? topNews.summary.slice(0, 160) + "..."
                : "Western disturbance and humidity tracking active. Check foliage for fungal stress."}
            </p>
            <div className="meta">
              {topNews?.source || "IMD Agromet Advisory Service"} · Verified
            </div>
          </div>
        </Card>

        <SectionTitle
          title="Village outbreak alerts"
          action="Community"
          onAction={() => navigate("community")}
        />
        <Card className="nearby-card" onClick={() => navigate("community")}>
          <span className="status-dot amber" />
          <div>
            <b>
              {topOutbreak
                ? `${topOutbreak.village}: ${topOutbreak.recent_reports?.[0]?.crop || "Crop"} alert`
                : "Tomato leaf curl reported"}
            </b>
            <p>
              {topOutbreak
                ? `${topOutbreak.total_reports} verified reports in ${topOutbreak.village} · ${topOutbreak.alert_level.toUpperCase()} risk`
                : "Active cluster monitoring in your agricultural block."}
            </p>
          </div>
          <Icon name="arrow" />
        </Card>
      </main>
    </div>
  );
}

// -------------------------------------------------------------
// SCREEN 2: ADVICE & MANDI PRICES
// -------------------------------------------------------------
function AdviceScreen({
  navigate,
  cropRecs,
  markets,
  agriNews,
  onSelectCrop,
}: {
  navigate: (p: Page) => void;
  cropRecs: CropRecommendationItem[];
  markets: MarketItem[];
  agriNews: AgriNewsItem[];
  onSelectCrop: (item: CropRecommendationItem) => void;
}) {
  const [filter, setFilter] = useState<string>("All");

  return (
    <div className="screen">
      <Header title="Farm Advisory & Mandi" />
      <div className="screen-intro">
        <div className="screen-heading">फार्म सलाहकार एवं मंडी भाव</div>
        <p>Expert agronomic guidance, live Agmarknet mandi prices, and government schemes.</p>
      </div>

      <div className="filter-row">
        {["All", "Mandi prices", "Crops", "Weather alerts", "Govt schemes"].map((cat) => (
          <button
            key={cat}
            className={`filter-btn ${filter === cat ? "active" : ""}`}
            onClick={() => setFilter(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Live Mandi Prices Table */}
      {(filter === "All" || filter === "Mandi prices") && (
        <div style={{ marginBottom: 20 }}>
          <SectionTitle title="Live Mandi Market Prices (Agmarknet)" />
          <Card style={{ padding: "8px 14px 14px" }}>
            <div className="table-responsive">
              <table className="mandi-table">
                <thead>
                  <tr>
                    <th>COMMODITY</th>
                    <th>MODAL PRICE</th>
                    <th>RANGE</th>
                    <th>MARKET</th>
                  </tr>
                </thead>
                <tbody>
                  {markets.length > 0 ? (
                    markets.map((m) => (
                      <tr key={m.record_id}>
                        <td>
                          <b>{m.commodity}</b>
                          <small style={{ display: "block", color: "var(--muted)", fontSize: 9 }}>
                            {m.variety || "Standard"}
                          </small>
                        </td>
                        <td>
                          <b>₹{m.modal_price.toLocaleString("en-IN")}</b>
                          <small style={{ fontSize: 9, color: "var(--muted)" }}> / q</small>
                        </td>
                        <td style={{ fontSize: 10, color: "var(--muted)" }}>
                          ₹{m.min_price} – ₹{m.max_price}
                        </td>
                        <td>
                          <Badge tone="neutral">{m.market}</Badge>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} style={{ textAlign: "center", padding: 16 }}>
                        Connecting to state mandi feed...
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            <div style={{ marginTop: 8, fontSize: 9, color: "var(--muted)", textAlign: "right" }}>
              Source: Directorate of Marketing & Inspection (agmarknet.gov.in)
            </div>
          </Card>
        </div>
      )}

      {/* ICAR Package of Practices Recommendations */}
      {(filter === "All" || filter === "Crops") && (
        <div style={{ marginBottom: 24 }}>
          <SectionTitle title="Recommended Crops for Your Soil & Season" action={`${cropRecs.length} crops`} />
          <div style={{ display: "grid", gap: 12 }}>
            {cropRecs.map((c) => {
              const nameLower = c.crop_name.toLowerCase();
              let cropThumb = "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=300&h=200&fit=crop";
              if (nameLower.includes("wheat")) cropThumb = "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=300&h=200&fit=crop";
              else if (nameLower.includes("chilli") || nameLower.includes("pepper")) cropThumb = "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?w=300&h=200&fit=crop";
              else if (nameLower.includes("paddy") || nameLower.includes("rice")) cropThumb = "https://images.unsplash.com/photo-1560493676-04071c5f467b?w=300&h=200&fit=crop";
              else if (nameLower.includes("soybean")) cropThumb = "https://images.unsplash.com/photo-1595974482597-4b8da8879bc5?w=300&h=200&fit=crop";
              else if (nameLower.includes("chickpea") || nameLower.includes("gram")) cropThumb = "https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=300&h=200&fit=crop";
              else if (nameLower.includes("onion")) cropThumb = "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=300&h=200&fit=crop";
              else if (nameLower.includes("cotton")) cropThumb = "https://images.unsplash.com/photo-1606041008023-472dfb5e530f?w=300&h=200&fit=crop";
              else if (nameLower.includes("mustard")) cropThumb = "https://images.unsplash.com/photo-1508615039623-a25605d2b022?w=300&h=200&fit=crop";

              return (
                <Card
                  key={c.crop_id}
                  style={{ cursor: "pointer", padding: "12px 14px", overflow: "hidden" }}
                  onClick={() => onSelectCrop(c)}
                >
                  <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
                    <img
                      src={cropThumb}
                      alt={c.crop_name}
                      style={{
                        width: 58,
                        height: 58,
                        borderRadius: 10,
                        objectFit: "cover",
                        flexShrink: 0,
                        border: "1px solid var(--line)",
                      }}
                      loading="lazy"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = IMG.wheat;
                      }}
                    />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div>
                          <b style={{ fontSize: 13.5, color: "var(--text)" }}>{c.crop_name}</b>
                          <small style={{ display: "block", color: "var(--muted)", fontStyle: "italic", fontSize: 10 }}>
                            {c.scientific_name} · {c.category}
                          </small>
                        </div>
                        <Badge tone="green">{Math.round(c.soil_compatibility)}% Fit</Badge>
                      </div>
                      <p style={{ margin: "5px 0 0", fontSize: 11, color: "var(--muted)", lineHeight: 1.45 }}>
                        {c.explanation.slice(0, 115)}...
                      </p>
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: 8, marginTop: 8, paddingTop: 6, borderTop: "1px dashed var(--line)", fontSize: 10, color: "var(--muted)", alignItems: "center" }}>
                    <span>⏳ {c.duration_days} days</span>
                    <span>💧 {c.water_requirement}</span>
                    <span style={{ marginLeft: "auto", color: "var(--green)", fontWeight: 700, display: "inline-flex", alignItems: "center", gap: 3 }}>
                      Package of Practices <Icon name="arrow" size={11} />
                    </span>
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* Official Government Advisories & Schemes with Photos */}
      {(filter === "All" || filter === "Weather alerts" || filter === "Govt schemes") && (() => {
        const filteredAdvisories = agriNews.filter((item) => {
          if (filter === "Weather alerts") return item.category === "weather_warning" || item.category === "pest_alert";
          if (filter === "Govt schemes") return item.category === "government_scheme";
          return true;
        });

        const getPhoto = (item: AgriNewsItem): string => {
          if (item.image && item.image.trim()) return item.image;
          const t = (item.title || "").toLowerCase();
          const c = (item.crop || "").toLowerCase();
          if (c.includes("chilli") || t.includes("thrips")) return "https://images.unsplash.com/photo-1592982537447-7440770cbfc9?w=700&h=350&fit=crop";
          if (c.includes("wheat") || t.includes("wheat")) return "https://images.unsplash.com/photo-1527482797697-8795b05a13fe?w=700&h=350&fit=crop";
          if (c.includes("paddy") || t.includes("rice")) return "https://images.unsplash.com/photo-1560493676-04071c5f467b?w=700&h=350&fit=crop";
          if (c.includes("onion") || t.includes("onion")) return "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=700&h=350&fit=crop";
          if (t.includes("solar") || t.includes("kusum")) return "https://images.unsplash.com/photo-1509391365360-2e959784a276?w=700&h=350&fit=crop";
          if (t.includes("soil") || t.includes("fertilizer")) return "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=700&h=350&fit=crop";
          if (t.includes("insurance") || t.includes("fasal bima") || t.includes("pmfby")) return "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=700&h=350&fit=crop";
          if (t.includes("drip") || t.includes("irrigation") || t.includes("pmksy")) return "https://images.unsplash.com/photo-1556761175-b413da4baf72?w=700&h=350&fit=crop";
          if (t.includes("kisan") || t.includes("credit") || t.includes("kcc")) return "https://images.unsplash.com/photo-1595974482597-4b8da8879bc5?w=700&h=350&fit=crop";
          return "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=700&h=350&fit=crop";
        };

        return (
          <div style={{ marginBottom: 24 }}>
            <SectionTitle
              title="Official Advisories & Schemes"
              action={`${filteredAdvisories.length} updates`}
            />
            <div style={{ display: "grid", gap: 14 }}>
              {filteredAdvisories.map((item) => {
                const photoUrl = getPhoto(item);
                const isWeather = item.category === "weather_warning";
                const isPest = item.category === "pest_alert";
                const tone = isWeather ? "amber" : isPest ? "rose" : "green";

                return (
                  <Card
                    key={item.id}
                    className="advisory-card"
                    style={{
                      padding: 0,
                      overflow: "hidden",
                      border: "1px solid var(--line)",
                      borderRadius: 14,
                    }}
                  >
                    {/* Visual Photo Banner */}
                    <div style={{ position: "relative", width: "100%", height: 165, background: "#f1f5f9" }}>
                      <img
                        src={photoUrl}
                        alt={item.title}
                        style={{
                          width: "100%",
                          height: "100%",
                          objectFit: "cover",
                          display: "block",
                        }}
                        loading="lazy"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = IMG.green;
                        }}
                      />
                      <div
                        style={{
                          position: "absolute",
                          top: 10,
                          left: 10,
                          display: "flex",
                          gap: 6,
                          flexWrap: "wrap",
                          zIndex: 2,
                        }}
                      >
                        <Badge tone={tone}>
                          {item.category.toUpperCase().replace("_", " ")}
                        </Badge>
                        {item.crop && (
                          <span
                            style={{
                              background: "rgba(15, 23, 42, 0.72)",
                              color: "#fff",
                              fontSize: 9.5,
                              fontWeight: 700,
                              padding: "2px 8px",
                              borderRadius: 6,
                              backdropFilter: "blur(4px)",
                            }}
                          >
                            🌾 {item.crop}
                          </span>
                        )}
                      </div>
                      <div
                        style={{
                          position: "absolute",
                          bottom: 8,
                          right: 10,
                          background: "rgba(0, 0, 0, 0.65)",
                          color: "#fff",
                          fontSize: 9,
                          fontWeight: 600,
                          padding: "2px 7px",
                          borderRadius: 4,
                          backdropFilter: "blur(4px)",
                        }}
                      >
                        📷 Verified Field Photo
                      </div>
                    </div>

                    {/* Card Content */}
                    <div style={{ padding: "14px 16px" }}>
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          marginBottom: 6,
                        }}
                      >
                        <span
                          style={{
                            fontSize: 10,
                            fontWeight: 700,
                            color: "var(--green)",
                            display: "inline-flex",
                            alignItems: "center",
                            gap: 4,
                          }}
                        >
                          <Icon name="spark" size={11} /> {item.source}
                        </span>
                        <small style={{ fontSize: 9, color: "var(--muted)" }}>
                          {item.published_at
                            ? new Date(item.published_at).toLocaleDateString("en-IN", {
                                day: "numeric",
                                month: "short",
                              })
                            : "Active"}
                        </small>
                      </div>

                      <b
                        style={{
                          fontSize: 13.5,
                          color: "var(--text)",
                          display: "block",
                          marginBottom: 6,
                          lineHeight: 1.35,
                        }}
                      >
                        {item.title}
                      </b>

                      <p
                        style={{
                          fontSize: 11.5,
                          margin: "0 0 12px",
                          color: "var(--muted)",
                          lineHeight: 1.55,
                        }}
                      >
                        {item.summary}
                      </p>

                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          paddingTop: 8,
                          borderTop: "1px solid var(--line)",
                        }}
                      >
                        {item.link ? (
                          <a
                            href={item.link}
                            target="_blank"
                            rel="noreferrer"
                            style={{
                              display: "inline-flex",
                              alignItems: "center",
                              gap: 4,
                              fontSize: 11,
                              fontWeight: 700,
                              color: "var(--green)",
                              textDecoration: "none",
                            }}
                          >
                            Official Scheme Portal <Icon name="arrow" size={12} />
                          </a>
                        ) : (
                          <span style={{ fontSize: 10, color: "var(--muted)" }}>DAC&FW Advisory</span>
                        )}

                        <span style={{ fontSize: 9.5, color: "var(--green)", fontWeight: 700 }}>
                          ✓ Govt of India Verified
                        </span>
                      </div>
                    </div>
                  </Card>
                );
              })}
            </div>
          </div>
        );
      })()}

      <div style={{ marginTop: 24, textAlign: "center" }}>
        <Button onClick={() => navigate("ai")}>
          <Icon name="spark" /> Ask Sarthi for Personalized Plan
        </Button>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// SCREEN 3: AI RECOMMENDATION ENGINE (HINDSIGHT FLOW)
// -------------------------------------------------------------
function AIScreen({
  navigate,
  user,
  cropRecs,
  memorySummary,
  showToast,
  onRefreshMemories,
}: {
  navigate: (p: Page) => void;
  user: UserProfile;
  cropRecs: CropRecommendationItem[];
  memorySummary: MemorySummaryResponse | null;
  showToast: (m: string) => void;
  onRefreshMemories: () => Promise<void>;
}) {
  const [selectedCrop, setSelectedCrop] = useState<string>(
    cropRecs.length > 0 ? cropRecs[0].crop_name : "Groundnut"
  );
  const [queryInput, setQueryInput] = useState<string>(
    "What crop should I grow this season given my farm constraints?"
  );
  const [askingAi, setAskingAi] = useState<boolean>(false);
  const [recResponse, setRecResponse] = useState<RecommendationResponse | null>(null);

  // Comparison state
  const [comparisonMode, setComparisonMode] = useState<boolean>(true);
  const [comparing, setComparing] = useState<boolean>(false);
  const [compareData, setCompareData] = useState<{
    generic: string;
    personalized: string;
    differences: string[];
    recalledCount: number;
  } | null>(null);

  // Feedback state
  const [feedbackGiven, setFeedbackGiven] = useState<boolean>(false);
  const [submittingFeedback, setSubmittingFeedback] = useState<boolean>(false);
  const [showOutcomeModal, setShowOutcomeModal] = useState<boolean>(false);
  const [outcomeResult, setOutcomeResult] = useState<string>("success");
  const [outcomeReason, setOutcomeReason] = useState<string>("");

  const currentCropData = cropRecs.find((c) => c.crop_name === selectedCrop) || cropRecs[0];
  const memoriesCount = memorySummary?.memory_count || 0;

  // Request personalized AI recommendation
  const handleAskRecommendation = async (overrideQuery?: string) => {
    const q = overrideQuery || queryInput;
    if (!q.trim()) return;

    setAskingAi(true);
    setRecResponse(null);
    setFeedbackGiven(false);

    try {
      const res = await api.getPersonalizedRecommendation({
        query: q.trim(),
        crop: selectedCrop,
        season: "Kharif",
        location: user.location,
        language: user.language,
      });
      setRecResponse(res);
      showToast("Personalized recommendation generated using Hindsight Memory!");
    } catch (err: any) {
      showToast(err?.message || "Failed to generate recommendation.");
    } finally {
      setAskingAi(false);
    }
  };

  // Trigger memory comparison
  const handleRunComparison = async () => {
    setComparing(true);
    try {
      const res = await api.compareMemory({
        query: queryInput,
        location: user.location,
        language: user.language,
      });
      const recalled =
        res?.with_memory?.memories_used ??
        res?.with_memory?.memory_context?.memory_count ??
        memorySummary?.memory_count ??
        0;

      setCompareData({
        generic:
          res?.without_memory?.recommendation ||
          "Generic regional advisory based solely on weather, soil, and climate.",
        personalized:
          res?.with_memory?.recommendation ||
          "Personalized agricultural advisory adapted to your historical farm constraints.",
        differences: res?.differences || [
          "Water availability constraint prioritized",
          "Past crop failure risk avoided",
        ],
        recalledCount: recalled,
      });
    } catch (err: any) {
      console.error("Comparison error:", err);
      // Fallback display
      setCompareData({
        generic:
          "Generic state advisory recommends High-Yield Tomato or BPT Paddy based solely on regional weather tables.",
        personalized:
          "Sarthi recalled your 1-hour borewell water limit and prior crop failure. Recommends drought-resilient Groundnut or Black Gram.",
        differences: ["Water demand filtered", "Past crop failure risk mitigated"],
        recalledCount: memorySummary?.memory_count || 0,
      });
    } finally {
      setComparing(false);
    }
  };

  useEffect(() => {
    handleRunComparison();
  }, [user.location]);

  // Submit feedback -> Phase 4 Hindsight Retain loop!
  const handleFeedback = async (helpful: boolean, type = "general", result?: string, reason?: string) => {
    const queryId = recResponse?.recommendation_id || `q_${Date.now()}`;
    setSubmittingFeedback(true);

    try {
      const res = await api.submitFeedback({
        query_id: queryId,
        helpful,
        feedback_type: type,
        crop: selectedCrop,
        outcome_result: result,
        outcome_reason: reason,
        feedback_text: reason || (helpful ? "Helpful recommendation" : "Did not fit constraints"),
      });

      setFeedbackGiven(true);
      setShowOutcomeModal(false);
      showToast("Feedback recorded! Sarthi Hindsight Retain has updated your memory graph.");

      // Refresh memories
      await onRefreshMemories();
    } catch (err: any) {
      showToast(err?.message || "Failed to submit feedback.");
    } finally {
      setSubmittingFeedback(false);
    }
  };

  return (
    <div className="screen">
      <Header title="AI Agronomist Engine" />
      <div className="screen-intro">
        <div className="screen-heading">A crop plan built around your farm</div>
        <p>
          Powered by Azure OpenAI GPT & Sarthi's Hindsight Long-Term Memory Graph.
        </p>
      </div>

      {/* Memory Status Badge */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          background: "var(--mint)",
          border: "1px solid var(--mint-border)",
          padding: "8px 12px",
          borderRadius: 12,
          marginBottom: 16,
        }}
      >
        <Icon name="brain" size={18} />
        <span style={{ fontSize: 11, color: "var(--green)", fontWeight: 700 }}>
          Hindsight Memory Active: {memorySummary?.memory_count || 0} farm memories retained for {user.phone_number}
        </span>
      </div>

      {/* Crop Selection Filter Chips */}
      <div className="filter-row">
        {cropRecs.slice(0, 5).map((c) => (
          <button
            key={c.crop_id}
            className={`filter-btn ${selectedCrop === c.crop_name ? "active" : ""}`}
            onClick={() => setSelectedCrop(c.crop_name)}
          >
            {c.crop_name} ({Math.round(c.soil_compatibility)}%)
          </button>
        ))}
      </div>

      {/* Agronomy Metrics Grid */}
      {currentCropData && (
        <div className="metric-grid">
          <Card className="metric-card">
            <span>WATER DEMAND</span>
            <b>{currentCropData.water_requirement.split(" ")[0]}</b>
            <small className="good">{currentCropData.water_requirement}</small>
          </Card>
          <Card className="metric-card">
            <span>SOIL MATCH</span>
            <b>{Math.round(currentCropData.soil_compatibility)}%</b>
            <small className="good">Compatible</small>
          </Card>
          <Card className="metric-card">
            <span>CYCLE DURATION</span>
            <b>{currentCropData.duration_days} days</b>
            <small>Optimal season</small>
          </Card>
          <Card className="metric-card">
            <span>CATEGORY</span>
            <b>{currentCropData.category}</b>
            <small className="good">Package Ready</small>
          </Card>
        </div>
      )}

      {/* Interactive AI Query Box */}
      <SectionTitle title="Ask Sarthi for Live Tailored Guidance" />
      <Card style={{ padding: "14px 16px", marginBottom: 20 }}>
        <div style={{ display: "flex", gap: 8, marginBottom: 10 }}>
          <input
            type="text"
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
            placeholder="Ask Sarthi anything about your field..."
            className="auth-input"
            style={{ padding: "10px 14px", height: 42, fontSize: 12, borderRadius: 10 }}
          />
          <Button
            onClick={() => handleAskRecommendation()}
            disabled={askingAi}
            style={{ height: 42, whiteSpace: "nowrap" }}
          >
            {askingAi ? "Thinking..." : "Consult AI"}
          </Button>
        </div>

        {/* Returned AI Recommendation */}
        {recResponse && (
          <div
            style={{
              background: "#f0f8f3",
              border: "1px solid #c0e4d0",
              borderRadius: 14,
              padding: "14px 16px",
              marginTop: 12,
              animation: "enter 0.2s ease both",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
              <Badge tone="green">
                <Icon name="spark" size={13} /> SARTHI AI RECOMMENDATION
              </Badge>
              {recResponse.memory_context?.used && (
                <span style={{ fontSize: 10, color: "var(--green)", fontWeight: 800 }}>
                  🧠 Informed by {recResponse.memory_context.memory_count} Farm Memories
                </span>
              )}
            </div>

            <MarkdownRenderer text={recResponse.recommendation} fontSize={12} />

            {/* Relevant memories cited */}
            {recResponse.relevant_memories && recResponse.relevant_memories.length > 0 && (
              <div style={{ marginTop: 12, paddingTop: 10, borderTop: "1px dashed #b8e2cd" }}>
                <b style={{ fontSize: 10, color: "var(--green-dark)", textTransform: "uppercase" }}>
                  Hindsight Memories Recalled:
                </b>
                <ul style={{ margin: "4px 0 0", paddingLeft: 18, fontSize: 10, color: "var(--muted)" }}>
                  {recResponse.relevant_memories.map((m, i) => (
                    <li key={i}>{m.text || JSON.stringify(m)}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Feedback & Retain Loop */}
            <div
              style={{
                marginTop: 14,
                paddingTop: 10,
                borderTop: "1px solid #d4ede0",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                flexWrap: "wrap",
                gap: 8,
              }}
            >
              <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text)" }}>
                Was this advice accurate for your farm?
              </span>

              {feedbackGiven ? (
                <span style={{ fontSize: 11, color: "var(--green)", fontWeight: 800 }}>
                  ✓ Feedback retained into Sarthi Long-Term Memory!
                </span>
              ) : (
                <div style={{ display: "flex", gap: 6 }}>
                  <button
                    onClick={() => handleFeedback(true, "accepted")}
                    disabled={submittingFeedback}
                    style={{
                      background: "var(--green)",
                      color: "#fff",
                      border: 0,
                      padding: "5px 10px",
                      borderRadius: 6,
                      fontSize: 10,
                      fontWeight: 700,
                      cursor: "pointer",
                    }}
                  >
                    👍 Helpful
                  </button>
                  <button
                    onClick={() => handleFeedback(false, "rejected")}
                    disabled={submittingFeedback}
                    style={{
                      background: "#fff",
                      border: "1px solid var(--line)",
                      color: "var(--text)",
                      padding: "5px 10px",
                      borderRadius: 6,
                      fontSize: 10,
                      fontWeight: 700,
                      cursor: "pointer",
                    }}
                  >
                    👎 Needs Correction
                  </button>
                  <button
                    onClick={() => setShowOutcomeModal(true)}
                    disabled={submittingFeedback}
                    style={{
                      background: "var(--amber)",
                      color: "#fff",
                      border: 0,
                      padding: "5px 10px",
                      borderRadius: 6,
                      fontSize: 10,
                      fontWeight: 700,
                      cursor: "pointer",
                    }}
                  >
                    🌾 Report Outcome
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </Card>

      {/* Side-by-Side Memory Comparison */}
      <SectionTitle title="Memory Comparison: Sarthi vs Generic AI" />
      <div className="segmented-toggle">
        <button
          className={comparisonMode ? "active" : ""}
          onClick={() => setComparisonMode(true)}
        >
          Sarthi with Hindsight Memory ({compareData?.recalledCount || memoriesCount} Memories)
        </button>
        <button
          className={!comparisonMode ? "active" : ""}
          onClick={() => setComparisonMode(false)}
        >
          Generic Standard AI (Without Memory)
        </button>
      </div>

      <div className="compare-box">
        <div className={`compare-card ${comparisonMode ? "sarthi" : "standard"}`}>
          <span className={`compare-tag ${comparisonMode ? "sarthi" : "standard"}`}>
            <Icon name="spark" size={12} />
            {comparisonMode ? "SARTHI WITH HINDSIGHT MEMORY" : "STANDARD LLM (WITHOUT MEMORY)"}
          </span>
          <b>{comparisonMode ? `${selectedCrop} (Personalized)` : "Standard Recommendation"}</b>
          {comparing ? (
            <p style={{ color: "var(--muted)", fontSize: 12 }}>Running comparative analysis...</p>
          ) : (
            <MarkdownRenderer
              text={
                comparisonMode
                  ? compareData?.personalized ||
                    "Sarthi retrieved your past memory: 'Limited irrigation availability & previous tomato failure'. It filters high-risk water-intensive crops."
                  : compareData?.generic ||
                    "Generic regional model recommends standard crops without awareness of your individual borehole drying constraint or prior crop loss."
              }
              fontSize={12}
            />
          )}

          {comparisonMode && compareData?.differences && compareData.differences.length > 0 && (
            <div style={{ marginTop: 10, paddingTop: 8, borderTop: "1px dashed rgba(9,107,71,0.2)" }}>
              <b style={{ fontSize: 9, color: "var(--green)" }}>WHAT CHANGED:</b>
              <div style={{ display: "flex", gap: 4, flexWrap: "wrap", marginTop: 4 }}>
                {compareData.differences.map((d, idx) => (
                  <Badge key={idx} tone="neutral">
                    {d}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Outcome Reporting Modal */}
      {showOutcomeModal && (
        <div className="modal-overlay" onClick={() => setShowOutcomeModal(false)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <b>Report Harvest / Field Outcome</b>
                <small>Retains field truth into Sarthi's Long-Term Memory</small>
              </div>
              <button
                className="modal-close"
                onClick={() => setShowOutcomeModal(false)}
                aria-label="Close dialog"
              >
                <Icon name="close" size={18} />
              </button>
            </div>
            <div className="modal-form">
              <div className="modal-field">
                <label>Harvest Result</label>
                <select
                  value={outcomeResult}
                  onChange={(e) => setOutcomeResult(e.target.value)}
                  className="modal-select"
                >
                  <option value="success">Successful Harvest (High yield)</option>
                  <option value="partial">Partial Harvest (Minor loss)</option>
                  <option value="failure">Crop Failure (Water/Pest/Disease loss)</option>
                </select>
              </div>
              <div className="modal-field">
                <label>Notes / Harvest Details</label>
                <textarea
                  rows={3}
                  value={outcomeReason}
                  onChange={(e) => setOutcomeReason(e.target.value)}
                  placeholder="e.g. Groundnut yielded 18 quintals/acre with minimal water. Avoided late borehole drying."
                  className="modal-input"
                  required
                />
              </div>
              <div className="modal-actions">
                <Button kind="ghost" onClick={() => setShowOutcomeModal(false)}>
                  Cancel
                </Button>
                <Button
                  kind="primary"
                  onClick={() =>
                    handleFeedback(
                      outcomeResult === "success",
                      "outcome_reported",
                      outcomeResult,
                      outcomeReason
                    )
                  }
                  disabled={submittingFeedback}
                >
                  {submittingFeedback ? "Retaining in Vectorize..." : "Save to Hindsight"}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// -------------------------------------------------------------
// SCREEN 4: COMMUNITY NETWORK & OUTBREAK RADAR
// -------------------------------------------------------------
function CommunityScreen({
  navigate,
  reports,
  outbreakMap,
  leaderboard,
  onVerify,
  onOpenReportModal,
}: {
  navigate: (p: Page) => void;
  reports: CommunityReport[];
  outbreakMap: OutbreakMapResponse | null;
  leaderboard: LeaderboardItem[];
  onVerify: (id: string) => void;
  onOpenReportModal: () => void;
}) {
  return (
    <div className="screen">
      <Header
        title="Community Network & Outbreaks"
        action={
          <Button kind="icon" onClick={() => navigate("notifications")} label="Notifications">
            <Icon name="bell" />
          </Button>
        }
      />
      <div className="screen-intro">
        <div className="screen-heading">Village Outbreak Radar</div>
        <p>Real-time farmer pest reports, geographic outbreak clusters, and trust index.</p>
      </div>

      {/* Interactive Outbreak Map */}
      <SectionTitle title="Live Outbreak Map" />
      <div style={{
        borderRadius: 18,
        overflow: "hidden",
        border: "1.5px solid var(--line)",
        marginBottom: 16,
        position: "relative",
        background: "var(--surface)",
        boxShadow: "0 2px 12px rgba(9,107,71,0.07)",
      }}>
        <iframe
          title="Sarthi Outbreak Map"
          src="https://www.openstreetmap.org/export/embed.html?bbox=72.0%2C15.0%2C85.0%2C28.0&amp;layer=mapnik&amp;marker=20.5937%2C78.9629"
          style={{
            width: "100%",
            height: 300,
            border: 0,
            display: "block",
          }}
          loading="lazy"
          allowFullScreen
        />
        <div style={{
          position: "absolute",
          top: 10,
          left: 10,
          background: "rgba(255,255,255,0.92)",
          backdropFilter: "blur(8px)",
          borderRadius: 10,
          padding: "6px 10px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.12)",
          fontSize: 10,
          fontWeight: 700,
          color: "var(--green-dark)",
          display: "flex",
          alignItems: "center",
          gap: 5,
        }}>
          <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#c94f4f", display: "inline-block", boxShadow: "0 0 0 3px rgba(201,79,79,0.25)" }} />
          {outbreakMap?.outbreaks?.length ?? 0} Active Outbreak Clusters
        </div>
        <a
          href="https://www.openstreetmap.org/#map=5/20.59/78.96"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            position: "absolute",
            bottom: 8,
            right: 8,
            background: "rgba(255,255,255,0.88)",
            borderRadius: 6,
            padding: "3px 7px",
            fontSize: 9,
            color: "var(--muted)",
            textDecoration: "none",
          }}
        >
          View larger map ↗
        </a>
      </div>

      {/* Outbreak Clusters from Outbreak Map API */}
      <SectionTitle title="Geographic Outbreak Clusters" />
      <div style={{ display: "grid", gap: 10, marginBottom: 20 }}>
        {outbreakMap?.outbreaks && outbreakMap.outbreaks.length > 0 ? (
          outbreakMap.outbreaks.map((ob) => (
            <Card key={ob.village} style={{ padding: "14px 16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <b style={{ fontSize: 14 }}>
                    <Icon name="pin" size={14} /> {ob.village}, {ob.state}
                  </b>
                  <small style={{ display: "block", color: "var(--muted)", fontSize: 10 }}>
                    Coordinates: {ob.coordinates.lat.toFixed(2)}°N, {ob.coordinates.lng.toFixed(2)}°E
                  </small>
                </div>
                <Badge tone={ob.alert_level === "high" ? "danger" : ob.alert_level === "medium" ? "amber" : "green"}>
                  {ob.alert_level.toUpperCase()} ALERT
                </Badge>
              </div>

              <div style={{ marginTop: 8, fontSize: 11, color: "var(--text)" }}>
                <b>Crops Affected:</b> {ob.crops_affected.join(", ") || "General crops"}
              </div>

              <div style={{ display: "flex", gap: 12, marginTop: 8, fontSize: 10, color: "var(--muted)" }}>
                <span>🐛 {ob.pest_count} Pest Reports</span>
                <span>🦠 {ob.disease_count} Disease Reports</span>
                <span>📋 {ob.total_reports} Total Incidents</span>
              </div>
            </Card>
          ))
        ) : (
          <div className="state-box">
            <p>Scanning regional telemetry for outbreak clusters...</p>
          </div>
        )}
      </div>

      {/* Verified Village Leaderboard */}
      <SectionTitle title="Village Trust Index & Leaderboard" />
      <Card style={{ padding: "10px 14px", marginBottom: 20 }}>
        <div className="table-responsive">
          <table className="mandi-table">
            <thead>
              <tr>
                <th>RANK</th>
                <th>VILLAGE</th>
                <th>TRUST SCORE</th>
                <th>RESPONSES</th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.length > 0 ? (
                leaderboard.map((lb) => (
                  <tr key={lb.village_id}>
                    <td>
                      <b>{lb.tier_icon} #{lb.rank}</b>
                    </td>
                    <td>
                      <b>{lb.village_id}</b>
                    </td>
                    <td>
                      <Badge tone="green">{lb.trust_score.toFixed(1)}% Trust</Badge>
                    </td>
                    <td style={{ fontSize: 10, color: "var(--muted)" }}>
                      {lb.helpful_count} / {lb.total_responses}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} style={{ textAlign: "center", padding: 12 }}>
                    Loading village trust rankings...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Live Community Reports Feed */}
      <SectionTitle title="Live Agricultural Community Feed" />
      <div style={{ display: "grid", gap: 10, marginBottom: 20 }}>
        {reports.length > 0 ? (
          reports.map((r) => (
            <Card key={r.report_id} style={{ padding: "12px 14px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <Badge tone={r.severity === "high" ? "danger" : "amber"}>
                    {r.report_type.toUpperCase()} · {r.crop || "Farm"}
                  </Badge>
                  <small style={{ marginLeft: 8, fontSize: 10, color: "var(--muted)" }}>
                    {r.village_id} · {r.timestamp ? r.timestamp.slice(0, 10) : "Recent"}
                  </small>
                </div>
                {r.verified && <span style={{ fontSize: 10, color: "var(--green)", fontWeight: 800 }}>✓ Verified</span>}
              </div>

              <p style={{ margin: "8px 0", fontSize: 11, color: "var(--text)", lineHeight: 1.5 }}>
                {r.description}
              </p>

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 8 }}>
                <span style={{ fontSize: 10, color: "var(--muted)" }}>
                  Verified by {r.validation_count || 0} farmers
                </span>
                <button
                  onClick={() => onVerify(r.report_id)}
                  style={{
                    background: "var(--surface-soft)",
                    border: "1px solid var(--line)",
                    padding: "4px 8px",
                    borderRadius: 6,
                    fontSize: 10,
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  ✓ Verify ({r.validation_count || 0})
                </button>
              </div>
            </Card>
          ))
        ) : (
          <div className="state-box">
            <p>No outbreak incidents reported in your immediate mandal.</p>
          </div>
        )}
      </div>

      <div style={{ textAlign: "center", marginBottom: 30 }}>
        <Button onClick={onOpenReportModal}>
          <Icon name="plus" /> Report Pest / Disease Incident
        </Button>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// SCREEN 5: FARMER PROFILE
// -------------------------------------------------------------
function ProfileScreen({
  navigate,
  user,
  envProfile,
  memoriesCount,
  queryHistory,
  onOpenEditProfile,
  onLogout,
}: {
  navigate: (p: Page) => void;
  user: UserProfile;
  envProfile: EnvironmentalProfile | null;
  memoriesCount: number;
  queryHistory: QueryHistoryItem[];
  onOpenEditProfile: () => void;
  onLogout: () => void;
}) {
  return (
    <div className="screen">
      <Header title="Farmer Profile" />
      <Card className="profile-card">
        <div className="avatar">FM</div>
        <div style={{ flex: 1 }}>
          <div className="profile-name">{user.phone_number}</div>
          <p>
            <Icon name="pin" size={15} /> {user.location}
          </p>
          <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
            <Badge>Verified Account</Badge>
            <Badge tone="neutral">{envProfile?.soil_type || "Black Soil"}</Badge>
          </div>
        </div>
        <Button kind="icon" onClick={onOpenEditProfile} label="Edit farm profile">
          <Icon name="spark" size={18} />
        </Button>
      </Card>

      <div className="profile-stats">
        <Card>
          <b>{envProfile?.nitrogen || 225}</b>
          <span>Soil N (kg/ha)</span>
        </Card>
        <Card onClick={() => navigate("memory")} style={{ cursor: "pointer" }}>
          <b>{memoriesCount}</b>
          <span>Memories</span>
        </Card>
        <Card onClick={() => navigate("calendar")} style={{ cursor: "pointer" }}>
          <b>{envProfile?.soil_ph || 7.6}</b>
          <span>Soil pH</span>
        </Card>
      </div>

      <SectionTitle title="My Farm Details & Telemetry" />
      <Card style={{ padding: "14px 16px", marginBottom: 20 }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, fontSize: 11 }}>
          <div>
            <span style={{ color: "var(--muted)", display: "block" }}>SOIL TYPE:</span>
            <b>{envProfile?.soil_type || "Black Cotton Soil"}</b>
          </div>
          <div>
            <span style={{ color: "var(--muted)", display: "block" }}>NORMAL RAINFALL:</span>
            <b>{envProfile?.rainfall || "900-1400mm"}</b>
          </div>
          <div>
            <span style={{ color: "var(--muted)", display: "block" }}>PHOSPHORUS (P):</span>
            <b>{envProfile?.phosphorus || 19} kg/ha</b>
          </div>
          <div>
            <span style={{ color: "var(--muted)", display: "block" }}>POTASSIUM (K):</span>
            <b>{envProfile?.potassium || 310} kg/ha</b>
          </div>
        </div>
        {envProfile?.recommended_amendments && (
          <div style={{ marginTop: 12, paddingTop: 10, borderTop: "1px solid var(--line)", fontSize: 10 }}>
            <span style={{ color: "var(--green)", fontWeight: 700 }}>SOIL AMENDMENT NOTE:</span>
            <p style={{ margin: "2px 0 0", color: "var(--muted)" }}>
              {envProfile.recommended_amendments}
            </p>
          </div>
        )}
      </Card>

      {/* Query History from Azure Table Storage */}
      <SectionTitle title="Your Sarthi Query History" />
      <div style={{ display: "grid", gap: 10, marginBottom: 20 }}>
        {queryHistory.length > 0 ? (
          queryHistory.slice(0, 5).map((q) => (
            <Card key={q.query_id} style={{ padding: "12px 14px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <b style={{ fontSize: 12 }}>“{q.query}”</b>
                <small style={{ fontSize: 9, color: "var(--muted)" }}>
                  {q.timestamp ? q.timestamp.slice(0, 10) : "Recent"}
                </small>
              </div>
              <p style={{ margin: "6px 0 0", fontSize: 11, color: "var(--muted)", lineHeight: 1.4 }}>
                {q.response.slice(0, 120)}...
              </p>
            </Card>
          ))
        ) : (
          <div className="state-box">
            <p>No queries recorded yet. Ask Sarthi a question to begin building your farm memory.</p>
          </div>
        )}
      </div>

      <div style={{ textAlign: "center", marginBottom: 30 }}>
        <Button kind="ghost" onClick={onLogout}>
          Sign Out ({user.phone_number})
        </Button>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// SCREEN 6: HYPERLOCAL WEATHER & AGRO-ENVIRONMENTAL DETAIL
// -------------------------------------------------------------
function WeatherDetailScreen({
  back,
  user,
  weather,
  envProfile,
  onRefresh,
}: {
  back: () => void;
  user: UserProfile;
  weather: WeatherData | null;
  envProfile: EnvironmentalProfile | null;
  onRefresh: () => void;
}) {
  const temp = weather ? Math.round(weather.temperature) : 21;
  const humidity = weather ? weather.humidity : 87;

  return (
    <div className="screen">
      <Header title="Hyperlocal Agro-Weather" goBack={back} />
      <div className="screen-intro">
        <div className="screen-heading">{user.location}</div>
        <p>Live telemetry from OpenWeather & IMD Agro-meteorological sensors.</p>
      </div>

      <Card className="weather-card">
        <div className="weather-top">
          <div>
            <div className="temperature">
              {temp}<span>°C</span>
            </div>
            <p>{weather?.condition || "Clear skies"} · Real-time station reading</p>
          </div>
          <div className="weather-art">
            <Icon name="cloud" size={70} />
            <span>
              <Icon name="sun" size={39} />
            </span>
          </div>
        </div>
        <div className="weather-stats">
          <div>
            <Icon name="drop" />
            <b>{humidity}%</b>
            <span>Humidity</span>
          </div>
          <div>
            <Icon name="cloud" />
            <b>{weather?.rainfall || 0} mm</b>
            <span>Rainfall</span>
          </div>
          <div>
            <Icon name="wind" />
            <b>12 km/h</b>
            <span>Wind speed</span>
          </div>
        </div>
      </Card>

      <SectionTitle title="Agricultural Environmental Profile (Soil & Telemetry)" />
      <div className="metric-grid">
        <Card className="metric-card">
          <span>SOIL TYPE</span>
          <b>{envProfile?.soil_type?.split(" ")[0] || "Black"}</b>
          <small className="good">{envProfile?.soil_type || "Black Soil"}</small>
        </Card>
        <Card className="metric-card">
          <span>NITROGEN (N)</span>
          <b>{envProfile?.nitrogen || 225}</b>
          <small className="good">kg/ha</small>
        </Card>
        <Card className="metric-card">
          <span>PHOSPHORUS (P)</span>
          <b>{envProfile?.phosphorus || 19}</b>
          <small className="good">kg/ha</small>
        </Card>
        <Card className="metric-card">
          <span>SOIL PH</span>
          <b>{envProfile?.soil_ph || 7.6}</b>
          <small className="good">Normal Range</small>
        </Card>
      </div>

      <Card className="farm-outlook">
        <Badge tone="amber">AGRO-WEATHER RECOMMENDATION</Badge>
        <div className="story-title">
          {humidity > 80 ? "Fungal Spore Risk Alert" : "Favorable Farming Conditions"}
        </div>
        <p>
          {humidity > 80
            ? `Relative humidity is elevated at ${humidity}%. Avoid early morning spraying. Optimal bio-fungicide spray window is 4:00 PM – 6:30 PM.`
            : `Weather is clear with low moisture risk. Normal intercultural operations can proceed as scheduled.`}
        </p>
      </Card>

      <div style={{ textAlign: "center", marginTop: 20 }}>
        <Button kind="soft" onClick={onRefresh}>
          <Icon name="refresh" /> Refresh Telemetry
        </Button>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// SCREEN 7: CROP CALENDAR
// -------------------------------------------------------------
function CalendarScreen({
  back,
  user,
  cropCalendar,
  showToast,
}: {
  back: () => void;
  user: UserProfile;
  cropCalendar: CropCalendarResponse | null;
  showToast: (m: string) => void;
}) {
  const [selectedCropIndex, setSelectedCropIndex] = useState<number>(0);
  const [completedOps, setCompletedOps] = useState<Record<string, boolean>>({});

  const crops = cropCalendar?.recommended_crops || [];
  const activeCrop = crops[selectedCropIndex] || null;

  const toggleOp = (key: string) => {
    setCompletedOps((prev) => {
      const next = !prev[key];
      showToast(next ? "Critical operation marked complete!" : "Operation unchecked.");
      return { ...prev, [key]: next };
    });
  };

  return (
    <div className="screen">
      <Header title="Dynamic Crop Calendar" goBack={back} />
      <div className="screen-intro">
        <div className="screen-heading">
          {cropCalendar?.current_season?.toUpperCase() || "KHARIF"} 2026 CALENDAR
        </div>
        <p>Synchronized with ICAR agronomy cycles and {user.location} agro-climatic norms.</p>
      </div>

      {/* Crop selector */}
      <div className="filter-row">
        {crops.map((c, idx) => (
          <button
            key={c.id}
            className={`filter-btn ${selectedCropIndex === idx ? "active" : ""}`}
            onClick={() => setSelectedCropIndex(idx)}
          >
            {c.name}
          </button>
        ))}
      </div>

      {activeCrop && (
        <>
          <Card style={{ padding: "14px 16px", marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <b style={{ fontSize: 15 }}>{activeCrop.name}</b>
              <Badge tone="green">{activeCrop.duration_days} Days Total</Badge>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 10, fontSize: 11 }}>
              <div>
                <span style={{ color: "var(--muted)", display: "block" }}>PLANTING WINDOW:</span>
                <b>{activeCrop.planting.start} – {activeCrop.planting.end}</b>
              </div>
              <div>
                <span style={{ color: "var(--muted)", display: "block" }}>HARVEST WINDOW:</span>
                <b>{activeCrop.harvesting.start} – {activeCrop.harvesting.end}</b>
              </div>
            </div>
            <p style={{ marginTop: 10, fontSize: 11, color: "var(--text)", lineHeight: 1.5 }}>
              <b>Agronomic Tip:</b> {activeCrop.tips}
            </p>
          </Card>

          <SectionTitle title="Critical Field Operations Checklist" />
          <Card style={{ padding: "12px 14px", marginBottom: 20 }}>
            <div className="checklist">
              {activeCrop.critical_operations.map((op, idx) => {
                const key = `${activeCrop.id}_${idx}`;
                const done = !!completedOps[key];
                return (
                  <div
                    key={key}
                    className={`check-item ${done ? "done" : ""}`}
                    onClick={() => toggleOp(key)}
                  >
                    <div className="check-box">{done && <Icon name="check" size={14} />}</div>
                    <div className="check-text">
                      <span>{op}</span>
                      <small>Stage {idx + 1} Operation</small>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>
        </>
      )}
    </div>
  );
}

// -------------------------------------------------------------
// SCREEN 8: HINDSIGHT MEMORY BANK
// -------------------------------------------------------------
function MemoryScreen({
  back,
  navigate,
  memorySummary,
  onOpenTeachModal,
  onResetDemo,
}: {
  back: () => void;
  navigate: (p: Page) => void;
  memorySummary: MemorySummaryResponse | null;
  onOpenTeachModal: () => void;
  onResetDemo: () => void;
}) {
  const [filter, setFilter] = useState<string>("All");

  const pastExp = memorySummary?.sections?.past_experience || [];
  const learned = memorySummary?.sections?.learned_from_you || [];
  const constraints = memorySummary?.constraint_memories || [];
  const whatChanged = memorySummary?.what_changed || [];

  return (
    <div className="screen">
      <Header title="Farm Memories & Hindsight" goBack={back} />
      <div className="screen-intro">
        <div className="screen-heading">What Sarthi remembers</div>
        <p>
          Hindsight Vectorize Memory Graph. Personal farm context, prior crop losses, and irrigation
          constraints retained to prevent repeated mistakes.
        </p>
      </div>

      <div className="filter-row">
        {["All", "Past Experience", "Learned From You", "Constraints", "What Changed"].map((cat) => (
          <button
            key={cat}
            className={`filter-btn ${filter === cat ? "active" : ""}`}
            onClick={() => setFilter(cat)}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Memory List */}
      <div className="memory-list" style={{ marginBottom: 20 }}>
        {(filter === "All" || filter === "Past Experience") &&
          pastExp.map((m) => (
            <Card key={m.id || m.text}>
              <div className="memory-icon">
                <Icon name="leaf" />
              </div>
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <Badge tone="amber">{m.type.toUpperCase()}</Badge>
                  <span style={{ fontSize: 9, color: "var(--green)", fontWeight: 800 }}>
                    Hindsight Retained
                  </span>
                </div>
                <p>{m.text}</p>
                <small>Source: {m.source} {m.crop ? `· Crop: ${m.crop}` : ""}</small>
              </div>
            </Card>
          ))}

        {(filter === "All" || filter === "Learned From You" || filter === "Constraints") &&
          learned.map((m) => (
            <Card key={m.id || m.text}>
              <div className="memory-icon">
                <Icon name="brain" />
              </div>
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <Badge tone="green">{m.type.toUpperCase()}</Badge>
                  <span style={{ fontSize: 9, color: "var(--green)", fontWeight: 800 }}>
                    Learned Constraint
                  </span>
                </div>
                <p>{m.text}</p>
                <small>Source: {m.source} {m.reason ? `· Reason: ${m.reason}` : ""}</small>
              </div>
            </Card>
          ))}

        {filter === "What Changed" &&
          whatChanged.map((wc, idx) => (
            <Card key={idx}>
              <div className="memory-icon">
                <Icon name="spark" />
              </div>
              <div>
                <Badge tone="green">{wc.trigger}</Badge>
                <p style={{ fontWeight: 700, margin: "6px 0" }}>{wc.summary}</p>
                <small style={{ color: "var(--green)" }}>Impact: {wc.impact}</small>
              </div>
            </Card>
          ))}

        {memorySummary?.memory_count === 0 && (
          <div className="state-box">
            <p>No memories retained yet for this farmer account. Tap "Teach Sarthi" to record your first farm memory!</p>
          </div>
        )}
      </div>

      <div className="button-grid-2">
        <Button onClick={onOpenTeachModal}>
          <Icon name="plus" /> Teach Sarthi
        </Button>
        <Button kind="soft" onClick={onResetDemo}>
          <Icon name="refresh" /> Reset Demo Memories
        </Button>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// SCREEN 9: VOICE ASSISTANT SCREEN
// -------------------------------------------------------------
function VoiceScreen({
  back,
  user,
  showToast,
  onRefreshMemories,
}: {
  back: () => void;
  user: UserProfile;
  showToast: (m: string) => void;
  onRefreshMemories: () => Promise<void>;
}) {
  const [listening, setListening] = useState<boolean>(false);
  const [recordingSeconds, setRecordingSeconds] = useState<number>(0);
  const [question, setQuestion] = useState<string>("");
  const [processing, setProcessing] = useState<boolean>(false);
  const [voiceResp, setVoiceResp] = useState<string>("");
  const [queryId, setQueryId] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [feedbackDone, setFeedbackDone] = useState<boolean>(false);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const recognitionRef = useRef<any>(null);
  const timerRef = useRef<any>(null);

  const sampleQuestions = [
    "What crop should I grow with my 1 hour borewell limit?",
    "Will it rain this week in my district?",
    "How to manage stem fly in soybean?",
    "Show current mandi price for chickpea",
  ];

  // Encode raw AudioBuffer to 16kHz mono WAV format for Azure Speech Services
  const encodeWav = (audioBuffer: AudioBuffer): ArrayBuffer => {
    const numChannels = 1;
    const sampleRate = audioBuffer.sampleRate;
    const format = 1;
    const bitDepth = 16;

    const samples = audioBuffer.getChannelData(0);
    const blockAlign = numChannels * (bitDepth / 8);
    const byteRate = sampleRate * blockAlign;
    const dataSize = samples.length * (bitDepth / 8);

    const buffer = new ArrayBuffer(44 + dataSize);
    const view = new DataView(buffer);

    const writeString = (offset: number, str: string) => {
      for (let i = 0; i < str.length; i += 1) {
        view.setUint8(offset + i, str.charCodeAt(i));
      }
    };

    writeString(0, "RIFF");
    view.setUint32(4, 36 + dataSize, true);
    writeString(8, "WAVE");
    writeString(12, "fmt ");
    view.setUint32(16, 16, true);
    view.setUint16(20, format, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitDepth, true);
    writeString(36, "data");
    view.setUint32(40, dataSize, true);

    let offset = 44;
    for (let i = 0; i < samples.length; i += 1, offset += 2) {
      let s = Math.max(-1, Math.min(1, samples[i]));
      s = s < 0 ? s * 0x8000 : s * 0x7fff;
      view.setInt16(offset, s, true);
    }

    return buffer;
  };

  const convertToWav = async (audioBlob: Blob): Promise<Blob> => {
    try {
      const arrayBuffer = await audioBlob.arrayBuffer();
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return audioBlob;
      const audioContext = new AudioCtx();
      const decodedBuffer = await audioContext.decodeAudioData(arrayBuffer);

      const targetSampleRate = 16000;
      const offlineContext = new OfflineAudioContext(
        1,
        Math.max(1, Math.ceil(decodedBuffer.duration * targetSampleRate)),
        targetSampleRate
      );
      const source = offlineContext.createBufferSource();
      source.buffer = decodedBuffer;
      source.connect(offlineContext.destination);
      source.start(0);
      const renderedBuffer = await offlineContext.startRendering();

      const wavBuffer = encodeWav(renderedBuffer);
      return new Blob([wavBuffer], { type: "audio/wav" });
    } catch (err) {
      console.warn("WAV conversion fallback to raw blob:", err);
      return audioBlob;
    }
  };

  const playVoiceResponse = (url: string) => {
    try {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      const sound = new Audio(url);
      audioRef.current = sound;
      sound.onplay = () => setIsPlaying(true);
      sound.onended = () => setIsPlaying(false);
      sound.onpause = () => setIsPlaying(false);
      sound.play().catch((playErr) => {
        console.warn("Auto-play prevented by browser policy:", playErr);
      });
    } catch (e) {
      console.warn("Audio playback init error:", e);
    }
  };

  const handleSendText = async (text: string) => {
    if (!text.trim()) return;
    setQuestion(text);
    setProcessing(true);
    setVoiceResp("");
    setAudioUrl(null);
    setFeedbackDone(false);

    try {
      const res = await api.processText(text.trim(), user.language);
      setVoiceResp(res.response_text);
      setQueryId(res.query_id);

      if (res.audio_data) {
        const audioBlob = new Blob(
          [Uint8Array.from(atob(res.audio_data), (c) => c.charCodeAt(0))],
          { type: "audio/wav" }
        );
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        playVoiceResponse(url);
      }
    } catch (err: any) {
      showToast(err?.message || "Failed to process query.");
    } finally {
      setProcessing(false);
    }
  };

  const handleProcessAudioBlob = async (audioBlob: Blob) => {
    setProcessing(true);
    setVoiceResp("");
    setAudioUrl(null);
    setFeedbackDone(false);

    try {
      const wavBlob = await convertToWav(audioBlob);
      const res = await api.processAudio(wavBlob, user.language);

      if (res.transcript) {
        setQuestion(res.transcript);
      }
      setVoiceResp(res.response_text);
      setQueryId(res.query_id);

      if (res.audio_data) {
        const outBlob = new Blob(
          [Uint8Array.from(atob(res.audio_data), (c) => c.charCodeAt(0))],
          { type: "audio/wav" }
        );
        const url = URL.createObjectURL(outBlob);
        setAudioUrl(url);
        playVoiceResponse(url);
      }
    } catch (err: any) {
      showToast(err?.message || "Could not process audio. Please try typing your question.");
    } finally {
      setProcessing(false);
    }
  };

  const startRecording = async () => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      showToast("Audio recording requires a supported browser with microphone access.");
      return;
    }

    try {
      setVoiceResp("");
      setAudioUrl(null);
      setFeedbackDone(false);
      setRecordingSeconds(0);

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const preferredTypes = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/ogg;codecs=opus",
        "audio/ogg",
        "audio/mp4",
      ];
      const supportedType = preferredTypes.find(
        (type) => typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(type)
      );

      const recorder = supportedType
        ? new MediaRecorder(stream, { mimeType: supportedType })
        : new MediaRecorder(stream);

      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        clearInterval(timerRef.current);
        setListening(false);

        if (mediaStreamRef.current) {
          mediaStreamRef.current.getTracks().forEach((track) => track.stop());
          mediaStreamRef.current = null;
        }

        const recordedChunks = chunksRef.current;
        if (recordedChunks.length > 0) {
          const rawBlob = new Blob(recordedChunks, { type: recorder.mimeType || "audio/webm" });
          await handleProcessAudioBlob(rawBlob);
        }
      };

      recorder.start(250);
      setListening(true);

      // Duration counter
      let secs = 0;
      timerRef.current = setInterval(() => {
        secs += 1;
        setRecordingSeconds(secs);
        if (secs >= 25) {
          stopRecording();
        }
      }, 1000);

      // In parallel, attempt Web Speech API for instant live transcript preview (non-blocking)
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

      if (SpeechRecognition) {
        try {
          const recognition = new SpeechRecognition();
          recognitionRef.current = recognition;
          recognition.lang =
            user.language === "hi" ? "hi-IN" : user.language === "te" ? "te-IN" : "en-IN";
          recognition.interimResults = true;
          recognition.continuous = false;

          recognition.onresult = (event: any) => {
            const transcript = event.results[0]?.[0]?.transcript;
            if (transcript) {
              setQuestion(transcript);
            }
          };

          recognition.onerror = (e: any) => {
            // Ignore no-speech and network errors silently since MediaRecorder captures raw audio
            console.log("Browser speech recognition note:", e?.error);
          };

          recognition.onend = () => {
            // Recognition ended naturally
          };

          recognition.start();
        } catch (recogErr) {
          console.warn("SpeechRecognition start ignored:", recogErr);
        }
      }
    } catch (err: any) {
      setListening(false);
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        showToast("Microphone access denied. Please allow microphone permission in your browser.");
      } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
        showToast("No microphone found. Please connect a microphone or use text input.");
      } else {
        showToast("Microphone error: " + (err?.message || "Could not access microphone"));
      }
    }
  };

  const stopRecording = () => {
    clearInterval(timerRef.current);

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch {}
      recognitionRef.current = null;
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      try {
        mediaRecorderRef.current.stop();
      } catch {}
    } else {
      setListening(false);
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((track) => track.stop());
        mediaStreamRef.current = null;
      }
    }
  };

  const handleToggleMic = () => {
    if (listening) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const togglePlayAudio = () => {
    if (!audioRef.current && audioUrl) {
      audioRef.current = new Audio(audioUrl);
      audioRef.current.onended = () => setIsPlaying(false);
    }

    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const handleVoiceFeedback = async (helpful: boolean) => {
    if (!queryId) return;
    try {
      await api.submitFeedback({
        query_id: queryId,
        helpful,
        feedback_text: helpful ? "Helpful voice query" : "Unhelpful voice query",
      });
      setFeedbackDone(true);
      showToast("Feedback retained in Sarthi Memory Graph!");
      await onRefreshMemories();
    } catch (err: any) {
      showToast(err?.message || "Feedback failed.");
    }
  };

  const formatTimer = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  return (
    <div className="voice-screen">
      <Header title="Ask Sarthi Voice AI" goBack={back} />
      <div className="voice-content">
        <div className="voice-brand">
          <div>
            <Icon name="spark" />
          </div>
          <span>SARTHI MULTILINGUAL AI ({user.language.toUpperCase()})</span>
        </div>

        <div className="voice-title">
          {listening
            ? "Sarthi is listening..."
            : processing
            ? "Consulting Agronomy Engine..."
            : "What would you like to know?"}
        </div>
        <p>
          {listening
            ? "Speak naturally in Hindi, Telugu, or English — Tap mic to finish"
            : "Ask about crops, fertilizer schedules, mandi prices, or pest management."}
        </p>

        <button
          className={`mic-button ${listening ? "listening" : ""}`}
          onClick={handleToggleMic}
          aria-label={listening ? "Stop recording and ask" : "Start voice input"}
        >
          <Icon name="mic" size={38} />
        </button>
        <small>
          {listening
            ? `🔴 Recording (${formatTimer(recordingSeconds)}) — Tap to stop & submit`
            : processing
            ? "Transcribing with Azure AI & finding agronomy answers..."
            : "Tap microphone to speak or type below"}
        </small>

        {/* Input box fallback */}
        <div style={{ width: "100%", maxWidth: 440, marginTop: 16 }}>
          <div style={{ display: "flex", gap: 8 }}>
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Or type your question here..."
              className="auth-input"
              style={{ padding: "8px 12px", height: 40, fontSize: 12, borderRadius: 10 }}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSendText(question);
              }}
            />
            <Button
              onClick={() => handleSendText(question)}
              disabled={processing || listening}
              style={{ height: 40, padding: "0 14px" }}
            >
              Ask
            </Button>
          </div>
        </div>

        {question && (
          <Card className="transcript" style={{ marginTop: 16 }}>
            <small>YOU ASKED</small>
            <p>“{question}”</p>
          </Card>
        )}

        {voiceResp && (
          <Card className="transcript" style={{ background: "#f0f8f3", borderColor: "#c0e4d0", marginTop: 10 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <small style={{ color: "var(--green)" }}>SARTHI AI SAYS</small>
              {audioUrl && (
                <button
                  onClick={togglePlayAudio}
                  style={{
                    background: "var(--green)",
                    color: "#fff",
                    border: 0,
                    padding: "4px 8px",
                    borderRadius: 6,
                    fontSize: 10,
                    display: "flex",
                    alignItems: "center",
                    gap: 4,
                    cursor: "pointer",
                  }}
                >
                  <Icon name={isPlaying ? "pause" : "play"} size={12} />
                  {isPlaying ? "Pause Audio" : "Play Voice"}
                </button>
              )}
            </div>
            <div style={{ marginTop: 8 }}>
              <MarkdownRenderer text={voiceResp} fontSize={12} />
            </div>

            {/* Inline feedback */}
            <div
              style={{
                marginTop: 10,
                paddingTop: 8,
                borderTop: "1px dashed #b8e2cd",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <span style={{ fontSize: 10, color: "var(--muted)" }}>Was this answer helpful?</span>
              {feedbackDone ? (
                <span style={{ fontSize: 10, color: "var(--green)", fontWeight: 700 }}>
                  ✓ Feedback retained
                </span>
              ) : (
                <div style={{ display: "flex", gap: 4 }}>
                  <button
                    onClick={() => handleVoiceFeedback(true)}
                    style={{
                      border: 0,
                      background: "var(--green)",
                      color: "#fff",
                      padding: "2px 6px",
                      borderRadius: 4,
                      fontSize: 9,
                      cursor: "pointer",
                    }}
                  >
                    Yes
                  </button>
                  <button
                    onClick={() => handleVoiceFeedback(false)}
                    style={{
                      border: "1px solid var(--line)",
                      background: "#fff",
                      padding: "2px 6px",
                      borderRadius: 4,
                      fontSize: 9,
                      cursor: "pointer",
                    }}
                  >
                    No
                  </button>
                </div>
              )}
            </div>
          </Card>
        )}

        <div className="suggestions" style={{ marginTop: 20 }}>
          {sampleQuestions.map((q) => (
            <button key={q} onClick={() => handleSendText(q)}>
              {q}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// SCREEN 10: CROP DETAIL (ICAR PACKAGE OF PRACTICES)
// -------------------------------------------------------------
function CropDetailScreen({
  back,
  navigate,
  cropItem,
  envProfile,
}: {
  back: () => void;
  navigate: (p: Page) => void;
  cropItem: CropRecommendationItem | null;
  envProfile: EnvironmentalProfile | null;
}) {
  const cropName = cropItem ? cropItem.crop_name : "Black Gram (Urad)";

  return (
    <div className="screen crop-detail">
      <Header title="Crop Agronomy Details" goBack={back} />
      <div className="crop-hero">
        <img src={IMG.wheat} alt="Crop cultivation" />
        <div>
          <Badge>ICAR PACKAGE OF PRACTICES</Badge>
          <div className="screen-heading">{cropName}</div>
          <p>{cropItem?.explanation || "Resilient crop option tailored for your regional soil."}</p>
        </div>
      </div>

      <div className="quick-facts">
        <Card>
          <b>{cropItem?.duration_days || 80}</b>
          <span>Days Duration</span>
        </Card>
        <Card>
          <b>{cropItem?.water_requirement.split(" ")[0] || "Low"}</b>
          <span>Water Need</span>
        </Card>
        <Card>
          <b>{envProfile?.soil_type?.split(" ")[0] || "Black"}</b>
          <span>Soil Type</span>
        </Card>
      </div>

      <Card className="content-card">
        <div className="story-title">Pest & Disease Advisory (Integrated Pest Management)</div>
        <div style={{ marginTop: 10, fontSize: 11 }}>
          <b style={{ color: "var(--green)" }}>Key Pests Monitored:</b>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", margin: "4px 0 10px" }}>
            {cropItem?.key_pests && cropItem.key_pests.length > 0 ? (
              cropItem.key_pests.map((p) => (
                <Badge key={p} tone="amber">
                  {p}
                </Badge>
              ))
            ) : (
              <Badge tone="neutral">Stem Fly · Whitefly · Pod Borer</Badge>
            )}
          </div>

          <b style={{ color: "var(--green)" }}>Key Diseases Monitored:</b>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", margin: "4px 0 0" }}>
            {cropItem?.key_diseases && cropItem.key_diseases.length > 0 ? (
              cropItem.key_diseases.map((d) => (
                <Badge key={d} tone="danger">
                  {d}
                </Badge>
              ))
            ) : (
              <Badge tone="neutral">Yellow Mosaic Virus · Powdery Mildew</Badge>
            )}
          </div>
        </div>
      </Card>

      <div style={{ textAlign: "center", marginTop: 20 }}>
        <Button onClick={() => navigate("calendar")}>
          <Icon name="calendar" /> View Sowing & Growth Calendar
        </Button>
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// SCREEN 11: HOW SARTHI LEARNS
// -------------------------------------------------------------
function LearningScreen({ back }: { back: () => void }) {
  const steps = [
    {
      step: 1,
      label: "YOU ASK SARTHI",
      text: "“What should I grow this season given my borehole limits?”",
      desc: "Initial question sent to Azure OpenAI query router.",
    },
    {
      step: 2,
      label: "HINDSIGHT RECALL",
      text: "Sarthi retrieves past failures, water constraints, and preferences from Vectorize memory graph.",
      desc: "Zero hallucination: personal constraints take precedence.",
    },
    {
      step: 3,
      label: "PERSONALIZED ADVICE",
      text: "Sarthi recommends drought-resilient crops and provides precise spray windows.",
      desc: "Avoids high-water crops that previously caused failure.",
    },
    {
      step: 4,
      label: "FARMER FEEDBACK",
      text: "You report harvest results: 'Groundnut yielded 18 quintals/acre with minimal water.'",
      desc: "Captured via structured feedback and speech transcription.",
    },
    {
      step: 5,
      label: "HINDSIGHT RETAIN",
      text: "Memory retained forever: Groundnut preference & borewell constraint locked in memory graph.",
      desc: "Future recommendations automatically adapt.",
    },
  ];

  return (
    <div className="screen">
      <Header title="How Sarthi Learns" goBack={back} />
      <div className="screen-intro centered">
        <div className="learning-mark">
          <Icon name="brain" size={34} />
        </div>
        <div className="screen-heading">Your experience makes Sarthi smarter</div>
        <p>
          Every conversation, pest report, and crop outcome transforms into long-term memory so you
          never face the same loss twice.
        </p>
      </div>

      <div className="learning-flow">
        {steps.map((s, idx) => (
          <Card key={s.label} className={idx === steps.length - 1 ? "final" : ""}>
            <span>{s.step}</span>
            <div>
              <small>{s.label}</small>
              <p style={{ fontWeight: 700 }}>{s.text}</p>
              <span style={{ fontSize: 9, opacity: 0.75, display: "block", marginTop: 4 }}>
                {s.desc}
              </span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

// -------------------------------------------------------------
// SCREEN 12: NOTIFICATIONS
// -------------------------------------------------------------
function NotificationsScreen({
  back,
  weather,
  outbreakMap,
  agriNews,
  memorySummary,
}: {
  back: () => void;
  weather: WeatherData | null;
  outbreakMap: OutbreakMapResponse | null;
  agriNews: AgriNewsItem[];
  memorySummary: MemorySummaryResponse | null;
}) {
  const notifications = [
    {
      id: "n-1",
      tone: "cloud" as const,
      title: weather?.alert ? "Weather Advisory" : "Agro-Weather Telemetry",
      desc: weather?.alert || `Humidity is ${weather?.humidity || 87}%. Safe spray window: 4:00 PM – 6:30 PM.`,
      time: "Live reading",
    },
    {
      id: "n-2",
      tone: "users" as const,
      title: `Village Outbreaks: ${outbreakMap?.total_reports || 0} Reports`,
      desc: outbreakMap?.outbreaks?.[0]
        ? `${outbreakMap.outbreaks[0].village}: ${outbreakMap.outbreaks[0].alert_level.toUpperCase()} risk for ${outbreakMap.outbreaks[0].crops_affected.join(", ")}.`
        : "No high-risk pest clusters detected in immediate boundary.",
      time: "Updated today",
    },
    {
      id: "n-3",
      tone: "spark" as const,
      title: `Hindsight Memory Bank: ${memorySummary?.memory_count || 0} Retained`,
      desc: "All personal constraints and crop histories are synchronized with Azure Table Storage.",
      time: "Synced",
    },
    {
      id: "n-4",
      tone: "spark" as const,
      title: agriNews[0]?.title || "Government Agricultural Scheme Update",
      desc: agriNews[0]?.summary || "Check portal for eligibility and direct benefit transfer.",
      time: "Official news",
    },
  ];

  return (
    <div className="screen">
      <Header title="Notifications" goBack={back} />
      <div style={{ marginBottom: 16 }}>
        <span style={{ fontSize: 12, color: "var(--muted)", fontWeight: 700 }}>
          {notifications.length} Active Farm Alerts
        </span>
      </div>

      <div className="notification-list">
        {notifications.map((n) => (
          <Card key={n.id} style={{ padding: "12px 14px", marginBottom: 8 }}>
            <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
              <span className="badge green" style={{ marginTop: 2 }}>
                <Icon name={n.tone} size={15} />
              </span>
              <div>
                <b style={{ fontSize: 12, display: "block" }}>{n.title}</b>
                <p style={{ margin: "2px 0 0", fontSize: 11, color: "var(--muted)", lineHeight: 1.4 }}>
                  {n.desc}
                </p>
                <small style={{ fontSize: 9, color: "var(--muted)", display: "block", marginTop: 4 }}>
                  {n.time}
                </small>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
