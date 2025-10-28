"""Quote options intake widget markup for the Python MCP server."""

INSURANCE_QUOTE_OPTIONS_WIDGET_HTML = """
<div id=\"insurance-quote-options-root\"></div>
<style>
  :root {
    color-scheme: light dark;
  }

  #insurance-quote-options-root {
    font-family: "Inter", "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont,
      "Helvetica Neue", Arial, sans-serif;
    color: rgba(15, 23, 42, 0.9);
  }

  @media (prefers-color-scheme: dark) {
    #insurance-quote-options-root {
      color: rgba(226, 232, 240, 0.94);
    }
  }

  .quote-widget {
    background: rgba(255, 255, 255, 0.96);
    border-radius: 20px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 18px;
    box-shadow: 0 18px 48px rgba(15, 23, 42, 0.12);
    max-width: 480px;
  }

  @media (prefers-color-scheme: dark) {
    .quote-widget {
      background: rgba(15, 23, 42, 0.92);
      border-color: rgba(148, 163, 184, 0.24);
      box-shadow: 0 18px 48px rgba(0, 0, 0, 0.45);
    }
  }

  .quote-widget__eyebrow {
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.14em;
    font-weight: 600;
    color: rgba(99, 102, 241, 0.9);
  }

  .quote-widget__title {
    font-size: 20px;
    line-height: 1.3;
    font-weight: 700;
    margin: 0;
  }

  .quote-widget__description {
    margin: 0;
    font-size: 14px;
    line-height: 1.6;
    color: rgba(15, 23, 42, 0.74);
  }

  @media (prefers-color-scheme: dark) {
    .quote-widget__description {
      color: rgba(226, 232, 240, 0.74);
    }
  }

  .quote-widget__form {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .quote-widget__field {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .quote-widget__label {
    font-size: 13px;
    font-weight: 600;
    color: rgba(15, 23, 42, 0.78);
  }

  @media (prefers-color-scheme: dark) {
    .quote-widget__label {
      color: rgba(226, 232, 240, 0.78);
    }
  }

  .quote-widget__input,
  .quote-widget__select,
  .quote-widget__date-input {
    border: 1px solid rgba(15, 23, 42, 0.12);
    border-radius: 12px;
    padding: 10px 14px;
    background: rgba(255, 255, 255, 0.98);
    font-size: 14px;
    color: inherit;
    transition: border 120ms ease, box-shadow 120ms ease;
  }

  .quote-widget__input:focus,
  .quote-widget__select:focus,
  .quote-widget__date-input:focus {
    border-color: rgba(99, 102, 241, 0.65);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.18);
    outline: none;
  }

  @media (prefers-color-scheme: dark) {
    .quote-widget__input,
    .quote-widget__select,
    .quote-widget__date-input {
      background: rgba(15, 23, 42, 0.88);
      border-color: rgba(148, 163, 184, 0.28);
    }

    .quote-widget__input:focus,
    .quote-widget__select:focus,
    .quote-widget__date-input:focus {
      border-color: rgba(129, 140, 248, 0.9);
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.32);
    }
  }

  .quote-widget__hint {
    font-size: 12px;
    color: rgba(71, 85, 105, 0.78);
    margin: 0;
  }

  @media (prefers-color-scheme: dark) {
    .quote-widget__hint {
      color: rgba(148, 163, 184, 0.78);
    }
  }

  .quote-widget__option-row {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    align-items: center;
  }

  .quote-widget__toggle-group {
    display: inline-flex;
    padding: 4px;
    border-radius: 9999px;
    background: rgba(99, 102, 241, 0.08);
    gap: 4px;
  }

  .quote-widget__toggle {
    border: none;
    background: transparent;
    color: rgba(15, 23, 42, 0.7);
    font-size: 12px;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 9999px;
    cursor: pointer;
    transition: background 120ms ease, color 120ms ease;
  }

  .quote-widget__toggle.is-active {
    background: rgba(99, 102, 241, 0.18);
    color: rgba(30, 64, 175, 0.96);
  }

  @media (prefers-color-scheme: dark) {
    .quote-widget__toggle-group {
      background: rgba(129, 140, 248, 0.18);
    }

    .quote-widget__toggle {
      color: rgba(226, 232, 240, 0.8);
    }

    .quote-widget__toggle.is-active {
      background: rgba(99, 102, 241, 0.32);
      color: rgba(224, 231, 255, 0.96);
    }
  }

  .quote-widget__submit {
    border: none;
    border-radius: 12px;
    padding: 14px 18px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    background: rgba(37, 99, 235, 0.92);
    color: #fff;
    box-shadow: 0 14px 34px rgba(37, 99, 235, 0.28);
    transition: transform 120ms ease, box-shadow 120ms ease;
  }

  .quote-widget__submit[aria-disabled="true"] {
    opacity: 0.6;
    cursor: not-allowed;
    box-shadow: none;
  }

  .quote-widget__submit:hover:not([aria-disabled="true"]) {
    transform: translateY(-1px);
    box-shadow: 0 18px 34px rgba(37, 99, 235, 0.32);
  }

  .quote-widget__footer {
    font-size: 12px;
    color: rgba(71, 85, 105, 0.72);
    margin: 0;
  }

  @media (prefers-color-scheme: dark) {
    .quote-widget__footer {
      color: rgba(148, 163, 184, 0.72);
    }
  }

  .quote-widget__status {
    border-radius: 12px;
    background: rgba(22, 163, 74, 0.1);
    color: rgba(22, 101, 52, 0.92);
    padding: 12px 14px;
    font-size: 13px;
    display: none;
  }

  .quote-widget__status.is-visible {
    display: block;
  }

  .quote-widget__status--error {
    background: rgba(220, 38, 38, 0.12);
    color: rgba(185, 28, 28, 0.92);
  }
</style>
<script type=\"module\">
  (function () {
    const root = document.getElementById("insurance-quote-options-root");
    if (!root) return;

    const POLICY_TYPE_OPTIONS = [
      { value: "New Business", label: "New business" },
      { value: "Rewrite", label: "Rewrite" },
      { value: "Endorsement", label: "Endorsement" },
      { value: "Cross Sell", label: "Cross-sell" },
    ];

    const TERM_OPTIONS = [
      { value: "Semi Annual", label: "6-month term" },
      { value: "Annual", label: "12-month term" },
      { value: "Monthly", label: "Month to month" },
    ];

    const PAYMENT_METHOD_OPTIONS = [
      { value: "Paid In Full", label: "Paid in full" },
      { value: "Electronic Funds Transfer", label: "Monthly autopay" },
      { value: "Quarterly", label: "Quarterly" },
      { value: "Agency Bill", label: "Agency bill" },
    ];

    const BUMP_LIMIT_OPTIONS = [
      { value: "No Bumping", label: "No bumping" },
      { value: "Bump Up", label: "Raise to recommended" },
      { value: "Bump Down", label: "Lower if required" },
    ];

    const POLICY_TYPE_CONTRACT_VALUE_MAP = new Map([
      ["NEW_BUSINESS", "New Business"],
      ["REWRITE", "Rewrite"],
      ["ENDORSEMENT", "Endorsement"],
      ["CROSS_SELL", "Cross Sell"],
      ["New Business", "New Business"],
      ["Rewrite", "Rewrite"],
      ["Endorsement", "Endorsement"],
      ["Cross Sell", "Cross Sell"],
    ]);

    const TERM_CONTRACT_VALUE_MAP = new Map([
      ["SIX_MONTHS", "Semi Annual"],
      ["TWELVE_MONTHS", "Annual"],
      ["MONTH_TO_MONTH", "Monthly"],
      ["Semi Annual", "Semi Annual"],
      ["Annual", "Annual"],
      ["Monthly", "Monthly"],
    ]);

    const PAYMENT_METHOD_CONTRACT_VALUE_MAP = new Map([
      ["PAID_IN_FULL", "Paid In Full"],
      ["MONTHLY_AUTOPAY", "Electronic Funds Transfer"],
      ["QUARTERLY", "Quarterly"],
      ["AGENCY_BILL", "Agency Bill"],
      ["Paid In Full", "Paid In Full"],
      ["Electronic Funds Transfer", "Electronic Funds Transfer"],
      ["Quarterly", "Quarterly"],
      ["Agency Bill", "Agency Bill"],
    ]);

    const BUMP_LIMIT_CONTRACT_VALUE_MAP = new Map([
      ["", ""],
      ["NONE", "No Bumping"],
      ["None", "No Bumping"],
      ["no bumping", "No Bumping"],
      ["NO_BUMPING", "No Bumping"],
      ["No Bumping", "No Bumping"],
      ["Bump Up", "Bump Up"],
      ["bump up", "Bump Up"],
      ["BUMP_UP", "Bump Up"],
      ["RAISE_TO_RECOMMENDED", "Bump Up"],
      ["Bump Down", "Bump Down"],
      ["bump down", "Bump Down"],
      ["BUMP_DOWN", "Bump Down"],
      ["MATCH_PREVIOUS", "Bump Down"],
      ["MATCH PRIOR POLICY", "Bump Down"],
      ["Match Prior Policy", "Bump Down"],
    ]);

    const container = document.createElement("div");
    container.className = "quote-widget";

    const eyebrow = document.createElement("span");
    eyebrow.className = "quote-widget__eyebrow";
    eyebrow.textContent = "Personal auto intake";

    const title = document.createElement("h2");
    title.className = "quote-widget__title";
    title.textContent = "Share the quote options";

    const description = document.createElement("p");
    description.className = "quote-widget__description";
    description.textContent =
      "Pick from AIS contract values so the assistant can pass an API-ready payload without extra follow-up.";

    const form = document.createElement("form");
    form.className = "quote-widget__form";
    form.setAttribute("novalidate", "true");

    function createTextField(id, labelText, placeholder) {
      const field = document.createElement("div");
      field.className = "quote-widget__field";

      const label = document.createElement("label");
      label.className = "quote-widget__label";
      label.setAttribute("for", id);
      label.textContent = labelText;

      const input = document.createElement("input");
      input.className = "quote-widget__input";
      input.id = id;
      input.type = "text";
      input.placeholder = placeholder || "";

      field.appendChild(label);
      field.appendChild(input);
      return { field, input };
    }

    function createDateField(id, labelText) {
      const field = document.createElement("div");
      field.className = "quote-widget__field";

      const label = document.createElement("label");
      label.className = "quote-widget__label";
      label.setAttribute("for", id);
      label.textContent = labelText;

      const input = document.createElement("input");
      input.className = "quote-widget__date-input";
      input.id = id;
      input.type = "date";

      const hint = document.createElement("p");
      hint.className = "quote-widget__hint";
      hint.textContent = "Effective dates are captured in YYYY-MM-DD format.";

      field.appendChild(label);
      field.appendChild(input);
      field.appendChild(hint);
      return { field, input };
    }

    function createSelectField(id, labelText, options) {
      const field = document.createElement("div");
      field.className = "quote-widget__field";

      const label = document.createElement("label");
      label.className = "quote-widget__label";
      label.setAttribute("for", id);
      label.textContent = labelText;

      const select = document.createElement("select");
      select.className = "quote-widget__select";
      select.id = id;

      const placeholderOption = document.createElement("option");
      placeholderOption.value = "";
      placeholderOption.textContent = "Select an option";
      select.appendChild(placeholderOption);

      options.forEach((option) => {
        const opt = document.createElement("option");
        opt.value = option.value;
        opt.textContent = option.label;
        select.appendChild(opt);
      });

      field.appendChild(label);
      field.appendChild(select);
      return { field, select };
    }

    const identifierField = createTextField(
      "insurance-quote-identifier",
      "Quote identifier",
      "Generated automatically"
    );
    const identifierHint = document.createElement("p");
    identifierHint.className = "quote-widget__hint";
    identifierHint.textContent =
      "Generated automatically when the assistant collects quote options.";
    identifierField.field.appendChild(identifierHint);
    identifierField.input.readOnly = true;
    identifierField.input.setAttribute("aria-readonly", "true");
    const effectiveDateField = createDateField(
      "insurance-quote-effective-date",
      "Effective date"
    );
    const policyTypeField = createSelectField(
      "insurance-quote-policy-type",
      "Policy type",
      POLICY_TYPE_OPTIONS
    );
    const termField = createSelectField(
      "insurance-quote-term",
      "Policy term",
      TERM_OPTIONS
    );
    const paymentMethodField = createSelectField(
      "insurance-quote-payment-method",
      "Payment method",
      PAYMENT_METHOD_OPTIONS
    );
    const bumpLimitsField = createSelectField(
      "insurance-quote-bump-limits",
      "Bump limits preference",
      BUMP_LIMIT_OPTIONS
    );

    const declinedCreditField = document.createElement("div");
    declinedCreditField.className = "quote-widget__field";
    const declinedLabel = document.createElement("span");
    declinedLabel.className = "quote-widget__label";
    declinedLabel.textContent = "Has the customer declined credit scoring?";
    const toggleGroup = document.createElement("div");
    toggleGroup.className = "quote-widget__toggle-group";

    const declinedOptions = [
      { value: "yes", label: "Yes" },
      { value: "no", label: "No" },
      { value: "unknown", label: "Not sure" },
    ];

    const toggleButtons = declinedOptions.map((option) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "quote-widget__toggle";
      button.setAttribute("data-value", option.value);
      button.textContent = option.label;
      toggleGroup.appendChild(button);
      return button;
    });

    declinedCreditField.appendChild(declinedLabel);
    declinedCreditField.appendChild(toggleGroup);

    const status = document.createElement("div");
    status.className = "quote-widget__status";

    const submit = document.createElement("button");
    submit.type = "submit";
    submit.className = "quote-widget__submit";
    submit.textContent = "Share quote options with the assistant";
    submit.setAttribute("aria-disabled", "true");
    submit.disabled = true;

    const footer = document.createElement("p");
    footer.className = "quote-widget__footer";
    footer.textContent =
      "The assistant converts these selections into the JSON payload required by AIS rating APIs.";

    [
      identifierField.field,
      effectiveDateField.field,
      policyTypeField.field,
      termField.field,
      paymentMethodField.field,
      bumpLimitsField.field,
      declinedCreditField,
    ].forEach((element) => form.appendChild(element));

    form.appendChild(status);
    form.appendChild(submit);

    container.appendChild(eyebrow);
    container.appendChild(title);
    container.appendChild(description);
    container.appendChild(form);
    container.appendChild(footer);

    root.appendChild(container);

    const state = {
      identifier: "",
      effectiveDate: "",
      policyType: "",
      term: "",
      paymentMethod: "",
      bumpLimits: "",
      customerDeclinedCredit: null,
    };

    function normalizeToContractValue(value, map) {
      if (value == null) {
        return "";
      }
      if (typeof value !== "string") {
        return value;
      }
      const trimmed = value.trim();
      if (!trimmed) {
        return "";
      }
      return map.get(trimmed) ?? trimmed;
    }

    function normalizeStatePartial(partial) {
      const normalized = { ...partial };
      if (Object.prototype.hasOwnProperty.call(partial, "policyType")) {
        normalized.policyType = normalizeToContractValue(
          partial.policyType,
          POLICY_TYPE_CONTRACT_VALUE_MAP
        );
      }
      if (Object.prototype.hasOwnProperty.call(partial, "term")) {
        normalized.term = normalizeToContractValue(
          partial.term,
          TERM_CONTRACT_VALUE_MAP
        );
      }
      if (Object.prototype.hasOwnProperty.call(partial, "paymentMethod")) {
        normalized.paymentMethod = normalizeToContractValue(
          partial.paymentMethod,
          PAYMENT_METHOD_CONTRACT_VALUE_MAP
        );
      }
      if (Object.prototype.hasOwnProperty.call(partial, "bumpLimits")) {
        normalized.bumpLimits = normalizeToContractValue(
          partial.bumpLimits,
          BUMP_LIMIT_CONTRACT_VALUE_MAP
        );
      }
      return normalized;
    }

    function normalizeStateSnapshot(snapshot) {
      return {
        ...snapshot,
        ...normalizeStatePartial({
          policyType: snapshot.policyType,
          term: snapshot.term,
          paymentMethod: snapshot.paymentMethod,
          bumpLimits: snapshot.bumpLimits,
        }),
      };
    }

    let isSubmitting = false;

    function setStatus(message, type) {
      if (!message) {
        status.textContent = "";
        status.classList.remove("is-visible", "quote-widget__status--error");
        return;
      }
      status.textContent = message;
      status.classList.add("is-visible");
      if (type === "error") {
        status.classList.add("quote-widget__status--error");
      } else {
        status.classList.remove("quote-widget__status--error");
      }
    }

    function persistState() {
      if (!window.openai || typeof window.openai.setWidgetState !== "function") {
        return;
      }
      const normalized = normalizeStateSnapshot(state);
      if (!normalized.identifier) {
        return;
      }
      const payload = {
        Identifier: normalized.identifier || undefined,
        EffectiveDate: normalized.effectiveDate || undefined,
        PolicyType: normalized.policyType || undefined,
        Term: normalized.term || undefined,
        PaymentMethod: normalized.paymentMethod || undefined,
        BumpLimits: normalized.bumpLimits || undefined,
        CustomerDeclinedCredit: state.customerDeclinedCredit,
      };
      try {
        void window.openai.setWidgetState(payload);
      } catch (error) {
        console.warn("Failed to persist widget state", error);
      }
    }

    function updateSubmitState() {
      const requiredFilled =
        state.identifier.trim().length > 0 && state.effectiveDate.trim().length > 0;
      if (requiredFilled) {
        submit.disabled = false;
        submit.setAttribute("aria-disabled", "false");
      } else {
        submit.disabled = true;
        submit.setAttribute("aria-disabled", "true");
      }
    }

    function setState(partial) {
      Object.assign(state, normalizeStatePartial(partial));
      updateSubmitState();
      persistState();
    }

    function attachInputListener(input, key, transform) {
      input.addEventListener("input", () => {
        const value = transform ? transform(input.value) : input.value;
        setState({ [key]: value });
      });
    }

    effectiveDateField.input.addEventListener("change", () => {
      setState({ effectiveDate: effectiveDateField.input.value });
    });

    policyTypeField.select.addEventListener("change", () => {
      setState({ policyType: policyTypeField.select.value });
    });

    termField.select.addEventListener("change", () => {
      setState({ term: termField.select.value });
    });

    paymentMethodField.select.addEventListener("change", () => {
      setState({ paymentMethod: paymentMethodField.select.value });
    });

    bumpLimitsField.select.addEventListener("change", () => {
      setState({ bumpLimits: bumpLimitsField.select.value });
    });

    toggleButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const value = button.getAttribute("data-value");
        toggleButtons.forEach((btn) => btn.classList.remove("is-active"));
        button.classList.add("is-active");
        if (value === "yes") {
          setState({ customerDeclinedCredit: true });
        } else if (value === "no") {
          setState({ customerDeclinedCredit: false });
        } else {
          setState({ customerDeclinedCredit: null });
        }
      });
    });

    function resolveOptionLabel(options, value) {
      const option = options.find((opt) => opt.value === value);
      return option ? option.label : null;
    }

    function buildToolArguments() {
      const normalized = normalizeStateSnapshot(state);
      const payload = {
        Identifier: normalized.identifier.trim(),
        EffectiveDate: normalized.effectiveDate,
      };
      if (normalized.policyType) payload.PolicyType = normalized.policyType;
      if (normalized.term) payload.Term = normalized.term;
      if (normalized.paymentMethod)
        payload.PaymentMethod = normalized.paymentMethod;
      if (normalized.bumpLimits) payload.BumpLimits = normalized.bumpLimits;
      if (state.customerDeclinedCredit !== null) {
        payload.CustomerDeclinedCredit = state.customerDeclinedCredit;
      }
      return payload;
    }

    async function sendSummaryMessage(payload) {
      if (!window.openai || typeof window.openai.sendFollowUpMessage !== "function") {
        return;
      }
      const policyTypeLabel = resolveOptionLabel(POLICY_TYPE_OPTIONS, payload.PolicyType);
      const termLabel = resolveOptionLabel(TERM_OPTIONS, payload.Term);
      const paymentLabel = resolveOptionLabel(PAYMENT_METHOD_OPTIONS, payload.PaymentMethod);

      const pieces = [
        `Quote ID ${payload.Identifier} effective ${payload.EffectiveDate}`,
      ];
      if (policyTypeLabel) pieces.push(`policy type ${policyTypeLabel.toLowerCase()}`);
      if (termLabel) pieces.push(termLabel.toLowerCase());
      if (paymentLabel) pieces.push(`payment method ${paymentLabel.toLowerCase()}`);
      if (payload.CustomerDeclinedCredit === true) {
        pieces.push("customer declined credit scoring");
      } else if (payload.CustomerDeclinedCredit === false) {
        pieces.push("customer approved credit scoring");
      }
      if (payload.BumpLimits) {
        const bumpLabel = resolveOptionLabel(BUMP_LIMIT_OPTIONS, payload.BumpLimits);
        if (bumpLabel) {
          pieces.push(`bump limits preference ${bumpLabel.toLowerCase()}`);
        }
      }

      const prompt = `Here are the quote options: ${pieces.join(", ")}.`;
      try {
        await window.openai.sendFollowUpMessage({ prompt });
      } catch (error) {
        console.warn("Failed to send follow-up message", error);
      }
    }

    async function submitForm(event) {
      event.preventDefault();
      if (isSubmitting || submit.disabled) return;

      const payload = buildToolArguments();
      if (!window.openai || typeof window.openai.callTool !== "function") {
        setStatus("Unable to call the tool from this client.", "error");
        return;
      }

      isSubmitting = true;
      submit.disabled = true;
      submit.setAttribute("aria-disabled", "true");
      submit.textContent = "Sharing with the assistant…";
      setStatus("", null);

      try {
        await window.openai.callTool("collect-personal-auto-quote-options", payload);
        await sendSummaryMessage(payload);
        setStatus("Shared quote options with the assistant.", "success");
      } catch (error) {
        console.warn("Failed to call tool", error);
        setStatus("There was a problem sending the quote options. Please try again.", "error");
      } finally {
        isSubmitting = false;
        submit.textContent = "Share quote options with the assistant";
        updateSubmitState();
      }
    }

    form.addEventListener("submit", submitForm);

    function applyStateToInputs(current) {
      const normalized = normalizeStateSnapshot(current);
      if (current === state) {
        Object.assign(state, normalized);
      }
      identifierField.input.value = normalized.identifier || "";
      effectiveDateField.input.value = normalized.effectiveDate || "";
      policyTypeField.select.value = normalized.policyType || "";
      termField.select.value = normalized.term || "";
      paymentMethodField.select.value = normalized.paymentMethod || "";
      bumpLimitsField.select.value = normalized.bumpLimits || "";
      toggleButtons.forEach((button) => {
        const value = button.getAttribute("data-value");
        const isActive =
          (value === "yes" && current.customerDeclinedCredit === true) ||
          (value === "no" && current.customerDeclinedCredit === false) ||
          (value === "unknown" && current.customerDeclinedCredit === null);
        button.classList.toggle("is-active", isActive);
      });
    }

    function hydrateStateFromGlobals(globals) {
      if (!globals || typeof globals !== "object") return;
      const toolOutput =
        globals.toolOutput && typeof globals.toolOutput === "object"
          ? globals.toolOutput
          : null;
      const widgetState =
        globals.widgetState && typeof globals.widgetState === "object"
          ? globals.widgetState
          : null;

      const source = toolOutput || widgetState;
      if (!source) return;

      const nextState = { ...state };
      if (typeof source.Identifier === "string") {
        nextState.identifier = source.Identifier;
      }
      if (typeof source.EffectiveDate === "string") {
        nextState.effectiveDate = source.EffectiveDate;
      }
      if (typeof source.PolicyType === "string") {
        nextState.policyType = source.PolicyType;
      }
      if (typeof source.Term === "string") {
        nextState.term = source.Term;
      }
      if (typeof source.PaymentMethod === "string") {
        nextState.paymentMethod = source.PaymentMethod;
      }
      if (typeof source.BumpLimits === "string") {
        nextState.bumpLimits = source.BumpLimits;
      }
      if (typeof source.CustomerDeclinedCredit === "boolean") {
        nextState.customerDeclinedCredit = source.CustomerDeclinedCredit;
      } else if (source.CustomerDeclinedCredit == null) {
        nextState.customerDeclinedCredit = null;
      }

      const normalizedNextState = normalizeStateSnapshot(nextState);
      Object.assign(state, normalizedNextState);
      applyStateToInputs(state);
      updateSubmitState();
      persistState();
    }

    hydrateStateFromGlobals(window.openai ?? {});

    window.addEventListener("openai:set_globals", (event) => {
      const detail = event.detail;
      if (!detail || !detail.globals) return;
      hydrateStateFromGlobals(detail.globals);
    });

    updateSubmitState();
    persistState();
  })();
</script>
""".strip()
