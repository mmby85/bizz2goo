# blog/admin.py

from django.contrib import admin
from django import forms
from .models import Post, Comment, Contact, AuthorProfile, CKPost, SubCategory, Category, Advertisement
from ckeditor.widgets import CKEditorWidget
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html # For custom JS in admin form

class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = CKPost
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-control'})
        self.fields['sub_category'].widget.attrs.update({'class': 'form-control'})
        self.fields['content'].widget.attrs.update({'class': 'form-control'}) # content already uses CKEditorWidget
        self.fields['image'].widget.attrs.update({'class': 'form-control-file'})
        self.fields['slug'].widget.attrs.update({'class': 'form-control'})

class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ('title', 'user', 'category', 'time')
    list_filter = ('category', 'time', 'user')
    search_fields = ('title', 'content', 'user__username', 'user__email')
    prepopulated_fields = {'slug': ('title',)} # Auto-populate slug from title

class AuthorProfileInline(admin.StackedInline):
    model = AuthorProfile
    can_delete = False
    verbose_name_plural = 'Author Profile'
    fk_name = 'user'

class AdvertisementAdminForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # JavaScript to show/hide category based on position
        # This makes 'category' field more prominent when needed
        self.fields['position'].widget.attrs['onchange'] = (
            "var categoryRow = document.querySelector('.field-category');"
            "if (this.value === 'bottom_banner_category' || this.value === 'sidebar') {"
            "  categoryRow.style.display = '';"
            "} else {"
            "  categoryRow.style.display = 'none';"
            "}"
        )
    
    # Include the script in the form's media
    class Media:
        js = ('admin/js/jquery.init.js', 'admin/js/dynamic_form_fields.js') # Example, ensure these paths are correct or provide inline script

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    form = AdvertisementAdminForm # Use the custom form
    list_display = ('title', 'position', 'link_type', 'category', 'is_active', 'display_order', 'created_at')
    list_filter = ('is_active', 'position', 'category', 'link_type')
    search_fields = ('title',)
    fieldsets = (
        (None, {
            'fields': ('title', 'image', 'is_active', 'position', 'display_order')
        }),
        ('Lien de l\'annonce', {
            'fields': ('link_type', 'external_url'),
            'description': ("Si 'Formulaire Interne' est choisi, l'URL externe sera ignorée. "
                           "Si 'Lien Externe' est choisi, l'URL externe est requise.")
        }),
        ('Ciblage par Catégorie', { # Changed title for clarity
            # 'classes': ('collapse',), # Keep it always visible for now or use JS to control
            'fields': ('category',),
            'description': ("Requis pour 'Bottom Banner Category'. Optionnel pour 'Sidebar Ad' "
                           "pour cibler une catégorie spécifique. Laisser vide pour les 'Sidebar Ad' généraux.")
        }),
    )
    list_editable = ('is_active', 'display_order')

    # To make the JavaScript work on add page as well, we can add it here
    # or ensure the onchange attribute on the widget fires correctly initially.
    # A more robust way is using a custom admin/js/dynamic_form_fields.js file.
    # For now, the onchange on the widget itself should work for edits.
    # For initial load of add page, the category field might be hidden if default position doesn't require it.
    # We can add a small script to the template or use a more complex JS solution.
    # A simpler approach is to ensure the default 'position' or the form init correctly sets visibility.

    # Let's ensure the category field is initially shown/hidden correctly based on initial position
    # This is better handled via custom JS in form.Media or admin template override.
    # For simplicity here, the onchange on the widget covers edit.
    # Admin users will need to select position first on 'add' page for category to show/hide.

class CustomUserAdmin(UserAdmin):
    inlines = (AuthorProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'get_is_author') # Renamed for consistency
    list_filter = ('is_staff', 'is_active', 'authorprofile__is_author')
    fieldsets = UserAdmin.fieldsets # Use default UserAdmin fieldsets
    add_fieldsets = UserAdmin.add_fieldsets # Use default UserAdmin add_fieldsets


    def get_is_author(self, obj):
        if hasattr(obj, 'authorprofile'):
            return obj.authorprofile.is_author
        return False
    get_is_author.boolean = True
    get_is_author.short_description = 'Is Author'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)

# --- Registration ---
admin.site.unregister(User) # Unregister default User admin
admin.site.register(User, CustomUserAdmin) # Register with custom admin

admin.site.register(CKPost, PostAdmin)
admin.site.register(Post) # Assuming this is your old Post model, keep if needed, otherwise remove
admin.site.register(Comment)
admin.site.register(Contact)
# admin.site.register(AuthorProfile) # This is handled by the inline in CustomUserAdmin

admin.site.site_header = 'GOZONE | ADMIN PANEL' # Updated name
admin.site.site_title = 'GOZONE | Content Management' # Updated name
admin.site.index_title = 'GoZone Site Administration' # Updated name