# Wizard Flow Specification

**Purpose**: Complete specification of the 5-step wizard UI from commit `a013415` to recreate it in a config-driven architecture.

---

## Overview

A **5-step wizard interface** for collecting personal auto insurance quote data with:
- Visual stepper indicator
- Form validation
- Review/edit capability
- Structured data submission

---

## Wizard Steps

### Step 1: Policy Setup
**Purpose**: Configure basic policy parameters

**Fields**:
```json
{
  "effectiveDate": {
    "type": "date",
    "label": "Effective Date",
    "required": true,
    "default": "today"
  },
  "term": {
    "type": "select",
    "label": "Term",
    "required": true,
    "options": ["Semi Annual", "Annual"],
    "default": "Semi Annual"
  },
  "paymentMethod": {
    "type": "select",
    "label": "Payment Method",
    "required": true,
    "options": ["Standard", "Electronic Funds Transfer", "Paid In Full", "Default"],
    "default": "Electronic Funds Transfer"
  },
  "policyType": {
    "type": "select",
    "label": "Policy Type",
    "required": true,
    "options": ["Standard", "Preferred", "Non-Standard"],
    "default": "Standard"
  },
  "bumpLimits": {
    "type": "select",
    "label": "Bump Limits",
    "required": true,
    "options": ["Bump Up", "Bump Down", "No Bumping"],
    "default": "Bump Up"
  },
  "customerDeclinedCredit": {
    "type": "checkbox",
    "label": "Customer Declined Credit",
    "default": false
  }
}
```

---

### Step 2: Customer Information
**Purpose**: Collect customer personal and contact details

**Sections**:

#### Personal Information
```json
{
  "firstName": {
    "type": "text",
    "label": "First Name",
    "required": true,
    "placeholder": "John"
  },
  "middleName": {
    "type": "text",
    "label": "Middle Name",
    "required": false
  },
  "lastName": {
    "type": "text",
    "label": "Last Name",
    "required": true,
    "placeholder": "Smith"
  },
  "monthsAtResidence": {
    "type": "number",
    "label": "Months at Residence",
    "required": false,
    "placeholder": "60",
    "default": 60
  }
}
```

#### Address
```json
{
  "street": {
    "type": "text",
    "label": "Street",
    "required": true,
    "placeholder": "123 Main St",
    "fullWidth": true
  },
  "city": {
    "type": "text",
    "label": "City",
    "required": true,
    "placeholder": "Long Beach"
  },
  "state": {
    "type": "select",
    "label": "State",
    "required": true,
    "options": ["ALL_US_STATES"],
    "placeholder": "Select state"
  },
  "county": {
    "type": "text",
    "label": "County",
    "required": false,
    "placeholder": "Los Angeles"
  },
  "zipCode": {
    "type": "text",
    "label": "ZIP Code",
    "required": true,
    "placeholder": "90807",
    "pattern": "^[0-9]{5}$"
  }
}
```

#### Contact Information
```json
{
  "mobilePhone": {
    "type": "tel",
    "label": "Mobile Phone",
    "required": false,
    "placeholder": "562-787-8209"
  },
  "homePhone": {
    "type": "tel",
    "label": "Home Phone",
    "required": false
  },
  "workPhone": {
    "type": "tel",
    "label": "Work Phone",
    "required": false
  },
  "emailAddress": {
    "type": "email",
    "label": "Email Address",
    "required": false,
    "placeholder": "email@example.com"
  },
  "declinedEmail": {
    "type": "checkbox",
    "label": "Declined Email",
    "default": false
  },
  "declinedPhone": {
    "type": "checkbox",
    "label": "Declined Phone",
    "default": false
  }
}
```

#### Prior Insurance
```json
{
  "priorInsurance": {
    "type": "checkbox",
    "label": "Had Prior Insurance",
    "default": false
  },
  "reasonForNoInsurance": {
    "type": "text",
    "label": "Reason for No Insurance",
    "required": false,
    "placeholder": "Other",
    "default": "Other"
  }
}
```

