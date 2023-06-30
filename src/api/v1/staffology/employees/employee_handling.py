import hashlib
from typing import List

from api.v1.crewplanner.dto.dto_cp_employee import CPEmployee
from api.v1.staffology.api.employees import StaffologyEmployeeAPI
from api.v1.staffology.dto.dto_so_employee import StaffologyEmployee
from api.v1.staffology.dto.dto_so_employee_full import StaffologyEmployeeFull
from api.v1.staffology.employees.employee_formatting import cp_emp_to_staffology_emp
from crewpay.models import Employee

"""
Handles all functions that manipulate employees within staffology
"""


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


def new_employee(cp_employee: CPEmployee, employer_id: str) -> None:
    """creates a new employee in staffology and the database"""
    new_employee_payload = cp_emp_to_staffology_emp(cp_employee, employer_id)
    created_staffology_employee = StaffologyEmployeeAPI().employee_create(employer_id, new_employee_payload)
    # create hash of employee payload for later comparison
    payload = cp_emp_to_staffology_emp(cp_employee, employer_id)
    payload_hash = consistent_hash(payload)

    new_entry = Employee(
        employer_id=employer_id,
        crewplanner_id=cp_employee.id,
        staffology_id=created_staffology_employee["id"],
        payroll_code=created_staffology_employee["employmentDetails"]["payrollCode"],
        status="ACTIVE",
        payload_hash=payload_hash,
    )
    new_entry.save()


def update_so_fields(so_full: StaffologyEmployeeFull, update_data: StaffologyEmployee) -> StaffologyEmployeeFull:
    """Updates fields in staffology object that can be changed from CP data"""
    fields_to_update = [
        "accountNumber",
        "sortCode",
        "line1",
        "line2",
        "line3",
        "postCode",
        "country",
        "maritalStatus",
        "email",
        "photoUrl",
        "telephone",
    ]

    for field in fields_to_update:
        if hasattr(update_data.bankDetails, field):
            setattr(so_full.bankDetails, field, getattr(update_data.bankDetails, field))
        if hasattr(update_data.personalDetails.address, field):
            setattr(so_full.personalDetails.address, field, getattr(update_data.personalDetails.address, field))
        if hasattr(update_data.personalDetails, field):
            setattr(so_full.personalDetails, field, getattr(update_data.personalDetails, field))

    return so_full


def update_employee(cp_employee: CPEmployee, employer_id: str) -> None:
    """Updates employee data in staffology"""
    employee = Employee.objects.get(crewplanner_id=cp_employee.id)

    # Retrieve the existing staffology employee data and populate object
    staffology_employee = StaffologyEmployeeAPI().staffology_employee_get(employer_id, employee.staffology_id)
    so_employee_full = StaffologyEmployeeFull(**staffology_employee)

    # Overwrite the relevant fields with the updated data from cp_employee
    update_data = cp_emp_to_staffology_emp(cp_employee, employer_id)
    updated_payload = update_so_fields(so_employee_full, update_data)

    # Update the employee data using the updated payload
    StaffologyEmployeeAPI().update_employees(employer_id, employee.staffology_id, updated_payload)

    # Update the hash of the employee using the cp payload only
    payload_hash = consistent_hash(update_data)
    employee.payload_hash = payload_hash
    employee.save()


def consistent_hash(payload: StaffologyEmployee):
    """Returns a consistent hash of the model"""
    instance_dict = payload.dict()
    sorted_dict = dict(sorted(instance_dict.items()))
    instance_str = str(sorted_dict)
    hash_object = hashlib.sha256(instance_str.encode())
    return hash_object.hexdigest()


def is_employee_modified(cp_employee: CPEmployee) -> bool:
    """Checks if the employee data is different from the stored hash"""
    employee = Employee.objects.get(crewplanner_id=cp_employee.id)
    employer_id = employee.employer.id
    new_payload = cp_emp_to_staffology_emp(cp_employee, employer_id)
    # Calculate the hash of the new payload using the same algorithm as before
    new_payload_hash = consistent_hash(new_payload)
    # Compare the new payload hash with the stored hash in the model
    if employee.payload_hash == new_payload_hash:
        return False  # Payload has not been modified
    return True  # Payload has been modified


def mark_as_leaver(existing_ids: List[CPEmployee], employer_id: str) -> List:
    """Marks archived cp employees as leavers"""
    leavers = []
    for cp_employee in existing_ids:
        if cp_employee.status == "ARCHIVED" and Employee.objects.get(crewplanner_id=cp_employee.id).status == "ACTIVE":
            leavers.append(Employee.objects.get(crewplanner_id=cp_employee.id).staffology_id)
        else:
            continue
    if len(leavers) > 0:
        StaffologyEmployeeAPI().mark_leavers(employer_id, leavers)
        Employee.objects.filter(staffology_id__in=leavers).update(status="ARCHIVED")
    return leavers


def mark_as_rehire(existing_ids: List[CPEmployee], employer_id: str) -> List:
    """Marks un-archived cp employees as rehires"""
    rehires = []
    for cp_employee in existing_ids:
        if (
            cp_employee.status != "ARCHIVED"
            and Employee.objects.get(crewplanner_id=cp_employee.id).status == "ARCHIVED"
        ):
            rehire = Employee.objects.get(crewplanner_id=cp_employee.id).staffology_id
            rehired = StaffologyEmployeeAPI().mark_rehires(employer_id, rehire)
            Employee.objects.filter(crewplanner_id=cp_employee.id).update(status="ACTIVE", staffology_id=rehired["id"])
            rehires.append(rehire)
        else:
            continue
    return rehires


def delete_employee(cp_employees: List[CPEmployee], employer_id: str) -> List:
    """Deletes non-existent cp employees from staffology and the db"""
    # update current employee list
    stored_cp_employee_ids = Employee.objects.filter(employer=employer_id).values_list("crewplanner_id", flat=True)
    # get list of stored employees not in cp
    id_list = [cp_employee.id for cp_employee in cp_employees]
    deleted = list(set(stored_cp_employee_ids).difference(id_list))
    to_delete = []
    # delete them from staffology and database
    if len(deleted) > 0:
        for cp_id in deleted:
            to_delete.append(Employee.objects.get(crewplanner_id=cp_id).staffology_id)
        StaffologyEmployeeAPI().delete_employees(employer_id, to_delete)
        Employee.objects.filter(crewplanner_id__in=to_delete).delete()
    return to_delete
