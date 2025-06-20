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
from .permissions import IsAuthor  # Import your custom permission
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .forms import LeadGenerationForm, GozoneContactForm

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


# blog/views.py

def new_index(request):
    categories_qs = Category.objects.all() # For filter buttons
    top_authors = (
        AuthorProfile.objects.filter(is_author=True)
        .annotate(total_likes=Sum('user__ckpost__likes'))
        .order_by('-total_likes')[:6]
    )

    # --- Variables for the template context ---
    ckposts_for_initial_render = CKPost.objects.all().order_by("-time") # Default: All posts
    category_for_hero_and_description = None # Default: Generic hero/description
    top_posts_for_initial_render = CKPost.objects.all().order_by("-likes")[:3] # Default: Top from all
    sidebar_ads_for_initial_render = Advertisement.objects.filter(
        position='sidebar', is_active=True, category__isnull=True # Default: General sidebar ads
    ).order_by('display_order')
    
    # --- Try to load "Featured" category specifically for initial prominent display ---
    try:
        featured_category_obj = Category.objects.get(name__iexact="Featured") # Case-insensitive
        logger.info(f"Found 'Featured' category: {featured_category_obj.name}")
        
        featured_posts = CKPost.objects.filter(category=featured_category_obj).order_by("-time")
        if featured_posts.exists():
            logger.info("'Featured' category has posts. Using it for initial display.")
            ckposts_for_initial_render = featured_posts
            category_for_hero_and_description = featured_category_obj # Use Featured for hero/desc
            top_posts_for_initial_render = CKPost.objects.filter(category=featured_category_obj).order_by("-likes")[:3]
            if not top_posts_for_initial_render.exists():
                 top_posts_for_initial_render = featured_posts.order_by("-likes")[:3]

            featured_sidebar_ads = Advertisement.objects.filter(
                position='sidebar', is_active=True, category=featured_category_obj
            ).order_by('display_order')
            if featured_sidebar_ads.exists():
                sidebar_ads_for_initial_render = featured_sidebar_ads
            
        else:
            logger.info("'Featured' category exists but has no posts. Defaulting to general view for hero/description, and all posts.")
            # All defaults (generic hero/desc, all posts, general sidebar) remain.
            
    except Category.DoesNotExist:
        logger.info("'Featured' category not found. Defaulting to general view for hero/description, and all posts.")
        # All defaults remain.

    # --- DYNAMIC CATEGORY AD CONTAINER: Empty on initial load ---
    # Pass an empty queryset for the initial state of bottom category ads.
    initial_bottom_category_ads_list = Advertisement.objects.none() 
    logger.info("The #dynamic-category-ad-container will be initially empty (no category-specific ads).")

    # --- General "bottom of home page" ad (this is a separate, single ad) ---
    bottom_home_ad_main_general = Advertisement.objects.filter(
        position='bottom_banner_home', is_active=True
    ).order_by('display_order', '?').first() # This remains .first() as it's a single slot

    context = {
        'categories': categories_qs,
        'top_authors': top_authors,
        'media_url': settings.MEDIA_URL,
        
        'ckposts': ckposts_for_initial_render,
        'category': category_for_hero_and_description, # For hero/description sections
        'sidebar_ads': sidebar_ads_for_initial_render, # List of sidebar ads
        'top_posts': top_posts_for_initial_render,
        
        # For the dynamic category-specific ads (plural name)
        'bottom_category_ads_initial': initial_bottom_category_ads_list, 
        
        # For the single general ad at the very bottom of the home page
        'bottom_home_ad': bottom_home_ad_main_general,
    }
    return render(request, "blog/home.html", context)

# blog/views.py

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
            else:
                User.objects.create_user(username=username, email=email, password=password).save()
                return redirect('signin')
        else:
            messages.info(request, "Password should match")
            return redirect('signup')

    return render(request, "signup.html")