---

### Step 3: Vehicle Details
**Purpose**: Collect vehicle information and coverage preferences

**Sections**:

#### Vehicle Information
```json
{
  "make": {
    "type": "text",
    "label": "Make",
    "required": true,
    "placeholder": "FORD"
  },
  "model": {
    "type": "text",
    "label": "Model",
    "required": true,
    "placeholder": "EDGE SEL"
  },
  "year": {
    "type": "number",
    "label": "Year",
    "required": true,
    "placeholder": "2018"
  },
  "annualMiles": {
    "type": "number",
    "label": "Annual Miles",
    "required": false,
    "placeholder": "13400"
  },
  "milesToWork": {
    "type": "number",
    "label": "Miles to Work",
    "required": false,
    "placeholder": "6",
    "default": 0
  },
  "percentToWork": {
    "type": "number",
    "label": "Percent to Work",
    "required": false,
    "placeholder": "100",
    "default": 100
  },
  "purchaseType": {
    "type": "select",
    "label": "Purchase Type",
    "options": ["New", "Owned", "Financed", "Leased"],
    "default": "New"
  },
  "usage": {
    "type": "select",
    "label": "Usage",
    "options": ["Artisan Use", "Business Use", "Farm", "Pleasure", "Work School"],
    "default": "Work School"
  },
  "odometer": {
    "type": "number",
    "label": "Odometer",
    "required": false,
    "placeholder": "0",
    "default": 0
  },
  "leasedVehicle": {
    "type": "checkbox",
    "label": "Leased Vehicle",
    "default": false
  },
  "rideShare": {
    "type": "checkbox",
    "label": "RideShare",
    "default": false
  },
  "salvaged": {
    "type": "checkbox",
    "label": "Salvaged",
    "default": false
  }
}
```

#### Garaging Address
```json
{
  "garagingStreet": {
    "type": "text",
    "label": "Street",
    "required": false,
    "placeholder": "Same as customer address",
    "fullWidth": true
  },
  "garagingCity": {
    "type": "text",
    "label": "City",
    "required": false
  },
  "garagingState": {
    "type": "select",
    "label": "State",
    "required": false,
    "options": ["ALL_US_STATES"]
  },
  "garagingZip": {
    "type": "text",
    "label": "ZIP Code",
    "required": false
  }
}
```

#### Coverage Information
```json
{
  "collisionDeductible": {
    "type": "select",
    "label": "Collision Deductible",
    "options": ["None", "250", "500", "1000"],
    "default": "None"
  },
  "comprehensiveDeductible": {
    "type": "select",
    "label": "Comprehensive Deductible",
    "options": ["None", "250", "500", "1000"],
    "default": "None"
  },
  "rentalLimit": {
    "type": "select",
    "label": "Rental Limit",
    "options": ["None", "500", "1000"],
    "default": "None"
  },
  "towingLimit": {
    "type": "select",
    "label": "Towing Limit",
    "options": ["None", "500", "1000"],
    "default": "None"
  },
  "customEquipmentValue": {
    "type": "number",
    "label": "Custom Equipment Value",
    "required": false,
    "placeholder": "0",
    "default": 0
  },
  "gapCoverage": {
    "type": "checkbox",
    "label": "Gap Coverage",
    "default": false
  },
  "safetyGlassCoverage": {
    "type": "checkbox",
    "label": "Safety Glass Coverage",
    "default": false
  }
}
```

---

### Step 4: Driver Information
**Purpose**: Collect driver details, license info, and discounts

**Sections**:

#### Driver Details
```json
{
  "driverFirstName": {
    "type": "text",
    "label": "First Name",
    "required": true,
    "placeholder": "CATest"
  },
  "driverMiddleName": {
    "type": "text",
    "label": "Middle Name",
    "required": false
  },
  "driverLastName": {
    "type": "text",
    "label": "Last Name",
    "required": true,
    "placeholder": "LongBeach"
  },
  "dateOfBirth": {
    "type": "date",
    "label": "Date of Birth",
    "required": true
  },
  "gender": {
    "type": "select",
    "label": "Gender",
    "options": ["Male", "Female"],
    "default": "Male"
  },
  "maritalStatus": {
    "type": "select",
    "label": "Marital Status",
    "options": ["Single", "Married", "Divorced", "Widowed"],
    "default": "Single"
  },
  "occupation": {
    "type": "text",
    "label": "Occupation",
    "required": false,
    "placeholder": "Engineer"
  },
  "industry": {
    "type": "text",
    "label": "Industry",
    "required": false,
    "placeholder": "Engineer/Architect/Science/Math"
  },
  "monthsEmployed": {
    "type": "number",
    "label": "Months Employed",
    "required": false,
    "placeholder": "0",
    "default": 0
  }
}
```

#### License Information
```json
{
  "licenseStatus": {
    "type": "select",
    "label": "License Status",
    "options": ["Valid", "Expired", "Suspended", "Revoked"],
    "default": "Valid"
  },
  "stateLicensed": {
    "type": "select",
    "label": "State Licensed",
    "required": true,
    "options": ["ALL_US_STATES"]
  },
  "monthsLicensed": {
    "type": "number",
    "label": "Months Licensed",
    "required": false,
    "placeholder": "335",
    "default": 335
  },
  "monthsStateLicensed": {
    "type": "number",
    "label": "Months State Licensed",
    "required": false,
    "placeholder": "335",
    "default": 335
  },
  "monthsMvrExperience": {
    "type": "number",
    "label": "Months MVR Experience",
    "required": false,
    "placeholder": "60",
    "default": 60
  },
  "monthsSuspended": {
    "type": "number",
    "label": "Months Suspended",
    "required": false,
    "placeholder": "0",
    "default": 0
  },
  "foreignNational": {
    "type": "checkbox",
    "label": "Foreign National",
    "default": false
  },
  "internationalLicense": {
    "type": "checkbox",
    "label": "International License",
    "default": false
  }
}
```

#### Attributes
```json
{
  "educationLevel": {
    "type": "select",
    "label": "Education Level",
    "options": ["Some College", "High School", "Bachelor", "Graduate"],
    "default": "Some College"
  },
  "relation": {
    "type": "select",
    "label": "Relation",
    "options": ["Insured", "Spouse", "Child", "Parent"],
    "default": "Insured"
  },
  "residencyStatus": {
    "type": "select",
    "label": "Residency Status",
    "options": ["Own", "Rent", "Lease"],
    "default": "Own"
  },
  "residencyType": {
    "type": "select",
    "label": "Residency Type",
    "options": ["Home", "Apartment", "Condo", "Mobile Home"],
    "default": "Home"
  },
  "driverMilesToWork": {
    "type": "number",
    "label": "Miles to Work",
    "required": false,
    "placeholder": "0",
    "default": 0
  },
  "propertyInsurance": {
    "type": "checkbox",
    "label": "Property Insurance",
    "default": false
  }
}
```

#### Discounts
```json
{
  "defensiveDriving": {
    "type": "checkbox",
    "label": "Defensive Driving",
    "default": false
  },
  "goodStudent": {
    "type": "checkbox",
    "label": "Good Student",
    "default": false
  },
  "seniorDriver": {
    "type": "checkbox",
    "label": "Senior Driver",
    "default": false
  },
  "multiplePolicies": {
    "type": "checkbox",
    "label": "Multiple Policies",
    "default": false
  }
}
```

