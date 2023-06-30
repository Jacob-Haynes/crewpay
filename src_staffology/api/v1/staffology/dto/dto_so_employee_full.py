from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class Address(BaseModel):
    line1: Optional[str]
    line2: Optional[str]
    line3: Optional[str]
    line4: Optional[str]
    line5: Optional[str]
    postCode: Optional[str]
    country: Optional[str]
    foreignCountry: Optional[str]


class PartnerDetails(BaseModel):
    firstName: Optional[str]
    initials: Optional[str]
    lastName: Optional[str]
    niNumber: Optional[str]


class PersonalDetails(BaseModel):
    address: Optional[Address]
    maritalStatus: Optional[str]
    title: Optional[str]
    firstName: Optional[str]
    middleName: Optional[str]
    lastName: Optional[str]
    alternativeEmail: Optional[str]
    previousSurName: Optional[str]
    email: Optional[str]
    emailPayslip: Optional[str]
    passwordProtectPayslip: Optional[str]
    pdfPassword: Optional[str]
    pdfPasswordType: Optional[str]
    emailStatement: Optional[str]
    photoUrl: Optional[str]
    telephone: Optional[str]
    mobile: Optional[str]
    dateOfBirth: Optional[str]
    statePensionAge: Optional[int]
    gender: Optional[str]
    niNumber: Optional[str]
    passportNumber: Optional[str]
    partnerDetails: Optional[PartnerDetails]


class OverseasEmployerDetails(BaseModel):
    overseasEmployer: Optional[str]
    overseasSecondmentStatus: Optional[str]
    eeaCitizen: Optional[str]
    epm6Scheme: Optional[str]


class PensionerPayroll(BaseModel):
    inReceiptOfPension: Optional[str]
    bereaved: Optional[str]
    amount: Optional[float]
    startDate: Optional[str]


class StarterDetails(BaseModel):
    startDate: Optional[str]
    starterDeclaration: Optional[str]
    overseasEmployerDetails: Optional[OverseasEmployerDetails]
    pensionerPayroll: Optional[PensionerPayroll]


class DirectorshipDetails(BaseModel):
    isDirector: Optional[str]
    startDate: Optional[str]
    leaveDate: Optional[str]
    niAlternativeMethod: Optional[str]


class LeaverDetails(BaseModel):
    hasLeft: Optional[str]
    leaveDate: Optional[str]
    isDeceased: Optional[str]
    paymentAfterLeaving: Optional[str]
    p45Sent: Optional[str]


class Verification(BaseModel):
    manuallyEntered: Optional[str]
    matchInsteadOfVerify: Optional[str]
    number: Optional[str]
    date: Optional[str]
    taxStatus: Optional[str]
    verificationRequest: Optional[str]
    verificationResponse: Optional[str]


class Cis(BaseModel):
    type: Optional[str]
    utr: Optional[str]
    tradingName: Optional[str]
    companyUtr: Optional[str]
    companyNumber: Optional[str]
    vatRegistered: Optional[str]
    vatNumber: Optional[str]
    vatRate: Optional[float]
    reverseChargeVAT: Optional[str]
    verification: Optional[Verification]


class Department(BaseModel):
    code: Optional[str]
    title: Optional[str]
    color: Optional[str]
    employeeCount: Optional[int]
    accountingCode: Optional[str]


class Role(BaseModel):
    id: Optional[str]
    name: Optional[str]
    metadata: Optional[Dict[str, Any]]
    url: Optional[str]


class VeteranDetails(BaseModel):
    isVeteran: Optional[str]
    firstCivilianEmploymentDate: Optional[str]


class EmploymentDetails(BaseModel):
    cisSubContractor: Optional[str]
    payrollCode: Optional[str]
    jobTitle: Optional[str]
    onHold: Optional[str]
    onFurlough: Optional[str]
    furloughStart: Optional[str]
    furloughEnd: Optional[str]
    furloughCalculationBasis: Optional[str]
    furloughCalculationBasisAmount: Optional[float]
    partialFurlough: Optional[str]
    furloughHoursNormallyWorked: Optional[float]
    furloughHoursOnFurlough: Optional[float]
    isApprentice: Optional[str]
    apprenticeshipStartDate: Optional[str]
    apprenticeshipEndDate: Optional[str]
    workingPattern: Optional[str]
    forcePreviousPayrollCode: Optional[str]
    starterDetails: Optional[StarterDetails]
    directorshipDetails: Optional[DirectorshipDetails]
    leaverDetails: Optional[LeaverDetails]
    cis: Optional[Cis]
    department: Optional[Department]
    roles: Optional[List[Role]]
    isWorkingInFreePort: Optional[str]
    veteranDetails: Optional[VeteranDetails]
    continuousEmploymentDate: Optional[str]
    includeSecondedInfoOnStarter: Optional[str]


class Action(BaseModel):
    action: Optional[str]
    employeeState: Optional[str]
    actionCompleted: Optional[str]
    actionCompletedMessage: Optional[str]
    requiredLetter: Optional[str]
    pensionSchemeId: Optional[str]
    workerGroupId: Optional[str]
    letterNotYetSent: Optional[str]


class Employee(BaseModel):
    id: Optional[str]
    name: Optional[str]
    metadata: Optional[Dict[str, Any]]
    url: Optional[str]


class LastAssessment(BaseModel):
    assessmentDate: Optional[str]
    employeeState: Optional[str]
    age: Optional[int]
    ukWorker: Optional[str]
    payPeriod: Optional[str]
    ordinal: Optional[int]
    earningsInPeriod: Optional[float]
    qualifyingEarningsInPeriod: Optional[float]
    aeExclusionCode: Optional[str]
    status: Optional[str]
    reason: Optional[str]
    action: Optional[Action]
    employee: Optional[Employee]
    id: Optional[str]


