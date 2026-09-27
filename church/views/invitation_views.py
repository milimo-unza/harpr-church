from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from church.models import Invitation, Membership, Person


def accept_invitation(request, token):
    invitation = get_object_or_404(Invitation, token=token)

    # Already-accepted state: the invitation has been used before.
    if invitation.accepted_at:
        return render(
            request,
            "signup/invitation_invalid.html",
            {"invitation": invitation, "already_accepted": True},
        )

    # Expired or otherwise invalid state.
    if not invitation.is_valid():
        return render(
            request,
            "signup/invitation_invalid.html",
            {"invitation": invitation, "already_accepted": False},
        )

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        phone = request.POST.get("phone", "").strip()

        error = None
        if not username:
            error = "Username is required."
        elif not first_name:
            error = "First name is required."
        elif not last_name:
            error = "Last name is required."
        elif not phone:
            error = "Phone number is required."
        elif User.objects.filter(username=username).exists():
            error = "That username is taken."
        elif password1 != password2:
            error = "The two passwords don't match."
        elif len(password1) < 8:
            error = "Password must be at least 8 characters."

        if error:
            return render(
                request,
                "signup/accept_invitation.html",
                {"invitation": invitation, "error": error},
            )

        user = User.objects.create_user(
            username=username,
            email=invitation.email,
            first_name=first_name,
            last_name=last_name,
            password=password1,
        )

        Membership.objects.create(
            user=user,
            church=invitation.church,
            role=invitation.role,
            department=invitation.department,
            invited_by=invitation.invited_by,
        )

        full_name = f"{first_name} {last_name}".strip()
        Person.objects.create(
            church=invitation.church,
            name=full_name or username,
            phone=phone,
            email=invitation.email,
            user=user,
        )

        invitation.accepted_at = timezone.now()
        invitation.save()

        login(request, user)
        return redirect("home")

    return render(
        request,
        "signup/accept_invitation.html",
        {"invitation": invitation},
    )
