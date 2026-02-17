# Minimal Required Fields Strategy

## Problem Statement

The current insurance intake flow asks for many fields, some of which are optional. This creates a lengthy form-filling experience. We need a strategy to only collect **truly required fields** to streamline the user experience while still generating valid quotes.

## API Contract Analysis

The zrater.io API provides JSON Schema contracts per state (e.g., CA) that define:
- **Required fields** - Must be present for a valid quote request
- **Optional fields** - Can be omitted or defaulted
- **Conditional requirements** - Some fields become required based on other field values

### Example Contract Endpoint
```
GET https://gateway.zrater.io/api/v1/linesOfBusiness/personalAuto/states/CA/contracts
```

## Core Required Fields (California Personal Auto)

Based on the CA contract schema, here are the **absolute minimum required fields**:

### Customer (Named Insured)
**Required:**
- `Identifier` - Quote ID (auto-generated)
- `FirstName`
- `LastName`
- `Address` (Street1, City, State, ZipCode)
- `MonthsAtResidence`
- `PriorInsuranceInformation.PriorInsurance` (boolean)
  - If `true`: Requires `PriorExpirationDate`, `PriorCarrierId`, `PriorLiabilityLimit`, `PriorMonthsCoverage`
  - If `false`: Requires `ReasonForNoInsurance`

### Driver (Each Rated Driver)
**Required:**
- `DriverId` (auto-assigned: 1, 2, 3...)
- `FirstName`
- `LastName`
- `DateOfBirth`
- `Gender`
- `MaritalStatus`
- `LicenseInformation.LicenseStatus`
  - If `Valid/Expired/Revoked/Suspended`: Requires `MonthsLicensed`, `StateLicensed`
  - If `Permit`: Requires `StateLicensed`
- `Attributes.PropertyInsurance` (boolean)
- `Attributes.Relation` (to named insured)
- `Attributes.ResidencyStatus` (Own/Rent/Lease)
- `Attributes.ResidencyType` (Home/Apartment/Condo/etc)

### Vehicle (Each Vehicle)
**Required:**
- `VehicleId` (auto-assigned: 1, 2, 3...)
- `Vin`
- `Year`
- `Make`
- `Model`
- `BodyType`
- `UseType`
- `AssignedDriverId` (which driver drives this vehicle)
- `CoverageInformation`:
  - `CollisionDeductible`
  - `ComprehensiveDeductible`
  - `RentalLimit`
  - `TowingLimit`
  - `SafetyGlassCoverage` (boolean)
- `PercentToWork` (% of driving for commute)
- `MilesToWork` (daily commute miles)
- `AnnualMiles`

### Policy-Level Coverages
**Required:**
- `LiabilityBiLimit`
- `LiabilityPdLimit`
- `MedPayLimit`
- `UninsuredMotoristBiLimit`
- `UninsuredMotoristPd/CollisionDamageWaiver` (boolean)
- `AccidentalDeathLimit`

### Policy Metadata
**Required:**
- `Identifier` (Quote ID)
- `EffectiveDate`

## Strategy Implementation

### Phase 1: Schema-Driven Field Collection ✅ (Implement First)

1. **Fetch Contract Schema on Startup**
   - Cache the CA contract schema on server initialization
   - Parse `required` arrays at each level
   - Build a "minimal fields map" that only includes truly required fields

2. **Update Widget to Use Schema**
   - Modify insurance state widget to request only required fields
   - Hide all optional fields by default
   - Add "Show advanced options" toggle for optional fields

3. **Provide Sensible Defaults**
   - Optional fields that have common values should default:
     - `CustomerDeclinedCredit: false`
     - `DeclinedEmail: false`
     - `DeclinedPhone: false`
     - `CustomEquipmentValue: 0`
     - `SafetyGlassCoverage: false` (unless collision/comp selected)
     - Most discount flags: `false`

4. **Simplify Conditional Logic**
   - Only show conditional fields when their parent field triggers them
   - Example: Only show `PriorExpirationDate` if user says they have prior insurance

### Phase 2: Progressive Disclosure UX Pattern

1. **Step 1: Basic Info (Customer)**
   - Name (first, last)
   - Address (street, city, state, zip)
   - Time at residence
   - Prior insurance? (yes/no)
     - If yes: Expand to show prior carrier fields
     - If no: Show reason dropdown

2. **Step 2: Drivers**
   - For each driver:
     - Name, DOB, gender, marital status
     - License status
     - How long licensed (if applicable)
     - Relationship to named insured
     - Residency status (own/rent/lease)
     - Residency type (home/apartment/condo)
     - Property insurance? (yes/no)

3. **Step 3: Vehicles**
   - For each vehicle:
     - VIN lookup → auto-fills year, make, model, body type
     - Use type (commute, pleasure, business)
     - Assigned driver (dropdown)
     - Annual miles, commute miles, % to work
     - Coverage selections:
       - Collision deductible
       - Comprehensive deductible
       - Rental coverage
       - Towing coverage

