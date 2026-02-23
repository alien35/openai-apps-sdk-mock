# Insurance Quote Estimation Engine - Implementation Plan

## Overview
Build a data-driven pricing model that generates realistic insurance quote estimates without hitting carrier APIs. Uses baseline premiums + multiplier factors to create honest, range-based estimates.

---

## Architecture

```
User Input → Baseline Calculator → Factor Engine → Carrier Engine → Range Calculator → Response
                                      ↓
                              [Age, Marital, Vehicle, ZIP, Coverage]
                                      ↓
                              Risk Score (0-1)
                                      ↓
                              Carrier Multipliers
                                      ↓
                              Final Estimates + Ranges
```

---

## Phase 1: Core Data Structures

### 1.1 State Base Rates (`insurance_server_python/pricing/state_base_rates.py`)

```python
STATE_BASE_FULL_COVERAGE_ANNUAL = {
    # High-cost states
    "CA": 2800,  # High traffic, litigation
    "FL": 2900,  # Hurricane, fraud, dense cities
    "MI": 3200,  # No-fault, high injury claims
    "LA": 2850,  # Litigation, weather
    "NY": 2700,  # Urban density, high repair costs

    # Mid-cost states
    "TX": 2400,
    "IL": 2300,
    "GA": 2200,
    "AZ": 2100,
    "NV": 2300,

    # Lower-cost states
    "ME": 1600,
    "VT": 1650,
    "IA": 1700,
    "OH": 1900,
    "WI": 1850,

    # Default for unlisted states
    "DEFAULT": 2000,
}
```

### 1.2 ZIP Cost Buckets (`insurance_server_python/pricing/zip_buckets.py`)

```python
# First 3 digits → cost multiplier
ZIP_BUCKET_MULTIPLIERS = {
    # California high-cost metros
    "900": 1.35,  # LA (90001-90089)
    "901": 1.35,  # LA continued
    "902": 1.35,  # Beverly Hills, Santa Monica
    "941": 1.30,  # San Francisco
    "943": 1.28,  # Palo Alto, Mountain View

    # Florida high-cost
    "330": 1.40,  # Miami metro (high fraud area)
    "331": 1.35,  # Miami continued

    # New York high-cost
    "100": 1.45,  # Manhattan
    "112": 1.35,  # Brooklyn

    # Default buckets by range
    "METRO_HIGH": 1.25,     # Major metros not listed
    "METRO_MEDIUM": 1.10,   # Mid-size cities
    "SUBURBAN": 1.00,       # Suburban areas
    "RURAL": 0.85,          # Rural areas
}

def get_zip_multiplier(zip_code: str) -> float:
    """Get cost multiplier based on ZIP code."""
    prefix = zip_code[:3]
    return ZIP_BUCKET_MULTIPLIERS.get(prefix, 1.0)
```

### 1.3 Carrier Posture Profiles (`insurance_server_python/pricing/carrier_profiles.py`)

```python
# (low_mult, high_mult) - interpolated based on risk score
CARRIER_BASE_MULT = {
    "Geico": (0.88, 1.05),                    # Competitive for good risks
    "Progressive Insurance": (0.92, 1.12),     # Broad appetite
    "Safeco Insurance": (1.00, 1.18),          # Standard/preferred
    "Mercury Auto Insurance": (0.90, 1.15),    # State-dependent, CA strong
    "National General": (1.05, 1.30),          # Non-standard friendly
    "Foremost Insurance Group": (1.08, 1.25), # Non-standard
    "Dairyland Insurance": (1.10, 1.35),       # High-risk specialty
    "Root": (0.85, 1.08),                      # Tech, telematics discount
    "Clearcover": (0.90, 1.10),                # Digital-first
}

# State-specific carrier adjustments (optional fine-tuning)
CARRIER_STATE_ADJ = {
    "Mercury Auto Insurance": {
        "CA": -0.08,  # Very competitive in CA
        "NV": -0.05,
        "AZ": -0.05,
    },
    "Geico": {
        "FL": 0.05,   # Less competitive in FL
    },
}
```

---

## Phase 2: Factor Calculation Engine

### 2.1 Age Factor (`insurance_server_python/pricing/factors.py`)