def get_category_ad_snippet_htmx(request):
    # 1. Get category_id from query parameter
    category_id_from_request = request.GET.get('category_id', 'all') 
    logger.info(f"get_category_ad_snippet_htmx received category_id: {category_id_from_request}")

    bottom_ad_to_display = None # Initialize
    
    # 2. Check if we are looking for a specific category's ad or the "all" case
    if category_id_from_request and category_id_from_request.lower() != 'all':
        try:
            # 3. Convert ID to integer and fetch Category object
            cat_id_int = int(category_id_from_request)
            target_category = get_object_or_404(Category, id=cat_id_int)
            logger.info(f"Target category for ad: {target_category.name}")

            # 4. Fetch the corresponding advertisement
            bottom_ad_to_display = Advertisement.objects.filter(
                position='bottom_banner_category', # Make sure this 'position' string matches your Advertisement model
                is_active=True,
                category=target_category # Filter by the specific category object
            ).order_by('display_order', '?').first() # '?' for random if multiple with same order

            if bottom_ad_to_display:
                logger.info(f"Ad found for category '{target_category.name}': {bottom_ad_to_display.title}")
            else:
                logger.info(f"No 'bottom_banner_category' ad found for category: {target_category.name}")

        except ValueError:
            # category_id_from_request was not a valid integer (e.g., if something other than 'all' or a number was passed)
            logger.warning(f"Invalid category_id format '{category_id_from_request}' received for ad snippet. It's not 'all' and not an integer.")
            # bottom_ad_to_display remains None
        except Category.DoesNotExist:
            logger.warning(f"Category with id '{category_id_from_request}' not found for ad snippet.")
            # bottom_ad_to_display remains None
    else:
        # Case: category_id_from_request is 'all' or was not provided (defaulted to 'all')
        # For "all" articles, we typically don't show a specific category's bottom ad.
        # So, bottom_ad_to_display remains None.
        # If you HAD a default ad for the "all" view, you would fetch it here, e.g.:
        # bottom_ad_to_display = Advertisement.objects.filter(position='bottom_banner_category', is_active=True, is_default_for_all=True).first()
        logger.info("Request for 'all' category ad, or no category_id provided. No specific category ad will be shown.")
            
    # 5. Render the snippet template
    return render(request, 'blog/partials/category_bottom_ad_snippet.html', {
        'bottom_category_ad': bottom_ad_to_display # Pass the fetched ad (or None) to the template
    })

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("index")
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
            form = forms.CKPostForm(request.POST, request.FILES)
            if form.is_valid():
                post.user = request.user  #
                form.save()
                print(form, form.user)
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
                post.user = request.user  #
                form.save()
                return redirect('post_list')
        except:
            print("Error")
        return redirect('index')
    else:
        form = forms.CKPostForm()
        return render(request, "create_old.html", context={"form": form})


# blog/views.py

def posts_by_category(request, id): # id is category_id string or 'all'
    media_url = settings.MEDIA_URL
    all_categories_for_filters = Category.objects.all() # For the filter buttons
    
    category_for_template = None # For hero/description sections
    ckposts_list = CKPost.objects.all() 
    top_posts_list = CKPost.objects.none() 
    sidebar_ads_list = Advertisement.objects.none() 
    
    # This will be a list/queryset of ads for the 'bottom_banner_category' position
    bottom_category_ads_list = Advertisement.objects.none() 

    if id.lower() == 'all':
        logger.info("Category 'all' selected. Generic hero/description. No specific bottom category ads.")
        # category_for_template remains None
        ckposts_list = ckposts_list.order_by("-time")
        sidebar_ads_list = Advertisement.objects.filter(
            position='sidebar', is_active=True, category__isnull=True
        ).order_by('display_order')
        top_posts_list = CKPost.objects.all().order_by("-likes")[:3]
        # bottom_category_ads_list remains Advertisement.objects.none()

    else: # A specific category ID is provided
        try:
            category_pk = int(id)
            specific_category_from_db = get_object_or_404(Category, id=category_pk)
            
            category_for_template = specific_category_from_db # Use this for hero/desc
            logger.info(f"Specific category '{specific_category_from_db.name}' selected.")

            ckposts_list = ckposts_list.filter(category=specific_category_from_db).order_by("-time")
            
            # Sidebar Ads
            sidebar_ads_list = Advertisement.objects.filter(
                position='sidebar', is_active=True, category=specific_category_from_db
            ).order_by('display_order')
            if not sidebar_ads_list.exists(): # Fallback to general sidebar ads
                sidebar_ads_list = Advertisement.objects.filter(
                    position='sidebar', is_active=True, category__isnull=True
                ).order_by('display_order')
            
            # Top Posts
            top_posts_list = CKPost.objects.filter(category=specific_category_from_db).order_by("-likes")[:3]
            if not top_posts_list.exists() and ckposts_list.exists():
                top_posts_list = ckposts_list.order_by("-likes")[:3]
            
            # Fetch ALL bottom_banner_category ads for this specific category, ordered
            bottom_category_ads_list = Advertisement.objects.filter(
                position='bottom_banner_category',
                is_active=True,
                category=specific_category_from_db
            ).order_by('display_order') # Order them by display_order
            
            if bottom_category_ads_list.exists():
                logger.info(f"{bottom_category_ads_list.count()} bottom category ad(s) found for '{specific_category_from_db.name}'.")
            else:
                logger.info(f"No bottom category ads found for '{specific_category_from_db.name}'.")

        except ValueError:
            logger.error(f"Invalid category ID format for posts_by_category: {id}")
            # category_for_template remains None, bottom_category_ads_list remains empty
            return HttpResponse("Invalid category ID format.", status=400)
        # get_object_or_404 handles DoesNotExist

    context = {
        'ckposts': ckposts_list,
        'media_url': media_url,
        'categories': all_categories_for_filters, 
        'category': category_for_template, # For hero/description
        'sidebar_ads': sidebar_ads_list, # List of sidebar ads
        'top_posts': top_posts_list,
        
        # Pass the LIST of bottom category-specific ads (plural name)
        'bottom_category_ads': bottom_category_ads_list, 
    }
    return render(request, 'blog/articlesTabV2htmx.html', context)

