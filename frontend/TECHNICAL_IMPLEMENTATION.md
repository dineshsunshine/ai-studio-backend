# 🔧 Technical Implementation - Mobile PWA

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│        Sharable Link Page (PWA)                 │
├─────────────────────────────────────────────────┤
│  HTML (shared_link.html)                        │
│  ├─ PWA Meta Tags                               │
│  ├─ Responsive CSS                              │
│  └─ JavaScript (API + Navigation)               │
├─────────────────────────────────────────────────┤
│  Manifest (manifest.json)                       │
│  └─ PWA Configuration                           │
├─────────────────────────────────────────────────┤
│  Service Worker (sw.js)                         │
│  └─ Offline Support & Caching                   │
└─────────────────────────────────────────────────┘
        │
        ├─ Desktop Browser (Chromium, Firefox)
        ├─ iOS Safari (PWA Install)
        └─ Android Chrome (PWA Install)
```

---

## 1. HTML Implementation (shared_link.html)

### PWA Meta Tags
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="AI Studio">
<meta name="theme-color" content="#0a0a0a">
<link rel="manifest" href="manifest.json">
```

**What each does:**
- `viewport-fit=cover`: Notch support (safe area insets)
- `user-scalable=no`: Prevents accidental zoom
- `apple-mobile-web-app-capable`: iOS installable
- `black-translucent`: Status bar styling
- `theme-color`: Browser/Android theme

### Service Worker Registration
```javascript
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js').catch(() => {
        // Silently fail if not available
    });
}
```

---

## 2. CSS Implementation

### Mobile-First Approach

```css
/* Base: Mobile first (smallest screen) */
body {
    font-size: 16px;
    height: 100dvh;  /* Dynamic viewport height */
}

/* Tablet (768px+) */
@media (min-width: 768px) {
    body {
        font-size: 17px;
    }
}

/* Desktop (1024px+) */
@media (min-width: 1024px) {
    body {
        font-size: 18px;
    }
}
```

### Safe Area Support
```css
.cover-page {
    padding-top: max(60px, env(safe-area-inset-top));
    padding-bottom: max(60px, env(safe-area-inset-bottom));
}

.look-page {
    padding-top: max(40px, env(safe-area-inset-top));
    padding-bottom: max(80px, calc(env(safe-area-inset-bottom) + 80px));
}
```

**How it works:**
- `env(safe-area-inset-*)`: Gets notch/home indicator size from OS
- `max()`: Uses larger of: fixed padding or safe area inset
- Automatically adapts to: iPhone 12+ notches, Dynamic Island, Android notches

### Touch-Friendly Interactions

```css
/* Desktop: Hover effects */
@media (hover: hover) {
    .product-item:hover {
        background: rgba(255, 255, 255, 0.05);
    }
}

/* Mobile/Touch: Active/tap effects */
@media (hover: none) and (pointer: coarse) {
    .product-item:active {
        background: rgba(255, 255, 255, 0.08);
        transform: scale(0.98);
    }
}
```

**Why this works:**
- Detects device capability (hover vs. touch)
- Desktop gets smooth hover states
- Mobile gets responsive tap feedback
- No false positives or ignored interactions

### Responsive Typography

```css
.cover-title {
    font-size: clamp(36px, 8vw, 96px);
}
```

