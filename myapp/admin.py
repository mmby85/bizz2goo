from django.contrib import admin
from django import forms
from .models import Post, Comment, Contact, AuthorProfile, CKPost, SubCategory, Category, Advertisement
from ckeditor.widgets import CKEditorWidget
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

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
    list_display = ('title', 'user', 'category', 'time')  # Display user
    list_filter = ('category', 'time', 'user')  # Filter by category and user
    search_fields = ('title', 'content', 'user__username', 'user__email') # Search by post title/content and author's username/email

# Define an inline class for AuthorProfile
class AuthorProfileInline(admin.StackedInline):
    model = AuthorProfile
    can_delete = False
    verbose_name_plural = 'Author Profile'
    fk_name = 'user'  # Explicitly specify the foreign key

# blog/admin.py
@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'created_at', 'url')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'url')
    list_editable = ('is_active',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('title', 'image', 'url', 'is_active')
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

# Extend the UserAdmin to include the AuthorProfile inline
class CustomUserAdmin(UserAdmin):
    inlines = (AuthorProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_author')
    list_filter = ('is_staff', 'is_active', 'authorprofile__is_author')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    #Add custom field of 'is_author'
    def is_author(self, obj):
        return obj.authorprofile.is_author
    is_author.boolean = True
    is_author.short_description = 'Is Author'


# Unregister the original UserAdmin
admin.site.unregister(User)

# Register the User model with the custom admin
admin.site.register(User, CustomUserAdmin)
admin.site.register(CKPost, PostAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Contact)
admin.site.register(Category)
admin.site.register(SubCategory)
#admin.site.register(AuthorProfile)  # Registered in UserAdmin

admin.site.site_header = 'BLOGSPOT | ADMIN PANEL'
admin.site.site_title = 'BLOGSPOT | BLOGGING WEBSITE'
admin.site.index_title = 'BlogSpot Site Administration'