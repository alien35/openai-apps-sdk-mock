"""
Configuration for insurance quote estimation.

All multipliers and base rates are easily adjustable here.
Tune these values to calibrate estimate accuracy.
"""

from typing import Dict, List, Tuple

# ============================================================================
# STATE BASE RATES
# ============================================================================
# Annual full coverage premium baseline by state (before any multipliers)

STATE_BASE_FULL_COVERAGE_ANNUAL: Dict[str, int] = {
    # High-cost states (dense population, high claims, litigation)
    "CA": 2800,  # High traffic, litigation costs, urban density
    "FL": 2900,  # Hurricane risk, fraud, PIP requirements
    "MI": 3200,  # No-fault system, high injury claims
    "LA": 2850,  # High litigation, weather risk
    "NY": 2700,  # Urban density, high repair costs
    "NJ": 2650,  # Dense population, high costs
    "NV": 2300,  # Las Vegas metro drives up costs
    "MD": 2200,  # DC area impacts
    "DE": 2200,  # Small state, higher urban costs

    # Mid-cost states
    "TX": 2400,  # Large state, mixed urban/rural
    "IL": 2300,  # Chicago area drives costs
    "GA": 2200,  # Atlanta area impact
    "AZ": 2100,  # Phoenix metro
    "CO": 2000,  # Denver area
    "WA": 2100,  # Seattle area
    "OR": 1950,  # Portland area
    "PA": 2150,  # Pittsburgh/Philly areas
    "CT": 2400,  # High costs, small state
    "RI": 2350,  # Dense, high costs
    "MA": 2300,  # Boston area

    # Lower-cost states (rural, less dense, lower claims)
    "ME": 1600,  # Rural, low population
    "VT": 1650,  # Rural, low population
    "NH": 1700,  # Rural, smaller population
    "IA": 1700,  # Agricultural, low density
    "OH": 1900,  # Mixed urban/rural
    "WI": 1850,  # Mixed
    "MN": 1900,  # Minneapolis area balanced by rural
    "SD": 1550,  # Very rural, low population
    "ND": 1550,  # Very rural, low population
    "ID": 1650,  # Rural, mountainous
    "MT": 1600,  # Very rural
    "WY": 1550,  # Very rural, low population
    "KS": 1750,  # Agricultural, moderate
    "NE": 1700,  # Agricultural, low density
    "MO": 1900,  # Kansas City/St. Louis balanced
    "OK": 1850,  # Mixed
    "AR": 1800,  # Mixed
    "MS": 1850,  # Mixed
    "AL": 1900,  # Birmingham area
    "TN": 1950,  # Nashville/Memphis areas
    "KY": 1800,  # Mixed
    "WV": 1750,  # Rural, lower costs
    "VA": 2000,  # DC area impacts northern region
    "NC": 1950,  # Charlotte/Raleigh areas
    "SC": 1900,  # Charleston/Columbia areas
    "IN": 1850,  # Indianapolis area
    "UT": 1800,  # Salt Lake City area
    "NM": 1850,  # Albuquerque area
    "AK": 1900,  # Remote, higher costs
    "HI": 2200,  # Island, higher costs

    # Default for any unlisted states or DC
    "DEFAULT": 2000,
}


# ============================================================================
# AGE FACTOR CURVES
# ============================================================================
# Format: (min_age, max_age, multiplier, description)
# Ages are inclusive

AGE_FACTOR_CURVES: List[Tuple[int, int, float, str]] = [
    (16, 17, 2.40, "Under 18 - highest risk category, new driver"),
    (18, 20, 2.00, "Age 18-20 - very high risk, minimal experience"),
    (21, 24, 1.45, "Age 21-24 - young driver, still elevated risk"),
    (25, 29, 1.15, "Age 25-29 - transitioning to standard rates"),
    (30, 45, 0.95, "Age 30-45 - prime age, lowest rates"),
    (46, 65, 0.90, "Age 46-65 - experienced driver, stable rates"),
    (66, 75, 1.05, "Age 66-75 - senior rates, slight increase"),
    (76, 120, 1.20, "Age 76+ - elevated senior rates"),
]


# ============================================================================
# MARITAL STATUS FACTORS
# ============================================================================
# Format: {status_keyword: (multiplier, description)}

MARITAL_STATUS_FACTORS: Dict[str, Tuple[float, str]] = {
    "married": (0.94, "Married status - statistically lower risk"),
    "single": (1.00, "Single status - standard baseline rates"),
    "divorced": (1.02, "Divorced status - slightly elevated rates"),
    "widowed": (1.02, "Widowed status - slightly elevated rates"),
    "default": (1.00, "Standard marital status rates"),
}


# ============================================================================
# VEHICLE CATEGORIZATION
# ============================================================================

