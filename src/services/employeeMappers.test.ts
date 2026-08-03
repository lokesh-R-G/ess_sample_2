import { contactMapper, employmentMapper, payrollConfigMapper } from './employeeMappers';

describe('Employee Mappers', () => {
  describe('contactMapper', () => {
    it('maps UI to Backend correctly', () => {
      const uiData = { workEmail: 'test@work.com', mobilePhone: '1234567890', personalEmail: 'test@home.com' };
      const backendData = contactMapper.toBackend(uiData);
      expect(backendData.officialEmail).toBe('test@work.com');
      expect(backendData.officialMobile).toBe('1234567890');
      expect(backendData.workEmail).toBeUndefined();
      expect(backendData.mobilePhone).toBeUndefined();
      expect(backendData.personalEmail).toBe('test@home.com');
    });

    it('maps Backend to UI correctly', () => {
      const backendData = { officialEmail: 'test@work.com', officialMobile: '1234567890', personalEmail: 'test@home.com' };
      const uiData = contactMapper.fromBackend(backendData);
      expect(uiData.workEmail).toBe('test@work.com');
      expect(uiData.mobilePhone).toBe('1234567890');
      expect(uiData.officialEmail).toBeUndefined();
      expect(uiData.officialMobile).toBeUndefined();
      expect(uiData.personalEmail).toBe('test@home.com');
    });
  });

  describe('employmentMapper', () => {
    it('maps UI to Backend correctly', () => {
      const uiData = { effectiveFrom: '2023-01-01', designationId: 'DESIG_1' };
      const backendData = employmentMapper.toBackend(uiData);
      expect(backendData.dateOfJoining).toBe('2023-01-01');
      expect(backendData.effectiveFrom).toBe('2023-01-01');
      expect(backendData.designationId).toBe('DESIG_1');
    });

    it('maps Backend to UI correctly', () => {
      const backendData = { dateOfJoining: '2023-01-01', effectiveFrom: '2023-01-01', designationId: 'DESIG_1' };
      const uiData = employmentMapper.fromBackend(backendData);
      expect(uiData.effectiveFrom).toBe('2023-01-01');
      expect(uiData.designationId).toBe('DESIG_1');
    });
  });

  describe('payrollConfigMapper', () => {
    it('maps UI to Backend correctly (OptOut)', () => {
      const uiData = { pfOption: 'OptOut', esiOption: 'PhysicalDisability', ptState: 'None' };
      const backendData = payrollConfigMapper.toBackend(uiData);
      expect(backendData.wantsPf).toBe(false);
      expect(backendData.pfCalculationMethod).toBe('Default');
      expect(backendData.esiEnabled).toBe(false);
      expect(backendData.ptState).toBeNull();
      expect(backendData.pfOption).toBeUndefined();
    });

    it('maps UI to Backend correctly (Actual)', () => {
      const uiData = { pfOption: 'Actual', esiOption: 'Default', ptState: 'Karnataka' };
      const backendData = payrollConfigMapper.toBackend(uiData);
      expect(backendData.wantsPf).toBe(true);
      expect(backendData.pfCalculationMethod).toBe('Actual');
      expect(backendData.esiEnabled).toBe(true);
      expect(backendData.ptState).toBe('Karnataka');
    });

    it('maps Backend to UI correctly (OptOut)', () => {
      const backendData = { wantsPf: false, pfCalculationMethod: 'Default', esiEnabled: false, ptState: null };
      const uiData = payrollConfigMapper.fromBackend(backendData);
      expect(uiData.pfOption).toBe('OptOut');
      expect(uiData.esiOption).toBe('PhysicalDisability');
      expect(uiData.ptState).toBe('None');
    });

    it('maps Backend to UI correctly (Ceiling)', () => {
      const backendData = { wantsPf: true, pfCalculationMethod: 'Ceiling', esiEnabled: true, ptState: 'Maharashtra' };
      const uiData = payrollConfigMapper.fromBackend(backendData);
      expect(uiData.pfOption).toBe('Ceiling');
      expect(uiData.esiOption).toBe('Default');
      expect(uiData.ptState).toBe('Maharashtra');
    });
  });
});
