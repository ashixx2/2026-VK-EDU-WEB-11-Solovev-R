from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import (
    Answer,
    AnswerLike,
    Profile,
    Question,
    QuestionLike,
    Tag,
)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0
    verbose_name = "профиль"
    verbose_name_plural = "профиль"


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ("author", "text", "is_correct", "created_at")
    readonly_fields = ("created_at",)
    raw_id_fields = ("author",)
    show_change_link = True


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "avatar")
    search_fields = ("user__username", "user__email")
    raw_id_fields = ("user",)
    list_select_related = ("user",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "slug")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "created_at", "updated_at")
    search_fields = ("title", "text", "author__username", "tags__title")
    list_filter = ("created_at", "updated_at", "tags")
    raw_id_fields = ("author",)
    filter_horizontal = ("tags",)
    list_select_related = ("author",)
    inlines = (AnswerInline,)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "author", "is_correct", "created_at")
    search_fields = ("text", "question__title", "author__username")
    list_filter = ("is_correct", "created_at")
    raw_id_fields = ("question", "author")
    list_select_related = ("question", "author")


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "user", "value", "created_at")
    search_fields = ("question__title", "user__username")
    list_filter = ("value", "created_at")
    raw_id_fields = ("question", "user")
    list_select_related = ("question", "user")


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "answer", "user", "value", "created_at")
    search_fields = ("answer__text", "user__username")
    list_filter = ("value", "created_at")
    raw_id_fields = ("answer", "user")
    list_select_related = ("answer", "user")
# Register your models here.
