# Admin Dashboard Deployment Guide

## Quick Start

### 1. Generate Encryption Key (First Time Only)

**On Rocky Linux:**
```bash
cd ~/selfhealing-app

# Generate encryption key
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy the output (e.g., "oK8r3k9F...")

# Add to .env file
echo "ENCRYPTION_KEY=<paste-key-here>" >> .env
```

### 2. Run Database Migration

```bash
# Copy migration file
docker compose exec postgres psql -U selfhealing_user -d selfhealing -f /docker-entrypoint-initdb.d/004_admin_tables.sql

# Or run from Windows:
scp "c:\Users\AlinD\Documents\GitHub\SelfHealing Application\backend\migrations\004_admin_tables.sql" alind@192.168.1.200:/home/alind/selfhealing-app/backend/migrations/

# Then on Rocky Linux:
docker compose exec postgres psql -U selfhealing_user -d selfhealing < backend/migrations/004_admin_tables.sql
```

### 3. Deploy Admin Service

```bash
# Build and start admin-service
docker compose build admin-service
docker compose up -d admin-service

# Check logs
docker compose logs admin-service | tail -20
```

### 4. Deploy Updated Frontend

```bash
# Rebuild frontend with Admin page
docker compose build frontend
docker compose up -d frontend
```

## Testing

### Backend API Tests

```bash
# Get admin token first (login as admin)
TOKEN=$(curl -s -X POST http://192.168.1.200:8006/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

echo "Token: $TOKEN"

# Test: List all users
curl -H "Authorization: Bearer $TOKEN" \
  http://192.168.1.200:8007/users | jq

# Test: Create a new user
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"test123","role":"user","full_name":"Test User"}' \
  http://192.168.1.200:8007/users | jq

# Test: Get system settings
curl -H "Authorization: Bearer $TOKEN" \
  http://192.168.1.200:8007/settings | jq

# Test: Health check
curl http://192.168.1.200:8007/health | jq
```

### Frontend Tests

1. **Login as Admin:**
   - Navigate to: `http://192.168.1.200:3000/login`
   - Username: `admin`
   - Password: `admin123`

2. **Access Admin Dashboard:**
   - Navigate to: `http://192.168.1.200:3000/admin`
   - Should see User Management tab

3. **Test User CRUD:**
   - Click "Create User" button
   - Fill in form and submit
   - Verify new user appears in table
   - Try activating/deactivating a user
   - Try deleting a user

4. **Test Access Control:**
   - Logout
   - Login as a non-admin user (if you created one)
   - Try to access `/admin`
   - Should see "Access Denied" page

## Verification Checklist

- [ ] Admin service starts without errors
- [ ] Database migration completes successfully
- [ ] Encryption key is set in environment
- [ ] Admin dashboard loads at `/admin`
- [ ] User CRUD operations work via API
- [ ] User CRUD operations work via UI
- [ ] Non-admin users cannot access `/admin`
- [ ] Audit logging captures admin actions
- [ ] System settings API works

## Troubleshooting

### Admin Service Won't Start

```bash
# Check logs
docker compose logs admin-service

# Check if encryption key is set
docker compose exec admin-service env | grep ENCRYPTION

# Rebuild without cache
docker compose build --no-cache admin-service
```

### Frontend Shows 404 for Admin Page

```bash
# Rebuild frontend
docker compose build frontend
docker compose up -d frontend

# Clear browser cache and hard refresh (Ctrl+Shift+R)
```

### Database Migration Errors

```bash
# Check if tables already exist
docker compose exec postgres psql -U selfhealing_user -d selfhealing -c "\dt"

# If migration was partial, you may need to drop and recreate tables
# BE CAREFUL: This will delete data!
docker compose exec postgres psql -U selfhealing_user -d selfhealing -c "DROP TABLE IF EXISTS audit_log, ai_settings, integrations, system_settings CASCADE;"
```

## Next Steps

After successful deployment:

1. Configure AI settings (Claude API key)
2. Set up ITSM integrations
3. Customize system settings
4. Create additional admin/operator user accounts
5. Review audit logs

## Files Created

### Backend
- `backend/migrations/004_admin_tables.sql`
- `backend/shared/crypto.py`
- `backend/admin-service/main.py`
- `backend/admin-service/requirements.txt`
- `backend/admin-service/Dockerfile`

### Frontend  
- `frontend/src/pages/Admin.tsx`
- `frontend/src/components/ProtectedRoute.tsx`

### Configuration
- Updated `docker-compose.yml` with admin-service
- Updated `frontend/src/App.tsx` with `/admin` route