def profile(request, username):
    return render(request, 'blog/profile.html', {
        'user_profile': get_object_or_404(User, username=username),
        'posts': CKPost.objects.all(),
        'media_url': settings.MEDIA_URL,
    })
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .models import AuthorProfile, User


def profileedit(request, username):
    author_profile = get_object_or_404(AuthorProfile, user__username=username)
    
    if request.method == 'POST':
        try:
            # Get form data
            firstname = request.POST.get('firstname')
            lastname = request.POST.get('lastname')
            email = request.POST.get('email')
            bio = request.POST.get('bio')
            facebook = request.POST.get('facebook')
            twitter = request.POST.get('twitter')
            gmail = request.POST.get('gmail')
            
            # Handle User model updates
            user = author_profile.user
            user.first_name = firstname
            user.last_name = lastname
            user.email = email  # Added email update
            user.save()

            # Handle AuthorProfile updates
            author_profile.bio = bio
            author_profile.facebook = facebook
            author_profile.twitter = twitter
            author_profile.gmail = gmail
            
            # Handle profile picture upload
            if 'profile_picture' in request.FILES:
                profile_picture = request.FILES['profile_picture']
                # Validate file type
                FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])(profile_picture)
                # Optional: Validate file size (5MB limit)
                if profile_picture.size > 5 * 1024 * 1024:
                    raise ValidationError("File size too large (max 5MB)")
                author_profile.profile_picture = profile_picture
            
            author_profile.save()
            
            return render(request, "blog/auteur.html", {
                'author_profile': author_profile
            })

        except ValidationError as e:
            # Handle validation errors
            return render(request, "blog/profileedit.html", {
                'author_profile': author_profile,
                'error': e.message
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


@permission_classes([IsAuthenticated, IsAuthor])
def create_post(request):
    if request.method == 'POST':
        logger.debug(f"Request POST data: {request.POST}")
        logger.debug(f"Request FILES data: {request.FILES}")
        form = forms.CKPostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user  # <--- This is important
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect('post_detail', slug=post.slug)
        else:
            logger.error(f"Form errors: {form.errors}")

    else:
        form = forms.CKPostForm()

    categories = Category.objects.all()
    return render(request, 'blog/create_post.html', {'form': form, 'categories': categories})


@permission_classes([IsAuthenticated, IsAuthor])
def post_list(request):
    posts = CKPost.objects.all().order_by('-time')
    media_url = "/media/"  # Define media_url outside the if-else block

    return render(request, 'blog/post_list.html', {
        'posts': posts,
        'media_url': media_url
    })


@permission_classes([IsAuthenticated, IsAuthor])
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


def home_new(request):
    return render(request, 'blog/base.html')


ckeditor_form_view = CkEditorFormView.as_view()


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


# blog/views.py

def post_detail(request, slug):
    post = get_object_or_404(CKPost, slug=slug)
    author_profile = None
    can_edit = False

    if request.user.is_authenticated and request.user == post.user:
        can_edit = True

    if post.user and hasattr(post.user, 'authorprofile'):
        author_profile = post.user.authorprofile

    related_posts = CKPost.objects.filter(category=post.category).exclude(slug=post.slug)[:3]
    top_level_comments = post.comments.filter(parent__isnull=True)
    media_url = "/media/"

    # Fetch the bottom banner ad for this post's category
    bottom_category_ad = None
    if post.category: # Ensure post has a category
        bottom_category_ad = Advertisement.objects.filter(
            position='bottom_banner_category',
            is_active=True,
            category=post.category
        ).order_by('display_order', '?').first()

    context = {
        "post": post,
        "author_profile": author_profile,
        "related_posts": related_posts,
        "media_url": media_url,
        "top_level_comments": top_level_comments,
        "can_edit": can_edit,
        "bottom_category_ad": bottom_category_ad, # Add to context
    }
    return render(request, "blog/post-detail.html", context)



def author_profile(request, username):
    try:
        user = get_object_or_404(User, username=username)
        profile = AuthorProfile.objects.get(user=user)
    except AuthorProfile.DoesNotExist:
        # Handle the case where the author profile does not exist
        return render(request, 'blog/no_author_profile.html', {'user': user})  # Or display a message

    return render(request, 'blog/auteur.html', {'author_profile': profile})

from .serializers import AuthorProfileSerializer  # Create this serializer

class CreateAuthorProfileView(generics.CreateAPIView):
    queryset = AuthorProfile.objects.all()
    serializer_class = AuthorProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  # automatically assigning profile to the current user


class AuthorProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = AuthorProfile.objects.all()
    serializer_class = AuthorProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'user__username'  # Use username instead of pk

    def get_object(self):
        username = self.kwargs['username']
        return get_object_or_404(AuthorProfile, user__username=username)


def hero_section(request, category_id):  # Added a new view for the Hero Section
    category = get_object_or_404(Category, pk=category_id)
    return render(request, 'blog/heroSection.html', {'category': category})


PROFIL_CHOICES_DICT = {
    'etudiant': 'Étudiant / Porteur de projet',
    'entrepreneur': 'Entrepreneur / Dirigeant de société',
    'investisseur': 'Investisseur',
    'autre': 'Autre',
}

from django.core.mail import send_mail, BadHeaderError

def lead_generation_form_view(request):
    if request.method == 'POST':
        form = LeadGenerationForm(request.POST)
        if form.is_valid():
            profil = form.cleaned_data['profil']
            email_from_user = form.cleaned_data['email'] # Renamed to avoid clash with email module
            nom_prenom = form.cleaned_data['nom_prenom']
            telephone = form.cleaned_data.get('telephone', 'N/A') # Use .get for optional
            gouvernorat = form.cleaned_data.get('gouvernorat', 'N/A') # Use .get for optional

            # --- Start Email Sending Logic ---
            subject = f"Nouvelle demande d'information (Livre Création Société) - {nom_prenom}"
            
            # Get the display label for profil
            profil_label = dict(form.fields['profil'].choices).get(profil, profil) # More robust way

            message_body = f"""
            Une nouvelle demande d'information a été soumise via le formulaire du livre :

            Profil: {profil_label}
            Nom et Prénom: {nom_prenom}
            Email du demandeur: {email_from_user}
            Téléphone: {telephone}
            Gouvernorat: {gouvernorat}

            ---
            Ceci est un message automatisé.
            """
            sender_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [settings.ADMIN_EMAIL_RECIPIENT]

            try:
                send_mail(subject, message_body, sender_email, recipient_list)
                messages.success(request, 'Merci ! Vos informations ont été soumises et envoyées avec succès.')
                
                # Optional: Send a confirmation email to the user
                # subject_user = "Confirmation de votre demande d'information"
                # message_user = f"Bonjour {nom_prenom},\n\nNous avons bien reçu votre demande concernant le livre 'Créer sa société en Tunisie en 2025'.\nNous reviendrons vers vous dans les plus brefs délais.\n\nCordialement,\nL'équipe [Your Website Name]"
                # try:
                #     send_mail(subject_user, message_user, sender_email, [email_from_user])
                # except Exception as e_user:
                #     print(f"Failed to send confirmation email to user: {e_user}") # Log this error

                # Redirect to the same page, but with an anchor to the form section
                # This helps if the success message is at the top.
                return redirect(request.path_info + '#lead-form')
            
            except BadHeaderError:
                # Django's send_mail raises BadHeaderError if subject, message, or from_email contain newlines
                messages.error(request, "Erreur d'en-tête invalide lors de la tentative d'envoi de l'email.")
            except Exception as e:
                # Catch other potential errors (e.g., SMTP server down, authentication failure)
                print(f"Erreur lors de l'envoi de l'email : {e}") # Log this error for debugging
                messages.error(request, "Une erreur s'est produite lors de l'envoi de votre demande. Veuillez réessayer plus tard ou nous contacter directement.")
            # If email sending fails, the form (with data) will be re-rendered below with the error message.

        else: # Form is not valid
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else: # GET request
        form = LeadGenerationForm()

    context = {
        'form': form
    }
    # Ensure 'blog/lead_form.html' is the correct path to your template
    return render(request, 'blog/lead_form.html', context)

def gozone_contact_view(request):
    if request.method == 'POST':
        form = GozoneContactForm(request.POST)
        if form.is_valid():
            nom_prenom = form.cleaned_data['nom_prenom']
            email_from_user = form.cleaned_data['email']
            telephone = form.cleaned_data.get('telephone', 'N/A')
            organisation = form.cleaned_data.get('organisation', 'N/A')
            
            profil_gozone_key = form.cleaned_data['profil_gozone']
            profil_gozone_label = dict(form.fields['profil_gozone'].choices).get(profil_gozone_key, profil_gozone_key)
            profil_gozone_autre_details = form.cleaned_data.get('profil_gozone_autre_details', '')

            besoins_gozone_keys = form.cleaned_data['besoins_gozone']
            besoins_labels = [dict(form.fields['besoins_gozone'].choices).get(key, key) for key in besoins_gozone_keys]
            besoins_gozone_str = ", ".join(besoins_labels)
            besoins_gozone_autre_details = form.cleaned_data.get('besoins_gozone_autre_details', '')
            message_complementaire = form.cleaned_data.get('message_complementaire', 'N/A')

            subject = f"Nouvelle prise de contact GOZONE - {nom_prenom}"
            
            message_body = f"""
            Une nouvelle demande de contact a été soumise via le formulaire GOZONE :

            Informations de Contact:
            -------------------------
            Nom et Prénom: {nom_prenom}
            Email: {email_from_user}
            Téléphone: {telephone}
            Organisation/Société: {organisation}

            Détails de la demande:
            ----------------------
            Profil: {profil_gozone_label}
            """
            if profil_gozone_key == 'autre_profil' and profil_gozone_autre_details:
                message_body += f"  Précision Profil Autre: {profil_gozone_autre_details}\n"
            
            message_body += f"\nRecherche de / Besoins: {besoins_gozone_str}\n"
            if 'autre_besoin' in besoins_gozone_keys and besoins_gozone_autre_details:
                message_body += f"  Précision Besoin Autre: {besoins_gozone_autre_details}\n"
            
            message_body += f"\nMessage complémentaire:\n{message_complementaire}\n"
            message_body += """
            ---
            Ceci est un message automatisé.
            """

            sender_email = settings.DEFAULT_FROM_EMAIL
            # You might want a different recipient for this form, or use the same ADMIN_EMAIL_RECIPIENT
            recipient_list = [settings.ADMIN_EMAIL_RECIPIENT] 

            try:
                send_mail(subject, message_body, sender_email, recipient_list)
                messages.success(request, 'Merci ! Votre message a été envoyé avec succès. Nous vous contacterons bientôt.')
                return redirect(request.path_info + '#gozone-contact-form-section') # Anchor to the form
            except BadHeaderError:
                messages.error(request, "Erreur d'en-tête invalide lors de la tentative d'envoi de l'email.")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de l'email (GOZONE Contact): {e}")
                messages.error(request, "Une erreur s'est produite lors de l'envoi de votre message. Veuillez réessayer plus tard.")
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = GozoneContactForm()

    context = {
        'form': form,
        'page_title': "Contactez l'équipe GOZONE", # For dynamic title in template if needed
        'form_section_id': 'gozone-contact-form-section' # For scrolling
    }
    return render(request, 'blog/gozone_contact_form.html', context)