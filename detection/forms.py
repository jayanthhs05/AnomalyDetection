from django import forms
from .models import DataSource


class DataSourceForm(forms.ModelForm):
    class Meta:
        model = DataSource
        fields = "__all__"
