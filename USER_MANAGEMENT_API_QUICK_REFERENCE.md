# User Management API - Quick Reference

## 🔐 Authentication Endpoints

### 1. **Google OAuth Login/Register**
```
POST /api/v1/auth/google
```
**Request:**
```json
{
  "idToken": "google_id_token"
}
```

**Responses:**
- **Success (Existing Active User):** Returns JWT access token
- **Pending:** User request is awaiting approval
- **New User:** Access request created
- **Rejected:** Request was rejected

---

### 2. **Get Current User**
```
GET /api/v1/auth/me
Headers: Authorization: Bearer <token>
```

---

### 3. **Logout**
```
POST /api/v1/auth/logout
Headers: Authorization: Bearer <token>
```

---

### 4. **Refresh Token**
```
POST /api/v1/auth/refresh
Headers: Authorization: Bearer <refresh_token>
```

---

### 5. **Check Request Status**
```
GET /api/v1/auth/request-status?email=user@example.com
```

---

## 👥 Admin Endpoints

### 1. **Get Access Requests Queue**
```
GET /api/v1/admin/access-requests?status=pending
Headers: Authorization: Bearer <admin_token>
```

---

### 2. **Approve Request**
```
POST /api/v1/admin/access-requests/{requestId}/approve
Headers: Authorization: Bearer <admin_token>

Body (optional):
{
  "role": "user"  // or "admin"
}
```

---

### 3. **Reject Request**
```
POST /api/v1/admin/access-requests/{requestId}/reject
Headers: Authorization: Bearer <admin_token>

Body (optional):
{
  "reason": "Rejection reason"
}
```

---

### 4. **Get All Users**
```
GET /api/v1/admin/users?status=active&role=user
Headers: Authorization: Bearer <admin_token>
```

---

### 5. **Update User**
```
PATCH /api/v1/admin/users/{userId}
Headers: Authorization: Bearer <admin_token>

Body:
{
  "role": "admin",
  "status": "active"
}
```

---

### 6. **Delete User**
```
DELETE /api/v1/admin/users/{userId}
Headers: Authorization: Bearer <admin_token>
```

---

## 📊 Updated Existing Endpoints

### Models API (Now User-Scoped)

**All endpoints require authentication**

```
GET  /api/v1/models/              # Returns current user's models
GET  /api/v1/models/?all=true     # Admin only - all models
POST /api/v1/models/              # Creates model for current user
GET  /api/v1/models/{id}/         # Get model (own or admin)
DELETE /api/v1/models/{id}/       # Delete model (own or admin)
```

---

### Looks API (Now User-Scoped)

**All endpoints require authentication**

```
GET  /api/v1/looks/               # Returns current user's looks
GET  /api/v1/looks/?all=true      # Admin only - all looks
POST /api/v1/looks/               # Creates look for current user
GET  /api/v1/looks/{id}/          # Get look (own or admin)
PATCH /api/v1/looks/{id}/         # Update look (own or admin)
DELETE /api/v1/looks/{id}/        # Delete look (own or admin)
```

---

## 🔑 User Roles & Permissions

### Regular User (role: "user")
- ✅ Login via Google OAuth
- ✅ View own models and looks
- ✅ Create models and looks
- ✅ Update/delete own content
- ❌ Cannot access admin routes
- ❌ Cannot view other users' content

### Admin (role: "admin")
- ✅ All regular user permissions
- ✅ View/approve/reject access requests
- ✅ View all users
- ✅ Update user roles and status
- ✅ Delete users
- ✅ View all models/looks (with `?all=true`)
- ✅ Delete any model/look

---

## 🚦 User Statuses

- **`pending`:** Access request submitted, awaiting approval
- **`active`:** Approved, can login and use the platform
- **`suspended`:** Account suspended by admin, cannot login

---

## 🔄 User Journey

### New User
1. Click "Sign in with Google" → Google OAuth
2. Backend creates access request (status: pending)
3. User sees "Request submitted" message
4. Admin approves request
5. User logs in again → Gets access token → Can use platform

### Existing User
1. Click "Sign in with Google" → Google OAuth
2. Backend verifies user (status: active)
3. Returns JWT access token
4. User can immediately access platform

---

## 🎯 Quick Setup for Frontend

### 1. Install Google OAuth
```bash
npm install @react-oauth/google
```

### 2. Wrap App with Provider
```jsx
<GoogleOAuthProvider clientId="YOUR_GOOGLE_CLIENT_ID">
  <App />
</GoogleOAuthProvider>
```

### 3. Add Login Button
```jsx
<GoogleLogin
  onSuccess={(response) => {
    // Send response.credential to backend /api/v1/auth/google
  }}
/>
```

### 4. Store Token
```javascript
// After successful login
localStorage.setItem('accessToken', response.data.data.accessToken);
```

### 5. Add to API Requests
```javascript
axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
```

---

## 📝 Response Status Codes

- **200:** Success
- **201:** Created
- **204:** No Content (successful deletion)
- **400:** Bad Request
- **401:** Unauthorized (invalid/missing token)
- **403:** Forbidden (insufficient permissions)
- **404:** Not Found
- **409:** Conflict (duplicate email)
- **500:** Internal Server Error

---

## 🔐 JWT Token Format

```json
{
  "sub": "user_uuid",
  "email": "user@example.com",
  "role": "user",
  "status": "active",
  "exp": 1697025600
}
```

**Token Expiry:** 24 hours (default)

---

## 📊 Database Tables

### Users
- id, email, google_id, full_name, profile_picture
- role (admin/user), status (pending/active/suspended)
- created_at, updated_at, last_login

### Access Requests
- id, email, full_name, google_id, profile_picture
- reason, status (pending/approved/rejected)
- requested_at, reviewed_at, reviewed_by, rejection_reason

### Models & Looks (Updated)
- Added: `user_id` (foreign key to users.id)

---

## 🌐 Environment Variables

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# JWT
JWT_SECRET_KEY=your_jwt_secret_key_JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# First Admin
FIRST_ADMIN_EMAIL=admin@example.com
```

---

## 🧪 Testing Endpoints

### Test Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/google \
  -H "Content-Type: application/json" \
  -d '{"idToken": "google_token_here"}'
```

### Test Protected Route
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer your_jwt_token"
```

### Test Admin Route
```bash
curl http://localhost:8000/api/v1/admin/access-requests \
  -H "Authorization: Bearer admin_jwt_token"
```

---

## ⚡ Key Features

✅ **Gmail OAuth Integration**
✅ **Automatic Access Request System**
✅ **Admin Approval Workflow**
✅ **Role-Based Access Control (RBAC)**
✅ **User-Scoped Models & Looks**
✅ **JWT Authentication**
✅ **Secure Token Management**

---

**Need implementation help? I can build this step-by-step!** 🚀