```python
def calculate_age_factor(age: int, coverage_type: str = "full") -> tuple[float, str]:
    """
    Returns (multiplier, explanation)
    """
    if age < 18:
        return (2.4, "Under 18 - highest risk category")
    elif age <= 20:
        return (2.0, "Age 18-20 - new driver rates")
    elif age <= 24:
        return (1.45, "Age 21-24 - young driver rates")
    elif age <= 29:
        return (1.15, "Age 25-29 - transitioning to standard rates")
    elif age <= 45:
        return (0.95, "Age 30-45 - prime age group with lowest rates")
    elif age <= 65:
        return (0.90, "Age 46-65 - experienced driver rates")
    elif age <= 75:
        return (1.05, "Age 66-75 - senior rates")
    else:
        return (1.20, "Age 76+ - elevated senior rates")
```

### 2.2 Marital Status Factor

```python
def calculate_marital_factor(marital_status: str) -> tuple[float, str]:
    """Returns (multiplier, explanation)"""
    status_lower = marital_status.lower()

    if "married" in status_lower:
        return (0.94, "Married status - lower risk profile")
    elif "single" in status_lower:
        return (1.00, "Single status - standard rates")
    elif "divorced" in status_lower or "widowed" in status_lower:
        return (1.02, "Divorced/widowed - slightly elevated rates")
    else:
        return (1.00, "Standard marital status rates")
```

### 2.3 Vehicle Factor

```python
# Vehicle type categories
LUXURY_MAKES = ["BMW", "Mercedes", "Audi", "Lexus", "Porsche", "Tesla"]
PERFORMANCE_MODELS = ["Mustang", "Camaro", "Charger", "Challenger", "WRX"]
ECONOMY_MODELS = ["Civic", "Corolla", "Accord", "Camry", "Sentra", "Elantra"]

def calculate_vehicle_factor(year: int, make: str, model: str, current_year: int = 2026) -> tuple[float, str]:
    """Returns (multiplier, explanation)"""
    vehicle_age = current_year - year
    make_upper = make.upper()
    model_upper = model.upper()

    # Base factor from age
    if vehicle_age <= 2:
        age_factor = 1.15
        age_desc = "Very new vehicle - higher repair/replacement costs"
    elif vehicle_age <= 5:
        age_factor = 1.08
        age_desc = "New vehicle - elevated repair costs"
    elif vehicle_age <= 9:
        age_factor = 1.00
        age_desc = "Standard age vehicle"
    else:
        age_factor = 0.93
        age_desc = "Older vehicle - lower replacement value"

    # Adjust for vehicle type
    if any(luxury in make_upper for luxury in LUXURY_MAKES):
        type_factor = 1.25
        type_desc = "Luxury vehicle - expensive parts and repairs"
    elif any(perf in model_upper for perf in PERFORMANCE_MODELS):
        type_factor = 1.35
        type_desc = "Performance vehicle - higher risk and repair costs"
    elif any(econ in model_upper for econ in ECONOMY_MODELS):
        type_factor = 0.95
        type_desc = "Economy vehicle - affordable repairs"
    else:
        type_factor = 1.00
        type_desc = "Standard vehicle type"

    final_factor = age_factor * type_factor
    explanation = f"{age_desc}; {type_desc}"

    return (final_factor, explanation)
```

### 2.4 Coverage Type Factor

```python
def calculate_coverage_factor(coverage_type: str) -> tuple[float, str]:
    """Returns (multiplier, explanation)"""
    coverage_lower = coverage_type.lower()

    if "liability" in coverage_lower or "minimum" in coverage_lower:
        return (0.60, "Liability-only coverage - lower premium")
    elif "full" in coverage_lower or "comprehensive" in coverage_lower:
        return (1.00, "Full coverage - includes collision and comprehensive")
    else:
        return (1.00, "Standard coverage level")
```

---

## Phase 3: Risk Scoring System

### 3.1 Calculate Overall Risk Score

```python
def calculate_risk_score(
    age: int,
    marital_status: str,
    vehicle_age: int,
    zip_code: str,
    coverage_type: str,
    accidents: int = 0,
    tickets: int = 0,
) -> float:
    """
    Calculate risk score from 0.0 (lowest risk) to 1.0 (highest risk)
    Used to interpolate carrier multipliers
    """
    score = 0.5  # Start at middle

    # Age contribution (40% weight)
    if age < 21:
        score += 0.30
    elif age < 25:
        score += 0.20
    elif age < 30:
        score += 0.10
    elif age <= 65:
        score -= 0.10  # Prime age discount
    else:
        score += 0.05

    # Marital status (10% weight)
    if "married" in marital_status.lower():
        score -= 0.05

    # Vehicle age (15% weight)
    if vehicle_age <= 2:
        score += 0.08
    elif vehicle_age >= 10:
        score -= 0.05

    # ZIP (15% weight)
    zip_mult = get_zip_multiplier(zip_code)
    if zip_mult > 1.3:
        score += 0.10
    elif zip_mult < 0.9:
        score -= 0.10

    # Coverage type (10% weight)
    if "liability" in coverage_type.lower():
        score -= 0.05

    # Violations (20% weight) - if available
    score += min(accidents * 0.15, 0.20)
    score += min(tickets * 0.08, 0.15)

    # Clamp to 0-1
    return max(0.0, min(1.0, score))
```

