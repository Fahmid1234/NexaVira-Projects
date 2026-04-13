from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import UserProfile


class CeoLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    next_page = reverse_lazy("dashboard:home")

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active or not user.is_superuser:
            messages.error(self.request, "Access denied. CEO account required.")
            return self.form_invalid(form)
        return super().form_valid(form)


def ceo_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("accounts:login")


# Create your views here.
