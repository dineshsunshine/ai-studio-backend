# User Management System - Setup Guide

## 🚀 Quick Start

This guide will help you set up the complete user management system with Google OAuth authentication.

---

## 📋 Prerequisites

- Python 3.8+ installed
- Google Cloud account (for OAuth)
- ngrok account (for public URL)

---

## 🔧 Step-by-Step Setup

### Step 1: Install Dependencies

```bash
cd /Users/dgolani/Documents/AI_Studio/backend
source venv/bin/activate
pip install -r requirements.txt
```

✅ **What was installed:**
- `google-auth` & `google-auth-oauthlib` - For Google OAuth
- `python-jose[cryptography]` - For JWT tokens
- `passlib[bcrypt]` - For password hashing (future use)

---

### Step 2: Set Up Google OAuth

#### 2.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Project name: "AI Studio" (or your preference)

#### 2.2 Enable Google+ API

1. Go to **APIs & Services** → **Library**
2. Search for "Google+ API"
3. Click **Enable**

#### 2.3 Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth 2.0 Client ID**
3. Application type: **Web application**
4. Name: "AI Studio Web Client"
5. **Authorized JavaScript origins:**
   ```
   http://localhost:3000
   https://yourdomain.com
   ```
6. **Authorized redirect URIs:**
   ```
   http://localhost:3000
   http://localhost:3000/auth/callback
   https://yourdomain.com/auth/callback
   ```
7. Click **Create**
8. Copy the **Client ID** and **Client Secret**

---

### Step 3: Configure Environment Variables

#### 3.1 Copy the sample .env file

```bash
cp .env_sample .env
```

#### 3.2 Edit .env and add your credentials

```bash
nano .env  # or use your preferred editor
```

**Update these values:**

```bash
# Google OAuth (REQUIRED)
GOOGLE_CLIENT_ID=your_actual_google_client_id
GOOGLE_CLIENT_SECRET=your_actual_google_client_secret

# JWT Secret (Generate a random string)
JWT_SECRET_KEY=run_openssl_rand_hex_32_to_generate_this

# First Admin Email (Your email)
FIRST_ADMIN_EMAIL=your_email@gmail.com

# ngrok (Already configured)
NGROK_AUTH_TOKEN=33kZfkHRoA3ixlRP66j9EmBPKXR_7o3v7V9HHNU1M9hCJcb2S
NGROK_DOMAIN=zestfully-chalky-nikia.ngrok-free.app
```

**To generate a secure JWT secret:**
```bash
openssl rand -hex 32
```

---

### Step 4: Migrate Database

⚠️ **WARNING:** This will drop all existing tables!

```bash
python scripts/migrate_database.py
```

**What this does:**
1. Backs up existing database (if any)
2. Drops all tables
3. Creates new tables with user management schema:
   - `users` - User accounts
   - `access_requests` - Pending access requests
   - `models` - Fashion models (with user_id)
   - `looks` - Fashion looks (with user_id)
   - `products` - Products in looks

---

### Step 5: Create Admin User

```bash
python scripts/create_admin.py
```

**Follow the prompts:**
- Enter your Gmail address (the one you'll use to login)
- Enter your full name
- Confirm

✅ **Result:** You now have an admin account!

---

### Step 6: Start the Backend

```bash
python api_with_db_and_ngrok.py
```

**You should see:**
```
✅ Tables created successfully!
🚀 Starting AI Studio Backend with Database + Ngrok
📊 Database tables: ['users', 'access_requests', 'models', 'looks', 'products']
```

---

### Step 7: Test Authentication

#### 7.1 Access the API documentation

Open your browser and go to:
```
https://zestfully-chalky-nikia.ngrok-free.app/AIStudio/docs
```

#### 7.2 Test the /auth/google endpoint

**You'll need to:**
1. Implement Google Sign-In in your frontend
2. Get the Google ID token from the OAuth flow
3. Send it to `/api/v1/auth/google`

**Example response (Admin user):**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "user": {
      "id": "uuid-here",
      "email": "your_email@gmail.com",
      "role": "admin",
      "status": "active"
    },
    "accessToken": "jwt_token_here",
    "tokenType": "Bearer",
    "expiresIn": 86400
  }
}
```

---

## 📚 API Endpoints Reference

### Authentication

- **POST** `/api/v1/auth/google` - Login/Register with Google
- **GET** `/api/v1/auth/me` - Get current user
- **POST** `/api/v1/auth/logout` - Logout
- **GET** `/api/v1/auth/request-status` - Check access request status

### Admin (Requires Admin Role)

- **GET** `/api/v1/admin/access-requests` - View pending requests
- **POST** `/api/v1/admin/access-requests/{id}/approve` - Approve request
- **POST** `/api/v1/admin/access-requests/{id}/reject` - Reject request
- **GET** `/api/v1/admin/users` - List all users
- **PATCH** `/api/v1/admin/users/{id}` - Update user (role/status)
- **DELETE** `/api/v1/admin/users/{id}` - Delete user

### Models (Requires Authentication)

- **GET** `/api/v1/models/` - List your models
- **GET** `/api/v1/models/?all=true` - List all models (admin only)
- **POST** `/api/v1/models/` - Create model (with authentication)
- **GET** `/api/v1/models/{id}/` - Get model
- **DELETE** `/api/v1/models/{id}/` - Delete model

### Looks (Requires Authentication)

- **GET** `/api/v1/looks/` - List your looks
- **GET** `/api/v1/looks/?all=true` - List all looks (admin only)
- **POST** `/api/v1/looks/` - Create look (with authentication)
- **GET** `/api/v1/looks/{id}/` - Get look
- **PATCH** `/api/v1/looks/{id}/` - Update look
- **DELETE** `/api/v1/looks/{id}/` - Delete look

---

## 🔐 Using JWT Tokens

### In API Requests

After successful login, include the JWT token in all API requests:

```bash
curl https://zestfully-chalky-nikia.ngrok-free.app/AIStudio/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### In Frontend (JavaScript/React)

