from django import forms

from .models import Client

# Shared Tailwind classes for accessible, responsive form controls (matches site design system).
CONTROL = (
    "block w-full min-h-[2.75rem] rounded-xl border-2 border-slate-200 bg-white px-4 py-2.5 text-sm "
    "text-slate-900 shadow-sm transition duration-150 placeholder:text-slate-400 "
    "hover:border-slate-300 focus:border-indigo-500 focus:outline-none focus:ring-4 focus:ring-indigo-500/20 "
    "disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-500"
)


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "phone", "messenger_username"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": CONTROL, "placeholder": "Company or contact name", "autocomplete": "organization"}
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": CONTROL,
                    "placeholder": "e.g. 15551234567",
                    "inputmode": "tel",
                    "autocomplete": "tel",
                }
            ),
            "messenger_username": forms.TextInput(
                attrs={"class": CONTROL, "placeholder": "Facebook Messenger username", "autocomplete": "off"}
            ),
        }

