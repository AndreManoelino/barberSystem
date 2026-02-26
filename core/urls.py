from django.urls import path
from . import views
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('cadastro/', views.cadastro_view, name='cadastro'), 
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('profissionais/', views.cadastrar_profissional, name='cadastrar_profissional'),
    path('profissionais/desativar/<int:id>/', views.desativar_profissional, name='desativar_profissional'),
    path('profissionais/ativar/<int:id>/', views.ativar_profissional, name='ativar_profissional'),

    path('produtos/', views.produtos, name='produtos'),
    path('produtos/cadastrar/', views.cadastrar_produto, name='cadastrar_produto'),
    path('produtos/excluir/<int:id>/', views.excluir_produto, name='excluir_produto'),

    
    path('dias/configurar/', views.configurar_dias, name='configurar_dias'),

    path('dias/toggle/<int:dia_id>/', views.toggle_dia_funcionamento, name='toggle_dia_funcionamento'),
    path('dias/atualizar/<int:dia_id>/', views.atualizar_horario_dia, name='atualizar_horario_dia'),
    
    path('cortes/', views.cortes, name='cortes'),
    path('cortes/salvar/', views.salvar_corte, name='salvar_corte'),
    path('cortes/editar/<int:id>/', views.editar_corte, name='editar_corte'),
    path('cortes/excluir/<int:id>/', views.excluir_corte, name='excluir_corte'),
    path('cortes/toggle/<int:id>/', views.toggle_corte, name='toggle_corte'),
    
    path('logout/', views.logout_view, name='logout'),
]