from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormMixin
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect

from .models import Post, Like, BookmarkPost
from .forms import PostCreateForm, CommentForm



class IndexListView(generic.ListView):
    # model = Post  -> get all objects
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

    def get_queryset(self):
        return Post.objects.filter(status='pub').order_by('-created_at')
    
    def get_context_data(self, **kwargs) :
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter().order_by('-datetime_created')
        context['comments_count'] = self.object.comments.count()
        context['likes_count'] = self.object.likes.count()
        context['bookmark_count'] = self.object.bookmarks.count()
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
    
    def get_success_url(self):
        return self.object.get_absolute_url()


class PostCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = PostCreateForm
    template_name = 'blog/post_create.html'
    
    def form_valid(self, form: form_class) :
        form.instance.author = self.request.user
        messages.success(self.request, 'پست با موفقیت ثبت شد.')
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/post_create.html'
    
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
        messages.success(self.request, 'پست با موفقیت به روز رسانی شد.')
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Post
    template_name = 'blog/post_delete.html'
    # success_url ='/blog/' not reeverse('blog_index')
    
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user 
    
    def get_success_url(self) -> str:
        return reverse('blog_index')

    # success_url = reverse_lazy('blog_index')
    
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
