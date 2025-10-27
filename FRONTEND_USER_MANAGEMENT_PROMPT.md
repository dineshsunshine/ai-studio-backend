# Frontend Implementation Guide: User Management Tab

## Overview

We need to build a User Management tab where admins can view all registered users, update their roles and status, and delete users if needed.

---

## What You're Building

A complete user management dashboard for admins with:
- **View all users** in a table/list format
- **Filter users** by role (Admin/User) and status (Active/Suspended)
- **Search users** by email or name
- **Update user roles** (promote to admin or demote to user)
- **Change user status** (activate or suspend users)
- **Delete users** (with confirmation)
- **Pagination** for large user lists

---

## User Interface Components

### Component 1: User Management Tab/Page

**When to show:** Only visible when logged-in user has `role: "admin"`

**Layout Structure:**

```
┌─────────────────────────────────────────────────────────────────┐
│  USER MANAGEMENT                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Filters: [All Roles ▼] [All Status ▼]    Search: [_________🔍] │
│                                                                   │
│  Showing 8 of 8 users                                            │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  USER           EMAIL                ROLE    STATUS      │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │  👤 Dinesh      dineshsunshine@     Admin   ● Active     │   │
│  │     Golani      gmail.com                                │   │
│  │                 Joined: Oct 10                           │   │
│  │                 Last login: 2 hours ago                  │   │
│  │                                                           │   │
│  │  👤 Charu       golanicharu@        User    ● Active     │   │
│  │     Jindal      gmail.com                    [Edit] [🗑]  │   │
│  │                 Joined: Oct 10                           │   │
│  │                 Last login: Never                        │   │
│  │                                                           │   │
│  │  👤 Sarah       sarah@gmail.com     User    ● Active     │   │
│  │     Johnson                                  [Edit] [🗑]  │   │
│  │                 Joined: Oct 9                            │   │
│  │                 Last login: 1 day ago                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│                         [← Previous] [Next →]                    │
└─────────────────────────────────────────────────────────────────┘
```

---

### Component 2: Edit User Modal

**Triggered by:** Clicking "Edit" button on a user row

**What to display:**

```
┌──────────────────────────────────────┐
│  Edit User                         ✕ │
├──────────────────────────────────────┤
│                                      │
│  👤 Sarah Johnson                    │
│     sarah@gmail.com                  │
│                                      │
│  Role:                               │
│  ○ User                              │
│  ○ Admin                             │
│                                      │
│  Status:                             │
│  ○ Active (can login)                │
│  ○ Suspended (blocked from login)    │
│                                      │
│           [Cancel]  [Save Changes]   │
└──────────────────────────────────────┘
```

**Fields:**
- **Role:** Radio buttons for "User" or "Admin"
- **Status:** Radio buttons for "Active" or "Suspended"
- Show user's profile picture, name, and email (read-only)

---

### Component 3: Delete User Confirmation Modal

**Triggered by:** Clicking delete (🗑) button on a user row

**What to display:**

```
┌──────────────────────────────────────┐
│  ⚠️  Delete User                      │
├──────────────────────────────────────┤
│                                      │
│  Are you sure you want to delete     │
│  this user?                          │
│                                      │
│  👤 Sarah Johnson                    │
│     sarah@gmail.com                  │
│                                      │
│  ⚠️  This action cannot be undone.   │
│     All their data (models, looks)   │
│     will also be deleted.            │
│                                      │
│           [Cancel]  [Delete User]    │
└──────────────────────────────────────┘
```

**Delete button should be red/destructive color**

---

## API Integration Details

### API 1: Get All Users (List)

**Endpoint:** `GET /AIStudio/api/v1/admin/users`

**When to call:** 
- When admin opens User Management tab
- After updating or deleting a user (to refresh the list)
- When changing filters or pagination

**Headers required:**
```javascript
{
  "Authorization": "Bearer admin_jwt_token_here"
}
```

**Query Parameters (all optional):**
- `role` - Filter by role: "user" or "admin"
- `status` - Filter by status: "active" or "suspended"
- `skip` - For pagination (default: 0)
- `limit` - Number per page (default: 20, max: 100)

**Example API calls:**

**Get all users (first page):**
```
GET /AIStudio/api/v1/admin/users?skip=0&limit=20
```

**Get only admin users:**
```
GET /AIStudio/api/v1/admin/users?role=admin&skip=0&limit=20
```

