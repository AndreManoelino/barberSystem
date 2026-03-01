from django import forms
from django.contrib.auth.hashers import make_password
from .models import Salao, Usuario
from .models import Profissional
from .models import Produto
from django.contrib.auth.forms import UserCreationForm

class SalaoCadastroForm(forms.Form):
    nome = forms.CharField(max_length=200, label='Nome da Barbearia *')
    nome_contato = forms.CharField(max_length=200, label='Nome do Contato *')
    cep= forms.CharField(max_length=200, label='Cep*')
    bairro = forms.CharField(max_length=200, label='Bairro *')
    numero = forms.CharField(max_length=200, label='Número do salão *')
    rua = forms.CharField(max_length=200, label='Nome da Rua*')
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


from django import forms
from .models import Usuario

class ClienteCadastroForm(forms.ModelForm):
    senha1 = forms.CharField(
        widget=forms.PasswordInput,
        label="Senha"
    )
    senha2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirmar Senha"
    )

    class Meta:
        model = Usuario
        fields = ['nome', 'email']

    def clean(self):
        dados = super().clean()
        senha1 = dados.get("senha1")
        senha2 = dados.get("senha2")

        if senha1 and senha2 and senha1 != senha2:
            raise forms.ValidationError("As senhas não coincidem.")

        return dados

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.tipo = 'cliente'
        usuario.salvar_senha(self.cleaned_data['senha1'])

        if commit:
            usuario.save()

        return usuario