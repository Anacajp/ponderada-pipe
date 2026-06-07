# EventOps Campus

EventOps Campus e um mini sistema em Python para planejar eventos academicos em
salas do campus. Ele valida agendas, detecta conflitos e sugere ajustes de sala
ou horario.

O projeto foi criado como base para uma atividade de CI/CD com GitHub Actions. A
parte mais importante da entrega sera a pipeline instrumentada, as metricas reais
coletadas e o relatorio tecnico em `entregaveis/`.

## Salas do campus

O catalogo fixo contem as salas `A01` ate `A13`, alem de `Auditorio` e
`Multiuso`. No codigo, `Auditorio` usa grafia sem acento para evitar problemas
de encoding em terminais e artefatos de CI.

## Comandos principais

```bash
python -m eventops rooms
python -m eventops validate data/sample_schedule.json
python -m eventops schedule data/sample_schedule.json
```

## Desenvolvimento local

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
ruff check .
pytest
```

## O que o sistema valida

- dois eventos na mesma sala e no mesmo horario;
- sala pequena demais para o publico esperado;
- sala sem recurso necessario;
- intervalo curto demais entre eventos na mesma sala;
- sugestao de sala alternativa ou proximo horario livre.