**Get only active users:**
```
GET /AIStudio/api/v1/admin/users?status=active&skip=0&limit=20
```

**Get suspended admin users:**
```
GET /AIStudio/api/v1/admin/users?role=admin&status=suspended
```

**Second page (if more than 20 users):**
```
GET /AIStudio/api/v1/admin/users?skip=20&limit=20
```

**What you'll get back:**

```javascript
{
  "users": [
    {
      "id": "a85d3356-0869-495d-86aa-210a92337ffd",
      "email": "dineshsunshine@gmail.com",
      "fullName": "Dinesh Golani",
      "profilePicture": "https://lh3.googleusercontent.com/a/...",
      "role": "admin",
      "status": "active",
      "createdAt": "2025-10-10T08:00:00Z",
      "lastLogin": "2025-10-10T12:30:00Z"
    },
    {
      "id": "user-uuid-2",
      "email": "sarah@gmail.com",
      "fullName": "Sarah Johnson",
      "profilePicture": "https://lh3.googleusercontent.com/a/...",
      "role": "user",
      "status": "active",
      "createdAt": "2025-10-09T14:20:00Z",
      "lastLogin": "2025-10-09T18:45:00Z"
    },
    {
      "id": "user-uuid-3",
      "email": "blocked@gmail.com",
      "fullName": "Blocked User",
      "profilePicture": "https://lh3.googleusercontent.com/a/...",
      "role": "user",
      "status": "suspended",
      "createdAt": "2025-10-08T10:15:00Z",
      "lastLogin": null  // Never logged in or null if no login yet
    }
  ],
  "total": 15,     // Total number of users matching the filter
  "skip": 0,       // Current offset
  "limit": 20      // Items per page
}
```

**What to do with this data:**
- Display users in a table/list
- Show total count: "Showing X of Y users"
- Calculate pagination: `totalPages = Math.ceil(total / limit)`
- Format dates nicely (e.g., "2 hours ago", "Oct 10, 2025")
- Show "Never" if `lastLogin` is null
- Apply visual indicators for status (green dot for active, red for suspended)
- Apply visual indicators for role (badge or icon for admin)

---

### API 2: Update User Role or Status

**Endpoint:** `PATCH /AIStudio/api/v1/admin/users/{userId}`

**When to call:** When admin clicks "Save Changes" in Edit User modal

**Headers required:**
```javascript
{
  "Authorization": "Bearer admin_jwt_token_here",
  "Content-Type": "application/json"
}
```

**What to send (at least one field is required):**

```javascript
{
  "role": "admin",      // or "user" - OPTIONAL
  "status": "active"    // or "suspended" - OPTIONAL
}
```

**Example API calls:**

**Change user to admin:**
```
PATCH /AIStudio/api/v1/admin/users/user-uuid-123
Body: { "role": "admin" }
```

**Suspend a user:**
```
PATCH /AIStudio/api/v1/admin/users/user-uuid-123
Body: { "status": "suspended" }
```

**Change role AND status at once:**
```
PATCH /AIStudio/api/v1/admin/users/user-uuid-123
Body: { "role": "user", "status": "active" }
```

**What you'll get back (success):**

```javascript
{
  "id": "user-uuid-123",
  "email": "sarah@gmail.com",
  "fullName": "Sarah Johnson",
  "profilePicture": "https://lh3.googleusercontent.com/a/...",
  "role": "admin",        // Updated role
  "status": "active",     // Updated status
  "createdAt": "2025-10-09T14:20:00Z",
  "lastLogin": "2025-10-09T18:45:00Z"
}
```

**What to do:**
- Close the Edit User modal
- Show success message: "User updated successfully!"
- Refresh the user list to show updated information
- Update the user row in the table without full reload (optional optimization)

**Error Cases:**

**404 - User not found:**
```javascript
{
  "detail": "User not found"
}
```
→ Show error: "User not found. They may have been deleted."

**400 - Cannot modify yourself:**
```javascript
{
  "detail": "You cannot modify your own account"
}
```
→ Show error: "You cannot edit your own account"

**400 - Invalid role/status:**
```javascript
{
  "detail": "Invalid role: superadmin"
}
```
→ Show error: "Invalid role or status provided"

---

### API 3: Delete User

**Endpoint:** `DELETE /AIStudio/api/v1/admin/users/{userId}`

**When to call:** When admin confirms deletion in the Delete User modal