**Breakdown:**
- Minimum: 36px (readable on small phones)
- Preferred: 8vw (scales with viewport)
- Maximum: 96px (doesn't grow too large)
- No media query needed!

### Dynamic Viewport Height

```css
body {
    height: 100vh;     /* Old way - buggy on mobile */
    height: 100dvh;    /* New way - accounts for address bar */
}
```

**Mobile browser height changes:**
- Address bar shown: ~56-80px taken
- Address bar hidden: Full available height
- `100dvh` adjusts automatically

---

## 3. JavaScript Implementation

### Navigation System

#### Desktop Navigation
```javascript
// Arrow keys navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown') {
        scrollToNextPage();
    } else if (e.key === 'ArrowUp') {
        scrollToPrevPage();
    }
});
```

#### Mobile Swipe Navigation
```javascript
let touchStartY = 0;
let isScrolling = false;

document.addEventListener('touchstart', (e) => {
    touchStartY = e.changedTouches[0].screenY;
    isScrolling = false;
}, { passive: true });

document.addEventListener('touchmove', () => {
    isScrolling = true;
}, { passive: true });

document.addEventListener('touchend', (e) => {
    if (isScrolling) return;  // User scrolling, not swiping
    const touchEndY = e.changedTouches[0].screenY;
    const diff = touchStartY - touchEndY;
    
    if (diff > 80) {  // Swipe up threshold
        scrollToNextPage();
    }
}, { passive: true });
```

**Why `isScrolling` flag:**
- Without it: Both scroll AND swipe events fire
- Prevents accidental navigation during scrolling
- Better UX: One gesture = one action

### Image Lazy Loading

```javascript
const page = createLookPage(look, lookNumber, totalLooks);
page.innerHTML = `
    <img src="${look.generatedImageUrl}"
         loading="lazy"
         alt="Look image">
`;
```

**Benefits:**
- Images load only when scrolling near them
- Reduces initial page load time
- Saves data on slow connections
- Browser native (no JS library needed)

### API Detection

```javascript
const isAIStudio = window.location.pathname.includes('/AIStudio/');
const API_BASE = window.location.origin + 
    (isAIStudio ? '/AIStudio/api/v1' : '/api/v1');

const response = await fetch(`${API_BASE}/links/shared/${linkId}`, {
    headers: {
        'ngrok-skip-browser-warning': '1'
    }
});
```

**Why this works:**
- Dev: `http://localhost:8000/l/{id}` → `/api/v1`
- Dev ngrok: `https://domain.ngrok.dev/AIStudio/l/{id}` → `/AIStudio/api/v1`
- Prod: `https://prod.com/l/{id}` → `/api/v1`

---

## 4. Service Worker Implementation (sw.js)

### Installation (Caching)
```javascript
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS).catch(() => {
                // Silently fail if not available
            });
        })
    );
    self.skipWaiting();
});
```

**What happens:**
1. User visits page
2. Service Worker installs
3. Caches static assets (HTML, manifest, etc.)
4. Ready to serve offline

### Fetch Interception (Caching Strategy)
```javascript
event.respondWith(
    caches.match(event.request)
        .then((response) => {
            if (response) return response;  // Cache hit
            
            return fetch(event.request)
                .then((response) => {
                    if (!response || response.status !== 200) {
                        return response;  // Don't cache errors
                    }
                    
                    const responseToCache = response.clone();
                    
                    // Cache API calls & static assets
                    if (event.request.url.includes('/api/')) {
                        caches.open(CACHE_NAME)
                            .then((cache) => {
                                cache.put(event.request, responseToCache);
                            });
                    }
                    
                    return response;
                })
                .catch(() => {
                    // Offline: Return stale cache
                    return caches.match(event.request);
                });
        })
);
```

**Caching Strategy:**
1. **Cache First**: Check cache first
2. **Network Second**: If not cached, fetch fresh
3. **Offline Fallback**: If offline, use cached version
4. **Smart Caching**: Only cache successful responses

### Cache Cleanup (Activation)
```javascript
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});
```

**Why cleanup:**
- Old versions cached with old name
- Accumulates over time
- Wastes storage space
- Cleanup on each SW activation

---

## 5. PWA Manifest (manifest.json)

```json
{
  "name": "AI Studio - Luxury Lookbook",
  "short_name": "Lookbook",
  "display": "standalone",
  "orientation": "portrait-primary",
  "theme_color": "#0a0a0a",
  "background_color": "#0a0a0a",
  "icons": [
    {
      "src": "data:image/svg+xml,<svg>...</svg>",
      "sizes": "192x192",
      "type": "image/svg+xml",
      "purpose": "any"
    }
  ]
}
```

**Key fields:**
- `display: standalone`: Hides browser UI
- `orientation: portrait-primary`: Prefer portrait
- `theme_color`: Android chrome color
- `icons`: App icon (used on home screen)
- `purpose: any maskable`: Adaptive icons for Android

---

## 6. Responsive Breakpoints

```css
/* Desktop: 1280px+ */
@media (min-width: 1280px) {
    .look-content {
        grid-template-columns: 1fr 1fr;
        gap: 80px;
    }
    .page-nav {
        display: flex;  /* Show side dots */
    }
    .mobile-nav-dots {
        display: none;  /* Hide bottom dots */
    }
}

/* Tablet: 768px - 1279px */
@media (max-width: 1279px) and (min-width: 768px) {
    .look-content {
        grid-template-columns: 1fr;
        gap: 30px;
    }
    /* Desktop navigation stays */
}

/* Mobile: 480px - 767px */
@media (max-width: 767px) {
    .page-nav {
        display: none;  /* Hide side dots */
    }
    .mobile-nav-dots.show {
        display: flex;  /* Show bottom dots */
    }
}

/* Small Mobile: < 480px */
@media (max-width: 480px) {
    .look-page {
        padding: 24px 14px;
        padding-bottom: max(90px, calc(env(safe-area-inset-bottom) + 90px));
    }
}
```

---

## 7. Performance Optimizations

### Image Lazy Loading
```html
<img src="..." loading="lazy" alt="...">
```
- Browser native (no library needed)
- Only loads when visible
- Reduces initial load time

### Service Worker Caching
```
First load:  Network (download files)
Revisit:     Cache (instant)
Offline:     Cache (works!)
```

### CSS Minification
- No unused styles
- Efficient selectors
- Single stylesheet
- ~50KB total (with HTML)

### JavaScript Optimization
- No external dependencies
- Vanilla JS only
- Event delegation
- Efficient DOM manipulation

---

## 8. Browser Compatibility

| Feature | Support |
|---------|---------|
| PWA (iOS 13+) | ✅ Full |
| PWA (Android) | ✅ Full |
| Service Worker | ✅ 95%+ browsers |
| Safe Area (iOS) | ✅ iOS 11+ |
| Dynamic Viewport | ✅ Modern browsers |
| Viewport-fit | ✅ iOS 11.2+ |

---

## 9. Testing & Debugging

### DevTools Navigation
```
DevTools → Application → Service Workers
  → Check if active
  → View network activity
  → Test offline mode

DevTools → Application → Cache Storage
  → View cached files
  → Clear cache

DevTools → Console
  → Service Worker messages
  → Errors/warnings
```

### Lighthouse Audit
```bash
# Run in DevTools
Lighthouse → Generate Report

Target scores:
  Performance: 90+
  Accessibility: 95+
  Best Practices: 100
  PWA: 100
  SEO: 100
```

---

## 10. Deployment Considerations

### Prerequisites
- ✅ HTTPS (required for Service Worker)
- ✅ Valid manifest.json
- ✅ Service Worker on same origin
- ✅ Icons accessible

### Production Checklist
- [ ] HTTPS enabled
- [ ] Manifest linked in HTML
- [ ] Service Worker file accessible
- [ ] Icons served correctly
- [ ] Cache headers appropriate
- [ ] Error pages handled
- [ ] Offline fallback page ready

---

## Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| HTML | PWA meta tags | Enable installability |
| CSS | Safe areas, media queries | Responsive design |
| JS | SW registration, nav | Offline + interactivity |
| SW | Cache API | Offline support |
| Manifest | JSON | PWA metadata |

**Result:** A web app that feels native, works offline, and performs great! 🚀
