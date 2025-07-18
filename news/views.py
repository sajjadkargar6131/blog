from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.views import generic
from django.views.generic.edit import FormMixin
from django.urls import reverse
from django.utils.timezone import now

from accounts.models import Activity
from .forms import NewsCreateForm, NewsCommentForm
from .models import News, NewsUniqueView
from blog.utils import get_clinet_ip


class NewsCreateView(PermissionRequiredMixin, LoginRequiredMixin, generic.CreateView):
    form_class = NewsCreateForm
    template_name = 'news/news_create.html'
    permission_required = 'news.add_news'

    def form_valid(self, form):
        form.instance.author = self.request.user
        news_instance = form.save()
        messages.success(self.request, 'خبر با موفقیت ثبت شد.')
        Activity.objects.create(
            user=self.request.user,
            action='news_create',
            timestamp=now(),
            description='ارسال خبر جدید'
        )
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

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        ip = get_clinet_ip(request)
        user = request.user if request.user.is_authenticated else None

        if not NewsUniqueView.objects.filter(news=self.object, ip_address=ip, user=user).exists():
            NewsUniqueView.objects.create(news=self.object, ip_address=ip, user=user)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments_qs = self.object.comments.filter(publish=True)
        context['comments'] = comments_qs.order_by('-datetime_created')
        context.update({
            'comments_count': self.object.comments_count,
            'form': self.get_form(),
            'unique_views': self.object.unique_views,
        })
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')

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
        Activity.objects.create(
            user=self.request.user,
            action='news_delete',
            timestamp=now(),
            description='حذف خبر'
        )
        messages.success(self.request, "خبر با موفقیت حذف شد")
        return super().form_valid(form)


class NewsUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = News
    form_class = NewsCreateForm
    template_name = 'news/news_create.html'

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def form_valid(self, form):
        Activity.objects.create(
            user=self.request.user,
            action='news_edit',
            timestamp=now(),
            description='ویرایش خبر'
        )
        messages.success(self.request, "خبر با موفقیت ویرایش شد")
        return super().form_valid(form)
