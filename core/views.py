from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SalaoCadastroForm
from .models import DiaFuncionamento, Salao, Produto
from django.contrib.auth.hashers import make_password, check_password
from .models import Profissional, Corte
from .forms import ProfissionalForm

def home(request):
    return render(request, 'home.html')

def cadastro_view(request):
    if request.method == 'POST':
        form = SalaoCadastroForm(request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data['email']

                # 🚨 Verifica duplicidade de email
                if Salao.objects.filter(email=email).exists():
                    messages.error(request, '❌ Já existe um salão com esse email!')
                    return redirect('cadastro')

                # 🔐 Criptografar senha
                senha_hash = make_password(form.cleaned_data['senha'])

                # Criar SALÃO (sem User)
                salao = Salao.objects.create(
                    nome=form.cleaned_data['nome'],
                    nome_contato=form.cleaned_data['nome_contato'],
                    telefone=form.cleaned_data['telefone'],
                    email=email,
                    senha=senha_hash  # precisa ter esse campo no model
                )

                request.session['salao_id'] = salao.id
                request.session['tipo_usuario'] = 'dono'

                messages.success(request, f'✅ "{salao.nome}" criado! 30 dias GRÁTIS!')
                return redirect('dashboard')

            except Exception as e:
                messages.error(request, f'❌ Erro: {str(e)}')
        else:
            messages.error(request, '❌ Verifique os campos!')
    else:
        form = SalaoCadastroForm()

    return render(request, 'cadastro.html', {'form': form})
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        try:
            salao = Salao.objects.get(email=email)
            # Login com USER (não Salao)
            user = salao.dono
            if user.check_password(senha):
                request.session['salao_id'] = salao.id
                messages.success(request, 'Login OK!')
                return redirect('dashboard')
        except:
            pass
        messages.error(request, 'Email ou senha incorretos!')
    return render(request, 'login.html')

def dashboard(request):
    salao_id = request.session.get('salao_id')
    if not salao_id:
        return redirect('login')
    salao = Salao.objects.get(id=salao_id)
    return render(request, 'dashboard.html', {'salao': salao})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            salao = Salao.objects.get(email=email)

            if check_password(senha, salao.senha):
                request.session['salao_id'] = salao.id
                messages.success(request, 'Login OK!')
                return redirect('dashboard')

        except Salao.DoesNotExist:
            pass

        messages.error(request, 'Email ou senha incorretos!')

    return render(request, 'login.html')


from .models import Profissional
from .forms import ProfissionalForm

def cadastrar_profissional(request):
    salao_id = request.session.get('salao_id')
    if not salao_id:
        return redirect('login')

    salao = Salao.objects.get(id=salao_id)

    total_profissionais = salao.profissionais.count()

    if total_profissionais >= salao.max_profissionais:
        messages.error(request, "❌ Seu plano atingiu o limite de profissionais.")
        return redirect('dashboard')

    if request.method == 'POST':
        nome = request.POST.get('nome')
        idade = request.POST.get('idade')
        descricao = request.POST.get('descricao')
        foto = request.FILES.get('foto')

        Profissional.objects.create(
            nome=nome,
            idade=idade,
            descricao=descricao,
            foto=foto,
            salao=salao
        )

        messages.success(request, "✅ Profissional cadastrado!")
        return redirect('dashboard')

    return redirect('dashboard')

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Profissional

def desativar_profissional(request, id):
    if request.method == "POST":
        salao_id = request.session.get('salao_id')
        if not salao_id:
            return JsonResponse({'error': 'Não autorizado'}, status=403)

        profissional = get_object_or_404(
            Profissional,
            id=id,
            salao_id=salao_id
        )

        profissional.ativo = False
        profissional.save()

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Método inválido'}, status=400)


def ativar_profissional(request, id):
    if request.method == "POST":
        salao_id = request.session.get('salao_id')
        if not salao_id:
            return JsonResponse({'error': 'Não autorizado'}, status=403)

        profissional = get_object_or_404(
            Profissional,
            id=id,
            salao_id=salao_id
        )

        profissional.ativo = True
        profissional.save()

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Método inválido'}, status=400)

from django.shortcuts import render, redirect, get_object_or_404
from .models import Produto, Salao

def produtos(request):
    salao_id = request.session.get('salao_id')
    if not salao_id:
        return redirect('login')

    salao = Salao.objects.get(id=salao_id)
    produtos = Produto.objects.filter(salao=salao)

    return render(request, 'dashboard.html', {
        'salao': salao,
        'produtos': produtos,
        'pagina': 'produtos'
    })

def cadastrar_produto(request):

    if request.method == "POST":

        salao_id = request.session.get('salao_id')
        salao = Salao.objects.get(id=salao_id)

        produto_id = request.POST.get('produto_id')

        if produto_id:
            produto = Produto.objects.get(id=produto_id, salao=salao)
        else:
            produto = Produto(salao=salao)

        produto.nome = request.POST.get('nome')
        produto.valor = request.POST.get('valor')
        produto.descricao = request.POST.get('descricao')

        if request.FILES.get('foto'):
            produto.foto = request.FILES.get('foto')

        produto.save()

    return redirect('produtos')
def salvar_produto(request):
    salao_id = request.session.get('salao_id')
    if not salao_id:
        return redirect('login')

    salao = Salao.objects.get(id=salao_id)

    if request.method == 'POST':
        produto_id = request.POST.get('produto_id')
        nome = request.POST.get('nome')
        valor = request.POST.get('valor')
        descricao = request.POST.get('descricao')
        foto = request.FILES.get('foto')

        if produto_id:  # EDITAR
            produto = get_object_or_404(Produto, id=produto_id, salao=salao)
            produto.nome = nome
            produto.valor = valor
            produto.descricao = descricao
            if foto:
                produto.foto = foto
            produto.save()
        else:  # NOVO
            Produto.objects.create(
                salao=salao,
                nome=nome,
                valor=valor,
                descricao=descricao,
                foto=foto
            )

    return redirect('produtos')


def editar_produto(request, id):
    salao_id = request.session.get('salao_id')
    if not salao_id:
        return redirect('login')

    salao = Salao.objects.get(id=salao_id)
    produto = get_object_or_404(Produto, id=id, salao=salao)

    produtos = Produto.objects.filter(salao=salao)

    return render(request, 'dashboard.html', {
        'salao': salao,
        'produtos': produtos,
        'produto_editar': produto,
        'pagina': 'produtos'
    })


def excluir_produto(request, id):
    salao_id = request.session.get('salao_id')
    if not salao_id:
        return redirect('login')

    salao = Salao.objects.get(id=salao_id)
    produto = get_object_or_404(Produto, id=id, salao=salao)
    produto.delete()

    return redirect('produtos')   
    salao_id = request.session.get('salao_id')
    if not salao_id:
        return redirect('login')
    
    salao = Salao.objects.get(id=salao_id)
    produtos = Produto.objects.filter(salao=salao)

    return render(request,'dashboard.html',{
        'salao': salao,
        'produtos': produtos,
        'pagina': produtos
    })


from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def toggle_dia_funcionamento(request, dia_id):
    if request.method == "POST":
        salao_id = request.session.get('salao_id')
        if not salao_id:
            return JsonResponse({'error': 'Não autorizado'}, status=403)

        dia = get_object_or_404(
            DiaFuncionamento,
            id=dia_id,
            salao_id=salao_id
        )

        dia.ativo = not dia.ativo
        dia.save(update_fields=['ativo'])

        return JsonResponse({
            'success': True,
            'ativo': dia.ativo
        })

    return JsonResponse({'error': 'Método inválido'}, status=400)

def atualizar_horario_dia(request, dia_id):
    if request.method == "POST":
        salao_id = request.session.get('salao_id')
        if not salao_id:
            return JsonResponse({'error': 'Não autorizado'}, status=403)

        dia = get_object_or_404(
            DiaFuncionamento,
            id=dia_id,
            salao_id=salao_id
        )

        horario_inicio = request.POST.get('horario_inicio')
        horario_fim = request.POST.get('horario_fim')

        if horario_inicio >= horario_fim:
            return JsonResponse({
                'error': 'Horário inválido'
            }, status=400)

        dia.horario_inicio = horario_inicio
        dia.horario_fim = horario_fim
        dia.save(update_fields=['horario_inicio', 'horario_fim'])

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Método inválido'}, status=400)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import DiaFuncionamento, Salao  # ajuste se necessário


def configurar_dias(request):
    if request.method == "POST":

        salao_id = request.session.get('salao_id')
        if not salao_id:
            return JsonResponse({'error': 'Não autorizado'}, status=403)

        salao = get_object_or_404(Salao, id=salao_id)

        dias_padrao = [
            "segunda",
            "terca",
            "quarta",
            "quinta",
            "sexta",
            "sabado",
            "domingo",
        ]

        for dia in dias_padrao:
            DiaFuncionamento.objects.get_or_create(
                salao=salao,
                dia_semana=dia,
                defaults={
                    "horario_inicio": "08:00",
                    "horario_fim": "18:00",
                    "ativo": True
                }
            )

        return JsonResponse({"success": True})

    return JsonResponse({"error": "Método inválido"}, status=400)
def logout_view(request):
    request.session.flush()
    return redirect('home')



# Metodos de Cortes

def cortes(request):
    salao_id = request.session.get('salao_id')
    if not salao_id:
        return redirect("login")
    
    salao = Salao.objects.get(id=salao_id)
    cortes = Corte.objects.filter(salao=salao)

    return render(request,'dashboard.html',{
        'salao':salao,
        'cortes':cortes,
        'pagina':'cortes'
    })

def salvar_corte(request):
    salao_id = request.session.get("salao_id")
    if not salao_id:
        return redirect('login')
    
    salao = Salao.objects.get(id=salao_id)
    if request.method == "POST":
        corte_id = request.POST.get("corte_id")
        nome = request.POST.get("nome")
        valor = request.POST.get('valor')
        descricao = request.POST.get('descricao')
        tempo_execucao = request.POST.get('tempo_execucao')
        foto = request.FILES.get("foto")

        if corte_id:
            corte = get_object_or_404(Corte, id=corte_id, salao=salao)
            corte.nome = nome
            corte.valor = valor
            corte.descricao = descricao
            corte.tempo_execucao = tempo_execucao

            if foto:
                corte.foto = foto
            corte.save()
        else : 
            Corte.objects.create(
                salao=salao,
                nome=nome,
                valor=valor,
                descricao=descricao,
                tempo_execucao=tempo_execucao,
                foto=foto
            )
    return redirect("cortes")


def editar_corte(request, id):
    salao_id = request.session.get("salao_id")
    if not salao_id:
        return redirect("login")
    
    salao = Salao.objects.get(id=salao_id)
    corte = get_object_or_404(Corte, id=id, salao=salao)
    cortes = Corte.objects.filter(salao=salao)

    return render(request,'dashboard.html',{
        'salao': salao,
        'cortes': cortes,
        'corte_editar': corte,
        'pagina':'cortes'
    })


def excluir_corte(request,id):
    salao_id = request.session.get("salao_id")
    if not salao_id:
        return redirect("login")
    
    salao = Salao.objects.get(id=salao_id)
    corte = get_object_or_404(Corte, id=id, salao=salao)
    corte.delete()
    return redirect("cortes")


def toggle_corte(request, id):
    if request.method == 'POST':
        salao_id = request.session.get('salao_id')
        if not salao_id:
            return JsonResponse({'error': 'Não autorizado'}, status=403)
        
        corte = get_object_or_404(Corte,id=id, salao_id=salao_id)

        corte.ativo = not corte.ativo
        corte.save()

        return JsonResponse({
            'success': True,
            'ativo': corte.ativo
        })
    return JsonResponse({'erro': 'Metodo inválido'}, status=400)