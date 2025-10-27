# User Management API - Complete Design

## Overview

This document outlines the complete user management system with Gmail OAuth, approval workflow, and role-based access control.

---

## 📊 Database Schema

### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    google_id VARCHAR(255) UNIQUE,
    full_name VARCHAR(255),
    profile_picture VARCHAR(512),
    role VARCHAR(20) DEFAULT 'user',  -- 'admin' or 'user'
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'active', 'suspended'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### Access Requests Table

```sql
CREATE TABLE access_requests (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    google_id VARCHAR(255),
    profile_picture VARCHAR(512),
    reason TEXT,  -- Optional: Why they want access
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewed_by UUID,  -- FK to users.id (admin who reviewed)
    rejection_reason TEXT,
    FOREIGN KEY (reviewed_by) REFERENCES users(id)
);
```

### Update Existing Tables

```sql
-- Add user_id to models table
ALTER TABLE models ADD COLUMN user_id UUID;
ALTER TABLE models ADD FOREIGN KEY (user_id) REFERENCES users(id);

-- Add user_id to looks table
ALTER TABLE looks ADD COLUMN user_id UUID;
ALTER TABLE looks ADD FOREIGN KEY (user_id) REFERENCES users(id);
```

---

## 🔐 Authentication Flow

### 1. Gmail OAuth Flow

```
Frontend → Google OAuth → Get ID Token → Send to Backend → Verify Token → Check User
```

---

## 📋 API Endpoints

### Base URL
```
/api/v1/auth
/api/v1/users
/api/v1/admin
```

---

## 1️⃣ Authentication Endpoints

### **POST** `/api/v1/auth/google`
**Description:** Login or request access via Google OAuth

**Request Body:**
```json
{
  "idToken": "google_id_token_here"
}
```

**Response (Existing User - Active):**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "fullName": "John Doe",
      "profilePicture": "https://...",
      "role": "user",
      "status": "active"
    },
    "accessToken": "jwt_token_here",
    "tokenType": "Bearer",
    "expiresIn": 86400
  }
}
```

**Response (Existing User - Pending):**
```json
{
  "status": "pending",
  "message": "Your access request is pending approval",
  "data": {
    "requestId": "uuid",
    "requestedAt": "2025-10-10T12:00:00Z"
  }
}
```

**Response (New User - Access Request Created):**
```json
{
  "status": "request_created",
  "message": "Access request submitted successfully. You will be notified once approved.",
  "data": {
    "requestId": "uuid",
    "email": "newuser@example.com",
    "requestedAt": "2025-10-10T12:00:00Z"
  }
}
```

**Response (Existing User - Rejected):**
```json
{
  "status": "rejected",
  "message": "Your access request was rejected",
  "data": {
    "rejectedAt": "2025-10-09T10:00:00Z",
    "rejectionReason": "Reason provided by admin"
  }
}
```

---

### **POST** `/api/v1/auth/refresh`
**Description:** Refresh access token

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response:**
```json
{
  "accessToken": "new_jwt_token_here",
  "tokenType": "Bearer",
  "expiresIn": 86400
}
```

---

### **POST** `/api/v1/auth/logout`
**Description:** Logout user (invalidate token)

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Logout successful"
}
```

---

