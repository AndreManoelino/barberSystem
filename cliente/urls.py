from django.urls import path
from . import views

urlpatterns = [
    path('produtos/', views.listar_produtos, name='listar_produtos'),
]