**Headers required:**
```javascript
{
  "Authorization": "Bearer admin_jwt_token_here"
}
```

**No request body needed**

**Example API call:**

```
DELETE /AIStudio/api/v1/admin/users/user-uuid-123
```

**What you'll get back (success):**

```javascript
{
  "message": "User deleted successfully"
}
```

**What to do:**
- Close the Delete User modal
- Show success message: "User deleted successfully"
- Refresh the user list to remove the deleted user
- If you're on the last item of a page, go back to previous page

**Error Cases:**

**404 - User not found:**
```javascript
{
  "detail": "User not found"
}
```
→ Show error: "User not found. They may already be deleted."

**400 - Cannot delete yourself:**
```javascript
{
  "detail": "You cannot delete your own account"
}
```
→ Show error: "You cannot delete your own account"

---

## Implementation Steps

### Step 1: Create User Management Tab

**In your admin navigation/sidebar:**

```javascript
// Only show this menu item if user is admin
if (currentUser.role === 'admin') {
  menuItems.push({
    label: 'User Management',
    icon: '👥',
    path: '/admin/users'
  });
}
```

---

### Step 2: Build User List Component

**Fetch and display users:**

```javascript
async function fetchUsers(filters = {}) {
  const { role, status, skip = 0, limit = 20 } = filters;
  
  // Build query string
  const params = new URLSearchParams();
  if (role) params.append('role', role);
  if (status) params.append('status', status);
  params.append('skip', skip);
  params.append('limit', limit);
  
  try {
    const response = await fetch(
      `/AIStudio/api/v1/admin/users?${params}`,
      {
        headers: {
          'Authorization': `Bearer ${adminToken}`
        }
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch users');
    }
    
    const data = await response.json();
    
    // Display users
    displayUserList(data.users);
    
    // Update pagination
    updatePagination(data.total, data.skip, data.limit);
    
    // Update count
    document.getElementById('userCount').textContent = 
      `Showing ${data.users.length} of ${data.total} users`;
      
  } catch (error) {
    showErrorMessage('Failed to load users. Please try again.');
  }
}
```

---

### Step 3: Implement Filters

**Filter dropdowns:**

```javascript
// Role filter dropdown
<select id="roleFilter" onchange="applyFilters()">
  <option value="">All Roles</option>
  <option value="user">User</option>
  <option value="admin">Admin</option>
</select>

// Status filter dropdown
<select id="statusFilter" onchange="applyFilters()">
  <option value="">All Status</option>
  <option value="active">Active</option>
  <option value="suspended">Suspended</option>
</select>

// Apply filters
function applyFilters() {
  const role = document.getElementById('roleFilter').value;
  const status = document.getElementById('statusFilter').value;
  
  fetchUsers({ role, status, skip: 0 });
}
```

---

### Step 4: Implement Search (Client-Side)

**Search by email or name:**

```javascript
let allUsers = []; // Store all fetched users

function searchUsers(searchTerm) {
  const filtered = allUsers.filter(user => 
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.fullName.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  displayUserList(filtered);
}

// Search input
<input 
  type="text" 
  placeholder="Search by email or name..."
  oninput="searchUsers(this.value)"
/>
```

---

### Step 5: Build Edit User Modal

**Show modal when Edit is clicked:**

```javascript
function openEditUserModal(user) {
  // Prevent editing yourself
  if (user.id === currentUser.id) {
    showErrorMessage("You cannot edit your own account");
    return;
  }
  
  // Populate modal with user data
  document.getElementById('editUserName').textContent = user.fullName;
  document.getElementById('editUserEmail').textContent = user.email;
  document.getElementById('editUserPicture').src = user.profilePicture;
  
  // Set current role
  document.getElementById(`roleRadio_${user.role}`).checked = true;
  
  // Set current status
  document.getElementById(`statusRadio_${user.status}`).checked = true;
  
  // Store user ID for update
  document.getElementById('editUserModal').dataset.userId = user.id;
  
  // Show modal
  showModal('editUserModal');
}
```

**Handle save:**

```javascript
async function saveUserChanges() {
  const userId = document.getElementById('editUserModal').dataset.userId;
  
  // Get selected values
  const role = document.querySelector('input[name="role"]:checked').value;
  const status = document.querySelector('input[name="status"]:checked').value;
  
  try {
    const response = await fetch(
      `/AIStudio/api/v1/admin/users/${userId}`,
      {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ role, status })
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update user');
    }
    
    const updatedUser = await response.json();
    
    // Close modal
    closeModal('editUserModal');
    
    // Show success
    showSuccessMessage('User updated successfully!');
    
    // Refresh user list
    fetchUsers();
    
  } catch (error) {
    showErrorMessage(error.message);
  }
}
```

