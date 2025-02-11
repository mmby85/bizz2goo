from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import *
from . import forms
from django.urls import reverse
from django.views import generic
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.db.models import Sum
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.edit import CreateView
import logging

logger = logging.getLogger(__name__)

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

    return render(request, "index.html", {
        'posts': Post.objects.filter(user_id=request.user.id).order_by("id").reverse(),
        'top_posts': Post.objects.all().order_by("-likes"),
        'recent_posts': Post.objects.all().order_by("-id"),
        'user': request.user,
        'media_url': settings.MEDIA_URL,
        'form': form
    })


def new_index(request):
    posts = CKPost.objects.order_by("-time")
    top_posts = CKPost.objects.all().order_by("-likes")[:3]
    recent_posts = CKPost.objects.all().order_by("-time")[:3]
    categories = Category.objects.all()
    all_posts = CKPost.objects.all()
    top_authors = (
        AuthorProfile.objects.annotate(total_likes=Sum('user__ckpost__likes'))
            .order_by('-total_likes')[:2]
    )
    context = {
        'posts': posts,
        'top_posts': top_posts,
        'recent_posts': recent_posts,
        'categories': categories,
        'user': request.user,
        'media_url': settings.MEDIA_URL,
        'all_posts': all_posts,
        'top_authors': top_authors,

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
                messages.info(request, "Username already Exists")
                return redirect('signup')
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email already Exists")
                return redirect('signup')
            else:
                User.objects.create_user(username=username, email=email, password=password).save()
                return redirect('signin')
        else:
            messages.info(request, "Password should match")
            return redirect('signup')

    return render(request, "signup.html")


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("new_index")
        else:
            messages.info(request, 'Username or Password is incorrect')
            return redirect("signin")

    return render(request, "signin.html")


def logout(request):
    auth.logout(request)
    return redirect('index')


def blog(request):
    return render(request, "blog.html", {
        'posts': Post.objects.filter(user_id=request.user.id).order_by("id").reverse(),
        'top_posts': Post.objects.all().order_by("-likes"),
        'recent_posts': Post.objects.all().order_by("-id"),
        'user': request.user,
        'media_url': settings.MEDIA_URL
    })


def create(request):
    if request.method == 'POST':
        try:
            form = forms.CKPostForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                print("Post saved successfully")
                return redirect('post_list')
            else:
                print("Form is not valid:", form.errors)
        except:
            print("Error")
        return redirect('index')
    else:
        category_form = forms.CategoryForm()
        form = forms.CKPostForm()
        return render(request, "blog/create_post.html", context={"form": form, category_form: category_form})


def create_old(request):
    if request.method == 'POST':
        try:
            form = forms.CKPostForm(request.POST)
            if form.is_valid():
                post.user = request.user # 
                form.save()
                return redirect('post_list')
        except:
            print("Error")
        return redirect('index')
    else:
        form = forms.CKPostForm()
        return render(request, "create_old.html", context={"form": form})


def posts_by_category(request, id):
    if id == 'all':
        ckposts = CKPost.objects.all()
    else:
        ckposts = CKPost.objects.filter(category__id=int(id))

    return render(request, 'blog/articlesSWAP_HTMX.html', {'ckposts': ckposts})


def profile(request, username):
    return render(request, 'blog/profile.html', {
        'user_profile': get_object_or_404(User, username=username),
        'posts': CKPost.objects.all(),
        'media_url': settings.MEDIA_URL,
    })


def profileedit(request, username):
    author_profile = get_object_or_404(AuthorProfile, user__username=username)

    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        bio = request.POST.get('bio')
        facebook = request.POST.get('facebook')
        twitter = request.POST.get('twitter')
        gmail = request.POST.get('gmail')

        user = author_profile.user
        user.first_name = firstname
        user.last_name = lastname

        user.save()

        author_profile.bio = bio
        author_profile.facebook = facebook
        author_profile.twitter = twitter
        author_profile.gmail = gmail
        author_profile.save()

        return render(request, "blog/auteur.html", {
            'author_profile': author_profile
        })

    return render(request, "blog/profileedit.html", {
        'author_profile': author_profile
    })


def increaselikes(request, id):
    if request.method == 'POST':
        post = Post.objects.get(id=id)
        post.likes += 1
        post.save()
    return redirect("index")


def removepost(request, id):
    if request.method == 'POST':
        post = Post.objects.get(id=id)
        post.delete()
    return redirect("index")


def post(request, id):  ### BECH TETBADEL CKPOST
    post = Post.objects.get(id=id)

    return render(request, "post-detail.html", {
        "user": request.user,
        'post': Post.objects.get(id=id),
        'recent_posts': Post.objects.all().order_by("-id"),
        'media_url': settings.MEDIA_URL,
        'comments': Comment.objects.filter(post_id=post.id),
        'total_comments': len(Comment.objects.filter(post_id=post.id))
    })


def savecomment(request, id):
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        content = request.POST['message']
        Comment(post_id=post.id, user_id=request.user.id, content=content).save()
        return redirect("index")


def deletecomment(request, id):
    comment = Comment.objects.get(id=id)
    postid = comment.post.id
    comment.delete()
    return post(request, postid)


def editpost(request, id):
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
        return profile(request, request.user.id)

    return render(request, "postedit.html", {
        'post': post
    })


def deletepost(request, id):
    Post.objects.get(id=id).delete()
    return profile(request, request.user.id)


def contact_us(request):
    context = {}
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        obj = Contact(name=name, email=email, subject=subject, message=message)
        obj.save()
        context['message'] = f"Dear {name}, Thanks for your time!"

    return render(request, "contact.html")


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
        logger.debug(f"Request POST data: {request.POST}")
        logger.debug(f"Request FILES data: {request.FILES}")
        form = forms.CKPostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user # <--- This is important 
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect('post_detail', slug=post.slug)
        else:
          logger.error(f"Form errors: {form.errors}")
    
     else:
        form = forms.CKPostForm()

     categories = Category.objects.all()
     return render(request, 'blog/create_post.html', {'form': form, 'categories': categories})

def post_list(request):
    posts = CKPost.objects.all().order_by('-time')

    return render(request, 'blog/post_list.html', {
        'posts': posts,
    })

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
    author_profile = None  # Initialize to None

    # Check if user is staff and has an AuthorProfile
    if post.user.is_staff and hasattr(post.user, 'authorprofile'):
        author_profile = post.user.authorprofile

    related_posts = CKPost.objects.filter(category=post.category).exclude(slug=post.slug)[:3]
    top_level_comments = post.comments.filter(parent__isnull=True)
    media_url = "/media/"

    context = {
        "post": post,
        "author_profile": author_profile,
        "related_posts": related_posts,
        "media_url": media_url,
        "top_level_comments": top_level_comments,
    }
    return render(request, "blog/post-detail.html", context)


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


@csrf_exempt
def add_comment(request):
    if request.method == "POST":
        # Extract form data
        slug = request.POST.get("slug")
        username = request.POST.get("username")
        content = request.POST.get("content")
        parent_id = request.POST.get("parent_id")  # Parent comment ID (if it's a reply)

        # Ensure required fields are present
        if not all([slug, username, content]):
            return JsonResponse({"error": "Missing fields in the form."}, status=400)

        # Get the related post
        post = get_object_or_404(CKPost, slug=slug)

        # Handle parent comment if it's a reply
        parent_comment = None
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)

        # Create the comment
        comment = Comment.objects.create(
            user=username,
            content=content,
            post=post,
            parent=parent_comment
        )

        # Helper function to render a single comment or reply
        def render_comment(comment, is_reply=False):
            if is_reply:
                return render_to_string('blog/reply.html', {'comment': comment, 'request': request})
            else:
                return render_to_string('blog/comment.html', {'comment': comment, 'post': post, 'request': request})

        # Render only the new comment/reply
        comment_html = render_comment(comment, is_reply=bool(parent_id))

        # Determine the target for the response
        if parent_id:
            target = f"#comment-{parent_id} .replies"
        else:
            target = "#comments-container"

        # Return the HTML of all comments for the targeted container
        return HttpResponse(comment_html, content_type="text/html", headers={"HX-Target": target, "HX-Reswap": "beforeend"})

    return JsonResponse({"error": "Invalid request method."}, status=405)


