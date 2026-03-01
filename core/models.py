from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import logging
import requests

logger = logging.getLogger(__name__)

class Salao(models.Model):
    PLANOS = [
        ('basico', 'Básico (2 profissional)'),
        ('equipe_pequena', 'Equipe Pequena (5 profissionais)'),
        ('equipe_media', 'Equipe Média (15 profissionais)'),
        ('equipe_grande', 'Equipe Grande (30)'),
    ]
    
    nome = models.CharField(max_length=200, unique=True)
    nome_contato = models.CharField(max_length=200)
    numero = models.CharField(max_length=200)
    bairro = models.CharField(max_length=100, null=True, blank=True)
    cep = models.CharField(max_length=20, null=True, blank=True)
    rua = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15)
    senha = models.CharField(max_length=255) 
    plano = models.CharField(max_length=20, choices=PLANOS, default='basico')
    max_profissionais = models.IntegerField(default=2)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    trial_inicio = models.DateTimeField(auto_now_add=True)
    trial_fim = models.DateTimeField()
    ativo = models.BooleanField(default=True)
    profissionais_cadastrados = models.IntegerField(default=0)
    latitude = models.FloatField(null=True, blank=True, default=None)
    longitude = models.FloatField(null=True, blank=True, default=None)

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        # Geocode depois de salvar o objeto
        if self.cep and (self.latitude is None or self.longitude is None):
            self.salvar_coordenadas()

            super().save(update_fields=[
                "latitude",
                "longitude",
                "rua",
                "bairro"
            ])

            super().save(update_fields=["latitude", "longitude"])
            
    def trial_ativo(self):
        return timezone.now() <= self.trial_fim if self.trial_fim else False
    

    def salvar_coordenadas(self):
        try:
            if not self.cep:
                return

            import requests

            cep_limpo = "".join(filter(str.isdigit, self.cep))

            headers = {
                "User-Agent": "barberSystem"
            }

            # ===============================
            # STEP 1 → Buscar CEP BrasilAPI
            # ===============================

            try:
                url = f"https://brasilapi.com.br/api/cep/v1/{cep_limpo}"

                response = requests.get(url, timeout=10, headers=headers)

                if response.status_code == 200:
                    data = response.json()

                    # Latitude / Longitude se existir
                    if "location" in data and data["location"]:
                        coords = data["location"]["coordinates"]

                        self.latitude = float(coords["latitude"])
                        self.longitude = float(coords["longitude"])

                        # Atualiza endereço também
                        self.rua = data.get("street", self.rua)
                        self.bairro = data.get("neighborhood", self.bairro)

                        return

            except Exception:
                pass

            # ===============================
            # STEP 2 → Fallback OpenStreetMap
            # ===============================

            query = f"{cep_limpo}, Brazil"

            url = "https://nominatim.openstreetmap.org/search"

            params = {
                "q": query,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:

                data = response.json()

                if data:

                    result = data[0]

                    self.latitude = float(result["lat"])
                    self.longitude = float(result["lon"])

                    # Reverse geocode detalhes
                    address = result.get("display_name", "")

                    parts = address.split(",")

                    if len(parts) > 1:
                        self.bairro = parts[1].strip()

                    return

        except Exception as e:
            print("🔥 ERRO GEO:", e)


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
    

from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Usuario(models.Model):
    TIPOS = [
        ('dono','Dono'),
        ('profissional','Profissional'),
        ('cliente','Cliente'),        
    ]

    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    salao = models.ForeignKey(Salao, on_delete=models.CASCADE, null=True, blank=True)
    ativo = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='usuarios/', null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def salvar_senha(self, senha_pura):
        self.senha = make_password(senha_pura)

    def verificar_senha(self, senha_pura):
        return check_password(senha_pura, self.senha)

    def __str__(self):
        return f"{self.nome} - {self.tipo}"
    

class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    telefone = models.CharField(max_length=15)

    def __str__(self):
        return self.usuario.nome