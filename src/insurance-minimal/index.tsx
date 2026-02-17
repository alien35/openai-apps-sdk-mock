import React, { useState, useEffect } from 'react';
import './styles.css';

interface FieldConfig {
  required: string[];
  conditional: Record<string, any>;
}

interface MinimalFieldsConfig {
  customer: FieldConfig;
  driver: FieldConfig;
  vehicle: FieldConfig;
  policy_coverages: FieldConfig;
  metadata: FieldConfig;
  field_descriptions: Record<string, string>;
  enums: Record<string, string[]>;
}

interface CustomerData {
  FirstName: string;
  LastName: string;
  Address: {
    Street1: string;
    City: string;
    State: string;
    ZipCode: string;
  };
  MonthsAtResidence: number;
  PriorInsuranceInformation: {
    PriorInsurance: boolean;
    PriorExpirationDate?: string;
    PriorCarrierId?: string;
    PriorLiabilityLimit?: string;
    PriorMonthsCoverage?: number;
    ReasonForNoInsurance?: string;
  };
}

interface DriverData {
  DriverId: number;
  FirstName: string;
  LastName: string;
  DateOfBirth: string;
  Gender: string;
  MaritalStatus: string;
  LicenseInformation: {
    LicenseStatus: string;
    MonthsLicensed?: number;
    StateLicensed?: string;
  };
  Attributes: {
    PropertyInsurance: boolean;
    Relation: string;
    ResidencyStatus: string;
    ResidencyType: string;
  };
}

interface VehicleData {
  VehicleId: number;
  Vin: string;
  Year: number;
  Make: string;
  Model: string;
  BodyType: string;
  UseType: string;
  AssignedDriverId: number;
  CoverageInformation: {
    CollisionDeductible: string;
    ComprehensiveDeductible: string;
    RentalLimit: string;
    TowingLimit: string;
    SafetyGlassCoverage: boolean;
  };
  PercentToWork: number;
  MilesToWork: number;
  AnnualMiles: number;
}

interface PolicyCoverages {
  LiabilityBiLimit: string;
  LiabilityPdLimit: string;
  MedPayLimit: string;
  UninsuredMotoristBiLimit: string;
  'UninsuredMotoristPd/CollisionDamageWaiver': boolean;
  AccidentalDeathLimit: string;
}

