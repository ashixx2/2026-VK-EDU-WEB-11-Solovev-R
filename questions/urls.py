from django.urls import path

from . import views


app_name = "questions"

urlpatterns = [
    path("", views.index, name="index"),
    path("hot/", views.hot, name="hot"),
    path("tag/<str:tag_name>/", views.tag, name="tag"),
    path("question/<int:question_id>/", views.question_detail, name="question_detail"),
    path("ask/", views.ask, name="ask"),

    path("ajax/vote-question/", views.vote_question, name="vote_question"),
    path("ajax/vote-answer/", views.vote_answer, name="vote_answer"),
    path("ajax/mark-correct-answer/", views.mark_correct_answer, name="mark_correct_answer"),
]