class AutoEnrolment(BaseModel):
    state: Optional[str]
    stateDate: Optional[str]
    ukWorker: Optional[str]
    daysToDeferAssessment: Optional[int]
    postponementDate: Optional[str]
    deferByMonthsNotDays: Optional[str]
    exempt: Optional[str]
    aeExclusionCode: Optional[str]
    aePostponementLetterSent: Optional[str]
    lastAssessment: Optional[LastAssessment]


class LeaveSettings(BaseModel):
    useDefaultHolidayType: Optional[str]
    useDefaultAllowanceResetDate: Optional[str]
    useDefaultAllowance: Optional[str]
    useDefaultAccruePaymentInLieu: Optional[str]
    useDefaultAccruePaymentInLieuRate: Optional[str]
    useDefaultAccruePaymentInLieuAllGrossPay: Optional[str]
    useDefaultAccruePaymentInLieuPayAutomatically: Optional[str]
    useDefaultAccrueHoursPerDay: Optional[str]
    allowanceResetDate: Optional[str]
    allowance: Optional[float]
    adjustment: Optional[float]
    allowanceUsed: Optional[float]
    allowanceUsedPreviousPeriod: Optional[float]
    allowanceRemaining: Optional[float]
    holidayType: Optional[str]
    accrueSetAmount: Optional[str]
    accrueHoursPerDay: Optional[float]
    showAllowanceOnPayslip: Optional[str]
    showAhpOnPayslip: Optional[str]
    accruePaymentInLieuRate: Optional[float]
    accruePaymentInLieuAllGrossPay: Optional[str]
    accruePaymentInLieuPayAutomatically: Optional[str]
    holidayAccrualBasis: Optional[str]
    occupationalSicknessUniqueId: Optional[str]
    accruedPaymentLiability: Optional[float]
    accruedPaymentAdjustment: Optional[float]
    accruedPaymentPaid: Optional[float]
    accruedPaymentBalance: Optional[float]


class RightToWork(BaseModel):
    checked: Optional[str]
    documentType: Optional[str]
    documentRef: Optional[str]
    documentExpiry: Optional[str]
    note: Optional[str]


class BankDetails(BaseModel):
    bankName: Optional[str]
    bankBranch: Optional[str]
    bankReference: Optional[str]
    accountName: Optional[str]
    accountNumber: Optional[str]
    sortCode: Optional[str]
    note: Optional[str]
    buildingSocietyRollNumber: Optional[str]


class TaxAndNi(BaseModel):
    niTable: Optional[str]
    secondaryClass1NotPayable: Optional[str]
    postgradLoan: Optional[str]
    postgraduateLoanStartDate: Optional[str]
    postgraduateLoanEndDate: Optional[str]
    studentLoan: Optional[str]
    studentLoanStartDate: Optional[str]
    studentLoanEndDate: Optional[str]
    taxCode: Optional[str]
    week1Month1: Optional[str]
    foreignTaxCredit: Optional[str]


class FpsFields(BaseModel):
    offPayrollWorker: Optional[str]
    irregularPaymentPattern: Optional[str]
    nonIndividual: Optional[str]
    hoursNormallyWorked: Optional[str]


class RegularPayLine(BaseModel):
    value: Optional[float]
    rate: Optional[float]
    multiplier: Optional[float]
    description: Optional[str]
    attachmentOrderId: Optional[str]
    pensionId: Optional[str]
    leaveId: Optional[str]
    loanId: Optional[str]
    leaveStatutoryDaysPaid: Optional[float]
    leaveStatutoryWeeksPaid: Optional[float]
    code: Optional[str]
    tags: Optional[List[str]]
    childId: Optional[str]
    isNetToGross: Optional[str]
    targetNetToGrossValue: Optional[float]
    netToGrossDiscrepancy: Optional[float]
    effectiveFrom: Optional[str]
    effectiveTo: Optional[str]
    isAutoGeneratedBasicPayLine: Optional[str]
    percentageOfEffectiveDays: Optional[float]
    totalWorkingDays: Optional[float]
    autoAdjustForLeave: Optional[str]
    totalPaidDays: Optional[float]
    roleId: Optional[str]


class PayOptions(BaseModel):
    period: Optional[str]
    ordinal: Optional[int]
    payAmount: Optional[float]
    basis: Optional[str]
    nationalMinimumWage: Optional[str]
    payAmountMultiplier: Optional[float]
    baseHourlyRate: Optional[float]
    baseDailyRate: Optional[float]
    autoAdjustForLeave: Optional[str]
    method: Optional[str]
    payCode: Optional[str]
    withholdTaxRefundIfPayIsZero: Optional[str]
    mileageVehicleType: Optional[str]
    mapsMiles: Optional[int]
    taxAndNi: Optional[TaxAndNi]
    fpsFields: Optional[FpsFields]
    regularPayLines: Optional[List[RegularPayLine]]
    tags: Optional[List[str]]


class StaffologyEmployeeFull(BaseModel):
    holidaySchemeUniqueId: Optional[str]
    id: Optional[str]
    personalDetails: Optional[PersonalDetails]
    employmentDetails: Optional[EmploymentDetails]
    autoEnrolment: Optional[AutoEnrolment]
    leaveSettings: Optional[LeaveSettings]
    rightToWork: Optional[RightToWork]
    bankDetails: Optional[BankDetails]
    tags: Optional[List[str]]
    payOptions: Optional[PayOptions]
    status: Optional[str]
    aeNotEnroledWarning: Optional[bool]
    sourceSystemId: Optional[str]
