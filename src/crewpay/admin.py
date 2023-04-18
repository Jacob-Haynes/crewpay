from django.contrib import admin

from crewpay.models import CrewplannerUser, Employee, Employer, StaffologyUser

admin.site.register(CrewplannerUser)
admin.site.register(StaffologyUser)
admin.site.register(Employer)
admin.site.register(Employee)
