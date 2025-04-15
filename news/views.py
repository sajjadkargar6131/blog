import os
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.views.generic.edit import FormMixin
from django.urls import reverse
from .forms import NewsCreateForm, NewsCommentForm
from .models import News


class NewsCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = NewsCreateForm
    template_name = 'news/news_create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        news_instance = form.save()
        messages.success(self.request, 'خبر با موفقیت ثبت شد.')
        return redirect(news_instance.get_absolute_url())


class AllNewsListView(generic.ListView):
    template_name = 'news/news_list_all.html'
    context_object_name = 'list'
    paginate_by = 10

    def get_queryset(self):
        return News.objects.filter(status='pub').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_numbers'] = context['paginator'].page_range
        return context


class NewsListView(generic.ListView):
    template_name = 'news/news_list.html'
    context_object_name = 'list'

    def get_queryset(self):
        return News.objects.filter(status='pub').order_by('-created_at')[:10]


class NewsDetailView(FormMixin, generic.DetailView):
    model = News
    context_object_name = 'detail'
    template_name = 'news/news_detail.html'
    form_class = NewsCommentForm

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_queryset(self):
        return News.objects.filter(status='pub').select_related('author')

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        comments_qs = self.object.comments.filter(publish=True)
        context['comments'] = comments_qs.order_by('-datetime_created')
        context.update({
            'comments_count': self.object.comments_count,
            'form': self.get_form()
        })
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')  # استفاده از redirect به جای HttpResponseRedirect

        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            comment = form.save(commit=False)
            comment.news = self.object
            comment.user = request.user
            comment.save()
            messages.success(request, 'نظر شما با موفقیت ثبت شد. در صورت تایید مدیر نمایش داده میشود')
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


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