# Luxury brands (higher repair costs, theft risk)
LUXURY_MAKES = [
    "BMW", "MERCEDES", "MERCEDES-BENZ", "AUDI", "LEXUS", "PORSCHE",
    "TESLA", "JAGUAR", "LAND ROVER", "RANGE ROVER", "MASERATI",
    "BENTLEY", "ROLLS-ROYCE", "CADILLAC", "LINCOLN", "ACURA", "INFINITI"
]

# Performance models (higher risk, expensive repairs)
PERFORMANCE_MODELS = [
    "MUSTANG", "CAMARO", "CHARGER", "CHALLENGER", "CORVETTE",
    "WRX", "STI", "M3", "M5", "AMG", "TYPE R", "GT-R",
    "911", "HELLCAT", "DEMON", "SUPRA", "370Z", "Z06"
]

# Economy/reliable models (lower repair costs, lower theft)
ECONOMY_MODELS = [
    "CIVIC", "COROLLA", "ACCORD", "CAMRY", "SENTRA", "ELANTRA",
    "JETTA", "FORTE", "IMPREZA", "LEGACY", "MAZDA3", "MAZDA6",
    "OPTIMA", "SONATA", "MALIBU", "FUSION", "ALTIMA", "PRIUS"
]


# ============================================================================
# VEHICLE AGE FACTORS
# ============================================================================
# Format: (max_age, multiplier, description)

VEHICLE_AGE_FACTORS: List[Tuple[int, float, str]] = [
    (2, 1.15, "Very new vehicle (0-2 years) - higher replacement/repair costs"),
    (5, 1.08, "New vehicle (3-5 years) - elevated repair costs"),
    (9, 1.00, "Standard age vehicle (6-9 years) - baseline rates"),
    (999, 0.93, "Older vehicle (10+ years) - lower replacement value"),
]


# ============================================================================
# VEHICLE TYPE FACTORS
# ============================================================================

VEHICLE_TYPE_FACTORS: Dict[str, Tuple[float, str]] = {
    "luxury": (1.25, "Luxury vehicle - expensive parts and repairs"),
    "performance": (1.35, "Performance vehicle - higher risk and repair costs"),
    "economy": (0.95, "Economy vehicle - affordable, reliable repairs"),
    "standard": (1.00, "Standard vehicle type - baseline rates"),
}


# ============================================================================
# ZIP CODE COST BUCKETS
# ============================================================================
# Format: {zip_prefix: multiplier}
# Multiplier reflects urban density, theft, accident rates, repair costs

ZIP_BUCKET_MULTIPLIERS: Dict[str, float] = {
    # California high-cost metros
    "900": 1.35,  # LA (90001-90089)
    "901": 1.35,  # LA continued
    "902": 1.40,  # Beverly Hills, Santa Monica, Malibu (very high)
    "903": 1.30,  # Inglewood, Hawthorne
    "904": 1.30,  # Santa Monica, Venice
    "905": 1.25,  # Torrance, Carson
    "906": 1.25,  # Long Beach
    "910": 1.30,  # Pasadena
    "917": 1.25,  # Glendale, Burbank
    "941": 1.35,  # San Francisco
    "943": 1.30,  # Palo Alto, Mountain View
    "944": 1.32,  # San Mateo
    "945": 1.28,  # Oakland, Berkeley
    "946": 1.25,  # Castro Valley, Hayward
    "947": 1.20,  # Berkeley suburbs
    "948": 1.18,  # Richmond

    # Florida high-cost (fraud hotspots)
    "330": 1.45,  # Miami metro (notorious for fraud)
    "331": 1.40,  # Miami continued
    "332": 1.35,  # Miami suburbs
    "333": 1.38,  # Fort Lauderdale
    "334": 1.35,  # West Palm Beach

    # New York high-cost
    "100": 1.50,  # Manhattan (highest in nation)
    "101": 1.48,  # Manhattan continued
    "102": 1.45,  # Manhattan continued
    "112": 1.38,  # Brooklyn
    "113": 1.35,  # Flushing, Queens
    "104": 1.30,  # Bronx
    "103": 1.32,  # Staten Island

    # Illinois - Chicago
    "606": 1.30,  # Chicago downtown
    "607": 1.28,  # Chicago north side
    "608": 1.25,  # Chicago suburbs

    # Texas - major metros
    "750": 1.22,  # Dallas
    "770": 1.25,  # Houston
    "787": 1.20,  # Austin

    # Michigan - Detroit area
    "482": 1.40,  # Detroit (high due to no-fault)
    "483": 1.35,  # Detroit suburbs

    # Nevada - Las Vegas
    "891": 1.25,  # Las Vegas

    # Default bucket categories (for unlisted ZIPs)
    "METRO_HIGH": 1.25,      # Major metro not specifically listed
    "METRO_MEDIUM": 1.10,    # Mid-size cities
    "SUBURBAN": 1.00,        # Suburban areas
    "RURAL": 0.85,           # Rural areas
}


