from .models import Category
from assignments.models import SocialLink

def get_categories(request):
    return dict(categories=Category.objects.all())


def get_social_links(request):
    social_links = SocialLink.objects.all()
    return dict(social_links=social_links)