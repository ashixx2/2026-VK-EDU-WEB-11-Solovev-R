import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from faker import Faker

from questions.models import (
    Answer,
    AnswerLike,
    Profile,
    Question,
    QuestionLike,
    Tag,
)


BATCH_SIZE = 5000
AVATARS = [
    "questions/img/anime1.jpg",
    "questions/img/anime2.jpg",
    "questions/img/anime3.jpg",
    "questions/img/anime4.jpg",
    "questions/img/anime5.jpg",
    "questions/img/avatar.png",
]


class Command(BaseCommand):
    help = "Fill database with test data: users, tags, questions, answers and likes."

    def add_arguments(self, parser):
        parser.add_argument(
            "ratio",
            type=int,
            help="Fill ratio. Users=ratio, questions=ratio*10, answers=ratio*100, tags=ratio, likes=ratio*200.",
        )

    def handle(self, *args, **options):
        ratio = options["ratio"]

        if ratio <= 0:
            raise CommandError("ratio must be a positive integer")

        fake = Faker("ru_RU")
        random.seed(42)
        Faker.seed(42)

        users_count = ratio
        tags_count = ratio
        questions_count = ratio * 10
        answers_count = ratio * 100
        likes_count = ratio * 200

        self.stdout.write(self.style.NOTICE(f"Creating {users_count} users..."))
        user_ids = self._create_users(fake, users_count)

        self.stdout.write(self.style.NOTICE(f"Creating {tags_count} tags..."))
        tag_ids = self._create_tags(tags_count)

        self.stdout.write(self.style.NOTICE(f"Creating {questions_count} questions..."))
        question_ids = self._create_questions(fake, questions_count, user_ids)

        self.stdout.write(self.style.NOTICE("Creating question-tag relations..."))
        self._create_question_tags(question_ids, tag_ids)

        self.stdout.write(self.style.NOTICE(f"Creating {answers_count} answers..."))
        answer_ids = self._create_answers(fake, answers_count, question_ids, user_ids)

        self.stdout.write(self.style.NOTICE(f"Creating {likes_count} likes..."))
        self._create_likes(likes_count, question_ids, answer_ids, user_ids)

        self.stdout.write(self.style.SUCCESS("Database was filled successfully."))

    @staticmethod
    def _chunks(items, size):
        for start in range(0, len(items), size):
            yield items[start:start + size]

    def _create_users(self, fake, count):
        start_index = User.objects.count() + 1
        users = []
        profiles = []
        created_user_ids = []

        for i in range(start_index, start_index + count):
            username = f"user_{i}_{fake.user_name()}"[:150]
            users.append(
                User(
                    username=username,
                    email=f"user_{i}@example.com",
                    first_name=fake.first_name()[:150],
                    last_name=fake.last_name()[:150],
                    is_active=True,
                )
            )

            if len(users) >= BATCH_SIZE:
                created_user_ids.extend(self._bulk_create_users_with_profiles(users, profiles))
                users = []
                profiles = []

        if users:
            created_user_ids.extend(self._bulk_create_users_with_profiles(users, profiles))

        return created_user_ids

    def _bulk_create_users_with_profiles(self, users, profiles):
        created_users = User.objects.bulk_create(users, batch_size=BATCH_SIZE)

        for user in created_users:
            profiles.append(
                Profile(
                    user_id=user.id,
                )
            )

        Profile.objects.bulk_create(profiles, batch_size=BATCH_SIZE)

        return [user.id for user in created_users]

    def _create_tags(self, count):
        start_index = Tag.objects.count() + 1
        tags = []
        created_tag_ids = []

        for i in range(start_index, start_index + count):
            tags.append(
                Tag(
                    title=f"tag {i}",
                    slug=f"tag-{i}",
                )
            )

            if len(tags) >= BATCH_SIZE:
                created_tags = Tag.objects.bulk_create(tags, batch_size=BATCH_SIZE)
                created_tag_ids.extend(tag.id for tag in created_tags)
                tags = []

        if tags:
            created_tags = Tag.objects.bulk_create(tags, batch_size=BATCH_SIZE)
            created_tag_ids.extend(tag.id for tag in created_tags)

        return created_tag_ids

    def _create_questions(self, fake, count, user_ids):
        questions = []
        question_ids = []

        for i in range(count):
            author_id = user_ids[i % len(user_ids)]

            questions.append(
                Question(
                    title=fake.sentence(nb_words=8)[:255],
                    text=fake.paragraph(nb_sentences=5),
                    author_id=author_id,
                )
            )

            if len(questions) >= BATCH_SIZE:
                created_questions = Question.objects.bulk_create(questions, batch_size=BATCH_SIZE)
                question_ids.extend(question.id for question in created_questions)
                questions = []

        if questions:
            created_questions = Question.objects.bulk_create(questions, batch_size=BATCH_SIZE)
            question_ids.extend(question.id for question in created_questions)

        return question_ids

    def _create_question_tags(self, question_ids, tag_ids):
        through_model = Question.tags.through
        relations = []

        for index, question_id in enumerate(question_ids):
            first_tag_id = tag_ids[index % len(tag_ids)]
            second_tag_id = tag_ids[(index + 17) % len(tag_ids)]
            third_tag_id = tag_ids[(index + 31) % len(tag_ids)]

            unique_tag_ids = {first_tag_id, second_tag_id, third_tag_id}

            for tag_id in unique_tag_ids:
                relations.append(
                    through_model(
                        question_id=question_id,
                        tag_id=tag_id,
                    )
                )

            if len(relations) >= BATCH_SIZE:
                through_model.objects.bulk_create(relations, batch_size=BATCH_SIZE)
                relations = []

        if relations:
            through_model.objects.bulk_create(relations, batch_size=BATCH_SIZE)

    def _create_answers(self, fake, count, question_ids, user_ids):
        answers = []
        answer_ids = []

        for i in range(count):
            answers.append(
                Answer(
                    question_id=question_ids[i % len(question_ids)],
                    author_id=user_ids[(i * 7) % len(user_ids)],
                    text=fake.paragraph(nb_sentences=4),
                    is_correct=(i % 20 == 0),
                )
            )

            if len(answers) >= BATCH_SIZE:
                created_answers = Answer.objects.bulk_create(answers, batch_size=BATCH_SIZE)
                answer_ids.extend(answer.id for answer in created_answers)
                answers = []

        if answers:
            created_answers = Answer.objects.bulk_create(answers, batch_size=BATCH_SIZE)
            answer_ids.extend(answer.id for answer in created_answers)

        return answer_ids

    def _create_likes(self, count, question_ids, answer_ids, user_ids):
        question_likes_count = count // 2
        answer_likes_count = count - question_likes_count

        self._create_question_likes(question_likes_count, question_ids, user_ids)
        self._create_answer_likes(answer_likes_count, answer_ids, user_ids)

    def _create_question_likes(self, count, question_ids, user_ids):
        likes = []
        question_count = len(question_ids)
        user_count = len(user_ids)

        for i in range(count):
            question_index = i % question_count
            round_index = i // question_count
            user_index = (question_index + round_index) % user_count

            likes.append(
                QuestionLike(
                    question_id=question_ids[question_index],
                    user_id=user_ids[user_index],
                    value=QuestionLike.LIKE if i % 5 else QuestionLike.DISLIKE,
                )
            )

            if len(likes) >= BATCH_SIZE:
                QuestionLike.objects.bulk_create(likes, batch_size=BATCH_SIZE)
                likes = []

        if likes:
            QuestionLike.objects.bulk_create(likes, batch_size=BATCH_SIZE)

    def _create_answer_likes(self, count, answer_ids, user_ids):
        likes = []
        answer_count = len(answer_ids)
        user_count = len(user_ids)

        for i in range(count):
            answer_index = i % answer_count
            user_index = (i * 17) % user_count

            likes.append(
                AnswerLike(
                    answer_id=answer_ids[answer_index],
                    user_id=user_ids[user_index],
                    value=AnswerLike.LIKE if i % 6 else AnswerLike.DISLIKE,
                )
            )

            if len(likes) >= BATCH_SIZE:
                AnswerLike.objects.bulk_create(likes, batch_size=BATCH_SIZE)
                likes = []

        if likes:
            AnswerLike.objects.bulk_create(likes, batch_size=BATCH_SIZE)