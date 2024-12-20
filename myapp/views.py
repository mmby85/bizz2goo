from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import *
from . import forms

from django.urls import reverse
from django.views import generic


from .models import Comment,Post

# Create your views here.
def index(request):
    if request.method == 'POST':
        form = forms.CKPostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post_list')  # Assuming you have a URL for listing posts
    else:
        form = forms.CKPostForm()

    return render(request,"index.html",{
        'posts':Post.objects.filter(user_id=request.user.id).order_by("id").reverse(),
        'top_posts':Post.objects.all().order_by("-likes"),
        'recent_posts':Post.objects.all().order_by("-id"),
        'user':request.user,
        'media_url':settings.MEDIA_URL,
        'form' : form
    })


def new_index(request):
    if request.method == 'POST':
        form = forms.CKPostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post_list')  # Assuming you have a URL for listing posts
    else:
        form = forms.CKPostForm()

    return render(request,"blog/home.html",{
        'posts':Post.objects.filter(user_id=request.user.id).order_by("id").reverse(),
        'top_posts':Post.objects.all().order_by("-likes"),
        'recent_posts':Post.objects.all().order_by("-id"),
        'user':request.user,
        'media_url':settings.MEDIA_URL,
        'form' : form,

    })

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request,"Username already Exists")
                return redirect('signup')
            if User.objects.filter(email=email).exists():
                messages.info(request,"Email already Exists")
                return redirect('signup')
            else:
                User.objects.create_user(username=username,email=email,password=password).save()
                return redirect('signin')
        else:
            messages.info(request,"Password should match")
            return redirect('signup')
            
    return render(request,"signup.html")

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect("index")
        else:
            messages.info(request,'Username or Password is incorrect')
            return redirect("signin")
            
    return render(request,"signin.html")

def logout(request):
    auth.logout(request)
    return redirect('index')

def blog(request):
    return render(request,"blog.html",{
            'posts':Post.objects.filter(user_id=request.user.id).order_by("id").reverse(),
            'top_posts':Post.objects.all().order_by("-likes"),
            'recent_posts':Post.objects.all().order_by("-id"),
            'user':request.user,
            'media_url':settings.MEDIA_URL
        })
    
def create(request):
    if request.method == 'POST':
        try:
            # postname = request.POST['postname']
            # content = request.POST['content']
            # category = request.POST['category']
            # image = request.FILES['image']
            # Post(postname=postname,content=content,category=category,image=image,user=request.user).save()
            form = forms.CKPostForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('post_list')  # Assuming you have a URL for listing posts
        except:
            print("Error")
        return redirect('index')
    else:
        form = forms.CKPostForm()
        return render(request,"create.html" , context={"form" : form})
    
def create_old(request):
    if request.method == 'POST':
        try:
            # postname = request.POST['postname']
            # content = request.POST['content']
            # category = request.POST['category']
            # image = request.FILES['image']
            # Post(postname=postname,content=content,category=category,image=image,user=request.user).save()
            form = forms.CKPostForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('post_list')  # Assuming you have a URL for listing posts
        except:
            print("Error")
        return redirect('index')
    else:
        form = forms.CKPostForm()
        return render(request,"create_old.html" , context={"form" : form})

    
def profile(request,id):
    
    return render(request,'profile.html',{
        'user':User.objects.get(id=id),
        'posts':Post.objects.all(),
        'media_url':settings.MEDIA_URL,
    })
    

def profileedit(request,id):
    if request.method == 'POST':
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
    
        user = User.objects.get(id=id)
        user.first_name = firstname
        user.email = email
        user.last_name = lastname
        user.save()
        return profile(request,id)
    return render(request,"profileedit.html",{
        'user':User.objects.get(id=id),
    })
    
def increaselikes(request,id):
    if request.method == 'POST':
        post = Post.objects.get(id=id)
        post.likes += 1
        post.save() 
    return redirect("index")

def removepost(request,id):
    if request.method == 'POST':
        post = Post.objects.get(id=id)
        post.delete()
    return redirect("index")

def post(request,id):
    post = Post.objects.get(id=id)
    
    return render(request,"post-details.html",{
        "user":request.user,
        'post':Post.objects.get(id=id),
        'recent_posts':Post.objects.all().order_by("-id"),
        'media_url':settings.MEDIA_URL,
        'comments':Comment.objects.filter(post_id = post.id),
        'total_comments': len(Comment.objects.filter(post_id = post.id))
    })
    
def savecomment(request,id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        content = request.POST['message']
        Comment(post_id = post.id,user_id = request.user.id, content = content).save()
        return redirect("index")
    
def deletecomment(request,id):
    comment = Comment.objects.get(id=id)
    postid = comment.post.id
    comment.delete()
    return post(request,postid)
    
def editpost(request,id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        try:
            postname = request.POST['postname']
            content = request.POST['content']
            category = request.POST['category']
            
            post.postname = postname
            post.content = content
            post.category = category
            post.save()
        except:
            print("Error")
        return profile(request,request.user.id)
    
    return render(request,"postedit.html",{
        'post':post
    })
    
def deletepost(request,id):
    Post.objects.get(id=id).delete()
    return profile(request,request.user.id)


def contact_us(request):
    context={}
    if request.method == 'POST':
        name=request.POST.get('name')    
        email=request.POST.get('email')  
        subject=request.POST.get('subject')  
        message=request.POST.get('message')  

        obj = Contact(name=name,email=email,subject=subject,message=message)
        obj.save()
        context['message']=f"Dear {name}, Thanks for your time!"

    return render(request,"contact.html")


# CKEditor
class CkEditorFormView(generic.FormView):
    form_class = forms.CkEditorForm
    template_name = "ckeditor.html"

    def get_success_url(self):
        return reverse("ckeditor-form")

class CkEditorMultiWidgetFormView(generic.FormView):
    form_class = forms.CkEditorMultiWidgetForm
    template_name = "ckeditor.html"

    def get_success_url(self):
        return reverse("ckeditor-multi-widget-form")

def create_post(request):
    if request.method == 'POST':
        form = forms.CKPostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post_list')  # Assuming you have a URL for listing posts
    else:
        form = forms.CKPostForm()
    return render(request, 'ckeditor.html', {'form': form})

def post_list(request):
    posts = CKPost.objects.all()
    print(vars(posts[0]))
    return render(request, 'post_list.html', {'posts': posts})

def edit_post(request, post_id):
    post = CKPost.objects.get(id=post_id)
    if request.method == 'POST':
        form = forms.CKPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_list')  # Replace with your detail view
    else:
        form = forms.CKPostForm(instance=post)
    return render(request, 'create.html', {'form': form})


# @Walid to do post_detail.html
# create view post_detail path('post/<int:post_id>/', views.post_detail, name='post_detail'),
# def post_detail(request, post_id):
#     post = CKPost.objects.get(id=post_id)
#     return render(request, 'post_detail.html', {'post': post})

def home_new(request):
    return render(request, 'blog/base.html')

ckeditor_form_view = CkEditorFormView.as_view()
# ckeditor_multi_widget_form_view = CkEditorMultiWidgetFormView.as_view()