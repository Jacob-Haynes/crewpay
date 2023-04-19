from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import redirect, render
from rest_framework.authtoken.models import Token

from api.v1.staffology.employers import create_employer
from crewpay.forms import EmployerForm
from crewpay.models import CrewplannerUser, StaffologyUser, Employer


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def get_employer_choices():
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

    if "staffology_connected_already" in request.GET:
        context = {"staffology_connected_already": True}
    elif "user_exists" in request.GET:
        context = {"user_exists": True}
    elif "user_created" in request.GET:
        context = {"user_created": True}
    elif "staffology_connected_success" in request.GET:
        context = {"staffology_connected_success": True}
    else:
        context = {}

    form = EmployerForm()
    form.fields['employer'].choices = get_employer_choices()
    context['form'] = form
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
def about(request):
    return render(request, "logged_in/root.html")


@login_required(login_url="/")
def contact(request):
    return render(request, "logged_in/root.html")


@login_required(login_url="/")
def token(request):
    token = Token.objects.get(user__exact=request.user)
    return render(request, "logged_in/token.html", {"token": token})


@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    try:
        CrewplannerUser.objects.get(stub=request.POST["stub"])
        return redirect("/?user_exists=true")
    except CrewplannerUser.DoesNotExist:
        new_user = User(username=request.POST["name"], password=User.objects.make_random_password())
        new_cp_user = CrewplannerUser(
            user=new_user, access_key=request.POST["crewplanner_key"], stub=request.POST["stub"]
        )
        new_user.save()
        new_cp_user.save()
        access_key = StaffologyUser.objects.get(user=request.user).staffology_key
        create_employer(new_user, access_key)
        return redirect("/?user_created=true")


@user_passes_test(lambda u: u.is_superuser)
def create_staffology_user(request):
    try:
        StaffologyUser.objects.get(user=request.user)
        return redirect("/?staffology_connected_already=true")
    except StaffologyUser.DoesNotExist:
        new_staffology_user = StaffologyUser(user=request.user, staffology_key=request.POST["staffology_key"])
        new_staffology_user.save()
        return redirect("/?staffology_connected_success=true")
