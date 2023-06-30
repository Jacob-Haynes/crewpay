from typing import Dict

from api.v1.staffology.payroll.payroll_manager import PayrollManager


def run_payroll(employer, tax_year, arrears) -> Dict:
    """Function for running payroll"""
    manager = PayrollManager(employer=employer, tax_year=tax_year, arrears=arrears)
    result = manager.process_payroll()
    return result
