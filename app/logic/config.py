"""Configurações do jogador inteligente."""

# Estratégia ativa: "random", "heuristic", "minimax" ou "rl"
ACTIVE_STRATEGY = "minimax"

# Configurações do Minimax
MINIMAX_DEPTH = 4
MINIMAX_TIME_LIMIT_SECONDS = 3.5  # margem antes dos 5s da API

# Times
TEAM_TURING_PROFESSORS = ["CLARO", "REY"]
TEAM_LOVELACE_PROFESSORS = ["KARIN", "BEATRIZ"]

# Tabuleiro
WINNING_LEVEL = 4   # ao chegar em célula nível 4, professor vence
MAX_LEVEL = 4
