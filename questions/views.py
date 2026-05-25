from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import AnswerForm, QuestionForm, get_answer_page_number
from .models import Answer, Question, Tag
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