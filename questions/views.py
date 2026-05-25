from django.shortcuts import get_object_or_404, render

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
    page = paginate(Answer.objects.for_question(question), request, ANSWERS_PER_PAGE)

    return render(request, "questions/question_detail.html", {
        "question": question,
        "page": page,
    })


def ask(request):
    return render(request, "questions/ask.html")