from . import views
from django.urls import path
# from .views import AuthorProfileCreateView

urlpatterns = [
    path("",views.new_index,name="index"),
    path("old_index",views.index,name="old_index"),

    path("ckeditor" , views.create_post, name="ckeditor-form"),
    path('posts/', views.post_list, name='post_list'),  # This is the URL for listing posts
    path('edit_post/<slug:slug>/', views.edit_post, name='edit_post'),
    path('hero_section/<int:category_id>/', views.hero_section, name='hero_section'), # New URL for hero section
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    # Gestion des catégories et sous-catégories
    path('categories/<str:id>/', views.posts_by_category, name='posts_by_category'),  # Articles par catégorie
    path('get-subcategories/', views.get_subcategories, name='get_subcategories'),  # Récupérer les sous-catégories (HTMX)
    path('author/<str:username>/', views.author_profile, name='author_profile'),
    path("new-home" , views.home_new, name="new-home"),
    #path('author-profile/create/', AuthorProfileCreateView.as_view(), name='create-author-profile'),
    path('create_author_profile/', views.CreateAuthorProfileView.as_view(), name='create_author_profile'),
    path('author-profile/<str:username>/', views.AuthorProfileDetailView.as_view(), name='author_profile_detail'),  # detail view
    path("blog",views.blog,name="blog"),
    path("signin",views.signin,name="signin"),
    path("signup",views.signup,name="signup"),
    path("logout",views.logout,name="logout"),
    path("create",views.create_post,name="create_post"),
    path("increaselikes/<int:id>",views.increaselikes,name='increaselikes'),
    path("create_old",views.create_old,name="create_old"),
    path('add-comment/', views.add_comment, name='add_comment'),
    path("removepost/<int:id>",views.removepost,name='removepost'),
    path("profile/<str:username>",views.profile,name='profile'),
    path("profile/edit/<str:username>",views.profileedit,name='profileedit'),
    path("post/<int:id>",views.post,name="post"),
    path("post/comment/<int:id>",views.savecomment,name="savecomment"),
    path("post/comment/delete/<int:id>",views.deletecomment,name="deletecomment"),
    path("post/edit/<int:id>",views.editpost,name="editpost"),
    path("post/delete/<int:id>",views.deletepost,name="deletepost"),
    path("contact",views.contact_us,name="contact"),
    path('get_subcategories/', views.get_subcategories, name='get_subcategories'),
    path('htmx/get-category-ad-snippet/', views.get_category_ad_snippet_htmx, name='htmx_get_category_ad_snippet'),
    path('contactez-nous/creation-societe/', views.lead_generation_form_view, name='lead_generation_form'),
    path('contactez-nous/gozone/', views.gozone_contact_view, name='gozone_contact_form'),

    
]