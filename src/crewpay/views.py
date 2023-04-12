from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import redirect, render
from rest_framework.authtoken.models import Token

from crewpay.models import CrewplannerUser


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def root(request):
    if not request.user.is_authenticated:
        failed = False
        if "login_failed" not in request.session:
            request.session["login_failed"] = False
        else:
            failed = True
            request.session.pop("login_failed")

        return render(request, "not_logged_in/root.html", {"is_login_failed": failed})

    return render(request, "logged_in/root.html")


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
def user_created(request):
    return render(request, "logged_in/user_created.html")


@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    new_user = User(username=request.POST["stub"], password=User.objects.make_random_password())
    new_cp_user = CrewplannerUser(user=new_user, access_key=request.POST["crewplanner_key"], stub=request.POST["stub"])
    new_user.save()
    new_cp_user.save()
    return redirect("user_created")