const InsuranceMinimalWidget: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [config, setConfig] = useState<MinimalFieldsConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [customer, setCustomer] = useState<CustomerData>({
    FirstName: '',
    LastName: '',
    Address: {
      Street1: '',
      City: '',
      State: 'California',
      ZipCode: '',
    },
    MonthsAtResidence: 0,
    PriorInsuranceInformation: {
      PriorInsurance: false,
    },
  });

  const [drivers, setDrivers] = useState<DriverData[]>([
    {
      DriverId: 1,
      FirstName: '',
      LastName: '',
      DateOfBirth: '',
      Gender: 'Male',
      MaritalStatus: 'Single',
      LicenseInformation: {
        LicenseStatus: 'Valid',
      },
      Attributes: {
        PropertyInsurance: false,
        Relation: 'Insured',
        ResidencyStatus: 'Own',
        ResidencyType: 'Home',
      },
    },
  ]);

  const [vehicles, setVehicles] = useState<VehicleData[]>([
    {
      VehicleId: 1,
      Vin: '',
      Year: new Date().getFullYear(),
      Make: '',
      Model: '',
      BodyType: 'Sedan',
      UseType: 'Commute',
      AssignedDriverId: 1,
      CoverageInformation: {
        CollisionDeductible: '500',
        ComprehensiveDeductible: '500',
        RentalLimit: 'None',
        TowingLimit: 'None',
        SafetyGlassCoverage: false,
      },
      PercentToWork: 50,
      MilesToWork: 10,
      AnnualMiles: 12000,
    },
  ]);

  const [policyCoverages, setPolicyCoverages] = useState<PolicyCoverages>({
    LiabilityBiLimit: '25000/50000',
    LiabilityPdLimit: '25000',
    MedPayLimit: 'None',
    UninsuredMotoristBiLimit: '25000/50000',
    'UninsuredMotoristPd/CollisionDamageWaiver': false,
    AccidentalDeathLimit: 'None',
  });

  const [effectiveDate, setEffectiveDate] = useState('');

  useEffect(() => {
    // Fetch minimal fields configuration
    fetch('/minimal-fields-config.json')
      .then((res) => res.json())
      .then((data) => {
        setConfig(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load config:', err);
        setError('Failed to load form configuration');
        setLoading(false);
      });

    // Set default effective date to 30 days from now
    const defaultDate = new Date();
    defaultDate.setDate(defaultDate.getDate() + 30);
    setEffectiveDate(defaultDate.toISOString().split('T')[0]);
  }, []);

  const validateStep = (step: number): boolean => {
    switch (step) {
      case 1:
        return Boolean(
          customer.FirstName &&
          customer.LastName &&
          customer.Address.Street1 &&
          customer.Address.City &&
          customer.Address.ZipCode &&
          customer.MonthsAtResidence > 0
        );
      case 2:
        return drivers.every(
          (d) =>
            d.FirstName &&
            d.LastName &&
            d.DateOfBirth &&
            (d.LicenseInformation.LicenseStatus !== 'Valid' ||
              (d.LicenseInformation.MonthsLicensed && d.LicenseInformation.StateLicensed))
        );
      case 3:
        return vehicles.every(
          (v) =>
            v.Vin &&
            v.Year &&
            v.Make &&
            v.Model &&
            v.AnnualMiles > 0
        );
      case 4:
        return true; // Coverages have defaults
      default:
        return true;
    }
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(prev + 1, 5));
    } else {
      alert('Please fill out all required fields');
    }
  };

  const prevStep = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const addDriver = () => {
    const newDriver: DriverData = {
      DriverId: drivers.length + 1,
      FirstName: '',
      LastName: '',
      DateOfBirth: '',
      Gender: 'Male',
      MaritalStatus: 'Single',
      LicenseInformation: {
        LicenseStatus: 'Valid',
      },
      Attributes: {
        PropertyInsurance: false,
        Relation: 'Spouse',
        ResidencyStatus: 'Own',
        ResidencyType: 'Home',
      },
    };
    setDrivers([...drivers, newDriver]);
  };

  const removeDriver = (index: number) => {
    if (drivers.length > 1) {
      setDrivers(drivers.filter((_, i) => i !== index));
    }
  };

  const addVehicle = () => {
    const newVehicle: VehicleData = {
      VehicleId: vehicles.length + 1,
      Vin: '',
      Year: new Date().getFullYear(),
      Make: '',
      Model: '',
      BodyType: 'Sedan',
      UseType: 'Commute',
      AssignedDriverId: 1,
      CoverageInformation: {
        CollisionDeductible: '500',
        ComprehensiveDeductible: '500',
        RentalLimit: 'None',
        TowingLimit: 'None',
        SafetyGlassCoverage: false,
      },
      PercentToWork: 50,
      MilesToWork: 10,
      AnnualMiles: 12000,
    };
    setVehicles([...vehicles, newVehicle]);
  };

  const removeVehicle = (index: number) => {
    if (vehicles.length > 1) {
      setVehicles(vehicles.filter((_, i) => i !== index));
    }
  };

  const handleSubmit = async () => {
    // Generate quote ID
    const identifier = `quote-${Date.now()}`;

    // Build payload
    const payload = {
      Identifier: identifier,
      EffectiveDate: `${effectiveDate}T00:00:00`,
      Customer: customer,
      RatedDrivers: drivers,
      Vehicles: vehicles,
      PolicyCoverages: policyCoverages,
    };

    console.log('Submitting minimal payload:', payload);

    // Send to assistant via message
    if (window.openai && typeof window.openai.sendFollowUpMessage === 'function') {
      const prompt = `I've collected all the insurance information. Please submit this personal auto rate request using the exact data structure below:\n\n\`\`\`json\n${JSON.stringify(payload, null, 2)}\n\`\`\`\n\nPlease call the request-personal-auto-rate tool with this data.`;

      await window.openai.sendFollowUpMessage({ prompt });
    }
  };

  if (loading) {
    return (
      <div className="insurance-minimal">
        <div className="loading">Loading form configuration...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="insurance-minimal">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="insurance-minimal">
      <div className="header">
        <h2>Get Your Auto Insurance Quote</h2>
        <p>Quick and easy - only the essentials</p>
      </div>

      <div className="progress-bar">
        {[1, 2, 3, 4, 5].map((step) => (
          <div
            key={step}
            className={`progress-step ${currentStep >= step ? 'active' : ''} ${currentStep === step ? 'current' : ''}`}
          >
            <div className="step-number">{step}</div>
            <div className="step-label">
              {step === 1 && 'Customer'}
              {step === 2 && 'Drivers'}
              {step === 3 && 'Vehicles'}
              {step === 4 && 'Coverage'}
              {step === 5 && 'Review'}
            </div>
          </div>
        ))}
      </div>

      <div className="step-content">
        {currentStep === 1 && (
          <CustomerStep
            customer={customer}
            setCustomer={setCustomer}
            config={config}
          />
        )}

        {currentStep === 2 && (
          <DriversStep
            drivers={drivers}
            setDrivers={setDrivers}
            addDriver={addDriver}
            removeDriver={removeDriver}
            config={config}
          />
        )}

        {currentStep === 3 && (
          <VehiclesStep
            vehicles={vehicles}
            setVehicles={setVehicles}
            addVehicle={addVehicle}
            removeVehicle={removeVehicle}
            drivers={drivers}
            config={config}
          />
        )}

        {currentStep === 4 && (
          <CoveragesStep
            policyCoverages={policyCoverages}
            setPolicyCoverages={setPolicyCoverages}
            effectiveDate={effectiveDate}
            setEffectiveDate={setEffectiveDate}
            config={config}
          />
        )}

        {currentStep === 5 && (
          <ReviewStep
            customer={customer}
            drivers={drivers}
            vehicles={vehicles}
            policyCoverages={policyCoverages}
            effectiveDate={effectiveDate}
          />
        )}
      </div>

      <div className="navigation">
        {currentStep > 1 && (
          <button onClick={prevStep} className="btn btn-secondary">
            Previous
          </button>
        )}

        {currentStep < 5 && (
          <button onClick={nextStep} className="btn btn-primary">
            Next
          </button>
        )}

        {currentStep === 5 && (
          <button onClick={handleSubmit} className="btn btn-success">
            Get Quote
          </button>
        )}
      </div>
    </div>
  );
};

