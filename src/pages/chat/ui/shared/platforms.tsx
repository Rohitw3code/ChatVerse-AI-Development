const GmailIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="gmailGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#ea4335" />
        <stop offset="25%" stopColor="#fbbc04" />
        <stop offset="50%" stopColor="#34a853" />
        <stop offset="75%" stopColor="#4285f4" />
        <stop offset="100%" stopColor="#ea4335" />
      </linearGradient>
    </defs>
    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" 
          fill="white" stroke="url(#gmailGradient)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M22 6l-10 7L2 6" fill="none" stroke="#ea4335" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const InstagramIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none">
    <defs>
      <radialGradient id="instagramGradient" cx="30%" cy="120%" r="120%">
        <stop offset="0%" stopColor="#fdf497" />
        <stop offset="5%" stopColor="#fdf497" />
        <stop offset="45%" stopColor="#fd5949" />
        <stop offset="60%" stopColor="#d6249f" />
        <stop offset="90%" stopColor="#285AEB" />
      </radialGradient>
    </defs>
    <rect x="2" y="2" width="20" height="20" rx="5" ry="5" 
          fill="url(#instagramGradient)" stroke="none"/>
    <circle cx="12" cy="12" r="4" fill="none" stroke="white" strokeWidth="2.5"/>
    <circle cx="17.5" cy="6.5" r="1.2" fill="white"/>
  </svg>
);

const LinkedInIcon = () => (
  <svg width="20" height="20" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" fill="none">
    <rect x="1" y="1" width="14" height="14" rx="2" fill="#0A66C2"/>
    <path fill="white" d="M12.225 12.225h-1.778V9.44c0-.664-.012-1.519-.925-1.519-.926 0-1.068.724-1.068 1.47v2.834H6.676V6.498h1.707v.783h.024c.348-.594.996-.95 1.684-.925 1.802 0 2.135 1.185 2.135 2.728l-.001 3.14zM4.67 5.715a1.037 1.037 0 01-1.032-1.031c0-.566.466-1.032 1.032-1.032.566 0 1.031.466 1.032 1.032 0 .566-.466 1.032-1.032 1.032zm.889 6.51h-1.78V6.498h1.78v5.727z" />
  </svg>
);

const SuccessIcon = () => (
  <svg className="w-4 h-4 text-green-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 6L9 17L4 12" />
  </svg>
);

const YouTubeIcon = () => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 32 32"
    width="24"
    height="24"
    fill="#FF0000"
  >
    <title>YouTube</title>
    <path d="M12.932 20.459v-8.917l7.839 4.459zM30.368 8.735c-0.354-1.301-1.354-2.307-2.625-2.663l-0.027-0.006c-3.193-0.406-6.886-0.638-10.634-0.638-0.381 0-0.761 0.002-1.14 0.007l0.058-0.001c-0.322-0.004-0.701-0.007-1.082-0.007-3.748 0-7.443 0.232-11.070 0.681l0.434-0.044c-1.297 0.363-2.297 1.368-2.644 2.643l-0.006 0.026c-0.4 2.109-0.628 4.536-0.628 7.016 0 0.088 0 0.176 0.001 0.263l-0-0.014c-0 0.074-0.001 0.162-0.001 0.25 0 2.48 0.229 4.906 0.666 7.259l-0.038-0.244c0.354 1.301 1.354 2.307 2.625 2.663l0.027 0.006c3.193 0.406 6.886 0.638 10.634 0.638 0.38 0 0.76-0.002 1.14-0.007l-0.058 0.001c0.322 0.004 0.702 0.007 1.082 0.007 3.749 0 7.443-0.232 11.070-0.681l-0.434 0.044c1.298-0.362 2.298-1.368 2.646-2.643l0.006-0.026c0.399-2.109 0.627-4.536 0.627-7.015 0-0.088-0-0.176-0.001-0.263l0 0.013c0-0.074 0.001-0.162 0.001-0.25 0-2.48-0.229-4.906-0.666-7.259l0.038 0.244z" />
  </svg>
);

const TavilyIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="tavilyGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#3B82F6" />
        <stop offset="50%" stopColor="#1D4ED8" />
        <stop offset="100%" stopColor="#1E40AF" />
      </linearGradient>
    </defs>
    <circle cx="12" cy="12" r="10" fill="url(#tavilyGradient)" />
    <path d="M8 12l2 2 4-4" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
    <circle cx="12" cy="12" r="3" fill="none" stroke="white" strokeWidth="1.5" strokeOpacity="0.6" />
    <path d="M21 21l-4.35-4.35" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const DocsIcon = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" xmlns="http://www.w3.org/2000/svg" fill="none">
    <rect x="4" y="2" width="14" height="20" rx="2" fill="#1E3A8A" />
    <path d="M14 2v6h6" fill="#3B82F6" />
    <rect x="7" y="10" width="8" height="1.8" rx="0.9" fill="white" />
    <rect x="7" y="13" width="8" height="1.8" rx="0.9" fill="white" />
    <rect x="7" y="16" width="6" height="1.8" rx="0.9" fill="white" />
  </svg>
);

// Updated Google Sheets logo (clean, recognizable sheet grid)
const SheetsIcon = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" xmlns="http://www.w3.org/2000/svg" fill="none">
    <rect x="3" y="2" width="18" height="20" rx="2" fill="#0F9D58" />
    <rect x="7" y="7" width="10" height="8" rx="1" fill="#ffffff" opacity="0.95" />
    <path d="M7 10.5h10M12 7v8" stroke="#0F9D58" strokeWidth="1.5" />
  </svg>
);

export {SuccessIcon, GmailIcon, LinkedInIcon, InstagramIcon, YouTubeIcon, TavilyIcon, DocsIcon, SheetsIcon};