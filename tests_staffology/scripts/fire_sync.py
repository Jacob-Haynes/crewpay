import csv
from pathlib import Path

from api.v1.staffology.api.employees import StaffologyEmployeeAPI
from crewpay.models import Employee
from crewpay.wsgi import application


def fire_data():
    with open("fireupload.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        data = []
        for row in reader:
            data.append(dict(row))
    return data


def link_employee(cp_staff_list, employer_id: str) -> None:
    """this links an already existing staffology employee to a cp one via a csv.
    used primarily for importing fire but could be useful."""
    staffology_list = StaffologyEmployeeAPI().staffology_employees_get(employer_id)
    for person in cp_staff_list:
        payroll_code = person["payroll_code"]
        if Employee.objects.filter(employer=employer_id, payroll_code=payroll_code).exists():
            continue
        else:
            for staff in staffology_list:
                if staff["metadata"]["payrollCode"] == payroll_code and person["status"] == "Active":
                    new_entry = Employee(
                        employer_id=employer_id,
                        crewplanner_id=person["id"],
                        staffology_id=staff["id"],
                        payroll_code=payroll_code,
                        status="ACTIVE",
                    )
                    print(new_entry)
                    new_entry.save()
                elif staff["metadata"]["payrollCode"] == payroll_code:
                    new_entry = Employee(
                        employer_id=employer_id,
                        crewplanner_id=person["id"],
                        staffology_id=staff["id"],
                        payroll_code=payroll_code,
                        status="ARCHIVED",
                    )
                    print(new_entry)
                    new_entry.save()


data = fire_data()
link_employee(data, "3e863ec8-a81f-45a5-96b9-0c4144c97148")
