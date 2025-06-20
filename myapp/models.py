from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.core.validators import URLValidator
from django.urls import reverse # Import reverse


now = datetime.now()
time = now.strftime("%d %B %Y")

choices = (
    ('Technology', 'Technology'),
    ('Science', 'Science'),
    ('Business', 'Business'),
    ('Entertainment', 'Entertainment'),
    ('Sports', 'Sports'),
    ('Politics', 'Politics'),
    ('Health', 'Health'),
)


class Post(models.Model):
    postname = models.CharField(max_length=600)
    category = models.CharField(max_length=600)
    image = models.ImageField(upload_to='images/posts', blank=True, null=True)
    content = models.CharField(max_length=100000)
    time = models.CharField(default=time, max_length=100, blank=True)
    likes = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.postname)

# blog/models.py
# class Advertisement(models.Model):
#     title = models.CharField(max_length=200)
#     image = models.ImageField(upload_to='ads/')
#     url = models.URLField()
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title

class Category(models.Model):
    name = models.CharField(  # Removed 'choices' parameter
        max_length=600,
        blank=True,
        null=True
    )
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(
        upload_to='category_images/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories", blank=True,
                                 null=True)
    name = models.CharField(max_length=600)

    def __str__(self):
        return self.name


class Advertisement(models.Model):
    LINK_TYPE_CHOICES = [
        ('external', 'Lien Externe Personnalisé'),
        ('internal_form_livre', 'Formulaire Interne (Livre Création Société)'), # Renamed for clarity
        ('internal_form_gozone', 'Formulaire Interne (Contact GOZONE)'),   # <<< NEW CHOICE
    ]
    POSITION_CHOICES = [
        ('sidebar', 'Sidebar Ad (Vertical)'),
        ('bottom_banner_home', 'Bottom Banner Home (Horizontal)'),
        ('bottom_banner_category', 'Bottom Banner Category (Horizontal)'),
    ]

    title = models.CharField(max_length=200, help_text="Internal title for the ad.")
    image = models.ImageField(upload_to='ads/', help_text="Image for the advertisement.")

    link_type = models.CharField(
        max_length=30, # Increased length to accommodate longer choice values
        choices=LINK_TYPE_CHOICES,
        default='external',
        help_text="Choisir si l'annonce redirige vers un lien externe ou un formulaire interne."
    )
    external_url = models.URLField(
        blank=True, null=True,
        help_text="URL externe (si 'Lien Externe Personnalisé' est choisi)."
    )

    is_active = models.BooleanField(default=True, help_text="Is this ad currently active?")
    position = models.CharField(
        max_length=50,
        choices=POSITION_CHOICES,
        default='sidebar',
        help_text="Where this ad will be displayed."
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name="advertisements",
        help_text="Required for 'Bottom Banner Category' & optional for 'Sidebar Ad'."
    )
    display_order = models.IntegerField(default=0, help_text="Order of display (lower numbers first).")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"

    def get_absolute_url(self):
        if self.link_type == 'internal_form_livre': # Updated value
            return reverse('lead_generation_form')
        elif self.link_type == 'internal_form_gozone': # <<< NEW
            return reverse('gozone_contact_form') # <<< New URL name we will create
        elif self.link_type == 'external' and self.external_url:
            return self.external_url
        return None

    class Meta:
        ordering = ['position', 'category', 'display_order', '-created_at']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.link_type == 'external' and not self.external_url:
            raise ValidationError({'external_url': "L'URL externe est requise lorsque le type de lien est 'Lien Externe Personnalisé'."})

        if self.position == 'bottom_banner_category' and not self.category:
            raise ValidationError({'category': "Une catégorie doit être associée pour les 'Bottom Banner Category'."})
         
class CKPost(models.Model):
    title = models.CharField(max_length=600)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="posts", blank=True, null=True,
                                 )
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, blank=True, null=True)
    content = RichTextField()
    slug = models.SlugField(default="", max_length=200, unique=True, blank=True, null=False)
    image = models.ImageField(upload_to='images/posts', blank=True, null=True)
    likes = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title) if self.title else self.slug
        original_slug = self.slug
        slug = original_slug
        counter = 1

        while CKPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1

        self.slug = slug
        super().save(*args, **kwargs)


class Comment(models.Model):
    user = models.CharField(max_length=100)
    content = models.TextField()
    post = models.ForeignKey(CKPost, related_name="comments", on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.post.title}"


class Contact(models.Model):
    name = models.CharField(max_length=600)
    email = models.EmailField(max_length=600)
    subject = models.CharField(max_length=1000)
    message = models.CharField(max_length=10000, blank=True)


class AuthorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    is_author = models.BooleanField(default=False) # Add this field
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='author_pictures/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    metier = models.TextField(blank=True, null=True)
    facebook = models.URLField(validators=[URLValidator()], blank=True, null=True)
    twitter = models.URLField(validators=[URLValidator()], blank=True, null=True)
    gmail = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"Author Profile: {self.user.username}"