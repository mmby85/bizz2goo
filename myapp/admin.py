from django.contrib import admin
from django import forms
from .models import Post,Comment,Contact
from ckeditor.widgets import CKEditorWidget

from .models import CKPost , SubCategory , Category

class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = CKPost
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajoutez les classes CSS ici
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['sub_category'].widget.attrs.update({'class': 'form-control'})
        self.fields['content'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['slug'].widget.attrs.update({'class': 'form-control'})

class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm




admin.site.register(CKPost, PostAdmin)

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Contact)
admin.site.register(Category)
admin.site.register(SubCategory)


admin.site.site_header = 'BLOGSPOT | ADMIN PANEL'
admin.site.site_title = 'BLOGSPOT | BLOGGING WEBSITE'
admin.site.index_title= 'BlogSpot Site Administration'
