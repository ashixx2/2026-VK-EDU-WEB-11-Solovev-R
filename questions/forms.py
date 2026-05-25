import math
from uuid import uuid4

from django import forms
from django.template.defaultfilters import slugify

from .models import Answer, Question, Tag


MAX_TAGS_PER_QUESTION = 3


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        label="Теги",
        required=False,
        help_text="Укажите не более 3 тегов через запятую.",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Например: учёба, игры, общение",
            "id": "question-tags",
        }),
    )

    class Meta:
        model = Question
        fields = ("title", "text", "tags")
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Введите заголовок",
                "id": "question-title",
            }),
            "text": forms.Textarea(attrs={
                "class": "form-control ask-textarea",
                "placeholder": "Опишите вопрос",
                "id": "question-text",
                "rows": 8,
            }),
        }
        labels = {
            "title": "Заголовок",
            "text": "Текст вопроса",
        }

    def clean_tags(self):
        raw_tags = self.cleaned_data.get("tags", "")
        tags = [
            tag.strip().lower()
            for tag in raw_tags.split(",")
            if tag.strip()
        ]

        unique_tags = list(dict.fromkeys(tags))

        if len(unique_tags) > MAX_TAGS_PER_QUESTION:
            raise forms.ValidationError("Можно указать не более 3 тегов.")

        return unique_tags

    def save(self, author, commit=True):
        question = super().save(commit=False)
        question.author = author

        if commit:
            question.save()
            question.tags.set(self._get_or_create_tags())

        return question

    def _get_or_create_tags(self):
        result = []

        for tag_title in self.cleaned_data["tags"]:
            tag, _ = Tag.objects.get_or_create(
                title=tag_title,
                defaults={"slug": self._make_unique_slug(tag_title)},
            )
            result.append(tag)

        return result

    @staticmethod
    def _make_unique_slug(title):
        base_slug = slugify(title)

        if not base_slug:
            base_slug = f"tag-{uuid4().hex[:8]}"

        slug = base_slug
        counter = 1

        while Tag.objects.filter(slug=slug).exists():
            counter += 1
            slug = f"{base_slug}-{counter}"

        return slug


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(attrs={
                "class": "form-control answer-textarea",
                "placeholder": "Введите ваш ответ",
                "rows": 6,
            }),
        }
        labels = {
            "text": "Ваш ответ",
        }

    def save(self, author, question, commit=True):
        answer = super().save(commit=False)
        answer.author = author
        answer.question = question

        if commit:
            answer.save()

        return answer


def get_answer_page_number(question, answers_per_page):
    answers_count = Answer.objects.filter(question=question).count()
    return max(1, math.ceil(answers_count / answers_per_page))