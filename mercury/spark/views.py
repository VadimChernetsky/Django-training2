from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.views import PasswordChangeView
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from django.core.signing import BadSignature
from django.views.generic.edit import DeleteView
from django.contrib.auth import logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect

from .models import AdvUser
from .models import SubRubric, Ob
from .models import Comment

from .forms import PravkaOsnovnyhSvedForm
from .forms import RegisterUserForm
from .forms import SearchForm
from .forms import ObForm, AIFormSet
from .forms import UserCommentForm, GuestCommentForm

from .utilities import signer

# Create your views here.
def index(request):
    bbs = Ob.objects.filter(is_active=True)
    context = {'bbs': bbs}
    return render(request, 'spark/index.html', context)

#контроллер для вывода вспомогательной страницы
def other_page(request, page):
    try:
        template = get_template('spark/' + page +'.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))

class GHLoginView(LoginView):
    template_name = 'spark/login.html'

@login_required
def profile(request):
    bbs = Ob.objects.filter(author=request.user.pk)
    context = {'bbs': bbs}
    return render(request, 'spark/profile.html', context)

class VHLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'spark/vyhod.html'


#изменить личные данные
class PravkaOsnovnyhSvedView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'spark/profile_izmenit.html'
    form_class = PravkaOsnovnyhSvedForm
    success_url = reverse_lazy('spark:profile')
    success_message = 'Данные пользователя изменены'

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


#изменить пароль
class PRPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'spark/izmenit_parol.html'
    success_url = reverse_lazy('spark:profile')
    success_message = 'Пароль пользователя изменен'

#контроллер, регестрирующий пользователя
class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'spark/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('spark:register_done')

#сообщение об успешной регистрации
class RegisterDoneView(TemplateView):
    template_name = 'spark/register_done.html'

#активация пользователя
def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        # если цифровая подпись скомпроментирована
        return render(request, 'spark/bad_signature.html')
    user = get_object_or_404(AdvUser, username=username)
    if user.is_activated:
        template = 'spark/user_is_activated.html'
    else:
        template = 'spark/activation_done.html'
        user.is_active = True
        #если пользователь был активирован ранее
        user.is_activated = True
        user.save()
    return render(request, template)

#удаление пользователя
class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'spark/delete_user.html'
    success_url = reverse_lazy('spark:index')

    #сохраняю ключ, текущего пользователя
    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    #делаю выход, перед удалением
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, **kwargs)

    #ищу пользователя по ключу для удаления
    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)

def by_rubric(request,pk):
    rubric = get_object_or_404(SubRubric, pk=pk)
    bbs = Ob.objects.filter(is_active=True, rubric=pk)
    #фрагмент кода отвечающий за фильтрацию объявлений по искомому слову
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        bbs = bbs.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(bbs, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'rubric': rubric, 'page': page, 'bbs': page.object_list, 'form': form}
    return render(request, 'spark/by_rubric.html', context)

#информация об объявлении
def detail(request, rubric_pk, pk):
    bb = get_object_or_404(Ob, pk=pk)
    #дополнительные иллюстрации
    ais = bb.additionalimage_set.all()
    comments = Comment.objects.filter(bb=pk, is_active=True)
    initial = {'bb': bb.pk}
    if request.user.is_authenticated:
        initial['author'] = request.user.username
        form_class = UserCommentForm
    else:
        form_class = GuestCommentForm
    form = form_class(initial=initial)
    if request.method == 'POST':
        c_form = form_class(request.POST)
        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен')
        else:
            form = c_form
            messages.add_message(request, messages.WARNING, 'Комментарий не добавлен')
    context = {'bb': bb, 'ais': ais, 'comments': comments, 'form': form}
    return render(request, 'spark/detail.html', context)

#объявления доступные зарегестрированному пользователю
@login_required
def profile_detail(request, pk):
    bb = get_object_or_404(Ob, pk=pk)
    ais = bb.additionalimage_set.all()
    comments = Comment.objects.filter(bb=pk, is_active=True)
    context = {'bb': bb, 'ais': ais, 'comments': comments}
    return render(request, 'spark/profile_detail.html', context)

#добавиить объявление
@login_required
def profile_add(request):
    if request.method == 'POST':
        form = ObForm(request.POST, request.FILES)
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление добавлено')
                return redirect('spark:profile')
    else:
        form = ObForm(initial={'author': request.user.pk})
        formset = AIFormSet()
    context = {'form': form, 'formset': formset}
    return render(request, 'spark/profile_add.html', context)

#исправить объявление
@login_required
def profile_change(request, pk):
    bb = get_object_or_404(Ob, pk=pk)
    if request.method == 'POST':
        form = ObForm(request.POST, request.FILES, instance=bb)
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление исправлено')
                return redirect('spark:profile')
    else:
        form = ObForm(instance=bb)
        formset = AIFormSet(instance=bb)
    context = {'form': form, 'formset': formset}
    return render(request, 'spark/profile_change.html', context)

#удалить объявление
@login_required
def profile_delete(request, pk):
    bb = get_object_or_404(Ob, pk=pk)
    if request.method == 'POST':
        bb.delete()
        messages.add_message(request, messages.SUCCESS, 'Объявление удалено')
        return redirect('spark:profile')
    else:
        context = {'bb': bb}
        return render(request, 'spark/profile_delete.html', context)