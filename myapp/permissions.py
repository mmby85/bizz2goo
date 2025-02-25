from rest_framework import permissions
from .models import AuthorProfile

class IsAuthor(permissions.BasePermission):
    """
    Allows access only to authors.
    """

    def has_permission(self, request, view):
        # Check if user is authenticated first
        if not request.user.is_authenticated:
            return False

        # Check if user is staff (admin)
        if request.user.is_staff:
            return True

        try:
            author_profile = request.user.authorprofile
            return author_profile.is_author
        except AuthorProfile.DoesNotExist:
            return False