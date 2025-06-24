from dados import movimentacoes, salvar_dados

def adicionar_movimentacao(tipo, valor, descricao, data, categoria):
    movimentacoes.append({
        "tipo": tipo,
        "valor": valor,
        "descricao": descricao,
        "data": data,
        "categoria": categoria
    })
    salvar_dados()
