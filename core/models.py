from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class Salao(models.Model):
    PLANOS = [
        ('basico', 'Básico (1 profissional)'),
        ('equipe_pequena', 'Equipe Pequena (2-5 profissionais)'),
        ('equipe_media', 'Equipe Média (6-15 profissionais)'),
        ('equipe_grande', 'Equipe Grande (+15 profissionais)'),
    ]
    
    nome = models.CharField(max_length=200, unique=True)
    nome_contato = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15)
    senha = models.CharField(max_length=255) 
    plano = models.CharField(max_length=20, choices=PLANOS, default='basico')
    max_profissionais = models.IntegerField(default=1)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    trial_inicio = models.DateTimeField(auto_now_add=True)
    trial_fim = models.DateTimeField()
    ativo = models.BooleanField(default=True)
    profissionais_cadastrados = models.IntegerField(default=0)


    def save(self, *args, **kwargs):
        if not self.pk:  
            self.trial_inicio = timezone.now()
            self.trial_fim = self.trial_inicio + timedelta(days=30)
        super().save(*args, **kwargs)

    def trial_ativo(self):
        return timezone.now() <= self.trial_fim if self.trial_fim else False
    
    def __str__(self):
        return self.nome

class Profissional(models.Model):
    nome = models.CharField(max_length=200)
    idade = models.IntegerField(null=True, blank=True)
    descricao = models.TextField(blank=True)
    foto = models.ImageField(upload_to='profissionais/', null=True, blank=True)

    salao = models.ForeignKey(Salao, on_delete=models.CASCADE, related_name='profissionais')
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nome} - {self.salao.nome}"


# Prodtutos

# models.py

class Produto(models.Model):
    salao = models.ForeignKey(Salao, on_delete=models.CASCADE, related_name='produtos')
    nome = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.TextField(blank=True)
    foto = models.ImageField(upload_to='produtos/', null=True, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class DiaFuncionamento(models.Model):
    DIAS_SEMANA = [
        ('segunda', 'Segunda-feira'),
        ('terca', 'Terça-feira'),
        ('quarta', 'Quarta-feira'),
        ('quinta', 'Quinta-feira'),
        ('sexta', 'Sexta-feira'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]

    salao = models.ForeignKey(
        Salao,
        on_delete=models.CASCADE,
        related_name='dias_funcionamento'
    )
    dia_semana = models.CharField(max_length=20, choices=DIAS_SEMANA)
    ativo = models.BooleanField(default=False)
    horario_inicio = models.TimeField(default='08:00')
    horario_fim = models.TimeField(default='18:00')

    class Meta:
        unique_together = ['salao', 'dia_semana']
        ordering = ['id']

    def __str__(self):
        return f"{self.get_dia_semana_display()} - {self.salao.nome}"

class Corte(models.Model):
    salao = models.ForeignKey(Salao, on_delete=models.CASCADE, related_name='cortes')
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tempo_execucao = models.PositiveBigIntegerField(help_text="Tempo estimado em minutos")
    foto = models.ImageField(upload_to='cortes/',null=True,blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['nome']
        unique_together = ['salao','nome']

    def __str__(self):
        return f"{self.nome} - {self.salao.nome}"
    

