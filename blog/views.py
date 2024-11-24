from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormMixin
from django.views import generic

from .models import Post
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
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['form'] = self.get_form()
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