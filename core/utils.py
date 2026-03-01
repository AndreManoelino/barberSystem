from datetime import datetime, timedelta
from core.models import DiaFuncionamento, Agendamento


def gerar_horarios_disponiveis(salao, profissional, data, corte):

    dias_map = {
        'Monday': 'segunda',
        'Tuesday': 'terca',
        'Wednesday': 'quarta',
        'Thursday': 'quinta',
        'Friday': 'sexta',
        'Saturday': 'sabado',
        'Sunday': 'domingo',
    }

    dia_semana = dias_map[data.strftime('%A')]

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

    horarios = []

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
            horarios.append(hora_inicio.strftime('%H:%M'))

        inicio += timedelta(minutes=10)

    return horarios