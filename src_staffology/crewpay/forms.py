from django import forms


class EmployerForm(forms.Form):
    employer = forms.ChoiceField(choices=())
