# Understanding the Ngrok Browser Warning

## 🎯 TL;DR

**The warning page you see is NORMAL and happens on ALL ngrok plans** (including Hobby/Pro). It's not an error!

---

## ❓ Why Am I Seeing This?

When you type an ngrok URL directly in your browser's address bar, ngrok shows a warning page **before** your request reaches your server. This is ngrok's anti-phishing protection.

### This Happens When:
- ✅ You type the URL in the browser address bar
- ✅ You open a bookmark to an ngrok URL
- ✅ You open an ngrok link in a new incognito window
- ✅ Your browser cookies are cleared

### This NEVER Happens When:
- ✅ Your frontend code makes API calls (with the header)
- ✅ Mobile apps access your API
- ✅ Postman/curl with the header
- ✅ After clicking "Visit Site" (sets a cookie)

---

## 💰 Does Upgrading to Paid Remove It?

**No, but that's not the point!**

Even with a **Hobby or Pro account**, the warning still appears for **direct browser access** (first time). This is by design.

### What You GET with Hobby Account:

| Feature | Free Plan | Hobby Plan ($8/mo) |
|---------|-----------|-------------------|
| Static Domains | 1 | 3 |
| Active Tunnels | 1 | 3 |
| Connections/min | 40 | 120 |
| Custom Domains | ❌ | ✅ |
| IP Restrictions | ❌ | ✅ |
| Support | Community | Email |

**All of these benefits ARE active!** The warning page doesn't affect them.

---

## ✅ Solutions Based on Your Use Case

### Use Case 1: Accessing Swagger UI in Browser

**Problem:** You type `https://your-domain.ngrok-free.dev/AIStudio/docs` in your browser

**Solution:** 
1. Click "Visit Site" button (just once)
2. Ngrok sets a cookie
3. Won't see the warning again this session

**Duration:** Cookie lasts for your browser session (until you close browser or clear cookies)

---

### Use Case 2: Frontend Application Accessing API

**Problem:** Your React/Vue/Angular app needs to call your API

**Solution:** Add the header to ALL API requests

```javascript
// Option 1: Set globally (recommended)
axios.defaults.headers.common['ngrok-skip-browser-warning'] = 'true';

// Option 2: Add to fetch
fetch('https://your-domain.ngrok-free.dev/AIStudio/api/v1/models/', {
    headers: {
        'ngrok-skip-browser-warning': 'true'
    }
});
```

**Result:** ✅ No warning page, ever!

---

### Use Case 3: Mobile App

**Problem:** Your iOS/Android app needs to access API

**Solution:** Add the header to your HTTP client

**React Native:**
```javascript
fetch('https://your-domain.ngrok-free.dev/AIStudio/api/v1/models/', {
    headers: {
        'ngrok-skip-browser-warning': 'true'
    }
});
```

**Flutter:**
```dart
final response = await http.get(
  Uri.parse('https://your-domain.ngrok-free.dev/AIStudio/api/v1/models/'),
  headers: {
    'ngrok-skip-browser-warning': 'true'
  },
);
```

**Swift (iOS):**
```swift
var request = URLRequest(url: url)
request.setValue("true", forHTTPHeaderField: "ngrok-skip-browser-warning")
```

**Result:** ✅ No warning page!

---

### Use Case 4: Testing with Postman/cURL

**Problem:** You want to test API calls

**Postman:**
1. Add header: `ngrok-skip-browser-warning: true`
2. Make your request

**cURL:**
```bash
curl -H "ngrok-skip-browser-warning: true" \
  https://your-domain.ngrok-free.dev/AIStudio/api/v1/models/
```

**Result:** ✅ Direct API access, no warning!

---

### Use Case 5: Sharing with Non-Technical Users

**Problem:** You want to share Swagger UI with someone who will type the URL

**Solution Options:**

**Option A: Tell them to click "Visit Site"**
- Send them the URL
- Tell them: "You'll see a security notice - just click 'Visit Site'"
- They only need to do this once per session

