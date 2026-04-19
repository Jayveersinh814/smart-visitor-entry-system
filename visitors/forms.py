from django import forms
from django.contrib.auth.models import User
from .models import Gate, VisitorPass


def apply_bootstrap_widget_classes(form: forms.BaseForm) -> None:
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault("class", "form-check-input")
        elif isinstance(widget, forms.Select):
            widget.attrs.setdefault("class", "form-select")
        else:
            widget.attrs.setdefault("class", "form-control")


class VisitorPassForm(forms.ModelForm):
    class Meta:
        model = VisitorPass
        fields = [
            "visitor_name",
            "phone_number",
            "email",
            "id_proof",
            "purpose",
            "host",
            "reference_by",
            "visitor_type",
            "valid_from",
            "valid_until",
            "is_multi_entry",
        ]
        widgets = {
            "valid_from": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "valid_until": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "purpose": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["host"].queryset = User.objects.filter(is_active=True).order_by("first_name", "username")
        apply_bootstrap_widget_classes(self)


class ApprovalForm(forms.Form):
    decision = forms.ChoiceField(choices=[("approved", "Approve"), ("rejected", "Reject")])
    note = forms.CharField(max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widget_classes(self)


class ScanForm(forms.Form):
    qr_token = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}), help_text="Paste scanned QR token")
    gate = forms.ModelChoiceField(queryset=Gate.objects.filter(is_active=True))
    action = forms.ChoiceField(choices=[("entry", "Entry"), ("exit", "Exit")])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_bootstrap_widget_classes(self)