#### SR-22 Information
```json
{
  "sr22": {
    "type": "checkbox",
    "label": "SR-22 Required",
    "default": false
  },
  "sr22Reason": {
    "type": "text",
    "label": "SR-22 Reason",
    "required": false,
    "placeholder": "Other",
    "default": "Other"
  },
  "sr22State": {
    "type": "select",
    "label": "SR-22 State",
    "required": false,
    "options": ["ALL_US_STATES"],
    "default": "California"
  },
  "sr22Date": {
    "type": "date",
    "label": "SR-22 Date",
    "required": false
  }
}
```

---

### Step 5: Review & Submit
**Purpose**: Show collected data with edit capabilities, then submit

**Layout**:
- Review sections grouped by wizard step
- Each section has "Edit" button to go back to that step
- Shows formatted summary of all collected fields
- "Confirm & Submit" button at bottom

**Review Sections**:
1. **Policy Setup**
   - Effective Date, Term, Payment Method, Policy Type, Bump Limits
   - Edit button → goToStep(1)

2. **Customer Information**
   - Name, Address, Email, Phone
   - Edit button → goToStep(2)

3. **Vehicle**
   - Year Make Model, Usage
   - Edit button → goToStep(3)

4. **Driver**
   - Name, DOB, Gender, Marital Status
   - Edit button → goToStep(4)

---

## Visual Design

### Stepper Component
```
┌────┐        ┌────┐        ┌────┐        ┌────┐        ┌────┐
│ 1  │───────│ 2  │───────│ 3  │───────│ 4  │───────│ 5  │
└────┘        └────┘        └────┘        └────┘        └────┘
Policy      Customer     Vehicle       Driver        Review
Setup        Info

States:
- Active: Blue background, white text, shadow
- Completed: Green background, white text
- Pending: Gray background, gray text
```

### Layout Grid
- Most fields use 2-column responsive grid
- Full-width fields marked with `fullWidth: true`
- Sections have titles
- Form groups visually separated

### Animations
- Step transitions: fade-in with slide-up (300ms)
- Button hover effects
- Focus states on inputs

---

## Behavior

### Navigation
- **Next Button**: Advances to next step (1→2→3→4→5)
- **Previous Button**: Goes back one step (hidden on step 1)
- **Step 5 Next Button**: Shows "Confirm & Submit" text

### Validation
Runs before submission (step 5):

**Required Fields**:
```javascript
{
  // Step 1
  "effectiveDate": "required",

  // Step 2
  "firstName": "required",
  "lastName": "required",
  "street": "required",
  "city": "required",
  "state": "required",
  "zipCode": "required",

  // Step 3
  "make": "required",
  "model": "required",
  "year": "required",

  // Step 4
  "driverFirstName": "required",
  "driverLastName": "required",
  "dateOfBirth": "required",
  "stateLicensed": "required (or falls back to customer state)"
}
```

**Validation Errors**:
- Displayed in alert dialog
- Lists all missing required fields
- Prevents submission until fixed

### State Management
- All form data stored in `formData` object
- State persists across steps
- Two-way binding with inputs
- Checkbox fields: boolean values
- Number fields: integer or null
- Text fields: string values

### Review Edit Flow
1. User clicks "Edit" button in review section
2. Calls `goToStep(stepNumber)`
3. Returns to that step with data preserved
4. User makes changes
5. Clicks "Next" to return to review

---

## Submission

### Payload Structure
Submits via `window.openai.sendFollowUpMessage()` with structured JSON:

```json
{
  "Identifier": "generated-id",
  "EffectiveDate": "ISO-8601",
  "Customer": {
    "FirstName": "...",
    "Address": {...},
    "ContactInformation": {...}
  },
  "PolicyCoverages": {
    "LiabilityBiLimit": "30000/60000",
    ...
  },
  "RatedDrivers": [{...}],
  "Vehicles": [{...}],
  "CarrierInformation": {
    "Products": [...]
  }
}
```

### Submission Flow
1. User clicks "Confirm & Submit" on step 5
2. Validation runs
3. If valid: Button text → "Submitting..."
4. Build payload from formData
5. Call `window.openai.sendFollowUpMessage()` with prompt
6. Button text → "Submitted!"
7. MCP tool `request-personal-auto-rate` called by assistant

