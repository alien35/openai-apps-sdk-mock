"""Personal auto rate results display widget markup for the Python MCP server."""

INSURANCE_RATE_RESULTS_WIDGET_HTML = """
<div id=\"insurance-rate-results-root\"></div>
<style>
  :root {
    color-scheme: light dark;
  }

  #insurance-rate-results-root {
    font-family: \"Inter\", \"Segoe UI\", system-ui, -apple-system, BlinkMacSystemFont,
      \"Helvetica Neue\", Arial, sans-serif;
    color: rgba(15, 23, 42, 0.94);
    line-height: 1.6;
  }

  @media (prefers-color-scheme: dark) {
    #insurance-rate-results-root {
      color: rgba(226, 232, 240, 0.96);
    }
  }

  .rate-results {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 20px;
    border: 1px solid rgba(15, 23, 42, 0.08);
    padding: 24px;
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.16);
    display: flex;
    flex-direction: column;
    gap: 20px;
    max-width: 960px;
  }

  @media (prefers-color-scheme: dark) {
    .rate-results {
      background: rgba(15, 23, 42, 0.92);
      border-color: rgba(148, 163, 184, 0.28);
      box-shadow: 0 22px 48px rgba(2, 6, 23, 0.58);
    }
  }

  .rate-results__header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
    flex-wrap: wrap;
  }

  .rate-results__eyebrow {
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: rgba(99, 102, 241, 0.92);
  }

  .rate-results__title {
    margin: 6px 0 4px;
    font-size: 26px;
    line-height: 1.2;
    font-weight: 700;
  }

  .rate-results__subtitle {
    margin: 0;
    font-size: 15px;
    color: rgba(15, 23, 42, 0.7);
  }

  @media (prefers-color-scheme: dark) {
    .rate-results__subtitle {
      color: rgba(226, 232, 240, 0.72);
    }
  }

  .rate-results__status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 600;
    background: rgba(16, 185, 129, 0.16);
    color: rgba(4, 120, 87, 0.94);
    white-space: nowrap;
  }

  .rate-results__status.is-hidden {
    display: none;
  }

  .rate-results__status.is-error {
    background: rgba(248, 113, 113, 0.2);
    color: rgba(185, 28, 28, 0.94);
  }

  .rate-results__meta {
    font-size: 14px;
    color: rgba(15, 23, 42, 0.64);
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  @media (prefers-color-scheme: dark) {
    .rate-results__meta {
      color: rgba(226, 232, 240, 0.68);
    }
  }

  .rate-results__meta-chip {
    border-radius: 999px;
    background: rgba(59, 130, 246, 0.14);
    color: rgba(37, 99, 235, 0.94);
    padding: 4px 12px;
    font-weight: 600;
    font-size: 13px;
  }

  @media (prefers-color-scheme: dark) {
    .rate-results__meta-chip {
      background: rgba(96, 165, 250, 0.24);
      color: rgba(191, 219, 254, 0.94);
    }
  }

  .rate-results__coverage-summary {
    display: none;
    flex-direction: column;
    gap: 10px;
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.28);
    background: rgba(248, 250, 252, 0.92);
    padding: 16px 18px;
  }

  @media (prefers-color-scheme: dark) {
    .rate-results__coverage-summary {
      background: rgba(30, 41, 59, 0.72);
      border-color: rgba(148, 163, 184, 0.4);
    }
  }

  .coverage-summary__headline {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(79, 70, 229, 0.88);
  }

  .coverage-summary__limits {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    font-size: 14px;
  }

  .coverage-summary__footnote {
    font-size: 13px;
    color: rgba(15, 23, 42, 0.68);
  }

  @media (prefers-color-scheme: dark) {
    .coverage-summary__footnote {
      color: rgba(226, 232, 240, 0.7);
    }
  }

  .rate-results__view-toggle {
    display: inline-flex;
    border-radius: 12px;
    border: 1px solid rgba(148, 163, 184, 0.32);
    overflow: hidden;
    background: rgba(248, 250, 252, 0.85);
  }

  @media (prefers-color-scheme: dark) {
    .rate-results__view-toggle {
      background: rgba(30, 41, 59, 0.6);
      border-color: rgba(148, 163, 184, 0.45);
    }
  }

  .rate-results__view-button {
    padding: 10px 18px;
    border: none;
    background: transparent;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    color: inherit;
  }

  .rate-results__view-button.is-active {
    background: rgba(59, 130, 246, 0.16);
    color: rgba(37, 99, 235, 0.95);
  }

  @media (prefers-color-scheme: dark) {
    .rate-results__view-button.is-active {
      background: rgba(96, 165, 250, 0.22);
      color: rgba(191, 219, 254, 0.94);
    }
  }

  .rate-results__cards {
    display: grid;
    gap: 18px;
  }

  @media (min-width: 960px) {
    .rate-results__cards {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  .product-card {
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.3);
    background: rgba(255, 255, 255, 0.94);
    padding: 18px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  @media (prefers-color-scheme: dark) {
    .product-card {
      background: rgba(15, 23, 42, 0.85);
      border-color: rgba(148, 163, 184, 0.45);
    }
  }

  .product-card__header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
  }

  .product-card__name {
    margin: 0;
    font-size: 20px;
    font-weight: 700;
  }

  .product-card__badges {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .badge {
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
    background: rgba(99, 102, 241, 0.12);
    color: rgba(79, 70, 229, 0.9);
  }

  @media (prefers-color-scheme: dark) {
    .badge {
      background: rgba(129, 140, 248, 0.2);
      color: rgba(199, 210, 254, 0.94);
    }
  }

  .product-card__headline {
    margin: 0;
    font-size: 18px;
  }

  .product-card__headline strong {
    display: block;
    font-size: 28px;
    font-weight: 700;
    color: rgba(37, 99, 235, 0.95);
  }

  @media (prefers-color-scheme: dark) {
    .product-card__headline strong {
      color: rgba(191, 219, 254, 0.95);
    }
  }

  .product-card__plan-toggle {
    display: inline-flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .product-card__plan-button {
    padding: 6px 12px;
    border-radius: 10px;
    border: 1px solid rgba(148, 163, 184, 0.36);
    background: transparent;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
  }

  .product-card__plan-button.is-active {
    background: rgba(59, 130, 246, 0.16);
    border-color: rgba(37, 99, 235, 0.5);
    color: rgba(37, 99, 235, 0.94);
  }

  @media (prefers-color-scheme: dark) {
    .product-card__plan-button.is-active {
      background: rgba(96, 165, 250, 0.22);
      border-color: rgba(191, 219, 254, 0.6);
      color: rgba(191, 219, 254, 0.95);
    }
  }

  .product-card__plan-summary {
    border-radius: 14px;
    border: 1px solid rgba(148, 163, 184, 0.3);
    background: rgba(248, 250, 252, 0.92);
    padding: 12px 16px;
    display: grid;
    gap: 6px;
    font-size: 14px;
  }

  @media (prefers-color-scheme: dark) {
    .product-card__plan-summary {
      background: rgba(30, 41, 59, 0.7);
      border-color: rgba(148, 163, 184, 0.45);
    }
  }

  .product-card__callout {
    font-size: 13px;
    color: rgba(22, 101, 52, 0.82);
    font-weight: 600;
  }

  @media (prefers-color-scheme: dark) {
    .product-card__callout {
      color: rgba(167, 243, 208, 0.92);
    }
  }

  .product-card__details {
    display: grid;
    gap: 10px;
  }

  .product-card__details-title {
    font-size: 13px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 600;
    color: rgba(15, 23, 42, 0.62);
  }

  @media (prefers-color-scheme: dark) {
    .product-card__details-title {
      color: rgba(226, 232, 240, 0.68);
    }
  }

  .product-card__details-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: grid;
    gap: 6px;
    font-size: 14px;
  }

  .product-card__coverage {
    border-radius: 14px;
    border: 1px solid rgba(148, 163, 184, 0.3);
    background: rgba(248, 250, 252, 0.92);
    padding: 12px 16px;
    display: grid;
    gap: 6px;
  }

  @media (prefers-color-scheme: dark) {
    .product-card__coverage {
      background: rgba(30, 41, 59, 0.72);
      border-color: rgba(148, 163, 184, 0.45);
    }
  }

  .product-card__coverage-item {
    display: flex;
    justify-content: space-between;
    gap: 12px;
  }

  .product-card__coverage-label {
    font-weight: 600;
  }

  .product-card__cta {
    align-self: flex-start;
    padding: 10px 18px;
    border-radius: 12px;
    border: none;
    background: rgba(37, 99, 235, 0.95);
    color: white;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
  }

  .rate-results__compare {
    border-radius: 18px;
    border: 1px solid rgba(148, 163, 184, 0.3);
    overflow: hidden;
    display: none;
  }

  .compare-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    background: rgba(255, 255, 255, 0.94);
  }

  @media (prefers-color-scheme: dark) {
    .compare-table {
      background: rgba(15, 23, 42, 0.82);
    }
  }

  .compare-table thead {
    background: rgba(59, 130, 246, 0.14);
  }

  .compare-table th,
  .compare-table td {
    padding: 14px 16px;
    border-bottom: 1px solid rgba(148, 163, 184, 0.28);
    text-align: left;
    vertical-align: top;
  }

  .compare-table tbody tr:last-child td {
    border-bottom: none;
  }

  .compare-table__product {
    display: grid;
    gap: 6px;
  }

  .compare-table__badges {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .compare-table__note {
    font-size: 13px;
    color: rgba(15, 23, 42, 0.68);
  }

  @media (prefers-color-scheme: dark) {
    .compare-table__note {
      color: rgba(226, 232, 240, 0.72);
    }
  }

  .rate-results__empty {
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.32);
    background: rgba(248, 250, 252, 0.9);
    padding: 18px;
    font-size: 14px;
    color: rgba(15, 23, 42, 0.72);
    display: none;
  }

  @media (prefers-color-scheme: dark) {
    .rate-results__empty {
      background: rgba(30, 41, 59, 0.74);
      color: rgba(226, 232, 240, 0.75);
    }
  }

  .rate-results__empty.is-visible {
    display: block;
  }
</style>
<script>
  (() => {
    function createDataModel() {
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
      const POLICY_FEE_KEYS = [
        "PolicyFee",
        "PolicyFees",
        "PolicyFeeAmount",
        "PolicyFeeTotal",
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
      const PAYMENT_METHOD_KEYS = [
        "PaymentMethod",
        "PaymentType",
        "PaymentMode",
        "Method",
        "PayPlan",
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
      const WARNING_KEYS = ["Warnings", "Messages", "Alerts", "Notes"];
      const ADD_ON_FIELDS = [
        { amountKeys: ["TravelClubPremium", "TravelClubFee"], label: "Travel Club" },
        {
          amountKeys: ["MotoristProtectionPremium", "MotoristProtection"],
          label: "Motorist Protection",
        },
      ];
      const PLAN_SORT_ORDER = [
        "full_pay",
        "monthly_card",
        "monthly_eft",
        "monthly_invoice",
        "monthly",
      ];

      function formatCurrency(value) {
        if (value === null || value === undefined) return null;
        if (typeof value === "string" && !value.trim()) return null;
        try {
          return currencyFormatter.format(typeof value === "number" ? value : Number(value));
        } catch (error) {
          const num = Number(value);
          return Number.isFinite(num) ? `$${num.toFixed(2)}` : null;
        }
      }

      function coerceNumber(value) {
        if (typeof value === "number" && Number.isFinite(value)) return value;
        if (typeof value === "string") {
          const cleaned = value.replace(/[^0-9.-]/g, "");
          if (!cleaned) return null;
          const parsed = Number.parseFloat(cleaned);
          return Number.isFinite(parsed) ? parsed : null;
        }
        return null;
      }

      function firstString(record, keys) {
        for (const key of keys) {
          if (!Object.prototype.hasOwnProperty.call(record, key)) continue;
          const value = record[key];
          if (typeof value === "string" && value.trim()) return value.trim();
        }
        return null;
      }

      function firstNumber(record, keys) {
        for (const key of keys) {
          if (!Object.prototype.hasOwnProperty.call(record, key)) continue;
          const value = coerceNumber(record[key]);
          if (value !== null) return value;
        }
        return null;
      }

      function firstArray(record, keys) {
        for (const key of keys) {
          if (!Object.prototype.hasOwnProperty.call(record, key)) continue;
          const value = record[key];
          if (Array.isArray(value) && value.length) return value;
        }
        return null;
      }

      function formatTerm(record, fallback) {
        const fromRecord = firstString(record, TERM_KEYS);
        if (fromRecord) return fromRecord;
        if (fallback) return fallback;
        const months = firstNumber(record, TERM_MONTH_KEYS);
        if (months !== null) {
          const rounded = Math.round(months);
          if (rounded > 0) {
            return `${rounded} month${rounded === 1 ? "" : "s"}`;
          }
        }
        return null;
      }

      function parseTermMonths(record, termLabel) {
        const direct = firstNumber(record, TERM_MONTH_KEYS);
        if (direct !== null) return direct;
        if (typeof termLabel === "string") {
          const match = termLabel.match(/([0-9]+(?:[.][0-9]+)?)/);
          if (match) {
            const parsed = Number.parseFloat(match[1]);
            if (Number.isFinite(parsed)) return parsed;
          }
        }
        return null;
      }

      function normalizeLimit(value) {
        if (value === null || value === undefined) return null;
        if (typeof value === "number") {
          if (!Number.isFinite(value)) return null;
          return value >= 1000 ? `${Math.round(value / 1000)}k` : `${value}`;
        }
        if (typeof value === "string") {
          const trimmed = value.trim();
          return trimmed
            ? trimmed.replace(/[\\t\\n\\r ]+/g, " ")
            : null;
        }
        return null;
      }

      function collectWarnings(record) {
        const result = [];
        for (const key of WARNING_KEYS) {
          if (!Object.prototype.hasOwnProperty.call(record, key)) continue;
          const value = record[key];
          if (!value) continue;
          if (Array.isArray(value)) {
            value.forEach((item) => {
              if (typeof item === "string" && item.trim()) {
                result.push(item.trim());
              }
            });
          } else if (typeof value === "string" && value.trim()) {
            result.push(value.trim());
          }
        }
        return result;
      }

      function parseMileageAssumption(warnings) {
        for (const warning of warnings) {
          const match = warning.match(
            /([0-9][0-9,]*)[\\t\\n\\r ]*(?:mi|mile|miles)/i,
          );
          if (match) {
            const numeric = Number.parseInt(match[1].replace(/,/g, ""), 10);
            if (Number.isFinite(numeric)) return numeric;
          }
        }
        return null;
      }

      function extractAddOns(record) {
        const addOns = [];
        for (const spec of ADD_ON_FIELDS) {
          const amount = firstNumber(record, spec.amountKeys);
          if (amount !== null) {
            addOns.push({ label: spec.label, amount });
          }
        }
        return addOns;
      }
      function normalizeMethod(label) {
        const text = label ? label.toLowerCase() : "";
        if (/credit|card|cc|debit/.test(text)) return "card";
        if (/eft|ach|electronic|fund/.test(text)) return "eft";
        if (/invoice|bill|mail|paper/.test(text)) return "invoice";
        if (/cash|check/.test(text)) return "invoice";
        return null;
      }

      function normalizePlanKey(label, methodLabel, installmentCount, frequency, downPayment, total) {
        const combined = [label, methodLabel, frequency].filter(Boolean).join(" ").toLowerCase();
        const method = normalizeMethod(combined) || normalizeMethod(methodLabel || label);
        const mentionsMonthly = /month|installment|pay plan/.test(combined);
        const mentionsFull = /full|one pay|single|annual/.test(combined);
        const hasInstallments = typeof installmentCount === "number" && installmentCount > 0;

        if (mentionsFull || (!hasInstallments && mentionsMonthly === false && downPayment !== null && total !== null && Math.abs(total - downPayment) < 0.5)) {
          return "full_pay";
        }

        if (hasInstallments || mentionsMonthly) {
          if (method === "card") return "monthly_card";
          if (method === "eft") return "monthly_eft";
          if (method === "invoice") return "monthly_invoice";
          return "monthly";
        }

        if (method === "invoice" && downPayment !== null && total !== null && downPayment < total) {
          return "monthly_invoice";
        }

        if (downPayment !== null && total !== null && Math.abs(total - downPayment) < 0.5) {
          return "full_pay";
        }

        return "other";
      }

      function derivePlan(record) {
        const label = firstString(record, PLAN_LABEL_KEYS);
        const methodLabel = firstString(record, PAYMENT_METHOD_KEYS);
        const frequency = firstString(record, FREQUENCY_KEYS);
        const downPayment = firstNumber(record, DOWN_PAYMENT_KEYS);
        let installmentCount = firstNumber(record, INSTALLMENT_COUNT_KEYS);
        let installmentAmount = firstNumber(record, INSTALLMENT_AMOUNT_KEYS);
        const totalPremium = firstNumber(record, PREMIUM_KEYS);
        const installments = firstArray(record, INSTALLMENT_ARRAY_KEYS);
        let scheduleSum = null;
        let scheduleCount = null;

        if (installments) {
          let total = 0;
          let count = 0;
          let uniformAmount = null;
          let uniform = true;
          for (const item of installments) {
            if (!item || typeof item !== "object") continue;
            const amount = firstNumber(item, INSTALLMENT_AMOUNT_KEYS);
            if (amount === null) continue;
            total += amount;
            count += 1;
            if (uniformAmount === null) {
              uniformAmount = amount;
            } else if (Math.abs(uniformAmount - amount) > 0.01) {
              uniform = false;
            }
          }
          if (count > 0) {
            scheduleSum = total;
            scheduleCount = count;
            if (uniform && installmentAmount === null) {
              installmentAmount = uniformAmount;
            }
            if (installmentCount === null) {
              installmentCount = count;
            }
          }
        }

        const planKey = normalizePlanKey(
          label,
          methodLabel,
          installmentCount,
          frequency,
          downPayment,
          totalPremium
        );

        return {
          key: planKey,
          label,
          methodLabel,
          frequency,
          downPayment,
          installmentCount,
          installmentAmount,
          scheduleSum,
          scheduleCount,
          totalPremium,
        };
      }

      function firstFinite(values) {
        if (!values) return null;
        for (const value of values) {
          if (typeof value === "number" && Number.isFinite(value)) return value;
        }
        return null;
      }

      function finalizePlan(key, aggregate, baseTotal, termMonths) {
        const labelMap = {
          full_pay: "Full Pay",
          monthly_card: "Monthly (Card)",
          monthly_eft: "Monthly (EFT)",
          monthly_invoice: "Monthly (Invoice)",
          monthly: "Monthly",
        };
        const downPayment = firstFinite(aggregate.downPayments);
        let installmentCount = firstFinite(aggregate.installmentCounts);
        if (installmentCount === null || installmentCount === undefined) {
          const fallbackCount = firstFinite(aggregate.scheduleCounts);
          if (fallbackCount !== null && fallbackCount !== undefined) {
            installmentCount = fallbackCount;
          }
        }
        let installmentAmount = firstFinite(aggregate.installmentAmounts);
        const scheduleSum = firstFinite(aggregate.scheduleSums);
        const totalPremium = firstFinite(aggregate.totals);
        if (installmentAmount === null && scheduleSum !== null && installmentCount) {
          installmentAmount = scheduleSum / installmentCount;
        }

        let effectiveTotal = null;
        if (scheduleSum !== null || installmentAmount !== null) {
          const sum =
            (downPayment !== null ? downPayment : 0) +
            (scheduleSum !== null
              ? scheduleSum
              : installmentAmount !== null && installmentCount
              ? installmentAmount * installmentCount
              : 0);
          if (sum > 0) effectiveTotal = sum;
        }
        if (effectiveTotal === null && totalPremium !== null) {
          effectiveTotal = totalPremium;
        }
        if (effectiveTotal === null && downPayment !== null) {
          effectiveTotal = downPayment;
        }

        const installmentFees =
          effectiveTotal !== null && baseTotal !== null
            ? Math.max(0, Number((effectiveTotal - baseTotal).toFixed(2)))
            : null;

        const averageMonthly =
          effectiveTotal !== null && termMonths
            ? effectiveTotal / termMonths
            : null;

        const rawLabel = aggregate.rawLabels.length ? aggregate.rawLabels[0] : null;

        return {
          key,
          displayLabel: labelMap[key] || rawLabel || "Payment plan",
          rawLabels: aggregate.rawLabels.slice(),
          downPayment,
          installmentAmount,
          installmentCount,
          effectiveTotal,
          installmentFees,
          averageMonthly,
          frequency: aggregate.frequencies.length ? aggregate.frequencies[0] : null,
        };
      }
      function aggregateRatePrograms(rateResults) {
        const entries = new Map();
        const seen = new WeakSet();

        function ensureEntry(key, seed) {
          if (!entries.has(key)) {
            entries.set(key, {
              key,
              carrierName: seed.carrierName,
              programName: seed.programName,
              termLabel: seed.termLabel,
              totals: [],
              termMonths: new Set(),
              policyFees: new Set(),
              coverage: {
                bi: new Set(),
                pd: new Set(),
                um: new Set(),
                comp: new Set(),
                collision: new Set(),
              },
              costBreakdown: {
                bi: new Set(),
                pd: new Set(),
                um: new Set(),
              },
              addOns: new Map(),
              mileage: new Set(),
              warnings: new Set(),
              plans: new Map(),
            });
          }
          return entries.get(key);
        }

        function addPlan(entry, plan) {
          if (!plan || !plan.key) return;
          if (!entry.plans.has(plan.key)) {
            entry.plans.set(plan.key, {
              rawLabels: [],
              downPayments: [],
              installmentAmounts: [],
              installmentCounts: [],
              scheduleSums: [],
              scheduleCounts: [],
              totals: [],
              frequencies: [],
            });
          }
          const aggregate = entry.plans.get(plan.key);
          if (plan.label) aggregate.rawLabels.push(plan.label);
          if (plan.downPayment !== null) aggregate.downPayments.push(plan.downPayment);
          if (plan.installmentAmount !== null) aggregate.installmentAmounts.push(plan.installmentAmount);
          if (plan.installmentCount !== null) aggregate.installmentCounts.push(plan.installmentCount);
          if (plan.scheduleSum !== null) aggregate.scheduleSums.push(plan.scheduleSum);
          if (plan.scheduleCount !== null) aggregate.scheduleCounts.push(plan.scheduleCount);
          if (plan.totalPremium !== null) aggregate.totals.push(plan.totalPremium);
          if (plan.frequency) aggregate.frequencies.push(plan.frequency);
        }

        function addCostBreakdown(entry, key, value) {
          if (typeof value !== "number" || !Number.isFinite(value)) return;
          const lower = key.toLowerCase();
          if (lower.includes("bodily")) entry.costBreakdown.bi.add(value);
          if (lower.includes("property")) entry.costBreakdown.pd.add(value);
          if (lower.includes("uninsured")) entry.costBreakdown.um.add(value);
        }

        function visit(node, context) {
          if (!node || typeof node !== "object") return;
          if (seen.has(node)) return;
          seen.add(node);

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
          const biLimit = normalizeLimit(firstString(record, BI_KEYS));
          const pdLimit = normalizeLimit(firstString(record, PD_KEYS));
          const umLimit = normalizeLimit(firstString(record, UM_KEYS));
          const compDeductible = normalizeLimit(firstString(record, COMP_KEYS));
          const collisionDeductible = normalizeLimit(firstString(record, COLLISION_KEYS));
          const termMonths = parseTermMonths(record, termLabel);

          if (programName) {
            const key = `${carrierName || ""}::${programName}::${termLabel || ""}`;
            const entry = ensureEntry(key, { carrierName, programName, termLabel });
            if (totalPremium !== null) entry.totals.push(totalPremium);
            if (termMonths !== null) entry.termMonths.add(termMonths);
            if (policyFee !== null) entry.policyFees.add(policyFee);
            if (biLimit) entry.coverage.bi.add(biLimit);
            if (pdLimit) entry.coverage.pd.add(pdLimit);
            if (umLimit) entry.coverage.um.add(umLimit);
            if (compDeductible) entry.coverage.comp.add(compDeductible);
            if (collisionDeductible) entry.coverage.collision.add(collisionDeductible);

            const warnings = collectWarnings(record);
            warnings.forEach((warning) => entry.warnings.add(warning));
            const mileage = parseMileageAssumption(warnings);
            if (mileage !== null) entry.mileage.add(mileage);

            const addOns = extractAddOns(record);
            addOns.forEach((addOn) => {
              const current = entry.addOns.get(addOn.label) || new Set();
              current.add(addOn.amount);
              entry.addOns.set(addOn.label, current);
            });

            const plan = derivePlan(record);
            addPlan(entry, plan);
          }

          Object.entries(record).forEach(([key, value]) => {
            if (typeof value === "number") {
              addCostBreakdown(entries.get(`${carrierName || ""}::${programName || ""}::${termLabel || ""}`) || ensureEntry(`${carrierName || ""}::${programName || ""}::${termLabel || ""}`, {
                carrierName,
                programName,
                termLabel,
              }), key, value);
            } else if (value && typeof value === "object") {
              visit(value, {
                carrierName,
                programName,
                termLabel,
              });
            }
          });
        }

        visit(rateResults, {});

        const products = [];
        for (const entry of entries.values()) {
          if (!entry.programName) continue;
          const baseTotal = entry.totals.length
            ? entry.totals.reduce((min, value) => Math.min(min, value), Infinity)
            : null;
          const termMonths = entry.termMonths.size
            ? [...entry.termMonths][0]
            : null;

          const plans = {};
          const order = [];
          for (const planKey of PLAN_SORT_ORDER) {
            const aggregate = entry.plans.get(planKey);
            if (!aggregate) continue;
            const finalized = finalizePlan(planKey, aggregate, baseTotal, termMonths);
            plans[planKey] = finalized;
            order.push(planKey);
          }
          for (const [planKey, aggregate] of entry.plans.entries()) {
            if (plans[planKey]) continue;
            const finalized = finalizePlan(planKey, aggregate, baseTotal, termMonths);
            plans[planKey] = finalized;
            order.push(planKey);
          }

          const recommended = order.find((key) => key.startsWith("monthly")) || order[0] || null;

          const addOns = [];
          entry.addOns.forEach((amounts, label) => {
            const values = [...amounts];
            if (!values.length) return;
            addOns.push({ label, amount: values[0] });
          });

          const mileageAssumption = entry.mileage.size ? [...entry.mileage][0] : null;

          const coverage = {
            bi: entry.coverage.bi.size ? [...entry.coverage.bi][0] : null,
            pd: entry.coverage.pd.size ? [...entry.coverage.pd][0] : null,
            um: entry.coverage.um.size ? [...entry.coverage.um][0] : null,
            comp: entry.coverage.comp.size ? [...entry.coverage.comp][0] : null,
            collision: entry.coverage.collision.size ? [...entry.coverage.collision][0] : null,
          };

          const costBreakdown = {
            bi: entry.costBreakdown.bi.size ? [...entry.costBreakdown.bi][0] : null,
            pd: entry.costBreakdown.pd.size ? [...entry.costBreakdown.pd][0] : null,
            um: entry.costBreakdown.um.size ? [...entry.costBreakdown.um][0] : null,
          };

          const bestPlanKey = order.reduce((current, key) => {
            if (!plans[key]) return current;
            if (!current) return key;
            const currentPlan = plans[current];
            const nextPlan = plans[key];
            const currentTotal =
              currentPlan.effectiveTotal !== null && currentPlan.effectiveTotal !== undefined
                ? currentPlan.effectiveTotal
                : Number.POSITIVE_INFINITY;
            const nextTotal =
              nextPlan.effectiveTotal !== null && nextPlan.effectiveTotal !== undefined
                ? nextPlan.effectiveTotal
                : Number.POSITIVE_INFINITY;
            return nextTotal < currentTotal ? key : current;
          }, null);

          const lowestDownPlanKey = order.reduce((current, key) => {
            const plan = plans[key];
            if (!plan || plan.downPayment === null) return current;
            if (!current) return key;
            const currentPlan = plans[current];
            if (currentPlan.downPayment === null) return key;
            return plan.downPayment < currentPlan.downPayment ? key : current;
          }, null);

          const lowestMonthlyPlanKey = order.reduce((current, key) => {
            const plan = plans[key];
            if (!plan) return current;
            const monthlyValue =
              plan.installmentAmount !== null && plan.installmentAmount !== undefined
                ? plan.installmentAmount
                : plan.averageMonthly !== null && plan.averageMonthly !== undefined
                ? plan.averageMonthly
                : null;
            if (monthlyValue === null) return current;
            if (!current) return key;
            const currentPlan = plans[current];
            const currentValue =
              currentPlan.installmentAmount !== null && currentPlan.installmentAmount !== undefined
                ? currentPlan.installmentAmount
                : currentPlan.averageMonthly !== null && currentPlan.averageMonthly !== undefined
                ? currentPlan.averageMonthly
                : null;
            if (currentValue === null) return key;
            return monthlyValue < currentValue ? key : current;
          }, null);

          const monthlyCard = plans["monthly_card"];
          const monthlyInvoice = plans["monthly_invoice"];
          let monthlySavings = null;
          if (monthlyCard && monthlyInvoice && monthlyCard.installmentFees !== null && monthlyInvoice.installmentFees !== null) {
            const diff = monthlyInvoice.installmentFees - monthlyCard.installmentFees;
            if (diff > 0) monthlySavings = diff;
          }

          const product = {
            key: entry.key,
            carrierName: entry.carrierName,
            programName: entry.programName,
            termLabel: entry.termLabel,
            termMonths,
            baseTotal,
            policyFee: entry.policyFees.size ? [...entry.policyFees][0] : null,
            coverage,
            costBreakdown,
            addOns,
            mileageAssumption,
            warnings: [...entry.warnings],
            plans,
            planOrder: order,
            recommendedPlanKey: recommended,
            summary: {
              bestPlanKey,
              lowestDownPlanKey,
              lowestMonthlyPlanKey,
              monthlySavings,
            },
          };

          products.push(product);
        }

        products.sort((a, b) => {
          const totalA =
            a.baseTotal !== null && a.baseTotal !== undefined
              ? a.baseTotal
              : Number.POSITIVE_INFINITY;
          const totalB =
            b.baseTotal !== null && b.baseTotal !== undefined
              ? b.baseTotal
              : Number.POSITIVE_INFINITY;
          return totalA - totalB;
        });

        const shared = {
          coverage: {
            bi: null,
            pd: null,
            um: null,
          },
          policyFee: null,
          termLabel: null,
        };
        if (products.length) {
          const first = products[0];
          const allShare = (selector) =>
            products.every((product) => selector(product) === selector(first));
          if (allShare((product) => product.coverage.bi)) {
            shared.coverage.bi = first.coverage.bi;
          }
          if (allShare((product) => product.coverage.pd)) {
            shared.coverage.pd = first.coverage.pd;
          }
          if (allShare((product) => product.coverage.um)) {
            shared.coverage.um = first.coverage.um;
          }
          if (allShare((product) => product.policyFee)) {
            shared.policyFee = first.policyFee;
          }
          if (allShare((product) => product.termLabel)) {
            shared.termLabel = first.termLabel;
          }
        }

        let bestOverallKey = null;
        if (products.length) {
          bestOverallKey = products[0].key;
        }

        let bestMonthlyKey = null;
        let bestMonthlyValue = Number.POSITIVE_INFINITY;
        products.forEach((product) => {
          const key = product.summary.lowestMonthlyPlanKey;
          if (!key) return;
          const plan = product.plans[key];
          if (!plan) return;
          const value =
            plan.installmentAmount !== null && plan.installmentAmount !== undefined
              ? plan.installmentAmount
              : plan.averageMonthly !== null && plan.averageMonthly !== undefined
              ? plan.averageMonthly
              : null;
          if (value === null) return;
          if (value < bestMonthlyValue) {
            bestMonthlyValue = value;
            bestMonthlyKey = product.key;
          }
        });

        products.forEach((product) => {
          const badges = [];
          if (product.key === bestOverallKey) badges.push("Best overall price");
          if (product.key === bestMonthlyKey) badges.push("Lowest monthly");
          if (product.addOns.length) badges.push("Includes extra benefits");
          product.badges = badges;
        });

        return {
          products,
          shared,
        };
      }

      return {
        aggregateRatePrograms,
        formatCurrency,
        PLAN_SORT_ORDER,
      };
    }
    const dataModel = createDataModel();
    const testingApi = {
      aggregateRatePrograms: dataModel.aggregateRatePrograms,
      formatCurrency: dataModel.formatCurrency,
      PLAN_SORT_ORDER: dataModel.PLAN_SORT_ORDER,
    };
    if (typeof window !== "undefined") {
      window.__RATE_RESULTS_WIDGET_TESTING__ = testingApi;
    }

    if (typeof document === "undefined") {
      return;
    }

    const root = document.getElementById("insurance-rate-results-root");
    if (!root) return;

    const widget = document.createElement("div");
    widget.className = "rate-results";
    widget.innerHTML = `
      <div class="rate-results__header">
        <div class="rate-results__header-text">
          <div class="rate-results__eyebrow">Quote results</div>
          <h1 class="rate-results__title" data-role="title">Quote</h1>
          <p class="rate-results__subtitle" data-role="subtitle"></p>
          <div class="rate-results__meta" data-role="meta"></div>
        </div>
        <span class="rate-results__status is-hidden" data-role="status"></span>
      </div>
      <div class="rate-results__coverage-summary" data-role="coverage-summary">
        <div class="coverage-summary__headline">Coverage limits</div>
        <div class="coverage-summary__limits" data-role="coverage-limits"></div>
        <div class="coverage-summary__footnote">
          BI = Bodily Injury • PD = Property Damage • UM = Uninsured Motorist
        </div>
      </div>
      <div class="rate-results__view-toggle" data-role="view-toggle">
        <button class="rate-results__view-button is-active" data-view="cards">Product cards</button>
        <button class="rate-results__view-button" data-view="compare">Compare</button>
      </div>
      <div class="rate-results__cards" data-role="card-view"></div>
      <div class="rate-results__compare" data-role="compare-view"></div>
      <div class="rate-results__empty" data-role="empty">No carrier rate results are available for this quote.</div>
    `;

    root.appendChild(widget);

    const titleEl = widget.querySelector('[data-role="title"]');
    const subtitleEl = widget.querySelector('[data-role="subtitle"]');
    const metaEl = widget.querySelector('[data-role="meta"]');
    const statusEl = widget.querySelector('[data-role="status"]');
    const coverageSummaryEl = widget.querySelector('[data-role="coverage-summary"]');
    const coverageLimitsEl = widget.querySelector('[data-role="coverage-limits"]');
    const toggleEl = widget.querySelector('[data-role="view-toggle"]');
    const toggleButtons = Array.from(toggleEl.querySelectorAll(".rate-results__view-button"));
    const cardsEl = widget.querySelector('[data-role="card-view"]');
    const compareEl = widget.querySelector('[data-role="compare-view"]');
    const emptyEl = widget.querySelector('[data-role="empty"]');

    const state = {
      view: "cards",
      selectedPlans: new Map(),
      products: [],
      shared: null,
    };

    function setView(view) {
      state.view = view;
      toggleButtons.forEach((button) => {
        button.classList.toggle("is-active", button.dataset.view === view);
      });
      if (view === "cards") {
        cardsEl.style.display = "grid";
        compareEl.style.display = "none";
      } else {
        cardsEl.style.display = "none";
        compareEl.style.display = "block";
      }
    }

    toggleButtons.forEach((button) => {
      button.addEventListener("click", () => {
        if (button.dataset.view === state.view) return;
        setView(button.dataset.view);
      });
    });
    function renderCoverage(shared) {
      if (!shared || !shared.coverage) {
        coverageSummaryEl.style.display = "none";
        coverageLimitsEl.innerHTML = "";
        return;
      }

      coverageLimitsEl.innerHTML = "";
      const entries = [];
      if (shared.coverage.bi) entries.push({ label: "BI", value: shared.coverage.bi });
      if (shared.coverage.pd) entries.push({ label: "PD", value: shared.coverage.pd });
      if (shared.coverage.um) entries.push({ label: "UM", value: shared.coverage.um });

      if (!entries.length) {
        coverageSummaryEl.style.display = "none";
        return;
      }

      coverageSummaryEl.style.display = "flex";
      entries.forEach((entry) => {
        const span = document.createElement("span");
        span.textContent = `${entry.label} ${entry.value}`;
        coverageLimitsEl.appendChild(span);
      });
    }

    function planSummaryLines(plan) {
      const lines = [];
      if (!plan) return lines;
      if (plan.downPayment !== null && plan.installmentCount) {
        lines.push(`${dataModel.formatCurrency(plan.downPayment) || "--"} down`);
      } else if (plan.downPayment !== null && !plan.installmentCount) {
        lines.push(`Pay ${dataModel.formatCurrency(plan.downPayment) || "--"} today`);
      }
      if (plan.installmentAmount !== null && plan.installmentCount) {
        lines.push(`${dataModel.formatCurrency(plan.installmentAmount) || "--"} × ${plan.installmentCount}`);
      }
      if (plan.averageMonthly !== null && !plan.installmentAmount) {
        lines.push(`Avg monthly ${dataModel.formatCurrency(plan.averageMonthly) || "--"}`);
      }
      if (plan.frequency) {
        lines.push(plan.frequency);
      }
      return lines.filter(Boolean);
    }

    function updatePlanSummary(container, product, planKey) {
      const plan = product.plans[planKey];
      container.innerHTML = "";
      if (!plan) {
        container.textContent = "Plan details unavailable.";
        return;
      }

      const title = document.createElement("strong");
      title.textContent = plan.displayLabel;
      container.appendChild(title);

      const lines = planSummaryLines(plan);
      if (lines.length) {
        const detail = document.createElement("div");
        detail.textContent = lines.join(" · ");
        container.appendChild(detail);
      }

      if (plan.installmentFees !== null && plan.installmentFees > 0) {
        const fees = document.createElement("div");
        fees.textContent = `Includes ${dataModel.formatCurrency(plan.installmentFees) || "--"} in installment fees.`;
        container.appendChild(fees);
      }

      if (plan.averageMonthly !== null && plan.installmentAmount !== null) {
        const avg = document.createElement("div");
        avg.textContent = `All-in average ≈ ${dataModel.formatCurrency(plan.averageMonthly) || "--"}/mo`;
        container.appendChild(avg);
      }
    }
    function createDetailsList(product) {
      const list = document.createElement("ul");
      list.className = "product-card__details-list";

      const items = [];
      if (product.policyFee !== null) {
        items.push(`Required carrier fee ${dataModel.formatCurrency(product.policyFee) || "--"}`);
      }
      product.addOns.forEach((addOn) => {
        const amount = dataModel.formatCurrency(addOn.amount) || "--";
        items.push(`Includes ${addOn.label} (+${amount})`);
      });
      if (product.mileageAssumption !== null) {
        items.push(`Assumes ${product.mileageAssumption.toLocaleString()} mi/yr`);
      }
      const monthlyCard = product.plans["monthly_card"];
      const monthlyInvoice = product.plans["monthly_invoice"];
      if (monthlyCard || monthlyInvoice) {
        const fees = [];
        if (monthlyCard && monthlyCard.installmentFees !== null) {
          fees.push(`Card/EFT fees ${dataModel.formatCurrency(monthlyCard.installmentFees) || "--"}`);
        }
        if (monthlyInvoice && monthlyInvoice.installmentFees !== null) {
          fees.push(`Invoice fees ${dataModel.formatCurrency(monthlyInvoice.installmentFees) || "--"}`);
        }
        if (fees.length) {
          items.push(`Monthly fees: ${fees.join(" • ")}`);
        }
      }
      if (product.costBreakdown.bi || product.costBreakdown.pd || product.costBreakdown.um) {
        const parts = [];
        if (product.costBreakdown.bi !== null) {
          parts.push(`BI ${dataModel.formatCurrency(product.costBreakdown.bi) || "--"}`);
        }
        if (product.costBreakdown.pd !== null) {
          parts.push(`PD ${dataModel.formatCurrency(product.costBreakdown.pd) || "--"}`);
        }
        if (product.costBreakdown.um !== null) {
          parts.push(`UM ${dataModel.formatCurrency(product.costBreakdown.um) || "--"}`);
        }
        if (parts.length) {
          items.push(`Cost breakdown: ${parts.join(" • ")}`);
        }
      }

      if (!items.length) {
        const placeholder = document.createElement("li");
        placeholder.textContent = "No additional price factors noted.";
        list.appendChild(placeholder);
        return list;
      }

      items.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        list.appendChild(li);
      });
      return list;
    }

    function renderProductCards(products, shared) {
      cardsEl.innerHTML = "";
      state.selectedPlans.clear();

      products.forEach((product) => {
        const card = document.createElement("article");
        card.className = "product-card";

        const header = document.createElement("div");
        header.className = "product-card__header";

        const title = document.createElement("h2");
        title.className = "product-card__name";
        title.textContent = product.programName || "Carrier program";
        header.appendChild(title);

        if (product.badges && product.badges.length) {
          const badges = document.createElement("div");
          badges.className = "product-card__badges";
          product.badges.forEach((badge) => {
            const badgeEl = document.createElement("span");
            badgeEl.className = "badge";
            badgeEl.textContent = badge;
            badges.appendChild(badgeEl);
          });
          header.appendChild(badges);
        }

        card.appendChild(header);

        const headline = document.createElement("p");
        headline.className = "product-card__headline";
        const sharedTermLabel = shared && shared.termLabel ? shared.termLabel : null;
        const termLabel = product.termLabel || sharedTermLabel || "term";
        const totalText = product.baseTotal !== null
          ? `${dataModel.formatCurrency(product.baseTotal) || "--"} for ${termLabel}`
          : `Total premium unavailable`;
        headline.innerHTML = `<strong>${totalText}</strong>`;
        card.appendChild(headline);

        const planToggle = document.createElement("div");
        planToggle.className = "product-card__plan-toggle";
        const planSummary = document.createElement("div");
        planSummary.className = "product-card__plan-summary";

        const planOrder = product.planOrder.length ? product.planOrder : Object.keys(product.plans);
        const selectedKey = product.recommendedPlanKey || planOrder[0] || null;
        if (selectedKey) {
          state.selectedPlans.set(product.key, selectedKey);
        }

        planOrder.forEach((planKey) => {
          const plan = product.plans[planKey];
          if (!plan) return;
          const button = document.createElement("button");
          button.className = "product-card__plan-button";
          if (planKey === selectedKey) button.classList.add("is-active");
          button.type = "button";
          button.textContent = plan.displayLabel;
          button.addEventListener("click", () => {
            if (state.selectedPlans.get(product.key) === planKey) return;
            state.selectedPlans.set(product.key, planKey);
            planToggle.querySelectorAll(".product-card__plan-button").forEach((btn) => {
              btn.classList.toggle("is-active", btn === button);
            });
            updatePlanSummary(planSummary, product, planKey);
          });
          planToggle.appendChild(button);
        });

        card.appendChild(planToggle);
        updatePlanSummary(planSummary, product, selectedKey);
        card.appendChild(planSummary);

        if (product.summary.monthlySavings) {
          const callout = document.createElement("div");
          callout.className = "product-card__callout";
          callout.textContent = `Paying by Card/EFT saves ${dataModel.formatCurrency(product.summary.monthlySavings) || "--"} vs Invoice.`;
          card.appendChild(callout);
        }

        const details = document.createElement("div");
        details.className = "product-card__details";
        const detailsTitle = document.createElement("div");
        detailsTitle.className = "product-card__details-title";
        detailsTitle.textContent = "What affects this price";
        details.appendChild(detailsTitle);
        details.appendChild(createDetailsList(product));
        card.appendChild(details);

        const coverage = document.createElement("div");
        coverage.className = "product-card__coverage";
        const coverageItems = [
          { label: "Injuries you cause", value: product.coverage.bi ? `${product.coverage.bi}` : "--" },
          { label: "Property damage", value: product.coverage.pd ? `${product.coverage.pd}` : "--" },
          { label: "Uninsured motorist", value: product.coverage.um ? `${product.coverage.um}` : "--" },
        ];
        coverageItems.forEach((item) => {
          const row = document.createElement("div");
          row.className = "product-card__coverage-item";
          const label = document.createElement("span");
          label.className = "product-card__coverage-label";
          label.textContent = item.label;
          const value = document.createElement("span");
          value.textContent = item.value;
          row.appendChild(label);
          row.appendChild(value);
          coverage.appendChild(row);
        });
        card.appendChild(coverage);

        const cta = document.createElement("button");
        cta.className = "product-card__cta";
        cta.type = "button";
        cta.textContent = "Select this product";
        card.appendChild(cta);

        cardsEl.appendChild(card);
      });
    }
    function renderCompareTable(products) {
      compareEl.innerHTML = "";
      if (!products.length) return;

      const table = document.createElement("table");
      table.className = "compare-table";
      table.innerHTML = `
        <thead>
          <tr>
            <th>Product</th>
            <th>Best total (term)</th>
            <th>Lowest upfront</th>
            <th>Typical monthly</th>
            <th>Installment fees</th>
          </tr>
        </thead>
      `;
      const tbody = document.createElement("tbody");

      products.forEach((product) => {
        const bestPlan = product.summary.bestPlanKey ? product.plans[product.summary.bestPlanKey] : null;
        const lowestDownPlan = product.summary.lowestDownPlanKey ? product.plans[product.summary.lowestDownPlanKey] : null;
        const monthlyPlan = product.summary.lowestMonthlyPlanKey ? product.plans[product.summary.lowestMonthlyPlanKey] : null;

        const row = document.createElement("tr");

        const productCell = document.createElement("td");
        const productInfo = document.createElement("div");
        productInfo.className = "compare-table__product";
        const name = document.createElement("strong");
        name.textContent = product.programName || "Program";
        productInfo.appendChild(name);
        if (product.badges.length) {
          const badges = document.createElement("div");
          badges.className = "compare-table__badges";
          product.badges.forEach((badge) => {
            const badgeEl = document.createElement("span");
            badgeEl.className = "badge";
            badgeEl.textContent = badge;
            badges.appendChild(badgeEl);
          });
          productInfo.appendChild(badges);
        }
        if (product.addOns.length) {
          const note = document.createElement("div");
          note.className = "compare-table__note";
          note.textContent = product.addOns.map((addOn) => `${addOn.label} (+${dataModel.formatCurrency(addOn.amount) || "--"})`).join(" • ");
          productInfo.appendChild(note);
        }
        productCell.appendChild(productInfo);
        row.appendChild(productCell);

        const bestCell = document.createElement("td");
        if (bestPlan) {
          const amount = document.createElement("div");
          amount.innerHTML = `<strong>${dataModel.formatCurrency(bestPlan.effectiveTotal) || "--"}</strong>`;
          bestCell.appendChild(amount);
          const note = document.createElement("div");
          note.className = "compare-table__note";
          const sharedTerm = state.shared && state.shared.termLabel ? state.shared.termLabel : null;
          const termLabel = product.termLabel || sharedTerm || "term";
          note.textContent = `${bestPlan.displayLabel} • ${termLabel}`;
          bestCell.appendChild(note);
        } else {
          bestCell.textContent = "--";
        }
        row.appendChild(bestCell);

        const downCell = document.createElement("td");
        if (lowestDownPlan && lowestDownPlan.downPayment !== null) {
          const amount = dataModel.formatCurrency(lowestDownPlan.downPayment) || "--";
          downCell.innerHTML = `<strong>${amount}</strong>`;
          const note = document.createElement("div");
          note.className = "compare-table__note";
          note.textContent = lowestDownPlan.displayLabel;
          downCell.appendChild(note);
        } else {
          downCell.textContent = "--";
        }
        row.appendChild(downCell);

        const monthlyCell = document.createElement("td");
        if (monthlyPlan) {
          const monthlyAmount =
            monthlyPlan.installmentAmount !== null && monthlyPlan.installmentAmount !== undefined
              ? monthlyPlan.installmentAmount
              : monthlyPlan.averageMonthly !== null && monthlyPlan.averageMonthly !== undefined
              ? monthlyPlan.averageMonthly
              : null;
          monthlyCell.innerHTML = `<strong>${dataModel.formatCurrency(monthlyAmount) || "--"}</strong>`;
          const note = document.createElement("div");
          note.className = "compare-table__note";
          if (monthlyPlan.installmentAmount !== null && monthlyPlan.installmentCount) {
            note.textContent = `${monthlyPlan.displayLabel} • ${monthlyPlan.installmentCount} payments`;
          } else {
            note.textContent = `${monthlyPlan.displayLabel}`;
          }
          monthlyCell.appendChild(note);
        } else {
          monthlyCell.textContent = "--";
        }
        row.appendChild(monthlyCell);

        const feesCell = document.createElement("td");
        if (monthlyPlan && monthlyPlan.installmentFees !== null) {
          const amount = dataModel.formatCurrency(monthlyPlan.installmentFees) || "--";
          feesCell.innerHTML = `<strong>${amount}</strong>`;
          if (product.summary.monthlySavings) {
            const note = document.createElement("div");
            note.className = "compare-table__note";
            note.textContent = `Card/EFT saves ${dataModel.formatCurrency(product.summary.monthlySavings) || "--"} vs Invoice`;
            feesCell.appendChild(note);
          }
        } else {
          feesCell.textContent = "--";
        }
        row.appendChild(feesCell);

        tbody.appendChild(row);
      });

      table.appendChild(tbody);
      compareEl.appendChild(table);
    }

    function renderMeta(products, shared, identifier) {
      metaEl.innerHTML = "";
      const chips = [];
      if (identifier) chips.push(`Quote ${identifier}`);
      if (shared && shared.termLabel) chips.push(shared.termLabel);
      if (products.length) chips.push(`${products.length} product${products.length === 1 ? "" : "s"}`);
      const planCount = products.reduce((total, product) => total + Object.keys(product.plans).length, 0);
      if (planCount) chips.push(`${planCount} payment plans`);
      chips.forEach((chip) => {
        const span = document.createElement("span");
        span.className = "rate-results__meta-chip";
        span.textContent = chip;
        metaEl.appendChild(span);
      });
    }
    function renderProducts(products, shared, identifier) {
      state.products = products;
      state.shared = shared;

      if (!products.length) {
        cardsEl.innerHTML = "";
        compareEl.innerHTML = "";
        emptyEl.classList.add("is-visible");
        setView("cards");
        renderCoverage(shared);
        renderMeta(products, shared, identifier);
        subtitleEl.textContent = "We could not parse carrier premiums from the response.";
        return;
      }

      emptyEl.classList.remove("is-visible");
      renderCoverage(shared);
      renderProductCards(products, shared);
      renderCompareTable(products);
      renderMeta(products, shared, identifier);

      const planCount = products.reduce((total, product) => total + Object.keys(product.plans).length, 0);
      subtitleEl.textContent = `Grouped ${products.length} product${products.length === 1 ? "" : "s"} with ${planCount} payment option${planCount === 1 ? "" : "s"}.`;
      setView(state.view);
    }

    function applyToolOutput(toolOutput) {
      const identifier =
        toolOutput && typeof toolOutput.identifier === "string"
          ? toolOutput.identifier.trim()
          : null;
      titleEl.textContent = identifier ? `Quote results — ${identifier}` : "Quote results";

      let statusCode = null;
      if (toolOutput && typeof toolOutput.status === "number") {
        statusCode = toolOutput.status;
      } else if (
        toolOutput &&
        typeof toolOutput.rate_results_status === "number"
      ) {
        statusCode = toolOutput.rate_results_status;
      }

      if (statusCode !== null) {
        statusEl.textContent = `Status ${statusCode}`;
        statusEl.classList.toggle("is-error", statusCode >= 300);
        statusEl.classList.remove("is-hidden");
      } else {
        statusEl.textContent = "";
        statusEl.classList.add("is-hidden");
      }

      const rateResults = toolOutput ? toolOutput.rate_results : null;
      const aggregated = dataModel.aggregateRatePrograms(rateResults || {});
      renderProducts(aggregated.products || [], aggregated.shared || null, identifier);
    }

    function hydrate(globals) {
      if (!globals || typeof globals !== "object") return;
      if (globals.toolOutput) {
        applyToolOutput(globals.toolOutput);
      }
    }

    const initialGlobals =
      typeof window !== "undefined" && window.openai ? window.openai : {};
    hydrate(initialGlobals);

    window.addEventListener("openai:set_globals", (event) => {
      const detail = event.detail;
      if (!detail || !detail.globals) return;
      hydrate(detail.globals);
    });
  })();
</script>
""".strip()
