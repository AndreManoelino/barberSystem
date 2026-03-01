from django.shortcuts import get_object_or_404, render, redirect
from core.models import Produto, Usuario,DiaFuncionamento,Agendamento
from datetime import datetime, timedelta

def listar_produtos(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login_cliente')

    usuario = get_object_or_404(Usuario, id=usuario_id, tipo='cliente')

    # ⚠️ Garantir que ele tenha salão
    if not usuario.salao:
        return render(request, 'clientes/produtos/listar.html', {
            'produtos': [],
            'erro': 'Cliente não está vinculado a um salão.'
        })

    produtos = Produto.objects.filter(
        salao_id=usuario.salao_id,  # 🔥 usando salao_id direto
        ativo=True
    ).order_by('-criado_em')

    return render(request, 'clientes/produtos/listar.html', {
        'produtos': produtos
    })
    print("SESSION:", request.session.items())




from datetime import datetime, timedelta

def gerar_horarios_disponiveis(salao, profissional, data, corte):

    dia_semana = data.strftime('%A').lower()

    dia = DiaFuncionamento.objects.filter(
        salao=salao,
        dia_semana=dia_semana,
        ativo=True
    ).first()

    if not dia:
        return []

    inicio = datetime.combine(data, dia.horario_inicio)
    fim = datetime.combine(data, dia.horario_fim)

    duracao_total = corte.tempo_execucao + 10

    horarios_disponiveis = []

    while inicio + timedelta(minutes=duracao_total) <= fim:

        hora_inicio = inicio.time()
        hora_fim = (inicio + timedelta(minutes=duracao_total)).time()

        conflito = Agendamento.objects.filter(
            profissional=profissional,
            data=data,
            status='agendado',
            hora_inicio__lt=hora_fim,
            hora_fim__gt=hora_inicio
        ).exists()

        if not conflito:
            horarios_disponiveis.append(hora_inicio)

        inicio += timedelta(minutes=10)

    return horarios_disponiveis



