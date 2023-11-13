from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone as tz
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, UserForm
from .mixins import CommentMixin, DeleteMixin, DispatchMixin, EditMixin
from .models import Category, Post

PAGINATE_BY = 10


class IndexListView(ListView):
    model = Post
    paginate_by = PAGINATE_BY
    template_name = 'blog/index.html'
    ordering = '-pub_date'
    queryset = (
        Post.objects.select_related('location', 'author', 'category')
        .filter(is_published=True,
                category__is_published=True,
                pub_date__lte=tz.now())
        .annotate(comment_count=Count('comments'))
    )


class CategoryPostsListView(ListView):
    model = Post
    paginate_by = PAGINATE_BY
    template_name = 'blog/category.html'

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

        return (
            category.posts.select_related('location', 'author', 'category')
            .filter(is_published=True,
                    pub_date__lte=tz.now())
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    paginate_by = PAGINATE_BY

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))

        is_author = (post.author == self.request.user)
        is_published = (post.is_published and post.category.is_published)
        is_published_in_time = (post.pub_date <= tz.now())

        if not (is_author or (is_published and is_published_in_time)):
            raise Http404('Page does not exist')

        context['comments'] = (
            self.object.comments.select_related('author')
            .filter(post_id__is_published=True,
                    post_id__category__is_published=True)
        )

        context['form'] = CommentForm()
        return context


class PostUpdateView(DispatchMixin, LoginRequiredMixin,
                     UpdateView, EditMixin):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class PostDeleteView(DispatchMixin, LoginRequiredMixin,
                     DeleteView, DeleteMixin):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'


class ProfileListView(ListView):
    model = Post
    paginate_by = PAGINATE_BY
    template_name = 'blog/profile.html'

    def get_queryset(self):
        return (
            self.model.objects.select_related('author')
            .filter(author__username=self.kwargs['username'])
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'])
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserForm

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


class CommentUpdateView(LoginRequiredMixin, CommentMixin,
                        UpdateView, EditMixin):
    pass


class CommentDeleteView(LoginRequiredMixin, CommentMixin,
                        DeleteView, DeleteMixin):
    pass
