from django import forms
from django.forms import DateInput


class VehicleUserDataForm(forms.Form):
    insurance_rate = forms.DecimalField()
    insurance_provider = forms.CharField(max_length=100)
    insurance_renewal_date = forms.DateField(widget=DateInput(attrs={'type': 'date'}))
    financing_interest_rate = forms.DecimalField()
    financing_term_end = forms.DateField(widget=DateInput(attrs={'type': 'date'}))
    previous_maintenance_data = forms.CharField(widget=forms.Textarea)
