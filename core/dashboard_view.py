from views import criar_dias_padrao
from .models import Salao

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    salao_id = self.request.session.get('salao_id')
    salao = Salao.objects.get(id=salao_id)

    criar_dias_padrao(salao)

    context['salao'] = salao
    context['dias_disponiveis'] = salao.dias_funcionamento.filter(ativo=True).count()

    return context