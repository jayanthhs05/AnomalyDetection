from django import forms
from .models import DataSource, DetectorConfig
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class DataSourceForm(forms.ModelForm):
    threshold   = forms.FloatField(initial=0.0, help_text="Anomaly cutoff")
    sensitivity = forms.FloatField(initial=0.02)
    batch_size  = forms.IntegerField(initial=5_000, min_value=100)
    enabled     = forms.BooleanField(initial=True, required=False)
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

    def save(self, commit=True):
        ds = super().save(commit)
        cfg, _ = DetectorConfig.objects.get_or_create(datasource=ds)
        cfg.threshold   = self.cleaned_data["threshold"]
        cfg.sensitivity = self.cleaned_data["sensitivity"]
        cfg.batch_size  = self.cleaned_data["batch_size"]
        cfg.enabled     = self.cleaned_data["enabled"]
        cfg.save()
        return ds