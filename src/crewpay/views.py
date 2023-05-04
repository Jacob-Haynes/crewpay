from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import redirect, render
from rest_framework.authtoken.models import Token

from api.v1.staffology.employees import sync_employees
from api.v1.staffology.employers import create_employer, staffology_employer
from crewpay.forms import EmployerForm
from crewpay.models import CrewplannerUser, Employer, StaffologyUser
from crewpay.settings import CREWPAY_VERSION


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def get_employer_choices():
    """Used for populating the employer selector dropdown."""
    employers = Employer.objects.all()
    result = tuple([(0, "")] + [(employer.id, employer.user) for employer in employers])
    return result


def root(request: WSGIRequest):
    if not request.user.is_authenticated:
        failed = False
        if "login_failed" not in request.session:
            request.session["login_failed"] = False
        else:
            failed = True
            request.session.pop("login_failed")

        return render(request, "not_logged_in/root.html", {"is_login_failed": failed})

    context = {}

    employer_selector = EmployerForm()
    employer_selector.fields["employer"].choices = get_employer_choices()
    context["employer_selector"] = employer_selector

    return render(request, "logged_in/root.html", context)


def login_view(request):
    user = authenticate(username=request.POST["username"], password=request.POST["password"])
    if user is None:
        request.session["login_failed"] = True
        return redirect("root")

    login(request, user)
    return redirect("root")


def logout_view(request):
    logout(request)
    return redirect("root")


@login_required(login_url="/")
def onboard(request):
    if "user_exists" in request.GET:
        context = {"user_exists": True}
    elif "user_created" in request.GET:
        context = {"user_created": True}
    else:
        context = {}

    employer_selector = EmployerForm()
    employer_selector.fields["employer"].choices = get_employer_choices()
    context["employer_selector"] = employer_selector

    return render(request, "logged_in/onboard.html", context)


@login_required(login_url="/")
def about(request):
    return render(request, "logged_in/about.html", {"version": CREWPAY_VERSION})


@login_required(login_url="/")
def contact(request):
    return render(request, "logged_in/contact.html")


@login_required(login_url="/")
def settings(request):
    if "staffology_connected_already" in request.GET:
        context = {"staffology_connected_already": True}
    elif "staffology_connected_success" in request.GET:
        context = {"staffology_connected_success": True}
    else:
        context = {}

    employer_selector = EmployerForm()
    employer_selector.fields["employer"].choices = get_employer_choices()
    context["employer_selector"] = employer_selector
    return render(request, "logged_in/settings.html", context)


@login_required(login_url="/")
def token(request):
    token = Token.objects.get(user__exact=request.user)
    return render(request, "logged_in/token.html", {"token": token})


@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    try:
        User.objects.get(username=request.POST["name"])
        return redirect("/onboard?user_exists=true")
    except User.DoesNotExist:
        new_user = User(username=request.POST["name"], password=User.objects.make_random_password())
        new_cp_user = CrewplannerUser(
            user=new_user, access_key=request.POST["crewplanner_key"], stub=request.POST["stub"]
        )
        new_user.save()
        new_cp_user.save()
        employer = staffology_employer(request)
        create_employer(
            new_user,
            request.POST["pay_period"],
            request.POST["tax_year"],
            request.POST["period_end"],
            request.POST["payment_date"],
            employer,
        )
        return redirect("/onboard?user_created=true")


@user_passes_test(lambda u: u.is_superuser)
def create_staffology_user(request):
    try:
        StaffologyUser.objects.get(user=request.user)
        return redirect("/?staffology_connected_already=true")
    except StaffologyUser.DoesNotExist:
        new_staffology_user = StaffologyUser(user=request.user, staffology_key=request.POST["staffology_key"])
        new_staffology_user.save()
        return redirect("/?staffology_connected_success=true")
