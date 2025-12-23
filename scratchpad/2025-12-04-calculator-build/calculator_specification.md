# Flourisha Calculator Web App - Full Specification

**Project**: Calculator with Calculation History
**Status**: Ready for Implementation
**Date**: 2025-12-04

---

## Value Proposition

A modern, fully functional web calculator that demonstrates complete full-stack integration with persistent history storage. Users can perform calculations, see their calculation history, and have that history survive page refreshes via SQLite database persistence.

---

## Core Features

### Display
- Clean calculator UI with large display screen
- Show current expression being built (e.g., "5 + 3")
- Show calculated result (e.g., "= 8")
- Modern dark theme design
- Responsive layout for desktop and mobile

### Actions
- **Number Buttons** (0-9): Append digit to current expression
- **Operation Buttons** (+, -, *, /): Append operator to expression
- **Equals Button** (=): Calculate result and save to history
- **Clear Button** (C): Reset calculator to 0
- **Delete Button** (←): Remove last character
- **Calculation History Panel**: View all past calculations with timestamps
- **Clear History Button**: Remove all history entries

### Persistence
- All calculations saved to SQLite database
- History survives page refresh
- Each entry shows: expression, result, and timestamp
- History displays newest first

---

## Technical Requirements

### Database Schema

**Table: calculations**
```sql
CREATE TABLE calculations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expression TEXT NOT NULL,
    result FLOAT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Backend API (FastAPI)

**Endpoint 1: POST /api/calculate**
```
Request Body:
{
  "expression": "5 + 3"
}

Response (200):
{
  "expression": "5 + 3",
  "result": 8.0,
  "id": 1,
  "timestamp": "2025-12-04T12:34:56"
}

Response (400):
{
  "error": "Invalid expression: unsupported characters"
}
```

**Endpoint 2: GET /api/history**
```
Response (200):
{
  "history": [
    {
      "id": 3,
      "expression": "10 - 2",
      "result": 8.0,
      "timestamp": "2025-12-04T12:35:00"
    },
    {
      "id": 2,
      "expression": "5 * 2",
      "result": 10.0,
      "timestamp": "2025-12-04T12:34:58"
    },
    {
      "id": 1,
      "expression": "5 + 3",
      "result": 8.0,
      "timestamp": "2025-12-04T12:34:56"
    }
  ]
}
```

**Endpoint 3: DELETE /api/history**
```
Response (200):
{
  "message": "History cleared successfully",
  "deleted_count": 3
}
```

### Frontend Architecture

**Technology Stack**:
- HTML5 + CSS3 (vanilla, no frameworks)
- Vanilla JavaScript (ES6+)
- Fetch API for backend communication

**Components**:
```
Calculator UI
├── Display Screen
│   ├── Expression Area
│   └── Result Area
├── Button Grid
│   ├── Row 1: C, ←, /, *
│   ├── Row 2: 7, 8, 9, -
│   ├── Row 3: 4, 5, 6, +
│   ├── Row 4: 1, 2, 3, =
│   └── Row 5: 0 (wide), .
└── History Panel
    ├── "Clear History" Button
    └── History List
        └── Individual Calculation Items
```

**State Management**:
```javascript
{
  currentExpression: "5 + 3",
  history: [
    { id: 1, expression: "5 + 3", result: 8, timestamp: "..." },
    ...
  ]
}
```

---

## Implementation Details

### Backend Logic (main.py)

```python
# Health check
GET /health → { "status": "healthy", "service": "calculator", "version": "1.0" }

# POST /api/calculate
1. Validate expression (only digits, +, -, *, /, . and spaces allowed)
2. Check for division by zero
3. Use Python's eval() safely with restricted namespace
4. Save calculation to database
5. Return expression, result, id, timestamp

# GET /api/history
1. Query all calculations from database
2. Order by timestamp DESC (newest first)
3. Return as JSON array with all fields

# DELETE /api/history
1. Delete all rows from calculations table
2. Return success message with count deleted
```

### Frontend Logic (index.html)

```javascript
// State
let expression = "0";
let history = [];

// Number button click
function appendDigit(digit) {
  if (expression === "0") expression = digit;
  else expression += digit;
  updateDisplay();
}

// Operation button click
function appendOperator(op) {
  if (!expression.endsWith(" ")) {
    expression += " " + op + " ";
  }
  updateDisplay();
}

// Equals button click
async function calculate() {
  try {
    const response = await fetch("/api/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ expression })
    });
    const result = await response.json();
    expression = result.result.toString();
    await loadHistory();
    updateDisplay();
  } catch (error) {
    showError("Calculation failed");
  }
}

// Clear button click
function clear() {
  expression = "0";
  updateDisplay();
}

// Delete last character
function deleteLast() {
  if (expression.length > 1) {
    expression = expression.slice(0, -1);
  } else {
    expression = "0";
  }
  updateDisplay();
}

// Load history from server
async function loadHistory() {
  const response = await fetch("/api/history");
  history = (await response.json()).history;
  renderHistory();
}

// Clear all history
async function clearHistory() {
  await fetch("/api/history", { method: "DELETE" });
  history = [];
  renderHistory();
}

// Update display
function updateDisplay() {
  document.getElementById("expression").textContent = expression;
  document.getElementById("result").textContent = expression;
}

