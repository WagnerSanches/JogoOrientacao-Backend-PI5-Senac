# Jogador Inteligente — PI5 Senac

Backend do jogador inteligente para o **Jogo da Orientação** do Projeto Integrador 5 do Senac.

**Autor:** Wagner Sanches — Análise e Desenvolvimento de Sistemas  
**API:** https://pi5-api-production.up.railway.app

---

## Como o jogador funciona

A IA usa **Reinforcement Learning** com o algoritmo **PPO (Proximal Policy Optimization)** para aprender a jogar. O modelo foi treinado em milhões de partidas simuladas localmente, sem consumir a API do professor.

### Por que RL?

O Jogo da Orientação é um jogo de tabuleiro com decisões sequenciais. Reinforcement Learning é a técnica ideal para esse tipo de problema: o agente aprende sozinho, jogando, sem precisar de heurísticas escritas manualmente.

---

## Arquitetura

```
.
├── app/                        # Codigo de producao (API)
│   ├── main.py                 # Endpoints /health e /move
│   ├── schemas.py              # DTOs (Pydantic)
│   └── logic/
│       ├── config.py           # Estrategia ativa (rl, heuristic, random)
│       ├── rules.py            # Regras do jogo
│       └── strategies/
│           ├── random_bot.py   # Bot aleatorio
│           ├── heuristic.py    # Heuristica (fallback)
│           ├── minimax.py      # Minimax (placeholder)
│           └── rl.py           # Estrategia RL (em uso)
│
└── training/                   # Codigo de treinamento (offline)
    ├── game/                   # Simulador local do jogo
    ├── envs/                   # Ambiente Gymnasium + recompensas
    └── train/                  # Scripts de treino
```

---

## Estratégia de IA — detalhes técnicos

### Algoritmo: MaskablePPO

Variante do PPO que suporta **action masking** — o modelo só considera jogadas válidas em cada turno. Isso acelera muito o aprendizado porque o agente não desperdiça tempo tentando jogadas ilegais.

### Estrutura da rede neural

**Entrada:** tensor `5×5×9` (tabuleiro codificado)

| Canal | Significado |
|-------|-------------|
| 0 | Nível de cada célula (normalizado 0–1) |
| 1–4 | Posição one-hot de cada professor (CLARO, REY, KARIN, BEATRIZ) |
| 5 | Células vazias |
| 6 | Meus professores |
| 7 | Fase do jogo |
| 8 | Meu time |

**Rede:** MLP `[256, 256]`  
**Saída:** 2625 ações possíveis (25 setup + 2600 turn)

### Função de recompensa

| Evento | Recompensa |
|--------|-----------|
| Vitória | +10 |
| Derrota | −10 |
| Empate | −1 |
| Subir nível de aluno | +0.1 |
| Criar nível 3 (próximo da vitória) | +0.3 |
| Criar nível 4 seguro (só meu time alcança) | +0.5 |
| Criar nível 4 perigoso (adversário alcança) | −0.8 |
| Bloquear vitória do adversário | +0.4 |
| Alternar entre professores | +0.5 |
| Insistir no mesmo professor | −0.5 |
| Professor parado por muitos turnos | −0.2/turno |
| Por turno (incentiva ganhar rápido) | −0.01 |

A penalidade por insistir no mesmo professor foi crucial: sem ela o modelo aprendia a focar apenas em um dos dois professores do time, o que funciona contra bots aleatórios mas falha contra adversários competentes.

### Treinamento

**Fase 1 — Contra bot aleatório (~1.5M timesteps)**
- Objetivo: aprender regras básicas e estratégias iniciais
- Resultado: 89–96% de win rate

**Fase 2 — Self-play (~2–3M timesteps adicionais)**
- O modelo joga contra versões anteriores de si mesmo
- Mantém um pool de gerações para evitar *catastrophic forgetting*
- Resultado: gerações novas vencem gerações antigas em 70–96%

Hardware usado: Intel i5, 16 GB RAM, sem GPU. Cada milhão de timesteps levou ~2 horas.

---

## Endpoints da API

### `GET /health`

Verifica se a API está rodando.

```json
{
  "status": "ok",
  "timestamp": "2026-06-10T12:00:00"
}
```

### `POST /move`

Endpoint chamado pelo orquestrador de partidas. Recebe o estado do turno e retorna a jogada.

**Request — fase setup:**
```json
{
  "game_id": "...",
  "turn_number": 1,
  "turn_phase": "setup_placement",
  "your_team": 1,
  "professor_to_place": "CLARO",
  "board": [[]]
}
```

**Response:**
```json
{ "row": 2, "col": 2 }
```

**Request — fase turn:**
```json
{
  "game_id": "...",
  "turn_number": 5,
  "turn_phase": "player_turn",
  "your_team": 1,
  "board": [[]]
}
```

**Response:**
```json
{
  "professor": "CLARO",
  "move_to": { "row": 1, "col": 2 },
  "mentor_at": { "row": 2, "col": 3 }
}
```

---

## Como rodar localmente

**Requisitos:** Python 3.12+

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

pip install -r requirements.txt
```

**Rodar a API:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

Acesse o Swagger: http://localhost:8001/docs

**Treinar o modelo:**
```bash
pip install -r training/requirements.txt

# Treino contra bot aleatorio
python -m training.train.train_vs_random --timesteps 1500000

# Self-play (apos modelo basico estar pronto)
python -m training.train.train_self_play \
  --base training/models/ppo_vs_random_final.zip \
  --timesteps 2000000 \
  --promote-every 500000
```

**Avaliar o modelo:**
```bash
python -m training.train.evaluate --episodes 200
```

**Acompanhar métricas em tempo real:**
```bash
tensorboard --logdir training/logs
```

---

## Trocar de estratégia

A estratégia ativa é controlada em `app/logic/config.py`:

```python
ACTIVE_STRATEGY = "rl"  # opcoes: "random", "heuristic", "minimax", "rl"
```

Se o modelo RL falhar ao carregar, a API usa automaticamente a `heuristic` como fallback.

---

## Stack

| Componente | Tecnologia |
|------------|-----------|
| Linguagem | Python 3.12 |
| Framework Web | FastAPI |
| ML | Stable Baselines 3 + sb3-contrib (MaskablePPO) |
| Ambiente RL | Gymnasium |
| Deploy | Railway |

---

## Resultados

| Métrica | Valor |
|---------|-------|
| Win rate vs Random Bot | ~89–96% |
| Tempo de resposta | < 200 ms |
| Treinamento total | ~10 horas |
| Timesteps totais | ~5M |

---

## Limitações conhecidas

- Em algumas partidas o modelo prefere usar um professor mais que o outro
- Estratégia é principalmente ofensiva (foca em vencer rápido)
- Foi treinado contra bot aleatório + self-play, não contra adversários humanos
