# Frontend Implementation Guide: Access Request System

## Overview

We need to implement a complete access request system that allows new users to request access to the platform and admins to approve or reject those requests.

---

## User Flows to Implement

### Flow 1: New User Requesting Access

**What happens:**
1. A new user clicks "Sign in with Google"
2. They authenticate with Google
3. Backend tells us they need to request access
4. We show them a "Request Access" screen
5. They can optionally provide a reason for requesting access
6. They submit the request
7. We show them a "Request Submitted" confirmation

### Flow 2: Existing User with Pending Request

**What happens:**
1. User clicks "Sign in with Google"
2. They authenticate with Google
3. Backend tells us their request is still pending
4. We show them a "Request Pending" screen with status
5. They wait for admin approval (can check status periodically)

### Flow 3: Admin Viewing and Managing Requests

**What happens:**
1. Admin logs in (they're already approved)
2. They see a notification/badge showing number of pending requests
3. They navigate to "Access Requests" section
4. They see a list of all pending requests with user details
5. For each request, they can:
   - View user email, name, profile picture, reason
   - Approve the request (optionally assign a role)
   - Reject the request (optionally provide a reason)
6. After action, the list updates

---

## UI Components to Build

### Component 1: Access Request Screen (for new users)

**When to show:** After Google login, when backend returns `status: "request_created"` or `status: "pending"`

**What to display:**
- User's name and profile picture (from Google)
- User's email
- A text area for "Why do you want access?" (optional)
- "Submit Request" button
- OR if already submitted: "Your request is pending approval"
- Show when request was submitted
- "Check Status" button to refresh

**Design suggestions:**
- Friendly, welcoming message
- Maybe an icon or illustration
- Clear call-to-action
- Show estimated response time if available

---

### Component 2: Admin Access Requests Dashboard

**When to show:** In admin panel/section, when user has `role: "admin"`

**What to display:**

**Header Section:**
- Title: "Access Requests"
- Badge showing number of pending requests
- Filter tabs: "Pending" | "Approved" | "Rejected"

**Request List:**
For each request, show a card with:
- User profile picture
- User name
- User email
- Request date (e.g., "Requested 2 hours ago")
- Reason (if provided)
- Action buttons: "Approve" | "Reject"

**Approve Modal:**
- Confirmation: "Approve access for [name]?"
- Dropdown: Select role (User | Admin)
- Default: User
- "Confirm" and "Cancel" buttons

**Reject Modal:**
- Confirmation: "Reject access for [name]?"
- Text area: "Reason for rejection" (optional)
- "Confirm" and "Cancel" buttons

**Design suggestions:**
- Clean, professional look
- Easy to scan list
- Clear actions
- Show most recent requests first
- Maybe add search/filter by email

---

## API Integration Details

### API 1: Login with Google

**Endpoint:** `POST /AIStudio/api/v1/auth/google/`

**When to call:** Right after user successfully signs in with Google

**What to send:**
```javascript
{
  "google_id_token": "the_token_you_got_from_google"
}
```

**What you'll get back:**

**Case 1: User is approved and can login**
```javascript
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "user": {
      "id": "user-uuid",
      "email": "user@gmail.com",
      "fullName": "John Doe",
      "profilePicture": "https://...",
      "role": "admin",  // or "user"
      "status": "active"
    },
    "accessToken": "jwt_token_here",
    "tokenType": "Bearer",
    "expiresIn": 86400
  }
}
```
**What to do:** Store the `accessToken`, save user info, redirect to main app

---

**Case 2: New user needs to request access**
```javascript
{
  "status": "request_created",
  "message": "Access request submitted successfully. You will be notified once approved.",
  "data": {
    "requestId": "request-uuid",
    "email": "user@gmail.com",
    "requestedAt": "2025-10-10T12:00:00Z"
  }
}
```
**What to do:** Show "Request Submitted" screen, save request ID locally

---

**Case 3: User has a pending request**
```javascript
{
  "status": "pending",
  "message": "Your access request is pending approval",
  "data": {
    "requestId": "request-uuid",
    "requestedAt": "2025-10-10T12:00:00Z"
  }
}
```
**What to do:** Show "Request Pending" screen with status

---

**Case 4: User's request was rejected**
```javascript
{
  "status": "rejected",
  "message": "Your access request was rejected",
  "data": {
    "rejectedAt": "2025-10-10T15:00:00Z",
    "rejectionReason": "Does not meet criteria"
  }
}
```
**What to do:** Show rejection message, allow them to request again

---

### API 2: Get All Access Requests (Admin Only)

**Endpoint:** `GET /AIStudio/api/v1/admin/access-requests`

**When to call:** When admin opens the Access Requests page

**Headers required:**
```javascript
{
  "Authorization": "Bearer admin_jwt_token_here"
}
```

**Query parameters (optional):**
- `status=pending` - Filter by status (pending/approved/rejected)
- `skip=0` - For pagination
- `limit=20` - Number per page

**Example call:**
```
GET /AIStudio/api/v1/admin/access-requests?status=pending&skip=0&limit=20
```

**What you'll get back:**
```javascript
{
  "requests": [
    {
      "id": "request-uuid",
      "email": "newuser@gmail.com",
      "fullName": "Jane Smith",
      "profilePicture": "https://...",
      "reason": "I want to use the platform for my fashion store",
      "status": "pending",
      "requestedAt": "2025-10-10T12:00:00Z",
      "reviewedAt": null,
      "rejectionReason": null
    },
    // ... more requests
  ],
  "total": 5,
  "skip": 0,
  "limit": 20
}
```

**What to do:** Display the list of requests in your admin dashboard

---

### API 3: Approve Access Request (Admin Only)

**Endpoint:** `POST /AIStudio/api/v1/admin/access-requests/{requestId}/approve`

**When to call:** When admin clicks "Approve" and confirms

**Headers required:**
```javascript
{
  "Authorization": "Bearer admin_jwt_token_here",
  "Content-Type": "application/json"
}
```

**What to send:**
```javascript
{
  "role": "user"  // or "admin" if you want to make them admin
}
```

**Example call:**
```
POST /AIStudio/api/v1/admin/access-requests/abc-123-def/approve
Body: { "role": "user" }
```

**What you'll get back:**
```javascript
{
  "id": "user-uuid",
  "email": "newuser@gmail.com",
  "fullName": "Jane Smith",
  "profilePicture": "https://...",
  "role": "user",
  "status": "active",
  "createdAt": "2025-10-10T15:30:00Z",
  "lastLogin": null
}
```

**What to do:** 
- Show success message: "Access approved for [name]!"
- Remove the request from the pending list
- Optionally notify the user (future feature)

---

### API 4: Reject Access Request (Admin Only)

**Endpoint:** `POST /AIStudio/api/v1/admin/access-requests/{requestId}/reject`

**When to call:** When admin clicks "Reject" and confirms

**Headers required:**
```javascript
{
  "Authorization": "Bearer admin_jwt_token_here",
  "Content-Type": "application/json"
}
```

**What to send:**
```javascript
{
  "reason": "Does not meet our criteria"  // optional but recommended
}
```

**Example call:**
```
POST /AIStudio/api/v1/admin/access-requests/abc-123-def/reject
Body: { "reason": "Does not meet our criteria" }
```

**What you'll get back:**
```javascript
{
  "message": "Access request rejected successfully",
  "requestId": "abc-123-def"
}
```

**What to do:**
- Show success message: "Request rejected"
- Remove the request from the pending list

---

### API 5: Check Request Status (Optional)

**Endpoint:** `GET /AIStudio/api/v1/auth/request-status?email=user@gmail.com`

**When to call:** When user clicks "Check Status" on pending request screen

**No authentication required** (public endpoint)

**Example call:**
```
GET /AIStudio/api/v1/auth/request-status?email=newuser@gmail.com
```

**What you'll get back:**
```javascript
{
  "status": "pending",  // or "approved" or "rejected"
  "requestId": "request-uuid",
  "requestedAt": "2025-10-10T12:00:00Z",
  "reviewedAt": null,
  "message": "Your request is under review"
}
```

**What to do:** Update the status message on screen

---

## Implementation Steps

### Step 1: Update Login Flow

In your existing Google Sign-In handler:

```javascript
async function handleGoogleLogin(googleToken) {
  try {
    const response = await fetch('/AIStudio/api/v1/auth/google/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ google_id_token: googleToken })
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      // User is approved - login successful
      localStorage.setItem('accessToken', result.data.accessToken);
      localStorage.setItem('user', JSON.stringify(result.data.user));
      redirectToDashboard();
    }
    else if (result.status === 'request_created') {
      // New user - show request submitted screen
      showRequestSubmittedScreen(result.data);
    }
    else if (result.status === 'pending') {
      // Existing request pending - show pending screen
      showRequestPendingScreen(result.data);
    }
    else if (result.status === 'rejected') {
      // Request was rejected - show rejection screen
      showRequestRejectedScreen(result.data);
    }
  } catch (error) {
    showErrorMessage('Login failed. Please try again.');
  }
}
```

---

### Step 2: Build Request Submitted Screen

Create a new page/component that shows:
- "Thank you for your interest!"
- User's email
- "Your request has been submitted"
- When it was submitted
- "You'll receive an email when your request is reviewed"
- "Check Status" button

---

### Step 3: Build Request Pending Screen

Similar to submitted screen, but shows:
- "Your request is under review"
- How long ago it was submitted
- "Check Status" button
- Maybe a "Contact Support" option

---

### Step 4: Build Admin Dashboard Section

Add a new section in admin panel:

**Navigation:**
- Add "Access Requests" menu item (only visible if user role is "admin")
- Show badge with count of pending requests

**Main Screen:**
- Fetch and display list of requests
- Implement approve/reject actions
- Add confirmation modals
- Handle success/error states
- Refresh list after actions

---

### Step 5: Add Admin Badge/Notification

In your main navigation/header:
- If user is admin, fetch pending request count
- Show badge: "Access Requests (5)" or just a number badge
- Update count after approving/rejecting

**How to get count:**
```javascript
const response = await fetch('/AIStudio/api/v1/admin/access-requests?status=pending', {
  headers: { 'Authorization': `Bearer ${adminToken}` }
});
const data = await response.json();
const pendingCount = data.total;
```

---

## Error Handling

### Handle These Cases:

**401 Unauthorized:**
- Token expired or invalid
- Log user out, redirect to login

**403 Forbidden:**
- User trying to access admin endpoints without admin role
- Show "Access denied" message

**404 Not Found:**
- Request ID doesn't exist
- Show "Request not found" message

**500 Internal Server Error:**
- Backend error
- Show "Something went wrong, please try again"

---

## Testing Checklist

### Test as New User:
- [ ] Sign in with Google (new email)
- [ ] See request submitted screen
- [ ] Request appears in admin dashboard
- [ ] Sign in again - see pending status
- [ ] After admin approves, can login successfully

### Test as Admin:
- [ ] Sign in with admin account (dineshsunshine@gmail.com)
- [ ] See pending requests count
- [ ] View all pending requests
- [ ] Approve a request - see success message
- [ ] Reject a request - see success message
- [ ] Filter by status (pending/approved/rejected)
- [ ] See empty state when no pending requests

### Test Edge Cases:
- [ ] Network error during request
- [ ] Token expiration during admin actions
- [ ] Multiple admins approving same request
- [ ] User tries to request multiple times
- [ ] Very long rejection reason

---

## URLs Quick Reference

**Backend Base URL:**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio
```

**Authentication:**
```
POST /api/v1/auth/google/
GET  /api/v1/auth/request-status?email={email}
```

**Admin Only (require Authorization header):**
```
GET  /api/v1/admin/access-requests?status=pending&skip=0&limit=20
POST /api/v1/admin/access-requests/{id}/approve
POST /api/v1/admin/access-requests/{id}/reject
```

---

## Sample User Stories

### Story 1: Sarah wants to use the platform
1. Sarah visits the site and clicks "Sign in with Google"
2. She authenticates with her Gmail account
3. The app shows: "Thanks for your interest! Your request has been submitted."
4. She closes the browser
5. Two hours later, admin Dinesh approves her request
6. Sarah opens the site again and signs in
7. She's logged in successfully and can use the platform!

### Story 2: Admin Dinesh reviews requests
1. Dinesh logs in to the admin panel
2. He sees a badge: "Access Requests (3)"
3. He clicks on it and sees three pending requests
4. He reviews the first request from Sarah
5. She provided a good reason, so he clicks "Approve"
6. Selects "User" role and confirms
7. Success message appears and Sarah's request disappears from the list
8. Badge now shows "Access Requests (2)"

---

## Design Mockup Suggestions

### Request Submitted Screen:
```
┌─────────────────────────────────────┐
│                                     │
│         ✓ Request Submitted!        │
│                                     │
│      Hi, Sarah! (profile pic)       │
│      sarah@gmail.com               │
│                                     │
│  Your request has been submitted    │
│  and is under review.               │
│                                     │
│  Submitted: 2 hours ago             │
│                                     │
│  You'll be notified via email when  │
│  your request is reviewed.          │
│                                     │
│     [ Check Status ]                │
│                                     │
└─────────────────────────────────────┘
```

### Admin Dashboard:
```
┌─────────────────────────────────────────────────────────────┐
│  Access Requests                    Pending (3) | Show All   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 👤 Sarah Johnson       sarah@gmail.com              │   │
│  │    Requested 2 hours ago                            │   │
│  │    Reason: "I want to use this for my fashion blog" │   │
│  │                                                       │   │
│  │    [Approve]  [Reject]                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 👤 Mike Chen          mike@gmail.com                │   │
│  │    Requested 5 hours ago                            │   │
│  │    No reason provided                               │   │
│  │                                                       │   │
│  │    [Approve]  [Reject]                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Notes

- **All admin endpoints require authentication**: Always include `Authorization: Bearer {token}` header
- **All endpoints use JSON**: Set `Content-Type: application/json` for POST requests
- **Token expiration**: Access tokens last 24 hours (86400 seconds)
- **CORS is enabled**: You can call from localhost during development
- **Admin account**: dineshsunshine@gmail.com is already set up as admin

---

## Getting Help

If you encounter issues:
1. Check browser console for errors
2. Check network tab to see exact API responses
3. Verify you're using the correct endpoint URLs
4. Verify authorization header is being sent for admin endpoints
5. Check that google_id_token is a fresh token from Google (they expire quickly)

---

## Summary

You're building two main user experiences:

1. **Regular User Flow**: Sign in → Request access → Wait → Get approved → Sign in again → Use platform
2. **Admin Flow**: Sign in → See pending requests → Approve or reject → Request disappears

The backend handles all the logic - you just need to call the right endpoints and show the right screens based on the responses.

Good luck! 🚀