---

### Step 6: Build Delete User Modal

**Show confirmation modal:**

```javascript
function openDeleteUserModal(user) {
  // Prevent deleting yourself
  if (user.id === currentUser.id) {
    showErrorMessage("You cannot delete your own account");
    return;
  }
  
  // Populate modal with user data
  document.getElementById('deleteUserName').textContent = user.fullName;
  document.getElementById('deleteUserEmail').textContent = user.email;
  document.getElementById('deleteUserPicture').src = user.profilePicture;
  
  // Store user ID for deletion
  document.getElementById('deleteUserModal').dataset.userId = user.id;
  
  // Show modal
  showModal('deleteUserModal');
}
```

**Handle deletion:**

```javascript
async function confirmDeleteUser() {
  const userId = document.getElementById('deleteUserModal').dataset.userId;
  
  try {
    const response = await fetch(
      `/AIStudio/api/v1/admin/users/${userId}`,
      {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${adminToken}`
        }
      }
    );
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete user');
    }
    
    const result = await response.json();
    
    // Close modal
    closeModal('deleteUserModal');
    
    // Show success
    showSuccessMessage(result.message);
    
    // Refresh user list
    fetchUsers();
    
  } catch (error) {
    showErrorMessage(error.message);
  }
}
```

---

### Step 7: Implement Pagination

**Navigation buttons:**

```javascript
let currentPage = 0;
const itemsPerPage = 20;

function nextPage() {
  currentPage++;
  fetchUsers({ skip: currentPage * itemsPerPage, limit: itemsPerPage });
}

function previousPage() {
  if (currentPage > 0) {
    currentPage--;
    fetchUsers({ skip: currentPage * itemsPerPage, limit: itemsPerPage });
  }
}

