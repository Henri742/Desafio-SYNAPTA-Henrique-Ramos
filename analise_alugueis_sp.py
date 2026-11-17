"""
Desafio Inicial SYNAPTA 2026 - Análise de Preços de Aluguel em São Paulo
Autor: Henrique Leandro Ramos Silva
Curso: Ciência da Computação - UNINASSAU Maceió
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

def carregar_e_auditar_dados(caminho_csv='data.csv'):
    if not os.path.exists(caminho_csv) and os.path.exists(os.path.join('data', 'data.csv')):
        caminho_csv = os.path.join('data', 'data.csv')
    df_raw = pd.read_csv(caminho_csv)
    print("=== 1. AUDITORIA DA BASE BRUTA ===")
    print(f"Quantidade de linhas: {df_raw.shape[0]} | Quantidade de colunas: {df_raw.shape[1]}")
    print("Valores ausentes por coluna:\n", df_raw.isnull().sum())
    print(f"Registros exatamente duplicados: {df_raw.duplicated().sum()}")
    return df_raw

def limpar_e_enriquecer_dados(df_raw):
    # Regra 1: Remover imóveis com área menor que 10 m² (inclui 2 imóveis com 0 m² e 5 imóveis entre 1 e 5 m²)
    # Regra 2: Remover imóveis com 0 quartos quando NÃO são do tipo 'Studio e kitnet' (7 apartamentos e 4 casas)
    mask_valida = (df_raw['area'] >= 10) & ~((df_raw['bedrooms'] == 0) & (df_raw['type'] != 'Studio e kitnet'))
    df = df_raw[mask_valida].copy()

    # Engenharia de atributos para aprofundar a análise
    df['encargos'] = df['total'] - df['rent']
    df['peso_encargos_pct'] = (df['encargos'] / df['rent']) * 100
    df['preco_m2'] = df['rent'] / df['area']

    print("\n=== 2. RESUMO DA LIMPEZA E PREPARAÇÃO ===")
    print(f"Registros originais: {len(df_raw)}")
    print(f"Registros removidos por inconsistência física/cadastral: {len(df_raw) - len(df)}")
    print(f"Registros válidos na base limpa: {len(df)}")
    return df

def exibir_estatisticas(df_raw, df):
    print("\n=== 3. MÉDIA E MEDIANA DOS ALUGUÉIS ===")
    print(f"[Base Bruta]  Média: R$ {df_raw['rent'].mean():,.2f} | Mediana: R$ {df_raw['rent'].median():,.2f}")
    print(f"[Base Limpa]  Média: R$ {df['rent'].mean():,.2f} | Mediana: R$ {df['rent'].median():,.2f}")
    print(f"[Custo Total] Média: R$ {df['total'].mean():,.2f} | Mediana: R$ {df['total'].median():,.2f}")

    # Bairros com quantidade razoável de registros (mínimo de 30 anúncios)
    bairros = df.groupby('district').agg(
        qtd=('rent', 'count'),
        media_aluguel=('rent', 'mean'),
        mediana_aluguel=('rent', 'median'),
        mediana_m2=('preco_m2', 'median'),
        mediana_area=('area', 'median')
    ).query('qtd >= 30')

    print("\n=== 4. TOP 10 BAIRROS COM MAIORES PREÇOS MÉDIOS (n >= 30) ===")
    print(bairros.sort_values('media_aluguel', ascending=False).head(10).round(2))

    print("\n=== 5. TOP 10 BAIRROS COM MENORES PREÇOS MÉDIOS (n >= 30) ===")
    print(bairros.sort_values('media_aluguel', ascending=True).head(10).round(2))

    print("\n=== 6. COMPARAÇÃO POR TIPO DE IMÓVEL ===")
    print(df.groupby('type')[['area', 'rent', 'total', 'encargos', 'preco_m2']].median().round(2))

if __name__ == '__main__':
    df_bruto = carregar_e_auditar_dados()
    df_limpo = limpar_e_enriquecer_dados(df_bruto)
    exibir_estatisticas(df_bruto, df_limpo)
