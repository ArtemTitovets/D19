from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Comment
from django.urls import reverse_lazy, reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseRedirect


class Posts(ListView):
    model = Post
    template_name = 'head.html'
    context_object_name = 'posts'
    ordering = '-date_post'
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['amount_posts'] = None
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post_detail'


class PostCreate(CreateView):
    model = Post
    template_name = 'post_create.html'
    form_class = PostForm

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.method == 'POST':
            post.author_post, created = User.objects.get_or_create(id=self.request.user.id)
            post.save()
            # post_create(post_comment_id=post.id)
        return super().form_valid(form)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PostEdit(UpdateView):
    model = Post
    template_name = 'post_edit.html'
    form_class = PostForm


class PostDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('posts')


class Profile(ListView):
    model = Comment
    template_name = 'profile.html'


class Comments(ListView):
    model = Comment
    template_name = 'comments.html'
    context_object_name = 'comments'
    ordering = '-date_comment'
    paginate_by = 5

    def get_queryset(self):
        queryset = Comment.objects.filter(post_comment__author_post=self.request.user)
        return queryset


class CommentCreate(CreateView):
    model = Comment
    template_name = 'comment_create.html'
    form_class = CommentForm
    success_url = '/comments/'

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.author_comment = User.objects.get(id=self.request.user.id)
        comment.post_comment = Post.objects.get(id=self.kwargs['pk'])
        comment.save()
        result = super().form_valid(form)
        send_mail(
            subject=f'Новый комментарий у вашего объявления "{comment.post_comment.title_post}"',
            message=f'Комментарий от {comment.author_comment}: "{comment.text_comment}"',
            from_email=settings.EMAIL_HOST_USER + '@yandex.ru',
            recipient_list=settings.EMAIL_HOST_USER + '@yandex.ru'
        )
        return result


class CommentDetail(DetailView):
    model = Comment
    template_name = 'comment_detail.html'
    context_object_name = 'comment_detail'

    def get_template_names(self):
        response = self.get_object()
        if response.post_comment.author_post == self.request.user:
            self.template_name = 'comment_detail.html'
            return self.template_name
        else:
            raise PermissionDenied

@login_required()
def confirm_comment(request, pk):
    comment = Comment.objects.get(pk=pk)
    comment.confirmation_comment = True
    comment.save()
    send_mail(
        subject=f'Принят комментарий от {comment.author_comment}',
        message=f'Принят комментарий от {comment.author_comment} к объявлению "{comment.post_comment.title_post}"',
        from_email=settings.EMAIL_HOST_USER + '@yandex.ru',
        recipient_list=settings.EMAIL_HOST_USER + '@yandex.ru'
    )
    return render(request, 'accept.html')


@login_required()
def reject_comment(request, pk):
    comment = Comment.objects.get(pk=pk)
    comment.confirmation_comment = False
    comment.save()
    return HttpResponseRedirect(reverse('comments'))
