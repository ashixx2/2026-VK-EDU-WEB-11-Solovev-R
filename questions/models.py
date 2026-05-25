from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.urls import reverse


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="пользователь",
    )
    avatar = models.CharField(
        max_length=255,
        default="questions/img/avatar.png",
        verbose_name="аватар",
    )

    class Meta:
        verbose_name = "профиль"
        verbose_name_plural = "профили"

    def __str__(self):
        return self.user.username


class Tag(models.Model):
    title = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="название",
    )
    slug = models.SlugField(
        max_length=64,
        unique=True,
        verbose_name="slug",
    )

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "теги"
        ordering = ["title"]

    def __str__(self):
        return self.title


class QuestionQuerySet(models.QuerySet):
    def with_related_data(self):
        return self.select_related("author", "author__profile").prefetch_related("tags")

    def with_counters(self):
        return self.annotate(
            rating=Coalesce(Sum("question_likes__value"), 0),
            answers_count=Count("answers", distinct=True),
        )

    def new(self):
        return self.with_related_data().with_counters().order_by("-created_at")

    def hot(self):
        return self.with_related_data().with_counters().order_by("-rating", "-created_at")

    def by_tag(self, tag_slug):
        return self.filter(tags__slug=tag_slug).new()


class QuestionManager(models.Manager):
    def get_queryset(self):
        return QuestionQuerySet(self.model, using=self._db)

    def new(self):
        return self.get_queryset().new()

    def hot(self):
        return self.get_queryset().hot()

    def by_tag(self, tag_slug):
        return self.get_queryset().by_tag(tag_slug)


class Question(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="заголовок",
    )
    text = models.TextField(
        verbose_name="текст вопроса",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="автор",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="questions",
        blank=True,
        verbose_name="теги",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="дата создания",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="дата обновления",
    )

    objects = QuestionManager()

    class Meta:
        verbose_name = "вопрос"
        verbose_name_plural = "вопросы"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("questions:question_detail", kwargs={"question_id": self.pk})


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="вопрос",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="автор",
    )
    text = models.TextField(
        verbose_name="текст ответа",
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name="правильный ответ",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="дата создания",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="дата обновления",
    )

    class Meta:
        verbose_name = "ответ"
        verbose_name_plural = "ответы"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["question", "created_at"]),
        ]

    def __str__(self):
        return f"Ответ на вопрос {self.question_id}"


class QuestionLike(models.Model):
    LIKE = 1
    DISLIKE = -1

    VOTE_CHOICES = (
        (LIKE, "лайк"),
        (DISLIKE, "дизлайк"),
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="question_likes",
        verbose_name="вопрос",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="question_likes",
        verbose_name="пользователь",
    )
    value = models.SmallIntegerField(
        choices=VOTE_CHOICES,
        verbose_name="оценка",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="дата создания",
    )

    class Meta:
        verbose_name = "оценка вопроса"
        verbose_name_plural = "оценки вопросов"
        unique_together = ("question", "user")
        indexes = [
            models.Index(fields=["question", "user"]),
        ]

    def __str__(self):
        return f"{self.user_id} -> {self.question_id}: {self.value}"


class AnswerLike(models.Model):
    LIKE = 1
    DISLIKE = -1

    VOTE_CHOICES = (
        (LIKE, "лайк"),
        (DISLIKE, "дизлайк"),
    )

    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name="answer_likes",
        verbose_name="ответ",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="answer_likes",
        verbose_name="пользователь",
    )
    value = models.SmallIntegerField(
        choices=VOTE_CHOICES,
        verbose_name="оценка",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="дата создания",
    )

    class Meta:
        verbose_name = "оценка ответа"
        verbose_name_plural = "оценки ответов"
        unique_together = ("answer", "user")
        indexes = [
            models.Index(fields=["answer", "user"]),
        ]

    def __str__(self):
        return f"{self.user_id} -> {self.answer_id}: {self.value}"