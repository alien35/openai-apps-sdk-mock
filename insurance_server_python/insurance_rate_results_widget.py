"""Personal auto rate results display widget markup for the Python MCP server."""

INSURANCE_RATE_RESULTS_WIDGET_HTML = """
<div id=\"insurance-rate-results-root\"></div>
<style>
  :root {
    color-scheme: light dark;
  }

  #insurance-rate-results-root {
    font-family: "Inter", "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont,
      "Helvetica Neue", Arial, sans-serif;
    color: rgba(15, 23, 42, 0.92);
  }

  @media (prefers-color-scheme: dark) {
    #insurance-rate-results-root {
      color: rgba(226, 232, 240, 0.94);
    }
  }

  .rate-results-widget {
    background: rgba(255, 255, 255, 0.97);
    border-radius: 20px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    box-shadow: 0 18px 48px rgba(15, 23, 42, 0.12);
    max-width: 720px;
  }

  @media (prefers-color-scheme: dark) {
    .rate-results-widget {
      background: rgba(15, 23, 42, 0.92);
      border-color: rgba(148, 163, 184, 0.22);
      box-shadow: 0 18px 48px rgba(0, 0, 0, 0.45);
    }
  }

  .rate-results-widget__header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
  }

  .rate-results-widget__eyebrow {
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.14em;
    font-weight: 600;
    color: rgba(99, 102, 241, 0.92);
  }

  .rate-results-widget__title {
    margin: 4px 0 0;
    font-size: 22px;
    line-height: 1.25;
    font-weight: 700;
  }

  .rate-results-widget__status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 9999px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 600;
    background: rgba(16, 185, 129, 0.12);
    color: rgba(5, 122, 85, 0.92);
    white-space: nowrap;
  }

  .rate-results-widget__status--error {
    background: rgba(248, 113, 113, 0.16);
    color: rgba(185, 28, 28, 0.92);
  }

  .rate-results-widget__subtitle {
    margin: 0;
    font-size: 14px;
    line-height: 1.6;
    color: rgba(15, 23, 42, 0.75);
  }

  @media (prefers-color-scheme: dark) {
    .rate-results-widget__subtitle {
      color: rgba(226, 232, 240, 0.75);
    }
  }

  .rate-results-widget__coverage {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }

  .rate-results-widget__coverage-chip {
    border-radius: 12px;
    border: 1px solid rgba(79, 70, 229, 0.22);
    background: rgba(129, 140, 248, 0.1);
    padding: 10px 14px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 120px;
  }

  .rate-results-widget__coverage-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: rgba(79, 70, 229, 0.9);
  }

  .rate-results-widget__coverage-value {
    font-size: 15px;
    font-weight: 600;
  }

  .rate-results-widget__program-list {
    display: grid;
    gap: 16px;
  }

  @media (min-width: 720px) {
    .rate-results-widget__program-list {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  .rate-results-widget__empty {
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.24);
    background: rgba(241, 245, 249, 0.55);
    padding: 18px;
    font-size: 14px;
    color: rgba(15, 23, 42, 0.7);
    display: none;
  }

  @media (prefers-color-scheme: dark) {
    .rate-results-widget__empty {
      background: rgba(30, 41, 59, 0.55);
      color: rgba(226, 232, 240, 0.7);
    }
  }

  .rate-results-widget__empty.is-visible {
    display: block;
  }

  .rate-program {
    border-radius: 16px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    background: rgba(248, 250, 252, 0.8);
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  @media (prefers-color-scheme: dark) {
    .rate-program {
      background: rgba(30, 41, 59, 0.85);
      border-color: rgba(148, 163, 184, 0.24);
    }
  }

  .rate-program__header {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: flex-start;
  }

  .rate-program__name {
    font-size: 17px;
    font-weight: 700;
    margin: 0;
  }

  .rate-program__carrier {
    margin: 0;
    font-size: 13px;
    color: rgba(15, 23, 42, 0.65);
  }

  @media (prefers-color-scheme: dark) {
    .rate-program__carrier {
      color: rgba(226, 232, 240, 0.68);
    }
  }

  .rate-program__premium {
    font-size: 20px;
    font-weight: 700;
    color: rgba(37, 99, 235, 0.95);
    margin: 0;
    white-space: nowrap;
  }

  @media (prefers-color-scheme: dark) {
    .rate-program__premium {
      color: rgba(129, 140, 248, 0.95);
    }
  }

  .rate-program__term {
    font-size: 13px;
    color: rgba(15, 23, 42, 0.65);
  }

  @media (prefers-color-scheme: dark) {
    .rate-program__term {
      color: rgba(226, 232, 240, 0.68);
    }
  }

  .rate-program__section-title {
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(15, 23, 42, 0.5);
    margin: 0;
  }

  @media (prefers-color-scheme: dark) {
    .rate-program__section-title {
      color: rgba(226, 232, 240, 0.55);
    }
  }

  .rate-program__plans {
    border-radius: 12px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    background: rgba(255, 255, 255, 0.78);
    padding: 12px 14px;
    display: grid;
    gap: 10px;
  }

  @media (prefers-color-scheme: dark) {
    .rate-program__plans {
      background: rgba(15, 23, 42, 0.88);
      border-color: rgba(129, 140, 248, 0.24);
    }
  }

  .rate-program__plan {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .rate-program__plan-label {
    font-size: 13px;
    font-weight: 600;
    color: rgba(15, 23, 42, 0.78);
  }

  @media (prefers-color-scheme: dark) {
    .rate-program__plan-label {
      color: rgba(226, 232, 240, 0.78);
    }
  }

  .rate-program__plan-detail {
    font-size: 13px;
    color: rgba(15, 23, 42, 0.68);
  }

  @media (prefers-color-scheme: dark) {
    .rate-program__plan-detail {
      color: rgba(226, 232, 240, 0.7);
    }
  }

  .rate-program__notes {
    border-radius: 12px;
    background: rgba(79, 70, 229, 0.08);
    padding: 12px 14px;
    margin: 0;
    list-style: none;
    display: grid;
    gap: 8px;
  }

  .rate-program__note {
    font-size: 13px;
    color: rgba(55, 65, 81, 0.88);
    position: relative;
    padding-left: 18px;
  }

  .rate-program__note::before {
    content: "";
    position: absolute;
    top: 6px;
    left: 6px;
    width: 6px;
    height: 6px;
    border-radius: 9999px;
    background: rgba(79, 70, 229, 0.9);
  }

  @media (prefers-color-scheme: dark) {
    .rate-program__notes {
      background: rgba(129, 140, 248, 0.18);
    }

    .rate-program__note {
      color: rgba(226, 232, 240, 0.86);
    }

    .rate-program__note::before {
      background: rgba(196, 181, 253, 0.95);
    }
  }
</style>
<script>
  (() => {
    const root = document.getElementById("insurance-rate-results-root");
    if (!root) return;

    const widget = document.createElement("div");
    widget.className = "rate-results-widget";
    widget.innerHTML = `
      <div class="rate-results-widget__header">
        <div>
          <div class="rate-results-widget__eyebrow">Carrier rate results</div>
          <h1 class="rate-results-widget__title" data-role="title">Quote</h1>
        </div>
        <span class="rate-results-widget__status" data-role="status"></span>
      </div>
      <p class="rate-results-widget__subtitle" data-role="subtitle"></p>
      <div class="rate-results-widget__coverage" data-role="coverage"></div>
      <div class="rate-results-widget__program-list" data-role="programs"></div>
      <div class="rate-results-widget__empty" data-role="empty">No carrier rate results are available for this quote yet.</div>
    `;

    root.appendChild(widget);

    const currencyFormatter = new Intl.NumberFormat(undefined, {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 2,
    });

    const PROGRAM_NAME_KEYS = [
      "ProgramName",
      "ProductName",
      "Program",
      "ProgramDescription",
      "PlanName",
      "Name",
      "Label",
    ];
    const CARRIER_NAME_KEYS = [
      "CarrierName",
      "Carrier",
      "CompanyName",
      "Company",
      "ProviderName",
    ];
    const TERM_KEYS = [
      "Term",
      "TermName",
      "TermDescription",
      "PolicyTerm",
      "TermType",
      "TermLabel",
      "TermText",
      "TermDisplay",
    ];
    const TERM_MONTH_KEYS = ["TermMonths", "PolicyTermMonths", "TermInMonths"];
    const PREMIUM_KEYS = [
      "TotalPremium",
      "TotalPremiumAmount",
      "TotalPolicyPremium",
      "TotalPremiumWithFees",
      "TotalTermPremium",
      "Premium",
      "PremiumTotal",
      "Total",
    ];
    const POLICY_FEE_KEYS = ["PolicyFee", "PolicyFees", "PolicyFeeAmount"];
    const LIABILITY_KEYS = [
      "BaseLiability",
      "BaseLiabilityLimits",
      "LiabilityLimits",
      "Liability",
      "BaseLiabilityLimit",
    ];
    const BI_KEYS = [
      "BodilyInjuryLimit",
      "BodilyInjury",
      "BILimit",
      "BodilyInjuryLiability",
    ];
    const PD_KEYS = [
      "PropertyDamageLimit",
      "PropertyDamage",
      "PDLimit",
      "PropertyDamageLiability",
    ];
    const UM_KEYS = [
      "UninsuredMotoristLimit",
      "UninsuredMotorist",
      "UMLimit",
      "UMBI",
      "UninsuredMotoristBodilyInjury",
    ];
    const COMP_KEYS = [
      "ComprehensiveDeductible",
      "CompDeductible",
      "Comprehensive",
    ];
    const COLLISION_KEYS = [
      "CollisionDeductible",
      "CollDeductible",
      "Collision",
    ];
    const PAYMENT_COLLECTION_KEYS = [
      "PaymentPlans",
      "PaymentOptions",
      "PaymentPlanOptions",
      "PaymentMethods",
      "PaymentSchedules",
      "PaymentPlanList",
      "Plans",
    ];
    const PLAN_LABEL_KEYS = [
      "PlanName",
      "Plan",
      "Name",
      "DisplayName",
      "Description",
      "PaymentPlanName",
      "Method",
      "Code",
    ];
    const DOWN_PAYMENT_KEYS = [
      "DownPayment",
      "DownPaymentAmount",
      "Down",
      "DueToday",
      "Deposit",
      "DownPaymentDue",
    ];
    const INSTALLMENT_ARRAY_KEYS = [
      "Installments",
      "Payments",
      "Schedule",
      "InstallmentSchedule",
    ];
    const INSTALLMENT_AMOUNT_KEYS = [
      "InstallmentAmount",
      "Amount",
      "PaymentAmount",
      "MonthlyPayment",
    ];
    const INSTALLMENT_COUNT_KEYS = [
      "InstallmentCount",
      "NumberOfPayments",
      "Payments",
      "Installments",
      "Count",
    ];
    const FREQUENCY_KEYS = [
      "Frequency",
      "InstallmentFrequency",
      "PaymentFrequency",
      "Mode",
      "Cadence",
    ];

    function coerceNumber(value) {
      if (typeof value === "number" && !Number.isNaN(value)) return value;
      if (typeof value === "string") {
        const cleaned = value.replace(/[^0-9.-]/g, "");
        if (!cleaned) return null;
        const parsed = Number.parseFloat(cleaned);
        return Number.isNaN(parsed) ? null : parsed;
      }
      return null;
    }

    function firstString(record, keys) {
      for (const key of keys) {
        if (!Object.prototype.hasOwnProperty.call(record, key)) continue;
        const value = record[key];
        if (typeof value === "string" && value.trim()) {
          return value.trim();
        }
      }
      return null;
    }

    function firstNumber(record, keys) {
      for (const key of keys) {
        if (!Object.prototype.hasOwnProperty.call(record, key)) continue;
        const value = coerceNumber(record[key]);
        if (value !== null) {
          return value;
        }
      }
      return null;
    }

    function firstArray(record, keys) {
      for (const key of keys) {
        if (!Object.prototype.hasOwnProperty.call(record, key)) continue;
        const value = record[key];
        if (Array.isArray(value) && value.length) {
          return value;
        }
      }
      return null;
    }

    function formatCurrency(value) {
      if (value === null || value === undefined) return null;
      try {
        return currencyFormatter.format(value);
      } catch (error) {
        return `$${value.toFixed ? value.toFixed(2) : value}`;
      }
    }

    function formatTerm(record, contextTerm) {
      const termString = firstString(record, TERM_KEYS) || contextTerm;
      if (termString) {
        return termString;
      }

      const termMonths = firstNumber(record, TERM_MONTH_KEYS);
      if (termMonths !== null) {
        const rounded = Math.round(termMonths);
        if (rounded === 12) return "12 months";
        if (rounded === 6) return "6 months";
        if (rounded === 1) return "Monthly";
        if (rounded > 0) return `${rounded} months`;
      }

      return null;
    }

    function collectNotes(record) {
      const notes = new Set();
      for (const key of ["Notes", "Highlights", "NotesList", "Messages"]) {
        const value = record[key];
        if (!value) continue;
        if (Array.isArray(value)) {
          value.forEach((entry) => {
            if (typeof entry === "string" && entry.trim()) {
              notes.add(entry.trim());
            } else if (
              typeof entry === "number" &&
              Number.isFinite(entry)
            ) {
              notes.add(formatCurrency(entry) || `${entry}`);
            }
          });
        } else if (typeof value === "string" && value.trim()) {
          notes.add(value.trim());
        }
      }

      const travelClub = firstNumber(record, ["TravelClubPremium"]);
      if (travelClub !== null) {
        const formatted = formatCurrency(travelClub);
        if (formatted) {
          notes.add(`Includes ${formatted} Travel Club premium`);
        }
      }

      const motoristProtection = firstNumber(record, ["MotoristProtectionPremium"]);
      if (motoristProtection !== null) {
        const formatted = formatCurrency(motoristProtection);
        if (formatted) {
          notes.add(`Includes ${formatted} Motorist Protection premium`);
        }
      }

      return Array.from(notes);
    }

    function extractPaymentPlans(record) {
      const plans = [];
      const seen = new Set();

      function addPlan(planRecord, fallbackLabel) {
        if (!planRecord || typeof planRecord !== "object") return;
        const label =
          firstString(planRecord, PLAN_LABEL_KEYS) ||
          (typeof fallbackLabel === "string" && fallbackLabel)
            ? fallbackLabel
            : null;

        const planLabel = label || "Payment plan";
        const key = `${planLabel}|${JSON.stringify(planRecord)}`;
        if (seen.has(key)) return;
        seen.add(key);

        const details = [];
        const downPayment = firstNumber(planRecord, DOWN_PAYMENT_KEYS);
        if (downPayment !== null) {
          const formattedDown = formatCurrency(downPayment);
          if (formattedDown) {
            details.push(`${formattedDown} down`);
          }
        }

        const installmentsArray = firstArray(planRecord, INSTALLMENT_ARRAY_KEYS);
        if (installmentsArray) {
          for (const installment of installmentsArray) {
            if (!installment || typeof installment !== "object") continue;
            const amount = firstNumber(installment, INSTALLMENT_AMOUNT_KEYS);
            const count = firstNumber(installment, INSTALLMENT_COUNT_KEYS);
            if (amount !== null && count !== null) {
              const formattedAmount = formatCurrency(amount);
              if (formattedAmount) {
                details.push(`${formattedAmount} × ${count}`);
              }
            } else if (amount !== null) {
              const formattedAmount = formatCurrency(amount);
              if (formattedAmount) {
                details.push(formattedAmount);
              }
            }
          }
        } else {
          const installmentAmount = firstNumber(
            planRecord,
            INSTALLMENT_AMOUNT_KEYS
          );
          const installmentCount = firstNumber(
            planRecord,
            INSTALLMENT_COUNT_KEYS
          );
          if (installmentAmount !== null && installmentCount !== null) {
            const formattedAmount = formatCurrency(installmentAmount);
            if (formattedAmount) {
              details.push(`${formattedAmount} × ${installmentCount}`);
            }
          }
        }

        const frequency = firstString(planRecord, FREQUENCY_KEYS);
        if (frequency) {
          details.push(frequency);
        }

        if (!details.length) {
          const total = firstNumber(planRecord, PREMIUM_KEYS);
          const formattedTotal = formatCurrency(total);
          if (formattedTotal) {
            details.push(formattedTotal);
          }
        }

        plans.push({ label: planLabel, details });
      }

      for (const key of PAYMENT_COLLECTION_KEYS) {
        if (!Object.prototype.hasOwnProperty.call(record, key)) continue;
        const value = record[key];
        if (!value) continue;

        if (Array.isArray(value)) {
          value.forEach((plan, index) => addPlan(plan, `Plan ${index + 1}`));
        } else if (typeof value === "object") {
          Object.entries(value).forEach(([planKey, planValue]) => {
            const fallback = typeof planKey === "string" ? planKey : undefined;
            addPlan(planValue, fallback);
          });
        }
      }

      return plans;
    }

    function extractPrograms(rateResults) {
      const programs = [];
      const seenNodes = new WeakSet();
      const dedupe = new Set();

      function visit(node, context) {
        if (!node || typeof node !== "object") return;
        if (seenNodes.has(node)) return;
        seenNodes.add(node);

        if (Array.isArray(node)) {
          node.forEach((item) => visit(item, context));
          return;
        }

        const record = node;

        const carrierName =
          firstString(record, CARRIER_NAME_KEYS) || context.carrierName || null;
        const programName =
          firstString(record, PROGRAM_NAME_KEYS) || context.programName || null;
        const termLabel = formatTerm(record, context.termLabel || null);
        const totalPremium = firstNumber(record, PREMIUM_KEYS);

        const policyFee = firstNumber(record, POLICY_FEE_KEYS);
        const baseLiability = firstString(record, LIABILITY_KEYS);
        const bi = firstString(record, BI_KEYS);
        const pd = firstString(record, PD_KEYS);
        const um = firstString(record, UM_KEYS);
        const comp =
          firstString(record, COMP_KEYS) ||
          (() => {
            const numeric = firstNumber(record, COMP_KEYS);
            if (numeric === null) return null;
            return formatCurrency(numeric) || `${numeric}`;
          })();
        const collision =
          firstString(record, COLLISION_KEYS) ||
          (() => {
            const numeric = firstNumber(record, COLLISION_KEYS);
            if (numeric === null) return null;
            return formatCurrency(numeric) || `${numeric}`;
          })();

        if (programName && totalPremium !== null) {
          const keyParts = [carrierName || "", programName, totalPremium, termLabel || ""];
          const key = keyParts.join("|");
          if (!dedupe.has(key)) {
            dedupe.add(key);
            programs.push({
              carrierName,
              programName,
              termLabel,
              totalPremium,
              policyFee,
              baseLiability,
              coverage: {
                bi,
                pd,
                um,
                comp,
                collision,
              },
              paymentPlans: extractPaymentPlans(record),
              notes: collectNotes(record),
            });
          }
        }

        const nextContext = {
          carrierName,
          programName,
          termLabel,
        };

        Object.values(record).forEach((value) => {
          if (value && typeof value === "object") {
            visit(value, nextContext);
          }
        });
      }

      visit(rateResults, {});
      return programs;
    }

    function computeSharedCoverage(programs) {
      if (!programs.length) return {};

      const keys = [
        { key: "bi", label: "BI" },
        { key: "pd", label: "PD" },
        { key: "um", label: "UM" },
        { key: "comp", label: "Comp Deductible" },
        { key: "collision", label: "Collision Deductible" },
      ];

      const shared = {};
      for (const { key, label } of keys) {
        let value = null;
        let consistent = true;
        for (const program of programs) {
          const programValue = program.coverage?.[key] || null;
          if (!programValue) {
            consistent = false;
            break;
          }
          if (value === null) {
            value = programValue;
          } else if (value !== programValue) {
            consistent = false;
            break;
          }
        }
        if (consistent && value !== null) {
          shared[label] = value;
        }
      }

      let policyFee = null;
      for (const program of programs) {
        if (program.policyFee === null || program.policyFee === undefined) {
          policyFee = null;
          break;
        }
        if (policyFee === null) {
          policyFee = program.policyFee;
        } else if (policyFee !== program.policyFee) {
          policyFee = null;
          break;
        }
      }
      if (policyFee !== null) {
        const formatted = formatCurrency(policyFee);
        if (formatted) {
          shared["Policy Fee"] = formatted;
        }
      }

      return shared;
    }

    function renderSharedCoverage(sharedCoverage) {
      const coverageEl = widget.querySelector('[data-role="coverage"]');
      coverageEl.innerHTML = "";

      const entries = Object.entries(sharedCoverage);
      if (!entries.length) {
        coverageEl.style.display = "none";
        return;
      }

      coverageEl.style.display = "flex";
      for (const [label, value] of entries) {
        const chip = document.createElement("div");
        chip.className = "rate-results-widget__coverage-chip";

        const labelEl = document.createElement("div");
        labelEl.className = "rate-results-widget__coverage-label";
        labelEl.textContent = label;
        chip.appendChild(labelEl);

        const valueEl = document.createElement("div");
        valueEl.className = "rate-results-widget__coverage-value";
        valueEl.textContent = value;
        chip.appendChild(valueEl);

        coverageEl.appendChild(chip);
      }
    }

    function renderPrograms(programs, sharedCoverage) {
      const list = widget.querySelector('[data-role="programs"]');
      const empty = widget.querySelector('[data-role="empty"]');
      list.innerHTML = "";

      if (!programs.length) {
        empty.classList.add("is-visible");
        return;
      }

      empty.classList.remove("is-visible");

      programs
        .sort((a, b) => a.totalPremium - b.totalPremium)
        .forEach((program) => {
          const card = document.createElement("article");
          card.className = "rate-program";

          const header = document.createElement("div");
          header.className = "rate-program__header";

          const headingGroup = document.createElement("div");

          const name = document.createElement("h2");
          name.className = "rate-program__name";
          name.textContent = program.programName;
          headingGroup.appendChild(name);

          if (program.carrierName) {
            const carrier = document.createElement("p");
            carrier.className = "rate-program__carrier";
            carrier.textContent = program.carrierName;
            headingGroup.appendChild(carrier);
          }

          header.appendChild(headingGroup);

          const premium = document.createElement("p");
          premium.className = "rate-program__premium";
          const formattedPremium = formatCurrency(program.totalPremium);
          premium.textContent = formattedPremium || "--";
          header.appendChild(premium);

          card.appendChild(header);

          if (program.termLabel) {
            const term = document.createElement("div");
            term.className = "rate-program__term";
            term.textContent = program.termLabel;
            card.appendChild(term);
          }

          if (program.paymentPlans.length) {
            const plansTitle = document.createElement("p");
            plansTitle.className = "rate-program__section-title";
            plansTitle.textContent = "Payment options";
            card.appendChild(plansTitle);

            const plansList = document.createElement("div");
            plansList.className = "rate-program__plans";

            program.paymentPlans.forEach((plan) => {
              if (!plan || !plan.label) return;
              const planEl = document.createElement("div");
              planEl.className = "rate-program__plan";

              const labelEl = document.createElement("div");
              labelEl.className = "rate-program__plan-label";
              labelEl.textContent = plan.label;
              planEl.appendChild(labelEl);

              const details = plan.details && plan.details.length
                ? plan.details
                : ["See carrier portal for installment breakdown"];

              details.forEach((detail) => {
                if (!detail) return;
                const detailEl = document.createElement("div");
                detailEl.className = "rate-program__plan-detail";
                detailEl.textContent = detail;
                planEl.appendChild(detailEl);
              });

              plansList.appendChild(planEl);
            });

            card.appendChild(plansList);
          }

          const notes = program.notes.slice();
          if (program.baseLiability) {
            notes.unshift(`Base liability ${program.baseLiability}`);
          }

          const sharedPolicyFee = sharedCoverage && sharedCoverage["Policy Fee"];
          if (!sharedPolicyFee && program.policyFee !== null && program.policyFee !== undefined) {
            const formattedFee = formatCurrency(program.policyFee);
            if (formattedFee) {
              notes.push(`Policy fee ${formattedFee}`);
            }
          }

          const compShared = sharedCoverage && sharedCoverage["Comp Deductible"];
          if (!compShared && program.coverage?.comp) {
            notes.push(`Comprehensive deductible ${program.coverage.comp}`);
          }

          const collisionShared = sharedCoverage && sharedCoverage["Collision Deductible"];
          if (!collisionShared && program.coverage?.collision) {
            notes.push(`Collision deductible ${program.coverage.collision}`);
          }

          if (notes.length) {
            const notesTitle = document.createElement("p");
            notesTitle.className = "rate-program__section-title";
            notesTitle.textContent = "Highlights";
            card.appendChild(notesTitle);

            const notesList = document.createElement("ul");
            notesList.className = "rate-program__notes";
            notes.forEach((note) => {
              if (!note) return;
              const item = document.createElement("li");
              item.className = "rate-program__note";
              item.textContent = note;
              notesList.appendChild(item);
            });
            card.appendChild(notesList);
          }

          list.appendChild(card);
        });
    }

    function applyToolOutput(toolOutput) {
      const titleEl = widget.querySelector('[data-role="title"]');
      const statusEl = widget.querySelector('[data-role="status"]');
      const subtitleEl = widget.querySelector('[data-role="subtitle"]');

      const identifier =
        toolOutput && typeof toolOutput.identifier === "string"
          ? toolOutput.identifier.trim()
          : null;
      if (identifier) {
        titleEl.textContent = `Quote ${identifier}`;
      } else {
        titleEl.textContent = "Carrier quote";
      }

      const statusCode =
        typeof toolOutput.status === "number"
          ? toolOutput.status
          : typeof toolOutput.rate_results_status === "number"
          ? toolOutput.rate_results_status
          : null;
      if (statusCode !== null) {
        statusEl.textContent = `Status ${statusCode}`;
        statusEl.classList.toggle(
          "rate-results-widget__status--error",
          statusCode >= 300
        );
        statusEl.style.display = "inline-flex";
      } else {
        statusEl.textContent = "";
        statusEl.style.display = "none";
      }

      const rateResults = toolOutput ? toolOutput.rate_results : null;
      const programs = extractPrograms(rateResults);
      const sharedCoverage = computeSharedCoverage(programs);
      renderSharedCoverage(sharedCoverage);
      renderPrograms(programs, sharedCoverage);

      if (programs.length) {
        subtitleEl.textContent = `Showing ${programs.length} carrier option${
          programs.length === 1 ? "" : "s"
        } sorted by total premium.`;
      } else {
        subtitleEl.textContent =
          "We could not parse carrier premiums from the response. Review the carrier portal for more details.";
      }
    }

    function hydrateFromGlobals(globals) {
      if (!globals || typeof globals !== "object") return;
      if (globals.toolOutput) {
        applyToolOutput(globals.toolOutput);
      }
    }

    hydrateFromGlobals(window.openai ?? {});

    window.addEventListener("openai:set_globals", (event) => {
      const detail = event.detail;
      if (!detail || !detail.globals) return;
      hydrateFromGlobals(detail.globals);
    });
  })();
</script>
""".strip()
