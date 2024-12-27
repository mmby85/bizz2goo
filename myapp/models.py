from django.db import models
from django.contrib.auth.models import User
from datetime import datetime  
from ckeditor.fields import RichTextField
from django.utils.text import slugify

now =  datetime.now()
time = now.strftime("%d %B %Y")
# Create your models here.

class Post(models.Model):
    postname = models.CharField(max_length=600)
    category = models.CharField(max_length=600)
    image = models.ImageField(upload_to='images/posts',blank=True,null=True)
    content = models.CharField(max_length=100000)
    time = models.CharField(default=time,max_length=100, blank=True)
    likes = models.IntegerField(null=True,blank=True,default=0)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    
    def __str__(self):
        return str( self.postname)





class Category(models.Model):
    name = models.CharField(max_length=600, blank=True, null=True)
    
    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories", blank=True, null=True)
    name = models.CharField(max_length=600)

    def __str__(self):
        return self.name

class CKPost(models.Model):
    title = models.CharField(max_length=600)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="posts", blank=True, null=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, blank=True, null=True)
    content = RichTextField()
    slug = models.SlugField(default="",max_length=200, unique=True, blank=True , null=False)
    image = models.ImageField(upload_to='images/posts', blank=True, null=True)
    likes = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE , blank=True, null=True)
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
        limit_choices_to={'is_staff': True}  # Limite aux utilisateurs administrateurs
    )
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='author_pictures/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    metier= models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Author Profile: {self.user.username}"
    