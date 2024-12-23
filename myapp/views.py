from django.shortcuts import render,redirect , get_object_or_404
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import *
from . import forms

from django.urls import reverse
from django.views import generic
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Comment,Post

convert_category = {
'creation-dentreprise': 'Création d’entreprise',
'management-and-strategie': 'Management & Stratégie',
'technologies': 'Technologies',
'financement-et-startups': 'Financement et Startups',
'gestion-et-conformite': 'Gestion et Conformité',
'competences': 'Compétences',
'events': 'Events',
}


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
    posts = CKPost.objects.order_by("-time")
    top_posts = CKPost.objects.all().order_by("-likes")[:3]
    recent_posts = CKPost.objects.all().order_by("-time")[:3]
    categories = Category.objects.all()
    all_posts = CKPost.objects.all()
    
    context = {
        'posts': posts,
        'top_posts': top_posts,
        'recent_posts': recent_posts,
        'categories': categories,
        'user': request.user,
        'media_url': settings.MEDIA_URL,
        'all_posts': all_posts,
        
    }

    return render(request, "blog/home.html", context)


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
        return render(request,"blog/create_post.html" , context={"form" : form})
    
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


def posts_by_category(request, id):
    
    if id == 'all':
        ckposts = CKPost.objects.all()  # Fetch all CKPosts
    else:
        # id_category = convert_category[category]        
        ckposts = CKPost.objects.filter(category__id=int(id))  # Fetch CKPosts by category
        
    return render(request, 'blog/articlesSWAP_HTMX.html', {'ckposts': ckposts})


def profile(request, id):
    return render(request, 'blog/profile.html', {
        'user_profile': AuthorProfile.objects.get(user__id=id),
        'posts': CKPost.objects.all(),
        'media_url': settings.MEDIA_URL,
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

def post(request,id):             ### BECH TETBADEL CKPOST
    post = Post.objects.get(id=id)
    
    return render(request,"post-detail.html",{
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
        form = forms.CKPostForm(request.POST, request.FILES)  # Inclure les fichiers pour l'image
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect('post_detail', slug=post.slug)
    else:
        form = forms.CKPostForm()

    categories = Category.objects.all()
    return render(request, 'blog/create_post.html', {'form': form, 'categories': categories})

def post_list(request):  
    posts = CKPost.objects.all().order_by('-time')  

    return render(request, 'blog/post_list.html', {
        'posts': posts,  
    })

from django.shortcuts import render, get_object_or_404, redirect
from .models import CKPost
from . import forms

def edit_post(request, slug):
    post = get_object_or_404(CKPost, slug=slug)

    if request.method == 'POST':
        form = forms.CKPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('post_detail', slug=post.slug)
    else:
        form = forms.CKPostForm(instance=post)

    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})



def post_detail(request, slug):
    post = get_object_or_404(CKPost, slug=slug)
    related_posts = CKPost.objects.filter(category=post.category).exclude(slug=post.slug)[:3]
    author_profile = None
    if post.user.is_staff and hasattr(post.user, 'authorprofile'):
        author_profile = post.user.authorprofile
    context = {
        'post': post,
        'related_posts': related_posts,
        'media_url': settings.MEDIA_URL,
        'author_profile': author_profile,
    }
    return render(request, 'blog/post-detail.html', context)

def home_new(request):
    return render(request, 'blog/base.html')

ckeditor_form_view = CkEditorFormView.as_view()
# ckeditor_multi_widget_form_view = CkEditorMultiWidgetFormView.as_view()

def get_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(category_id=category_id)
    return JsonResponse({
        'subcategories': [{'id': sub.id, 'name': sub.name} for sub in subcategories]
    })
    
from django.template.loader import render_to_string
from django.http import HttpResponse



from django.shortcuts import get_object_or_404

@csrf_exempt
def add_comment(request):
    if request.method == "POST":
        # Extraire les données
        slug = request.POST.get("slug")
        username = request.POST.get("username")
        content = request.POST.get("content")
        parent_id = request.POST.get("parent_id")  # ID du commentaire parent (s'il existe)
        
        # Vérification des champs requis
        if not all([slug, username, content]):
            return JsonResponse({"error": "Missing fields in the form."}, status=400)
        
        # Vérifier l'existence du post
        post = get_object_or_404(CKPost, slug=slug)

        # Récupérer le commentaire parent s'il existe
        parent_comment = None
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)

        # Créer le commentaire
        comment = Comment.objects.create(
            user=username,
            content=content,
            post=post,
            
        )

        # Générer le HTML du commentaire (ou de la réponse)
        comment_html = f"""
        <div class="media p-3 border rounded mb-3 bg-white shadow-sm">
          <a class="pull-left" href="#">
            <div class="avatar">
              <img src="/static/assets/images/user.png" alt="{comment.user}" class="media-object" />
            </div>
          </a>
          <div class="media-body">
            <h5 class="media-heading">{comment.user}</h5>
            <h6 class="text-muted">{comment.time.strftime('%B %d, %Y %I:%M %p')}</h6>
            <p>{comment.content}</p>
            <a href="#" class="btn-link pull-right btn btn-info reply-btn" data-comment-id="{comment.id}">
              <i class="fa fa-reply mr-1"></i> Reply
            </a>
          </div>
        </div>
        """
        return HttpResponse(comment_html, content_type="text/html")

    return JsonResponse({"error": "Invalid request method."}, status=405)





# def load_more_comments(request, post_id):
#     post = Post.objects.get(id=post_id)
#     comments = post.comments.all()[3:]  # Skip first 3 comments

#     # Render new comments to send back to the front-end
#     return render(request, 'blog/comment_list.html', {'comments': comments})

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import AuthorProfile

def author_profile(request, username):
    user = get_object_or_404(User, username=username, is_staff=True)  # Vérifie que c'est un administrateur
    profile = get_object_or_404(AuthorProfile, user=user)

    return render(request, 'blog/auteur.html', {'author_profile': profile})


from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.shortcuts import redirect
from .models import AuthorProfile

class AuthorProfileCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = AuthorProfile
    fields = ['bio', 'profile_picture', 'website', 'metier']
    template_name = 'blog/author_profile_form.html'
    success_url = '/success/'  # Redirection après la création

    def test_func(self):
        # Vérifie que l'utilisateur connecté est un administrateur
        return self.request.user.is_staff

    def form_valid(self, form):
        # Vérifie si un profil existe déjà pour l'utilisateur
        if AuthorProfile.objects.filter(user=self.request.user).exists():
            # Retourne une erreur si un profil existe déjà
            form.add_error(None, "Vous avez déjà créé un profil auteur.")
            return self.form_invalid(form)
        
        # Associe automatiquement le profil à l'utilisateur connecté
        form.instance.user = self.request.user
        return super().form_valid(form)
