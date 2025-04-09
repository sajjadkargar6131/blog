import os
from django.contrib import messages
from django.shortcuts import redirect
# from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.urls import reverse
from .forms import NewsCreateForm
from .models import News


class NewsCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = NewsCreateForm
    template_name = 'news/news_create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        news_instance = form.save()
        messages.success(self.request,'خبر با موفقیت ثبت شد.')
        return redirect(news_instance.get_absolute_url())


class NewsListView(generic.ListView):
    template_name = 'news/news_list.html'
    context_object_name = 'list'
    paginate_by = 6

    def get_queryset(self):
        return News.objects.filter(status='pub').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_numbers'] = range(1, context['paginator'].num_pages + 1)
        return context


class NewsDetailView(generic.DetailView):
    model = News
    context_object_name = 'detail'
    template_name = 'news/news_detail.html'

    def get_success_url(self):
        return self.object.get_absolute_url()


class NewsDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = News
    template_name = 'news/news_delete.html'

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def get_success_url(self):
        return reverse('news_list')

    def form_valid(self, form):
        # حذف عکس کاور اگر وجود داشته باشد
        obj = self.get_object()
        if obj.cover:
            try:
                cover_path = obj.cover.path
                if os.path.isfile(cover_path):
                    os.remove(cover_path)
                else:
                    print(f"File not found: {cover_path}")
            except Exception as e:
                print(f"Error deleting file: {e}")

        messages.success(self.request, "خبر با موفقیت حذف شد")
        return super().form_valid(form)


class NewsUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = News
    form_class = NewsCreateForm
    template_name = 'news/news_create.html'

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user
