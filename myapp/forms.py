from django import forms

from ckeditor.fields import RichTextFormField
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.fields import RichTextUploadingFormField
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import CKPost , Category, SubCategory


from django.forms import MultiWidget


class CkEditorMultiWidget(MultiWidget):
    def decompress(self, value):
        return [value for _ in self.widgets]

class CkEditorForm(forms.Form):
    ckeditor_standard_example = RichTextFormField()
    # ckeditor_upload_example = RichTextUploadingFormField(
    #     config_name="my-custom-toolbar"
    # )


class CkEditorMultiWidgetForm(forms.Form):
    SUBWIDGET_SUFFIXES = ["0", "1"]

    ckeditor_standard_multi_widget_example = forms.CharField(
        widget=CkEditorMultiWidget(
            widgets={suffix: CKEditorWidget for suffix in SUBWIDGET_SUFFIXES},
        ),
    )
    # ckeditor_upload_multi_widget_example = forms.CharField(
    #     widget=CkEditorMultiWidget(
    #         widgets={
    #             suffix: CKEditorUploadingWidget(config_name="my-custom-toolbar")
    #             for suffix in SUBWIDGET_SUFFIXES
    #         },
    #     ),
    # )


class CKPostForm(forms.ModelForm):
    class Meta:
        model = CKPost
        fields = '__all__'
        exclude = ['slug']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrage dynamique des sous-catégories
        if 'category' in self.data:
            try:
                category_id = int(self.data.get('category'))
                self.fields['sub_category'].queryset = SubCategory.objects.filter(category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['sub_category'].queryset = SubCategory.objects.none()
        elif self.instance.pk and self.instance.category:
            self.fields['sub_category'].queryset = self.instance.category.subcategories.order_by('name')
        else:
            self.fields['sub_category'].queryset = SubCategory.objects.none()

        # Option par défaut pour les sous-catégories
        self.fields['sub_category'].empty_label = "Sélectionnez une sous-catégorie"

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        sub_category = cleaned_data.get("sub_category")

        # Validation que la sous-catégorie appartient bien à la catégorie
        if sub_category and sub_category.category != category:
            self.add_error('sub_category', "La sous-catégorie ne correspond pas à la catégorie sélectionnée.")

        return cleaned_data


# class CKPostOverriddenWidgetForm(forms.ModelForm):
#     class Meta:
#         model = CKPost
#         fields = "__all__"

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.fields["content"].widget = CKEditorUploadingWidget(
#             config_name="my-custom-toolbar",
#             extra_plugins=["someplugin", "anotherplugin"],
#             external_plugin_resources=[
#                 (
#                     "someplugin",
#                     "/static/path/to/someplugin/",
#                     "plugin.js",
#                 )
#             ],
#         )