### **GET** `/api/v1/auth/me`
**Description:** Get current user info

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "fullName": "John Doe",
  "profilePicture": "https://...",
  "role": "user",
  "status": "active",
  "createdAt": "2025-10-10T12:00:00Z",
  "lastLogin": "2025-10-10T14:30:00Z"
}
```

---

## 2️⃣ Access Request Endpoints (User)

### **POST** `/api/v1/auth/request-access`
**Description:** Submit access request (alternative to OAuth for manual requests)

**Request Body:**
```json
{
  "email": "user@example.com",
  "fullName": "John Doe",
  "reason": "I'm a fashion designer and want to use AI Studio"
}
```

**Response:**
```json
{
  "message": "Access request submitted successfully",
  "requestId": "uuid",
  "requestedAt": "2025-10-10T12:00:00Z"
}
```

---

### **GET** `/api/v1/auth/request-status`
**Description:** Check access request status

**Query Parameters:**
- `email` (required): Email to check

**Response:**
```json
{
  "status": "pending",
  "requestId": "uuid",
  "requestedAt": "2025-10-10T12:00:00Z",
  "message": "Your request is under review"
}
```

---

## 3️⃣ Admin Endpoints

### **GET** `/api/v1/admin/access-requests`
**Description:** Get all pending access requests

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Query Parameters:**
- `status` (optional): Filter by status (pending/approved/rejected)
- `skip` (optional, default: 0): Pagination offset
- `limit` (optional, default: 20): Pagination limit

**Response:**
```json
{
  "requests": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "fullName": "John Doe",
      "profilePicture": "https://...",
      "reason": "I'm a fashion designer...",
      "status": "pending",
      "requestedAt": "2025-10-10T12:00:00Z"
    }
  ],
  "total": 10,
  "skip": 0,
  "limit": 20
}
```

---

### **POST** `/api/v1/admin/access-requests/{requestId}/approve`
**Description:** Approve an access request

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
  "role": "user"  // Optional: "user" (default) or "admin"
}
```

**Response:**
```json
{
  "message": "Access request approved successfully",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "fullName": "John Doe",
    "role": "user",
    "status": "active"
  }
}
```

---

### **POST** `/api/v1/admin/access-requests/{requestId}/reject`
**Description:** Reject an access request

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
  "reason": "Reason for rejection"  // Optional
}
```

**Response:**
```json
{
  "message": "Access request rejected successfully",
  "requestId": "uuid"
}
```

---

### **GET** `/api/v1/admin/users`
**Description:** Get all users (admin only)

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Query Parameters:**
- `status` (optional): Filter by status (active/pending/suspended)
- `role` (optional): Filter by role (admin/user)
- `skip` (optional, default: 0): Pagination offset
- `limit` (optional, default: 20): Pagination limit

**Response:**
```json
{
  "users": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "fullName": "John Doe",
      "profilePicture": "https://...",
      "role": "user",
      "status": "active",
      "createdAt": "2025-10-10T12:00:00Z",
      "lastLogin": "2025-10-10T14:30:00Z"
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 20
}
```

---

### **PATCH** `/api/v1/admin/users/{userId}`
**Description:** Update user (change role, suspend, etc.)

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
  "role": "admin",  // Optional
  "status": "suspended"  // Optional: active/suspended
}
```

**Response:**
```json
{
  "message": "User updated successfully",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "admin",
    "status": "active"
  }
}
```

---

### **DELETE** `/api/v1/admin/users/{userId}`
**Description:** Delete user (admin only)

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
{
  "message": "User deleted successfully"
}
```

---

## 4️⃣ Updated Existing Endpoints

### Models API (With User Association)

All model endpoints now require authentication and filter by user:

**POST** `/api/v1/models/`
- Now requires `Authorization` header
- Automatically associates model with current user

**GET** `/api/v1/models/`
- Returns only models created by current user
- Query param `all=true` (admin only) to see all models

**DELETE** `/api/v1/models/{id}/`
- Users can only delete their own models
- Admins can delete any model

---

### Looks API (With User Association)

Same pattern as Models API:

**POST** `/api/v1/looks/`
- Requires authentication
- Associates with current user

**GET** `/api/v1/looks/`
- Returns user's own looks
- Admin can use `all=true` to see all

**DELETE** `/api/v1/looks/{id}/`
- Users delete own looks
- Admins can delete any

---

## 🔒 Authentication & Authorization

### JWT Token Structure

```json
{
  "sub": "user_uuid",
  "email": "user@example.com",
  "role": "user",
  "status": "active",
  "iat": 1696939200,
  "exp": 1697025600
}
```

### Protected Routes

All routes except `/auth/google` and `/auth/request-access` require authentication.

### Admin-Only Routes

These routes require `role: "admin"`:
- `/api/v1/admin/*` (all admin endpoints)
- `/api/v1/models?all=true`
- `/api/v1/looks?all=true`

---

## 📝 Implementation Checklist

### Database Setup
- [ ] Create `users` table
- [ ] Create `access_requests` table
- [ ] Add `user_id` to `models` table
- [ ] Add `user_id` to `looks` table
- [ ] Create database indexes
- [ ] Create migration scripts

### Backend Implementation
- [ ] Install dependencies (`google-auth`, `pyjwt`)
- [ ] Create User model
- [ ] Create AccessRequest model
- [ ] Implement Google OAuth verification
- [ ] Implement JWT token generation
- [ ] Create authentication middleware
- [ ] Create authorization middleware (role check)
- [ ] Implement auth endpoints
- [ ] Implement admin endpoints
- [ ] Update models endpoints
- [ ] Update looks endpoints
- [ ] Add user filtering logic

### Frontend Implementation
- [ ] Install Google OAuth library
- [ ] Create login page
- [ ] Create access request page
- [ ] Create admin dashboard
- [ ] Create request queue view
- [ ] Add authentication context
- [ ] Add protected routes
- [ ] Update models pages to use auth
- [ ] Update looks pages to use auth

---

## 🔧 Configuration

### Environment Variables

Add to `.env`:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# JWT
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
JWT_REFRESH_TOKEN_EXPIRE_DAYS=30

# Admin (first admin user - created on startup)
FIRST_ADMIN_EMAIL=admin@example.com
```

---

## 📚 Dependencies to Install

```bash
# Backend
pip install google-auth google-auth-oauthlib google-auth-httplib2
pip install pyjwt[crypto]
pip install python-jose[cryptography]

# Frontend
npm install @react-oauth/google
# or for other frameworks, appropriate OAuth library
```

---

## 🚀 Quick Start Guide

### 1. Set up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs:
   - `http://localhost:3000` (dev)
   - `https://your-production-domain.com` (prod)
6. Copy Client ID and Client Secret to `.env`

### 2. Create First Admin

Run this script once to create your first admin user:

```bash
python scripts/create_first_admin.py
```

### 3. Test Authentication

```bash
# 1. Get Google ID token from frontend
# 2. Test login
curl -X POST http://localhost:8000/api/v1/auth/google \
  -H "Content-Type: application/json" \
  -d '{"idToken": "google_token_here"}'

# 3. Use returned JWT for protected routes
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer jwt_token_here"
```

---

## 🔄 User Flow Diagrams

### New User Flow

```
1. User clicks "Sign in with Google"
   ↓
2. Google OAuth popup
   ↓
3. User grants permission
   ↓
4. Frontend receives ID token
   ↓
5. Frontend sends ID token to backend
   ↓
6. Backend checks if user exists
   ↓
7. User doesn't exist → Create access request
   ↓
8. Show "Request submitted, awaiting approval" message
   ↓
9. Admin reviews request
   ↓
10. Admin approves → User receives email notification
   ↓
11. User logs in again → Gets access token → Can use app
```

### Existing User Flow

```
1. User clicks "Sign in with Google"
   ↓
2. Google OAuth popup
   ↓
3. Frontend receives ID token
   ↓
4. Frontend sends ID token to backend
   ↓
5. Backend verifies token & finds user
   ↓
6. Backend generates JWT access token
   ↓
7. User is logged in → Can use app
```

### Admin Approval Flow

```
1. Admin logs in
   ↓
2. Goes to Admin Dashboard
   ↓
3. Sees "Access Requests" section with count badge
   ↓
4. Clicks to view requests queue
   ↓
5. Reviews each request (email, name, reason)
   ↓
6. Clicks "Approve" or "Reject"
   ↓
7. If rejected, can add reason
   ↓
8. Request status updated in database
   ↓
9. User notified via email (optional)
```

---

## 🎨 Frontend Code Examples

### React Example - Login

```jsx
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import axios from 'axios';

function LoginPage() {
  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const response = await axios.post('/api/v1/auth/google', {
        idToken: credentialResponse.credential
      });

      if (response.data.status === 'success') {
        // Store token and redirect
        localStorage.setItem('accessToken', response.data.data.accessToken);
        window.location.href = '/dashboard';
      } else if (response.data.status === 'pending') {
        // Show pending message
        alert('Your request is pending approval');
      } else if (response.data.status === 'request_created') {
        // Show success message
        alert('Access request submitted! You will be notified once approved.');
      }
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <GoogleOAuthProvider clientId="YOUR_GOOGLE_CLIENT_ID">
      <div>
        <h1>Welcome to AI Studio</h1>
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={() => console.log('Login Failed')}
        />
      </div>
    </GoogleOAuthProvider>
  );
}
```

### React Example - Admin Dashboard

```jsx
import { useState, useEffect } from 'react';
import axios from 'axios';

function AdminDashboard() {
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    loadRequests();
  }, []);

  const loadRequests = async () => {
    const response = await axios.get('/api/v1/admin/access-requests', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
      }
    });
    setRequests(response.data.requests);
  };

  const handleApprove = async (requestId) => {
    await axios.post(
      `/api/v1/admin/access-requests/${requestId}/approve`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      }
    );
    loadRequests(); // Reload
  };

  const handleReject = async (requestId) => {
    const reason = prompt('Rejection reason (optional):');
    await axios.post(
      `/api/v1/admin/access-requests/${requestId}/reject`,
      { reason },
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      }
    );
    loadRequests(); // Reload
  };

  return (
    <div>
      <h1>Access Requests ({requests.length})</h1>
      {requests.map(request => (
        <div key={request.id}>
          <h3>{request.fullName}</h3>
          <p>{request.email}</p>
          <p>{request.reason}</p>
          <button onClick={() => handleApprove(request.id)}>Approve</button>
          <button onClick={() => handleReject(request.id)}>Reject</button>
        </div>
      ))}
    </div>
  );
}
```

---

## 🔐 Security Best Practices

1. **JWT Secret:** Use a strong, random secret key (256+ bits)
2. **Token Expiry:** Access tokens should expire (24 hours recommended)
3. **HTTPS Only:** Always use HTTPS in production
4. **Token Storage:** Store JWT in httpOnly cookies (not localStorage)
5. **CORS:** Configure CORS properly
6. **Rate Limiting:** Add rate limiting to auth endpoints
7. **Input Validation:** Validate all inputs
8. **SQL Injection:** Use parameterized queries (SQLAlchemy handles this)
9. **XSS Protection:** Sanitize user inputs
10. **Admin Actions:** Log all admin actions for audit trail

---

## 📊 Database Indexes

For performance, create these indexes:

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_role_status ON users(role, status);
CREATE INDEX idx_access_requests_status ON access_requests(status);
CREATE INDEX idx_access_requests_email ON access_requests(email);
CREATE INDEX idx_models_user_id ON models(user_id);
CREATE INDEX idx_looks_user_id ON looks(user_id);
```

---

## 🧪 Testing Checklist

### Authentication Tests
- [ ] Google OAuth login (new user)
- [ ] Google OAuth login (existing user)
- [ ] Access request creation
- [ ] JWT token generation
- [ ] JWT token validation
- [ ] Token expiry
- [ ] Logout

### Authorization Tests
- [ ] User can access own models
- [ ] User cannot access other user's models
- [ ] Admin can access all models
- [ ] User cannot access admin routes
- [ ] Admin can access admin routes

### Access Request Tests
- [ ] Create access request
- [ ] Approve access request
- [ ] Reject access request
- [ ] Check request status
- [ ] Duplicate requests handling

---

## 📞 Support & Next Steps

After implementing this system, you may want to add:

1. **Email Notifications:**
   - Welcome email on approval
   - Rejection notification
   - Admin notification on new request

2. **Audit Logging:**
   - Track all admin actions
   - User login history
   - Model/look creation tracking

3. **Advanced Features:**
   - Team/workspace support
   - Model sharing between users
   - Collaboration features
   - Usage analytics

---

**Ready to implement? Let me know and I'll help you build this step by step!** 🚀