```javascript
// Store token after login
localStorage.setItem('accessToken', response.data.data.accessToken);

// Use in all API requests
const config = {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
  }
};

axios.get('/api/v1/auth/me', config);
```

---

## 🧪 Testing the Complete Flow

### Test 1: Admin Login

1. **Frontend:** User clicks "Sign in with Google"
2. **Google:** User authorizes your app
3. **Frontend:** Gets ID token from Google
4. **Frontend → Backend:** POST `/api/v1/auth/google` with `idToken`
5. **Backend:** Verifies token, checks if admin exists
6. **Backend → Frontend:** Returns JWT access token
7. **Frontend:** Stores token, redirects to dashboard

✅ **Expected:** Admin is logged in

---

### Test 2: New User Request

1. **New user** tries to login with Google
2. **Backend:** Creates access request (status: pending)
3. **Backend → Frontend:** Returns "request_created" status
4. **Frontend:** Shows "Request submitted, awaiting approval"

✅ **Expected:** Access request created

---

### Test 3: Admin Approves Request

1. **Admin:** Opens admin dashboard
2. **Admin → Backend:** GET `/api/v1/admin/access-requests`
3. **Backend → Admin:** Returns list of pending requests
4. **Admin:** Clicks "Approve" on a request
5. **Admin → Backend:** POST `/api/v1/admin/access-requests/{id}/approve`
6. **Backend:** Creates user account (status: active)
7. **Backend → Admin:** Returns created user

✅ **Expected:** User can now login

---

### Test 4: Approved User Login

1. **User:** Tries to login again with Google
2. **Backend:** Finds user, checks status (active)
3. **Backend → User:** Returns JWT token
4. **User:** Is logged in and can use the platform

✅ **Expected:** User has full access

---

## 🎨 Frontend Integration Guide

### React Example - Google OAuth

```jsx
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import axios from 'axios';

const API_BASE_URL = 'https://zestfully-chalky-nikia.ngrok-free.app/AIStudio/api/v1';

function LoginPage() {
  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/auth/google`, {
        idToken: credentialResponse.credential
      });

      const { status, message, data } = response.data;

      if (status === 'success') {
        // Store token
        localStorage.setItem('accessToken', data.accessToken);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Redirect to dashboard
        window.location.href = '/dashboard';
      } 
      else if (status === 'pending') {
        // Show pending message
        alert('Your access request is pending approval. Please wait.');
      } 
      else if (status === 'request_created') {
        // Show request created message
        alert('Access request submitted! You will be notified once approved.');
      }
      else if (status === 'rejected') {
        // Show rejected message
        alert(`Your request was rejected: ${data.rejectionReason || 'No reason provided'}`);
      }
    } catch (error) {
      console.error('Login failed:', error);
      alert('Login failed. Please try again.');
    }
  };

  return (
    <GoogleOAuthProvider clientId="YOUR_GOOGLE_CLIENT_ID">
      <div className="login-container">
        <h1>Welcome to AI Studio</h1>
        <p>Please sign in to continue</p>
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={() => alert('Login Failed')}
        />
      </div>
    </GoogleOAuthProvider>
  );
}

export default LoginPage;
```

---

## 🛠️ Troubleshooting

### Issue: "Invalid Google ID token"

**Solution:**
- Check that `GOOGLE_CLIENT_ID` in `.env` matches your Google Cloud Console
- Ensure Google+ API is enabled
- Verify redirect URIs are correctly configured

---

### Issue: "User account is pending"

**Solution:**
- Login as admin
- Go to admin dashboard
- Approve the pending access request

---

### Issue: "Could not validate credentials" (401)

**Solution:**
- Check that JWT token is being sent correctly
- Verify token hasn't expired (24 hours by default)
- Ensure `Authorization: Bearer TOKEN` header format is correct

---

### Issue: Database connection error

**Solution:**
```bash
# Re-run migration
python scripts/migrate_database.py

# Recreate admin
python scripts/create_admin.py
```

---

## 📖 Additional Documentation

- **Complete API Design:** `USER_MANAGEMENT_API_DESIGN.md`
- **Quick Reference:** `USER_MANAGEMENT_API_QUICK_REFERENCE.md`
- **Frontend Integration:** See React example above

---

## 🎉 You're All Set!

Your user management system is now fully functional with:

✅ Google OAuth authentication  
✅ JWT-based session management  
✅ Role-based access control (Admin/User)  
✅ Access request approval workflow  
✅ User-scoped models and looks  
✅ Admin dashboard for user management  

**Need help?** Check the documentation or ask questions!

---

## 🔄 Next Steps

1. **Build Frontend UI:**
   - Login page with Google Sign-In button
   - Admin dashboard for managing requests
   - User profile page

2. **Add Email Notifications:**
   - Send email when request is approved
   - Send email when request is rejected
   - Welcome email for new users

3. **Add More Features:**
   - User profile editing
   - Password reset (if adding email/password auth)
   - Activity logs
   - Usage analytics

---

**Happy coding!** 🚀


