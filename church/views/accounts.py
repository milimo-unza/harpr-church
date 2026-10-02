from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def delete_my_account(request):
    if request.method == "POST":
        confirm = (request.POST.get("confirm") or "").strip()
        if confirm != request.user.username:
            messages.error(request, "Type your username exactly to confirm.")
            return render(
                request,
                "church/accounts/delete_confirm.html",
                {
                    "username": request.user.username,
                },
            )

        user = request.user
        user.is_active = False
        user.save(update_fields=["is_active"])
        logout(request)
        return redirect("home")

    return render(
        request,
        "church/accounts/delete_confirm.html",
        {
            "username": request.user.username,
        },
    )
