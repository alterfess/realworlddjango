from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=90, default='', verbose_name='Категория')

    def display_event_count(self):
        return self.events.count()

    display_event_count.short_description = 'Количество событий'

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Feature(models.Model):
    title = models.CharField(max_length=90, default='', verbose_name='Свойство')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Свойство события'
        verbose_name_plural = 'Свойства события'


class Event(models.Model):
    FULLNESS_FREE = '1'
    FULLNESS_MIDDLE = '2'
    FULLNESS_FULL = '3'
    FULLNESS_LEGEND_FREE = '<= 50%'
    FULLNESS_LEGEND_MIDDLE = '> 50%'
    FULLNESS_LEGEND_FULL = 'sold-out'
    FULLNESS_VARIANTS = (
        (FULLNESS_FREE, FULLNESS_LEGEND_FREE),
        (FULLNESS_MIDDLE, FULLNESS_LEGEND_MIDDLE),
        (FULLNESS_FULL, FULLNESS_LEGEND_FULL),
    )

    logo = models.ImageField(upload_to='events/events/', blank=True, null=True)
    title = models.CharField(max_length=200, default='', verbose_name='Название')
    description = models.TextField(default='', verbose_name='Описание')
    date_start = models.DateTimeField(verbose_name='Дата начала')
    participants_number = models.PositiveSmallIntegerField(default=0, verbose_name='Количество участников')
    is_private = models.BooleanField(default=False, verbose_name='Частное')
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE, related_name='events')
    features = models.ManyToManyField(Feature, blank=True)

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    @property
    def rate(self):
        all_reviews = self.reviews.count()
        sum_rate = sum([i.rate for i in self.reviews.all()])
        try:
            return round(sum_rate / all_reviews, 1)
        except:
            return 0

    @property
    def logo_url(self):
        return self.logo.url if self.logo else f'{settings.STATIC_URL}images/svg-icon/event.svg'

    def get_absolute_url(self):
        return reverse('events:event_detail', args=[str(self.pk)])

    def __str__(self):
        return self.title

    def get_enroll_count(self):
        """
        Return number of enrolls for this event.
        """
        return self.enrolls.count()

    def get_places_left(self):
        """
        Return number of free places for this event.
        """
        return int(self.participants_number or 0) - self.get_enroll_count()

    def get_fullness_legend(self, **kwargs):
        """
        Return legend for event's places_left.
        Legend is in the FULLNESS_VARIANTS.

        kwargs may contain the following parameters:
        `places_left`: number of free places for this event (to avoid additional query)
        """
        legend = ''
        if int(self.participants_number or 0) > 0:
            legend = Event.FULLNESS_LEGEND_FREE
            places_left = kwargs.get('places_left', None)
            if places_left is None:
                places_left = self.get_places_left()
            if places_left == 0:
                legend = Event.FULLNESS_LEGEND_FULL
            elif places_left < self.participants_number / 2:
                legend = Event.FULLNESS_LEGEND_MIDDLE
        return legend

    def display_enroll_count(self):
        return self.get_enroll_count()

    display_enroll_count.short_description = 'Количество записей'

    def display_places_left(self):
        places_left = self.get_places_left()
        return f'{places_left} ({self.get_fullness_legend(places_left=places_left)})'

    display_places_left.short_description = 'Осталось мест'


class Enroll(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='enrolls')
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE, related_name='enrolls')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.event.title} - {self.user}'

    class Meta:
        verbose_name = 'Запись на событие'
        verbose_name_plural = 'Записи на событие'


class Review(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='reviews')
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE, related_name='reviews')
    rate = models.PositiveSmallIntegerField(default=0)
    text = models.TextField(max_length=1000, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.rate} - {self.event.title}'

    class Meta:
        verbose_name = 'Отзыв на событие'
        verbose_name_plural = 'Отзывы на события'
