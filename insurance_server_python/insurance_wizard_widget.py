"""5-step insurance wizard widget for personal auto quotes."""

INSURANCE_WIZARD_WIDGET_HTML = r"""
<div id="insurance-wizard-root"></div>
<style>
  :root {
    color-scheme: light dark;
  }

  #insurance-wizard-root {
    font-family: "Inter", "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont,
      "Helvetica Neue", Arial, sans-serif;
    color: rgba(0, 0, 0, 0.82);
  }

  @media (prefers-color-scheme: dark) {
    #insurance-wizard-root {
      color: rgba(255, 255, 255, 0.88);
    }
  }

  .wizard {
    background: rgba(255, 255, 255, 0.94);
    border-radius: 20px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    padding: 32px;
    max-width: 800px;
    margin: 0 auto;
    box-shadow: 0 18px 48px rgba(15, 23, 42, 0.12);
  }

  @media (prefers-color-scheme: dark) {
    .wizard {
      background: rgba(15, 23, 42, 0.92);
      border-color: rgba(255, 255, 255, 0.12);
      box-shadow: 0 18px 48px rgba(0, 0, 0, 0.45);
    }
  }

  .wizard__header {
    text-align: center;
    margin-bottom: 32px;
  }

  .wizard__eyebrow {
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.14em;
    font-weight: 600;
    color: rgba(99, 102, 241, 0.9);
  }

  .wizard__title {
    font-size: 24px;
    font-weight: 700;
    margin: 8px 0 12px;
  }

  .wizard__description {
    font-size: 14px;
    line-height: 1.6;
    color: rgba(15, 23, 42, 0.74);
  }

  @media (prefers-color-scheme: dark) {
    .wizard__description {
      color: rgba(226, 232, 240, 0.72);
    }
  }

  .wizard__stepper {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin: 32px 0;
  }

  .wizard__step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    flex: 1;
    max-width: 120px;
  }

  .wizard__step-circle {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 600;
    background: rgba(148, 163, 184, 0.2);
    color: rgba(15, 23, 42, 0.6);
    transition: all 200ms ease;
  }

  .wizard__step.is-active .wizard__step-circle {
    background: rgba(99, 102, 241, 0.9);
    color: #fff;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
  }

  .wizard__step.is-completed .wizard__step-circle {
    background: rgba(34, 197, 94, 0.85);
    color: #fff;
  }

  @media (prefers-color-scheme: dark) {
    .wizard__step-circle {
      background: rgba(148, 163, 184, 0.3);
      color: rgba(226, 232, 240, 0.7);
    }

    .wizard__step.is-active .wizard__step-circle {
      background: rgba(129, 140, 248, 0.9);
    }

    .wizard__step.is-completed .wizard__step-circle {
      background: rgba(34, 197, 94, 0.9);
    }
  }

  .wizard__step-label {
    font-size: 11px;
    font-weight: 600;
    text-align: center;
    color: rgba(15, 23, 42, 0.6);
  }

  .wizard__step.is-active .wizard__step-label {
    color: rgba(99, 102, 241, 0.9);
  }

  @media (prefers-color-scheme: dark) {
    .wizard__step-label {
      color: rgba(226, 232, 240, 0.7);
    }

    .wizard__step.is-active .wizard__step-label {
      color: rgba(129, 140, 248, 0.9);
    }
  }

  .wizard__step-divider {
    flex: 1;
    height: 2px;
    background: rgba(148, 163, 184, 0.3);
    margin: 0 4px;
  }

  .wizard__content {
    min-height: 400px;
  }

  .wizard__step-content {
    display: none;
  }

  .wizard__step-content.is-active {
    display: block;
    animation: fadeIn 300ms ease;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .wizard__form-section {
    margin-bottom: 24px;
  }

  .wizard__section-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 16px;
    color: rgba(15, 23, 42, 0.82);
  }

  @media (prefers-color-scheme: dark) {
    .wizard__section-title {
      color: rgba(226, 232, 240, 0.88);
    }
  }

  .wizard__grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }

  .wizard__grid--full {
    grid-template-columns: 1fr;
  }

  .wizard__field {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .wizard__label {
    font-size: 13px;
    font-weight: 600;
    color: rgba(15, 23, 42, 0.72);
  }

  @media (prefers-color-scheme: dark) {
    .wizard__label {
      color: rgba(226, 232, 240, 0.78);
    }
  }

  .wizard__input-wrapper {
    border: 1px solid rgba(15, 23, 42, 0.12);
    border-radius: 10px;
    padding: 0 12px;
    background: rgba(255, 255, 255, 0.96);
    transition: border 120ms ease, box-shadow 120ms ease;
  }

  .wizard__input-wrapper:focus-within {
    border-color: rgba(99, 102, 241, 0.65);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.18);
  }

  @media (prefers-color-scheme: dark) {
    .wizard__input-wrapper {
      background: rgba(15, 23, 42, 0.88);
      border-color: rgba(148, 163, 184, 0.28);
    }

    .wizard__input-wrapper:focus-within {
      border-color: rgba(99, 102, 241, 0.8);
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.28);
    }
  }

  .wizard__input,
  .wizard__select {
    width: 100%;
    border: none;
    outline: none;
    height: 40px;
    background: transparent;
    color: inherit;
    font-size: 14px;
  }

  .wizard__input::placeholder {
    color: rgba(15, 23, 42, 0.45);
  }

  @media (prefers-color-scheme: dark) {
    .wizard__input::placeholder {
      color: rgba(226, 232, 240, 0.45);
    }
  }

  .wizard__toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    user-select: none;
  }

  .wizard__toggle-switch {
    position: relative;
    width: 44px;
    height: 24px;
    background: rgba(148, 163, 184, 0.3);
    border-radius: 12px;
    transition: background 150ms ease;
  }

  .wizard__toggle-switch::before {
    content: '';
    position: absolute;
    width: 18px;
    height: 18px;
    background: white;
    border-radius: 50%;
    top: 3px;
    left: 3px;
    transition: transform 150ms ease;
  }

  .wizard__toggle input:checked + .wizard__toggle-switch {
    background: rgba(99, 102, 241, 0.9);
  }

  .wizard__toggle input:checked + .wizard__toggle-switch::before {
    transform: translateX(20px);
  }

  .wizard__toggle input {
    position: absolute;
    opacity: 0;
  }

  .wizard__actions {
    display: flex;
    gap: 12px;
    margin-top: 32px;
  }

  .wizard__button {
    flex: 1;
    border: none;
    border-radius: 12px;
    padding: 14px 20px;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
    transition: all 150ms ease;
  }

  .wizard__button--secondary {
    background: rgba(148, 163, 184, 0.15);
    color: rgba(15, 23, 42, 0.8);
  }

  .wizard__button--secondary:hover:not(:disabled) {
    background: rgba(148, 163, 184, 0.25);
  }

  .wizard__button--primary {
    background: linear-gradient(135deg, #6366f1, #4338ca);
    color: #fff;
  }

  .wizard__button--primary:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 12px 28px rgba(79, 70, 229, 0.32);
  }

  .wizard__button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  @media (prefers-color-scheme: dark) {
    .wizard__button--secondary {
      background: rgba(148, 163, 184, 0.2);
      color: rgba(226, 232, 240, 0.9);
    }

    .wizard__button--secondary:hover:not(:disabled) {
      background: rgba(148, 163, 184, 0.3);
    }
  }

  .wizard__review-section {
    background: rgba(248, 250, 252, 0.6);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
  }

  @media (prefers-color-scheme: dark) {
    .wizard__review-section {
      background: rgba(30, 41, 59, 0.6);
    }
  }

  .wizard__review-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  .wizard__review-title {
    font-size: 15px;
    font-weight: 600;
  }

  .wizard__review-edit {
    font-size: 13px;
    color: rgba(99, 102, 241, 0.9);
    background: none;
    border: none;
    cursor: pointer;
    font-weight: 600;
  }

  .wizard__review-edit:hover {
    text-decoration: underline;
  }

  .wizard__review-grid {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 8px 16px;
  }

  .wizard__review-label {
    font-size: 13px;
    color: rgba(15, 23, 42, 0.6);
  }

  .wizard__review-value {
    font-size: 13px;
    font-weight: 500;
  }

  @media (prefers-color-scheme: dark) {
    .wizard__review-label {
      color: rgba(226, 232, 240, 0.65);
    }
  }
</style>
<script type="module">
  (function () {
    const root = document.getElementById("insurance-wizard-root");
    if (!root) return;

    const LOG_PREFIX = "[insurance-wizard]";

    function notifyIssue(level, message, error) {
      const fullMessage = \`\${LOG_PREFIX} \${message}\`;
      const reporter =
        window.openai && typeof window.openai.reportError === "function"
          ? window.openai.reportError
          : null;

      if (reporter) {
        try {
          reporter(fullMessage);
        } catch (reportError) {
          console.error(\`\${LOG_PREFIX} Failed to report issue\`, reportError);
        }
      }

      const logArgs = error ? [fullMessage, error] : [fullMessage];
      if (level === "error") {
        console.error(...logArgs);
      } else {
        console.warn(...logArgs);
      }
    }

    // State data
    const formData = {
      // Step 1: Policy Setup
      effectiveDate: '',
      term: 'Semi Annual',
      paymentMethod: 'Electronic Funds Transfer',
      policyType: 'Standard',
      customerDeclinedCredit: false,
      bumpLimits: 'Bump Up',

      // Step 2: Customer Information
      firstName: '',
      middleName: '',
      lastName: '',
      declinedEmail: false,
      declinedPhone: false,
      monthsAtResidence: 60,
      street: '',
      city: '',
      state: '',
      county: '',
      zipCode: '',
      mobilePhone: '',
      homePhone: '',
      workPhone: '',
      emailAddress: '',
      priorInsurance: false,
      reasonForNoInsurance: 'Other',

      // Step 3: Vehicle Details
      make: '',
      model: '',
      year: null,
      annualMiles: null,
      milesToWork: 0,
      leasedVehicle: false,
      percentToWork: 100,
      purchaseType: 'New',
      rideShare: false,
      salvaged: false,
      usage: 'Work School',
      odometer: 0,
      garagingStreet: '',
      garagingCity: '',
      garagingState: '',
      garagingZip: '',
      collisionDeductible: 'None',
      comprehensiveDeductible: 'None',
      rentalLimit: 'None',
      gapCoverage: false,
      customEquipmentValue: 0,
      safetyGlassCoverage: false,
      towingLimit: 'None',

      // Step 4: Driver Information
      driverFirstName: '',
      driverMiddleName: '',
      driverLastName: '',
      dateOfBirth: '',
      gender: 'Male',
      maritalStatus: 'Single',
      occupation: '',
      industry: '',
      monthsEmployed: 0,
      licenseStatus: 'Valid',
      monthsLicensed: 335,
      monthsStateLicensed: 335,
      monthsMvrExperience: 60,
      monthsSuspended: 0,
      stateLicensed: '',
      foreignNational: false,
      internationalLicense: false,
      educationLevel: 'Some College',
      relation: 'Insured',
      residencyStatus: 'Own',
      residencyType: 'Home',
      driverMilesToWork: 0,
      propertyInsurance: false,
      defensiveDriving: false,
      goodStudent: false,
      seniorDriver: false,
      multiplePolicies: false,
      sr22: false,
      sr22Reason: 'Other',
      sr22State: 'California',
      sr22Date: ''
    };

    let currentStep = 1;
    let isSending = false;

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
    ];

    // Create wizard HTML
    const wizard = document.createElement("div");
    wizard.className = "wizard";
    wizard.innerHTML = \`
      <div class="wizard__header">
        <div class="wizard__eyebrow">Personal Auto Quote</div>
        <h2 class="wizard__title">Complete Your Insurance Application</h2>
        <p class="wizard__description">We'll guide you through 5 quick steps to get your personalized quote</p>
      </div>

      <div class="wizard__stepper">
        <div class="wizard__step is-active" data-step="1">
          <div class="wizard__step-circle">1</div>
          <div class="wizard__step-label">Policy Setup</div>
        </div>
        <div class="wizard__step-divider"></div>
        <div class="wizard__step" data-step="2">
          <div class="wizard__step-circle">2</div>
          <div class="wizard__step-label">Customer Info</div>
        </div>
        <div class="wizard__step-divider"></div>
        <div class="wizard__step" data-step="3">
          <div class="wizard__step-circle">3</div>
          <div class="wizard__step-label">Vehicle</div>
        </div>
        <div class="wizard__step-divider"></div>
        <div class="wizard__step" data-step="4">
          <div class="wizard__step-circle">4</div>
          <div class="wizard__step-label">Driver</div>
        </div>
        <div class="wizard__step-divider"></div>
        <div class="wizard__step" data-step="5">
          <div class="wizard__step-circle">5</div>
          <div class="wizard__step-label">Review</div>
        </div>
      </div>

      <div class="wizard__content">
        <!-- Step 1: Policy Setup -->
        <div class="wizard__step-content is-active" data-step-content="1">
          <div class="wizard__form-section">
            <h3 class="wizard__section-title">Policy Details</h3>
            <div class="wizard__grid">
              <div class="wizard__field">
                <label class="wizard__label">Effective Date</label>
                <div class="wizard__input-wrapper">
                  <input type="date" class="wizard__input" data-field="effectiveDate">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Term</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="term">
                    <option value="Semi Annual">Semi-Annual</option>
                    <option value="Annual">Annual</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Payment Method</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="paymentMethod">
                    <option value="Standard">Standard</option>
                    <option value="Electronic Funds Transfer">Electronic Funds Transfer</option>
                    <option value="Paid In Full">Paid In Full</option>
                    <option value="Default">Default</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Policy Type</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="policyType">
                    <option value="Standard">Standard</option>
                    <option value="Preferred">Preferred</option>
                    <option value="Non-Standard">Non-Standard</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Bump Limits</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="bumpLimits">
                    <option value="Bump Up">Bump Up</option>
                    <option value="Bump Down">Bump Down</option>
                    <option value="No Bumping">None</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="customerDeclinedCredit">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">Customer Declined Credit</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 2: Customer Information -->
        <div class="wizard__step-content" data-step-content="2">
          <div class="wizard__form-section">
            <h3 class="wizard__section-title">Personal Information</h3>
            <div class="wizard__grid">
              <div class="wizard__field">
                <label class="wizard__label">First Name *</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" placeholder="John" data-field="firstName" required>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Middle Name</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" data-field="middleName">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Last Name *</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" placeholder="Smith" data-field="lastName" required>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Months at Residence</label>
                <div class="wizard__input-wrapper">
                  <input type="number" class="wizard__input" placeholder="60" data-field="monthsAtResidence">
                </div>
              </div>
            </div>
          </div>

          <div class="wizard__form-section">
            <h3 class="wizard__section-title">Address</h3>
            <div class="wizard__grid">
              <div class="wizard__field wizard__grid--full">
                <label class="wizard__label">Street *</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" placeholder="123 Main St" data-field="street" required>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">City *</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" placeholder="Long Beach" data-field="city" required>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">State *</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="state" required>
                    <option value="">Select state</option>
                    \${STATES.map(s => \`<option value="\${s.name}">\${s.name}</option>\`).join('')}
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">County</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" placeholder="Los Angeles" data-field="county">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">ZIP Code *</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" placeholder="90807" data-field="zipCode" required>
                </div>
              </div>
            </div>
          </div>

          <div class="wizard__form-section">
            <h3 class="wizard__section-title">Contact Information</h3>
            <div class="wizard__grid">
              <div class="wizard__field">
                <label class="wizard__label">Mobile Phone</label>
                <div class="wizard__input-wrapper">
                  <input type="tel" class="wizard__input" placeholder="562-787-8209" data-field="mobilePhone">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Home Phone</label>
                <div class="wizard__input-wrapper">
                  <input type="tel" class="wizard__input" data-field="homePhone">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Work Phone</label>
                <div class="wizard__input-wrapper">
                  <input type="tel" class="wizard__input" data-field="workPhone">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Email Address</label>
                <div class="wizard__input-wrapper">
                  <input type="email" class="wizard__input" placeholder="email@example.com" data-field="emailAddress">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="declinedEmail">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">Declined Email</span>
                </label>
              </div>
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="declinedPhone">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">Declined Phone</span>
                </label>
              </div>
            </div>
          </div>

          <div class="wizard__form-section">
            <h3 class="wizard__section-title">Prior Insurance</h3>
            <div class="wizard__grid">
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="priorInsurance">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">Had Prior Insurance</span>
                </label>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Reason for No Insurance</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" placeholder="Other" data-field="reasonForNoInsurance">
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 3: Vehicle Details -->
        <div class="wizard__step-content" data-step-content="3">
          <div class="wizard__form-section">
            <h3 class="wizard__section-title">Vehicle Information</h3>
            <div class="wizard__grid">
              <div class="wizard__field">
                <label class="wizard__label">Make *</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" placeholder="FORD" data-field="make" required>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Model *</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" placeholder="EDGE SEL" data-field="model" required>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Year *</label>
                <div class="wizard__input-wrapper">
                  <input type="number" class="wizard__input" placeholder="2018" data-field="year" required>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Annual Miles</label>
                <div class="wizard__input-wrapper">
                  <input type="number" class="wizard__input" placeholder="13400" data-field="annualMiles">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Miles to Work</label>
                <div class="wizard__input-wrapper">
                  <input type="number" class="wizard__input" placeholder="6" data-field="milesToWork">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Percent to Work</label>
                <div class="wizard__input-wrapper">
                  <input type="number" class="wizard__input" placeholder="100" data-field="percentToWork">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Purchase Type</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="purchaseType">
                    <option value="New">New</option>
                    <option value="Owned">Owned</option>
                    <option value="Financed">Financed</option>
                    <option value="Leased">Leased</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Usage</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="usage">
                    <option value="Artisan Use">Artisan Use</option>
                    <option value="Business Use">Business Use</option>
                    <option value="Farm">Farm</option>
                    <option value="Pleasure">Pleasure</option>
                    <option value="Work School">Work School</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Odometer</label>
                <div class="wizard__input-wrapper">
                  <input type="number" class="wizard__input" placeholder="0" data-field="odometer">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="leasedVehicle">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">Leased Vehicle</span>
                </label>
              </div>
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="rideShare">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">RideShare</span>
                </label>
              </div>
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="salvaged">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">Salvaged</span>
                </label>
              </div>
            </div>
          </div>

          <div class="wizard__form-section">
            <h3 class="wizard__section-title">Garaging Address</h3>
            <div class="wizard__grid">
              <div class="wizard__field wizard__grid--full">
                <label class="wizard__label">Street</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" placeholder="Same as customer address" data-field="garagingStreet">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">City</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" data-field="garagingCity">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">State</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="garagingState">
                    <option value="">Select state</option>
                    \${STATES.map(s => \`<option value="\${s.name}">\${s.name}</option>\`).join('')}
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">ZIP Code</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" data-field="garagingZip">
                </div>
              </div>
            </div>
          </div>

          <div class="wizard__form-section">
            <h3 class="wizard__section-title">Coverage Information</h3>
            <div class="wizard__grid">
              <div class="wizard__field">
                <label class="wizard__label">Collision Deductible</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="collisionDeductible">
                    <option value="None">None</option>
                    <option value="250">$250</option>
                    <option value="500">$500</option>
                    <option value="1000">$1,000</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Comprehensive Deductible</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="comprehensiveDeductible">
                    <option value="None">None</option>
                    <option value="250">$250</option>
                    <option value="500">$500</option>
                    <option value="1000">$1,000</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Rental Limit</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="rentalLimit">
                    <option value="None">None</option>
                    <option value="500">$500</option>
                    <option value="1000">$1,000</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Towing Limit</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="towingLimit">
                    <option value="None">None</option>
                    <option value="500">$500</option>
                    <option value="1000">$1,000</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Custom Equipment Value</label>
                <div class="wizard__input-wrapper">
                  <input type="number" class="wizard__input" placeholder="0" data-field="customEquipmentValue">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="gapCoverage">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">Gap Coverage</span>
                </label>
              </div>
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="safetyGlassCoverage">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">Safety Glass Coverage</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 4: Driver Information -->
        <div class="wizard__step-content" data-step-content="4">
          <div class="wizard__form-section">
            <h3 class="wizard__section-title">Driver Details</h3>
            <div class="wizard__grid">
              <div class="wizard__field">
                <label class="wizard__label">First Name *</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" placeholder="CATest" data-field="driverFirstName" required>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Middle Name</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" data-field="driverMiddleName">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Last Name *</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" placeholder="LongBeach" data-field="driverLastName" required>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Date of Birth *</label>
                <div class="wizard__input-wrapper">
                  <input type="date" class="wizard__input" data-field="dateOfBirth" required>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Gender</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="gender">
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Marital Status</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="maritalStatus">
                    <option value="Single">Single</option>
                    <option value="Married">Married</option>
                    <option value="Divorced">Divorced</option>
                    <option value="Widowed">Widowed</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Occupation</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" placeholder="Engineer" data-field="occupation">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Industry</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" placeholder="Engineer/Architect/Science/Math" data-field="industry">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Months Employed</label>
                <div class="wizard__input-wrapper">
                  <input type="number" class="wizard__input" placeholder="0" data-field="monthsEmployed">
                </div>
              </div>
            </div>
          </div>

          <div class="wizard__form-section">
            <h3 class="wizard__section-title">License Information</h3>
            <div class="wizard__grid">
              <div class="wizard__field">
                <label class="wizard__label">License Status</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="licenseStatus">
                    <option value="Valid">Valid</option>
                    <option value="Expired">Expired</option>
                    <option value="Suspended">Suspended</option>
                    <option value="Revoked">Revoked</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">State Licensed</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="stateLicensed">
                    <option value="">Select state</option>
                    \${STATES.map(s => \`<option value="\${s.name}">\${s.name}</option>\`).join('')}
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Months Licensed</label>
                <div class="wizard__input-wrapper">
                  <input type="number" class="wizard__input" placeholder="335" data-field="monthsLicensed">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Months State Licensed</label>
                <div class="wizard__input-wrapper">
                  <input type="number" class="wizard__input" placeholder="335" data-field="monthsStateLicensed">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Months MVR Experience</label>
                <div class="wizard__input-wrapper">
                  <input type="number" class="wizard__input" placeholder="60" data-field="monthsMvrExperience">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Months Suspended</label>
                <div class="wizard__input-wrapper">
                  <input type="number" class="wizard__input" placeholder="0" data-field="monthsSuspended">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="foreignNational">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">Foreign National</span>
                </label>
              </div>
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="internationalLicense">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">International License</span>
                </label>
              </div>
            </div>
          </div>

          <div class="wizard__form-section">
            <h3 class="wizard__section-title">Attributes</h3>
            <div class="wizard__grid">
              <div class="wizard__field">
                <label class="wizard__label">Education Level</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="educationLevel">
                    <option value="Some College">Some College</option>
                    <option value="High School">High School</option>
                    <option value="Bachelor">Bachelor's Degree</option>
                    <option value="Graduate">Graduate Degree</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Relation</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="relation">
                    <option value="Insured">Insured</option>
                    <option value="Spouse">Spouse</option>
                    <option value="Child">Child</option>
                    <option value="Parent">Parent</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Residency Status</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="residencyStatus">
                    <option value="Own">Own</option>
                    <option value="Rent">Rent</option>
                    <option value="Lease">Lease</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Residency Type</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="residencyType">
                    <option value="Home">Home</option>
                    <option value="Apartment">Apartment</option>
                    <option value="Condo">Condo</option>
                    <option value="Mobile Home">Mobile Home</option>
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">Miles to Work</label>
                <div class="wizard__input-wrapper">
                  <input type="number" class="wizard__input" placeholder="0" data-field="driverMilesToWork">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="propertyInsurance">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">Property Insurance</span>
                </label>
              </div>
            </div>
          </div>

          <div class="wizard__form-section">
            <h3 class="wizard__section-title">Discounts</h3>
            <div class="wizard__grid">
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="defensiveDriving">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">Defensive Driving</span>
                </label>
              </div>
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="goodStudent">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">Good Student</span>
                </label>
              </div>
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="seniorDriver">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">Senior Driver</span>
                </label>
              </div>
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="multiplePolicies">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">Multiple Policies</span>
                </label>
              </div>
            </div>
          </div>

          <div class="wizard__form-section">
            <h3 class="wizard__section-title">SR-22 Information</h3>
            <div class="wizard__grid">
              <div class="wizard__field">
                <label class="wizard__toggle">
                  <input type="checkbox" data-field="sr22">
                  <span class="wizard__toggle-switch"></span>
                  <span class="wizard__label">SR-22 Required</span>
                </label>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">SR-22 Reason</label>
                <div class="wizard__input-wrapper">
                  <input type="text" class="wizard__input" placeholder="Other" data-field="sr22Reason">
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">SR-22 State</label>
                <div class="wizard__input-wrapper">
                  <select class="wizard__select" data-field="sr22State">
                    <option value="">Select state</option>
                    \${STATES.map(s => \`<option value="\${s.name}">\${s.name}</option>\`).join('')}
                  </select>
                </div>
              </div>
              <div class="wizard__field">
                <label class="wizard__label">SR-22 Date</label>
                <div class="wizard__input-wrapper">
                  <input type="date" class="wizard__input" data-field="sr22Date">
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 5: Review & Submit -->
        <div class="wizard__step-content" data-step-content="5">
          <div id="review-container"></div>
        </div>
      </div>

      <div class="wizard__actions">
        <button type="button" class="wizard__button wizard__button--secondary" id="prevBtn">Previous</button>
        <button type="button" class="wizard__button wizard__button--primary" id="nextBtn">Next</button>
      </div>
    \`;

    root.appendChild(wizard);

    const prevBtn = wizard.querySelector('#prevBtn');
    const nextBtn = wizard.querySelector('#nextBtn');
    const reviewContainer = wizard.querySelector('#review-container');

    // Bind form inputs to formData
    function bindInputs() {
      const inputs = wizard.querySelectorAll('[data-field]');
      inputs.forEach(input => {
        const field = input.getAttribute('data-field');
        if (input.type === 'checkbox') {
          input.checked = formData[field];
          input.addEventListener('change', () => {
            formData[field] = input.checked;
          });
        } else {
          input.value = formData[field] !== null && formData[field] !== undefined ? formData[field] : '';
          input.addEventListener('input', () => {
            const value = input.value;
            formData[field] = input.type === 'number' ? (value ? parseInt(value) : null) : value;
          });
        }
      });
    }

    bindInputs();

    function goToStep(step) {
      currentStep = step;

      // Update step indicators
      wizard.querySelectorAll('.wizard__step').forEach((stepEl, idx) => {
        const stepNum = idx + 1;
        stepEl.classList.remove('is-active', 'is-completed');
        if (stepNum === currentStep) {
          stepEl.classList.add('is-active');
        } else if (stepNum < currentStep) {
          stepEl.classList.add('is-completed');
        }
      });

      // Update step content
      wizard.querySelectorAll('.wizard__step-content').forEach((content, idx) => {
        const stepNum = idx + 1;
        content.classList.toggle('is-active', stepNum === currentStep);
      });

      // Update buttons
      prevBtn.style.display = currentStep === 1 ? 'none' : 'block';
      if (currentStep === 5) {
        nextBtn.textContent = 'Confirm & Submit';
        renderReview();
      } else {
        nextBtn.textContent = 'Next';
      }
    }

    function renderReview() {
      const stateObj = STATES.find(s => s.name === formData.state);
      const stateCode = stateObj ? stateObj.code : '';

      reviewContainer.innerHTML = \`
        <div class="wizard__review-section">
          <div class="wizard__review-header">
            <h4 class="wizard__review-title">Policy Setup</h4>
            <button class="wizard__review-edit" onclick="window.goToStep(1)">Edit</button>
          </div>
          <div class="wizard__review-grid">
            <span class="wizard__review-label">Effective Date:</span>
            <span class="wizard__review-value">\${formData.effectiveDate || 'Not set'}</span>
            <span class="wizard__review-label">Term:</span>
            <span class="wizard__review-value">\${formData.term}</span>
            <span class="wizard__review-label">Payment Method:</span>
            <span class="wizard__review-value">\${formData.paymentMethod}</span>
            <span class="wizard__review-label">Policy Type:</span>
            <span class="wizard__review-value">\${formData.policyType}</span>
            <span class="wizard__review-label">Bump Limits:</span>
            <span class="wizard__review-value">\${formData.bumpLimits}</span>
          </div>
        </div>

        <div class="wizard__review-section">
          <div class="wizard__review-header">
            <h4 class="wizard__review-title">Customer Information</h4>
            <button class="wizard__review-edit" onclick="window.goToStep(2)">Edit</button>
          </div>
          <div class="wizard__review-grid">
            <span class="wizard__review-label">Name:</span>
            <span class="wizard__review-value">\${formData.firstName} \${formData.middleName} \${formData.lastName}</span>
            <span class="wizard__review-label">Address:</span>
            <span class="wizard__review-value">\${formData.street}, \${formData.city}, \${stateCode} \${formData.zipCode}</span>
            <span class="wizard__review-label">Email:</span>
            <span class="wizard__review-value">\${formData.emailAddress || 'Not provided'}</span>
            <span class="wizard__review-label">Phone:</span>
            <span class="wizard__review-value">\${formData.mobilePhone || formData.homePhone || 'Not provided'}</span>
          </div>
        </div>

        <div class="wizard__review-section">
          <div class="wizard__review-header">
            <h4 class="wizard__review-title">Vehicle</h4>
            <button class="wizard__review-edit" onclick="window.goToStep(3)">Edit</button>
          </div>
          <div class="wizard__review-grid">
            <span class="wizard__review-label">Vehicle:</span>
            <span class="wizard__review-value">\${formData.year || ''} \${formData.make} \${formData.model}</span>
            <span class="wizard__review-label">Usage:</span>
            <span class="wizard__review-value">\${formData.usage}</span>
          </div>
        </div>

        <div class="wizard__review-section">
          <div class="wizard__review-header">
            <h4 class="wizard__review-title">Driver</h4>
            <button class="wizard__review-edit" onclick="window.goToStep(4)">Edit</button>
          </div>
          <div class="wizard__review-grid">
            <span class="wizard__review-label">Name:</span>
            <span class="wizard__review-value">\${formData.driverFirstName} \${formData.driverMiddleName} \${formData.driverLastName}</span>
            <span class="wizard__review-label">DOB:</span>
            <span class="wizard__review-value">\${formData.dateOfBirth || 'Not set'}</span>
            <span class="wizard__review-label">Gender:</span>
            <span class="wizard__review-value">\${formData.gender}</span>
            <span class="wizard__review-label">Marital Status:</span>
            <span class="wizard__review-value">\${formData.maritalStatus}</span>
          </div>
        </div>
      \`;
    }

    // Make goToStep globally accessible for review edit buttons
    window.goToStep = goToStep;

    prevBtn.addEventListener('click', () => {
      if (currentStep > 1) {
        goToStep(currentStep - 1);
      }
    });

    nextBtn.addEventListener('click', async () => {
      if (currentStep < 5) {
        goToStep(currentStep + 1);
      } else {
        // Submit
        if (isSending) return;
        isSending = true;
        nextBtn.disabled = true;
        nextBtn.textContent = 'Submitting...';

        try {
          await submitQuote();
        } catch (error) {
          notifyIssue('error', 'Failed to submit quote', error);
          nextBtn.disabled = false;
          nextBtn.textContent = 'Confirm & Submit';
          isSending = false;
        }
      }
    });

    async function submitQuote() {
      // Build payload matching the structure user provided
      const stateObj = STATES.find(s => s.name === formData.state);
      const stateCode = stateObj ? stateObj.code : 'CA';

      const payload = {
        "Identifier": \`\${formData.firstName.charAt(0).toLowerCase()}\${formData.lastName.toLowerCase()}-\${Date.now()}\`,
        "EffectiveDate": formData.effectiveDate ? new Date(formData.effectiveDate).toISOString() : new Date().toISOString(),
        "CustomerDeclinedCredit": formData.customerDeclinedCredit,
        "BumpLimits": formData.bumpLimits,
        "Term": formData.term,
        "PaymentMethod": formData.paymentMethod,
        "PolicyType": formData.policyType,
        "Customer": {
          "Identifier": \`\${stateCode}-\${formData.firstName}\${formData.lastName}-\${Date.now()}\`,
          "FirstName": formData.firstName,
          "MiddleName": formData.middleName || "",
          "LastName": formData.lastName,
          "DeclinedEmail": formData.declinedEmail,
          "DeclinedPhone": formData.declinedPhone,
          "MonthsAtResidence": formData.monthsAtResidence || 60,
          "Address": {
            "Street1": formData.street,
            "City": formData.city,
            "State": formData.state,
            "County": formData.county || "",
            "ZipCode": formData.zipCode
          },
          "ContactInformation": {
            "MobilePhone": formData.mobilePhone || "",
            "HomePhone": formData.homePhone || "",
            "WorkPhone": formData.workPhone || "",
            "EmailAddress": formData.emailAddress || ""
          },
          "PriorInsuranceInformation": {
            "PriorInsurance": formData.priorInsurance,
            "ReasonForNoInsurance": formData.reasonForNoInsurance || "Other"
          }
        },
        "PolicyCoverages": {
          "LiabilityBiLimit": "30000/60000",
          "LiabilityPdLimit": "15000",
          "MedPayLimit": "None",
          "UninsuredMotoristBiLimit": "30000/60000",
          "AccidentalDeathLimit": "None",
          "UninsuredMotoristPd/CollisionDamageWaiver": false
        },
        "RatedDrivers": [{
          "DriverId": 1,
          "FirstName": formData.driverFirstName,
          "MiddleName": formData.driverMiddleName || "",
          "LastName": formData.driverLastName,
          "DateOfBirth": formData.dateOfBirth ? new Date(formData.dateOfBirth).toISOString() : "",
          "Gender": formData.gender,
          "MaritalStatus": formData.maritalStatus,
          "MonthsEmployed": formData.monthsEmployed || 0,
          "Industry": formData.industry || "",
          "Occupation": formData.occupation || "",
          "LicenseInformation": {
            "LicenseStatus": formData.licenseStatus,
            "MonthsForeignLicense": 0,
            "MonthsLicensed": formData.monthsLicensed || 335,
            "MonthsStateLicensed": formData.monthsStateLicensed || 335,
            "MonthsMvrExperience": formData.monthsMvrExperience || 60,
            "MonthsSuspended": formData.monthsSuspended || 0,
            "StateLicensed": formData.stateLicensed || formData.state,
            "CountryOfOrigin": "None",
            "ForeignNational": formData.foreignNational,
            "InternationalDriversLicense": formData.internationalLicense
          },
          "Attributes": {
            "EducationLevel": formData.educationLevel,
            "OccasionalOperator": false,
            "PropertyInsurance": formData.propertyInsurance,
            "Relation": formData.relation,
            "ResidencyStatus": formData.residencyStatus,
            "ResidencyType": formData.residencyType,
            "MilesToWork": formData.driverMilesToWork || 0
          },
          "Discounts": {
            "DistantStudent": "None",
            "DriversTraining": false,
            "DrugAwareness": false,
            "GoodStudent": formData.goodStudent,
            "SingleParent": false,
            "SeniorDriverDiscount": formData.seniorDriver,
            "MultiplePolicies": formData.multiplePolicies,
            "DefensiveDriving": formData.defensiveDriving
          },
          "FinancialResponsibilityInformation": {
            "Sr22": formData.sr22,
            "Sr22Reason": formData.sr22Reason || "Other",
            "Sr22State": formData.sr22State || formData.state,
            "Sr22Date": formData.sr22Date ? new Date(formData.sr22Date).toISOString() : new Date().toISOString()
          }
        }],
        "Vehicles": [{
          "VehicleId": 1,
          "Make": formData.make,
          "Model": formData.model,
          "Year": formData.year || 2018,
          "AnnualMiles": formData.annualMiles || 13400,
          "AssignedDriverId": 1,
          "MilesToWork": formData.milesToWork || 6,
          "Odometer": formData.odometer || 0,
          "LeasedVehicle": formData.leasedVehicle,
          "PercentToWork": formData.percentToWork || 100,
          "PurchaseType": formData.purchaseType,
          "RideShare": formData.rideShare,
          "Salvaged": formData.salvaged,
          "Usage": formData.usage,
          "GaragingAddress": {
            "Street1": formData.garagingStreet || formData.street,
            "City": formData.garagingCity || formData.city,
            "State": formData.garagingState || formData.state,
            "ZipCode": formData.garagingZip || formData.zipCode
          },
          "CoverageInformation": {
            "CollisionDeductible": formData.collisionDeductible,
            "ComprehensiveDeductible": formData.comprehensiveDeductible,
            "RentalLimit": formData.rentalLimit,
            "GapCoverage": formData.gapCoverage,
            "CustomEquipmentValue": formData.customEquipmentValue || 0,
            "SafetyGlassCoverage": formData.safetyGlassCoverage,
            "TowingLimit": formData.towingLimit
          }
        }],
        "CarrierInformation": {
          "UseExactCarrierInfo": false,
          "Products": [
            {
              "AgencyId": "456494ef-0742-499c-92e0-db9fc8c78941",
              "ProductId": "9c0220c6-49c4-4358-aefc-d5bc51630fe5",
              "ProductName": "Anchor Gemini",
              "CarrierUserName": "autoinsspec",
              "CarrierPassword": "character99",
              "ProducerCode": "92000",
              "CarrierLoginUserName": "",
              "CarrierLoginPassword": "",
              "CarrierId": "0b0ab021-dd46-4d60-8cd5-e22901030008",
              "CarrierName": "Anchor General Ins"
            },
            {
              "AgencyId": "456494ef-0742-499c-92e0-db9fc8c78941",
              "ProductId": "5e9d28df-214d-4dfc-b723-2f2abd3f5ee5",
              "ProductName": "Anchor Motor Club",
              "CarrierUserName": "autoinsspec",
              "CarrierPassword": "charachter99",
              "ProducerCode": "92002",
              "CarrierLoginUserName": "",
              "CarrierLoginPassword": "",
              "CarrierId": "0b0ab021-dd46-4d60-8cd5-e22901030008",
              "CarrierName": "Anchor General Ins",
              "ProductQuestions": {
                "AnchorMotorClubV3RTCollBuyback": {
                  "Id": "0-AnchorMotorClubV3RTCollBuyback",
                  "Value": "Yes"
                }
              }
            },
            {
              "AgencyId": "456494ef-0742-499c-92e0-db9fc8c78941",
              "ProductId": "bdd4c0f9-7c50-45dc-a5df-deac8ac717fe",
              "ProductName": "Anchor Premier",
              "CarrierUserName": "autoinsspec",
              "CarrierPassword": "charachter99",
              "ProducerCode": "92840",
              "CarrierLoginUserName": "",
              "CarrierLoginPassword": "",
              "CarrierId": "0b0ab021-dd46-4d60-8cd5-e22901030008",
              "CarrierName": "Anchor General Ins",
              "ProductQuestions": {
                "AnchorPremierV3MPP": {
                  "Id": "0-AnchorPremierV3MPP",
                  "Value": "Yes"
                },
                "AnchorPremierV3RTCollBuyback": {
                  "Id": "0-AnchorPremierV3RTCollBuyback",
                  "Value": "Yes"
                }
              }
            }
          ]
        }
      };

      // Send to assistant
      if (window.openai && typeof window.openai.sendFollowUpMessage === "function") {
        try {
          await window.openai.sendFollowUpMessage({
            prompt: \`I've completed the insurance application form. Please submit this quote for rating.\`,
            metadata: { quotePayload: payload }
          });
          nextBtn.textContent = 'Submitted!';
        } catch (error) {
          throw error;
        }
      } else {
        console.warn('OpenAI sendFollowUpMessage not available');
        nextBtn.textContent = 'Submit (API unavailable)';
      }

      isSending = false;
    }

    // Set today as default effective date
    const today = new Date().toISOString().split('T')[0];
    formData.effectiveDate = today;
    const effectiveDateInput = wizard.querySelector('[data-field="effectiveDate"]');
    if (effectiveDateInput) {
      effectiveDateInput.value = today;
    }
  })();
</script>
""".strip()
