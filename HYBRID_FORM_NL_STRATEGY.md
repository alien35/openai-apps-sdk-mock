# Strategy: Conversational Batch Collection with Form Assistance

## Goal  
Create a streamlined insurance quote flow that:
1. Collects information in **logical batches** (Customer → Drivers → Vehicles)
2. Each batch asks for ONLY required fields (8-15 fields per batch)
3. Users can respond via **natural language chat** OR **structured form**
4. System validates completeness before moving to next batch
5. Conversational flow managed by Claude, not by widget navigation

## Key Insight
This is a **conversational wizard** where:
- Claude asks for one batch at a time in chat
- Widget is a **form helper** for that specific batch  
- User chooses: type naturally in chat OR fill form and click "Submit"
- Claude validates completeness and proceeds to next batch
- No multi-step navigation in widget - each widget = one batch

---

## Conversational Flow Examples

### Example 1: User Provides Info via Chat

```
User: "I need car insurance"