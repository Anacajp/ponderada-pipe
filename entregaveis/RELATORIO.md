# Relatorio tecnico: EventOps Campus CI/CD

> Este relatorio deve ser preenchido depois das 12 execucoes reais no GitHub
> Actions. Nao invente IDs, tempos ou prints: use o CSV e o JSON gerados pelos
> scripts em `entregaveis/dados/`.

## 1. Contexto do projeto

O EventOps Campus e um sistema Python para organizar eventos academicos em salas
do campus. Ele usa as salas A01 a A13, Auditorio e Multiuso, detectando conflitos
de horario, capacidade e recursos.

A pipeline foi criada para medir o comportamento real do CI/CD no GitHub
Actions, com variacoes controladas e coleta automatica de metricas.

## 2. Hipotese inicial

Hipoteses antes do experimento:

- o job de testes de carga deve ser o maior gargalo;
- a segunda execucao baseline deve ser mais rapida que a primeira por causa do cache;
- o modo paralelo deve reduzir o tempo total quando comparado ao modo sequencial;
- a falha controlada deve aparecer rapidamente no job de testes unitarios.

## 3. Execucoes reais

Preencher esta tabela apos rodar `scripts/collect_metrics.py`.

| Cenario | Run ID | Commit | Status | Link da execucao | Variacao |
| --- | --- | --- | --- | --- | --- |
| 01 | PREENCHER | PREENCHER | PREENCHER | PREENCHER | Baseline paralelo |
| 02 | PREENCHER | PREENCHER | PREENCHER | PREENCHER | Cache aquecido |
| 03 | PREENCHER | PREENCHER | PREENCHER | PREENCHER | Conflito de capacidade |
| 04 | PREENCHER | PREENCHER | PREENCHER | PREENCHER | Recurso ausente |
| 05 | PREENCHER | PREENCHER | PREENCHER | PREENCHER | Sobreposicao de horario |
| 06 | PREENCHER | PREENCHER | PREENCHER | PREENCHER | Mais testes sinteticos |
| 07 | PREENCHER | PREENCHER | PREENCHER | PREENCHER | Agenda media |
| 08 | PREENCHER | PREENCHER | PREENCHER | PREENCHER | Teste lento |
| 09 | PREENCHER | PREENCHER | PREENCHER | PREENCHER | Cache invalidado |
| 10 | PREENCHER | PREENCHER | PREENCHER | PREENCHER | Jobs sequenciais |
| 11 | PREENCHER | PREENCHER | failure | PREENCHER | Falha controlada |
| 12 | PREENCHER | PREENCHER | success | PREENCHER | Recuperacao verde |

## 4. Graficos

Inserir os graficos gerados em `entregaveis/graficos/`:

```md
![Tempo total](graficos/01_tempo_total_pipeline.png)
![Tempo por job](graficos/02_tempo_medio_por_job.png)
![Sucesso vs falha](graficos/03_sucesso_vs_falha.png)
![Testes vs duracao](graficos/04_testes_vs_duracao.png)
```

## 5. Analise das perguntas obrigatorias

### Qual etapa mais contribuiu para o tempo total do pipeline?

PREENCHER com base no grafico de tempo medio por job.

### Houve diferenca significativa entre execucoes com e sem cache?

Comparar os cenarios 01, 02 e 09.

### O paralelismo reduziu o tempo total? Em que condicoes?

Comparar os cenarios 10 e 12, que usam carga parecida.

### Quais falhas foram mais frequentes?

PREENCHER com base nos status e nos artefatos dos testes. A falha esperada e a
do cenario 11.

### O pipeline fornece feedback rapido o suficiente?

PREENCHER avaliando tempo total e tempo ate a falha controlada aparecer.

### Que melhorias poderiam ser feitas?

Possiveis melhorias: separar testes lentos para execucoes noturnas, publicar
sumario de testes no PR, reduzir instalacoes repetidas entre jobs ou ajustar
cache.

### Quais limitacoes existem nos dados coletados?

Possiveis limitacoes: poucas amostras, variacao natural dos runners hospedados
do GitHub, tempo de fila nao controlado e artefatos que podem expirar.

### Como essa analise apoia decisoes de engenharia?

Ela ajuda a decidir onde otimizar primeiro, quando paralelizar jobs, quando usar
cache e qual limite de tempo ainda oferece feedback util para quem desenvolve.

## 6. Resultados inesperados

Registrar pelo menos dois resultados inesperados depois de olhar os dados.

1. PREENCHER.
2. PREENCHER.

## 7. Comparacao entre hipotese e resultado observado

PREENCHER comparando a secao 2 com os dados reais.

## 8. Conclusao

PREENCHER com uma conclusao pratica sobre desempenho, estabilidade e gargalos da
pipeline.