def post_detail(request, slug):
    post = get_object_or_404(CKPost, slug=slug)
    author_profile = None

    if post.user: # Check if post.user exists and is not None
        if post.user.is_staff and isinstance(post.user, User):  # Check if it's an actual user object
            if hasattr(post.user, 'authorprofile'):
                author_profile = post.user.authorprofile

    related_posts = CKPost.objects.filter(category=post.category).exclude(slug=post.slug)[:3]
    top_level_comments = post.comments.filter(parent__isnull=True)
    media_url = "/media/"

    context = {
        "post": post,
        "author_profile": author_profile,
        "related_posts": related_posts,
        "media_url": media_url,
        "top_level_comments": top_level_comments,
    }
    return render(request, "blog/post-detail.html", context)


def author_profile(request, username):
    user = get_object_or_404(User, username=username, is_staff=True)
    profile = get_object_or_404(AuthorProfile, user=user)

    return render(request, 'blog/auteur.html', {'author_profile': profile})

class AuthorProfileCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = AuthorProfile
    fields = ['bio', 'profile_picture', 'website', 'metier', 'facebook', 'gmail', 'twitter']
    template_name = 'blog/author_profile_form.html'
    success_url = '/success/'

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        if AuthorProfile.objects.filter(user=self.request.user).exists():
            form.add_error(None, "Vous avez déjà créé un profil auteur.")
            return self.form_invalid(form)

        form.instance.user = self.request.user
        return super().form_valid(form)