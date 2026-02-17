# Conversational Batch Collection Strategy

## Core Concept
Insurance quote collection happens through **conversational batches** managed by Direct Sales Assistant in ChatGPT, with form widgets as optional helpers.

## Flow

**Batch 1: Customer Info (8 fields)**
- Direct Sales Assistant: "Let's get your quote started. Can you tell me your name, address, how long you've lived there, and whether you currently have insurance?"
- User Option A: Types in chat "I'm John Smith, 123 Main St, SF CA 94102, 24 months, yes I have insurance"
- User Option B: Fills form widget and clicks "Submit Customer Info"
- Direct Sales Assistant validates → proceeds to Batch 2

**Batch 2: Driver Info (10 fields per driver)**
- Direct Sales Assistant: "Great! Now tell me about the drivers. For each driver I need: name, DOB, gender, marital status, license status, and a few other details."
- User Option A: Types "Driver is me, John Smith, DOB 1/1/1980, male, married, valid license..."
- User Option B: Fills driver form and clicks "Submit Driver Info"
- Direct Sales Assistant: "Got it! Any other drivers?" → If yes, repeat; if no, proceed to Batch 3

**Batch 3: Vehicle Info (15 fields per vehicle)**
- Direct Sales Assistant: "Now let's add your vehicle(s)..."
- User provides via chat or form
- Direct Sales Assistant validates → proceeds to final quote

## Technical Implementation

### Widget Types
- **collect-customer-info** tool: Shows 8-field customer form with "Submit Customer Info" button
- **collect-driver-info** tool: Shows 10-field driver form with "Submit Driver Info" button  
- **collect-vehicle-info** tool: Shows 15-field vehicle form with "Submit Vehicle Info" button

### Tool Schemas
Each tool accepts OPTIONAL pre-population parameters:

```python
# collect-customer-info
{
    "firstName": "string",     # Direct Sales Assistant extracted from chat
    "lastName": "string",
    "address": {...},
    # ... etc
}

# If user already provided info in chat, Direct Sales Assistant calls tool with pre-filled data
# If not, Direct Sales Assistant calls tool with empty params, user fills form manually
```

### Widget Behavior
1. Widget receives pre-populated data (if any)
2. Shows form with fields filled or empty
3. User can edit/complete fields
4. Clicks "Submit [Batch] Info" button
5. Widget calls rate tool OR returns data to Direct Sales Assistant
6. Direct Sales Assistant validates completeness, asks follow-ups if needed
7. Once batch complete, Direct Sales Assistant moves to next batch

### Validation Logic
Direct Sales Assistant tracks what's been collected:
```
batchesComplete = {
  customer: false,
  drivers: [],     # Track each driver separately
  vehicles: []     # Track each vehicle separately  
}

# Only proceed to next batch when current batch complete
# Only call final rate tool when ALL batches complete
```

## Benefits

1. **Flexible**: User chooses chat vs form
2. **Conversational**: Natural back-and-forth dialog
3. **Progressive**: One batch at a time reduces overwhelm
4. **Validating**: Can't proceed with incomplete data
5. **Forgiving**: Can answer questions, clarify requirements

## Implementation Phases

### Phase 1: Split Widget into Batch Widgets (3-4 hours)
- Create 3 separate widgets: customer-form, driver-form, vehicle-form
- Each shows only required fields for that batch
- Each has its own "Submit" button
- Remove multi-step navigation

### Phase 2: Update Tool Schemas (2 hours)
- Create 3 new tools: collect-customer-info, collect-driver-info, collect-vehicle-info
- Each accepts optional pre-population params
- Each returns structured data when submitted

### Phase 3: Add Pre-Population Logic (2 hours)
- Widget reads initialData from tool invocation
- Pre-fills fields if data provided
- Leaves empty if not

### Phase 4: Add Validation & Progress (2 hours)
- Show "X/Y fields complete" in each widget
- Disable Submit until all required fields filled
- Green checkmarks on completed fields

### Phase 5: Prompt Engineering (2 hours)
- Train Direct Sales Assistant to collect in batches
- Extract data from chat, pass to tools
- Validate completeness before proceeding
- Handle conversational back-and-forth

**Total: 11-14 hours**

## Key Decision: Separate Tools vs Single Tool

**Option A: Three Separate Tools** (Recommended)
- `collect-customer-info`
- `collect-driver-info`  
- `collect-vehicle-info`

Pros: Clear intent, easier validation, better UX
Cons: More tools to maintain

**Option B: Single Tool with Mode Parameter**
- `collect-insurance-info` with `mode: "customer" | "driver" | "vehicle"`

Pros: Fewer tools
Cons: Less clear, harder to validate

**Recommendation: Option A** for clarity and maintainability.

