from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.edit import FormMixin
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.text import slugify

from .utils import get_clinet_ip
from .models import Post, Like, BookmarkPost, PostView, Category
from .forms import PostCreateForm, CommentForm
from taggit.models import Tag
import re


class IndexListView(generic.ListView):
    template_name = 'blog/post_list.html'
    context_object_name = 'list'
    paginate_by = 6

    def get_queryset(self):
        return Post.objects.filter(status='pub').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context =super().get_context_data(**kwargs)
        context['page_numbers'] = range(1, context['paginator'].num_pages + 1)
        return context


class PostDetailView(generic.DetailView, FormMixin):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'detail'
    form_class = CommentForm
    slug_url_kwarg ='slug'
    
    def get_queryset(self):
        return Post.objects.filter(status='pub').order_by('-created_at')
    
    def get_context_data(self, **kwargs) :
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter().order_by('-datetime_created')
        context['comments_count'] = self.object.comments.count()
        context['likes_count'] = self.object.likes.count()
        context['bookmark_count'] = self.object.bookmarks.count()
        context['unique_views'] = self.object.views.count()
        context['form'] = self.get_form()
        if user.is_authenticated:
            context['liked'] = Like.objects.filter(post=self.object, user=user).exists() #True
            context['bookmarked'] = BookmarkPost.objects.filter(post=self.object, user=user).exists()
        else :
            context['liked'] = False
            context['bookmarked'] = False
        return context
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:   
            return HttpResponseRedirect('/login/')
        
        self.object = self.get_object()
        form = self.get_form()
        
        if form.is_valid():
            comment  = form.save(commit=False)
            comment.post = self.object
            comment.user = request.user
            comment.save()
            messages.success(request, 'نظر شما با موفقیت ثبت شد.')
            return self.form_valid(form)
        else :
            return self.form_invalid(form)
        
    def get(self, request, *args, **kwargs):
        self.object  = self.get_object()
        context = self.get_context_data(object=self.object)
        ip = get_clinet_ip(request)
        user = request.user if request.user.is_authenticated else None
        
        if not PostView.objects.filter(post=self.object, ip_address=ip, user=user).exists():
            PostView.objects.create(post=self.object, ip_address=ip, user=user)
        return self.render_to_response(context)
        
    def get_success_url(self):
        return self.object.get_absolute_url()


class PostCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = PostCreateForm
    template_name = 'blog/post_create.html'
    
    def form_valid(self, form) :
        form.instance.author = self.request.user

        def clean_slug(title) :
            title = re.sub(r'[^\w\s-]', '', title)
            title = re.sub(r'[-\s]+', '-', title)
            title = title.strip('-')
            if not title :
                title = 'پست'
            return title
        isinstance= form.save(commit=False)
        base_slug = slugify(clean_slug(isinstance.title), allow_unicode=True)
        unique_slug =base_slug
        if Post.objects.filter(slug=unique_slug).exists():
            isinstance.save()
            unique_slug = f'{base_slug}-{isinstance.pk}'
        isinstance.slug = unique_slug
        isinstance.save()    
        messages.success(self.request, 'پست با موفقیت ثبت شد.')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_create'] = True
        return kwargs
        
        
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/post_create.html'

    def get_object(self, queryset=None) :
        return Post.objects.get(slug=self.kwargs['slug'])
    
    def get_initial(self) :
      initial = super().get_initial()
      initial['tags'] = " ".join(self.object.tags.names())
      return initial
    
    
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user 
    
    def form_valid(self, form: form_class) :
        tags = form.cleaned_data['tags'] #اعمال تغییرات برای اینکه در فرم ویرایش هم تگ ها با فاصله نمایش داده شوند و نه با کاما
        self.object.tags.set(tags)
        
        def clean_slug(title) :
            title = re.sub(r'[^\w\s-]', '', title)
            title = re.sub(r'[-\s]+', '-', title)
            title = title.strip('-')
            if not title :
                title = 'پست'
            return title
        isinstance= form.save(commit=False)
        base_slug = slugify(clean_slug(isinstance.title), allow_unicode=True)  
        if isinstance.slug != base_slug :
            unique_slug = base_slug
            if Post.objects.filter(slug=unique_slug).exclude(pk=isinstance.pk).exists():
                unique_slug = f'{base_slug}-{isinstance.pk}'
            isinstance.slug = unique_slug
        isinstance.save()
        messages.success(self.request, 'پست با موفقیت به روز رسانی شد.')           
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_create'] = False
        return kwargs
    
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Post
    template_name = 'blog/post_delete.html'
    
    def get_object(self, queryset=None) :
        return Post.objects.get(slug=self.kwargs['slug'])
    
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user 
    
    def get_success_url(self) -> str:
        return reverse('blog_index')

    
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
    
@login_required
def bookmark_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    if request.method == 'POST':
        if BookmarkPost.objects.filter(post=post, user=user).exists():
            BookmarkPost.objects.filter(post=post, user=user).delete()
            bookmarked = False
        else :
            BookmarkPost.objects.create(post=post, user=user)
            bookmarked = True
        bookmarked_count = post.bookmarks.count() 
        return JsonResponse({"bookarked" :bookmarked , "bookmarks_count":bookmarked_count})                   
    
def archive_month(request, year, month):
    posts = Post.objects.filter(
        created_at__year = year,
        created_at__month = month
    )
    return render(request, 'blog/archive.html', {'list':posts})
        
class CategoryPostListView(generic.ListView):
    model = Post
    template_name = 'blog/posts_by_category.html'
    context_object_name = 'list'
    paginate_by = 6
    
    def get_queryset(self) :
        category_name = self.kwargs['name']
        return Post.objects.filter(categories__name=category_name).distinct()
    
    def get_context_data(self, **kwargs):
        context =super().get_context_data(**kwargs)
        context['category']=Category.objects.get(name=self.kwargs['name'])
        context['page_numbers'] = range(1, context['paginator'].num_pages + 1)
        return context
    
    
class PostListByTagView(generic.ListView):
    model = Post 
    context_object_name = 'list'  
    paginate_by = 6
    
    def get_queryset(self):
        # دریافت تگ از URL بر اساس slug
        tag_slug = self.kwargs['tag_slug']
        tag = Tag.objects.get(slug=tag_slug)
        # فیلتر کردن پست‌ها بر اساس تگ
        return Post.objects.filter(tags=tag)

    def get_context_data(self, **kwargs):
        context =super().get_context_data(**kwargs)
        # context['tag']=Tag.objects.get(name=self.kwargs['name'])
        context['page_numbers'] = range(1, context['paginator'].num_pages + 1)
        return context