from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormMixin
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Post, Like
from .forms import PostCreateForm, CommentForm


# def index(request):
#     post_list = Post.objects.filter(status='pub').order_by('-created_at')
#     return render(request, 'blog/post_list.html', {'list':post_list})

class IndexListView(generic.ListView):
    # model = Post  -> get all objects
    template_name = 'blog/post_list.html'
    context_object_name = 'list'

    def get_queryset(self):
        return Post.objects.filter(status='pub').order_by('-created_at')


# def post_detail(request, pk):
#     post_detail = get_object_or_404(Post, pk=pk, status='pub')
#     return render(request, 'blog/post_detail.html', {'detail':post_detail})


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
        context['comments'] = self.object.comments.all()
        context['comments_count'] = self.object.comments.count()
        context['likes_count'] = self.object.likes.count()
        context['form'] = self.get_form()
        if user.is_authenticated:
            context['liked'] = Like.objects.filter(post=self.object, user=user).exists()
        else :
            context['liked'] = False
        return context
    
    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk' : self.object.pk})
    
    def post(self, request, *args, **kwargs):
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
    

# def post_create(request):
#     if request.method == "POST":
#         user_form = PostCreateForm(request.POST)
#         if user_form.is_valid():
#             user_form.save()
#             user_form = user_form = PostCreateForm()
#     else :
#         user_form = PostCreateForm()
#     return render(request, 'blog/post_create.html', {'form':user_form})


class PostCreateView(generic.CreateView):
    form_class = PostCreateForm
    template_name = 'blog/post_create.html'
    
    def form_valid(self, form: form_class) :
        messages.success(self.request, 'پست با موفقیت ثبت شد.')
        return super().form_valid(form)


# def post_update(request, pk):
#     post  = get_object_or_404(Post, pk=pk)
#     form = PostCreateForm(request.POST or None, instance=post)
#     if form.is_valid():
#         form.save()
#         return redirect('blog_index')
#     return render(request, 'blog/post_create.html',{'form': form})

class PostUpdateview(generic.UpdateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/post_create.html'
    
    def form_valid(self, form: form_class) :
        messages.success(self.request, 'پست با موفقیت به روز رسانی شد.')
        return super().form_valid(form)


# def post_delete(request, pk):
#     post  = get_object_or_404(Post, pk=pk)
#     if request.method == 'POST':
#         post.delete()
#         return redirect('blog_index')
#     return render(request, 'blog/post_delete.html', context ={'post' : post})


class PostDeleteView(generic.DeleteView):
    model = Post
    template_name = 'blog/post_delete.html'
    # success_url ='/blog/' not reeverse('blog_index')

    def get_success_url(self) -> str:
        return reverse('blog_index')

    # success_url = reverse_lazy('blog_index')
    
    def delete(self, request, *args, **kwargs): 
        response = super().delete(request, *args, **kwargs) 
        messages.success(self.request, 'پست با موفقیت حذف شد.') 
        return response
    
    
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