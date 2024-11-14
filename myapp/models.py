from django.db import models
from django.contrib.auth.models import User
from datetime import datetime  
from ckeditor.fields import RichTextField

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


#@Islem implement the model + update the form in forms.py + @Walid upadte the form in html
from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

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
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    image = models.ImageField(upload_to='images/posts', blank=True, null=True)
    likes = models.IntegerField(null=True, blank=True, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True, blank=True)  # Automatically set the time created
    def __str__(self):
        return self.title
      
    


class Comment(models.Model):
    content = models.CharField(max_length=200)
    time = models.CharField(default=time,max_length=100, blank=True)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return  f"{self.id}.{self.content[:20]}..."
    
    

class Contact(models.Model):
    name = models.CharField(max_length=600)
    email = models.EmailField(max_length=600)
    subject = models.CharField(max_length=1000)
    message = models.CharField(max_length=10000, blank=True)