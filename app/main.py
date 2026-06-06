from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Jogador Inteligente PI5",
    description="API do jogador inteligente para o Jogo da Orientação",
    version="0.1.0",
)

# CORS liberado para facilitar testes locais
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Endpoint de saúde — verifica se a API está rodando."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
    }
