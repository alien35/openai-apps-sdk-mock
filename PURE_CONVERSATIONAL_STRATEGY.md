# Pure Conversational Batch Collection Strategy

## Core Concept
Insurance quote collection happens through **pure conversational batches** - no forms, just Claude asking questions and users responding naturally in chat.

## Key Principles

1. **No Form Widgets**: Users only interact via ChatGPT's text input
2. **Batch Collection**: Information gathered in logical groups (Customer → Drivers → Vehicles)
3. **Forward-Only Flow**: Missing fields from earlier batches get appended to the next batch
4. **Reduce Fatigue**: Don't go back and ask again - just catch it in the next batch

---

## Conversational Flow

### Batch 1: Customer Information (8 required fields)
**Claude asks:**
"Let's get your quote started! I need some basic information:
- Your full name
- Your address (street, city, state, ZIP)
- How many months you've lived there
- Whether you currently have insurance"

**User responds naturally:**
"I'm John Smith at 123 Main St, San Francisco CA 94102. I've been here for 24 months and yes I have insurance."

**Claude validates:**
- Extracts: FirstName, LastName, Address (Street, City, State, ZIP), MonthsAtResidence, PriorInsurance
- Calls `collect-customer-info` tool with extracted data
- If missing fields: Notes them for next batch
- Proceeds to Batch 2

---

### Batch 2: Driver Information (10 required fields per driver)
**Claude asks (including any missing customer fields):**
"Great! Now let's talk about the drivers. For each driver I need:
- Full name
- Date of birth
- Gender and marital status
- License status
- Whether they have property insurance
- Their relationship to you
- Residency status and type

*[If customer address.state was missing]:* Also, what state is your address in?"

**User responds:**
"That's me - John Smith, born 1/1/1980, male, married, valid license, I have property insurance, I'm the primary, US citizen, owner."

**Claude:**
- Extracts driver data + any missing customer fields
- Updates customer info if needed
- Calls `collect-driver-info` tool
- Asks: "Any other drivers?"
- If yes: repeats for next driver
- If no: proceeds to Batch 3

---

### Batch 3: Vehicle Information (15 required fields per vehicle)
**Claude asks (including any missing driver/customer fields):**
"Perfect! Now tell me about your vehicle(s):
- VIN
- Year, make, model, body type
- How it's used (commute, pleasure, business)
- Who drives it (driver ID or name)
- Coverage preferences (collision/comprehensive deductibles, rental, towing)
- Annual miles, commute miles, percent used for work

*[If driver DateOfBirth was missing]:* Also, what's your date of birth?"

**User responds:**
"2020 Honda Accord sedan, VIN 1HGCV1F3XLA123456, I use it for commuting, I drive it, $500 collision and comprehensive, $50/day rental coverage, $100 towing, 12,000 miles/year, 20 miles each way to work, 80% for commuting."

**Claude:**
- Extracts vehicle data + any missing fields
- Updates earlier records if needed
- Calls `collect-vehicle-info` tool
- Asks: "Any other vehicles?"
- If no: Proceeds to rate request

---

### Final: Submit Rate Request
**Claude:**
"Perfect! I have everything I need. Let me submit your quote request..."

- Calls `request-personal-auto-rate` with complete payload
- Shows results via `retrieve-personal-auto-rate-results` or displays inline

---

## Technical Implementation

### Tool Schema Design

Each batch tool accepts the **full data structure** (not just that batch), allowing forward-appending of missed fields:

```python
# collect-customer-info
{
  "customer": {
    "firstName": "string",
    "lastName": "string",
    "address": {...},
    "monthsAtResidence": "number",
    "priorInsurance": "boolean"
  }
}

# collect-driver-info (can also update customer if needed)
{
  "customer": {...},  # Optional - for appending missing fields
  "drivers": [
    {
      "firstName": "string",
      "lastName": "string",
      "dateOfBirth": "string",
      # ... 10 required fields
    }
  ]
}

# collect-vehicle-info (can also update customer/drivers if needed)
{
  "customer": {...},  # Optional
  "drivers": [...],    # Optional
  "vehicles": [
    {
      "vin": "string",
      "year": "number",
      "make": "string",
      # ... 15 required fields
    }
  ]
}
```

