from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .models import AdvUser
from .models import SuperRubric, SubRubric
from .apps import user_registered
from django.forms import inlineformset_factory
from .models import Ob, AdditionalImage
from captcha.fields import CaptchaField
from .models import Comment

#форма, для ввода основных данных
class PravkaOsnovnyhSvedForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name', 'last_name', 'send_messages')

#форма, для занесения сведений о новои пользователе
class RegisterUserForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Адрес электронной почты')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput, help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль (повторно)', widget=forms.PasswordInput, help_text='Введите тот же самый пароль еще раз для проверки')

    #валидация пароля
    def clean_password(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    #проверяем, совпадают ли оба пароля
    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Введенные пароли не совпадают', code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False    #является ли пользователь активным
        user.is_activated = False #выполнил ли пользователь активацию
        if commit:
            user.save()
        #сохранить закодированый пароль, для активации
        user_registered.send(RegisterUserForm, instance=user)
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'send_messages')

#форма надрубрики
class SubRubricForm(forms.ModelForm):
    #обязательное для заполнения
    super_rubric = forms.ModelChoiceField(queryset=SuperRubric.objects.all(), empty_label=None, label='Надрубрика', required=True)

    class Meta:
        model = SubRubric
        fields = '__all__'

#форма поиска
class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=20, label='')

#форма добавления объявлений
class ObForm(forms.ModelForm):
    class Meta:
        model = Ob
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}

AIFormSet = inlineformset_factory(Ob, AdditionalImage, fields='__all__')

#коментарии зарегистрированного пользователя
class UserCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('is_active',)
        widgets = {'bb': forms.HiddenInput}

#коментарии гостя
class GuestCommentForm(forms.ModelForm):
    captcha = CaptchaField(label='Введите текст с картинки', error_messages={'invalid': 'Неправильный текст'})

    class Meta:
        model = Comment
        exclude = ('is_active',)
        widgets = {'bb': forms.HiddenInput}
