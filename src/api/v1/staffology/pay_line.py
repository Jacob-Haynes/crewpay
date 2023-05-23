from api.v1.crewplanner.dto_cp_ShiftsByUser import CPShiftsByUser
from api.v1.staffology.dto_so_pay_options_import import Line, PayLine
from crewpay.models import Employee


def create_pay_line(user_shifts: CPShiftsByUser) -> PayLine:
    """Converts  cp shifts by user to a staffology Payline"""
    new_lines = []
    for shift in user_shifts.shifts:
        code = "BASICHOURLY" if shift.wage.type_ == "hourly" else "BASICDAILY"
        new_lines.append(
            Line(
                value=shift.wage.total,
                rate=shift.wage.value,
                multiplier=shift.timesheet.registered.netto_minutes / 60,
                description=f"{shift.project.date} - {shift.project.company.name} - {shift.project.name}",
                code=code,
            )
        )

    return PayLine(
        payrollCode=Employee.objects.get(crewplanner_id=user_shifts.user_id).payroll_code,
        lines=new_lines,
    )