### Validation Strategy

Claude tracks what's been collected in each batch:

```javascript
// Conceptual state tracking (Claude does this in conversation context)
{
  customer: {
    complete: false,
    missing: ["address.state"],
    collected: ["firstName", "lastName", ...]
  },
  drivers: [
    {
      complete: true,
      missing: [],
      collected: [...]
    }
  ],
  vehicles: [
    {
      complete: false,
      missing: ["assignedDriverId"],
      collected: [...]
    }
  ]
}
```

**Validation Rules:**
1. After each batch, Claude notes missing required fields
2. Missing fields get appended to next batch's questions
3. Only proceed to rate request when ALL required fields collected
4. Don't go back - always move forward

---

## Backend Changes Needed

### 1. Update Tool Schemas
- `collect-customer-info`: Accepts customer object, returns validation status
- `collect-driver-info`: Accepts customer + drivers array, returns validation
- `collect-vehicle-info`: Accepts customer + drivers + vehicles, returns validation
- Each tool should accept optional fields from other batches for forward-appending

### 2. Tool Response Format
Each tool returns:
```json
{
  "structured_content": {
    "customer": {...},
    "drivers": [...],
    "vehicles": [...],
    "validation": {
      "customer_complete": true/false,
      "drivers_complete": true/false,
      "vehicles_complete": true/false,
      "missing_fields": ["customer.address.state", "driver[0].dateOfBirth"]
    }
  },
  "response_text": "Captured customer information for John Smith. Still need: address state."
}
```

### 3. State Management
Tools maintain cumulative state across batches:
- First call to `collect-customer-info` stores customer data
- Later call to `collect-driver-info` can append missing customer fields
- Final call to `collect-vehicle-info` can append any remaining missing fields

---

## Benefits

1. **Zero UI Complexity**: No form widgets, no navigation, no Submit buttons
2. **Natural Conversation**: Users describe things in their own words
3. **Flexible**: Can answer in any order or format
4. **Forward-Only**: Reduces conversation fatigue by not going back
5. **Forgiving**: Can clarify, ask questions, handle edge cases conversationally

---

## Implementation Phases

### Phase 1: Tool Schema Updates (2-3 hours)
- Update existing `collect-customer-info` tool
- Add cumulative state support
- Add validation response with missing fields

### Phase 2: Add Driver/Vehicle Collection Tools (2-3 hours)
- Implement `collect-driver-info` with cross-batch field support
- Implement `collect-vehicle-info` with cross-batch field support
- Each tool can append missing fields from earlier batches

### Phase 3: Prompt Engineering (2-3 hours)
- Train Claude to ask in batches
- Extract data from natural language responses
- Track missing fields and append to next batch
- Only proceed when all required fields collected

### Phase 4: Backend Integration (1-2 hours)
- Ensure rate request tool receives complete payload
- Apply defaults for optional fields (existing `build_minimal_payload_with_defaults`)
- Test end-to-end flow

**Total: 7-11 hours**

---

## Example Complete Flow

```
User: "I need car insurance"

Claude: "I'd be happy to help! Let's start with your basic information.
What's your name, address, how long you've lived there, and do you currently have insurance?"

User: "John Smith, 123 Main St San Francisco CA 94102, 2 years, yes"

Claude: [Calls collect-customer-info]
"Perfect! Now tell me about the drivers..."

User: "Just me - DOB 1/1/1980, male, married, valid license..."

Claude: [Calls collect-driver-info]
"Great! Any other drivers?"

User: "No, just me"

Claude: "Got it. Now tell me about your vehicle..."

User: "2020 Honda Accord..."

Claude: [Calls collect-vehicle-info]
[Calls request-personal-auto-rate]
"Here are your quotes: [displays results widget]"
```

---

## Key Difference from Previous Strategy

**Before**: Forms with Submit buttons alongside conversation
**Now**: Pure conversation, no forms, forward-only flow with missing fields appended to next batch
