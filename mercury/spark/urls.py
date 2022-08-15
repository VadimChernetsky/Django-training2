from .views import other_page
from django.urls import path
from .views import index
from .views import GHLoginView
from .views import profile
from .views import VHLogoutView
from .views import PravkaOsnovnyhSvedView
from .views import PRPasswordChangeView
from .views import RegisterUserView, RegisterDoneView
from .views import user_activate
from .views import DeleteUserView
from .views import by_rubric
from .views import detail
from .views import profile_detail
from .views import profile_add
from .views import profile_change
from .views import profile_delete

app_name = 'spark'
urlpatterns = [
    path('<int:rubric_pk>/<int:pk>/', detail, name='detail'),
    path('<int:pk>/', by_rubric, name='by_rubric'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index'),
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/login/', GHLoginView.as_view(), name='login'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/profile/izmenit/', PravkaOsnovnyhSvedView.as_view(), name='profile_izmenit'),
    path('accounts/profile/change/<int:pk>/', profile_change, name='profile_change'),
    path('accounts/profile/delete/<int:pk>/', profile_delete, name='profile_delete'),
    path('accounts/profile/add/', profile_add, name='profile_add'),
    path('accounts/profile/<int:pk>/', profile_detail, name='profile_detail'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/vyhod/', VHLogoutView.as_view(), name='vyhod'),
    path('accounts/password/smenaparolya/', PRPasswordChangeView.as_view(), name='izmenit_parol'),
]
