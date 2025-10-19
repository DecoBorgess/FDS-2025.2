from django.shortcuts import render, redirect
from .models import Entradas,Saidas,Saldo
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
import datetime
import json
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

def index(request):
    return render(request, 'app1/html/index.html')

@login_required
def entradas_view(request):
    errors = None
    if request.method == 'POST':
        descricao = request.POST.get("descricao")
        valor = request.POST.get("valor")
        date_str = request.POST.get("date") 

        if descricao and valor and date_str:
            try:
                valor = float(valor)
                entrada = Entradas(
                    descricao=descricao,
                    valor=valor,
                    date=date_str, 
                    owner=request.user
                )
                entrada.save()
                Saldo.criar_registro_saldo_apos_transacao(request.user)
                
                return redirect('entradas')  
            except Exception as e:
                errors = f"Erro ao salvar: {e}"
        else:
            errors = "Todos os campos são obrigatórios."

    context = {"errors": errors}
    return render(request, "app1/html/entradas.html", context)

@login_required
def saidas_view(request):
    errors = []
    selected_descricao = ''
    valor = ''
    date_str = ''

    if request.method == "POST":
        selected_descricao = request.POST.get("descricao", "").strip()
        valor = request.POST.get("valor", "").strip()
        date_str = request.POST.get("date", "").strip()

        
        if not selected_descricao:
            errors.append("A descrição é obrigatória.")
        if not valor:
            errors.append("O valor é obrigatório.")
        else:
            try:
                valor = float(valor)
            except ValueError:
                errors.append("O valor deve ser numérico.")
        if not date_str:
            errors.append("A data é obrigatória.")

        
        if not errors:
            Saidas.objects.create(
                descricao=selected_descricao,
                valor=valor,
                date=date_str,
                owner=request.user
            )
            
            
            Saldo.criar_registro_saldo_apos_transacao(request.user)
            
            return redirect("saidas")

    context = {
        "errors": errors,
        "opcoes_descricao": Saidas.OPCOES_DESCRICAO,
        "selected_descricao": selected_descricao,
        "valor": valor,
        "date": date_str
    }
    return render(request, "app1/html/saidas.html", context)

@login_required
def extrato_views(request):
    entradas=Entradas.objects.filter(owner=request.user).order_by('-date')
    saidas=Saidas.objects.filter(owner=request.user).order_by('-date')
    context={'entradas':entradas,'saidas':saidas}
    return render(request,'app1/html/extrato.html',context)

@login_required
def nav_view(request):
    
    try:
        
        saldo = Saldo.objects.filter(owner=request.user).latest('data_registro')
    except Saldo.DoesNotExist:
        
        saldo = Saldo(owner=request.user, valor=0.0)
        
    context={'saldo': saldo}
    return render(request,'app1/html/nav.html',context)

@login_required
def dashboard(request):

    ano = datetime.date.today().year
    mes = datetime.date.today().month

    
    saldos_anuais = []
    for m in range(1, 13):
        try:
            ultimo_saldo = Saldo.objects.filter(owner=request.user, data_registro__year=ano, data_registro__month=m).latest('data_registro')
            saldos_anuais.append(float(ultimo_saldo.valor))
        except Saldo.DoesNotExist:
            saldos_anuais.append(0.0)

    meses_rotulos = [f"Mês {m}" for m in range(1, 13)]
    saldo_positivo = [s if s > 0 else 0 for s in saldos_anuais]
    saldo_negativo = [abs(s) if s < 0 else 0 for s in saldos_anuais]
    saldo_liquido = saldos_anuais

    
    entradas = Entradas.objects.filter(owner=request.user, date__year=ano, date__month=mes).aggregate(Sum("valor"))["valor__sum"] or 0
    saidas = Saidas.objects.filter(owner=request.user, date__year=ano, date__month=mes).aggregate(Sum("valor"))["valor__sum"] or 0


    saidas_por_categoria = Saidas.objects.filter(owner=request.user, date__year=ano, date__month=mes).values("descricao").annotate(total=Sum("valor"))

    context = {
        "ano": ano,
        "mes": mes,
        "meses_rotulos": json.dumps(meses_rotulos),
        "saldo_positivo": json.dumps(saldo_positivo),
        "saldo_negativo": json.dumps(saldo_negativo),
        "saldo_liquido": json.dumps(saldo_liquido),
        "entradas": float(entradas),
        "saidas": float(saidas),
        "saidas_por_categoria": saidas_por_categoria,
    }
    return render(request, "app1/html/dashboard.html", context)