---

## Phase 4: Uncertainty & Range Calculation

### 4.1 Data Completeness Assessment

```python
def assess_data_completeness(inputs: dict) -> tuple[float, str]:
    """
    Assess how much data we have and return uncertainty band
    Returns (band_percentage, confidence_level)
    """
    score = 0
    max_score = 10

    # Core inputs (have these)
    if inputs.get("age"): score += 1
    if inputs.get("zip_code"): score += 1
    if inputs.get("vehicle"): score += 1
    if inputs.get("coverage_type"): score += 1
    if inputs.get("marital_status"): score += 1

    # Optional inputs (improve accuracy)
    if inputs.get("driving_history", {}).get("accidents") is not None: score += 1
    if inputs.get("driving_history", {}).get("tickets") is not None: score += 1
    if inputs.get("annual_mileage"): score += 1
    if inputs.get("credit_tier"): score += 1
    if inputs.get("continuous_insurance"): score += 1

    # Calculate band
    if score >= 8:
        return (0.20, "high")    # ±20% range
    elif score >= 5:
        return (0.30, "medium")  # ±30% range
    else:
        return (0.40, "low")     # ±40% range
```

### 4.2 Generate Range

```python
def calculate_range(
    point_estimate: float,
    band_percentage: float,
    state: str,
) -> tuple[float, float]:
    """
    Returns (low, high) range
    Applies sanity bounds per state
    """
    low = point_estimate * (1 - band_percentage)
    high = point_estimate * (1 + band_percentage)

    # State-specific monthly minimums
    monthly_mins = {
        "CA": 120,
        "FL": 150,
        "MI": 180,
        "NY": 130,
        "DEFAULT": 100,
    }

    monthly_min = monthly_mins.get(state, monthly_mins["DEFAULT"])
    monthly_max = 800  # Soft cap for sanity

    # Apply bounds (for monthly)
    low = max(low, monthly_min)
    high = min(high, monthly_max)

    return (low, high)
```

---

## Phase 5: Main Estimation Engine

### 5.1 Core Calculator (`insurance_server_python/pricing/estimator.py`)

