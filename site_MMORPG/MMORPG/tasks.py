from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Post


@shared_task
def post_create(post_comment_id):
    post = Post.objects.get(pk=post_comment_id)
    html_content = render_to_string('post_create_email.html',
                                    {'link': f'{settings.SITE_URL}/{post_comment_id}'})

    msg = EmailMultiAlternatives(subject=f'На "Доске объявлений MMORPG" новое объявление - {post.title_post}', body='',
                                 from_email=settings.EMAIL_HOST_USER + '@yandex.ru',
                                 to=settings.EMAIL_HOST_USER + '@yandex.ru',)
    msg.attach_alternative(html_content, 'text/html')
    msg.send()