---

## Testing Features

### Test Data Fill Button
- Shown when `window.IS_TESTING = true`
- Button: "🧪 Fill Test Data"
- Populates all fields with valid test data:
  - Customer: John Smith, Beverly Hills
  - Vehicle: 2018 Honda Civic
  - Driver: matches customer, born 1990-01-15
  - Policy: today's date

---

## Config-Driven Mapping

### How to Make This Config-Driven:

#### 1. **Wizard Configuration JSON**
```json
{
  "wizard_name": "personal_auto_quote",
  "title": "Complete Your Insurance Application",
  "description": "We'll guide you through 5 quick steps",
  "steps": [
    {
      "id": 1,
      "name": "policy_setup",
      "title": "Policy Setup",
      "label": "Policy Setup",
      "sections": [
        {
          "title": "Policy Details",
          "fields": ["effectiveDate", "term", "paymentMethod", ...]
        }
      ]
    },
    ...
  ],
  "review_step": {
    "enabled": true,
    "sections": [
      {
        "title": "Policy Setup",
        "fields": ["effectiveDate", "term", ...],
        "edit_step": 1
      },
      ...
    ]
  },
  "validation": {
    "required_fields": ["effectiveDate", "firstName", ...]
  },
  "submission": {
    "tool_name": "request-personal-auto-rate",
    "payload_mapping": {...}
  }
}
```

#### 2. **Field Definitions Reference**
Reference fields from `fields.json` by name

#### 3. **Step Rendering Engine**
- Reads wizard config
- Loads field definitions
- Generates form UI dynamically
- Handles validation from config
- Maps to API payload via config

---

## Key Differences from Conversational Flow

| Feature | Wizard (Commit a013415) | Adaptive/Conversational |
|---------|-------------------------|-------------------------|
| **UI** | 5-step visual wizard | Chat-based, no visual steps |
| **Navigation** | Next/Previous buttons | Natural language responses |
| **Review** | Dedicated step 5 with edit buttons | Optional review mode in flow |
| **Submission** | Single payload at end | Progressive collection |
| **Field Order** | Fixed by step | Order-agnostic |
| **Validation** | At submission | Continuous during collection |
| **User Control** | Can go back anytime | Can correct during review |

---

## Implementation Priority

### Must Have (Core Wizard):
1. ✅ 5-step structure
2. ✅ Visual stepper indicator
3. ✅ Form fields per step
4. ✅ Navigation (next/previous)
5. ✅ Review step with edit buttons
6. ✅ Validation before submit
7. ✅ Structured payload submission

### Should Have:
1. ✅ Animated transitions
2. ✅ Responsive grid layout
3. ✅ Test data fill button
4. ✅ Dark mode support

### Could Have:
1. ⚪ Progress percentage
2. ⚪ Save draft functionality
3. ⚪ Field-level validation (real-time)
4. ⚪ Conditional field visibility

---

## Next Steps

When back on `main` branch:

1. **Create wizard config JSON** based on this spec
2. **Map fields** from field_registry.json to wizard steps
3. **Build wizard renderer** that reads config
4. **Add wizard flow** to flow_configs.json
5. **Test end-to-end** with config-driven approach

---

## Files to Reference

On commit `a013415`:
- `insurance_server_python/insurance_wizard_widget.py` - Full wizard HTML/JS
- Tool handler that invokes `request-personal-auto-rate`
- Widget registration in `widget_registry.py`

---

## Summary

**Total Fields**: ~80 fields across 4 collection steps
**UI Pattern**: Multi-step wizard with visual progress indicator
**Data Flow**: Collect → Review → Submit single payload
**Key Feature**: Editable review step before final submission

This specification captures all details needed to recreate the wizard flow in a config-driven architecture when returning to the main branch.
