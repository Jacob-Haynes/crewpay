from rest_framework.response import Response

from api.v1.crewplanner.employees import crewplanner_employees_get
from api.v1.staffology.employee_handling import is_employee_modified, new_employee, mark_as_leaver, mark_as_rehire, \
    delete_employee, update_employee
from crewpay.models import Employer, CrewplannerUser, Employee, InvalidEmployee


class EmployeeManager:
    def __init__(self, employer_id):
        self.employer_id = employer_id
        self.user = Employer.objects.get(id=employer_id).user
        self.access_token = CrewplannerUser.objects.get(user=self.user).access_key
        self.stub = CrewplannerUser.objects.get(user=self.user).stub
        self.cp_employees = None
        self.failed_employees = None
        self.stored_cp_employee_ids = None
        self.new_employee_count = 0
        self.employees_to_update = []
        self.leavers = []
        self.rehires = []
        self.deleted = []
        self.failures_list = []

    def get_cp_employees(self):
        """ Get the cp employees from crewplanner. """
        cp_employees_list = crewplanner_employees_get(self.stub, self.access_token)
        self.cp_employees = [employee for employee in cp_employees_list if employee is not None]
        self.failed_employees = len(cp_employees_list) - len(self.cp_employees)

    def get_stored_cp_employee_ids(self):
        """ Get list of employees already stored. """
        self.stored_cp_employee_ids = Employee.objects.filter(employer=self.employer_id).values_list(
            "crewplanner_id", flat=True
        )

    def process_employees(self):
        """ process the CP employee list"""
        # check if existing employees are modified and need updating
        for cp_employee in self.cp_employees:
            if cp_employee.id in self.stored_cp_employee_ids:
                if is_employee_modified(cp_employee):
                    self.employees_to_update.append(cp_employee)
            elif cp_employee.status != "ARCHIVED":
                new_employee(cp_employee, self.employer_id)
                self.new_employee_count += 1
        # mark leavers
        self.leavers = mark_as_leaver(self.employees_to_update, self.employer_id)
        self.employees_to_update = [emp for emp in self.employees_to_update if emp.id not in self.leavers]
        # mark rehires
        self.rehires = mark_as_rehire(self.employees_to_update, self.employer_id)
        self.employees_to_update = [emp for emp in self.employees_to_update if emp.id not in self.rehires]
        # delete employees
        run_delete = False  # Currently forced off - need to build admin controls
        if run_delete:
            self.deleted = delete_employee(self.cp_employees, self.employer_id)
        self.employees_to_update = [emp for emp in self.employees_to_update if emp.id not in self.deleted]
        # Update modified employees
        for employee in self.employees_to_update:
            update_employee(employee, self.employer_id)
        # capture failed imports
        failures = InvalidEmployee.objects.filter(employer=self.employer_id).order_by("-date_time")[
                   :self.failed_employees
                   ]
        self.failures_list = [
            {
                "employee_id": failure.employee_id,
                "name": failure.name,
                "error": failure.error,
                "date_time": failure.date_time,
            }
            for failure in failures
        ]

    def run(self):
        """ wrapper function"""
        self.get_cp_employees()
        self.get_stored_cp_employee_ids()
        self.process_employees()

        return Response(
            {
                "Employees Added": self.new_employee_count,
                "Failed to Sync": self.failed_employees,
                "Marked as Leaver": len(self.leavers),
                "Marked as Rehired": len(self.rehires),
                "Deleted Employees": len(self.deleted),
                "Updated Employees": len(self.employees_to_update),
                "Failed Syncs": self.failures_list,
            }
        )


# Usage
# processor = EmployeeProcessor(employer_id)
# response = processor.run()
