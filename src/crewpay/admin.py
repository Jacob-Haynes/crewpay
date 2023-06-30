from django.contrib import admin

from crewpay.models import (
    CrewplannerUser,
    Employee,
    Employer,
    InvalidEmployee,
    InvalidShift,
)


class TimeAdmin(admin.ModelAdmin):
    readonly_fields = ("date_time",)


admin.site.register(CrewplannerUser)
admin.site.register(Employer)
admin.site.register(Employee)
admin.site.register(InvalidEmployee, TimeAdmin)
admin.site.register(InvalidShift)