function updatePagination(total, skip, limit) {
  const totalPages = Math.ceil(total / limit);
  currentPage = Math.floor(skip / limit);
  
  // Enable/disable buttons
  document.getElementById('prevBtn').disabled = (currentPage === 0);
  document.getElementById('nextBtn').disabled = (currentPage >= totalPages - 1);
  
  // Show current page
  document.getElementById('pageInfo').textContent = 
    `Page ${currentPage + 1} of ${totalPages}`;
}
```

---

## Visual Design Suggestions

### User List Table/Card Design:

**Each user row should show:**
- ✅ Profile picture (circular)
- ✅ Full name (bold)
- ✅ Email (smaller, gray text)
- ✅ Role badge ("Admin" in blue/purple, "User" in gray)
- ✅ Status indicator (green dot + "Active" or red dot + "Suspended")
- ✅ Join date ("Joined: Oct 10")
- ✅ Last login ("Last login: 2 hours ago" or "Never")
- ✅ Action buttons (Edit icon, Delete icon) - hide for current user

**Color coding:**
- Admin role: Blue/purple badge
- User role: Gray badge
- Active status: Green dot
- Suspended status: Red dot
- Your own account: Maybe a light yellow background or "You" label

---

### Modal Design Tips:

**Edit User Modal:**
- Clean, centered modal
- User info at top (read-only)
- Clear radio button groups
- Helpful labels ("can login" / "blocked from login")
- Primary color for Save button

**Delete Modal:**
- Red accent color for danger
- Warning icon (⚠️)
- Clear consequences message
- Red/destructive Delete button
- Easy-to-find Cancel button

---

## User Stories

### Story 1: Admin promotes a user to admin role

1. Admin opens "User Management" tab
2. Sees list of all users
3. Finds "Sarah Johnson" in the list
4. Clicks "Edit" next to her name
5. Modal opens showing her current role (User) and status (Active)
6. Admin selects "Admin" radio button
7. Clicks "Save Changes"
8. Modal closes, success message appears
9. Sarah's row now shows "Admin" badge
10. Sarah can now access admin features when she logs in

---

### Story 2: Admin suspends a problematic user

1. Admin opens "User Management" tab
2. Uses search to find user by email: "spammer@gmail.com"
3. Clicks "Edit" next to the user
4. Modal opens
5. Admin selects "Suspended" status
6. Clicks "Save Changes"
7. User's row now shows red dot + "Suspended"
8. That user can no longer log in
9. If they try to log in, they see "Your account has been suspended"

---

### Story 3: Admin deletes a user permanently

1. Admin opens "User Management" tab
2. Filters by "Suspended" status to see blocked users
3. Finds a user they want to completely remove
4. Clicks delete (🗑) icon
5. Confirmation modal appears with warning
6. Admin reads: "All their data (models, looks) will also be deleted"
7. Admin clicks "Delete User"
8. User is removed from the list
9. All their models and looks are also deleted from database

---

### Story 4: Admin reviews all admin users

1. Admin opens "User Management" tab
2. Selects "Admin" from role filter dropdown
3. List shows only admin users
4. Admin sees: Dinesh Golani, Sarah Johnson
5. Reviews who has admin access
6. Decides to demote Sarah back to regular user
7. Clicks Edit, changes role to "User", saves
8. Sarah disappears from the filtered view (since we're filtering by Admin)
9. Admin changes filter back to "All Roles"
10. Now sees Sarah as a regular user

---

## Error Handling

### Handle These Cases:

**401 Unauthorized:**
- Token expired
→ Log admin out, redirect to login

**403 Forbidden:**
- User is not an admin
→ Show "Access denied" and redirect to home

**404 Not Found:**
- User was deleted by another admin
→ Show "User not found" and refresh list

**400 Bad Request:**
- Trying to edit/delete yourself
→ Show specific error message
- Invalid role/status value
→ Show "Invalid data" error

**500 Internal Server Error:**
- Backend error
→ Show "Something went wrong, please try again"

**Network Error:**
- No internet connection
→ Show "Connection lost. Please check your internet."

---

## Testing Checklist

### Test as Admin:
- [ ] Open User Management tab - see all users
- [ ] Filter by Role (Admin only) - see only admins
- [ ] Filter by Role (User only) - see only regular users
- [ ] Filter by Status (Active) - see only active users
- [ ] Filter by Status (Suspended) - see only suspended users
- [ ] Search by email - find correct user
- [ ] Search by name - find correct user
- [ ] Edit a user's role - save successfully
- [ ] Edit a user's status - save successfully
- [ ] Edit both role and status - save successfully
- [ ] Try to edit yourself - see error message
- [ ] Delete a user - see confirmation modal
- [ ] Confirm deletion - user is removed
- [ ] Try to delete yourself - see error message
- [ ] Pagination works (if > 20 users)
- [ ] Click Next/Previous - loads correct page

### Test Edge Cases:
- [ ] User list empty state - shows "No users found"
- [ ] Network error during fetch - shows error message
- [ ] Token expired during update - redirects to login
- [ ] Another admin deletes user you're editing - shows not found
- [ ] Update fails - error message shown, modal stays open
- [ ] Delete fails - error message shown, modal stays open
- [ ] Very long user name - UI doesn't break
- [ ] User with no profile picture - shows placeholder
- [ ] User who never logged in - shows "Never" for last login

---

## URLs Quick Reference

**Backend Base URL:**
```
https://zestfully-chalky-nikia.ngrok-free.dev/AIStudio
```

**Admin User Management Endpoints:**
```
GET    /api/v1/admin/users                  - List all users
GET    /api/v1/admin/users?role=admin        - List only admins
GET    /api/v1/admin/users?status=active     - List only active users
PATCH  /api/v1/admin/users/{userId}          - Update user role/status
DELETE /api/v1/admin/users/{userId}          - Delete user
```

---

## Additional Features (Optional)

### Feature 1: Bulk Actions
- Checkbox for each user
- "Select All" checkbox
- Bulk suspend selected users
- Bulk delete selected users

### Feature 2: Export Users
- "Export CSV" button
- Downloads list of all users
- Includes email, name, role, status, join date

### Feature 3: User Activity Log
- Show last login time
- Show number of models created
- Show number of looks created
- Click to view user's content

### Feature 4: Quick Stats
- Total users count
- Active users count
- Suspended users count
- Admin users count
- New users this week

---

## Sample HTML Structure

```html
<!-- User Management Page -->
<div id="userManagement" class="admin-page">
  
  <!-- Header -->
  <div class="page-header">
    <h1>User Management</h1>
  </div>
  
  <!-- Filters & Search -->
  <div class="filters-bar">
    <div class="filters">
      <select id="roleFilter" onchange="applyFilters()">
        <option value="">All Roles</option>
        <option value="user">User</option>
        <option value="admin">Admin</option>
      </select>
      
      <select id="statusFilter" onchange="applyFilters()">
        <option value="">All Status</option>
        <option value="active">Active</option>
        <option value="suspended">Suspended</option>
      </select>
    </div>
    
    <div class="search-box">
      <input 
        type="text" 
        placeholder="Search by email or name..." 
        oninput="searchUsers(this.value)"
      />
    </div>
  </div>
  
  <!-- User Count -->
  <div id="userCount" class="count-display">
    Showing 8 of 8 users
  </div>
  
  <!-- User List -->
  <div id="userList" class="user-list">
    <!-- User items will be inserted here -->
  </div>
  
  <!-- Pagination -->
  <div class="pagination">
    <button id="prevBtn" onclick="previousPage()">← Previous</button>
    <span id="pageInfo">Page 1 of 1</span>
    <button id="nextBtn" onclick="nextPage()">Next →</button>
  </div>
  
