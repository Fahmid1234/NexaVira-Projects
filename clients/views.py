from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.mixins import CeoRequiredMixin

from .forms import ClientForm
from .models import Client


class ClientListView(CeoRequiredMixin, ListView):
    model = Client
    template_name = "clients/list.html"
    context_object_name = "clients"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        q = (self.request.GET.get("q") or "").strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(phone__icontains=q)
                | Q(messenger_username__icontains=q)
            )
        return qs


class ClientCreateView(CeoRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/form.html"
    success_url = reverse_lazy("clients:list")

    def form_valid(self, form):
        messages.success(self.request, "Client created.")
        return super().form_valid(form)


class ClientUpdateView(CeoRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/form.html"
    success_url = reverse_lazy("clients:list")

    def form_valid(self, form):
        messages.success(self.request, "Client updated.")
        return super().form_valid(form)


class ClientDeleteView(CeoRequiredMixin, DeleteView):
    model = Client
    template_name = "clients/confirm_delete.html"
    success_url = reverse_lazy("clients:list")

    def form_valid(self, form):
        messages.success(self.request, "Client deleted.")
        return super().form_valid(form)
