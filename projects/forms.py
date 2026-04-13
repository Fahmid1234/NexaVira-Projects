from django import forms

from clients.models import Client

from .models import Project, ProjectComment

CONTROL = (
    "block w-full min-h-[2.75rem] rounded-xl border-2 border-slate-200 bg-white px-4 py-2.5 text-sm "
    "text-slate-900 shadow-sm transition duration-150 placeholder:text-slate-400 "
    "hover:border-slate-300 focus:border-indigo-500 focus:outline-none focus:ring-4 focus:ring-indigo-500/20 "
    "disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-500"
)


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["client", "title", "budget", "start_date", "deadline", "status"]
        widgets = {
            "client": forms.Select(attrs={"class": f"{CONTROL} cursor-pointer"}),
            "title": forms.TextInput(attrs={"class": CONTROL, "placeholder": "Project name"}),
            "budget": forms.NumberInput(
                attrs={"class": CONTROL, "step": "0.01", "placeholder": "0.00", "min": "0"}
            ),
            "start_date": forms.DateInput(
                attrs={"class": f"{CONTROL} cursor-pointer", "type": "date"}
            ),
            "deadline": forms.DateInput(
                attrs={"class": f"{CONTROL} cursor-pointer", "type": "date"}
            ),
            "status": forms.Select(attrs={"class": f"{CONTROL} cursor-pointer"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = Client.objects.order_by("name")


class CommentForm(forms.ModelForm):
    class Meta:
        model = ProjectComment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={
                "class": f"{CONTROL} min-h-[120px] resize-none",
                "placeholder": "Add a comment...",
                "rows": 4,
            }),
        }
        labels = {
            "content": "Comment",
        }


