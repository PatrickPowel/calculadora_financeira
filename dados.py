import csv
import os

movimentacoes = []

def salvar_dados():
    with open("movimentacoes.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["tipo", "valor", "descricao", "data", "categoria"])
        for m in movimentacoes:
            writer.writerow([m["tipo"], m["valor"], m["descricao"], m["data"], m["categoria"]])

def carregar_dados():
    if not os.path.exists("movimentacoes.csv"):
        return
    with open("movimentacoes.csv", "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for linha in reader:
            movimentacoes.append({
                "tipo": linha["tipo"],
                "valor": float(linha["valor"]),
                "descricao": linha["descricao"],
                "data": linha["data"],
                "categoria": linha["categoria"]
            })
