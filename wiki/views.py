from django.http import Http404,HttpResponse
from django.shortcuts import get_object_or_404,redirect,render
from django.urls import reverse,reverse_lazy
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic import DetailView,ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView,UpdateView


from wiki import forms
from wiki import utils
from wiki.markdown import Markdown
from wiki.models import Article,Tag,Term
from wiki.pages import Error404


# Create your views here.

class TagView(DetailView):
    model = Tag
    context_object_name = 'tag'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        articles = []
        for article in self.object.articles.all():
            if not article.is_redirect:
                articles.append(article)

        context['articles'] = articles

        return context

class TagEditView(UpdateView):
    model = Tag
    context_object_name = 'tag'
    fields = ('name','slug','description')


class ArticleListView(ListView):
    queryset = Article.objects.filter(is_published=True).exclude(slug__startswith='special:')
    context_object_name = 'articles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = 'All Pages on Langthil'

        return context


class WikiPageView(View):
    article_template = 'wiki/article_detail.html'
    nsfw_template = 'wiki/article_nsfw.html'
    disambiguation_template = 'wiki/article_list.html'
    show_nsfw_content = False
    create_url = None

    def get(self, request, slug, namespace):
        self.show_nsfw_content = self.show_nsfw_content or request.session.get('show_nsfw', False)

        try:
            redirected, article = self.get_article(slug, namespace)
            context = {
                'article':article,
                'redirected':redirected,
                'canonical_url':article.get_absolute_url(),
            }
        except Article.DoesNotExist:
            article = Error404.get()
            context = {
                'article':article,
                'create_url':reverse('wiki-new', args=[namespace, slug]),
            }

        if article.is_nsfw and not self.show_nsfw_content:
            return render(request, self.nsfw_template, context=context)
        else:
            return render(request, self.article_template, context=context)

    def post(self, request, *args, **kwargs):
        if request.POST.get('show-me'):
            self.show_nsfw_content = True
            if request.POST.get('remember'):
                request.session['show_nsfw'] = True

        return self.get(request, *args, **kwargs)

    def get_article(self, slug, namespace):
        if self.request.user.has_perm('wiki.change_article') or 'preview' in self.request.GET:
            qs = Article.objects
        else:
            qs = Article.objects.filter(is_published=True)

        article = qs.get(slug=slug, namespace=namespace)

        if article.is_redirect and self.request.GET.get('redirect') != 'no':
            try:
                return (article, article.get_redirect(qs))
            except Article.DoesNotExist:
                pass

        return (None, article)


class WikiUpdateView(UpdateView):
    model = Article
    form_class = forms.ArticleUpdateForm

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()

        return queryset.get(**self.kwargs)

class WikiCreateView(CreateView):
    model = Article
    form_class = forms.ArticleCreateForm

    def get_initial(self):
        slug = self.kwargs['slug']
        title = slug.replace('_', ' ').strip().title()

        if not self.kwargs['slug'].startswith('_'):
            slug = utils.slugify(title)

        initial = {
            'title': title,
            'slug': slug,
            'namespace': self.kwargs['namespace'],
            'is_published': True,
        }

        template = self._get_template()
        if template:
            initial['markdown'] = template

        return initial

    def _get_template(self):
        # Start with a bogus "extra" namespace
        # We'll pop it off before the first lookup, which is how we'll get to the root
        namespace = utils.join_path(self.kwargs['namespace'], '__extra__')

        while namespace:
            namespace = utils.namespace(namespace)

            try:
                tmpl = Article.objects.get(namespace=namespace, slug='_template')
                return tmpl.markdown
            except Article.DoesNotExist:
                pass

        return None

class WikiMoveView(WikiUpdateView):
    form_class = None
    fields = ('namespace','slug')

    def form_valid(self, form):
        response = super().form_valid(form)

        self.__create_redirect_page()

        return response

    def __create_redirect_page(self):
        # Verify we're changing more than case
        if self.kwargs['namespace'].lower() == self.object.namespace.lower():
            if self.kwargs['slug'].lower() == self.object.slug.lower():
                return

        redirect = Article(
            title = self.object.title,
            is_published = self.object.is_published,
            is_nsfw = self.object.is_nsfw,
            is_spoiler = self.object.is_spoiler,
            **self.kwargs,
        )
        redirect.markdown = '[[REDIRECT:/{article}]]'.format(
            article = utils.join_path(self.object.namespace, self.object.slug),
        )
        redirect.save()

class PreviewView(View):
    def post(self, request):
        return HttpResponse(Markdown.to_html(request.POST.get('markdown', '')))


class GlossaryView(ListView):
    model = Term
    context_object_name = 'terms'

class TermCreateView(CreateView):
    model = Term
    fields = ('term', 'definition')

class TermEditView(UpdateView):
    model = Term
    fields = ('term', 'definition')


