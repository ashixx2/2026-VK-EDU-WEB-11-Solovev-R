from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import (
    AnswerForm,
    AnswerVoteForm,
    CorrectAnswerForm,
    QuestionForm,
    QuestionVoteForm,
    get_answer_page_number,
)
from .models import Answer, AnswerLike, Question, QuestionLike, Tag
from .utils import paginate


QUESTIONS_PER_PAGE = 5
ANSWERS_PER_PAGE = 5


def index(request):
    page = paginate(Question.objects.new(), request, QUESTIONS_PER_PAGE)

    return render(request, "questions/index.html", {
        "page": page,
    })


def hot(request):
    page = paginate(Question.objects.hot(), request, QUESTIONS_PER_PAGE)

    return render(request, "questions/hot.html", {
        "page": page,
    })


def tag(request, tag_name):
    tag_object = get_object_or_404(Tag, slug=tag_name)
    page = paginate(Question.objects.by_tag(tag_object.slug), request, QUESTIONS_PER_PAGE)

    return render(request, "questions/tag.html", {
        "page": page,
        "tag": tag_object,
        "tag_name": tag_object.title,
    })


def question_detail(request, question_id):
    question = get_object_or_404(Question.objects.new(), pk=question_id)
    form = AnswerForm(request.POST or None)

    if request.method == "POST":
        if not request.user.is_authenticated:
            login_url = f"{reverse('core:login')}?next={request.path}"
            return redirect(login_url)

        if form.is_valid():
            answer = form.save(author=request.user, question=question)
            page_number = get_answer_page_number(question, ANSWERS_PER_PAGE)
            return redirect(f"{question.get_absolute_url()}?page={page_number}#answer-{answer.id}")

    page = paginate(Answer.objects.for_question(question), request, ANSWERS_PER_PAGE)

    return render(request, "questions/question_detail.html", {
        "question": question,
        "page": page,
        "form": form,
    })


@login_required(login_url="core:login")
def ask(request):
    form = QuestionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        question = form.save(author=request.user)
        return redirect(question.get_absolute_url())

    return render(request, "questions/ask.html", {
        "form": form,
    })


def get_question_rating(question):
    return sum(question.question_likes.values_list("value", flat=True))


def get_answer_rating(answer):
    return sum(answer.answer_likes.values_list("value", flat=True))


def get_ajax_error(message, status=400):
    return JsonResponse(
        {
            "ok": False,
            "error": message,
        },
        status=status,
    )


@require_POST
def vote_question(request):
    if not request.user.is_authenticated:
        return get_ajax_error("Войдите, чтобы голосовать.", status=401)

    form = QuestionVoteForm(request.POST)

    if not form.is_valid():
        return get_ajax_error("Некорректные параметры голосования.")

    question = get_object_or_404(Question, pk=form.cleaned_data["question_id"])
    vote_value = form.get_vote_value()

    like, created = QuestionLike.objects.get_or_create(
        question=question,
        user=request.user,
        defaults={"value": vote_value},
    )

    if not created and like.value == vote_value:
        like.delete()
        return JsonResponse({
            "ok": True,
            "rating": get_question_rating(question),
            "user_vote": None,
        })

    if not created:
        like.value = vote_value
        like.save(update_fields=["value"])

    return JsonResponse({
        "ok": True,
        "rating": get_question_rating(question),
        "user_vote": vote_value,
    })


@require_POST
def vote_answer(request):
    if not request.user.is_authenticated:
        return get_ajax_error("Войдите, чтобы голосовать.", status=401)

    form = AnswerVoteForm(request.POST)

    if not form.is_valid():
        return get_ajax_error("Некорректные параметры голосования.")

    answer = get_object_or_404(Answer, pk=form.cleaned_data["answer_id"])
    vote_value = form.get_vote_value()

    like, created = AnswerLike.objects.get_or_create(
        answer=answer,
        user=request.user,
        defaults={"value": vote_value},
    )

    if not created and like.value == vote_value:
        like.delete()
        return JsonResponse({
            "ok": True,
            "rating": get_answer_rating(answer),
            "user_vote": None,
        })

    if not created:
        like.value = vote_value
        like.save(update_fields=["value"])

    return JsonResponse({
        "ok": True,
        "rating": get_answer_rating(answer),
        "user_vote": vote_value,
    })


@require_POST
def mark_correct_answer(request):
    if not request.user.is_authenticated:
        return get_ajax_error("Войдите, чтобы выбрать правильный ответ.", status=401)

    form = CorrectAnswerForm(request.POST)

    if not form.is_valid():
        return get_ajax_error("Некорректные параметры.")

    question = get_object_or_404(Question, pk=form.cleaned_data["question_id"])

    if question.author_id != request.user.id:
        return get_ajax_error("Только автор вопроса может выбрать правильный ответ.", status=403)

    answer = get_object_or_404(
        Answer,
        pk=form.cleaned_data["answer_id"],
        question=question,
    )

    Answer.objects.filter(question=question, is_correct=True).update(is_correct=False)
    answer.is_correct = True
    answer.save(update_fields=["is_correct"])

    return JsonResponse({
        "ok": True,
        "correct_answer_id": answer.id,
    })