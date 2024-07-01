from django.db import models

from .consts import LEN_AUTHOR, LEN_STR, LEN_TEXT, LEN_TITLE


class Post(models.Model):
    """Модель создания новости"""
    author = models.CharField('Автор', max_length=LEN_AUTHOR, blank=False)
    title = models.CharField('Название', max_length=LEN_TITLE, blank=False)
    text = models.TextField('Текст', max_length=LEN_TEXT, blank=False)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    def __str__(self) -> str:
        return self.text[:LEN_STR]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
