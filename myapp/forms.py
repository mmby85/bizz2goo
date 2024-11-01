from django import forms

from ckeditor.fields import RichTextFormField
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.fields import RichTextUploadingFormField
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import CKPost

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
        fields = "__all__"


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

