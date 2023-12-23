from django import forms

class InvoiceForm(forms.Form):
    height = forms.DecimalField(widget=forms.NumberInput(attrs={"class": "form-control"}))
    width = forms.DecimalField(widget=forms.NumberInput(attrs={"class": "form-control"}))