**Option B: Use a browser extension**
- Install [ModHeader](https://chrome.google.com/webstore/detail/modheader/idgpnmonknjnojddfkpgkljpfnnfcklj) (Chrome/Edge)
- Add header: `ngrok-skip-browser-warning: true`
- Never see the warning again

**Option C: Custom landing page**
- Create a simple HTML page that redirects
- Include JavaScript that adds the header
- Host it on your domain

---

## 🔧 Technical Explanation

### Why Does This Happen?

1. **User types URL in browser**
   ```
   Browser → ngrok edge → [WARNING PAGE SHOWN HERE]
   ```

2. **Ngrok intercepts at their edge** (before reaching your server)
   - Checks for bypass header
   - If no header → Shows warning page
   - If has header → Passes through directly

3. **Your server never sees the warning page**
   - It happens at ngrok's infrastructure
   - You have zero control over it
   - Even paid accounts can't disable it for direct browser access

### Why Can't We Bypass It for Browser URLs?

When you type a URL in the browser's address bar:
- Browser makes a **direct GET request**
- No way to add custom headers to this initial request
- Ngrok shows the warning at their edge
- After clicking "Visit Site", ngrok sets a cookie
- Subsequent requests use that cookie

### Why Does the Header Work for API Calls?

When your code makes an API call:
- You control the request
- You can add custom headers
- Ngrok sees the `ngrok-skip-browser-warning` header
- Bypasses the warning page entirely

---

## 📊 How to Verify Your Hobby Account Is Active

### Check Your Ngrok Dashboard:
Visit: https://dashboard.ngrok.com

Look for:
- ✅ Plan shows "Hobby" or "Personal"
- ✅ You see 3 domain slots (not 1)
- ✅ Limit shows 120 connections/minute

### Test Higher Limits:
```bash
# Run this 50 times quickly (would hit free plan limit)
for i in {1..50}; do
  curl -s -H "ngrok-skip-browser-warning: true" \
    https://your-domain.ngrok-free.dev/AIStudio/api/v1/models/ > /dev/null
  echo "Request $i complete"
done
```

If you're on Hobby, all 50 will succeed. Free plan would start failing around request 20-30.

---

## 🎯 Best Practices

### For Development:

1. **First time opening docs in browser:**
   - Click "Visit Site" once
   - Continue working
   
2. **Testing APIs:**
   - Always use Postman/cURL with the header
   - Or use your frontend code

3. **Sharing with team:**
   - Tell them about the "Visit Site" button
   - Or give them the ModHeader extension link

### For Production:

1. **Frontend developers:**
   - Add header to HTTP client globally (one time setup)
   - Document it in your API guide

2. **Mobile developers:**
   - Add header to all API calls
   - Test thoroughly before release

3. **Third-party integrations:**
   - Include header requirement in API docs
   - Provide code examples

---

## 🚫 What Won't Work

### ❌ Trying to disable the warning page entirely for browser URLs
- Not possible on any ngrok plan
- This is ngrok's security feature
- Would require custom domain (not ngrok subdomain)

### ❌ Using JavaScript redirects to bypass warning
- Warning shows before JavaScript executes
- Can't intercept the initial request

### ❌ Paying for Enterprise plan
- Even Enterprise shows the warning for direct browser access
- Only custom domains can avoid it (by not using ngrok's domain)

---

## ✅ What DOES Work

### ✅ Clicking "Visit Site" once per browser session
- Simple, free, works on all plans

### ✅ Adding the header to all API calls
- Perfect for production use
- Zero user friction
- Works reliably

### ✅ Using browser extensions (for development)
- ModHeader or similar
- Adds header automatically
- Great for testing

### ✅ Custom domain (Hobby+ plans)
- Use your own domain: `api.yourdomain.com`
- Points to ngrok
- No warning page (not using ngrok subdomain)

---

## 🎓 Summary

| Access Method | Warning Appears? | Solution |
|---------------|-----------------|----------|
| Browser: Type URL | ✅ Yes (first time) | Click "Visit Site" |
| Browser: With extension | ❌ No | Use ModHeader |
| Frontend code | ❌ No | Add header to requests |
| Mobile app | ❌ No | Add header to HTTP client |
| Postman/cURL | ❌ No (with header) | Add header: `-H "ngrok-skip-browser-warning: true"` |
| Custom domain | ❌ No | Use your domain instead |

---

## 💡 Key Takeaway

**The warning page is NOT an error or limitation!**

- ✅ Your Hobby account benefits ARE active
- ✅ Your API works perfectly
- ✅ Production users won't see it (they use your app, not browser)
- ✅ You only see it when manually typing URLs
- ✅ One click solves it for browser testing

**This is completely normal and expected behavior!** 🎉

---

## 📚 Additional Resources

- Ngrok Documentation: https://ngrok.com/docs
- Ngrok Browser Warning: https://ngrok.com/docs/guides/security/abuse-protection
- Your Dashboard: https://dashboard.ngrok.com
- Support: support@ngrok.com (Hobby+ plans)

---

Last Updated: October 10, 2025

