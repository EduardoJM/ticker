import json
from django import forms
from django.conf import settings
from django.contrib.admin import filters
from django.contrib.admin.utils import get_model_from_relation

class AutocompleteRelatedFilterMixin:
    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        js = [
            "admin/js/vendor/jquery/jquery%s.js" % extra,
            "admin/js/vendor/select2/select2.full%s.js" % extra,
            "admin/js/jquery.init.js",
            "admin/js/autocomplete.js",
            "admin/js/autocomplete_related_filter.js",
        ]
        css = {
            "all": [
                "admin/css/vendor/select2/select2%s.css" % extra,
                "admin/css/autocomplete.css",
            ]
        }
        return forms.Media(js=js, css=css)

class AutocompleteRelatedFilter(filters.FieldListFilter):
    template = 'admin/filters/autocomplete_related_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path) -> None:
        self.model = model
        self.model_admin = model_admin
        self.other_model = get_model_from_relation(field)

        self.lookup_kwarg = field_path

        params_value = params.get(self.lookup_kwarg)
        if params_value:
            self.lookup_val = params_value[0]
        else:
            self.lookup_val = None
        
        super().__init__(field, request, params, model, model_admin, field_path)

        if hasattr(model_admin, f"{field_path}_title"):
            self.title = getattr(model_admin, f"{field_path}_title")

    def expected_parameters(self):
        return [self.lookup_kwarg]
    
    def get_object_display_string(self, obj):
        if hasattr(obj, 'filter_autocomplete_name'):
            return obj.filter_autocomplete_name
        return str(obj)
    
    def choices(self, changelist):
        if not self.lookup_val:
            return []
        
        try:
            obj = self.other_model.objects.get(pk=self.lookup_val)

            yield {
                'selected': True,
                'query_string': changelist.get_query_string({self.lookup_kwarg: self.lookup_val}, []),
                'display': self.get_object_display_string(obj),
            }
        except self.other_model.DoesNotExist:
            return []

    def get_dependencies(self):
        if not hasattr(self.model_admin, f"{self.field_path}_depends"):
            return []
        return getattr(self.model_admin, f"{self.field_path}_depends")
    
    @property
    def context(self):
        model = self.field.model

        return {
            'app_label': model._meta.app_label,
            'model_name': model._meta.model_name,
            'field_name': self.field.name,
            'field_path': self.field_path,
            'dependencies': json.dumps(self.get_dependencies()),
        }

def custom_titled_filter(title):
    #https://stackoverflow.com/questions/17392087/how-to-modify-django-admin-filters-title

    class Wrapper(filters.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = filters.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper
