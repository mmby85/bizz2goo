from django.contrib import admin
from django import forms
from .models import Post,Comment,Contact
from ckeditor.widgets import CKEditorWidget

from .models import CKPost

class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = CKPost
        fields = '__all__'

class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm

admin.site.register(CKPost, PostAdmin)

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Contact)



admin.site.site_header = 'BLOGSPOT | ADMIN PANEL'
admin.site.site_title = 'BLOGSPOT | BLOGGING WEBSITE'
admin.site.index_title= 'BlogSpot Site Administration'