```python
class InsuranceQuoteEstimator:
    """Main estimation engine"""

    def estimate_quotes(
        self,
        state: str,
        zip_code: str,
        age: int,
        marital_status: str,
        vehicle: dict,
        coverage_type: str,
        carriers: list[str],
        **optional_inputs,
    ) -> dict:
        """
        Generate quote estimates for multiple carriers

        Returns:
        {
            "baseline": {
                "annual": 3100,
                "monthly": 258,
                "band": 0.35,
                "confidence": "medium"
            },
            "quotes": [
                {
                    "carrier": "Geico",
                    "annual": 2850,
                    "monthly": 238,
                    "range_monthly": [155, 321],
                    "range_annual": [1860, 3850],
                    "confidence": "medium",
                    "explanations": [...]
                },
                ...
            ]
        }
        """
        # 1. Get base rate
        base_annual = STATE_BASE_FULL_COVERAGE_ANNUAL.get(
            state,
            STATE_BASE_FULL_COVERAGE_ANNUAL["DEFAULT"]
        )

        # 2. Calculate all factors
        age_mult, age_exp = calculate_age_factor(age, coverage_type)
        marital_mult, marital_exp = calculate_marital_factor(marital_status)
        vehicle_mult, vehicle_exp = calculate_vehicle_factor(
            vehicle["year"],
            vehicle["make"],
            vehicle["model"]
        )
        zip_mult = get_zip_multiplier(zip_code)
        zip_exp = f"ZIP {zip_code[:3]}xx - {self._zip_desc(zip_mult)}"
        coverage_mult, coverage_exp = calculate_coverage_factor(coverage_type)

        # 3. Calculate baseline
        baseline_annual = (
            base_annual *
            age_mult *
            marital_mult *
            vehicle_mult *
            zip_mult *
            coverage_mult
        )
        baseline_monthly = baseline_annual / 12

        # 4. Calculate risk score
        risk_score = calculate_risk_score(
            age=age,
            marital_status=marital_status,
            vehicle_age=2026 - vehicle["year"],
            zip_code=zip_code,
            coverage_type=coverage_type,
            accidents=optional_inputs.get("accidents", 0),
            tickets=optional_inputs.get("tickets", 0),
        )

        # 5. Assess data completeness
        band, confidence = assess_data_completeness({
            "age": age,
            "zip_code": zip_code,
            "vehicle": vehicle,
            "coverage_type": coverage_type,
            "marital_status": marital_status,
            **optional_inputs,
        })

        # 6. Generate carrier quotes
        quotes = []
        for carrier in carriers:
            carrier_annual, carrier_exp = self._estimate_carrier(
                carrier=carrier,
                baseline_annual=baseline_annual,
                risk_score=risk_score,
                state=state,
            )
            carrier_monthly = carrier_annual / 12

            # Calculate ranges
            range_low, range_high = calculate_range(
                carrier_monthly,
                band,
                state
            )

            quotes.append({
                "carrier": carrier,
                "annual": int(carrier_annual),
                "monthly": int(carrier_monthly),
                "range_monthly": [int(range_low), int(range_high)],
                "range_annual": [int(range_low * 12), int(range_high * 12)],
                "confidence": confidence,
                "explanations": [
                    age_exp,
                    marital_exp,
                    vehicle_exp,
                    zip_exp,
                    coverage_exp,
                    carrier_exp,
                ]
            })

        # Sort by monthly price
        quotes.sort(key=lambda q: q["monthly"])

        return {
            "baseline": {
                "annual": int(baseline_annual),
                "monthly": int(baseline_monthly),
                "band": band,
                "confidence": confidence,
            },
            "quotes": quotes,
        }

    def _estimate_carrier(
        self,
        carrier: str,
        baseline_annual: float,
        risk_score: float,
        state: str,
    ) -> tuple[float, str]:
        """Calculate carrier-specific estimate"""
        # Get carrier multiplier range
        low_mult, high_mult = CARRIER_BASE_MULT.get(
            carrier,
            (1.0, 1.15)  # Default for unknown carriers
        )

        # Interpolate based on risk score
        carrier_mult = low_mult + (high_mult - low_mult) * risk_score

        # Apply state adjustment if exists
        state_adj = CARRIER_STATE_ADJ.get(carrier, {}).get(state, 0)
        carrier_mult += state_adj

        carrier_annual = baseline_annual * carrier_mult

        # Generate explanation
        if carrier_mult < 1.0:
            explanation = f"{carrier} - Competitive pricing for your profile"
        elif carrier_mult > 1.15:
            explanation = f"{carrier} - Higher rates but broader coverage options"
        else:
            explanation = f"{carrier} - Standard market pricing"

        return (carrier_annual, explanation)

    def _zip_desc(self, zip_mult: float) -> str:
        """Describe ZIP multiplier"""
        if zip_mult >= 1.3:
            return "high-cost urban area"
        elif zip_mult >= 1.1:
            return "moderate-cost area"
        elif zip_mult <= 0.9:
            return "low-cost rural area"
        else:
            return "average-cost area"
```

---

## Phase 6: Integration with MCP

### 6.1 Update Quick Quote Tool Handler

```python
async def _quick_quote_tool_handler(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Enhanced quick quote with estimation engine"""
    from .pricing.estimator import InsuranceQuoteEstimator

    # Parse inputs
    payload = QuickQuoteSubmission.model_validate(arguments)

    # Normalize state
    state = normalize_state(payload.state) or "CA"

    # Get carriers for state
    carriers = get_carriers_for_state(state)

    # Initialize estimator
    estimator = InsuranceQuoteEstimator()

    # Generate estimates
    result = estimator.estimate_quotes(
        state=state,
        zip_code=payload.zip_code,
        age=payload.primary_driver_age,
        marital_status=getattr(payload, "marital_status", "single"),
        vehicle={
            "year": getattr(payload, "vehicle_year", 2020),
            "make": getattr(payload, "vehicle_make", "Honda"),
            "model": getattr(payload, "vehicle_model", "Civic"),
        },
        coverage_type="full",  # Default for now
        carriers=carriers,
    )

    # Format for widget
    carriers_with_logos = []
    for quote in result["quotes"]:
        carriers_with_logos.append({
            "name": quote["carrier"],
            "logo": get_carrier_logo(quote["carrier"]),
            "annual_cost": quote["annual"],
            "monthly_cost": quote["monthly"],
            "range_low": quote["range_monthly"][0],
            "range_high": quote["range_monthly"][1],
            "confidence": quote["confidence"],
            "explanations": quote["explanations"],
        })

    # Build response...
```

