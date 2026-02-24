# Quick Test Checklist - Insurance Widget

Quick reference for daily testing. See `QUICK_QUOTE_TESTING_PLAN.md` for full details.

## 🚀 Quick Smoke Test (5 minutes)

### Phone-Only State Test
- [ ] MA zip `01760` → Shows phone prompt ☎️
- [ ] No carrier quotes visible
- [ ] Orange "Call Now" button
- [ ] Copy: "We're ready to help you get the best insurance rates in the Natick area"

### Normal State Test
- [ ] CA zip `90210` → Shows 3 carrier quotes
- [ ] Carrier table visible with logos and prices
- [ ] Orange "Continue to Personalized Quote" button
- [ ] Disclaimer text visible at bottom

### Visual Check
- [ ] Mercury logo visible (both states)
- [ ] Button color is orange #e67e50 (both states)
- [ ] No console errors
- [ ] Mobile responsive (resize browser)

---

## 📋 Pre-Release Checklist

Before deploying any changes:

### Critical Tests
- [ ] Test all 3 phone-only states:
  - [ ] MA: `01760` (Natick)
  - [ ] AK: `99501` (Anchorage)
  - [ ] HI: `96813` (Honolulu)
- [ ] Test 3 normal states:
  - [ ] CA: `90210` (Beverly Hills)
  - [ ] TX: `75001` (Dallas)
  - [ ] NY: `10001` (Manhattan)

### UI Verification
- [ ] Button colors correct (orange)
- [ ] Phone section styled correctly (white box, border)
- [ ] Carrier table styled correctly (rows, logos)
- [ ] Loading skeleton → content transition smooth

### Backend Verification
```bash
# Test state normalization
python3 -c "
from insurance_server_python.carrier_mapping import get_carriers_for_state
print('MA carriers:', get_carriers_for_state('MA'))
print('CA carriers:', get_carriers_for_state('CA'))
"
```
Expected: MA = `[]`, CA = `[carriers list]`

---

## 🐛 Known Issues Checklist

If you see these, check:

**Issue**: Carriers showing for MA
- [ ] Backend: `carrier_mapping.py` returns `[]` for MA
- [ ] Frontend: State in phone-only list
- [ ] Frontend: Carriers forced to empty for phone-only states

**Issue**: Wrong button color (green instead of orange)
- [ ] Check line ~455: `style.background = "#e67e50"`

**Issue**: Wrong state name format
- [ ] Backend normalizes to abbreviation: `state_abbreviation(state)`
- [ ] Frontend checks both formats: `["MA", "Massachusetts"]`

---

## 📱 Test Zips Reference

### Phone-Only States (No Quotes)
| State | Zip Code | City |
|-------|----------|------|
| MA | 01760 | Natick |
| MA | 02108 | Boston |
| AK | 99501 | Anchorage |
| HI | 96813 | Honolulu |

### Normal States (Show Quotes)
| State | Zip Code | City | Expected Carriers |
|-------|----------|------|-------------------|
| CA | 90210 | Beverly Hills | Progressive, Mercury, National General |
| TX | 75001 | Dallas | Geico, Progressive, Mercury |
| FL | 33139 | Miami | Geico, Progressive, Mercury |
| NY | 10001 | Manhattan | Progressive, Mercury |

---

## 🔧 Quick Fixes

### Restart Server
```bash
lsof -ti:8000 | xargs kill
source .venv/bin/activate
uvicorn insurance_server_python.main:app --port 8000
```

### Check Server Logs
```bash
tail -f server.log | grep -E "(MA|get-enhanced-quick-quote|carriers)"
```

### Test State Logic
```bash
node << 'EOF'
const phoneOnlyStates = ["AK", "HI", "MA", "Alaska", "Hawaii", "Massachusetts"];
console.log("MA:", phoneOnlyStates.includes("MA"));
console.log("Massachusetts:", phoneOnlyStates.includes("Massachusetts"));
EOF
```

---

## ✅ Success Criteria

**Must have** before marking as complete:
- ✅ MA/AK/HI show phone prompt (not carriers)
- ✅ All buttons are orange
- ✅ Phone section has clean styling (white box)
- ✅ Carrier table shows for normal states
- ✅ No console errors
- ✅ Mobile responsive

**Last verified**: _____________
**Verified by**: _____________
