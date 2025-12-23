# Firebase Setup Guide for Flourisha Content Intelligence

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Project name: `flourisha-content-intelligence`
4. Enable Google Analytics: **Yes** (recommended)
5. Click "Create project"

## Step 2: Enable Firebase Authentication

1. In Firebase Console, go to **Build** → **Authentication**
2. Click "Get started"
3. Enable sign-in methods:
   - ✅ **Email/Password** (required)
   - ✅ **Google** (recommended for mobile)
   - ✅ **Anonymous** (optional, for testing)

## Step 3: Create Service Account

1. Go to **Project Settings** (gear icon) → **Service accounts**
2. Click "Generate new private key"
3. Download JSON file
4. Save as `/root/flourisha/00_AI_Brain/credentials/firebase-service-account.json`
5. **IMPORTANT**: Add to `.gitignore`!

```bash
# Save the file
mv ~/Downloads/flourisha-content-intelligence-*.json /root/flourisha/00_AI_Brain/credentials/firebase-service-account.json

# Set permissions
chmod 600 /root/flourisha/00_AI_Brain/credentials/firebase-service-account.json
```

## Step 4: Get Firebase Config for Web/Mobile

1. In Firebase Console, click **Add app** → **Web** (</> icon)
2. App nickname: `flourisha-web`
3. Copy the config object:

```javascript
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "flourisha-content-intelligence.firebaseapp.com",
  projectId: "flourisha-content-intelligence",
  storageBucket: "flourisha-content-intelligence.firebasestorage.app",
  messagingSenderId: "...",
  appId: "..."
};
```

4. Save to `/root/flourisha/00_AI_Brain/credentials/firebase-web-config.json`

## Step 5: Add Firebase Config to Environment

Add to `/root/.claude/.env`:

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=flourisha-content-intelligence
FIREBASE_SERVICE_ACCOUNT=/root/flourisha/00_AI_Brain/credentials/firebase-service-account.json

# Firebase Web Config (for frontend)
FIREBASE_API_KEY=AIza...
FIREBASE_AUTH_DOMAIN=flourisha-content-intelligence.firebaseapp.com
FIREBASE_STORAGE_BUCKET=flourisha-content-intelligence.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=...
FIREBASE_APP_ID=...
```

## Step 6: Set Custom Claims for Multi-Tenant

Firebase custom claims allow us to add `tenant_id` and `groups` to user tokens.

```python
# This will be automated in the backend
from firebase_admin import auth

# When user signs up, set custom claims
auth.set_custom_user_claims(user_id, {
    'tenant_id': 'cocreators_group',
    'tenant_user_id': 'greg_wasmuth',
    'groups': ['engineering', 'admin']
})
```

## Step 7: Configure Supabase JWT Secret

Supabase needs to validate Firebase JWTs. We'll configure this in the next step.

---

## Security Checklist

- [ ] Service account JSON is in `/root/flourisha/00_AI_Brain/credentials/`
- [ ] Service account JSON has 600 permissions
- [ ] Service account JSON is in `.gitignore`
- [ ] Firebase config is in `.env` file
- [ ] `.env` file is NOT in git
- [ ] Firebase Auth is enabled
- [ ] Custom claims are set for test users

---

## Next Steps

After completing this setup:
1. Run the Supabase configuration script (next doc)
2. Test Firebase Auth → Supabase flow
3. Deploy backend API with Firebase Auth middleware

---

**Created:** 2025-11-21
**Status:** Setup required (manual step)
