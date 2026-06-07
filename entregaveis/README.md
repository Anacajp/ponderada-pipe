# Tutorial de reproducao do experimento

Este diretorio e o centro da entrega para correcao. Ele guarda o relatorio,
os dados coletados e os graficos gerados a partir das execucoes reais do GitHub
Actions.

## O que precisa estar configurado no GitHub

1. O repositorio precisa estar publico em `https://github.com/Anacajp/ponderada-pipe`.
2. A aba **Actions** precisa estar habilitada. Em repositorio publico, normalmente
   ela aparece automaticamente quando o arquivo YAML entra na branch `main`.
3. Para coletar metricas pela API, instale o GitHub CLI e rode uma vez:

```bash
gh auth login
```

Escolha GitHub.com, HTTPS e login pelo navegador. Isso e so para autorizar o
script a ler as execucoes do Actions. Nao e para copiar dados manualmente.

## Como gerar as 12 execucoes reais

Depois que a branch com a pipeline estiver mergeada e enviada para o GitHub,
faca uma execucao por cenario. A cada cenario, o script muda
`experiment/scenario.json`, cria um commit padronizado e voce envia esse commit.
Cada `git push` gera uma execucao real na aba Actions.

```bash
git switch main
git pull origin main

python scripts/prepare_experiment.py list

python scripts/prepare_experiment.py apply 01 --commit
git push origin main

python scripts/prepare_experiment.py apply 02 --commit
git push origin main

# repita ate o cenario 12
```

Importante: o cenario 11 foi feito para falhar de proposito. Isso e esperado e
serve como evidencia de pipeline vermelha. O cenario 12 volta para verde.

## Como coletar metricas

Quando as 12 execucoes aparecerem na aba Actions, rode:

```bash
python scripts/collect_metrics.py --repo Anacajp/ponderada-pipe --workflow eventops-ci.yml --limit 12
```

Esse comando gera:

- `entregaveis/dados/pipeline_metrics.csv`
- `entregaveis/dados/workflow_runs.json`

O CSV e a base estruturada exigida pela atividade. O JSON ajuda a montar a
tabela de evidencias no relatorio, com links e IDs reais.

## Como gerar os graficos

Depois de coletar as metricas:

```bash
python scripts/generate_charts.py
```

Os graficos saem em `entregaveis/graficos/`:

- `01_tempo_total_pipeline.png`
- `02_tempo_medio_por_job.png`
- `03_sucesso_vs_falha.png`
- `04_testes_vs_duracao.png`

## Links para entregar na Adalove

- Repositorio: `https://github.com/Anacajp/ponderada-pipe`
- YAML: `https://github.com/Anacajp/ponderada-pipe/blob/main/.github/workflows/eventops-ci.yml`
- Relatorio: `https://github.com/Anacajp/ponderada-pipe/blob/main/entregaveis/RELATORIO.md`

## Como explicar para o professor

Este projeto nao mede apenas se "passou ou falhou". Ele compara execucoes com
cache frio/quente, aumento de testes, teste lento, falha controlada, modo
sequencial e modo paralelo. O objetivo e entender onde a pipeline demora, onde
ela falha e se o feedback para quem desenvolve e rapido o suficiente.
