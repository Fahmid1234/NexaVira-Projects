from django.contrib.auth.mixins import AccessMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse


class CeoRequiredMixin(AccessMixin):
    """
    Internal app: only the CEO (superuser) may access protected views.
    """

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        if not request.user.is_active or not request.user.is_superuser:
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