# ============================================================================
# COVERAGE TYPE FACTORS
# ============================================================================

COVERAGE_TYPE_FACTORS: Dict[str, Tuple[float, str]] = {
    "liability": (0.60, "Liability-only coverage - no collision/comprehensive"),
    "minimum": (0.60, "Minimum coverage - state minimums only"),
    "full": (1.00, "Full coverage - includes collision and comprehensive"),
    "comprehensive": (1.00, "Comprehensive coverage - full protection"),
    "default": (1.00, "Standard coverage level"),
}


# ============================================================================
# CARRIER PRICING POSTURE
# ============================================================================
# Format: {carrier_name: (low_multiplier, high_multiplier)}
# Interpolated based on risk score (0.0 = low mult, 1.0 = high mult)

CARRIER_BASE_MULTIPLIERS: Dict[str, Tuple[float, float]] = {
    "Geico": (0.88, 1.05),                      # Competitive for good risks
    "Progressive Insurance": (0.88, 1.08),       # Broad appetite, middle market (calibrated)
    "Safeco Insurance": (1.00, 1.18),            # Standard/preferred market
    "Mercury Auto Insurance": (0.90, 1.15),      # Strong in CA/NV/AZ
    "National General": (1.10, 1.35),            # Non-standard friendly (calibrated)
    "Foremost Insurance Group": (1.08, 1.25),    # Non-standard specialty
    "Dairyland Insurance": (1.10, 1.35),         # High-risk specialty
    "Root": (0.85, 1.08),                        # Tech/telematics discount
    "Clearcover": (0.90, 1.10),                  # Digital-first, efficient
    "Assurance America": (1.05, 1.25),           # Non-standard
    "Gainsco": (1.08, 1.30),                     # Non-standard
    "Infinity Insurance Company": (1.10, 1.32),  # Non-standard specialty
}


# ============================================================================
# CARRIER STATE ADJUSTMENTS
# ============================================================================
# Optional fine-tuning per carrier per state
# Format: {carrier: {state: adjustment}}

CARRIER_STATE_ADJUSTMENTS: Dict[str, Dict[str, float]] = {
    "Mercury Auto Insurance": {
        "CA": -0.15,  # Extremely competitive in California (calibrated from 90210 data)
        "NV": -0.05,  # Strong Nevada presence
        "AZ": -0.05,  # Strong Arizona presence
    },
    "Geico": {
        "FL": 0.05,   # Less competitive in Florida
    },
    "Progressive Insurance": {
        "CA": 0.10,   # Higher pricing in California (calibrated from 90210 data)
    },
}


# ============================================================================
# RISK SCORING WEIGHTS
# ============================================================================
# Weights for calculating overall risk score (0.0 to 1.0)
# All weights should sum to 1.0

RISK_SCORE_WEIGHTS = {
    "age": 0.40,            # Age is primary risk indicator
    "marital": 0.10,        # Marital status moderate impact
    "vehicle_age": 0.15,    # Vehicle age moderate impact
    "zip_cost": 0.15,       # Location moderate impact
    "coverage": 0.10,       # Coverage type small impact
    "violations": 0.10,     # Accidents/tickets (if available)
}


# ============================================================================
# CONFIDENCE BANDS
# ============================================================================
# Uncertainty ranges based on data completeness
# Format: (min_score, band_percentage, confidence_level)

CONFIDENCE_BANDS: List[Tuple[int, float, str]] = [
    (8, 0.20, "high"),      # 8+ data points: ±20%
    (5, 0.30, "medium"),    # 5-7 data points: ±30%
    (0, 0.40, "low"),       # <5 data points: ±40%
]


# ============================================================================
# SANITY BOUNDS
# ============================================================================
# Minimum and maximum monthly premiums by state
# Prevents unrealistic estimates

MONTHLY_MINIMUM_BY_STATE: Dict[str, int] = {
    "CA": 120,
    "FL": 150,
    "MI": 180,
    "NY": 130,
    "NJ": 125,
    "LA": 140,
    "TX": 100,
    "DEFAULT": 100,
}

# Soft maximum (can go higher for extreme cases, but rare)
MONTHLY_MAXIMUM = 800


# ============================================================================
# EXPLANATIONS
# ============================================================================

ZIP_COST_DESCRIPTIONS = {
    "high": "high-cost urban area with heavy traffic and elevated claim rates",
    "medium_high": "moderate-cost metropolitan area",
    "medium": "average-cost area",
    "low": "low-cost rural area with lower claim rates",
}

CARRIER_PRICING_DESCRIPTIONS = {
    "competitive": "{carrier} - Competitive pricing for your risk profile",
    "standard": "{carrier} - Standard market pricing",
    "elevated": "{carrier} - Higher rates but broader coverage options",
}
