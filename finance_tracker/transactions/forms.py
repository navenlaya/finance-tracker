from django import forms

# Form for uploading CSV files containing transactions
class UploadCSVForm(forms.Form):
    csv_file = forms.FileField()