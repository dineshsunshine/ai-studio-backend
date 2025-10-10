# Add Admin User on Render Production

## Quick Steps to Add dineshsunshine@gmail.com as Admin

### Step 1: Update Environment Variable on Render

1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Select your service**: `ai-studio-backend`
3. **Go to "Environment" tab** in the left sidebar
4. **Find or Add** `FIRST_ADMIN_EMAIL`:
   - If it exists: Click "Edit" and change the value
   - If it doesn't exist: Click "Add Environment Variable"
5. **Set the value**:
   ```
   Key: FIRST_ADMIN_EMAIL
   Value: dineshsunshine@gmail.com
   ```
6. **Click "Save Changes"**
7. Render will automatically redeploy (wait ~2-3 minutes)

### Step 2: Run the Initialization Script

After the deployment completes, you need to run the initialization script to create/upgrade the admin user.

**Option A: Using Render Shell (Recommended)**

1. In your Render service dashboard, go to the **"Shell"** tab
2. Click **"Launch Shell"** (this opens a terminal connected to your production server)
3. Run the following command:
   ```bash
   python scripts/init_production_db.py
   ```
4. You should see:
   ```
   👤 Creating admin user: dineshsunshine@gmail.com
   ✅ Admin user created: dineshsunshine@gmail.com
   ```

**Option B: Manual Deploy Command (Alternative)**

If Shell is not available on your plan, you can trigger this via a one-time job:

1. Go to **"Settings"** → **"Restart Service"**
2. The initialization script is already set up to run automatically on startup
3. However, if the user already exists but is not admin, you'll need to manually upgrade them

### Step 3: Verify the Admin User

1. **Login with Google**:
   - Go to your frontend
   - Click "Login with Google"
   - Use `dineshsunshine@gmail.com` to sign in

2. **Check Admin Access**:
   - After login, try accessing admin features
   - Check if you can see the admin panel
   - Try accessing: `https://ai-studio-backend-ijkp.onrender.com/api/v1/admin/users`
   - You should get a list of users (with proper auth token)

---

## Alternative: Manual Database Update (If Script Fails)

If the initialization script doesn't work, you can manually update the database:

### Using Render PostgreSQL Dashboard

1. **Go to Render Dashboard**
2. **Select your PostgreSQL database** (`ai-studio-db`)
3. **Click "Connect"** → Choose "External Connection"
4. Copy the connection string (it looks like):
   ```
   postgres://user:password@host:5432/database
   ```

### Using a SQL Client (like pgAdmin or psql)

Connect to your database and run:

```sql
-- Check if user exists
SELECT id, email, role, status FROM users WHERE email = 'dineshsunshine@gmail.com';

-- If user exists and needs to be upgraded to admin:
UPDATE users 
SET role = 'admin', status = 'active'
WHERE email = 'dineshsunshine@gmail.com';

-- If user doesn't exist, create them:
INSERT INTO users (id, email, full_name, role, status, created_at, updated_at)
VALUES (
    gen_random_uuid()::text,
    'dineshsunshine@gmail.com',
    'Dinesh',
    'admin',
    'active',
    NOW(),
    NOW()
);

-- Verify the update
SELECT id, email, role, status FROM users WHERE email = 'dineshsunshine@gmail.com';
```

---

## Quick Verification Steps

After completing the above:

1. **Test Login**:
   ```bash
   curl -X POST https://ai-studio-backend-ijkp.onrender.com/api/v1/auth/google \
     -H "Content-Type: application/json" \
     -d '{"idToken": "your_google_id_token"}'
   ```
   
   Response should show:
   ```json
   {
     "status": "success",
     "data": {
       "user": {
         "email": "dineshsunshine@gmail.com",
         "role": "admin",
         "status": "active"
       }
     }
   }
   ```

2. **Test Admin Endpoint**:
   ```bash
   curl https://ai-studio-backend-ijkp.onrender.com/api/v1/admin/users \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```
   
   Should return a list of users (not a 403 error).

---

## Troubleshooting

### Issue: User already exists but not admin

**Solution**: Run this SQL:
```sql
UPDATE users 
SET role = 'admin', status = 'active'
WHERE email = 'dineshsunshine@gmail.com';
```

### Issue: User doesn't exist and can't login

**Solution**: The user needs to either:
1. Request access via the frontend (if access request system is enabled)
2. Be manually created in the database (see SQL above)

### Issue: "Access Denied" after login

**Check**:
1. User's `status` is `'active'`
2. User's `role` is `'admin'`
3. JWT token includes the correct role

### Issue: Script says "already exists" but user is not admin

**Run the upgrade**:
```bash
# Connect to Render Shell and run:
python -c "
from app.core.database import SessionLocal
from app.models.user import User, UserRole
db = SessionLocal()
user = db.query(User).filter(User.email == 'dineshsunshine@gmail.com').first()
if user:
    user.role = UserRole.ADMIN
    db.commit()
    print(f'✅ {user.email} upgraded to admin')
else:
    print('❌ User not found')
db.close()
"
```

---

## Summary

**Fastest Path**:
1. Add `FIRST_ADMIN_EMAIL=dineshsunshine@gmail.com` in Render Environment
2. Wait for auto-deploy (~2-3 mins)
3. Open Render Shell
4. Run `python scripts/init_production_db.py`
5. Login via Google with `dineshsunshine@gmail.com`
6. Verify admin access

**Total Time**: ~5 minutes

---

## Notes

- The `FIRST_ADMIN_EMAIL` variable can be changed at any time to add new admins
- Multiple admins can be created by running the script multiple times with different emails
- All admins have full access to admin endpoints (`/api/v1/admin/*`)
- Regular users will have `role = 'user'` instead of `'admin'`

