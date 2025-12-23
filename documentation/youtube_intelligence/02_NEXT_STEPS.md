# Firebase Setup - Next Steps

## ✅ Completed

- [x] Firebase project created: `flourisha-d959a`
- [x] Database schema created in Supabase
- [x] Firebase JWT verification code written (no service account needed!)
- [x] Environment variables configured

## 🚀 Next Steps (5 minutes)

### Step 1: Enable Firebase Authentication

1. Go to [Firebase Console](https://console.firebase.google.com/project/flourisha-d959a)
2. Click **Build** → **Authentication**
3. Click "**Get started**"
4. Enable sign-in methods:
   - ✅ **Email/Password** - Click, toggle "Enable", Save
   - ✅ **Google** - Click, toggle "Enable", Save (optional but recommended)

### Step 2: Get Firebase Web Config

1. In Firebase Console, click the **Settings gear** icon → **Project settings**
2. Scroll down to "**Your apps**" section
3. Click **</>** (Web icon) if no web app exists, or select existing web app
4. If creating new:
   - App nickname: `flourisha-web`
   - ✅ Check "Also set up Firebase Hosting" (optional)
   - Click "Register app"
5. Copy the `firebaseConfig` object:

```javascript
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "flourisha-d959a.firebaseapp.com",
  projectId: "flourisha-d959a",
  storageBucket: "flourisha-d959a.firebasestorage.app",
  messagingSenderId: "664808461264",
  appId: "1:664808461264:web:..."
};
```

6. **Paste the values here:**

```bash
# Update /root/.claude/.env with these values:
FIREBASE_API_KEY=AIza...  # From apiKey
FIREBASE_APP_ID=1:664808461264:web:...  # From appId
```

### Step 3: Test Authentication (Quick)

Once you provide the API key and App ID, I'll create a simple test script to verify everything works.

---

## 📋 Summary

**What we have:**
- ✅ Firebase project: `flourisha-d959a`
- ✅ JWT verification (no service account needed)
- ✅ Database schema ready
- ✅ Multi-tenant RBAC configured

**What we need:**
- ⏳ Enable Firebase Authentication (2 minutes)
- ⏳ Get API Key and App ID (1 minute)
- ⏳ Test authentication flow (2 minutes)

**Then we can build:**
- React web app
- FastAPI backend
- React Native mobile app

---

## Quick Commands

```bash
# View current Firebase config
grep FIREBASE /root/.claude/.env

# Update Firebase API key
nano /root/.claude/.env  # Edit FIREBASE_API_KEY and FIREBASE_APP_ID

# Test Firebase auth (after keys are set)
python /root/flourisha/00_AI_Brain/scripts/youtube_intelligence/test_firebase_auth.py
```

---

**Ready?** Enable Firebase Auth and send me the API key + App ID!
