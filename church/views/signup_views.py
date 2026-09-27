from django.contrib.auth import login
from django.shortcuts import redirect, render

from church.forms import ChurchSignupForm


def church_signup(request):
    """Public signup: creates a church and its first coordinator."""
    if request.user.is_authenticated:
        return redirect("home")

    form = ChurchSignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        church, user = form.save()
        login(request, user)
        return redirect("admin_dashboard")

    return render(request, "signup/church_signup.html", {"form": form})
