import plotly.graph_objs as go
from collections import defaultdict
from dados import movimentacoes

def grafico_despesas_por_categoria():
    categorias = defaultdict(float)
    for m in movimentacoes:
        if m["tipo"] == "despesa":
            categorias[m["categoria"]] += m["valor"]
    data = [go.Bar(x=list(categorias.keys()), y=list(categorias.values()), marker_color='tomato')]
    layout = go.Layout(title="Despesas por Categoria")
    return {"data": data, "layout": layout}

def grafico_receita_vs_despesa():
    total_receita = sum(m["valor"] for m in movimentacoes if m["tipo"] == "receita")
    total_despesa = sum(m["valor"] for m in movimentacoes if m["tipo"] == "despesa")
    data = [go.Pie(labels=["Receita", "Despesa"], values=[total_receita, total_despesa], marker_colors=["green", "red"])]
    layout = go.Layout(title="Receita vs Despesa")
    return {"data": data, "layout": layout}
