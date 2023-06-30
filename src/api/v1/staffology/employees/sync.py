from typing import Dict


from api.v1.staffology.employees.employee_manager import EmployeeManager
from api.v1.staffology.employers.employers import update_employer_db


def sync_employees(employer) -> Dict:
    """Function for syncing employees"""
    # check for employer updates
    update_employer_db(employer)
    # run employee manager
    manager = EmployeeManager(employer)
    result = manager.run()
    return result
