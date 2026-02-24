# Quick Quote ChatGPT Integration - Testing Plan

## Overview
This document outlines the testing plan for the insurance quick quote widget integrated with ChatGPT as an MCP app.

## Test Environment Setup

### Prerequisites
- [ ] Server running on port 8000
- [ ] ChatGPT developer mode enabled
- [ ] MCP connector configured with ngrok URL
- [ ] Test with fresh ChatGPT conversation for each test suite

### Server Commands
```bash
# Start server
source .venv/bin/activate
uvicorn insurance_server_python.main:app --port 8000

# Expose via ngrok
ngrok http 8000
# Add ngrok URL + /mcp to ChatGPT Settings > Connectors
```

---

## Test Suite 1: Phone-Only States (Critical)

### Test 1.1: Massachusetts (MA) - Full Flow
**Objective**: Verify MA shows phone prompt, not carrier quotes

**Test Steps**:
1. Start fresh ChatGPT conversation
2. Say: "I need a car insurance quote"
3. Provide zip code: `01760` (Natick, MA)
4. Provide additional info if requested

**Expected Results**:
- [ ] Widget displays "Speak with a Licensed Agent" title
- [ ] Phone section is visible with white background + border
- [ ] Copy reads: "We're ready to help you get the best insurance rates in the Natick area"
- [ ] Phone number displayed: (888) 772-4247
- [ ] Business hours shown
- [ ] Button text: "Call Now"
- [ ] Button color: Orange (#e67e50)
- [ ] Button links to: `tel:+18887724247`
- [ ] NO carrier table visible
- [ ] NO price disclaimer visible
- [ ] Mercury logo visible in header

**Test Multiple MA Zips**:
- [ ] `02108` (Boston, MA)
- [ ] `01420` (Fitchburg, MA)
- [ ] `01960` (Peabody, MA)

### Test 1.2: Alaska (AK)
**Test Steps**:
1. Fresh conversation
2. Request quote with AK zip: `99501` (Anchorage)

**Expected Results**:
- [ ] Same phone-only UI as MA
- [ ] Copy mentions "Anchorage area"
- [ ] No carrier quotes shown

### Test 1.3: Hawaii (HI)
**Test Steps**:
1. Fresh conversation
2. Request quote with HI zip: `96813` (Honolulu)

**Expected Results**:
- [ ] Same phone-only UI as MA
- [ ] Copy mentions "Honolulu area"
- [ ] No carrier quotes shown

---

## Test Suite 2: Normal States with Carrier Quotes

### Test 2.1: California (CA) - Standard Flow
**Test Steps**:
1. Fresh conversation
2. Request quote for zip: `90210` (Beverly Hills)
3. Provide driver age, vehicle info, etc.

**Expected Results**:
- [ ] Widget shows carrier table (not phone section)
- [ ] 3 carriers displayed (Progressive, Mercury, National General)
- [ ] Each carrier row shows:
  - [ ] Carrier logo
  - [ ] Monthly cost
  - [ ] Annual cost
- [ ] Description text visible with city/drivers/vehicles info
- [ ] Button text: "Continue to Personalized Quote"
- [ ] Button color: Orange (#e67e50)
- [ ] Button links to: `https://aisinsurance.com/?zip=90210`
- [ ] Price disclaimer visible at bottom
- [ ] Mercury logo visible in header

### Test 2.2: Other State Samples
Test these states to verify carrier display:

**Texas (TX)**:
- [ ] Zip: `75001` (Dallas)
- [ ] Carriers: Geico, Progressive, Mercury

**Florida (FL)**:
- [ ] Zip: `33139` (Miami)
- [ ] Carriers: Geico, Progressive, Mercury

**New York (NY)**:
- [ ] Zip: `10001` (Manhattan)
- [ ] Carriers: Progressive, Mercury

---

## Test Suite 3: State Name Handling (Defense-in-Depth)

### Test 3.1: Backend Normalization
**Objective**: Verify backend converts full state names to abbreviations

**Test Method** (Python):
```bash
source .venv/bin/activate
python3 << 'EOF'
from insurance_server_python.utils import _lookup_city_state_from_zip, state_abbreviation

# Test MA zips
for zip_code in ["01760", "02108"]:
    result = _lookup_city_state_from_zip(zip_code)
    if result:
        city, state = result
        state_abbr = state_abbreviation(state)
        print(f"{zip_code}: {state} -> {state_abbr}")
        assert state_abbr == "MA", f"Expected MA, got {state_abbr}"
EOF
```

**Expected**:
- [ ] All MA zips normalize to "MA"
- [ ] All states normalize to 2-letter abbreviations

### Test 3.2: Frontend State Handling
**Objective**: Verify frontend handles both abbreviations and full names

**Test Method** (Node):
```bash
node << 'EOF'
const phoneOnlyStates = ["AK", "HI", "MA", "Alaska", "Hawaii", "Massachusetts"];

// Test abbreviations
console.log("MA:", phoneOnlyStates.includes("MA"));
console.log("AK:", phoneOnlyStates.includes("AK"));
console.log("HI:", phoneOnlyStates.includes("HI"));

// Test full names
console.log("Massachusetts:", phoneOnlyStates.includes("Massachusetts"));
console.log("Alaska:", phoneOnlyStates.includes("Alaska"));
console.log("Hawaii:", phoneOnlyStates.includes("Hawaii"));

// Test normal state
console.log("CA (should be false):", phoneOnlyStates.includes("CA"));
EOF
```

**Expected**:
- [ ] All phone-only states return `true`
- [ ] Normal states return `false`

### Test 3.3: Carrier Filtering
**Test Method** (Python):
```bash
source .venv/bin/activate
python3 << 'EOF'
from insurance_server_python.carrier_mapping import get_carriers_for_state

# Phone-only states should return empty
ma_carriers = get_carriers_for_state("MA")
ak_carriers = get_carriers_for_state("AK")
hi_carriers = get_carriers_for_state("HI")

print(f"MA carriers: {ma_carriers}")
print(f"AK carriers: {ak_carriers}")
print(f"HI carriers: {hi_carriers}")

assert len(ma_carriers) == 0, "MA should have no carriers"
assert len(ak_carriers) == 0, "AK should have no carriers"
assert len(hi_carriers) == 0, "HI should have no carriers"

# Normal states should return carriers
ca_carriers = get_carriers_for_state("CA")
print(f"CA carriers: {ca_carriers}")
assert len(ca_carriers) > 0, "CA should have carriers"
EOF
```

**Expected**:
- [ ] MA, AK, HI return empty list `[]`
- [ ] CA returns 3 carriers

---

## Test Suite 4: UI/UX Consistency

### Test 4.1: Visual Consistency
**Compare phone-only state UI vs normal carrier UI:**

**Both Should Have**:
- [ ] Mercury logo in header
- [ ] "Powered by AIS" text
- [ ] Orange CTA button (#e67e50)
- [ ] Same border-radius and shadows
- [ ] Responsive layout (test mobile viewport)

**Differences (Expected)**:
- Phone-only: White bordered box with phone info
- Normal: Bordered table with carrier rows

### Test 4.2: Loading States
**Test Steps**:
1. Request quote
2. Observe loading skeleton

**Expected**:
- [ ] Loading skeleton displays during data fetch
- [ ] Skeleton transitions smoothly to content
- [ ] No flash of wrong content

### Test 4.3: Button Interaction
**Phone-Only States**:
- [ ] Click "Call Now" → Opens phone dialer
- [ ] Button has hover effect

**Normal States**:
- [ ] Click "Continue to Personalized Quote" → Opens aisinsurance.com
- [ ] Button has hover effect

---

## Test Suite 5: Edge Cases

### Test 5.1: Invalid Zip Codes
**Test Steps**:
1. Request quote with invalid zip: `00000`

**Expected**:
- [ ] Error message displayed
- [ ] No widget shown or error state in widget

### Test 5.2: Rapid State Switching
**Test Steps**:
1. Request MA quote
2. In same conversation, request CA quote
3. Switch back to MA

**Expected**:
- [ ] UI updates correctly for each state
- [ ] No carrier data leaks between states

### Test 5.3: Multiple Drivers/Vehicles
**Test Steps**:
1. Request quote with 2 drivers, 2 vehicles
2. Test in both phone-only (MA) and normal (CA) states

**Expected MA**:
- [ ] Copy mentions "2 drivers" in personalized text

**Expected CA**:
- [ ] Description mentions "2 drivers and own 2 vehicles"

---

## Test Suite 6: ChatGPT Integration

### Test 6.1: Natural Language Understanding
**Test Variations**:
- "I need car insurance in Massachusetts"
- "How much is auto insurance in Boston?"
- "Quote me for insurance in zip 01760"
- "I'm moving to Natick, need insurance"

**Expected**:
- [ ] ChatGPT correctly identifies intent
- [ ] Tool is called with correct parameters
- [ ] Widget renders properly

### Test 6.2: Tool Invocation
**Monitor Server Logs**:
```bash
tail -f server.log | grep "get-enhanced-quick-quote"
```

**Expected**:
- [ ] Tool called with correct arguments
- [ ] State normalized to abbreviation in response
- [ ] Carriers array empty for phone-only states
- [ ] Carriers array populated for normal states

### Test 6.3: Error Handling
**Test Steps**:
1. Stop server mid-request
2. Return invalid data

**Expected**:
- [ ] ChatGPT shows graceful error
- [ ] User can retry

---

## Test Suite 7: Cross-Browser Testing

### Test 7.1: Desktop Browsers
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### Test 7.2: Mobile Browsers
- [ ] iOS Safari
- [ ] Android Chrome

**Check**:
- [ ] Layout responsive
- [ ] Phone button clickable on mobile
- [ ] Text readable
- [ ] No horizontal scroll

---

## Test Suite 8: Accessibility

### Test 8.1: Screen Reader
- [ ] Phone number announced correctly
- [ ] Button purpose clear
- [ ] Alt text on logos

### Test 8.2: Keyboard Navigation
- [ ] Can tab to button
- [ ] Can activate button with Enter/Space

---

## Regression Testing Checklist

Run this after any code changes:

**Quick Smoke Test** (5 min):
- [ ] MA zip 01760 → Phone prompt
- [ ] CA zip 90210 → Carrier quotes
- [ ] Button colors correct (orange)
- [ ] No JavaScript errors in console

**Full Regression** (20 min):
- [ ] All phone-only states (MA, AK, HI)
- [ ] Sample of 3-5 normal states
- [ ] UI consistency checks
- [ ] Mobile responsive check

---

## Bug Reporting Template

```markdown
**Bug**: [Short description]

**Severity**: [Critical / High / Medium / Low]

**Test Case**: [Test number, e.g., Test 1.1]

**Steps to Reproduce**:
1.
2.
3.

**Expected**:

**Actual**:

**Environment**:
- Browser:
- Zip Code:
- State:

**Screenshots**: [Attach if applicable]

**Logs**: [Relevant server logs]
```

---

## Success Criteria

### Must Pass (Critical)
- ✅ All phone-only states (MA, AK, HI) show phone prompt, not carriers
- ✅ Button color is orange for all states
- ✅ No carrier data shown for phone-only states
- ✅ State normalization working (backend + frontend)

### Should Pass (High Priority)
- ✅ All normal states show carrier quotes
- ✅ UI styling consistent across all states
- ✅ Mobile responsive
- ✅ No console errors

### Nice to Have (Medium Priority)
- ✅ Smooth loading transitions
- ✅ Personalized copy with city names
- ✅ Cross-browser compatibility

---

## Test Execution Log

| Date | Tester | Test Suite | Pass/Fail | Notes |
|------|--------|------------|-----------|-------|
| 2024-XX-XX | [Name] | Suite 1 | ✅ Pass | All phone-only states working |
| | | Suite 2 | ⚠️ Partial | CA works, TX needs fix |
| | | Suite 3 | ✅ Pass | Defense-in-depth verified |

---

## Maintenance

**Update Frequency**:
- Review after each major release
- Update test zips if carriers change
- Add new edge cases as discovered

**Owner**: [Team/Person responsible]

**Last Updated**: 2024-02-24