---

## Phase 7: Widget Updates

### 7.1 Display Ranges and Confidence

Update `quick_quote_results_widget.py` to show:
- Price ranges (e.g., "$238 - $321/mo")
- Confidence badges ("Medium Confidence")
- Hover tooltips with explanations
- Visual indicators for uncertainty

```html
<div class="carrier-row">
  <div class="carrier-left">
    <img src="..." alt="Carrier">
    <span class="confidence-badge confidence-medium">Medium Confidence</span>
  </div>
  <div class="carrier-right">
    <div class="cost-column">
      <div class="cost-label">Est. Monthly Cost</div>
      <div class="cost-value">$238</div>
      <div class="cost-range">Range: $155 - $321</div>
    </div>
    <div class="explanations">
      <button class="info-icon" onclick="toggleExplanations(this)">ℹ️</button>
      <div class="explanations-popup hidden">
        <ul>
          <li>Age 25-29 - transitioning to standard rates</li>
          <li>Married status - lower risk profile</li>
          <li>2020 Honda Civic - economy vehicle</li>
          <li>ZIP 90210 - high-cost urban area</li>
          <li>Full coverage selected</li>
        </ul>
      </div>
    </div>
  </div>
</div>
```

---

## Phase 8: Compliance & Disclaimers

### 8.1 Add Prominent Disclaimers

```python
ESTIMATION_DISCLAIMER = """
**Important:** These are estimated price ranges based on limited information and
industry averages. Actual quotes from carriers may differ significantly based on:
- Complete driving history (accidents, violations)
- Credit score (where permitted)
- Exact coverage selections and deductibles
- Discounts you may qualify for (bundling, safety features, etc.)
- Carrier-specific underwriting criteria

To get an accurate quote, you'll need to contact carriers directly or complete
a full application with detailed information.
"""
```

Add to widget as collapsible section at bottom.

---

## Implementation Order

### Sprint 1: Foundation (2-3 days)
- [ ] Create pricing module structure
- [ ] Implement state base rates
- [ ] Implement ZIP bucket mapping
- [ ] Build factor calculation functions
- [ ] Unit tests for factors

### Sprint 2: Estimation Engine (2-3 days)
- [ ] Implement carrier profiles
- [ ] Build risk scoring system
- [ ] Create main estimator class
- [ ] Range calculation logic
- [ ] Integration tests

### Sprint 3: MCP Integration (1-2 days)
- [ ] Update quick_quote tool handler
- [ ] Update data models
- [ ] Test with existing flow
- [ ] Logging and observability

### Sprint 4: Widget Enhancement (2 days)
- [ ] Update UI for ranges and confidence
- [ ] Add explanation tooltips
- [ ] Add compliance disclaimers
- [ ] Visual polish

### Sprint 5: Calibration & Testing (1-2 days)
- [ ] Compare estimates against known benchmarks
- [ ] Adjust multipliers for realism
- [ ] User acceptance testing
- [ ] Documentation

---

## Calibration Strategy

To ensure estimates are realistic:

1. **Benchmark Against Known Data:**
   - Use publicly available state average premiums
   - Compare against real quotes (if available)
   - Adjust STATE_BASE rates to match averages

2. **Validate Ranges:**
   - Check that 80% of real quotes fall within ranges
   - Adjust band percentages if too wide/narrow

3. **Carrier Posture Tuning:**
   - Research carrier market positioning
   - Adjust multipliers based on reputation
   - Test across different risk profiles

4. **User Feedback Loop:**
   - Track when users say "too high" or "too low"
   - Collect data on actual quotes obtained
   - Iterate on factors

---

## Success Metrics

- **Accuracy:** 70% of actual quotes fall within ±20% of estimate
- **Realism:** Ranges feel honest and achievable
- **Trust:** Users understand it's an estimate, not a promise
- **Utility:** Users can make carrier comparison decisions
- **Performance:** < 100ms to generate estimates

---

## Future Enhancements

1. **Machine Learning:** Train on real quote data to improve factors
2. **More Factors:** Credit tier, annual mileage, deductible preferences
3. **Discount Modeling:** Bundle discounts, safety features, loyalty
4. **Historical Trends:** Adjust for market rate changes over time
5. **A/B Testing:** Test different multiplier strategies
