import React, { useState, useEffect } from 'react';
import { GlassCard, AnimatedButton } from '../../../components/ui';
import { employeeApi } from '../../../services/employeeApi';
import { toast } from 'react-hot-toast';
import { useNavigate, useParams } from 'react-router-dom';
import { CheckCircle, ChevronRight, ChevronLeft, Save, X } from 'lucide-react';

import PersonalInfoStep from './wizard-steps/PersonalInfoStep';
import ContactAddressStep from './wizard-steps/ContactAddressStep';
import EmploymentStep from './wizard-steps/EmploymentStep';
import BankingGovIdStep from './wizard-steps/BankingGovIdStep';
import SalaryPayrollStep from './wizard-steps/SalaryPayrollStep';

const STEPS = [
  { id: 'personal', title: 'Personal Info', component: PersonalInfoStep },
  { id: 'contact', title: 'Contact & Address', component: ContactAddressStep },
  { id: 'employment', title: 'Employment', component: EmploymentStep },
  { id: 'banking', title: 'Banking & Gov IDs', component: BankingGovIdStep },
  { id: 'salary', title: 'Salary & Payroll', component: SalaryPayrollStep }
];

export default function EmployeeWizard() {
  const navigate = useNavigate();
  const { id: editEmployeeId } = useParams<{ id: string }>();
  const [currentStep, setCurrentStep] = useState(0);
  
  // Highest step the user is allowed to navigate to
  const [maxCompletedStep, setMaxCompletedStep] = useState(-1);
  
  const [formData, setFormData] = useState<any>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (editEmployeeId) {
      loadEmployeeData(editEmployeeId);
    } else {
      const draft = localStorage.getItem('employee_wizard_draft');
      if (draft) {
        try {
          const parsed = JSON.parse(draft);
          setFormData(parsed.data || {});
          setCurrentStep(parsed.step || 0);
          setMaxCompletedStep(parsed.maxCompletedStep || -1);
        } catch (e) {
          console.error("Failed to parse draft", e);
        }
      }
    }
  }, [editEmployeeId]);

  const loadEmployeeData = async (employeeId: string) => {
    try {
      // Base
      const empRes = await employeeApi.getEmployee(employeeId);
      const baseData = empRes?.data || empRes || {};
      
      const [pers, cont, addr, emp, bank, gov, pay] = await Promise.all([
        employeeApi.getPersonal(employeeId),
        employeeApi.getContact(employeeId),
        employeeApi.getAddress(employeeId),
        employeeApi.getEmployment(employeeId),
        employeeApi.getBanking(employeeId),
        employeeApi.getGovernmentId(employeeId),
        employeeApi.getPayrollConfig(employeeId)
      ]);

      setFormData({
        employeeId,
        ...baseData,
        ...(pers?.data?.[0] || pers?.[0] || {}),
        ...(cont?.[0] || {}), // Contact is already mapped in api
        ...(addr?.data?.[0] || addr?.[0] || {}),
        ...(emp?.[0] || {}), // Employment is already mapped in api
        ...(bank?.data?.[0] || bank?.[0] || {}),
        ...(gov?.data?.[0] || gov?.[0] || {}),
        ...(pay?.[0] || {}) // Payroll is already mapped in api
      });
      
      // In edit mode, all steps are accessible
      setMaxCompletedStep(STEPS.length - 1);
    } catch (e) {
      console.error("Failed to load employee data", e);
      toast.error("Failed to load employee data for editing.");
    }
  };

  const handleSaveDraft = () => {
    localStorage.setItem('employee_wizard_draft', JSON.stringify({
      data: formData,
      step: currentStep,
      maxCompletedStep
    }));
    toast.success('Draft saved successfully!');
  };

  const handleCancel = () => {
    if (window.confirm("Are you sure you want to cancel? Any unsaved progress will be lost. (Draft will be kept)")) {
      navigate('/admin/employees');
    }
  };

  const validateStep = (stepIndex: number): boolean => {
    const errors: Record<string, string> = {};
    let isValid = true;

    if (stepIndex === 0) {
      if (!formData.firstName) errors.firstName = "First Name is required";
      if (!formData.lastName) errors.lastName = "Last Name is required";
      if (!formData.dob) errors.dob = "Date of Birth is required";
      if (!formData.gender) errors.gender = "Gender is required";
    } else if (stepIndex === 1) {
      if (!formData.workEmail) errors.workEmail = "Work Email is required";
      if (!formData.mobilePhone) errors.mobilePhone = "Mobile Phone is required";
      if (!formData.currentAddressLine1) errors.currentAddressLine1 = "Current Address is required";
      if (!formData.currentCity) errors.currentCity = "City is required";
      if (!formData.currentState) errors.currentState = "State is required";
      if (!formData.currentPincode) errors.currentPincode = "Pincode is required";
    } else if (stepIndex === 2) {
      if (!formData.companyId) errors.companyId = "Company is required";
      if (!formData.branchId) errors.branchId = "Branch is required";
      if (!formData.departmentId) errors.departmentId = "Department is required";
      if (!formData.designationId) errors.designationId = "Designation is required";
      if (!formData.effectiveFrom) errors.effectiveFrom = "Date of Joining is required";
      if (!formData.employmentType) errors.employmentType = "Employment Type is required";
    } else if (stepIndex === 3) {
      // Optional fields largely, but we can enforce PAN
      if (!formData.panNumber) errors.panNumber = "PAN Number is required for payroll";
    } else if (stepIndex === 4) {
      if (!formData.salaryStructureId) errors.salaryStructureId = "Salary Structure is required";
      if (!formData.basicSalary) errors.basicSalary = "Basic Salary is required";
      if (!formData.isSalaryPreviewCalculated) {
        errors.general = "You must calculate and review the salary preview before saving.";
      }
    }

    setValidationErrors(errors);
    if (Object.keys(errors).length > 0) {
      isValid = false;
      toast.error('Please fix the validation errors before continuing.');
    }
    return isValid;
  };
  const cleanPayload = (payload: any) => {
    const cleaned: any = {};
    for (const [key, value] of Object.entries(payload)) {
      if (value === '') continue;
      cleaned[key] = value;
    }
    return cleaned;
  };

  const saveStepApi = async (stepIndex: number): Promise<boolean> => {
    try {
      if (stepIndex === 0) {
        let empId = formData.employeeId;
        if (!empId) {
          const empRes = await employeeApi.createEmployee({});
          empId = empRes._id || empRes.employeeId || empRes.id;
          setFormData((prev: any) => ({ ...prev, employeeId: empId }));
        }
        const personalPayload = cleanPayload({ ...formData, employeeId: empId });
        await employeeApi.createPersonal(personalPayload);
      } else if (stepIndex === 1) {
        await employeeApi.createContact(cleanPayload({ ...formData, employeeId: formData.employeeId }));
        await employeeApi.createAddress(cleanPayload({ ...formData, employeeId: formData.employeeId }));
      } else if (stepIndex === 2) {
        await employeeApi.createEmployment(cleanPayload({ ...formData, employeeId: formData.employeeId }));
      } else if (stepIndex === 3) {
        await employeeApi.createBanking(cleanPayload({ ...formData, employeeId: formData.employeeId }));
        await employeeApi.createGovernmentId(cleanPayload({ ...formData, employeeId: formData.employeeId }));
      } else if (stepIndex === 4) {
        const payload = cleanPayload({ ...formData, employeeId: formData.employeeId });
        await employeeApi.createPayrollConfig(payload);
        await employeeApi.assignSalary(payload);
      }
      return true;
    } catch (e: any) {
      console.error(e);
      let errorMsg = 'Failed to save section.';
      // Our custom fetch wrapper throws an Error with the message being the parsed detail.
      if (e instanceof Error && e.message) {
        // e.message might be a JSON string if the backend returned a validation array, or a simple string.
        try {
          const parsed = JSON.parse(e.message);
          if (Array.isArray(parsed)) {
             errorMsg = parsed.map((err: any) => `${err.loc?.join('.')} - ${err.msg}`).join(', ');
          } else {
             errorMsg = e.message;
          }
        } catch {
          errorMsg = e.message;
        }
      }
      toast.error(errorMsg);
      return false;
    }
  };

  const handleSaveAndContinue = async () => {
    if (!validateStep(currentStep)) {
      return;
    }

    setIsSubmitting(true);
    const toastId = toast.loading(`Saving ${STEPS[currentStep].title}...`);

    const success = await saveStepApi(currentStep);
    
    if (success) {
      toast.success(`${STEPS[currentStep].title} saved successfully`, { id: toastId });
      if (currentStep > maxCompletedStep) {
        setMaxCompletedStep(currentStep);
      }
      
      if (currentStep < STEPS.length - 1) {
        setCurrentStep(curr => curr + 1);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        // Final Step Completed
        localStorage.removeItem('employee_wizard_draft');
        toast.success(editEmployeeId ? "Employee Update Completed!" : "Employee Onboarding Completed!");
        navigate('/admin/employees');
      }
    } else {
      toast.dismiss(toastId);
    }
    
    setIsSubmitting(false);
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(curr => curr - 1);
      setValidationErrors({});
    }
  };

  const navigateToStep = (index: number) => {
    if (index <= maxCompletedStep + 1) {
      setCurrentStep(index);
      setValidationErrors({});
    }
  };

  const CurrentComponent = STEPS[currentStep].component;
  const progressPercentage = ((currentStep) / (STEPS.length - 1)) * 100;

  return (
    <div className="max-w-5xl mx-auto flex flex-col min-h-[calc(100vh-100px)]">
      
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-neutral-900">{editEmployeeId ? 'Edit Employee' : 'Create New Employee'}</h1>
          <p className="text-neutral-500 mt-1">Step {currentStep + 1} of {STEPS.length} - {STEPS[currentStep].title}</p>
        </div>
      </div>

      {/* Stepper Header */}
      <GlassCard className="p-4 mb-6">
        <div className="relative">
          {/* Progress Bar Background */}
          <div className="absolute top-4 left-0 w-full h-1 bg-neutral-200 -z-10 rounded-full"></div>
          {/* Progress Bar Fill */}
          <div 
            className="absolute top-4 left-0 h-1 bg-brand-500 -z-10 rounded-full transition-all duration-300"
            style={{ width: `${progressPercentage}%` }}
          ></div>
          
          <div className="flex justify-between">
            {STEPS.map((step, index) => {
              const isCompleted = index <= maxCompletedStep;
              const isActive = index === currentStep;
              const isClickable = index <= maxCompletedStep + 1;
              
              return (
                <button 
                  key={step.id} 
                  onClick={() => isClickable ? navigateToStep(index) : null}
                  className={`flex flex-col items-center relative z-10 w-full ${isClickable ? 'cursor-pointer hover:opacity-80' : 'cursor-not-allowed opacity-50'}`}
                >
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm mb-2 transition-colors
                    ${isCompleted && !isActive ? 'bg-brand-500 text-white' : isActive ? 'bg-brand-100 text-brand-600 border-2 border-brand-500' : 'bg-neutral-100 text-neutral-400 border border-neutral-300'}
                  `}>
                    {isCompleted && !isActive ? <CheckCircle className="w-5 h-5" /> : (index + 1)}
                  </div>
                  <span className={`text-xs font-medium text-center ${isActive ? 'text-brand-900 font-bold' : isCompleted ? 'text-brand-700' : 'text-neutral-500'}`}>
                    {step.title}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </GlassCard>

      {/* Step Content */}
      <GlassCard className="p-8 flex-grow mb-24">
        <CurrentComponent 
          data={formData} 
          onChange={setFormData} 
          errors={validationErrors} 
        />
      </GlassCard>

      {/* Sticky Footer */}
      <div className="fixed bottom-0 left-0 right-0 lg:left-64 bg-white border-t border-neutral-200 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] p-4 px-8 z-50">
        <div className="max-w-5xl mx-auto flex justify-between items-center">
          
          <div className="flex space-x-4">
            <button
              onClick={handleCancel}
              className="flex items-center space-x-2 px-4 py-2 text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 rounded-lg transition-colors"
            >
              <X className="w-4 h-4" />
              <span>Cancel</span>
            </button>

            {currentStep > 0 && (
              <button
                onClick={handleBack}
                disabled={isSubmitting}
                className="flex items-center space-x-2 px-6 py-2 bg-white border border-neutral-300 text-neutral-700 rounded-lg hover:bg-neutral-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-5 h-5" />
                <span>Previous</span>
              </button>
            )}
          </div>

          <div className="flex space-x-4">
            <button 
              onClick={handleSaveDraft}
              disabled={isSubmitting}
              className="flex items-center space-x-2 px-6 py-2 bg-white border border-brand-300 text-brand-700 rounded-lg hover:bg-brand-50 transition-colors disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              <span>Save Draft</span>
            </button>

            <AnimatedButton onClick={handleSaveAndContinue} disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : currentStep === STEPS.length - 1 ? 'Save & Assign Salary' : 'Save & Continue'}
            </AnimatedButton>
          </div>

        </div>
      </div>

    </div>
  );
}