</div>

<!-- Edit User Modal -->
<div id="editUserModal" class="modal">
  <div class="modal-content">
    <h2>Edit User</h2>
    
    <div class="user-info">
      <img id="editUserPicture" class="profile-pic" />
      <div>
        <div id="editUserName" class="name"></div>
        <div id="editUserEmail" class="email"></div>
      </div>
    </div>
    
    <div class="form-group">
      <label>Role:</label>
      <label>
        <input type="radio" name="role" value="user" id="roleRadio_user" />
        User
      </label>
      <label>
        <input type="radio" name="role" value="admin" id="roleRadio_admin" />
        Admin
      </label>
    </div>
    
    <div class="form-group">
      <label>Status:</label>
      <label>
        <input type="radio" name="status" value="active" id="statusRadio_active" />
        Active (can login)
      </label>
      <label>
        <input type="radio" name="status" value="suspended" id="statusRadio_suspended" />
        Suspended (blocked from login)
      </label>
    </div>
    
    <div class="modal-actions">
      <button onclick="closeModal('editUserModal')">Cancel</button>
      <button onclick="saveUserChanges()" class="primary">Save Changes</button>
    </div>
  </div>
</div>

<!-- Delete User Modal -->
<div id="deleteUserModal" class="modal">
  <div class="modal-content">
    <h2>⚠️ Delete User</h2>
    
    <p>Are you sure you want to delete this user?</p>
    
    <div class="user-info">
      <img id="deleteUserPicture" class="profile-pic" />
      <div>
        <div id="deleteUserName" class="name"></div>
        <div id="deleteUserEmail" class="email"></div>
      </div>
    </div>
    
    <div class="warning">
      ⚠️ This action cannot be undone.
      All their data (models, looks) will also be deleted.
    </div>
    
    <div class="modal-actions">
      <button onclick="closeModal('deleteUserModal')">Cancel</button>
      <button onclick="confirmDeleteUser()" class="danger">Delete User</button>
    </div>
  </div>
</div>
```

---

## Notes

- **All endpoints require admin authentication**: Always include `Authorization: Bearer {token}` header
- **Cannot modify yourself**: Backend prevents admins from editing or deleting their own account
- **Suspended users cannot login**: When status is "suspended", login will fail
- **All endpoints use JSON**: Set `Content-Type: application/json` for PATCH requests
- **Pagination defaults**: skip=0, limit=20 (you can omit these for defaults)
- **CORS is enabled**: You can call from localhost during development

---

## Getting Help

If you encounter issues:
1. Check browser console for errors
2. Check network tab to see exact API responses
3. Verify you're using the correct endpoint URLs
4. Verify authorization header is being sent (admin token)
5. Check that you're not trying to edit/delete yourself
6. Ensure role values are exactly "user" or "admin" (lowercase)
7. Ensure status values are exactly "active" or "suspended" (lowercase)

---

## Summary

You're building a user management dashboard where admins can:

1. **View all users** with their details (email, name, role, status, etc.)
2. **Filter users** by role (admin/user) and status (active/suspended)
3. **Search users** by email or name
4. **Edit users** to change their role or status
5. **Delete users** permanently with confirmation
6. **Navigate** through pages if there are many users

The backend handles all validation and prevents admins from modifying themselves. You just need to call the right endpoints and show the right UI based on the responses.

Good luck! 🚀


