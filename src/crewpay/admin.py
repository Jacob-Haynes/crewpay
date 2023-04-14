from django.contrib import admin

from crewpay.models import CrewplannerUser, Employer, StaffologyUser

admin.site.register(CrewplannerUser)
admin.site.register(StaffologyUser)
admin.site.register(Employer)
