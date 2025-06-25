from django import forms
from .models import DataSource
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class DataSourceForm(forms.ModelForm):
    class Meta:
        model   = DataSource
        exclude = ("owner",)
        labels  = {
            "alias"      : "Alias",
            "engine"     : "Engine",
            "host"       : "DB Host",
            "port"       : "Port",
            "name"       : "Database / Schema",
            "user"       : "User",
            "password"   : "Password",
            "sql"        : "SQL query",
            "ts_column"  : "Timestamp Column",
            "series_cols": "Series Column(s)",
            "is_active"  : "Active?",
        }

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.helper = FormHelper()
        self.helper.form_class  = "row g-3"
        self.helper.label_class = "col-sm-4 col-form-label text-sm-end"
        self.helper.field_class = "col-sm-8"
        self.helper.add_input(Submit("submit", "Save"))