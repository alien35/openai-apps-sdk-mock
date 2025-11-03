"""Insurance state selector widget markup for the Python MCP server."""

INSURANCE_STATE_WIDGET_HTML = """
<div id="insurance-state-root"></div>
<style>
  :root {
    color-scheme: light dark;
  }

  #insurance-state-root {
    font-family: "Inter", "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont,
      "Helvetica Neue", Arial, sans-serif;
    color: rgba(0, 0, 0, 0.82);
  }

  @media (prefers-color-scheme: dark) {
    #insurance-state-root {
      color: rgba(255, 255, 255, 0.88);
    }
  }

  .insurance-widget {
    background: rgba(255, 255, 255, 0.94);
    border-radius: 20px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    box-shadow: 0 18px 48px rgba(15, 23, 42, 0.12);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget {
      background: rgba(15, 23, 42, 0.92);
      border-color: rgba(255, 255, 255, 0.12);
      box-shadow: 0 18px 48px rgba(0, 0, 0, 0.45);
    }
  }

  .insurance-widget__eyebrow {
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.14em;
    font-weight: 600;
    color: rgba(99, 102, 241, 0.9);
  }

  .insurance-widget__title {
    font-size: 20px;
    line-height: 1.3;
    font-weight: 700;
    margin: 0;
  }

  .insurance-widget__description {
    margin: 0;
    font-size: 14px;
    line-height: 1.6;
    color: rgba(15, 23, 42, 0.74);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__description {
      color: rgba(226, 232, 240, 0.72);
    }
  }

  .insurance-widget__search {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .insurance-widget__form {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .insurance-widget__field {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .insurance-widget__label {
    font-size: 13px;
    font-weight: 600;
    color: rgba(15, 23, 42, 0.72);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__label {
      color: rgba(226, 232, 240, 0.78);
    }
  }

  .insurance-widget__select {
    border: 1px solid rgba(15, 23, 42, 0.12);
    border-radius: 12px;
    padding: 0 14px;
    background: rgba(255, 255, 255, 0.96);
    transition: border 120ms ease, box-shadow 120ms ease;
  }

  .insurance-widget__select select {
    width: 100%;
    border: none;
    outline: none;
    height: 42px;
    background: transparent;
    color: inherit;
    font-size: 14px;
    appearance: none;
  }

  .insurance-widget__select:focus-within {
    border-color: rgba(99, 102, 241, 0.65);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.18);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__select {
      background: rgba(15, 23, 42, 0.88);
      border-color: rgba(148, 163, 184, 0.28);
    }

    .insurance-widget__select:focus-within {
      border-color: rgba(99, 102, 241, 0.8);
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.28);
    }
  }

  .insurance-widget__input {
    position: relative;
    display: flex;
    align-items: center;
    gap: 8px;
    border: 1px solid rgba(15, 23, 42, 0.12);
    border-radius: 12px;
    padding: 0 14px;
    background: rgba(255, 255, 255, 0.96);
    transition: border 120ms ease, box-shadow 120ms ease;
  }

  .insurance-widget__input:focus-within {
    border-color: rgba(99, 102, 241, 0.65);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.18);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__input {
      background: rgba(15, 23, 42, 0.88);
      border-color: rgba(148, 163, 184, 0.28);
    }

    .insurance-widget__input:focus-within {
      border-color: rgba(99, 102, 241, 0.8);
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.28);
    }
  }

  .insurance-widget__input input {
    width: 100%;
    border: none;
    outline: none;
    height: 42px;
    background: transparent;
    color: inherit;
    font-size: 14px;
  }

  .insurance-widget__input input::placeholder {
    color: rgba(15, 23, 42, 0.45);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__input input::placeholder {
      color: rgba(226, 232, 240, 0.45);
    }
  }

  .insurance-widget__message {
    font-size: 12px;
    min-height: 16px;
    color: rgba(220, 38, 38, 0.8);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__message {
      color: rgba(252, 165, 165, 0.9);
    }
  }

  .insurance-widget__options {
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-radius: 12px;
    padding: 4px;
    max-height: 240px;
    overflow-y: auto;
    display: grid;
    gap: 4px;
    background: rgba(248, 250, 252, 0.72);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__options {
      border-color: rgba(148, 163, 184, 0.24);
      background: rgba(30, 41, 59, 0.72);
    }
  }

  .insurance-widget__option {
    border: none;
    background: rgba(255, 255, 255, 0.96);
    color: inherit;
    border-radius: 10px;
    padding: 10px 12px;
    text-align: left;
    font-size: 14px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    gap: 8px;
    transition: background 120ms ease, transform 120ms ease;
  }

  .insurance-widget__option:hover,
  .insurance-widget__option:focus-visible {
    background: rgba(99, 102, 241, 0.12);
    transform: translateY(-1px);
    outline: none;
  }

  .insurance-widget__option.is-selected {
    background: linear-gradient(90deg, rgba(99, 102, 241, 0.22), rgba(79, 70, 229, 0.26));
    box-shadow: inset 0 0 0 1px rgba(79, 70, 229, 0.32);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__option {
      background: rgba(15, 23, 42, 0.92);
    }

    .insurance-widget__option:hover,
    .insurance-widget__option:focus-visible {
      background: rgba(129, 140, 248, 0.22);
    }

    .insurance-widget__option.is-selected {
      background: linear-gradient(90deg, rgba(129, 140, 248, 0.32), rgba(99, 102, 241, 0.38));
      box-shadow: inset 0 0 0 1px rgba(165, 180, 252, 0.55);
    }
  }

  .insurance-widget__option-code {
    font-weight: 600;
    font-size: 12px;
    color: rgba(79, 70, 229, 0.9);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__option-code {
      color: rgba(165, 180, 252, 0.9);
    }
  }

  .insurance-widget__selection {
    font-size: 13px;
    color: rgba(15, 23, 42, 0.68);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__selection {
      color: rgba(226, 232, 240, 0.7);
    }
  }

  .insurance-widget__confirm {
    border: none;
    border-radius: 12px;
    padding: 12px 16px;
    background: linear-gradient(135deg, #6366f1, #4338ca);
    color: #fff;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
    transition: transform 150ms ease, box-shadow 150ms ease;
  }

  .insurance-widget__confirm:hover:not([aria-disabled="true"]) {
    transform: translateY(-1px);
    box-shadow: 0 12px 28px rgba(79, 70, 229, 0.32);
  }

  .insurance-widget__confirm[aria-disabled="true"] {
    background: rgba(148, 163, 184, 0.5);
    cursor: not-allowed;
    box-shadow: none;
  }

  .insurance-widget__footnote {
    margin: 0;
    font-size: 12px;
    color: rgba(15, 23, 42, 0.5);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__footnote {
      color: rgba(148, 163, 184, 0.65);
    }
  }

  .insurance-widget__empty {
    padding: 16px 12px;
    font-size: 13px;
    text-align: center;
    color: rgba(15, 23, 42, 0.55);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__empty {
      color: rgba(226, 232, 240, 0.6);
    }
  }

  .insurance-widget__stepper {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-bottom: 8px;
  }

  .insurance-widget__step {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .insurance-widget__step-circle {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 600;
    background: rgba(148, 163, 184, 0.2);
    color: rgba(15, 23, 42, 0.6);
    transition: all 200ms ease;
  }

  .insurance-widget__step.is-active .insurance-widget__step-circle {
    background: rgba(99, 102, 241, 0.9);
    color: #fff;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  }

  .insurance-widget__step.is-completed .insurance-widget__step-circle {
    background: rgba(34, 197, 94, 0.85);
    color: #fff;
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__step-circle {
      background: rgba(148, 163, 184, 0.3);
      color: rgba(226, 232, 240, 0.7);
    }

    .insurance-widget__step.is-active .insurance-widget__step-circle {
      background: rgba(129, 140, 248, 0.9);
      color: #fff;
    }

    .insurance-widget__step.is-completed .insurance-widget__step-circle {
      background: rgba(34, 197, 94, 0.9);
    }
  }

  .insurance-widget__step-divider {
    width: 40px;
    height: 2px;
    background: rgba(148, 163, 184, 0.3);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__step-divider {
      background: rgba(148, 163, 184, 0.4);
    }
  }

  .insurance-widget__step-content {
    display: none;
  }

  .insurance-widget__step-content.is-active {
    display: block;
  }

  .insurance-widget__actions {
    display: flex;
    gap: 12px;
    margin-top: 8px;
  }

  .insurance-widget__button {
    flex: 1;
    border: none;
    border-radius: 12px;
    padding: 12px 16px;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
    transition: all 150ms ease;
  }

  .insurance-widget__button--secondary {
    background: rgba(148, 163, 184, 0.15);
    color: rgba(15, 23, 42, 0.8);
  }

  .insurance-widget__button--secondary:hover {
    background: rgba(148, 163, 184, 0.25);
  }

  .insurance-widget__button--primary {
    background: linear-gradient(135deg, #6366f1, #4338ca);
    color: #fff;
  }

  .insurance-widget__button--primary:hover:not([aria-disabled="true"]) {
    transform: translateY(-1px);
    box-shadow: 0 12px 28px rgba(79, 70, 229, 0.32);
  }

  .insurance-widget__button[aria-disabled="true"] {
    opacity: 0.5;
    cursor: not-allowed;
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__button--secondary {
      background: rgba(148, 163, 184, 0.2);
      color: rgba(226, 232, 240, 0.9);
    }

    .insurance-widget__button--secondary:hover {
      background: rgba(148, 163, 184, 0.3);
    }
  }

  /* Step titles */
  .insurance-widget__step-title {
    font-size: 18px;
    font-weight: 700;
    margin: 0 0 16px 0;
    color: rgba(15, 23, 42, 0.9);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__step-title {
      color: rgba(255, 255, 255, 0.92);
    }
  }

  /* Subsection titles */
  .insurance-widget__subsection-title {
    font-size: 14px;
    font-weight: 600;
    margin: 16px 0 12px 0;
    color: rgba(15, 23, 42, 0.8);
    padding-top: 8px;
    border-top: 1px solid rgba(15, 23, 42, 0.08);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__subsection-title {
      color: rgba(226, 232, 240, 0.85);
      border-top-color: rgba(148, 163, 184, 0.2);
    }
  }

  /* Toggle field layout */
  .insurance-widget__field--toggle {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }

  /* Toggle switch styles */
  .insurance-widget__toggle {
    position: relative;
    width: 48px;
    height: 28px;
    appearance: none;
    background: rgba(148, 163, 184, 0.3);
    border-radius: 14px;
    cursor: pointer;
    transition: background 200ms ease;
    outline: none;
  }

  .insurance-widget__toggle:checked {
    background: rgba(99, 102, 241, 0.9);
  }

  .insurance-widget__toggle::before {
    content: "";
    position: absolute;
    top: 2px;
    left: 2px;
    width: 24px;
    height: 24px;
    background: #fff;
    border-radius: 50%;
    transition: transform 200ms ease;
  }

  .insurance-widget__toggle:checked::before {
    transform: translateX(20px);
  }

  .insurance-widget__toggle:focus {
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__toggle {
      background: rgba(148, 163, 184, 0.4);
    }

    .insurance-widget__toggle:checked {
      background: rgba(129, 140, 248, 0.9);
    }

    .insurance-widget__toggle:focus {
      box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.3);
    }
  }

  /* Review sections */
  .insurance-widget__review-sections {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .insurance-widget__review-section {
    border: 1px solid rgba(15, 23, 42, 0.1);
    border-radius: 12px;
    overflow: hidden;
    background: rgba(248, 250, 252, 0.5);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__review-section {
      border-color: rgba(148, 163, 184, 0.2);
      background: rgba(30, 41, 59, 0.5);
    }
  }

  .insurance-widget__review-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.8);
    border-bottom: 1px solid rgba(15, 23, 42, 0.08);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__review-header {
      background: rgba(15, 23, 42, 0.8);
      border-bottom-color: rgba(148, 163, 184, 0.15);
    }
  }

  .insurance-widget__review-header h4 {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: rgba(15, 23, 42, 0.85);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__review-header h4 {
      color: rgba(226, 232, 240, 0.9);
    }
  }

  .insurance-widget__button--edit {
    border: none;
    background: rgba(99, 102, 241, 0.1);
    color: rgba(99, 102, 241, 0.95);
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 150ms ease;
  }

  .insurance-widget__button--edit:hover {
    background: rgba(99, 102, 241, 0.18);
    transform: translateY(-1px);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__button--edit {
      background: rgba(129, 140, 248, 0.15);
      color: rgba(165, 180, 252, 0.95);
    }

    .insurance-widget__button--edit:hover {
      background: rgba(129, 140, 248, 0.25);
    }
  }

  .insurance-widget__review-content {
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .insurance-widget__review-item {
    font-size: 13px;
    line-height: 1.5;
    color: rgba(15, 23, 42, 0.75);
  }

  .insurance-widget__review-item strong {
    color: rgba(15, 23, 42, 0.9);
    font-weight: 600;
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__review-item {
      color: rgba(226, 232, 240, 0.75);
    }

    .insurance-widget__review-item strong {
      color: rgba(226, 232, 240, 0.95);
    }
  }
</style>
<script type="module">
  (function () {
    const root = document.getElementById("insurance-state-root");
    if (!root) return;

    const LOG_PREFIX = "[insurance-state-widget]";

    function notifyIssue(level, message, error) {
      const fullMessage = `${LOG_PREFIX} ${message}`;
      const reporter =
        window.openai && typeof window.openai.reportError === "function"
          ? window.openai.reportError
          : null;

      if (reporter) {
        try {
          reporter(fullMessage);
        } catch (reportError) {
          console.error(`${LOG_PREFIX} Failed to report widget issue`, reportError);
        }
      }

      const logArgs = error ? [fullMessage, error] : [fullMessage];
      if (level === "error") {
        console.error(...logArgs);
      } else {
        console.warn(...logArgs);
      }
    }

    let missingSetWidgetStateNotified = false;
    let missingSendFollowUpNotified = false;

    const STATES = [
      { code: "AL", name: "Alabama" },
      { code: "AK", name: "Alaska" },
      { code: "AZ", name: "Arizona" },
      { code: "AR", name: "Arkansas" },
      { code: "CA", name: "California" },
      { code: "CO", name: "Colorado" },
      { code: "CT", name: "Connecticut" },
      { code: "DE", name: "Delaware" },
      { code: "DC", name: "District of Columbia" },
      { code: "FL", name: "Florida" },
      { code: "GA", name: "Georgia" },
      { code: "HI", name: "Hawaii" },
      { code: "ID", name: "Idaho" },
      { code: "IL", name: "Illinois" },
      { code: "IN", name: "Indiana" },
      { code: "IA", name: "Iowa" },
      { code: "KS", name: "Kansas" },
      { code: "KY", name: "Kentucky" },
      { code: "LA", name: "Louisiana" },
      { code: "ME", name: "Maine" },
      { code: "MD", name: "Maryland" },
      { code: "MA", name: "Massachusetts" },
      { code: "MI", name: "Michigan" },
      { code: "MN", name: "Minnesota" },
      { code: "MS", name: "Mississippi" },
      { code: "MO", name: "Missouri" },
      { code: "MT", name: "Montana" },
      { code: "NE", name: "Nebraska" },
      { code: "NV", name: "Nevada" },
      { code: "NH", name: "New Hampshire" },
      { code: "NJ", name: "New Jersey" },
      { code: "NM", name: "New Mexico" },
      { code: "NY", name: "New York" },
      { code: "NC", name: "North Carolina" },
      { code: "ND", name: "North Dakota" },
      { code: "OH", name: "Ohio" },
      { code: "OK", name: "Oklahoma" },
      { code: "OR", name: "Oregon" },
      { code: "PA", name: "Pennsylvania" },
      { code: "RI", name: "Rhode Island" },
      { code: "SC", name: "South Carolina" },
      { code: "SD", name: "South Dakota" },
      { code: "TN", name: "Tennessee" },
      { code: "TX", name: "Texas" },
      { code: "UT", name: "Utah" },
      { code: "VT", name: "Vermont" },
      { code: "VA", name: "Virginia" },
      { code: "WA", name: "Washington" },
      { code: "WV", name: "West Virginia" },
      { code: "WI", name: "Wisconsin" },
      { code: "WY", name: "Wyoming" }
    ].map((state) => ({
      ...state,
      nameLower: state.name.toLowerCase(),
      codeLower: state.code.toLowerCase(),
    }));

    const INSURANCE_TYPES = [
      { value: "personal-auto", label: "Personal auto" },
      { value: "homeowners", label: "Homeowners" },
      { value: "renters", label: "Renters" },
    ];

    const container = document.createElement("div");
    container.className = "insurance-widget";

    const eyebrow = document.createElement("span");
    eyebrow.className = "insurance-widget__eyebrow";
    eyebrow.textContent = "Insurance quote";

    const title = document.createElement("h2");
    title.className = "insurance-widget__title";
    title.textContent = "Help us tailor your insurance quote (5 steps)";

    const description = document.createElement("p");
    description.className = "insurance-widget__description";
    description.textContent =
      "Complete all steps to get your personalized insurance quote: policy setup, customer info, vehicle details, driver info, and review.";

    // Stepper UI
    const stepper = document.createElement("div");
    stepper.className = "insurance-widget__stepper";

    const step1Wrapper = document.createElement("div");
    step1Wrapper.className = "insurance-widget__step is-active";
    step1Wrapper.setAttribute("data-step", "1");
    const step1Circle = document.createElement("div");
    step1Circle.className = "insurance-widget__step-circle";
    step1Circle.textContent = "1";
    step1Wrapper.appendChild(step1Circle);

    const divider1 = document.createElement("div");
    divider1.className = "insurance-widget__step-divider";

    const step2Wrapper = document.createElement("div");
    step2Wrapper.className = "insurance-widget__step";
    step2Wrapper.setAttribute("data-step", "2");
    const step2Circle = document.createElement("div");
    step2Circle.className = "insurance-widget__step-circle";
    step2Circle.textContent = "2";
    step2Wrapper.appendChild(step2Circle);

    const divider2 = document.createElement("div");
    divider2.className = "insurance-widget__step-divider";

    const step3Wrapper = document.createElement("div");
    step3Wrapper.className = "insurance-widget__step";
    step3Wrapper.setAttribute("data-step", "3");
    const step3Circle = document.createElement("div");
    step3Circle.className = "insurance-widget__step-circle";
    step3Circle.textContent = "3";
    step3Wrapper.appendChild(step3Circle);

    const divider3 = document.createElement("div");
    divider3.className = "insurance-widget__step-divider";

    const step4Wrapper = document.createElement("div");
    step4Wrapper.className = "insurance-widget__step";
    step4Wrapper.setAttribute("data-step", "4");
    const step4Circle = document.createElement("div");
    step4Circle.className = "insurance-widget__step-circle";
    step4Circle.textContent = "4";
    step4Wrapper.appendChild(step4Circle);

    const divider4 = document.createElement("div");
    divider4.className = "insurance-widget__step-divider";

    const step5Wrapper = document.createElement("div");
    step5Wrapper.className = "insurance-widget__step";
    step5Wrapper.setAttribute("data-step", "5");
    const step5Circle = document.createElement("div");
    step5Circle.className = "insurance-widget__step-circle";
    step5Circle.textContent = "5";
    step5Wrapper.appendChild(step5Circle);

    stepper.appendChild(step1Wrapper);
    stepper.appendChild(divider1);
    stepper.appendChild(step2Wrapper);
    stepper.appendChild(divider2);
    stepper.appendChild(step3Wrapper);
    stepper.appendChild(divider3);
    stepper.appendChild(step4Wrapper);
    stepper.appendChild(divider4);
    stepper.appendChild(step5Wrapper);

    // Step 1 content wrapper - Policy Setup
    const step1Content = document.createElement("div");
    step1Content.className = "insurance-widget__step-content is-active";
    step1Content.setAttribute("data-step-content", "1");

    const step1Title = document.createElement("h3");
    step1Title.className = "insurance-widget__step-title";
    step1Title.textContent = "🧩 Step 1: Policy Setup";

    // Effective Date
    const effectiveDateField = document.createElement("div");
    effectiveDateField.className = "insurance-widget__field";
    const effectiveDateLabel = document.createElement("label");
    effectiveDateLabel.className = "insurance-widget__label";
    effectiveDateLabel.setAttribute("for", "effective-date");
    effectiveDateLabel.textContent = "Effective Date";
    const effectiveDateWrapper = document.createElement("div");
    effectiveDateWrapper.className = "insurance-widget__input";
    const effectiveDateInput = document.createElement("input");
    effectiveDateInput.id = "effective-date";
    effectiveDateInput.type = "date";
    effectiveDateWrapper.appendChild(effectiveDateInput);
    effectiveDateField.appendChild(effectiveDateLabel);
    effectiveDateField.appendChild(effectiveDateWrapper);

    // Term
    const termField = document.createElement("div");
    termField.className = "insurance-widget__field";
    const termLabel = document.createElement("label");
    termLabel.className = "insurance-widget__label";
    termLabel.setAttribute("for", "term");
    termLabel.textContent = "Term";
    const termWrapper = document.createElement("div");
    termWrapper.className = "insurance-widget__select";
    const termSelect = document.createElement("select");
    termSelect.id = "term";
    const termPlaceholder = document.createElement("option");
    termPlaceholder.value = "";
    termPlaceholder.textContent = "Select term";
    termSelect.appendChild(termPlaceholder);
    ["Semi-Annual", "Annual", "Quarterly", "Monthly"].forEach((t) => {
      const opt = document.createElement("option");
      opt.value = t.toLowerCase().replace("-", "");
      opt.textContent = t;
      termSelect.appendChild(opt);
    });
    termWrapper.appendChild(termSelect);
    termField.appendChild(termLabel);
    termField.appendChild(termWrapper);

    // Payment Method
    const paymentMethodField = document.createElement("div");
    paymentMethodField.className = "insurance-widget__field";
    const paymentMethodLabel = document.createElement("label");
    paymentMethodLabel.className = "insurance-widget__label";
    paymentMethodLabel.setAttribute("for", "payment-method");
    paymentMethodLabel.textContent = "Payment Method";
    const paymentMethodWrapper = document.createElement("div");
    paymentMethodWrapper.className = "insurance-widget__select";
    const paymentMethodSelect = document.createElement("select");
    paymentMethodSelect.id = "payment-method";
    const paymentMethodPlaceholder = document.createElement("option");
    paymentMethodPlaceholder.value = "";
    paymentMethodPlaceholder.textContent = "Select payment method";
    paymentMethodSelect.appendChild(paymentMethodPlaceholder);
    ["EFT", "Credit Card", "Check", "Cash"].forEach((pm) => {
      const opt = document.createElement("option");
      opt.value = pm.toLowerCase().replace(" ", "-");
      opt.textContent = pm;
      paymentMethodSelect.appendChild(opt);
    });
    paymentMethodWrapper.appendChild(paymentMethodSelect);
    paymentMethodField.appendChild(paymentMethodLabel);
    paymentMethodField.appendChild(paymentMethodWrapper);

    // Policy Type
    const policyTypeField = document.createElement("div");
    policyTypeField.className = "insurance-widget__field";
    const policyTypeLabel = document.createElement("label");
    policyTypeLabel.className = "insurance-widget__label";
    policyTypeLabel.setAttribute("for", "policy-type");
    policyTypeLabel.textContent = "Policy Type";
    const policyTypeWrapper = document.createElement("div");
    policyTypeWrapper.className = "insurance-widget__select";
    const policyTypeSelect = document.createElement("select");
    policyTypeSelect.id = "policy-type";
    const policyTypePlaceholder = document.createElement("option");
    policyTypePlaceholder.value = "";
    policyTypePlaceholder.textContent = "Select policy type";
    policyTypeSelect.appendChild(policyTypePlaceholder);
    ["Standard", "Premium", "Basic"].forEach((pt) => {
      const opt = document.createElement("option");
      opt.value = pt.toLowerCase();
      opt.textContent = pt;
      policyTypeSelect.appendChild(opt);
    });
    policyTypeWrapper.appendChild(policyTypeSelect);
    policyTypeField.appendChild(policyTypeLabel);
    policyTypeField.appendChild(policyTypeWrapper);

    // Customer Declined Credit (toggle)
    const declinedCreditField = document.createElement("div");
    declinedCreditField.className = "insurance-widget__field insurance-widget__field--toggle";
    const declinedCreditLabel = document.createElement("label");
    declinedCreditLabel.className = "insurance-widget__label";
    declinedCreditLabel.textContent = "Customer Declined Credit?";
    const declinedCreditToggle = document.createElement("input");
    declinedCreditToggle.type = "checkbox";
    declinedCreditToggle.id = "declined-credit";
    declinedCreditToggle.className = "insurance-widget__toggle";
    declinedCreditField.appendChild(declinedCreditLabel);
    declinedCreditField.appendChild(declinedCreditToggle);

    // Bump Limits
    const bumpLimitsField = document.createElement("div");
    bumpLimitsField.className = "insurance-widget__field";
    const bumpLimitsLabel = document.createElement("label");
    bumpLimitsLabel.className = "insurance-widget__label";
    bumpLimitsLabel.setAttribute("for", "bump-limits");
    bumpLimitsLabel.textContent = "Bump Limits";
    const bumpLimitsWrapper = document.createElement("div");
    bumpLimitsWrapper.className = "insurance-widget__select";
    const bumpLimitsSelect = document.createElement("select");
    bumpLimitsSelect.id = "bump-limits";
    const bumpLimitsPlaceholder = document.createElement("option");
    bumpLimitsPlaceholder.value = "";
    bumpLimitsPlaceholder.textContent = "Select option";
    bumpLimitsSelect.appendChild(bumpLimitsPlaceholder);
    ["Bump Up", "Bump Down", "None"].forEach((bl) => {
      const opt = document.createElement("option");
      opt.value = bl.toLowerCase().replace(" ", "-");
      opt.textContent = bl;
      bumpLimitsSelect.appendChild(opt);
    });
    bumpLimitsWrapper.appendChild(bumpLimitsSelect);
    bumpLimitsField.appendChild(bumpLimitsLabel);
    bumpLimitsField.appendChild(bumpLimitsWrapper);

    // Add step 1 fields to step 1 content
    step1Content.appendChild(step1Title);
    step1Content.appendChild(effectiveDateField);
    step1Content.appendChild(termField);
    step1Content.appendChild(paymentMethodField);
    step1Content.appendChild(policyTypeField);
    step1Content.appendChild(declinedCreditField);
    step1Content.appendChild(bumpLimitsField);

    // Step 2 content wrapper - Customer Information
    const step2Content = document.createElement("div");
    step2Content.className = "insurance-widget__step-content";
    step2Content.setAttribute("data-step-content", "2");

    const step2Title = document.createElement("h3");
    step2Title.className = "insurance-widget__step-title";
    step2Title.textContent = "👤 Step 2: Customer Information";

    // Helper function to create input field
    const createInputField = (id, labelText, type = "text", placeholder = "") => {
      const field = document.createElement("div");
      field.className = "insurance-widget__field";
      const label = document.createElement("label");
      label.className = "insurance-widget__label";
      label.setAttribute("for", id);
      label.textContent = labelText;
      const wrapper = document.createElement("div");
      wrapper.className = "insurance-widget__input";
      const input = document.createElement("input");
      input.id = id;
      input.type = type;
      if (placeholder) input.placeholder = placeholder;
      wrapper.appendChild(input);
      field.appendChild(label);
      field.appendChild(wrapper);
      return field;
    };

    // Helper function to create toggle field
    const createToggleField = (id, labelText) => {
      const field = document.createElement("div");
      field.className = "insurance-widget__field insurance-widget__field--toggle";
      const label = document.createElement("label");
      label.className = "insurance-widget__label";
      label.textContent = labelText;
      const toggle = document.createElement("input");
      toggle.type = "checkbox";
      toggle.id = id;
      toggle.className = "insurance-widget__toggle";
      field.appendChild(label);
      field.appendChild(toggle);
      return field;
    };

    // Name fields
    const firstNameField = createInputField("customer-first-name", "First Name", "text", "Enter first name");
    const middleNameField = createInputField("customer-middle-name", "Middle Name", "text", "Enter middle name (optional)");
    const lastNameField = createInputField("customer-last-name", "Last Name", "text", "Enter last name");

    // Toggles
    const declinedEmailField = createToggleField("declined-email", "Declined Email?");
    const declinedPhoneField = createToggleField("declined-phone", "Declined Phone?");

    // Months at Residence
    const monthsAtResidenceField = createInputField("months-at-residence", "Months at Residence", "number", "Enter months");

    // Address section
    const addressTitle = document.createElement("h4");
    addressTitle.className = "insurance-widget__subsection-title";
    addressTitle.textContent = "Address";

    const streetField = createInputField("address-street", "Street", "text", "Enter street address");
    const cityField = createInputField("address-city", "City", "text", "Enter city");

    // State dropdown
    const stateField = document.createElement("div");
    stateField.className = "insurance-widget__field";
    const stateLabel = document.createElement("label");
    stateLabel.className = "insurance-widget__label";
    stateLabel.setAttribute("for", "address-state");
    stateLabel.textContent = "State";
    const stateWrapper = document.createElement("div");
    stateWrapper.className = "insurance-widget__select";
    const stateSelect = document.createElement("select");
    stateSelect.id = "address-state";
    const statePlaceholder = document.createElement("option");
    statePlaceholder.value = "";
    statePlaceholder.textContent = "Select state";
    stateSelect.appendChild(statePlaceholder);
    STATES.forEach((state) => {
      const opt = document.createElement("option");
      opt.value = state.code;
      opt.textContent = state.name;
      stateSelect.appendChild(opt);
    });
    stateWrapper.appendChild(stateSelect);
    stateField.appendChild(stateLabel);
    stateField.appendChild(stateWrapper);

    const countyField = createInputField("address-county", "County", "text", "Enter county");
    const zipCodeField = createInputField("address-zip", "ZIP Code", "text", "Enter ZIP code");

    // Contact Info section
    const contactTitle = document.createElement("h4");
    contactTitle.className = "insurance-widget__subsection-title";
    contactTitle.textContent = "Contact Information";

    const mobilePhoneField = createInputField("mobile-phone", "Mobile Phone", "tel", "Enter mobile phone");
    const homePhoneField = createInputField("home-phone", "Home Phone", "tel", "Enter home phone");
    const workPhoneField = createInputField("work-phone", "Work Phone", "tel", "Enter work phone");
    const emailField = createInputField("email", "Email Address", "email", "Enter email address");

    // Prior Insurance section
    const priorInsuranceTitle = document.createElement("h4");
    priorInsuranceTitle.className = "insurance-widget__subsection-title";
    priorInsuranceTitle.textContent = "Prior Insurance";

    const priorInsuranceField = createToggleField("prior-insurance", "Prior Insurance?");
    const noInsuranceReasonField = createInputField("no-insurance-reason", "Reason for No Insurance", "text", "Enter reason (if applicable)");

    // Append all fields to step 2 content
    step2Content.appendChild(step2Title);
    step2Content.appendChild(firstNameField);
    step2Content.appendChild(middleNameField);
    step2Content.appendChild(lastNameField);
    step2Content.appendChild(declinedEmailField);
    step2Content.appendChild(declinedPhoneField);
    step2Content.appendChild(monthsAtResidenceField);
    step2Content.appendChild(addressTitle);
    step2Content.appendChild(streetField);
    step2Content.appendChild(cityField);
    step2Content.appendChild(stateField);
    step2Content.appendChild(countyField);
    step2Content.appendChild(zipCodeField);
    step2Content.appendChild(contactTitle);
    step2Content.appendChild(mobilePhoneField);
    step2Content.appendChild(homePhoneField);
    step2Content.appendChild(workPhoneField);
    step2Content.appendChild(emailField);
    step2Content.appendChild(priorInsuranceTitle);
    step2Content.appendChild(priorInsuranceField);
    step2Content.appendChild(noInsuranceReasonField);

    // Step 3 content wrapper - Vehicle Details
    const step3Content = document.createElement("div");
    step3Content.className = "insurance-widget__step-content";
    step3Content.setAttribute("data-step-content", "3");

    const step3Title = document.createElement("h3");
    step3Title.className = "insurance-widget__step-title";
    step3Title.textContent = "🚗 Step 3: Vehicle Details";

    // Helper to create select field
    const createSelectField = (id, labelText, options) => {
      const field = document.createElement("div");
      field.className = "insurance-widget__field";
      const label = document.createElement("label");
      label.className = "insurance-widget__label";
      label.setAttribute("for", id);
      label.textContent = labelText;
      const wrapper = document.createElement("div");
      wrapper.className = "insurance-widget__select";
      const select = document.createElement("select");
      select.id = id;
      const placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.textContent = "Select " + labelText.toLowerCase();
      select.appendChild(placeholder);
      options.forEach((opt) => {
        const option = document.createElement("option");
        option.value = typeof opt === "string" ? opt.toLowerCase().replace(/\\s+/g, "-") : opt.value;
        option.textContent = typeof opt === "string" ? opt : opt.label;
        select.appendChild(option);
      });
      wrapper.appendChild(select);
      field.appendChild(label);
      field.appendChild(wrapper);
      return field;
    };

    // Vehicle basic info
    const vinField = createInputField("vehicle-vin", "VIN", "text", "Enter VIN");
    const makeField = createInputField("vehicle-make", "Make", "text", "Enter make");
    const modelField = createInputField("vehicle-model", "Model", "text", "Enter model");
    const yearField = createInputField("vehicle-year", "Year", "number", "Enter year");
    const annualMilesField = createInputField("vehicle-annual-miles", "Annual Miles", "number", "Enter annual miles");
    const milesToWorkField = createInputField("vehicle-miles-to-work", "Miles to Work", "number", "Enter miles to work");

    // Toggles
    const leasedVehicleField = createToggleField("vehicle-leased", "Leased Vehicle?");

    // Additional fields
    const percentToWorkField = createInputField("vehicle-percent-to-work", "Percent To Work", "number", "Enter percentage");
    const purchaseTypeField = createSelectField("vehicle-purchase-type", "Purchase Type", ["New", "Used", "Lease"]);
    const rideShareField = createToggleField("vehicle-rideshare", "RideShare?");
    const salvagedField = createToggleField("vehicle-salvaged", "Salvaged?");
    const usageField = createSelectField("vehicle-usage", "Usage", ["Commute", "Business", "Pleasure", "Farm"]);
    const odometerField = createInputField("vehicle-odometer", "Odometer", "number", "Enter odometer reading");

    // Garaging Address section
    const garagingTitle = document.createElement("h4");
    garagingTitle.className = "insurance-widget__subsection-title";
    garagingTitle.textContent = "Garaging Address";

    const garagingStreetField = createInputField("garaging-street", "Street", "text", "Same as customer address or enter new");
    const garagingCityField = createInputField("garaging-city", "City", "text", "Enter city");
    const garagingStateField = createSelectField("garaging-state", "State", STATES.map(s => ({ value: s.code, label: s.name })));
    const garagingZipField = createInputField("garaging-zip", "ZIP Code", "text", "Enter ZIP code");

    // Coverage Info section
    const coverageInfoTitle = document.createElement("h4");
    coverageInfoTitle.className = "insurance-widget__subsection-title";
    coverageInfoTitle.textContent = "Coverage Information";

    const collisionDeductibleField = createSelectField("collision-deductible", "Collision Deductible", ["$250", "$500", "$1,000", "$2,500"]);
    const comprehensiveDeductibleField = createSelectField("comprehensive-deductible", "Comprehensive Deductible", ["$250", "$500", "$1,000", "$2,500"]);
    const rentalLimitField = createSelectField("rental-limit", "Rental Limit", ["$30/day", "$50/day", "$75/day", "$100/day"]);
    const gapCoverageField = createToggleField("gap-coverage", "Gap Coverage?");
    const customEquipmentField = createInputField("custom-equipment-value", "Custom Equipment Value", "number", "Enter value");
    const safetyGlassField = createToggleField("safety-glass-coverage", "Safety Glass Coverage?");
    const towingLimitField = createSelectField("towing-limit", "Towing Limit", ["$50", "$100", "$150", "$200"]);

    // Append all fields to step 3 content
    step3Content.appendChild(step3Title);
    step3Content.appendChild(vinField);
    step3Content.appendChild(makeField);
    step3Content.appendChild(modelField);
    step3Content.appendChild(yearField);
    step3Content.appendChild(annualMilesField);
    step3Content.appendChild(milesToWorkField);
    step3Content.appendChild(leasedVehicleField);
    step3Content.appendChild(percentToWorkField);
    step3Content.appendChild(purchaseTypeField);
    step3Content.appendChild(rideShareField);
    step3Content.appendChild(salvagedField);
    step3Content.appendChild(usageField);
    step3Content.appendChild(odometerField);
    step3Content.appendChild(garagingTitle);
    step3Content.appendChild(garagingStreetField);
    step3Content.appendChild(garagingCityField);
    step3Content.appendChild(garagingStateField);
    step3Content.appendChild(garagingZipField);
    step3Content.appendChild(coverageInfoTitle);
    step3Content.appendChild(collisionDeductibleField);
    step3Content.appendChild(comprehensiveDeductibleField);
    step3Content.appendChild(rentalLimitField);
    step3Content.appendChild(gapCoverageField);
    step3Content.appendChild(customEquipmentField);
    step3Content.appendChild(safetyGlassField);
    step3Content.appendChild(towingLimitField);

    // Step 4 content wrapper - Driver Information
    const step4Content = document.createElement("div");
    step4Content.className = "insurance-widget__step-content";
    step4Content.setAttribute("data-step-content", "4");

    const step4Title = document.createElement("h3");
    step4Title.className = "insurance-widget__step-title";
    step4Title.textContent = "👨‍✈️ Step 4: Driver Information";

    // Driver basic info
    const driverFirstNameField = createInputField("driver-first-name", "First Name", "text", "Enter first name");
    const driverMiddleNameField = createInputField("driver-middle-name", "Middle Name", "text", "Enter middle name");
    const driverLastNameField = createInputField("driver-last-name", "Last Name", "text", "Enter last name");
    const dobField = createInputField("driver-dob", "Date of Birth", "date", "");
    const genderField = createSelectField("driver-gender", "Gender", ["Male", "Female", "Non-Binary", "Prefer not to say"]);
    const maritalStatusField = createSelectField("driver-marital-status", "Marital Status", ["Single", "Married", "Divorced", "Widowed"]);
    const occupationField = createInputField("driver-occupation", "Occupation", "text", "Enter occupation");
    const industryField = createInputField("driver-industry", "Industry", "text", "Enter industry");
    const monthsEmployedField = createInputField("driver-months-employed", "Months Employed", "number", "Enter months");

    // License Info section
    const licenseTitle = document.createElement("h4");
    licenseTitle.className = "insurance-widget__subsection-title";
    licenseTitle.textContent = "License Information";

    const licenseNumberField = createInputField("license-number", "License Number", "text", "Enter license number");
    const licenseStatusField = createSelectField("license-status", "License Status", ["Valid", "Suspended", "Expired", "Learner's Permit"]);
    const monthsLicensedField = createInputField("months-licensed", "Months Licensed", "number", "Enter months");
    const stateLicensedField = createSelectField("state-licensed", "State Licensed", STATES.map(s => ({ value: s.code, label: s.name })));
    const mvrExperienceField = createInputField("mvr-experience", "MVR Experience", "text", "Enter MVR experience");
    const suspendedMonthsField = createInputField("suspended-months", "Suspended Months", "number", "Enter suspended months (if any)");
    const foreignNationalField = createToggleField("foreign-national", "Foreign National?");
    const internationalLicenseField = createToggleField("international-license", "International License?");

    // Attributes section
    const attributesTitle = document.createElement("h4");
    attributesTitle.className = "insurance-widget__subsection-title";
    attributesTitle.textContent = "Attributes";

    const educationLevelField = createSelectField("education-level", "Education Level", ["High School", "Some College", "Associate's", "Bachelor's", "Master's", "Doctorate"]);
    const relationField = createSelectField("relation", "Relation to Insured", ["Self", "Spouse", "Child", "Parent", "Other"]);
    const residencyTypeField = createSelectField("residency-type", "Residency Type", ["Own", "Home", "Rent", "Other"]);
    const driverMilesToWorkField = createInputField("driver-miles-to-work", "Miles To Work", "number", "Enter miles to work");
    const propertyInsuranceField = createToggleField("property-insurance", "Property Insurance?");

    // Discounts section
    const discountsTitle = document.createElement("h4");
    discountsTitle.className = "insurance-widget__subsection-title";
    discountsTitle.textContent = "Discounts";

    const defensiveDrivingField = createToggleField("discount-defensive-driving", "Defensive Driving");
    const goodStudentField = createToggleField("discount-good-student", "Good Student");
    const seniorField = createToggleField("discount-senior", "Senior");
    const multiplePoliciesField = createToggleField("discount-multiple-policies", "Multiple Policies");

    // SR-22 Info section
    const sr22Title = document.createElement("h4");
    sr22Title.className = "insurance-widget__subsection-title";
    sr22Title.textContent = "SR-22 Information";

    const sr22RequiredField = createToggleField("sr22-required", "SR-22 Required?");
    const sr22ReasonField = createInputField("sr22-reason", "SR-22 Reason", "text", "Enter reason (if applicable)");
    const sr22StateField = createSelectField("sr22-state", "SR-22 State", STATES.map(s => ({ value: s.code, label: s.name })));
    const sr22DateField = createInputField("sr22-date", "SR-22 Date", "date", "");

    // Append all fields to step 4 content
    step4Content.appendChild(step4Title);
    step4Content.appendChild(driverFirstNameField);
    step4Content.appendChild(driverMiddleNameField);
    step4Content.appendChild(driverLastNameField);
    step4Content.appendChild(dobField);
    step4Content.appendChild(genderField);
    step4Content.appendChild(maritalStatusField);
    step4Content.appendChild(occupationField);
    step4Content.appendChild(industryField);
    step4Content.appendChild(monthsEmployedField);
    step4Content.appendChild(licenseTitle);
    step4Content.appendChild(licenseNumberField);
    step4Content.appendChild(licenseStatusField);
    step4Content.appendChild(monthsLicensedField);
    step4Content.appendChild(stateLicensedField);
    step4Content.appendChild(mvrExperienceField);
    step4Content.appendChild(suspendedMonthsField);
    step4Content.appendChild(foreignNationalField);
    step4Content.appendChild(internationalLicenseField);
    step4Content.appendChild(attributesTitle);
    step4Content.appendChild(educationLevelField);
    step4Content.appendChild(relationField);
    step4Content.appendChild(residencyTypeField);
    step4Content.appendChild(driverMilesToWorkField);
    step4Content.appendChild(propertyInsuranceField);
    step4Content.appendChild(discountsTitle);
    step4Content.appendChild(defensiveDrivingField);
    step4Content.appendChild(goodStudentField);
    step4Content.appendChild(seniorField);
    step4Content.appendChild(multiplePoliciesField);
    step4Content.appendChild(sr22Title);
    step4Content.appendChild(sr22RequiredField);
    step4Content.appendChild(sr22ReasonField);
    step4Content.appendChild(sr22StateField);
    step4Content.appendChild(sr22DateField);

    // Step 5 content wrapper - Review & Submit
    const step5Content = document.createElement("div");
    step5Content.className = "insurance-widget__step-content";
    step5Content.setAttribute("data-step-content", "5");

    const step5Title = document.createElement("h3");
    step5Title.className = "insurance-widget__step-title";
    step5Title.textContent = "✅ Step 5: Review & Submit";

    const reviewDescription = document.createElement("p");
    reviewDescription.className = "insurance-widget__description";
    reviewDescription.textContent = "Review your information before submitting your insurance quote request.";

    // Create collapsible sections for review
    const reviewSections = document.createElement("div");
    reviewSections.className = "insurance-widget__review-sections";
    reviewSections.id = "review-sections";

    // We'll populate this dynamically when user reaches step 5

    step5Content.appendChild(step5Title);
    step5Content.appendChild(reviewDescription);
    step5Content.appendChild(reviewSections);

    // Navigation buttons
    const actions = document.createElement("div");
    actions.className = "insurance-widget__actions";

    const prevButton = document.createElement("button");
    prevButton.type = "button";
    prevButton.className = "insurance-widget__button insurance-widget__button--secondary";
    prevButton.textContent = "Previous";
    prevButton.style.display = "none";

    const nextButton = document.createElement("button");
    nextButton.type = "button";
    nextButton.className = "insurance-widget__button insurance-widget__button--primary";
    nextButton.textContent = "Next";
    nextButton.setAttribute("aria-disabled", "true");
    nextButton.disabled = true;

    actions.appendChild(prevButton);
    actions.appendChild(nextButton);

    // Progress indicator
    const selection = document.createElement("div");
    selection.className = "insurance-widget__selection";
    selection.textContent = "Complete all required fields to continue.";

    const footnote = document.createElement("p");
    footnote.className = "insurance-widget__footnote";
    footnote.textContent = "All information is securely processed. You can edit any step before final submission.";

    container.appendChild(eyebrow);
    container.appendChild(title);
    container.appendChild(description);
    container.appendChild(stepper);
    container.appendChild(step1Content);
    container.appendChild(step2Content);
    container.appendChild(step3Content);
    container.appendChild(step4Content);
    container.appendChild(step5Content);
    container.appendChild(selection);
    container.appendChild(actions);
    container.appendChild(footnote);

    root.appendChild(container);

    let isSending = false;
    let currentStep = 1;

    function goToStep(stepNumber) {
      currentStep = stepNumber;

      // Update step indicators
      const stepWrappers = container.querySelectorAll(".insurance-widget__step");
      stepWrappers.forEach((wrapper) => {
        const step = parseInt(wrapper.getAttribute("data-step"));
        wrapper.classList.remove("is-active", "is-completed");
        if (step === currentStep) {
          wrapper.classList.add("is-active");
        } else if (step < currentStep) {
          wrapper.classList.add("is-completed");
        }
      });

      // Update step content visibility
      const stepContents = container.querySelectorAll(".insurance-widget__step-content");
      stepContents.forEach((content) => {
        const step = parseInt(content.getAttribute("data-step-content"));
        content.classList.toggle("is-active", step === currentStep);
      });

      // Update button visibility and state
      if (currentStep === 1) {
        prevButton.style.display = "none";
        nextButton.textContent = "Next";
      } else if (currentStep === 5) {
        prevButton.style.display = "block";
        nextButton.textContent = "Submit Quote Request";
      } else {
        prevButton.style.display = "block";
        nextButton.textContent = "Next";
      }

      // Always enable next button (make all fields optional)
      nextButton.disabled = false;
      nextButton.setAttribute("aria-disabled", "false");

      // Populate review section when reaching step 5
      if (currentStep === 5) {
        populateReviewSection();
      }

      // Update progress message
      selection.textContent = `Step ${currentStep} of 5 - ${getStepTitle(currentStep)}`;
    }

    function getStepTitle(step) {
      const titles = {
        1: "Policy Setup",
        2: "Customer Information",
        3: "Vehicle Details",
        4: "Driver Information",
        5: "Review & Submit"
      };
      return titles[step] || "";
    }

    function populateReviewSection() {
      const reviewContainer = document.getElementById("review-sections");
      if (!reviewContainer) return;

      reviewContainer.innerHTML = "";

      // Helper to create a review section
      const createReviewSection = (title, fields, stepNumber) => {
        const section = document.createElement("div");
        section.className = "insurance-widget__review-section";

        const header = document.createElement("div");
        header.className = "insurance-widget__review-header";

        const headerTitle = document.createElement("h4");
        headerTitle.textContent = title;

        const editButton = document.createElement("button");
        editButton.type = "button";
        editButton.className = "insurance-widget__button--edit";
        editButton.textContent = "Edit";
        editButton.addEventListener("click", () => {
          goToStep(stepNumber);
        });

        header.appendChild(headerTitle);
        header.appendChild(editButton);

        const content = document.createElement("div");
        content.className = "insurance-widget__review-content";

        fields.forEach(({ label, id }) => {
          const element = document.getElementById(id);
          if (!element) return;

          let value = "";
          if (element.type === "checkbox") {
            value = element.checked ? "Yes" : "No";
          } else if (element.tagName === "SELECT") {
            value = element.options[element.selectedIndex]?.text || "";
          } else {
            value = element.value || "";
          }

          if (value) {
            const item = document.createElement("div");
            item.className = "insurance-widget__review-item";
            item.innerHTML = `<strong>${label}:</strong> ${value}`;
            content.appendChild(item);
          }
        });

        section.appendChild(header);
        section.appendChild(content);
        return section;
      };

      // Policy section
      const policyFields = [
        { label: "Effective Date", id: "effective-date" },
        { label: "Term", id: "term" },
        { label: "Payment Method", id: "payment-method" },
        { label: "Policy Type", id: "policy-type" },
        { label: "Declined Credit", id: "declined-credit" },
        { label: "Bump Limits", id: "bump-limits" }
      ];
      reviewContainer.appendChild(createReviewSection("Policy Setup", policyFields, 1));

      // Customer section
      const customerFields = [
        { label: "First Name", id: "customer-first-name" },
        { label: "Last Name", id: "customer-last-name" },
        { label: "Email", id: "email" },
        { label: "Mobile Phone", id: "mobile-phone" },
        { label: "Street", id: "address-street" },
        { label: "City", id: "address-city" },
        { label: "State", id: "address-state" },
        { label: "ZIP Code", id: "address-zip" }
      ];
      reviewContainer.appendChild(createReviewSection("Customer Information", customerFields, 2));

      // Vehicle section
      const vehicleFields = [
        { label: "VIN", id: "vehicle-vin" },
        { label: "Make", id: "vehicle-make" },
        { label: "Model", id: "vehicle-model" },
        { label: "Year", id: "vehicle-year" },
        { label: "Usage", id: "vehicle-usage" }
      ];
      reviewContainer.appendChild(createReviewSection("Vehicle Details", vehicleFields, 3));

      // Driver section
      const driverFields = [
        { label: "First Name", id: "driver-first-name" },
        { label: "Last Name", id: "driver-last-name" },
        { label: "Date of Birth", id: "driver-dob" },
        { label: "License Number", id: "license-number" },
        { label: "License Status", id: "license-status" }
      ];
      reviewContainer.appendChild(createReviewSection("Driver Information", driverFields, 4));
    }

    nextButton.addEventListener("click", async () => {
      if (currentStep < 5) {
        goToStep(currentStep + 1);
      } else if (currentStep === 5) {
        // Submit the form
        if (isSending) return;

        isSending = true;
        nextButton.textContent = "Sending to assistant…";
        nextButton.setAttribute("aria-disabled", "true");
        nextButton.disabled = true;
        prevButton.disabled = true;

        try {
          await sendFormToAssistant();
        } catch (error) {
          notifyIssue("error", "Failed to submit insurance quote request.", error);
        } finally {
          isSending = false;
          nextButton.textContent = "Submit Quote Request";
          prevButton.disabled = false;
          nextButton.disabled = false;
          nextButton.setAttribute("aria-disabled", "false");
        }
      }
    });

    prevButton.addEventListener("click", () => {
      if (currentStep > 1) {
        goToStep(currentStep - 1);
      }
    });

    // Helper function to get field value safely
    function getFieldValue(id) {
      const element = document.getElementById(id);
      if (!element) return null;

      if (element.type === "checkbox") {
        return element.checked;
      } else if (element.tagName === "SELECT") {
        return element.value || null;
      } else {
        return element.value || null;
      }
    }

    // Function to collect all form data
    function collectFormData() {
      return {
        // Step 1: Policy Setup
        policy: {
          effectiveDate: getFieldValue("effective-date"),
          term: getFieldValue("term"),
          paymentMethod: getFieldValue("payment-method"),
          policyType: getFieldValue("policy-type"),
          declinedCredit: getFieldValue("declined-credit"),
          bumpLimits: getFieldValue("bump-limits")
        },
        // Step 2: Customer Information
        customer: {
          firstName: getFieldValue("customer-first-name"),
          middleName: getFieldValue("customer-middle-name"),
          lastName: getFieldValue("customer-last-name"),
          declinedEmail: getFieldValue("declined-email"),
          declinedPhone: getFieldValue("declined-phone"),
          monthsAtResidence: getFieldValue("months-at-residence"),
          address: {
            street: getFieldValue("address-street"),
            city: getFieldValue("address-city"),
            state: getFieldValue("address-state"),
            county: getFieldValue("address-county"),
            zipCode: getFieldValue("address-zip")
          },
          contact: {
            mobilePhone: getFieldValue("mobile-phone"),
            homePhone: getFieldValue("home-phone"),
            workPhone: getFieldValue("work-phone"),
            email: getFieldValue("email")
          },
          priorInsurance: getFieldValue("prior-insurance"),
          noInsuranceReason: getFieldValue("no-insurance-reason")
        },
        // Step 3: Vehicle Details
        vehicle: {
          vin: getFieldValue("vehicle-vin"),
          make: getFieldValue("vehicle-make"),
          model: getFieldValue("vehicle-model"),
          year: getFieldValue("vehicle-year"),
          annualMiles: getFieldValue("vehicle-annual-miles"),
          milesToWork: getFieldValue("vehicle-miles-to-work"),
          leased: getFieldValue("vehicle-leased"),
          percentToWork: getFieldValue("vehicle-percent-to-work"),
          purchaseType: getFieldValue("vehicle-purchase-type"),
          rideShare: getFieldValue("vehicle-rideshare"),
          salvaged: getFieldValue("vehicle-salvaged"),
          usage: getFieldValue("vehicle-usage"),
          odometer: getFieldValue("vehicle-odometer"),
          garagingAddress: {
            street: getFieldValue("garaging-street"),
            city: getFieldValue("garaging-city"),
            state: getFieldValue("garaging-state"),
            zipCode: getFieldValue("garaging-zip")
          },
          coverage: {
            collisionDeductible: getFieldValue("collision-deductible"),
            comprehensiveDeductible: getFieldValue("comprehensive-deductible"),
            rentalLimit: getFieldValue("rental-limit"),
            gapCoverage: getFieldValue("gap-coverage"),
            customEquipmentValue: getFieldValue("custom-equipment-value"),
            safetyGlassCoverage: getFieldValue("safety-glass-coverage"),
            towingLimit: getFieldValue("towing-limit")
          }
        },
        // Step 4: Driver Information
        driver: {
          firstName: getFieldValue("driver-first-name"),
          middleName: getFieldValue("driver-middle-name"),
          lastName: getFieldValue("driver-last-name"),
          dateOfBirth: getFieldValue("driver-dob"),
          gender: getFieldValue("driver-gender"),
          maritalStatus: getFieldValue("driver-marital-status"),
          occupation: getFieldValue("driver-occupation"),
          industry: getFieldValue("driver-industry"),
          monthsEmployed: getFieldValue("driver-months-employed"),
          license: {
            number: getFieldValue("license-number"),
            status: getFieldValue("license-status"),
            monthsLicensed: getFieldValue("months-licensed"),
            stateLicensed: getFieldValue("state-licensed"),
            mvrExperience: getFieldValue("mvr-experience"),
            suspendedMonths: getFieldValue("suspended-months"),
            foreignNational: getFieldValue("foreign-national"),
            internationalLicense: getFieldValue("international-license")
          },
          attributes: {
            educationLevel: getFieldValue("education-level"),
            relation: getFieldValue("relation"),
            residencyType: getFieldValue("residency-type"),
            milesToWork: getFieldValue("driver-miles-to-work"),
            propertyInsurance: getFieldValue("property-insurance")
          },
          discounts: {
            defensiveDriving: getFieldValue("discount-defensive-driving"),
            goodStudent: getFieldValue("discount-good-student"),
            senior: getFieldValue("discount-senior"),
            multiplePolicies: getFieldValue("discount-multiple-policies")
          },
          sr22: {
            required: getFieldValue("sr22-required"),
            reason: getFieldValue("sr22-reason"),
            state: getFieldValue("sr22-state"),
            date: getFieldValue("sr22-date")
          }
        }
      };
    }

    // Function to send form data to assistant
    async function sendFormToAssistant() {
      if (!window.openai || typeof window.openai.sendFollowUpMessage !== "function") {
        if (!missingSendFollowUpNotified) {
          notifyIssue(
            "warn",
            "OpenAI sendFollowUpMessage helper is unavailable; the assistant will not receive insurance quote request."
          );
          missingSendFollowUpNotified = true;
        }
        return Promise.resolve();
      }

      const formData = collectFormData();

      // Build a human-readable prompt
      let prompt = "I would like to request an insurance quote with the following details:\\n\\n";

      if (formData.customer.firstName && formData.customer.lastName) {
        prompt += `Customer: ${formData.customer.firstName} ${formData.customer.lastName}\\n`;
      }

      if (formData.customer.address.city && formData.customer.address.state) {
        prompt += `Location: ${formData.customer.address.city}, ${formData.customer.address.state}`;
        if (formData.customer.address.zipCode) {
          prompt += ` ${formData.customer.address.zipCode}`;
        }
        prompt += "\\n";
      }

      if (formData.vehicle.make && formData.vehicle.model && formData.vehicle.year) {
        prompt += `Vehicle: ${formData.vehicle.year} ${formData.vehicle.make} ${formData.vehicle.model}\\n`;
      }

      if (formData.driver.firstName && formData.driver.lastName) {
        prompt += `Driver: ${formData.driver.firstName} ${formData.driver.lastName}\\n`;
      }

      prompt += "\\nPlease provide a quote based on this information.";

      const metadata = {
        formData: formData,
        submittedAt: new Date().toISOString()
      };

      return window.openai.sendFollowUpMessage({ prompt, metadata });
    }

    // Initialize widget on step 1
    goToStep(1);
  })();
</script>
""".strip()
