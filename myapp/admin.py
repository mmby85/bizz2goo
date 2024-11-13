from django.contrib import admin
from django import forms
from .models import Post,Comment,Contact
from ckeditor.widgets import CKEditorWidget

from .models import CKPost , SubCategory

class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = CKPost
        fields = ['title', 'category', 'sub_category', 'slug', 'content']


class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "sub_category":
            
            category_id = request.POST.get('category') if request.method == 'POST' else request.GET.get('category')
            
            if category_id:
                try:
                    
                    kwargs["queryset"] = SubCategory.objects.filter(category_id=category_id).order_by('name')
                except (ValueError, TypeError): 
                    kwargs["queryset"] = SubCategory.objects.none() 
            else:
                kwargs["queryset"] = SubCategory.objects.none()  
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(CKPost, PostAdmin)

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Contact)



admin.site.site_header = 'BLOGSPOT | ADMIN PANEL'
admin.site.site_title = 'BLOGSPOT | BLOGGING WEBSITE'
admin.site.index_title= 'BlogSpot Site Administration'
