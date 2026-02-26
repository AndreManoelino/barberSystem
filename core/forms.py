from django import forms
from django import forms
from django.contrib.auth.hashers import make_password
from .models import Salao
from .models import Profissional
from .models import Produto

class SalaoCadastroForm(forms.Form):
    nome = forms.CharField(max_length=200, label='Nome da Barbearia *')
    nome_contato = forms.CharField(max_length=200, label='Nome do Contato *')
    telefone = forms.CharField(max_length=15, label='Telefone *')
    email = forms.EmailField(label='Email *')
    senha = forms.CharField(min_length=6, max_length=15, label='Senha *', widget=forms.PasswordInput())
    termos = forms.BooleanField(required=True, label='Aceito os termos de uso')
    
    def clean_senha_hash(self):
        """Gera senha_hash automaticamente"""
        senha = self.cleaned_data.get('senha')
        if senha:
            return make_password(senha)
        return None
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        
        # Validação email único
        if email and Salao.objects.filter(email=email).exists():
            raise forms.ValidationError("❌ Email já cadastrado!")
        
        # Senha mínima
        senha = cleaned_data.get('senha')
        if senha and len(senha) < 6:
            raise forms.ValidationError("❌ Senha deve ter pelo menos 6 caracteres!")
            
        return cleaned_data



class ProfissionalForm(forms.ModelForm):
    class Meta:
        model = Profissional
        fields = ['nome', 'idade', 'descricao', 'foto']


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome','valor','descricao','foto']