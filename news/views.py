from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .forms import NewsCreateForm
from .models import News


class NewsCreateView(LoginRequiredMixin, generic.CreateView):
    form_class = NewsCreateForm
    template_name = 'news/news_create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        news_instance = form.save()
        return HttpResponseRedirect(news_instance.get_absolute_url())


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