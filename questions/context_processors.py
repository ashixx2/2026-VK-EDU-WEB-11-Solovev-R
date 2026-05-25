from django.contrib.auth.models import User
from django.db.models import Count

from .models import Tag


POPULAR_TAGS_LIMIT = 6
TOP_USERS_LIMIT = 5


def sidebar_data(request):
    popular_tags = (
        Tag.objects
        .annotate(questions_count=Count("questions"))
        .filter(questions_count__gt=0)
        .order_by("-questions_count", "title")[:POPULAR_TAGS_LIMIT]
    )

    top_users = (
        User.objects
        .annotate(questions_count=Count("questions"))
        .filter(questions_count__gt=0)
        .order_by("-questions_count", "username")[:TOP_USERS_LIMIT]
    )

    return {
        "popular_tags": popular_tags,
        "top_users": top_users,
    }