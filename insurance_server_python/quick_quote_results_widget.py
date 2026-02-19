"""Quick quote results display widget markup for the Python MCP server."""

QUICK_QUOTE_RESULTS_WIDGET_HTML = """
<div id="quick-quote-results-root"></div>
<style>
  :root {
    color-scheme: light dark;
  }

  #quick-quote-results-root {
    font-family: "Inter", "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont,
      "Helvetica Neue", Arial, sans-serif;
    color: rgba(15, 23, 42, 0.94);
    line-height: 1.6;
  }

  @media (prefers-color-scheme: dark) {
    #quick-quote-results-root {
      color: rgba(226, 232, 240, 0.96);
    }
  }

  .quick-quote {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(59, 130, 246, 0.05) 100%);
    border-radius: 24px;
    border: 1px solid rgba(99, 102, 241, 0.2);
    padding: 32px;
    box-shadow: 0 20px 48px rgba(99, 102, 241, 0.12);
    display: flex;
    flex-direction: column;
    gap: 28px;
    max-width: 720px;
  }

  @media (prefers-color-scheme: dark) {
    .quick-quote {
      background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(59, 130, 246, 0.1) 100%);
      border-color: rgba(129, 140, 248, 0.3);
      box-shadow: 0 24px 56px rgba(2, 6, 23, 0.7);
    }
  }

  .quick-quote__header {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .quick-quote__eyebrow {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(99, 102, 241, 0.9);
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .quick-quote__eyebrow::before {
    content: "⚡";
    font-size: 16px;
  }

  .quick-quote__title {
    margin: 0;
    font-size: 28px;
    line-height: 1.2;
    font-weight: 800;
    color: rgba(15, 23, 42, 0.95);
  }

  @media (prefers-color-scheme: dark) {
    .quick-quote__title {
      color: rgba(226, 232, 240, 0.98);
    }
  }

  .quick-quote__location {
    font-size: 16px;
    color: rgba(15, 23, 42, 0.7);
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .quick-quote__location::before {
    content: "📍";
    font-size: 14px;
  }

  @media (prefers-color-scheme: dark) {
    .quick-quote__location {
      color: rgba(226, 232, 240, 0.75);
    }
  }

  .quick-quote__ranges {
    display: grid;
    gap: 20px;
  }

  @media (min-width: 640px) {
    .quick-quote__ranges {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  .range-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 18px;
    border: 1.5px solid rgba(15, 23, 42, 0.08);
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .range-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(15, 23, 42, 0.12);
  }

  @media (prefers-color-scheme: dark) {
    .range-card {
      background: rgba(30, 41, 59, 0.85);
      border-color: rgba(148, 163, 184, 0.25);
    }
  }

  .range-card--best {
    border-color: rgba(16, 185, 129, 0.3);
  }

  .range-card--worst {
    border-color: rgba(251, 146, 60, 0.3);
  }

  .range-card__label {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(15, 23, 42, 0.65);
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .range-card--best .range-card__label {
    color: rgba(4, 120, 87, 0.9);
  }

  .range-card--worst .range-card__label {
    color: rgba(194, 65, 12, 0.9);
  }

  .range-card__label::before {
    font-size: 16px;
  }

  .range-card--best .range-card__label::before {
    content: "✨";
  }

  .range-card--worst .range-card__label::before {
    content: "⚠️";
  }

  .range-card__description {
    font-size: 13px;
    color: rgba(15, 23, 42, 0.6);
    line-height: 1.5;
  }

  @media (prefers-color-scheme: dark) {
    .range-card__description {
      color: rgba(226, 232, 240, 0.68);
    }
  }

  .range-card__price {
    margin: 4px 0;
    font-size: 32px;
    font-weight: 800;
    color: rgba(15, 23, 42, 0.95);
    line-height: 1.1;
  }

  @media (prefers-color-scheme: dark) {
    .range-card__price {
      color: rgba(226, 232, 240, 0.98);
    }
  }

  .range-card__period {
    font-size: 14px;
    font-weight: 600;
    color: rgba(15, 23, 42, 0.55);
  }

  @media (prefers-color-scheme: dark) {
    .range-card__period {
      color: rgba(226, 232, 240, 0.62);
    }
  }

  .range-card__monthly {
    font-size: 15px;
    color: rgba(15, 23, 42, 0.7);
    padding-top: 8px;
    border-top: 1px solid rgba(15, 23, 42, 0.08);
  }

  @media (prefers-color-scheme: dark) {
    .range-card__monthly {
      color: rgba(226, 232, 240, 0.75);
      border-top-color: rgba(148, 163, 184, 0.2);
    }
  }

  .quick-quote__disclaimer {
    background: rgba(241, 245, 249, 0.9);
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.22);
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  @media (prefers-color-scheme: dark) {
    .quick-quote__disclaimer {
      background: rgba(15, 23, 42, 0.6);
      border-color: rgba(148, 163, 184, 0.3);
    }
  }

  .disclaimer__title {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: rgba(15, 23, 42, 0.7);
  }

  @media (prefers-color-scheme: dark) {
    .disclaimer__title {
      color: rgba(226, 232, 240, 0.75);
    }
  }

  .disclaimer__text {
    font-size: 14px;
    color: rgba(15, 23, 42, 0.68);
    line-height: 1.6;
  }

  @media (prefers-color-scheme: dark) {
    .disclaimer__text {
      color: rgba(226, 232, 240, 0.72);
    }
  }

  .disclaimer__factors {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 4px;
  }

  .factor-chip {
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(99, 102, 241, 0.12);
    color: rgba(79, 70, 229, 0.92);
    font-size: 13px;
    font-weight: 600;
  }

  @media (prefers-color-scheme: dark) {
    .factor-chip {
      background: rgba(129, 140, 248, 0.2);
      color: rgba(199, 210, 254, 0.94);
    }
  }

  .quick-quote__cta {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.95) 0%, rgba(79, 70, 229, 0.95) 100%);
    border-radius: 16px;
    padding: 20px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    border: none;
    cursor: pointer;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .quick-quote__cta:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 40px rgba(99, 102, 241, 0.3);
  }

  .cta__text {
    display: flex;
    flex-direction: column;
    gap: 4px;
    text-align: left;
  }

  .cta__title {
    font-size: 17px;
    font-weight: 700;
    color: white;
  }

  .cta__subtitle {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.85);
  }

  .cta__arrow {
    font-size: 28px;
    color: white;
    line-height: 1;
  }

  .placeholder-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(251, 191, 36, 0.16);
    color: rgba(180, 83, 9, 0.92);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  .placeholder-badge::before {
    content: "ℹ️";
    font-size: 14px;
  }

  @media (prefers-color-scheme: dark) {
    .placeholder-badge {
      background: rgba(251, 191, 36, 0.22);
      color: rgba(254, 243, 199, 0.94);
    }
  }
</style>
<script>
  (() => {
    if (typeof document === "undefined") return;

    const root = document.getElementById("quick-quote-results-root");
    if (!root) return;

    const currencyFormatter = new Intl.NumberFormat(undefined, {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    });

    function formatCurrency(value) {
      if (value === null || value === undefined) return "--";
      try {
        return currencyFormatter.format(value);
      } catch {
        return `$${value}`;
      }
    }

    function createWidget(data) {
      if (!data) {
        console.error("Quick quote widget: No data provided");
        return null;
      }

      // Validate required fields
      if (!data.zip_code || !data.city || !data.state || !data.number_of_drivers) {
        console.error("Quick quote widget: Missing required fields", data);
        return null;
      }

      if (!data.best_case_range || !data.worst_case_range) {
        console.error("Quick quote widget: Missing range data", data);
        return null;
      }

      const {
        zip_code,
        city,
        state,
        number_of_drivers,
        best_case_range,
        worst_case_range,
        is_placeholder
      } = data;

      console.log("Quick quote widget: Rendering with data", { zip_code, city, state, number_of_drivers });

      const widget = document.createElement("div");
      widget.className = "quick-quote";

      // Header
      const header = document.createElement("div");
      header.className = "quick-quote__header";

      const eyebrow = document.createElement("div");
      eyebrow.className = "quick-quote__eyebrow";
      eyebrow.textContent = "Instant Quote Estimate";
      header.appendChild(eyebrow);

      const title = document.createElement("h1");
      title.className = "quick-quote__title";
      title.textContent = `${number_of_drivers} Driver${number_of_drivers > 1 ? "s" : ""} in ${city}`;
      header.appendChild(title);

      const location = document.createElement("div");
      location.className = "quick-quote__location";
      location.textContent = `${city}, ${state} ${zip_code}`;
      header.appendChild(location);

      if (is_placeholder) {
        const badge = document.createElement("div");
        badge.className = "placeholder-badge";
        badge.textContent = "Estimated Range";
        header.appendChild(badge);
      }

      widget.appendChild(header);

      // Ranges
      const ranges = document.createElement("div");
      ranges.className = "quick-quote__ranges";

      // Best case card
      const bestCard = document.createElement("div");
      bestCard.className = "range-card range-card--best";

      const bestLabel = document.createElement("div");
      bestLabel.className = "range-card__label";
      bestLabel.textContent = "Best Case Scenario";
      bestCard.appendChild(bestLabel);

      const bestDesc = document.createElement("div");
      bestDesc.className = "range-card__description";
      bestDesc.textContent = "Experienced drivers, clean records, reliable vehicles";
      bestCard.appendChild(bestDesc);

      const bestPrice = document.createElement("div");
      bestPrice.className = "range-card__price";
      bestPrice.textContent = `${formatCurrency(best_case_range.min)} – ${formatCurrency(best_case_range.max)}`;
      bestCard.appendChild(bestPrice);

      const bestPeriod = document.createElement("div");
      bestPeriod.className = "range-card__period";
      bestPeriod.textContent = "per 6 months";
      bestCard.appendChild(bestPeriod);

      const bestMonthly = document.createElement("div");
      bestMonthly.className = "range-card__monthly";
      bestMonthly.textContent = `≈ ${formatCurrency(best_case_range.per_month_min)} – ${formatCurrency(best_case_range.per_month_max)} / month`;
      bestCard.appendChild(bestMonthly);

      ranges.appendChild(bestCard);

      // Worst case card
      const worstCard = document.createElement("div");
      worstCard.className = "range-card range-card--worst";

      const worstLabel = document.createElement("div");
      worstLabel.className = "range-card__label";
      worstLabel.textContent = "Higher-Risk Scenario";
      worstCard.appendChild(worstLabel);

      const worstDesc = document.createElement("div");
      worstDesc.className = "range-card__description";
      worstDesc.textContent = "Young drivers, newer vehicles, limited history";
      worstCard.appendChild(worstDesc);

      const worstPrice = document.createElement("div");
      worstPrice.className = "range-card__price";
      worstPrice.textContent = `${formatCurrency(worst_case_range.min)} – ${formatCurrency(worst_case_range.max)}`;
      worstCard.appendChild(worstPrice);

      const worstPeriod = document.createElement("div");
      worstPeriod.className = "range-card__period";
      worstPeriod.textContent = "per 6 months";
      worstCard.appendChild(worstPeriod);

      const worstMonthly = document.createElement("div");
      worstMonthly.className = "range-card__monthly";
      worstMonthly.textContent = `≈ ${formatCurrency(worst_case_range.per_month_min)} – ${formatCurrency(worst_case_range.per_month_max)} / month`;
      worstCard.appendChild(worstMonthly);

      ranges.appendChild(worstCard);

      widget.appendChild(ranges);

      // Disclaimer
      const disclaimer = document.createElement("div");
      disclaimer.className = "quick-quote__disclaimer";

      const disclaimerTitle = document.createElement("div");
      disclaimerTitle.className = "disclaimer__title";
      disclaimerTitle.textContent = "Your actual rate depends on:";
      disclaimer.appendChild(disclaimerTitle);

      const factors = document.createElement("div");
      factors.className = "disclaimer__factors";

      const factorsList = [
        "Driver ages & experience",
        "Vehicle details",
        "Driving history",
        "Coverage selections",
        "Credit profile"
      ];

      factorsList.forEach(factor => {
        const chip = document.createElement("span");
        chip.className = "factor-chip";
        chip.textContent = factor;
        factors.appendChild(chip);
      });

      disclaimer.appendChild(factors);

      const disclaimerText = document.createElement("div");
      disclaimerText.className = "disclaimer__text";
      disclaimerText.textContent = "These ranges are estimates based on typical rates in your area. Get your personalized quote by providing detailed driver and vehicle information.";
      disclaimer.appendChild(disclaimerText);

      widget.appendChild(disclaimer);

      // CTA - Link to aisinsurance.com with zip code
      const cta = document.createElement("a");
      cta.className = "quick-quote__cta";
      cta.href = `https://aisinsurance.com/?zip=${encodeURIComponent(zip_code)}`;
      cta.target = "_blank";
      cta.rel = "noopener noreferrer";
      cta.style.textDecoration = "none";

      const ctaText = document.createElement("div");
      ctaText.className = "cta__text";

      const ctaTitle = document.createElement("div");
      ctaTitle.className = "cta__title";
      ctaTitle.textContent = "Get Your Personalized Quote";
      ctaText.appendChild(ctaTitle);

      const ctaSubtitle = document.createElement("div");
      ctaSubtitle.className = "cta__subtitle";
      ctaSubtitle.textContent = "Provide driver and vehicle details for accurate carrier quotes";
      ctaText.appendChild(ctaSubtitle);

      cta.appendChild(ctaText);

      const ctaArrow = document.createElement("div");
      ctaArrow.className = "cta__arrow";
      ctaArrow.textContent = "→";
      cta.appendChild(ctaArrow);

      widget.appendChild(cta);

      return widget;
    }

    function render(data) {
      root.innerHTML = "";
      if (!data) {
        root.textContent = "No quick quote data available.";
        return;
      }

      const widget = createWidget(data);
      if (widget) {
        root.appendChild(widget);
      } else {
        root.textContent = "Unable to display quick quote.";
      }
    }

    function hydrate(globals) {
      console.log("Quick quote widget: Hydrating with globals", globals);
      if (!globals || typeof globals !== "object") {
        console.warn("Quick quote widget: No valid globals object");
        return;
      }
      const toolOutput = globals.toolOutput || globals.tool_output;
      console.log("Quick quote widget: toolOutput", toolOutput);
      if (toolOutput) {
        // toolOutput IS the structured_content object
        render(toolOutput);
      } else {
        console.warn("Quick quote widget: No toolOutput found in globals");
      }
    }

    // Initial hydration
    const initialGlobals =
      typeof window !== "undefined" && window.openai ? window.openai : {};
    hydrate(initialGlobals);

    // Listen for updates
    window.addEventListener("openai:set_globals", (event) => {
      const detail = event.detail;
      if (!detail || !detail.globals) return;
      hydrate(detail.globals);
    });
  })();
</script>
""".strip()
