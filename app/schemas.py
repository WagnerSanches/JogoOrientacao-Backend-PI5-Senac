"""DTOs (Data Transfer Objects) da aplicação."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


# ===== Enums =====

class TurnPhase(str, Enum):
    """Fase atual do turno enviado pelo orquestrador."""
    SETUP_PLACEMENT = "setup_placement"
    PLAYER_TURN = "player_turn"


class TeamID(int, Enum):
    """Identificador do time."""
    TURING = 1
    LOVELACE = 2


# ===== Modelos base =====

class Cell(BaseModel):
    """Representa uma célula do tabuleiro.

    - level: nível do aluno (0=calouro, 1=1º ano, 2=2º ano, 3=3º ano, 4=pronto)
    - professor: nome do professor ocupando a célula, ou None se vazia
    """
    level: int = Field(
        ge=0,
        le=4,
        description="Nível do aluno (0 a 4)"
    )
    professor: Optional[str] = Field(
        default=None,
        description="Nome do professor (CLARO, REY, KARIN, BEATRIZ) ou None"
    )


class Position(BaseModel):
    """Coordenada (linha, coluna) no tabuleiro."""
    row: int = Field(ge=0, description="Índice da linha")
    col: int = Field(ge=0, description="Índice da coluna")


# ===== Payload recebido do orquestrador =====

class AITurnRequest(BaseModel):
    """Payload enviado pelo orquestrador de partidas ao endpoint /move.

    Contém todo o estado necessário para o jogador decidir sua jogada.
    """
    game_id: str = Field(description="UUID da partida")
    turn_number: int = Field(ge=1, description="Número do turno atual")
    turn_phase: TurnPhase = Field(description="Fase do turno atual")
    your_team: TeamID = Field(description="Time do jogador inteligente (1 ou 2)")
    professor_to_place: Optional[str] = Field(
        default=None,
        description="Professor a posicionar (somente na fase setup_placement)"
    )
    board: List[List[Cell]] = Field(description="Matriz do tabuleiro")


# ===== Respostas (jogadas) =====

class SetupResponse(BaseModel):
    """Resposta na fase de posicionamento de professores."""
    row: int = Field(ge=0, description="Linha onde posicionar o professor")
    col: int = Field(ge=0, description="Coluna onde posicionar o professor")


class PlayerTurnResponse(BaseModel):
    """Resposta na fase de turno do jogador.

    - professor: nome do professor que será movido
    - move_to: posição de destino do professor
    - mentor_at: posição onde aumentar o nível do aluno (omitido em jogada de vitória)
    """
    professor: str = Field(description="Nome do professor a ser movido")
    move_to: Position = Field(description="Posição de destino do professor")
    mentor_at: Optional[Position] = Field(
        default=None,
        description="Posição do aluno a ser orientado (None em jogada de vitória)"
    )