@login_required
def exportar_csv(request):
    #aq esta lendo o banco
    entradas = Entradas.objects.filter(owner=request.user).order_by('date')
    saidas = Saidas.objects.filter(owner=request.user).order_by('date')
    saldos = Saldo.objects.filter(owner=request.user).order_by('data')


    transacoes = []
    # aq esta juntando as entradas e saidas em uma unica lista em forma de dicionario
    for e in entradas:
        transacoes.append({
            'tipo': 'Entrada',
            'descricao': e.descricao,
            'valor': e.valor,
            'data': e.date,
        })
    # faz o mesmo para as saidas
    for s in saidas:
        transacoes.append({
            'tipo': 'Saída',
            'descricao': s.descricao,
            'valor': -s.valor,  
            'data': s.date,
        })

    
    transacoes.sort(key=lambda t: t['data'])#ordena pela data

    def get_saldo_por_data(data_transacao):# vai checar se tem um saldo para cada transacao pela data 
        saldo_registros = saldos.filter(data__lte=data_transacao).order_by('-data')
        if saldo_registros.exists():
            return saldo_registros.first().valor
        return None  

    response = HttpResponse(content_type='text/csv')# criando o arquivo csv
    response['Content-Disposition'] = 'attachment; filename="extrato.csv"'# nome do arquivo

    writer = csv.writer(response) # criando o escritor do csv
    writer.writerow(['Tipo', 'Descrição', 'Valor', 'Data', 'Saldo'])#escreve na primeira linha isso

   # escreve linha por linha no csv, pegando cada item pela chaave do dicionario
    for t in transacoes:
        saldo_valor = get_saldo_por_data(t['data'])
        writer.writerow([
            t['tipo'],
            t['descricao'],
            f"{t['valor']:.2f}",
            t['data'].strftime("%d/%m/%Y"),
            f"{saldo_valor:.2f}" if saldo_valor is not None else "-"
        ])

    return response

@login_required
def exportar_pdf(request):
    entradas=Entradas.objects.filter(owner=request.user).order_by('date')
    saidas=Saidas.objects.filter(owner=request.user).order_by('date')
    saldos=Saldo.objects.filter(owner=request.user).order_by('data')

    transacoes=[]
    for e in entradas:
        transacoes.append({
            'tipo': 'Entrada',
            'descricao': e.descricao,
            'valor': e.valor,
            'data': e.date,
        })
    for s in saidas:
        transacoes.append({
            'tipo': 'Saída',
            'descricao': s.descricao,
            'valor': -s.valor,  
            'data': s.date,
        })
    
    transacoes.sort(key=lambda t: t['data'])

    def get_saldo_por_data(data_transacao):# vai checar se tem um saldo para cada transacao pela data 
        saldo_registros = saldos.filter(data__lte=data_transacao).order_by('-data')
        if saldo_registros.exists():
            return saldo_registros.first().valor
        return None 
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="extrato.pdf"'
    
    #parte da logica que se distingue do csv
    # criando o pdf
    p = canvas.Canvas(response, pagesize=A4)
    largura, altura = A4
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(2*cm, altura - 2*cm, "Extrato Financeiro")
    p.setFont("Helvetica", 12)
    p.drawString(2*cm, altura - 2.7*cm, f"Usuário: {request.user.username}")

    y = altura - 4*cm
    p.setFont("Helvetica-Bold", 11)
    p.drawString(2*cm, y, "Tipo")
    p.drawString(5*cm, y, "Descrição")
    p.drawString(11*cm, y, "Valor (R$)")
    p.drawString(15*cm, y, "Data")
    p.drawString(18*cm, y, "Saldo")
    y -= 0.5*cm
    p.line(2*cm, y, 20*cm, y)
    y -= 0.5*cm
    p.setFont("Helvetica", 10)
    for t in transacoes:
        saldo_valor = get_saldo_por_data(t['data'])
        
        if y < 3*cm:
            p.showPage()
            y = altura - 3*cm
            p.setFont("Helvetica", 10)

        p.drawString(2*cm, y, t['tipo'])
        p.drawString(5*cm, y, str(t['descricao'])[:30])
        p.drawRightString(13.5*cm, y, f"{t['valor']:.2f}")
        p.drawString(15*cm, y, t['data'].strftime("%d/%m/%Y"))
        p.drawRightString(20*cm, y, f"{saldo_valor:.2f}" if saldo_valor is not None else "-")
        y -= 0.6*cm

    p.setFont("Helvetica-Oblique", 9)
    p.drawString(2*cm, 1.5*cm, "Gerado automaticamente pelo sistema.")
    p.showPage()
    p.save()

    return response