// Customer Step Component
const CustomerStep: React.FC<{
  customer: CustomerData;
  setCustomer: React.Dispatch<React.SetStateAction<CustomerData>>;
  config: MinimalFieldsConfig | null;
}> = ({ customer, setCustomer, config }) => {
  const updateCustomer = (field: string, value: any) => {
    setCustomer((prev) => {
      if (field.includes('.')) {
        const [parent, child] = field.split('.');
        return {
          ...prev,
          [parent]: {
            ...(prev[parent as keyof CustomerData] as any),
            [child]: value,
          },
        };
      }
      return { ...prev, [field]: value };
    });
  };

  const updateAddress = (field: string, value: string) => {
    setCustomer((prev) => ({
      ...prev,
      Address: {
        ...prev.Address,
        [field]: value,
      },
    }));
  };

  const updatePriorInsurance = (field: string, value: any) => {
    setCustomer((prev) => ({
      ...prev,
      PriorInsuranceInformation: {
        ...prev.PriorInsuranceInformation,
        [field]: value,
      },
    }));
  };

  return (
    <div className="customer-step">
      <h3>About You</h3>

      <div className="form-row">
        <div className="form-group">
          <label>
            First Name <span className="required">*</span>
          </label>
          <input
            type="text"
            value={customer.FirstName}
            onChange={(e) => updateCustomer('FirstName', e.target.value)}
            placeholder="John"
          />
        </div>

        <div className="form-group">
          <label>
            Last Name <span className="required">*</span>
          </label>
          <input
            type="text"
            value={customer.LastName}
            onChange={(e) => updateCustomer('LastName', e.target.value)}
            placeholder="Doe"
          />
        </div>
      </div>

      <div className="form-group">
        <label>
          Street Address <span className="required">*</span>
        </label>
        <input
          type="text"
          value={customer.Address.Street1}
          onChange={(e) => updateAddress('Street1', e.target.value)}
          placeholder="123 Main St"
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>
            City <span className="required">*</span>
          </label>
          <input
            type="text"
            value={customer.Address.City}
            onChange={(e) => updateAddress('City', e.target.value)}
            placeholder="San Francisco"
          />
        </div>

        <div className="form-group">
          <label>
            State <span className="required">*</span>
          </label>
          <select
            value={customer.Address.State}
            onChange={(e) => updateAddress('State', e.target.value)}
          >
            <option value="California">California</option>
          </select>
        </div>

        <div className="form-group">
          <label>
            ZIP Code <span className="required">*</span>
          </label>
          <input
            type="text"
            value={customer.Address.ZipCode}
            onChange={(e) => updateAddress('ZipCode', e.target.value)}
            placeholder="94105"
            pattern="[0-9]{5}"
            maxLength={5}
          />
        </div>
      </div>

      <div className="form-group">
        <label>
          Months at Current Address <span className="required">*</span>
        </label>
        <input
          type="number"
          value={customer.MonthsAtResidence}
          onChange={(e) => updateCustomer('MonthsAtResidence', parseInt(e.target.value) || 0)}
          min="0"
          max="1200"
        />
      </div>

      <div className="form-group">
        <label>
          Do you currently have auto insurance? <span className="required">*</span>
        </label>
        <div className="radio-group">
          <label>
            <input
              type="radio"
              checked={customer.PriorInsuranceInformation.PriorInsurance === true}
              onChange={() => updatePriorInsurance('PriorInsurance', true)}
            />
            Yes
          </label>
          <label>
            <input
              type="radio"
              checked={customer.PriorInsuranceInformation.PriorInsurance === false}
              onChange={() => updatePriorInsurance('PriorInsurance', false)}
            />
            No
          </label>
        </div>
      </div>

      {customer.PriorInsuranceInformation.PriorInsurance === false && (
        <div className="form-group">
          <label>
            Reason for No Insurance <span className="required">*</span>
          </label>
          <select
            value={customer.PriorInsuranceInformation.ReasonForNoInsurance || ''}
            onChange={(e) => updatePriorInsurance('ReasonForNoInsurance', e.target.value)}
          >
            <option value="">Select reason...</option>
            {config?.enums.ReasonForNoInsurance?.map((reason) => (
              <option key={reason} value={reason}>
                {reason}
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
};

// Drivers Step Component
const DriversStep: React.FC<{
  drivers: DriverData[];
  setDrivers: React.Dispatch<React.SetStateAction<DriverData[]>>;
  addDriver: () => void;
  removeDriver: (index: number) => void;
  config: MinimalFieldsConfig | null;
}> = ({ drivers, setDrivers, addDriver, removeDriver, config }) => {
  const updateDriver = (index: number, field: string, value: any) => {
    setDrivers((prev) => {
      const updated = [...prev];
      if (field.includes('.')) {
        const [parent, child] = field.split('.');
        updated[index] = {
          ...updated[index],
          [parent]: {
            ...(updated[index][parent as keyof DriverData] as any),
            [child]: value,
          },
        };
      } else {
        updated[index] = { ...updated[index], [field]: value };
      }
      return updated;
    });
  };

  return (
    <div className="drivers-step">
      <h3>Drivers</h3>
      <p>Add all drivers who will use the vehicles</p>

      {drivers.map((driver, index) => (
        <div key={index} className="driver-card">
          <div className="card-header">
            <h4>Driver {index + 1}</h4>
            {drivers.length > 1 && (
              <button onClick={() => removeDriver(index)} className="btn-remove">
                Remove
              </button>
            )}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>
                First Name <span className="required">*</span>
              </label>
              <input
                type="text"
                value={driver.FirstName}
                onChange={(e) => updateDriver(index, 'FirstName', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>
                Last Name <span className="required">*</span>
              </label>
              <input
                type="text"
                value={driver.LastName}
                onChange={(e) => updateDriver(index, 'LastName', e.target.value)}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>
                Date of Birth <span className="required">*</span>
              </label>
              <input
                type="date"
                value={driver.DateOfBirth}
                onChange={(e) => updateDriver(index, 'DateOfBirth', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>
                Gender <span className="required">*</span>
              </label>
              <select
                value={driver.Gender}
                onChange={(e) => updateDriver(index, 'Gender', e.target.value)}
              >
                {config?.enums.Gender?.map((gender) => (
                  <option key={gender} value={gender}>
                    {gender}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>
                Marital Status <span className="required">*</span>
              </label>
              <select
                value={driver.MaritalStatus}
                onChange={(e) => updateDriver(index, 'MaritalStatus', e.target.value)}
              >
                {config?.enums.MaritalStatus?.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>
                License Status <span className="required">*</span>
              </label>
              <select
                value={driver.LicenseInformation.LicenseStatus}
                onChange={(e) =>
                  updateDriver(index, 'LicenseInformation.LicenseStatus', e.target.value)
                }
              >
                {config?.enums.LicenseStatus?.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </div>

            {driver.LicenseInformation.LicenseStatus === 'Valid' && (
              <>
                <div className="form-group">
                  <label>
                    Months Licensed <span className="required">*</span>
                  </label>
                  <input
                    type="number"
                    value={driver.LicenseInformation.MonthsLicensed || ''}
                    onChange={(e) =>
                      updateDriver(
                        index,
                        'LicenseInformation.MonthsLicensed',
                        parseInt(e.target.value) || 0
                      )
                    }
                    min="0"
                    max="1200"
                  />
                </div>

                <div className="form-group">
                  <label>
                    State Licensed <span className="required">*</span>
                  </label>
                  <input
                    type="text"
                    value={driver.LicenseInformation.StateLicensed || ''}
                    onChange={(e) =>
                      updateDriver(index, 'LicenseInformation.StateLicensed', e.target.value)
                    }
                    placeholder="CA"
                  />
                </div>
              </>
            )}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>
                Relationship to Insured <span className="required">*</span>
              </label>
              <select
                value={driver.Attributes.Relation}
                onChange={(e) => updateDriver(index, 'Attributes.Relation', e.target.value)}
              >
                {config?.enums.Relation?.map((rel) => (
                  <option key={rel} value={rel}>
                    {rel}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>
                Residency Status <span className="required">*</span>
              </label>
              <select
                value={driver.Attributes.ResidencyStatus}
                onChange={(e) => updateDriver(index, 'Attributes.ResidencyStatus', e.target.value)}
              >
                {config?.enums.ResidencyStatus?.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>
                Residence Type <span className="required">*</span>
              </label>
              <select
                value={driver.Attributes.ResidencyType}
                onChange={(e) => updateDriver(index, 'Attributes.ResidencyType', e.target.value)}
              >
                {config?.enums.ResidencyType?.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={driver.Attributes.PropertyInsurance}
                onChange={(e) =>
                  updateDriver(index, 'Attributes.PropertyInsurance', e.target.checked)
                }
              />
              I have property insurance (home or renters)
            </label>
          </div>
        </div>
      ))}

      <button onClick={addDriver} className="btn btn-secondary">
        + Add Another Driver
      </button>
    </div>
  );
};

// Vehicles Step Component (continued in next part due to length)
const VehiclesStep: React.FC<{
  vehicles: VehicleData[];
  setVehicles: React.Dispatch<React.SetStateAction<VehicleData[]>>;
  addVehicle: () => void;
  removeVehicle: (index: number) => void;
  drivers: DriverData[];
  config: MinimalFieldsConfig | null;
}> = ({ vehicles, setVehicles, addVehicle, removeVehicle, drivers, config }) => {
  const updateVehicle = (index: number, field: string, value: any) => {
    setVehicles((prev) => {
      const updated = [...prev];
      if (field.includes('.')) {
        const [parent, child] = field.split('.');
        updated[index] = {
          ...updated[index],
          [parent]: {
            ...(updated[index][parent as keyof VehicleData] as any),
            [child]: value,
          },
        };
      } else {
        updated[index] = { ...updated[index], [field]: value };
      }
      return updated;
    });
  };

  return (
    <div className="vehicles-step">
      <h3>Vehicles</h3>
      <p>Add all vehicles you want to insure</p>

      {vehicles.map((vehicle, index) => (
        <div key={index} className="vehicle-card">
          <div className="card-header">
            <h4>Vehicle {index + 1}</h4>
            {vehicles.length > 1 && (
              <button onClick={() => removeVehicle(index)} className="btn-remove">
                Remove
              </button>
            )}
          </div>

          <div className="form-group">
            <label>
              VIN <span className="required">*</span>
            </label>
            <input
              type="text"
              value={vehicle.Vin}
              onChange={(e) => updateVehicle(index, 'Vin', e.target.value.toUpperCase())}
              placeholder="1HGCM82633A123456"
              maxLength={17}
            />
            <small>17-character Vehicle Identification Number</small>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>
                Year <span className="required">*</span>
              </label>
              <input
                type="number"
                value={vehicle.Year}
                onChange={(e) => updateVehicle(index, 'Year', parseInt(e.target.value) || 0)}
                min="1900"
                max={new Date().getFullYear() + 2}
              />
            </div>

            <div className="form-group">
              <label>
                Make <span className="required">*</span>
              </label>
              <input
                type="text"
                value={vehicle.Make}
                onChange={(e) => updateVehicle(index, 'Make', e.target.value)}
                placeholder="Honda"
              />
            </div>

            <div className="form-group">
              <label>
                Model <span className="required">*</span>
              </label>
              <input
                type="text"
                value={vehicle.Model}
                onChange={(e) => updateVehicle(index, 'Model', e.target.value)}
                placeholder="Accord"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>
                Body Type <span className="required">*</span>
              </label>
              <select
                value={vehicle.BodyType}
                onChange={(e) => updateVehicle(index, 'BodyType', e.target.value)}
              >
                <option value="Sedan">Sedan</option>
                <option value="Coupe">Coupe</option>
                <option value="SUV">SUV</option>
                <option value="Truck">Truck</option>
                <option value="Van">Van</option>
                <option value="Wagon">Wagon</option>
              </select>
            </div>

            <div className="form-group">
              <label>
                Primary Use <span className="required">*</span>
              </label>
              <select
                value={vehicle.UseType}
                onChange={(e) => updateVehicle(index, 'UseType', e.target.value)}
              >
                {config?.enums.UseType?.map((use) => (
                  <option key={use} value={use}>
                    {use}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>
                Primary Driver <span className="required">*</span>
              </label>
              <select
                value={vehicle.AssignedDriverId}
                onChange={(e) =>
                  updateVehicle(index, 'AssignedDriverId', parseInt(e.target.value))
                }
              >
                {drivers.map((driver, driverIndex) => (
                  <option key={driverIndex} value={driver.DriverId}>
                    {driver.FirstName} {driver.LastName} {!driver.FirstName && `Driver ${driverIndex + 1}`}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>
                Annual Miles <span className="required">*</span>
              </label>
              <input
                type="number"
                value={vehicle.AnnualMiles}
                onChange={(e) => updateVehicle(index, 'AnnualMiles', parseInt(e.target.value) || 0)}
                min="0"
                max="100000"
              />
            </div>

            <div className="form-group">
              <label>
                Daily Commute Miles <span className="required">*</span>
              </label>
              <input
                type="number"
                value={vehicle.MilesToWork}
                onChange={(e) => updateVehicle(index, 'MilesToWork', parseInt(e.target.value) || 0)}
                min="0"
                max="999"
              />
            </div>

            <div className="form-group">
              <label>
                % Used for Work <span className="required">*</span>
              </label>
              <input
                type="number"
                value={vehicle.PercentToWork}
                onChange={(e) => updateVehicle(index, 'PercentToWork', parseInt(e.target.value) || 0)}
                min="0"
                max="100"
              />
            </div>
          </div>

          <h5>Coverage</h5>

          <div className="form-row">
            <div className="form-group">
              <label>Collision Deductible</label>
              <select
                value={vehicle.CoverageInformation.CollisionDeductible}
                onChange={(e) =>
                  updateVehicle(index, 'CoverageInformation.CollisionDeductible', e.target.value)
                }
              >
                {config?.enums.CollisionDeductible?.map((ded) => (
                  <option key={ded} value={ded}>
                    {ded === 'None' ? 'None' : `$${ded}`}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Comprehensive Deductible</label>
              <select
                value={vehicle.CoverageInformation.ComprehensiveDeductible}
                onChange={(e) =>
                  updateVehicle(index, 'CoverageInformation.ComprehensiveDeductible', e.target.value)
                }
              >
                {config?.enums.ComprehensiveDeductible?.map((ded) => (
                  <option key={ded} value={ded}>
                    {ded === 'None' ? 'None' : `$${ded}`}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Rental Coverage</label>
              <select
                value={vehicle.CoverageInformation.RentalLimit}
                onChange={(e) =>
                  updateVehicle(index, 'CoverageInformation.RentalLimit', e.target.value)
                }
              >
                {config?.enums.RentalLimit?.map((limit) => (
                  <option key={limit} value={limit}>
                    {limit === 'None' ? 'None' : `$${limit}/day`}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Towing Coverage</label>
              <select
                value={vehicle.CoverageInformation.TowingLimit}
                onChange={(e) =>
                  updateVehicle(index, 'CoverageInformation.TowingLimit', e.target.value)
                }
              >
                {config?.enums.TowingLimit?.map((limit) => (
                  <option key={limit} value={limit}>
                    {limit === 'None' ? 'None' : `$${limit}`}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={vehicle.CoverageInformation.SafetyGlassCoverage}
                onChange={(e) =>
                  updateVehicle(index, 'CoverageInformation.SafetyGlassCoverage', e.target.checked)
                }
              />
              Glass Coverage (windshield/window replacement)
            </label>
          </div>
        </div>
      ))}

      <button onClick={addVehicle} className="btn btn-secondary">
        + Add Another Vehicle
      </button>
    </div>
  );
};

// Coverages Step Component
const CoveragesStep: React.FC<{
  policyCoverages: PolicyCoverages;
  setPolicyCoverages: React.Dispatch<React.SetStateAction<PolicyCoverages>>;
  effectiveDate: string;
  setEffectiveDate: React.Dispatch<React.SetStateAction<string>>;
  config: MinimalFieldsConfig | null;
}> = ({ policyCoverages, setPolicyCoverages, effectiveDate, setEffectiveDate, config }) => {
  const updateCoverage = (field: string, value: any) => {
    setPolicyCoverages((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="coverages-step">
      <h3>Policy Coverage</h3>
      <p>Select your liability and coverage limits</p>

      <div className="form-group">
        <label>
          Effective Date <span className="required">*</span>
        </label>
        <input
          type="date"
          value={effectiveDate}
          onChange={(e) => setEffectiveDate(e.target.value)}
          min={new Date().toISOString().split('T')[0]}
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>
            Bodily Injury Liability <span className="required">*</span>
          </label>
          <select
            value={policyCoverages.LiabilityBiLimit}
            onChange={(e) => updateCoverage('LiabilityBiLimit', e.target.value)}
          >
            {config?.enums.LiabilityBiLimit?.map((limit) => (
              <option key={limit} value={limit}>
                ${limit.replace('/', ' / $')}
              </option>
            ))}
          </select>
          <small>Per person / Per accident</small>
        </div>

        <div className="form-group">
          <label>
            Property Damage Liability <span className="required">*</span>
          </label>
          <select
            value={policyCoverages.LiabilityPdLimit}
            onChange={(e) => updateCoverage('LiabilityPdLimit', e.target.value)}
          >
            {config?.enums.LiabilityPdLimit?.map((limit) => (
              <option key={limit} value={limit}>
                ${limit}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Medical Payments</label>
          <select
            value={policyCoverages.MedPayLimit}
            onChange={(e) => updateCoverage('MedPayLimit', e.target.value)}
          >
            {config?.enums.MedPayLimit?.map((limit) => (
              <option key={limit} value={limit}>
                {limit === 'None' ? 'None' : `$${limit}`}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Uninsured Motorist BI</label>
          <select
            value={policyCoverages.UninsuredMotoristBiLimit}
            onChange={(e) => updateCoverage('UninsuredMotoristBiLimit', e.target.value)}
          >
            {config?.enums.UninsuredMotoristBiLimit?.map((limit) => (
              <option key={limit} value={limit}>
                ${limit.replace('/', ' / $')}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Accidental Death</label>
          <select
            value={policyCoverages.AccidentalDeathLimit}
            onChange={(e) => updateCoverage('AccidentalDeathLimit', e.target.value)}
          >
            {config?.enums.AccidentalDeathLimit?.map((limit) => (
              <option key={limit} value={limit}>
                {limit === 'None' ? 'None' : `$${limit}`}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={policyCoverages['UninsuredMotoristPd/CollisionDamageWaiver']}
              onChange={(e) =>
                updateCoverage('UninsuredMotoristPd/CollisionDamageWaiver', e.target.checked)
              }
            />
            Uninsured Motorist PD / Collision Deductible Waiver
          </label>
        </div>
      </div>

      <div className="info-box">
        <strong>💡 Recommended Coverage:</strong>
        <p>
          California minimum is 15/30/5, but we recommend at least 25/50/25 for better protection.
        </p>
      </div>
    </div>
  );
};

// Review Step Component
const ReviewStep: React.FC<{
  customer: CustomerData;
  drivers: DriverData[];
  vehicles: VehicleData[];
  policyCoverages: PolicyCoverages;
  effectiveDate: string;
}> = ({ customer, drivers, vehicles, policyCoverages, effectiveDate }) => {
  return (
    <div className="review-step">
      <h3>Review Your Information</h3>
      <p>Please review before submitting</p>

      <div className="review-section">
        <h4>Customer</h4>
        <p>
          {customer.FirstName} {customer.LastName}
        </p>
        <p>
          {customer.Address.Street1}, {customer.Address.City}, {customer.Address.State}{' '}
          {customer.Address.ZipCode}
        </p>
        <p>At residence: {customer.MonthsAtResidence} months</p>
      </div>

      <div className="review-section">
        <h4>Drivers ({drivers.length})</h4>
        {drivers.map((driver, index) => (
          <div key={index} className="review-item">
            <p>
              <strong>
                {driver.FirstName} {driver.LastName}
              </strong>
            </p>
            <p>
              {driver.Gender}, {driver.MaritalStatus}
            </p>
            <p>License: {driver.LicenseInformation.LicenseStatus}</p>
          </div>
        ))}
      </div>

      <div className="review-section">
        <h4>Vehicles ({vehicles.length})</h4>
        {vehicles.map((vehicle, index) => (
          <div key={index} className="review-item">
            <p>
              <strong>
                {vehicle.Year} {vehicle.Make} {vehicle.Model}
              </strong>
            </p>
            <p>VIN: {vehicle.Vin}</p>
            <p>
              Collision: ${vehicle.CoverageInformation.CollisionDeductible} | Comprehensive: $
              {vehicle.CoverageInformation.ComprehensiveDeductible}
            </p>
          </div>
        ))}
      </div>

      <div className="review-section">
        <h4>Coverage</h4>
        <p>Effective Date: {effectiveDate}</p>
        <p>Bodily Injury: ${policyCoverages.LiabilityBiLimit.replace('/', ' / $')}</p>
        <p>Property Damage: ${policyCoverages.LiabilityPdLimit}</p>
      </div>

      <div className="info-box">
        <strong>✅ Ready to Submit</strong>
        <p>
          Click "Get Quote" to submit your information and receive personalized rate quotes from
          multiple carriers.
        </p>
      </div>
    </div>
  );
};

export default InsuranceMinimalWidget;
