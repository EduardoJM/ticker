from django import forms

class ImportPaymentEventsForm(forms.Form):
    file = forms.FileField()
