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
    color: #0f172a;
  }

  @media (prefers-color-scheme: dark) {
    #insurance-state-root {
      color: #f8fafc;
    }
  }

  .mercury-widget {
    position: relative;
    overflow: hidden;
    border-radius: 28px;
    border: 1px solid rgba(15, 23, 42, 0.14);
    min-height: 320px;
    padding: 32px;
    display: flex;
    align-items: center;
    isolation: isolate;
    background: radial-gradient(circle at 18% 24%, rgba(30, 64, 175, 0.9), rgba(15, 23, 42, 0.95));
    color: #fff;
  }

  .mercury-widget::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image: linear-gradient(120deg, rgba(15, 23, 42, 0.3) 10%, rgba(15, 23, 42, 0.75) 65%, rgba(15, 23, 42, 0.95)),
      url("https://persistent.oaistatic.com/mercury/hero-family.webp");
    background-size: cover;
    background-position: center;
    z-index: -2;
  }

  .mercury-widget::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(0deg, rgba(15, 23, 42, 0.85) 12%, rgba(15, 23, 42, 0.45) 100%);
    z-index: -1;
  }

  @media (prefers-color-scheme: dark) {
    .mercury-widget {
      border-color: rgba(148, 163, 184, 0.32);
      background: radial-gradient(circle at 12% 20%, rgba(59, 130, 246, 0.18), rgba(15, 23, 42, 0.95));
    }

    .mercury-widget::before {
      opacity: 0.45;
    }

    .mercury-widget::after {
      background: linear-gradient(0deg, rgba(15, 23, 42, 0.85) 8%, rgba(15, 23, 42, 0.4) 100%);
    }
  }

  .mercury-widget__content {
    max-width: 440px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .mercury-widget__eyebrow {
    text-transform: uppercase;
    font-size: 12px;
    letter-spacing: 0.18em;
    font-weight: 600;
    color: rgba(165, 243, 252, 0.85);
  }

  .mercury-widget__headline {
    margin: 0;
    font-weight: 800;
    line-height: 1.1;
    font-size: clamp(26px, 3.2vw, 36px);
  }

  .mercury-widget__headline strong {
    color: rgba(252, 211, 77, 0.95);
  }

  .mercury-widget__subhead {
    margin: 0;
    font-size: 15px;
    line-height: 1.6;
    color: rgba(255, 255, 255, 0.86);
  }

  .mercury-widget__form {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .mercury-widget__fields {
    display: grid;
    grid-template-columns: minmax(160px, 1fr) minmax(160px, 1fr);
    gap: 12px;
  }

  .mercury-widget__field {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .mercury-widget__label {
    font-size: 13px;
    font-weight: 600;
    color: rgba(226, 232, 240, 0.82);
  }

  .mercury-widget__control {
    height: 48px;
    border-radius: 14px;
    border: none;
    padding: 0 16px;
    font-size: 15px;
    font-weight: 600;
    color: #0f172a;
    background: rgba(255, 255, 255, 0.96);
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.2);
  }

  .mercury-widget__control:focus {
    outline: 3px solid rgba(59, 130, 246, 0.4);
    outline-offset: 0;
  }

  .mercury-widget__control::placeholder {
    color: rgba(51, 65, 85, 0.48);
  }

  .mercury-widget__button {
    height: 52px;
    border-radius: 16px;
    border: none;
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    background: linear-gradient(90deg, #fde68a, #fbbf24, #f59e0b);
    box-shadow: 0 18px 32px rgba(250, 204, 21, 0.35);
    cursor: pointer;
    transition: transform 160ms ease, box-shadow 160ms ease;
  }

  .mercury-widget__button:hover:not([aria-disabled="true"]) {
    transform: translateY(-1px);
    box-shadow: 0 20px 40px rgba(250, 204, 21, 0.45);
  }

  .mercury-widget__button[aria-disabled="true"] {
    opacity: 0.6;
    cursor: not-allowed;
    box-shadow: none;
  }

  .mercury-widget__error {
    font-size: 13px;
    color: #fee2e2;
    min-height: 18px;
  }

  .mercury-widget__footer {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    font-size: 13px;
    color: rgba(255, 255, 255, 0.82);
  }

  .mercury-widget__footer a {
    color: inherit;
    font-weight: 600;
    text-decoration: none;
  }

  .mercury-widget__footer a:hover {
    text-decoration: underline;
  }

  .mercury-widget__footnote {
    font-size: 11px;
    color: rgba(226, 232, 240, 0.75);
    margin: 0;
  }

  @media (max-width: 640px) {
    .mercury-widget {
      padding: 24px;
      border-radius: 22px;
    }

    .mercury-widget__fields {
      grid-template-columns: 1fr;
    }
  }

  @media (prefers-color-scheme: dark) {
    .mercury-widget__label {
      color: rgba(203, 213, 225, 0.92);
    }

    .mercury-widget__control {
      background: rgba(226, 232, 240, 0.96);
      color: #0f172a;
    }

    .mercury-widget__button {
      color: #78350f;
    }

    .mercury-widget__error {
      color: #fecaca;
    }
  }
</style>
<script type="module">
  (function () {
    const root = document.getElementById("insurance-state-root");
    if (!root) return;

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

    const PRODUCTS = [
      { value: "auto", label: "Auto Insurance" },
      { value: "home", label: "Home Insurance" },
      { value: "renters", label: "Renters Insurance" },
      { value: "condo", label: "Condo Insurance" },
      { value: "umbrella", label: "Umbrella Insurance" }
    ];

    const container = document.createElement("div");
    container.className = "mercury-widget";

    const content = document.createElement("div");
    content.className = "mercury-widget__content";

    const eyebrow = document.createElement("span");
    eyebrow.className = "mercury-widget__eyebrow";
    eyebrow.textContent = "Drivers save";

    const headline = document.createElement("h2");
    headline.className = "mercury-widget__headline";
    headline.innerHTML = "Drivers save <strong>hundreds*</strong> when switching to Mercury Insurance";

    const subhead = document.createElement("p");
    subhead.className = "mercury-widget__subhead";
    subhead.textContent = "Enter your details below to jump straight into your Mercury quote.";

    const form = document.createElement("form");
    form.className = "mercury-widget__form";
    form.setAttribute("novalidate", "novalidate");

    const fields = document.createElement("div");
    fields.className = "mercury-widget__fields";

    const productField = document.createElement("div");
    productField.className = "mercury-widget__field";
    const productLabel = document.createElement("label");
    productLabel.className = "mercury-widget__label";
    productLabel.setAttribute("for", "mercury-product");
    productLabel.textContent = "Insurance product";
    const productSelect = document.createElement("select");
    productSelect.id = "mercury-product";
    productSelect.className = "mercury-widget__control";
    PRODUCTS.forEach((option) {
      const opt = document.createElement("option");
      opt.value = option.value;
      opt.textContent = option.label;
      productSelect.appendChild(opt);
    });
    productField.appendChild(productLabel);
    productField.appendChild(productSelect);

    const stateField = document.createElement("div");
    stateField.className = "mercury-widget__field";
    const stateLabel = document.createElement("label");
    stateLabel.className = "mercury-widget__label";
    stateLabel.setAttribute("for", "mercury-state");
    stateLabel.textContent = "Your state";
    const stateSelect = document.createElement("select");
    stateSelect.id = "mercury-state";
    stateSelect.className = "mercury-widget__control";
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Select a state";
    placeholder.disabled = true;
    placeholder.selected = true;
    stateSelect.appendChild(placeholder);
    STATES.forEach((state) => {
      const opt = document.createElement("option");
      opt.value = state.code;
      opt.textContent = `${state.name} (${state.code})`;
      stateSelect.appendChild(opt);
    });
    stateField.appendChild(stateLabel);
    stateField.appendChild(stateSelect);

    const zipField = document.createElement("div");
    zipField.className = "mercury-widget__field";
    const zipLabel = document.createElement("label");
    zipLabel.className = "mercury-widget__label";
    zipLabel.setAttribute("for", "mercury-zip");
    zipLabel.textContent = "Zip code";
    const zipInput = document.createElement("input");
    zipInput.id = "mercury-zip";
    zipInput.className = "mercury-widget__control";
    zipInput.type = "text";
    zipInput.inputMode = "numeric";
    zipInput.placeholder = "Enter ZIP";
    zipInput.setAttribute("maxlength", "10");
    zipField.appendChild(zipLabel);
    zipField.appendChild(zipInput);

    const zipError = document.createElement("div");
    zipError.className = "mercury-widget__error";

    const button = document.createElement("button");
    button.type = "submit";
    button.className = "mercury-widget__button";
    button.textContent = "Get a quote";
    button.setAttribute("aria-disabled", "true");
    button.disabled = true;

    const footer = document.createElement("div");
    footer.className = "mercury-widget__footer";
    footer.innerHTML = `Or call <a href="tel:18009563728">(800) 956-3728</a> · <a href="https://www.mercuryinsurance.com/agent" target="_blank" rel="noopener">Find an agent</a> · <a href="https://www.mercuryinsurance.com/payment" target="_blank" rel="noopener">Make a one-time payment</a>`;

    const footnote = document.createElement("p");
    footnote.className = "mercury-widget__footnote";
    footnote.textContent = "*Savings data based on Mercury internal analysis.";

    fields.appendChild(productField);
    fields.appendChild(stateField);
    fields.appendChild(zipField);

    form.appendChild(fields);
    form.appendChild(zipError);
    form.appendChild(button);

    content.appendChild(eyebrow);
    content.appendChild(headline);
    content.appendChild(subhead);
    content.appendChild(form);
    content.appendChild(footer);
    content.appendChild(footnote);

    container.appendChild(content);
    root.appendChild(container);

    let isSending = false;

    function findState(code) {
      if (!code) return null;
      return STATES.find((state) => state.code === code.toUpperCase()) ?? null;
    }

    function getGlobals() {
      if (typeof window === "undefined" || !window.openai) return {};
      return window.openai;
    }

    function persistWidgetState() {
      const globals = getGlobals();
      if (!globals || typeof globals.setWidgetState !== "function") return;
      const state = stateSelect.value;
      const stateMeta = findState(state);
      const payload = {
        state: stateMeta ? stateMeta.name : state || null,
        stateCode: stateMeta ? stateMeta.code : state || null,
        zip: zipInput.value.trim(),
        product: productSelect.value,
      };
      try {
        void globals.setWidgetState(payload);
      } catch (error) {
        console.warn("Failed to persist widget state", error);
      }
    }

    function validateZip(value) {
      if (!value) return false;
      const trimmed = value.trim();
      return /^[0-9]{5}(?:-[0-9]{4})?$/.test(trimmed);
    }

    function updateButtonState() {
      const hasState = !!stateSelect.value;
      const zipValid = validateZip(zipInput.value);
      const enabled = hasState && zipValid && !isSending;
      button.disabled = !enabled;
      button.setAttribute("aria-disabled", enabled ? "false" : "true");
      if (!zipValid && zipInput.value.trim().length > 0) {
        zipError.textContent = "Enter a valid 5-digit ZIP (optionally with +4).";
      } else {
        zipError.textContent = "";
      }
    }

    function openQuote(url) {
      const globals = getGlobals();
      if (globals && typeof globals.openExternal === "function") {
        globals.openExternal({ href: url });
        return;
      }
      window.open(url, "_blank", "noopener,noreferrer");
    }

    async function notifyAssistant(stateMeta, zip, product) {
      const globals = getGlobals();
      if (!globals || typeof globals.sendFollowUpMessage !== "function") return;
      const prettyState = stateMeta ? `${stateMeta.name} (${stateMeta.code})` : stateSelect.value;
      const message = `I'm starting a Mercury ${product} insurance quote for ${prettyState} at ZIP ${zip}.`;
      try {
        await globals.sendFollowUpMessage({ prompt: message });
      } catch (error) {
        console.warn("Failed to notify assistant", error);
      }
    }

    stateSelect.addEventListener("change", () => {
      persistWidgetState();
      updateButtonState();
    });

    productSelect.addEventListener("change", () => {
      persistWidgetState();
    });

    zipInput.addEventListener("input", () => {
      persistWidgetState();
      updateButtonState();
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (isSending) return;
      const selectedState = findState(stateSelect.value);
      const zip = zipInput.value.trim();
      const product = productSelect.value || "auto";
      if (!selectedState || !validateZip(zip)) {
        updateButtonState();
        return;
      }

      const url = `https://buy.mercuryinsurance.com/${product}/create?zip=${encodeURIComponent(zip)}&state=${encodeURIComponent(selectedState.code)}`;

      isSending = true;
      button.textContent = "Opening quote…";
      updateButtonState();

      try {
        openQuote(url);
        await notifyAssistant(selectedState, zip, productSelect.options[productSelect.selectedIndex].textContent || product);
      } finally {
        isSending = false;
        button.textContent = "Get a quote";
        updateButtonState();
      }
    });

    const globals = getGlobals();
    const initialStateValue = (() => {
      const toolOutput = globals.toolOutput && typeof globals.toolOutput === "object" ? globals.toolOutput : null;
      const widgetState = globals.widgetState && typeof globals.widgetState === "object" ? globals.widgetState : null;
      const stateFromTool = toolOutput && typeof toolOutput.stateCode === "string" ? toolOutput.stateCode : null;
      const stateFromWidget = widgetState && typeof widgetState.stateCode === "string" ? widgetState.stateCode : null;
      const fallbackName = toolOutput && typeof toolOutput.state === "string" ? toolOutput.state : null;
      const fallbackWidgetName = widgetState && typeof widgetState.state === "string" ? widgetState.state : null;
      return stateFromTool || stateFromWidget || fallbackName || fallbackWidgetName || "";
    })();

    const initialZipValue = (() => {
      const toolOutput = globals.toolOutput && typeof globals.toolOutput === "object" ? globals.toolOutput : null;
      const widgetState = globals.widgetState && typeof globals.widgetState === "object" ? globals.widgetState : null;
      const fromTool = toolOutput && typeof toolOutput.zip === "string" ? toolOutput.zip : null;
      const fromWidget = widgetState && typeof widgetState.zip === "string" ? widgetState.zip : null;
      return fromTool || fromWidget || "";
    })();

    const initialProductValue = (() => {
      const toolOutput = globals.toolOutput && typeof globals.toolOutput === "object" ? globals.toolOutput : null;
      const widgetState = globals.widgetState && typeof globals.widgetState === "object" ? globals.widgetState : null;
      const fromTool = toolOutput && typeof toolOutput.product === "string" ? toolOutput.product : null;
      const fromWidget = widgetState && typeof widgetState.product === "string" ? widgetState.product : null;
      return fromTool || fromWidget || "auto";
    })();

    const normalizedInitialState = (() => {
      if (!initialStateValue) return "";
      const fromCode = findState(initialStateValue);
      if (fromCode) return fromCode.code;
      const normalized = STATES.find((state) => state.name.toLowerCase() === String(initialStateValue).toLowerCase());
      return normalized ? normalized.code : "";
    })();

    if (normalizedInitialState) {
      stateSelect.value = normalizedInitialState;
    }

    if (initialZipValue) {
      zipInput.value = initialZipValue;
    }

    if (initialProductValue) {
      const exists = PRODUCTS.some((item) => item.value === initialProductValue);
      productSelect.value = exists ? initialProductValue : "auto";
    }

    persistWidgetState();
    updateButtonState();

    window.addEventListener("openai:set_globals", (event) => {
      const detail = event.detail;
      if (!detail || !detail.globals) return;
      const { globals: updated } = detail;

      if (updated.toolOutput && typeof updated.toolOutput === "object" && updated.toolOutput !== null) {
        if (typeof updated.toolOutput.stateCode === "string") {
          const state = findState(updated.toolOutput.stateCode);
          if (state) {
            stateSelect.value = state.code;
          }
        } else if (typeof updated.toolOutput.state === "string") {
          const state = findState(updated.toolOutput.state) || STATES.find((item) => item.name === updated.toolOutput.state);
          if (state) {
            stateSelect.value = state.code;
          }
        }

        if (typeof updated.toolOutput.zip === "string") {
          zipInput.value = updated.toolOutput.zip;
        }

        if (typeof updated.toolOutput.product === "string") {
          const exists = PRODUCTS.some((item) => item.value === updated.toolOutput.product);
          if (exists) {
            productSelect.value = updated.toolOutput.product;
          }
        }
      }

      if (updated.widgetState && typeof updated.widgetState === "object" && updated.widgetState !== null) {
        if (typeof updated.widgetState.stateCode === "string") {
          const state = findState(updated.widgetState.stateCode);
          if (state) {
            stateSelect.value = state.code;
          }
        } else if (typeof updated.widgetState.state === "string") {
          const state = findState(updated.widgetState.state) || STATES.find((item) => item.name === updated.widgetState.state);
          if (state) {
            stateSelect.value = state.code;
          }
        }

        if (typeof updated.widgetState.zip === "string") {
          zipInput.value = updated.widgetState.zip;
        }

        if (typeof updated.widgetState.product === "string") {
          const exists = PRODUCTS.some((item) => item.value === updated.widgetState.product);
          if (exists) {
            productSelect.value = updated.widgetState.product;
          }
        }
      }

      updateButtonState();
    });
  })();
</script>
""".strip()
