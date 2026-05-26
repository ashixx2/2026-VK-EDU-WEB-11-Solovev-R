from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def debug_celery_beat():
    return "Celery beat works"


@shared_task
def send_new_answer_email(answer_id):
    from .models import Answer

    try:
        answer = (
            Answer.objects
            .select_related("question", "question__author", "author")
            .get(pk=answer_id)
        )
    except Answer.DoesNotExist:
        return "Answer does not exist"

    question = answer.question
    recipient = question.author.email

    if not recipient:
        return "Question author has no email"

    question_url = f"{settings.SITE_URL}{question.get_absolute_url()}#answer-{answer.id}"

    send_mail(
        subject=f"Новый ответ на вопрос: {question.title}",
        message=(
            f"Здравствуйте!\n\n"
            f"Пользователь {answer.author.username} оставил новый ответ "
            f"на ваш вопрос «{question.title}».\n\n"
            f"Посмотреть ответ можно по ссылке:\n"
            f"{question_url}\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=False,
    )

    return f"Email sent to {recipient}"