// Render history list
function renderHistory() {
  const list = document.getElementById("history-list");
  list.innerHTML = history.map(item => `
    <div class="history-item">
      <span class="history-expr">${item.expression}</span>
      <span class="history-result">= ${item.result}</span>
      <span class="history-time">${new Date(item.timestamp).toLocaleTimeString()}</span>
    </div>
  `).join("");
}

// Initialize on page load
window.addEventListener("DOMContentLoaded", () => {
  loadHistory();
  updateDisplay();
});
```

---

## Success Criteria

- [ ] Backend starts on port 8000 without errors
- [ ] Frontend loads on port 5173 without errors
- [ ] Calculator displays with clean, modern UI
- [ ] Number buttons (0-9) append digits correctly
- [ ] Operation buttons (+, -, *, /) append operators
- [ ] Equals button calculates and displays correct result
- [ ] Calculation saves to database and appears in history
- [ ] History panel displays all calculations with timestamps
- [ ] Clear button resets display to 0
- [ ] Clear History button removes all entries
- [ ] History persists after page refresh
- [ ] Public URL accessible from outside sandbox
- [ ] All three layers work: Frontend ↔ Backend ↔ Database

---

## Testing

### Manual Test Flow

1. **Open app in browser**
   - Navigate to public URL
   - Verify calculator UI loads

2. **Test basic calculation**
   - Click: 5 → + → 3 → =
   - Expected: Display shows "8"
   - Expected: History shows "5 + 3 = 8"

3. **Test multiple calculations**
   - Click: 10 → - → 2 → =
   - Expected: Display shows "8"
   - Expected: History shows newest calculation first

4. **Test history persistence**
   - Perform calculation
   - Refresh page
   - Expected: History still shows all calculations

5. **Test clear functions**
   - Click Clear button
   - Expected: Display resets to "0"
   - Click Clear History button
   - Expected: History panel empties

6. **Test edge cases**
   - Division: 10 → / → 2 → = (should show 5)
   - Decimal: 5 → . → 5 → + → 2 → . → 5 → = (should show 8)
   - Negative: 5 → - → 10 → = (should show -5)

### Validation Commands

**Check database**:
```bash
sqlite3 calculator.db "SELECT COUNT(*) as calculations FROM calculations;"
sqlite3 calculator.db "SELECT expression, result FROM calculations ORDER BY id DESC LIMIT 5;"
```

**Check API endpoints**:
```bash
# Health check
curl http://localhost:8000/health

# Get history
curl http://localhost:8000/api/history

# Post calculation
curl -X POST http://localhost:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression":"5 + 3"}'

# Delete history
curl -X DELETE http://localhost:8000/api/history
```

**Check frontend**:
```bash
# Test from outside sandbox
curl -H "Host: calculator.test" https://[PUBLIC_URL]
```

---

## Why This Works

✅ **Simple**: Only basic arithmetic operations, no complex features
✅ **Fast**: Can build in under 1 hour with proper architecture
✅ **Complete**: Tests all three layers (Frontend, Backend, Database)
✅ **Observable**: Easy to verify calculations are mathematically correct
✅ **Practical**: Real-world use case (every app needs calculations)
✅ **Persistent**: Demonstrates database integration and page refresh survival
✅ **Professional**: Modern UI with responsive design
✅ **Testable**: All 13 success criteria are objectively verifiable

---

## UI Design

### Color Scheme
- **Background**: Dark slate (#1e1e1e)
- **Display**: Deep blue (#0d47a1)
- **Buttons**: Light gray (#f5f5f5) with dark text
- **Operations**: Orange (#ff9800) for visibility
- **Equals**: Green (#4caf50) for action emphasis
- **History**: Subtle background (#2a2a2a) with light text

### Typography
- **Display Font**: Monospace (for numbers and expressions)
- **Button Font**: Sans-serif, bold
- **History Font**: Monospace for consistency

### Layout
- **Calculator Width**: 320px (mobile-friendly)
- **Button Grid**: 4 columns × 5 rows
- **History Panel**: 300px width, scrollable (max 300px height)
- **Spacing**: 8px between elements
- **Rounded Corners**: 8px for modern look

### Responsive Design
- Desktop: Calculator left, History right (flexbox row)
- Mobile: Calculator top, History bottom (flexbox column)
- Breakpoint: 768px

---

## Deployment Notes

1. **Database Initialization**
   - Create `calculator.db` in project root
   - Initialize schema on first startup
   - Auto-create if doesn't exist

2. **CORS Configuration**
   - Allow origin: http://localhost:5173 (dev)
   - Allow origin: [PUBLIC_URL] (production)

3. **Static Files**
   - Serve index.html from /static/
   - CSS and JS bundled in single index.html

4. **Error Handling**
   - Invalid expressions: Return 400 with error message
   - Server errors: Return 500 with error message
   - Client errors: Display user-friendly messages

---

## Files to Create

**Backend**:
- `main.py` - FastAPI application with endpoints
- `requirements.txt` - Python dependencies (fastapi, uvicorn)
- `calculator.db` - SQLite database (auto-created)

**Frontend**:
- `index.html` - Single-file app with HTML, CSS, and JavaScript

**Deployment**:
- `README.md` - Setup and run instructions
- `.env` - Database path configuration (optional)

---

**Total Estimated Build Time**: 45 minutes - 1 hour
**Difficulty Level**: Beginner-Friendly
**Testing Complexity**: Low (straightforward validation)

