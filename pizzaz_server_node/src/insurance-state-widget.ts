export const INSURANCE_STATE_WIDGET_HTML = String.raw`
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

  .insurance-widget__results {
    margin-top: 24px;
    padding: 16px;
    border-radius: 16px;
    background: rgba(15, 23, 42, 0.04);
    border: 1px solid rgba(15, 23, 42, 0.08);
  }

  .insurance-widget__results-message {
    margin: 0;
    font-size: 14px;
    color: rgba(15, 23, 42, 0.8);
  }

  .insurance-widget__products-heading {
    margin: 16px 0 8px;
    font-size: 14px;
    font-weight: 600;
    color: rgba(15, 23, 42, 0.9);
  }

  .insurance-widget__products {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .insurance-widget__product {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    border-radius: 999px;
    background: rgba(59, 130, 246, 0.12);
    color: rgba(37, 99, 235, 0.95);
    font-size: 13px;
    font-weight: 600;
  }

  .insurance-widget__product small {
    display: block;
    font-size: 11px;
    font-weight: 500;
    color: rgba(37, 99, 235, 0.75);
  }

  .insurance-widget__footnote {
    margin: 0;
    font-size: 12px;
    color: rgba(15, 23, 42, 0.5);
  }

  .insurance-widget__empty {
    padding: 16px 12px;
    font-size: 13px;
    text-align: center;
    color: rgba(15, 23, 42, 0.55);
  }

  @media (prefers-color-scheme: dark) {
    .insurance-widget__results {
      background: rgba(148, 163, 184, 0.12);
      border-color: rgba(148, 163, 184, 0.24);
    }

    .insurance-widget__results-message {
      color: rgba(226, 232, 240, 0.85);
    }

    .insurance-widget__products-heading {
      color: rgba(226, 232, 240, 0.9);
    }

    .insurance-widget__product {
      background: rgba(37, 99, 235, 0.2);
      color: rgba(191, 219, 254, 0.95);
    }

    .insurance-widget__product small {
      color: rgba(191, 219, 254, 0.8);
    }

    .insurance-widget__footnote {
      color: rgba(148, 163, 184, 0.65);
    }

    .insurance-widget__empty {
      color: rgba(226, 232, 240, 0.6);
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
    ].map((state) => ({
      ...state,
      nameLower: state.name.toLowerCase(),
      codeLower: state.code.toLowerCase(),
    }));

    const container = document.createElement("div");
    container.className = "insurance-widget";

    const eyebrow = document.createElement("span");
    eyebrow.className = "insurance-widget__eyebrow";
    eyebrow.textContent = "Insurance quote";

    const title = document.createElement("h2");
    title.className = "insurance-widget__title";
    title.textContent = "Where should we quote coverage?";

    const description = document.createElement("p");
    description.className = "insurance-widget__description";
    description.textContent =
      "Insurance availability and pricing vary by state. Tell us where you live so we can pull the right plans.";

    const searchBlock = document.createElement("div");
    searchBlock.className = "insurance-widget__search";

    const label = document.createElement("label");
    label.className = "insurance-widget__label";
    label.setAttribute("for", "insurance-state-search");
    label.textContent = "Search for your state";

    const inputWrapper = document.createElement("div");
    inputWrapper.className = "insurance-widget__input";

    const input = document.createElement("input");
    input.id = "insurance-state-search";
    input.setAttribute("placeholder", "Type a state name or abbreviation");
    input.setAttribute("autocomplete", "off");
    input.setAttribute("aria-controls", "insurance-state-options");
    inputWrapper.appendChild(input);

    const options = document.createElement("div");
    options.id = "insurance-state-options";
    options.className = "insurance-widget__options";
    options.setAttribute("role", "listbox");
    options.setAttribute("aria-label", "State options");

    const selection = document.createElement("div");
    selection.className = "insurance-widget__selection";

    const results = document.createElement("div");
    results.className = "insurance-widget__results";
    results.setAttribute("role", "status");
    const resultsMessage = document.createElement("p");
    resultsMessage.className = "insurance-widget__results-message";
    resultsMessage.textContent = "Choose your state to see available insurance products.";
    const productsHeading = document.createElement("h3");
    productsHeading.className = "insurance-widget__products-heading";
    productsHeading.textContent = "What kind of insurance are you looking for?";
    productsHeading.hidden = true;
    const productList = document.createElement("div");
    productList.className = "insurance-widget__products";
    productList.hidden = true;
    results.appendChild(resultsMessage);
    results.appendChild(productsHeading);
    results.appendChild(productList);

    const confirm = document.createElement("button");
    confirm.type = "button";
    confirm.className = "insurance-widget__confirm";
    confirm.textContent = "Share state with the assistant";
    confirm.setAttribute("aria-disabled", "true");
    confirm.disabled = true;

    const footnote = document.createElement("p");
    footnote.className = "insurance-widget__footnote";
    footnote.textContent =
      "We’ll tailor the follow-up questions once we know your location.";

    searchBlock.appendChild(label);
    searchBlock.appendChild(inputWrapper);

    container.appendChild(eyebrow);
    container.appendChild(title);
    container.appendChild(description);
    container.appendChild(searchBlock);
    container.appendChild(options);
    container.appendChild(selection);
    container.appendChild(results);
    container.appendChild(confirm);
    container.appendChild(footnote);

    root.appendChild(container);

    let selectedCode = null;
    let isSending = false;
    const productCache = new Map();
    let currentRequestId = 0;

    function getStateByCode(code) {
      if (!code) return null;
      return STATES.find((state) => state.code === code.toUpperCase()) ?? null;
    }

    function updateSelectionDisplay(code) {
      const state = getStateByCode(code);
      selectedCode = state ? state.code : null;
      if (state) {
        selection.textContent =
          "Selected state: " + state.name + " (" + state.code + ")";
        confirm.disabled = false;
        confirm.setAttribute("aria-disabled", "false");
      } else {
        selection.textContent = "No state selected yet.";
        confirm.disabled = true;
        confirm.setAttribute("aria-disabled", "true");
      }

      Array.from(options.querySelectorAll("[data-state-code]"))
        .forEach((button) => {
          const codeAttr = button.getAttribute("data-state-code");
          const isSelected = codeAttr === selectedCode;
          button.classList.toggle("is-selected", isSelected);
          button.setAttribute("aria-selected", isSelected ? "true" : "false");
        });

      if (state) {
        loadProductsForState(state.code, state.name);
      } else {
        resultsMessage.textContent = "Choose your state to see available insurance products.";
        productsHeading.hidden = true;
        productList.hidden = true;
        productList.innerHTML = "";
      }
    }

    function pushWidgetState(code) {
      if (!window.openai || typeof window.openai.setWidgetState !== "function") {
        return;
      }
      if (!code) return;
      try {
        void window.openai.setWidgetState({ state: code });
      } catch (error) {
        console.warn("Failed to persist widget state", error);
      }
    }

    function requestProducts(stateCode) {
      const cached = productCache.get(stateCode);
      if (cached) {
        return Promise.resolve(cached);
      }

      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.withCredentials = true;

        xhr.addEventListener("readystatechange", function () {
          if (this.readyState === this.DONE) {
            if (this.status === 200) {
              try {
                const parsed = JSON.parse(this.responseText || "[]");
                const payload = { status: 200, products: parsed };
                productCache.set(stateCode, payload);
                resolve(payload);
              } catch (error) {
                reject(error);
              }
            } else if (this.status === 404) {
              const notFound = { status: 404, products: [] };
              productCache.set(stateCode, notFound);
              resolve(notFound);
            } else {
              reject(new Error("Request failed with status " + this.status));
            }
          }
        });

        xhr.addEventListener("error", () => {
          reject(new Error("Network error while fetching products"));
        });

        xhr.open(
          "GET",
          "https://gateway.pre.zrater.io/api/v1/linesOfBusiness/personalAuto/states/" +
            encodeURIComponent(stateCode) +
            "/activeProducts"
        );
        xhr.setRequestHeader("cookie", "BCSI-CS-7883f85839ae9af9=1");
        xhr.setRequestHeader("User-Agent", "insomnia/11.1.0");
        xhr.setRequestHeader("x-api-key", "e57528b0-95b4-4efe-8870-caa0f8a95143");

        xhr.send(null);
      });
    }

    function renderProducts(products) {
      productList.innerHTML = "";

      if (!products.length) {
        productsHeading.hidden = true;
        productList.hidden = true;
        return;
      }

      productsHeading.hidden = false;
      productList.hidden = false;

      products.forEach((product) => {
        const pill = document.createElement("div");
        pill.className = "insurance-widget__product";
        const name = document.createElement("span");
        name.textContent = product.productName || "Unnamed product";
        const carrier = document.createElement("small");
        carrier.textContent = product.carrierName || "";
        pill.appendChild(name);
        if (carrier.textContent) {
          pill.appendChild(carrier);
        }
        productList.appendChild(pill);
      });
    }

    function loadProductsForState(stateCode, stateName) {
      const requestId = ++currentRequestId;
      resultsMessage.textContent = "Checking available coverage in " + stateName + "…";
      productsHeading.hidden = true;
      productList.hidden = true;
      productList.innerHTML = "";

      requestProducts(stateCode)
        .then((result) => {
          if (requestId !== currentRequestId) {
            return;
          }

          if (result.status === 200 && result.products.length) {
            resultsMessage.textContent =
              "Great! Here are the active products we can explore in " + stateName + ".";
            renderProducts(result.products);
          } else if (result.status === 404 || !result.products.length) {
            resultsMessage.textContent =
              "We couldn't find any active products in " +
              stateName +
              ". Try another state or ask the assistant for help.";
            renderProducts([]);
          }
        })
        .catch((error) => {
          if (requestId !== currentRequestId) {
            return;
          }
          console.warn("Failed to fetch products", error);
          resultsMessage.textContent =
            "We ran into an issue checking products. Please try again or pick a different state.";
          productsHeading.hidden = true;
          productList.hidden = true;
          productList.innerHTML = "";
        });
    }

    function renderOptions() {
      const term = input.value.trim().toLowerCase();
      const matches = term
        ? STATES.filter(
            (state) =>
              state.nameLower.includes(term) || state.codeLower.includes(term)
          )
        : STATES;

      options.innerHTML = "";

      if (!matches.length) {
        const empty = document.createElement("div");
        empty.className = "insurance-widget__empty";
        empty.textContent = "No states match your search.";
        options.appendChild(empty);
        return;
      }

      matches.forEach((state) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "insurance-widget__option";
        button.setAttribute("data-state-code", state.code);
        button.setAttribute("role", "option");
        button.setAttribute(
          "aria-selected",
          state.code === selectedCode ? "true" : "false"
        );

        const nameSpan = document.createElement("span");
        nameSpan.textContent = state.name;

        const codeSpan = document.createElement("span");
        codeSpan.className = "insurance-widget__option-code";
        codeSpan.textContent = state.code;

        button.appendChild(nameSpan);
        button.appendChild(codeSpan);

        button.addEventListener("click", () => {
          updateSelectionDisplay(state.code);
          pushWidgetState(state.code);
          input.focus();
        });

        options.appendChild(button);
      });
    }

    function sendSelectionToAssistant(code) {
      if (!window.openai || typeof window.openai.sendFollowUpMessage !== "function") {
        return Promise.resolve();
      }
      const state = getStateByCode(code);
      if (!state) return Promise.resolve();
      const prompt =
        "My state for insurance purposes is " +
        state.name +
        " (" +
        state.code +
        ").";
      return window.openai.sendFollowUpMessage({ prompt });
    }

    confirm.addEventListener("click", async () => {
      if (!selectedCode || isSending) return;
      isSending = true;
      confirm.textContent = "Sending to assistant…";
      confirm.setAttribute("aria-disabled", "true");
      confirm.disabled = true;

      try {
        pushWidgetState(selectedCode);
        await sendSelectionToAssistant(selectedCode);
      } catch (error) {
        console.warn("Failed to share state with assistant", error);
      } finally {
        isSending = false;
        confirm.textContent = "Share state with the assistant";
        updateSelectionDisplay(selectedCode);
      }
    });

    input.addEventListener("input", () => {
      renderOptions();
    });

    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        const topMatch = options.querySelector("[data-state-code]");
        if (topMatch) {
          topMatch.click();
          event.preventDefault();
        }
      }
    });

    const initialFromState = (() => {
      const globals = window.openai ?? {};
      const widgetState =
        globals.widgetState && typeof globals.widgetState === "object"
          ? globals.widgetState
          : null;
      const toolOutput =
        globals.toolOutput && typeof globals.toolOutput === "object"
          ? globals.toolOutput
          : null;
      const stateValue =
        (toolOutput && typeof toolOutput.state === "string"
          ? toolOutput.state
          : null) ||
        (widgetState && typeof widgetState.state === "string"
          ? widgetState.state
          : null);
      return typeof stateValue === "string" ? stateValue : null;
    })();

    renderOptions();
    updateSelectionDisplay(initialFromState);

    if (initialFromState) {
      pushWidgetState(initialFromState);
    }

    window.addEventListener("openai:set_globals", (event) => {
      const detail = event.detail;
      if (!detail || !detail.globals) return;
      const globals = detail.globals;
      const maybeState = (() => {
        if (
          globals.toolOutput &&
          typeof globals.toolOutput === "object" &&
          globals.toolOutput !== null &&
          typeof globals.toolOutput.state === "string"
        ) {
          return globals.toolOutput.state;
        }
        if (
          globals.widgetState &&
          typeof globals.widgetState === "object" &&
          globals.widgetState !== null &&
          typeof globals.widgetState.state === "string"
        ) {
          return globals.widgetState.state;
        }
        return null;
      })();

      if (typeof maybeState === "string" && maybeState !== selectedCode) {
        updateSelectionDisplay(maybeState);
      }
    });
  })();
</script>
`;
