# Feature to Route Mapping

Maps ClickUp completed features to testable routes/components.

## Phase 1: Core Infrastructure (P1-01 to P1-15)

| Feature | Route/Component | Test |
|---------|-----------------|------|
| [P1-01] Next.js 14+ | `/` | Homepage loads |
| [P1-02] Chakra UI theme | `*` | Theme colors render |
| [P1-03] TanStack Query | `*` | API calls work |
| [P1-04] API client | `*` | Error handling |
| [P1-05] Firebase Auth | `/login` | Login form, OAuth buttons |
| [P1-06] Protected routes | `/dashboard/*` | Redirect to login if unauthenticated |
| [P1-07] Dashboard layout | `/dashboard` | Sidebar visible |
| [P1-08] Header | `/dashboard` | Workspace switcher in header |
| [P1-09] Navigation | `*` | Nav links work |
| [P1-10] Loading states | `*` | Skeletons appear |
| [P1-11] Error boundaries | `*` | Error page on crash |
| [P1-12] Toast system | `*` | Toasts appear on actions |
| [P1-13] Modal system | `*` | Modals open/close |
| [P1-14] Form validation | `/login`, `/signup` | Validation errors show |
| [P1-15] Theme toggle | `/dashboard` | Light/dark switch |

## Phase 2: Knowledge Features (P2-16 to P2-30)

| Feature | Route/Component | Test |
|---------|-----------------|------|
| [P2-16] Search bar | `/dashboard/search` | Search input exists |
| [P2-17] Search results | `/dashboard/search` | Results list renders |
| [P2-18] Search filters | `/dashboard/search` | Filter buttons work |
| [P2-19] PARA folder tree | `/dashboard/files` | Folder tree renders |
| [P2-20] Folder browser | `/dashboard/files` | Breadcrumbs work |
| [P2-21] File preview | `/dashboard/files` | Preview panel opens |
| [P2-22] Graph container | `/dashboard/knowledge` | Graph canvas exists |
| [P2-23] Graph visualization | `/dashboard/knowledge` | Nodes render |
| [P2-24] Node detail | `/dashboard/knowledge` | Sidebar opens on click |
| [P2-25] Entity filters | `/dashboard/knowledge` | Filter buttons |
| [P2-26] Graph search | `/dashboard/knowledge` | Search within graph |
| [P2-28] Upload dropzone | `/dashboard/ingest` | Dropzone exists |
| [P2-29] Upload progress | `/dashboard/ingest` | Progress bar |
| [P2-30] Document preview | `/dashboard/ingest` | Preview modal |

## Phase 3: Productivity Features (P3-31 to P3-43)

| Feature | Route/Component | Test |
|---------|-----------------|------|
| [P3-31] OKR dashboard | `/dashboard/okrs` | Layout renders |
| [P3-32] Quarter selector | `/dashboard/okrs` | Quarter dropdown |
| [P3-33] Objective cards | `/dashboard/okrs` | Cards with progress |
| [P3-34] Key Results | `/dashboard/okrs` | Progress bars |
| [P3-35] Measurement form | `/dashboard/okrs` | Input form |
| [P3-36] OKR badges | `/dashboard/okrs` | Status badges |
| [P3-38] Energy widget | `/dashboard` | Energy tracker |
| [P3-39] Energy slider | `/dashboard` | Slider input |
| [P3-40] Focus buttons | `/dashboard` | Quality buttons |
| [P3-41] Energy timeline | `/dashboard` | Chart renders |
| [P3-42] Energy forecast | `/dashboard` | Forecast display |
| [P3-43] Morning report | `/dashboard/reports` | Report viewer (IN PROGRESS) |

## Phase 4: Settings & Integrations (P4-44 to P4-60) - NOT YET IMPLEMENTED

These features are pending and should NOT be tested yet:
- Settings pages
- Integration OAuth flows
- System health dashboard
- Notification preferences

## Routes to Test

Based on completed features, these routes should work:

```
/                       # Homepage (P1-01)
/login                  # Login page (P1-05, P1-14)
/dashboard              # Main dashboard (P1-07, P1-08, P3-38 to P3-42)
/dashboard/search       # Search (P2-16 to P2-18)
/dashboard/files        # PARA browser (P2-19 to P2-21)
/dashboard/knowledge    # Knowledge graph (P2-22 to P2-26)
/dashboard/ingest       # Document upload (P2-28 to P2-30)
/dashboard/okrs         # OKR tracking (P3-31 to P3-36)
```

## Generating Test Suite from ClickUp

```bash
# Get completed features
python3 /root/flourisha/00_AI_Brain/scripts/testing/get_testable_features.py --format=json

# Cross-reference with this file to generate test cases
```
