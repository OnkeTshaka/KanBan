from django import forms

from .models import Type, Board, Project
from .widgets import ColorInput


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = "__all__"


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
        # exclude = ["slug", "run_date", "preview_url"]


class TypeForm(forms.ModelForm):
    class Meta:
        model = Type
        fields = [
            "name",
            "color",
        ]
        widgets = {
            "color": ColorInput(),
        }
