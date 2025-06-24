import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from movimentacoes import adicionar_movimentacao, movimentacoes, salvar_dados
from graficos import grafico_despesas_por_categoria, grafico_receita_vs_despesa
import json

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
app.title = "Calculadora Financeira"

# Função para montar tabela estilizada com botão excluir
def montar_tabela():
    if not movimentacoes:
        return html.P("Nenhuma movimentação cadastrada.", className="text-muted")

    linhas = []
    for i, m in enumerate(movimentacoes[::-1]):
        linhas.append(
            dbc.Row(
                [
                    dbc.Col(m["data"], xs=4, md=2),
                    dbc.Col(m["tipo"].capitalize(), xs=4, md=1),
                    dbc.Col(f"R$ {m['valor']:.2f}", xs=4, md=2),
                    dbc.Col(m["descricao"], xs=6, md=4),
                    dbc.Col(m["categoria"], xs=4, md=2),
                    dbc.Col(
                        dbc.Button("Excluir", color="danger", size="sm", id={"type": "btn-excluir", "index": len(movimentacoes) - 1 - i}),
                        xs=2, md=1,
                    ),
                ],
                className="align-items-center py-1 border-bottom",
            )
        )

    return dbc.Container(
        [dbc.Row([
            dbc.Col(html.Strong("Data"), xs=4, md=2),
            dbc.Col(html.Strong("Tipo"), xs=4, md=1),
            dbc.Col(html.Strong("Valor"), xs=4, md=2),
            dbc.Col(html.Strong("Descrição"), xs=6, md=4),
            dbc.Col(html.Strong("Categoria"), xs=4, md=2),
            dbc.Col(html.Strong(""), xs=2, md=1),
        ], className="border-bottom bg-light py-2")] + linhas,
        fluid=True,
        style={"maxHeight": "350px", "overflowY": "auto", "border": "1px solid #ddd", "borderRadius": "5px"}
    )

app.layout = dbc.Container([
    html.H2("📊 Calculadora Financeira", className="text-center my-4 text-primary"),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader(html.H4("➕ Adicionar Movimentação", className="text-primary")),
                dbc.CardBody([
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Tipo"),
                                dcc.Dropdown(
                                    id="tipo-input",
                                    options=[
                                        {"label": "Receita", "value": "receita"},
                                        {"label": "Despesa", "value": "despesa"}
                                    ],
                                    value="receita",
                                    clearable=False,
                                )
                            ], xs=12, md=4),
                            dbc.Col([
                                dbc.Label("Valor (R$)"),
                                dbc.Input(id="valor-input", type="number", min=0, step=0.01, placeholder="Ex: 1000.00"),
                            ], xs=12, md=4),
                            dbc.Col([
                                dbc.Label("Data (DD/MM/AAAA)"),
                                dbc.Input(id="data-input", type="text", placeholder="Ex: 22/06/2025"),
                            ], xs=12, md=4),
                        ], className="mb-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Descrição"),
                                dbc.Input(id="descricao-input", type="text", placeholder="Ex: Salário"),
                            ], xs=12, md=6),
                            dbc.Col([
                                dbc.Label("Categoria"),
                                dbc.Input(id="categoria-input", type="text", placeholder="Ex: Trabalho"),
                            ], xs=12, md=6),
                        ], className="mb-3"),
                        dbc.Button("Adicionar", id="botao-adicionar", color="primary", className="w-100 py-2"),
                    ]),
                    html.Div(id="mensagem-adicionar", className="mt-3"),
                ])
            ]),
            xs=12, md=4
        ),

        dbc.Col([
            html.H4("📋 Movimentações", className="text-secondary"),
            html.Div(id="lista-movimentacoes", className="mt-3", style={"overflowX": "auto"}),
        ], xs=12, md=8),
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col(dcc.Graph(id="grafico-despesas", config={"responsive": True}), xs=12, md=6),
        dbc.Col(dcc.Graph(id="grafico-receita-vs-despesa", config={"responsive": True}), xs=12, md=6),
    ]),
], fluid=True)

# Callback principal: adicionar e excluir movimentações
@app.callback(
    Output("mensagem-adicionar", "children"),
    Output("lista-movimentacoes", "children"),
    Output("grafico-despesas", "figure"),
    Output("grafico-receita-vs-despesa", "figure"),
    Input("botao-adicionar", "n_clicks"),
    Input({"type": "btn-excluir", "index": dash.ALL}, "n_clicks"),
    State("tipo-input", "value"),
    State("valor-input", "value"),
    State("descricao-input", "value"),
    State("data-input", "value"),
    State("categoria-input", "value"),
)
def atualizar_tudo(n_clicks_adicionar, n_clicks_excluir_list, tipo, valor, descricao, data, categoria):
    ctx = callback_context
    if not ctx.triggered:
        return "", montar_tabela(), grafico_despesas_por_categoria(), grafico_receita_vs_despesa()

    botao_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Botão adicionar
    if botao_id == "botao-adicionar":
        if not all([tipo, valor, descricao, data, categoria]):
            return dbc.Alert("Por favor, preencha todos os campos.", color="warning"), montar_tabela(), grafico_despesas_por_categoria(), grafico_receita_vs_despesa()
        try:
            valor_float = float(valor)
        except ValueError:
            return dbc.Alert("Valor inválido.", color="danger"), montar_tabela(), grafico_despesas_por_categoria(), grafico_receita_vs_despesa()

        adicionar_movimentacao(tipo, valor_float, descricao, data, categoria)
        return dbc.Alert("Movimentação adicionada com sucesso!", color="success"), montar_tabela(), grafico_despesas_por_categoria(), grafico_receita_vs_despesa()

    # Botão excluir
    try:
        botao_id_dict = json.loads(botao_id)
        if botao_id_dict.get("type") == "btn-excluir":
            idx = botao_id_dict.get("index")
            if 0 <= idx < len(movimentacoes):
                movimentacoes.pop(idx)
                salvar_dados()
            return "", montar_tabela(), grafico_despesas_por_categoria(), grafico_receita_vs_despesa()
    except Exception:
        pass

    raise dash.exceptions.PreventUpdate

if __name__ == "__main__":
    print("Rodando o app na porta 8050...")
    app.run(debug=True)
