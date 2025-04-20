
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import FormMixin
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from jalali_date import datetime2jalali
from datetime import datetime
from django.utils.timezone import now


from accounts.models import Activity
from .utils import get_clinet_ip, generate_unique_slug
from .models import Post, Like, BookmarkPost, PostView, Category
from .forms import PostCreateForm, CommentForm
from taggit.models import Tag


class IndexListView(generic.ListView):
    template_name = 'blog/post_list.html'
    context_object_name = 'list'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(status='pub').order_by('-created_at').select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_numbers'] = context['paginator'].page_range
        return context


# --- Post Detail View ---
class PostDetailView(generic.DetailView, FormMixin):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'detail'
    form_class = CommentForm
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Post.objects.filter(status='pub').select_related('author').prefetch_related('comments', 'likes',
                                                                                           'bookmarks')

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        comments_qs = self.object.comments.filter(publish=True)
        context['comments'] = comments_qs.order_by('-datetime_created')
        context.update({
            'comments_count': self.object.comments_count,
            'likes_count': self.object.likes_count,
            'bookmark_count': self.object.bookmark_count,
            'unique_views': self.object.unique_views,
            'form': self.get_form(),
            'liked': False,
            'bookmarked': False,
        })
        if user.is_authenticated:
            context['liked'] = self.object.likes.filter(user=user).exists()  # True
            context['bookmarked'] = self.object.bookmarks.filter(user=user).exists()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # استفاده از redirect به جای HttpResponseRedirect

        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.user = request.user
            comment.save()
            messages.success(request, 'نظر شما با موفقیت ثبت شد. در صورت تایید مدیر نمایش داده میشود')
            Activity.objects.create(
                user=self.request.user,
                action='comment_create',
                timestamp=now(),
                description='ثبت یک کامنت جدید'
            )
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        ip = get_clinet_ip(request)
        user = request.user if request.user.is_authenticated else None

        if not PostView.objects.filter(post=self.object, ip_address=ip, user=user).exists():
            PostView.objects.create(post=self.object, ip_address=ip, user=user)
        return self.render_to_response(context)

    def get_success_url(self):
        return self.object.get_absolute_url()


# --- Post Create View ---
class PostCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    form_class = PostCreateForm
    template_name = 'blog/post_create.html'
    permission_required = 'blog.add_post'

    def form_valid(self, form):
        form.instance.author = self.request.user
        instance = form.save(commit=False)
        instance.slug = generate_unique_slug(instance.title, instance=instance)
        instance.save()
        form.save_m2m()
        Activity.objects.create(
            user=self.request.user,
            action='post_create',
            timestamp=now(),
            description='ارسال یک پست جدید'
        )
        messages.success(self.request, 'پست با موفقیت ثبت شد.')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_create'] = True
        return kwargs


# --- Post Update View ---
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/post_create.html'

    def get_object(self, queryset=None):
        return Post.objects.get(slug=self.kwargs['slug'])

    def get_initial(self):
        initial = super().get_initial()
        initial['tags'] = " ".join(self.object.tags.names())
        return initial

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def form_valid(self, form):
        tags = form.cleaned_data['tags']
        self.object.tags.set(tags)

        instance = form.save(commit=False)
        instance.slug = generate_unique_slug(instance.title, instance=instance)
        instance.save()
        messages.success(self.request, 'پست با موفقیت به روز رسانی شد.')
        Activity.objects.create(
            user=self.request.user,
            action='post_edit',
            timestamp=now(),
            description='ویرایش پست'
        )
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_create'] = False
        return kwargs


# --- Post Delete View ---
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Post
    template_name = 'blog/post_delete.html'
    success_url = reverse_lazy('blog_index')

    def get_object(self, queryset=None):
        return Post.objects.get(slug=self.kwargs['slug'])

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def form_valid(self, form):
        obj = self.get_object()
        if obj.cover:
            try:
                obj.cover.delete(save=False)
            except Exception as e:
                print(f"Error deleting file: {e}")

        messages.success(self.request, "پست با موفقیت حذف شد")
        Activity.objects.create(
            user=self.request.user,
            action='post_delete',
            timestamp=now(),
            description='حذف پست'
        )
        return super().form_valid(form)


# --- Like Post ---
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    if request.method == "POST":
        if Like.objects.filter(post=post, user=user).exists():
            Like.objects.filter(post=post, user=user).delete()
            liked = False
        else:
            Like.objects.create(post=post, user=user)
            liked = True
        like_count = post.likes.count()
        return JsonResponse({"liked": liked, "likes_count": like_count})


# --- Bookmark Post ---
@login_required
def bookmark_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    if request.method == 'POST':
        if BookmarkPost.objects.filter(post=post, user=user).exists():
            BookmarkPost.objects.filter(post=post, user=user).delete()
            bookmarked = False
        else:
            BookmarkPost.objects.create(post=post, user=user)
            bookmarked = True
        bookmarked_count = post.bookmarks.count()
        return JsonResponse({"bookmarked": bookmarked, "bookmarks_count": bookmarked_count})


# --- Archive Month ---
def archive_month(request, year, month):
    posts = Post.objects.filter(
        created_at__year=year,
        created_at__month=month
    ).select_related('author')

    # تبدیل تاریخ میلادی به یک شیء datetime
    date = datetime(year, month, 1)
    jalali_date = datetime2jalali(date)
    month_name = jalali_date.strftime('%B %Y')  # نمایش نام ماه و سال به شمسی

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/archive.html', {'list': page_obj, 'month_name': month_name})


# --- Category Post List View ---
class CategoryPostListView(generic.ListView):
    model = Post
    template_name = 'blog/posts_by_category.html'
    context_object_name = 'list'
    paginate_by = 10

    def get_queryset(self):
        category_name = self.kwargs['name']
        return Post.objects.filter(categories__name=category_name).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(name=self.kwargs['name'])
        context['page_numbers'] = context['paginator'].page_range
        return context


# --- Post List by Tag ---
class PostListByTagView(generic.ListView):
    model = Post
    context_object_name = 'list'
    template_name = 'blog/posts_by_tag.html'
    paginate_by = 10

    def get_queryset(self):
        tag_slug = self.kwargs['tag_slug']
        tag = get_object_or_404(Tag, slug=tag_slug)
        return Post.objects.filter(tags=tag)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
        context['page_numbers'] = context['paginator'].page_range
        return context

