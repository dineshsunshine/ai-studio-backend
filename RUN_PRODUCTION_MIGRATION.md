# Production Database Migration Guide

## Issue
The production database has old column names (`client_name`, `client_phone`) but the code expects new ones (`title`, `description`).

## Error
```
psycopg2.errors.UndefinedColumn: column links.title does not exist
```

## Solution

### Option 1: Run Migration Script Locally (Recommended)

**Prerequisites:**
- Make sure your `.env` file has the production `DATABASE_URL` temporarily

**Steps:**

1. **Backup current .env file:**
   ```bash
   cd /Users/dgolani/Documents/AI_Studio/backend
   cp .env .env.backup
   ```

2. **Update .env with production DATABASE_URL:**
   ```bash
   # Open .env and temporarily change DATABASE_URL to your Render PostgreSQL URL
   # It should look like:
   # DATABASE_URL=postgresql://user:password@hostname/database
   ```

3. **Run the migration:**
   ```bash
   python scripts/migrate_links_production.py
   ```

4. **Restore local .env:**
   ```bash
   mv .env.backup .env
   ```

### Option 2: Run via Render Shell (Paid Plan Only)

If you have access to Render shell:

```bash
# In Render shell
cd /opt/render/project/src
python scripts/migrate_links_production.py
```

### Option 3: Create a Temporary Migration Endpoint

We can create a one-time admin endpoint that runs the migration when called.

## What the Migration Does

1. ✅ Renames `client_name` → `title`
2. ✅ Renames `client_phone` → `description`  
3. ✅ Makes `description` nullable
4. ✅ Safe to run multiple times (checks state first)
5. ✅ Works with PostgreSQL (production)

## Verification

After migration, the script will show:
- Column states before/after
- Total number of links migrated

## Need Help?

Let me know which option you prefer, or if you'd like me to create a temporary admin migration endpoint.