4. **Step 4: Policy Coverages**
   - Liability limits (BI and PD)
   - Medical payments limit
   - Uninsured motorist BI limit
   - Uninsured motorist PD/CDW
   - Accidental death limit

5. **Step 5: Quote Options**
   - Effective date
   - Policy type (new business, rewrite, etc)
   - Term (6-month, 12-month)
   - Payment method

### Phase 3: Smart Defaults & Assistive Validation

1. **State-Specific Defaults**
   - Use state minimums for liability limits as defaults
   - CA minimum: 15/30/5 → Default to 25/50/25 (higher than minimum)

2. **VIN Decoder Integration**
   - When user enters VIN, auto-populate:
     - Year, make, model, body type
     - Reduces typing, eliminates errors

3. **Address Validation**
   - Integrate with USPS or Google Places API
   - Validate address, auto-complete city/state/zip

4. **Prior Carrier Lookup**
   - Provide searchable dropdown of common carriers
   - Reduce typos in carrier names

### Phase 4: Backend Payload Construction

1. **Build Complete Payload Server-Side**
   - Widget collects only required fields from user
   - Server adds:
     - Auto-generated IDs (quote ID, driver IDs, vehicle IDs)
     - Default values for all optional fields
     - Carrier information (from env/config)
     - Normalized/sanitized values

2. **Validation Before Submission**
   - Validate against JSON Schema contract before hitting rating API
   - Return user-friendly errors if validation fails
   - Suggest corrections (e.g., "License status 'Valid' requires months licensed")

## Implementation Checklist

### Immediate (Week 1)
- [ ] Add schema fetching endpoint to MCP server
- [ ] Parse CA contract schema and extract required fields
- [ ] Create minimal field map JSON file
- [ ] Update insurance state widget to hide optional fields
- [ ] Test with minimal payload → ensure quote succeeds

### Short-term (Week 2-3)
- [ ] Implement VIN decoder integration
- [ ] Add address validation/autocomplete
- [ ] Create searchable prior carrier dropdown
- [ ] Refactor widget into step-by-step flow (5 steps)
- [ ] Add "advanced options" toggle for power users

### Medium-term (Month 1)
- [ ] Build dynamic form generator from schema
- [ ] Support multiple states (fetch schema per state)
- [ ] Add field-level help text from schema descriptions
- [ ] Implement smart defaults based on state regulations
- [ ] Add validation feedback in real-time

### Long-term (Month 2+)
- [ ] Machine learning for default suggestions based on prior quotes
- [ ] A/B test different form lengths to optimize conversion
- [ ] Add "quick quote" mode (even fewer fields, ranges instead of exact values)
- [ ] Multi-language support for field labels

## Success Metrics

1. **Form Completion Time**
   - Target: Reduce from ~15 minutes to <5 minutes
   - Measure: Time from widget open to quote submission

2. **Field Count**
   - Current: ~80-100 fields
   - Target: ~30-40 required fields
   - Optional: Available via "advanced options"

3. **Quote Success Rate**
   - Target: 95%+ of submissions generate valid quotes
   - Track: API errors, validation failures

4. **User Drop-off Rate**
   - Measure: % of users who abandon form mid-flow
   - Target: <20% drop-off rate

## Technical Architecture

```
┌─────────────────────────────────────────────┐
│  User fills minimal widget form             │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Widget sends only required fields          │
│  via sendFollowUpMessage() to assistant     │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Assistant calls request-personal-auto-rate │
│  with minimal payload                       │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  MCP Server enriches payload:               │
│  - Adds defaults for optional fields        │
│  - Adds carrier information                 │
│  - Normalizes/validates against schema      │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Server POSTs to zrater.io rating API      │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  Rating results returned                    │
│  - Widget displays carriers inline          │
│  - Quote ID injected into conversation      │
└─────────────────────────────────────────────┘
```

## Open Questions

1. **Should we support "quick quote" vs "full quote" modes?**
   - Quick: Minimal fields, faster but less accurate pricing
   - Full: All fields, slower but exact pricing

2. **How to handle state-specific requirements?**
   - Fetch schema per state on widget load
   - Or pre-fetch all state schemas and cache

3. **VIN decoder: Build in-house or use 3rd party API?**
   - NHTSA (free, rate-limited)
   - Commercial services (paid, faster, more data)

4. **Should optional fields be collapsible sections or separate "advanced" tab?**
   - UX consideration for power users vs typical users

## Next Steps

1. Review this plan with team
2. Prioritize immediate checklist items
3. Spike: Test minimal payload against zrater.io to ensure it works
4. Design mockups for new 5-step widget flow
5. Begin implementation of Phase 1

---

**Document Owner:** Development Team
**Last Updated:** 2026-02-17
**Status:** Draft - Awaiting Review
