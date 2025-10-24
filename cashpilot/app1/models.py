from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import date, datetime, time
from calendar import monthrange

class Entradas(models.Model):
    descricao = models.CharField(max_length=100)
    valor = models.DecimalField(
        default=0.0,
        verbose_name="valor ganho R$",
        max_digits=15,
        decimal_places=2,
        null=False,
        blank=False
    )
    date = models.DateField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entradas')

    def _str_(self):
        
        return self.descricao[:15] + "... - R$ " + str(self.valor)

class Saidas(models.Model):
    OPCOES_DESCRICAO = [
        ('alimentacao', 'Alimentação'),
        ('transporte', 'Transporte'),
        ('moradia', 'Moradia'),
        ('lazer', 'Lazer'),
        ('outros', 'Outros'),
    ]
    descricao = models.CharField(max_length=100, choices=OPCOES_DESCRICAO)
    valor = models.DecimalField(
        default=0.0,
        verbose_name="valor gasto R$",
        max_digits=15,
        decimal_places=2,
        null=False,
        blank=False
    )
    date = models.DateField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saidas')

    def _str_(self):
        
        return self.descricao[:15] + "... - R$ " + str(self.valor)

class Saldo(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saldos')
    valor = models.DecimalField(
        default=0.0,
        verbose_name="Saldo R$",
        max_digits=15,
        decimal_places=2
    )
   
    data_registro = models.DateTimeField(default=timezone.now, verbose_name="Data/Hora do Registro")
    

    @classmethod
    def criar_registro_saldo_apos_transacao(cls, user):
        """
        Calcula o saldo cumulativo total do usuário e salva um NOVO registro 
        de Saldo para rastrear o histórico transacional.
        """
       
        total_entradas = Entradas.objects.filter(owner=user).aggregate(Sum("valor"))["valor__sum"] or 0
        total_saidas = Saidas.objects.filter(owner=user).aggregate(Sum("valor"))["valor__sum"] or 0
        saldo_cumulativo = total_entradas - total_saidas

       
        saldo_obj = cls.objects.create(
            owner=user,
            valor=saldo_cumulativo,
            data_registro=timezone.now()
        )
        return saldo_obj

    def _str_(self):
        return f"Saldo de R$ {self.valor} em {self.data_registro.strftime('%Y-%m-%d %H:%M')}"
    
class Limite_gasto_mensal(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='limites_gasto_mensal')
    valor_limite = models.DecimalField(
        default=0.0,
        verbose_name="Limite de Gasto Mensal R$",
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True
    )
    data_definicao = models.DateTimeField(default=timezone.now, verbose_name="Data/Hora da Definição")

    def _str_(self):
        return f"Limite de Gasto Mensal de R$ {self.valor_limite} definido em {self.data_definicao.strftime('%Y-%m-%d %H:%M')}"