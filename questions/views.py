from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)

    page.elided_page_range = paginator.get_elided_page_range(
        page.number,
        on_each_side=2,
        on_ends=1,
    )

    return page


def make_questions():
    questions = [
        {
            'id': 1,
            'title': 'Зачем играть в роблокс, если есть майнкрафт',
            'text': 'Хочу понять, почему многие выбирают именно Roblox, если есть Minecraft.',
            'avatar': 'questions/img/anime1.jpg',
            'likes': 24,
            'answers_count': 24,
            'author': 'ggadk_batman',
            'created_at': '11 часов назад',
            'tags': ['мнение', 'майнкрафт', 'игры'],
        },
        {
            'id': 2,
            'title': 'Выгорел от учёбы?',
            'text': 'Помогите, учился все 3 четверти нормально и в 4 четверти всё пошло не по плану. Что делать?',
            'avatar': 'questions/img/anime4.jpg',
            'likes': 0,
            'answers_count': 22,
            'author': 'wenIafe',
            'created_at': '10 часов назад',
            'tags': ['мнения', 'другое', 'учёба'],
        },
        {
            'id': 3,
            'title': 'Вам повезло, у вас красивые одноклассницы',
            'text': 'Хочется обсудить, почему в разных школах и классах настолько отличается атмосфера.',
            'avatar': 'questions/img/anime5.jpg',
            'likes': 0,
            'answers_count': 23,
            'author': 'perry_ytkonos_zov4',
            'created_at': '10 часов назад',
            'tags': ['мнения', 'другое', 'школа'],
        },
        {
            'id': 4,
            'title': 'Как заставить себя нормально учиться?',
            'text': 'Не могу войти в режим после каникул, постоянно отвлекаюсь.',
            'avatar': 'questions/img/anime2.jpg',
            'likes': 12,
            'answers_count': 8,
            'author': 'cedar_5545',
            'created_at': '9 часов назад',
            'tags': ['учёба', 'школа'],
        },
        {
            'id': 5,
            'title': 'Что лучше: Python или JavaScript?',
            'text': 'Хочу начать программировать, но не понимаю, с чего лучше начать.',
            'avatar': 'questions/img/anime3.jpg',
            'likes': 18,
            'answers_count': 14,
            'author': 'Биба и Боба',
            'created_at': '8 часов назад',
            'tags': ['python', 'web'],
        },
    ]

    result = []

    for i in range(1, 31):
        question = questions[(i - 1) % len(questions)].copy()
        question['id'] = i
        result.append(question)

    return result


def index(request):
    questions = make_questions()
    page = paginate(questions, request, per_page=3)

    return render(request, 'questions/index.html', {
        'page': page,
    })


def hot(request):
    questions = sorted(make_questions(), key=lambda question: question['likes'], reverse=True)
    page = paginate(questions, request, per_page=3)

    return render(request, 'questions/hot.html', {
        'page': page,
    })


def tag(request, tag_name):
    questions = [
        question for question in make_questions()
        if tag_name in question['tags']
    ]

    page = paginate(questions, request, per_page=3)

    return render(request, 'questions/tag.html', {
        'page': page,
        'tag_name': tag_name,
    })


def question_detail(request, question_id):
    questions = make_questions()
    question = questions[(question_id - 1) % len(questions)].copy()
    question['id'] = question_id

    answers = [
        {
            'text': 'Не все любят майн бро.',
            'avatar': 'questions/img/anime2.jpg',
            'likes': 1,
            'author': 'cedar_5545',
            'created_at': '11 часов назад',
            'is_correct': True,
        },
        {
            'text': 'Зачем играть в МайнКампф, если он воссоздан в Роблокс?',
            'avatar': 'questions/img/anime3.jpg',
            'likes': 1,
            'author': 'ryangosling2049',
            'created_at': '11 часов назад',
            'is_correct': False,
        },
        {
            'text': 'Ага го играть.',
            'avatar': 'questions/img/anime4.jpg',
            'likes': -1,
            'author': 'sos686',
            'created_at': '11 часов назад',
            'is_correct': False,
        },
    ]

    page = paginate(answers, request, per_page=3)

    return render(request, 'questions/question_detail.html', {
        'question': question,
        'page': page,
    })


def ask(request):
    return render(request, 'questions/ask.html')
