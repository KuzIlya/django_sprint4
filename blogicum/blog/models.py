"""
Models from the Blog application.
It contains 4 models: User, Catalog, Location, Post
"""
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

MAX_LENGTH = 256


class PublishedModel(models.Model):
    """
    Abstract model class that added
    is_published, created_at fields
    """

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text=('Снимите галочку, '
                   'чтобы скрыть публикацию.'))

    created_at = models.DateTimeField('Добавлено',
                                      auto_now_add=True,
                                      )

    class Meta:
        abstract = True


class Category(PublishedModel):
    title = models.CharField('Заголовок',
                             max_length=MAX_LENGTH,
                             blank=False)
    description = models.TextField('Описание',
                                   blank=False)
    slug = models.SlugField('Идентификатор',
                            unique=True,
                            blank=False,
                            help_text='Идентификатор страницы для URL; '
                                      'разрешены символы латиницы, цифры, '
                                      'дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField('Название места',
                            max_length=MAX_LENGTH,
                            blank=False)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel):
    title = models.CharField('Заголовок поста',
                             max_length=MAX_LENGTH,
                             blank=False)
    text = models.TextField('Текст',
                            blank=False)
    pub_date = models.DateTimeField('Дата и время публикации',
                                    blank=False,
                                    help_text='Если установить дату и время '
                                              'в будущем — можно делать '
                                              'отложенные публикации.')
    image = models.ImageField('Изображение',
                              upload_to='posts_images',
                              blank=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               blank=False,
                               verbose_name='Автор публикации',
                               related_name='posts')
    location = models.ForeignKey(Location,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 related_name='posts',
                                 verbose_name='Местоположение')
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 blank=False,
                                 null=True,
                                 related_name='posts',
                                 verbose_name='Категория')
    

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.title


class Comment(models.Model):
    text = models.TextField('Текст комментария')

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='comments'
    )

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return self.text