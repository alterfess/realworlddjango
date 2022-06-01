import datetime

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from events.models import Category, Feature, Event, Review
from django.views.decorators.http import require_POST


def event_list(request):
    template_name = 'events/event_list.html'
    category_objects = Category.objects.all()
    features_objects = Feature.objects.all()
    event_objects = Event.objects.all()

    context = {
        'category_objects': category_objects,
        'feature_objects': features_objects,
        'event_objects': event_objects,
    }

    return render(request, template_name, context)


def event_detail(request, pk):
    template_name = 'events/event_detail.html'
    event = get_object_or_404(Event, pk=pk)
    context = {
        'event': event,
    }

    return render(request, template_name, context)


@require_POST
def create_review(request):

    data = {
        'ok': True,
        'msg': '',
        'rate': request.POST.get('rate'),
        'text': request.POST.get('text'),
        'created': datetime.date.today().strftime('%d.%m.%Y')
    }

    messages = {
        'is_not_registered': 'Отзывы могут оставлять только зарегистрированные пользователи',
        'is_not_rated_or_texted':'Оценка и текст отзыва - обязательные поля',
        'is_reviewed': 'Вы уже оставляли отзыв к этому событию',
        'is_empty': 'Такого события не существует',
    }

    pk = request.POST.get('event_id', '')
    rate = request.POST.get('rate', '')
    text = request.POST.get('text', '')

    if not pk:
        data['msg'] = messages['is_empty']
        data['ok'] = False
        return JsonResponse(data)
    else:

        event = Event.objects.get(pk=pk)

        if not request.user.is_authenticated:
            data['msg'] = messages['is_not_registered']
            data['ok'] = False
            return JsonResponse(data)

        data['user_name'] = request.user.__str__()

        if not rate or not text:
            data['msg'] = messages['is_not_rated_or_texted']
            data['ok'] = False
            return JsonResponse(data)

        elif Review.objects.filter(user=request.user, event=event).exists():
            data['msg'] = messages['is_reviewed']
            data['ok'] = False
            return JsonResponse(data)

        else:
            new_review = Review(
                user=request.user,
                event=event,
                rate=data['rate'],
                text=data['text'],
                created=data['created'],
                updated=data['created']
            )

            new_review.save()
        return JsonResponse(data)

