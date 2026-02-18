"""Wizard widget HTML template for multi-step insurance application form."""

INSURANCE_WIZARD_WIDGET_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Insurance Application Wizard</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }

        .wizard-container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 32px;
        }

        .wizard-header {
            text-align: center;
            margin-bottom: 32px;
        }

        .wizard-title {
            font-size: 24px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 8px;
        }

        .wizard-description {
            font-size: 14px;
            color: #666;
        }

        .stepper {
            display: flex;
            justify-content: space-between;
            margin-bottom: 40px;
            position: relative;
        }

        .stepper::before {
            content: '';
            position: absolute;
            top: 20px;
            left: 0;
            right: 0;
            height: 2px;
            background: #e5e7eb;
            z-index: 0;
        }

        .step {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            z-index: 1;
        }

        .step-number {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #e5e7eb;
            color: #9ca3af;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            margin-bottom: 8px;
            transition: all 0.3s ease;
        }

        .step.active .step-number {
            background: #3b82f6;
            color: white;
        }

        .step.completed .step-number {
            background: #10b981;
            color: white;
        }

        .step-label {
            font-size: 12px;
            color: #6b7280;
            text-align: center;
        }

        .step.active .step-label {
            color: #3b82f6;
            font-weight: 500;
        }

        .wizard-content {
            min-height: 300px;
            margin-bottom: 32px;
        }

        .wizard-loading {
            text-align: center;
            padding: 60px 20px;
            color: #6b7280;
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #e5e7eb;
            border-top-color: #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 16px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .wizard-actions {
            display: flex;
            justify-content: space-between;
            gap: 12px;
        }

        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-secondary {
            background: #f3f4f6;
            color: #374151;
        }

        .btn-secondary:hover {
            background: #e5e7eb;
        }

        .btn-primary {
            background: #3b82f6;
            color: white;
        }

        .btn-primary:hover {
            background: #2563eb;
        }

        .btn-primary:disabled {
            background: #93c5fd;
            cursor: not-allowed;
        }

        .error-message {
            background: #fef2f2;
            border: 1px solid #fecaca;
            color: #991b1b;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="wizard-container">
        <div class="wizard-header">
            <h1 class="wizard-title">Complete Your Insurance Application</h1>
            <p class="wizard-description">We'll guide you through 5 quick steps to get your personalized quote</p>
        </div>

        <div class="stepper">
            <div class="step active">
                <div class="step-number">1</div>
                <div class="step-label">Policy Setup</div>
            </div>
            <div class="step">
                <div class="step-number">2</div>
                <div class="step-label">Customer Info</div>
            </div>
            <div class="step">
                <div class="step-number">3</div>
                <div class="step-label">Vehicle</div>
            </div>
            <div class="step">
                <div class="step-number">4</div>
                <div class="step-label">Driver</div>
            </div>
            <div class="step">
                <div class="step-number">5</div>
                <div class="step-label">Review</div>
            </div>
        </div>

        <div class="wizard-content">
            <div class="wizard-loading">
                <div class="spinner"></div>
                <p>Loading wizard configuration...</p>
            </div>
        </div>

        <div class="wizard-actions">
            <button class="btn btn-secondary" id="prevBtn" style="display:none;">Previous</button>
            <button class="btn btn-primary" id="nextBtn">Next</button>
        </div>
    </div>

    <script>
        // Wizard state
        let wizardConfig = null;
        let fieldsConfig = null;
        let currentStep = 1;
        let formData = {};

        // Initialize wizard
        async function initWizard() {
            try {
                // Try to get config from structured content (passed from backend)
                const structuredContent = window.structuredContent || window.parent?.structuredContent || {};

                if (structuredContent.wizard_config && structuredContent.fields_config) {
                    // Config was passed from backend
                    console.log('Using config from structured content');
                    wizardConfig = structuredContent.wizard_config;
                    fieldsConfig = structuredContent.fields_config;

                    // Pre-fill data if available
                    if (structuredContent.pre_fill_data) {
                        formData = { ...structuredContent.pre_fill_data };
                    }
                } else {
                    // Fallback: fetch configuration from API
                    console.log('Fetching config from API');

                    // Try multiple server URLs
                    const serverUrls = [
                        'http://localhost:8000/api/wizard-config',
                        '/api/wizard-config',
                        window.location.origin + '/api/wizard-config'
                    ];

                    let configLoaded = false;
                    let lastError = null;

                    for (const url of serverUrls) {
                        try {
                            console.log('Trying URL:', url);
                            const response = await fetch(url);
                            if (response.ok) {
                                const config = await response.json();
                                wizardConfig = config.wizard;
                                fieldsConfig = config.fields;
                                configLoaded = true;
                                console.log('Config loaded from:', url);
                                break;
                            }
                        } catch (err) {
                            lastError = err;
                            console.warn('Failed to fetch from', url, ':', err.message);
                        }
                    }

                    if (!configLoaded) {
                        throw new Error('Failed to load wizard configuration from any source. Last error: ' + (lastError?.message || 'Unknown'));
                    }
                }

                // Render first step
                renderStep(1);
            } catch (error) {
                console.error('Wizard initialization error:', error);
                showError('Failed to load wizard: ' + error.message);
            }
        }

        function renderStep(stepId) {
            const step = wizardConfig.steps.find(s => s.id === stepId);
            if (!step) {
                showError('Invalid step');
                return;
            }

            currentStep = stepId;
            updateStepper();

            const content = document.querySelector('.wizard-content');

            if (step.is_review) {
                // Render review step
                content.innerHTML = renderReviewStep(step);
            } else {
                // Render collection step
                content.innerHTML = renderCollectionStep(step);
            }

            updateButtons();
        }

        function renderCollectionStep(step) {
            let html = `<h2 style="font-size: 20px; font-weight: 600; margin-bottom: 24px;">${step.title}</h2>`;

            step.sections.forEach(section => {
                html += `<div style="margin-bottom: 32px;">`;
                html += `<h3 style="font-size: 16px; font-weight: 500; margin-bottom: 16px; color: #374151;">${section.title}</h3>`;
                html += `<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">`;

                section.fields.forEach(fieldConfig => {
                    const fieldDef = fieldsConfig[fieldConfig.name];
                    if (!fieldDef) return;

                    const fullWidth = fieldConfig.fullWidth ? 'grid-column: 1 / -1;' : '';
                    const required = fieldConfig.required ? '<span style="color: #dc2626;">*</span>' : '';
                    const value = formData[fieldConfig.name] || '';

                    html += `<div style="${fullWidth}">`;
                    html += `<label style="display: block; font-size: 14px; font-weight: 500; margin-bottom: 6px; color: #374151;">`;
                    html += `${fieldDef.prompt_text} ${required}`;
                    html += `</label>`;
                    html += renderField(fieldDef, fieldConfig, value);
                    html += `</div>`;
                });

                html += `</div></div>`;
            });

            return html;
        }

        function renderField(fieldDef, fieldConfig, value) {
            const commonStyle = 'width: 100%; padding: 10px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px;';
            const placeholder = fieldDef.example ? `placeholder="${fieldDef.example}"` : '';

            if (fieldDef.enum_values && fieldDef.enum_values.length > 0) {
                // Select field
                let html = `<select name="${fieldDef.name}" style="${commonStyle}">`;
                html += `<option value="">Select ${fieldDef.prompt_text}</option>`;
                fieldDef.enum_values.forEach(opt => {
                    const selected = value === opt ? 'selected' : '';
                    html += `<option value="${opt}" ${selected}>${opt}</option>`;
                });
                html += `</select>`;
                return html;
            } else if (fieldDef.field_type === 'boolean') {
                // Checkbox
                const checked = value === true ? 'checked' : '';
                return `<input type="checkbox" name="${fieldDef.name}" ${checked} style="width: 20px; height: 20px;">`;
            } else if (fieldDef.field_type === 'date') {
                // Date input
                return `<input type="date" name="${fieldDef.name}" value="${value}" style="${commonStyle}">`;
            } else if (fieldDef.field_type === 'integer') {
                // Number input
                return `<input type="number" name="${fieldDef.name}" value="${value}" ${placeholder} style="${commonStyle}">`;
            } else {
                // Text input
                return `<input type="text" name="${fieldDef.name}" value="${value}" ${placeholder} style="${commonStyle}">`;
            }
        }

        function renderReviewStep(step) {
            let html = `<h2 style="font-size: 20px; font-weight: 600; margin-bottom: 24px;">${step.title}</h2>`;

            step.review_sections.forEach(section => {
                html += `<div style="margin-bottom: 24px; padding: 16px; background: #f9fafb; border-radius: 8px;">`;
                html += `<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">`;
                html += `<h3 style="font-size: 16px; font-weight: 500; color: #374151;">${section.title}</h3>`;
                html += `<button onclick="editStep(${section.edit_step})" style="padding: 6px 12px; background: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px;">Edit</button>`;
                html += `</div>`;

                html += `<div style="display: grid; gap: 8px;">`;
                section.fields.forEach(fieldName => {
                    const fieldDef = fieldsConfig[fieldName];
                    const value = formData[fieldName] || '-';
                    if (fieldDef) {
                        html += `<div style="display: flex; justify-content: space-between; font-size: 14px;">`;
                        html += `<span style="color: #6b7280;">${fieldDef.prompt_text}:</span>`;
                        html += `<span style="font-weight: 500;">${value}</span>`;
                        html += `</div>`;
                    }
                });
                html += `</div></div>`;
            });

            return html;
        }

        function updateStepper() {
            const steps = document.querySelectorAll('.step');
            steps.forEach((stepEl, index) => {
                const stepNum = index + 1;
                stepEl.classList.remove('active', 'completed');

                if (stepNum < currentStep) {
                    stepEl.classList.add('completed');
                } else if (stepNum === currentStep) {
                    stepEl.classList.add('active');
                }
            });
        }

        function updateButtons() {
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');

            prevBtn.style.display = currentStep > 1 ? 'block' : 'none';

            if (currentStep === wizardConfig.steps.length) {
                nextBtn.textContent = 'Submit';
            } else {
                nextBtn.textContent = 'Next';
            }
        }

        function collectFormData() {
            const inputs = document.querySelectorAll('input, select');
            inputs.forEach(input => {
                if (input.type === 'checkbox') {
                    formData[input.name] = input.checked;
                } else {
                    formData[input.name] = input.value;
                }
            });
        }

        function validateCurrentStep() {
            const step = wizardConfig.steps.find(s => s.id === currentStep);
            if (!step || step.is_review) return true;

            const requiredFields = [];
            step.sections.forEach(section => {
                section.fields.forEach(fieldConfig => {
                    if (fieldConfig.required) {
                        requiredFields.push(fieldConfig.name);
                    }
                });
            });

            const missing = requiredFields.filter(name => !formData[name] || formData[name] === '');

            if (missing.length > 0) {
                showError(`Please fill in all required fields: ${missing.join(', ')}`);
                return false;
            }

            return true;
        }

        function showError(message) {
            const content = document.querySelector('.wizard-content');
            const existing = content.querySelector('.error-message');
            if (existing) existing.remove();

            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = message;
            content.insertBefore(errorDiv, content.firstChild);
        }

        function editStep(stepId) {
            renderStep(stepId);
        }

        // Button handlers
        document.getElementById('prevBtn').addEventListener('click', () => {
            collectFormData();
            if (currentStep > 1) {
                renderStep(currentStep - 1);
            }
        });

        document.getElementById('nextBtn').addEventListener('click', async () => {
            collectFormData();

            if (!validateCurrentStep()) {
                return;
            }

            if (currentStep < wizardConfig.steps.length) {
                renderStep(currentStep + 1);
            } else {
                // Submit wizard
                await submitWizard();
            }
        });

        async function submitWizard() {
            try {
                // This would call the backend submission handler
                // For now, just show a success message
                const content = document.querySelector('.wizard-content');
                content.innerHTML = `
                    <div style="text-align: center; padding: 60px 20px;">
                        <div style="width: 60px; height: 60px; background: #10b981; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px;">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3">
                                <polyline points="20 6 9 17 4 12"></polyline>
                            </svg>
                        </div>
                        <h2 style="font-size: 20px; font-weight: 600; margin-bottom: 8px;">Application Submitted!</h2>
                        <p style="color: #6b7280;">We're processing your insurance quote. You'll receive your detailed quote shortly.</p>
                    </div>
                `;

                document.getElementById('prevBtn').style.display = 'none';
                document.getElementById('nextBtn').style.display = 'none';
            } catch (error) {
                showError('Failed to submit application: ' + error.message);
            }
        }

        // Initialize on load
        initWizard();
    </script>
</body>
</html>
"""
