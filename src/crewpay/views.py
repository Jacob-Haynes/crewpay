from typing import Tuple

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from crewpay.forms import EmployerForm
from crewpay.models import Employer
from crewpay.settings import CREWPAY_VERSION


def to_camel_case(snake_str: str) -> str:
    """Snake to camel case for interfacing"""
    return " ".join(x.capitalize() for x in snake_str.lower().split("_"))


def get_employer_choices() -> Tuple:
    """Used for populating the employer selector dropdown."""
    employers = Employer.objects.all()
    result = tuple([(0, "")] + [(employer.id, employer.user) for employer in employers])
    return result


def root(request: WSGIRequest) -> HttpResponse:
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
    employer_selector.fields["employer"].choices = get_employer_choices()  # type: ignore[attr-defined]
    context["employer_selector"] = employer_selector

    return render(request, "logged_in/root.html", context)


def login_view(request: WSGIRequest) -> HttpResponseRedirect:
    user = authenticate(username=request.POST["username"], password=request.POST["password"])
    if user is None:
        request.session["login_failed"] = True
        return redirect("root")

    login(request, user)
    return redirect("root")


def logout_view(request: WSGIRequest) -> HttpResponseRedirect:
    logout(request)
    return redirect("root")


@login_required(login_url="/")
def onboard(request: WSGIRequest) -> HttpResponse:
    if "user_exists" in request.GET:
        context = {"user_exists": True}
    elif "user_created" in request.GET:
        context = {"user_created": True}
    else:
        context = {}

    employer_selector = EmployerForm()
    employer_selector.fields["employer"].choices = get_employer_choices()  # type: ignore[attr-defined]
    context["employer_selector"] = employer_selector  # type: ignore[assignment]

    return render(request, "logged_in/onboard.html", context)


@login_required(login_url="/")
def about(request: WSGIRequest) -> HttpResponse:
    return render(request, "logged_in/about.html", {"version": CREWPAY_VERSION})


@login_required(login_url="/")
def contact(request: WSGIRequest) -> HttpResponse:
    return render(request, "logged_in/contact.html")


@login_required(login_url="/")
def settings(request: WSGIRequest) -> HttpResponse:
    context = {}
    employer_selector = EmployerForm()
    employer_selector.fields["employer"].choices = get_employer_choices()  # type: ignore[attr-defined]
    context["employer_selector"] = employer_selector
    return render(request, "logged_in/settings.html", context)


@user_passes_test(lambda u: u.is_superuser)  # type: ignore[union-attr]
def create_user(request: WSGIRequest) -> HttpResponseRedirect:
    return redirect("/onboard?user_created=true")


@user_passes_test(lambda u: u.is_superuser)  # type: ignore[union-attr]
def sync_employees_view(request: WSGIRequest) -> HttpResponse:
    return render(request, "logged_in/sync.html", {})


@user_passes_test(lambda u: u.is_superuser)  # type: ignore[union-attr]
def run_payroll_view(request: WSGIRequest) -> HttpResponse:
    return render(request, "logged_in/payroll.html", {})
