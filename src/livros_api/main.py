from fastapi import FastAPI, HTTPException
import redis
import json
from typing import List, Dict
from pydantic import BaseModel
import asyncio

# Inicializa a aplicação FastAPI
app = FastAPI()

# Lista em memória simulando um banco de dados de livros
books_db = [
    {"id": 1, "title": "O Senhor dos Anéis", "author": "J.R.R. Tolkien"},
    {"id": 2, "title": "1984", "author": "George Orwell"}
]

# Configuração da conexão com o Redis
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True  # Decodifica respostas automaticamente para strings
)

# Modelo Pydantic para validação de dados de livros
class Book(BaseModel):
    id: int
    title: str
    author: str

# Chave do cache no Redis e tempo de expiração (TTL)
BOOKS_CACHE_KEY = "livros"
CACHE_TTL = 300  # 5 minutos de TTL

async def salvar_livros_redis(books: List[Dict]) -> None:
    """
    Salva a lista de livros no Redis com um tempo de expiração (TTL).
    Args:
        books: Lista de dicionários contendo os dados dos livros.
    """
    try:
        # Converte a lista de livros para JSON
        books_json = json.dumps(books)
        # Salva no Redis com TTL
        redis_client.setex(BOOKS_CACHE_KEY, CACHE_TTL, books_json)
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Erro no Redis: {str(e)}")

async def deletar_livros_redis() -> None:
    """
    Remove a chave de livros do Redis.
    """
    try:
        redis_client.delete(BOOKS_CACHE_KEY)
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Erro no Redis: {str(e)}")

@app.get("/livros", response_model=List[Book])
async def get_livros():
    """
    Endpoint para listar livros. Verifica o cache no Redis antes de consultar o banco de dados.
    Se os dados estiverem no cache, retorna-os. Caso contrário, busca no banco, armazena no cache e retorna.
    """
    try:
        # Tenta obter os livros do cache
        cached_books = redis_client.get(BOOKS_CACHE_KEY)
        if cached_books:
            return json.loads(cached_books)  # Retorna dados do cache

        # Se não houver cache, busca do "banco de dados" (lista em memória)
        books = books_db
        # Salva no Redis para chamadas futuras
        await salvar_livros_redis(books)
        return books
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Erro no Redis: {str(e)}")

@app.post("/livros", response_model=Book)
async def add_livro(book: Book):
    """
    Endpoint para adicionar um livro. Atualiza o "banco de dados" e limpa o cache.
    """
    books_db.append(book.dict())
    await deletar_livros_redis()  # Limpa o cache após modificação
    return book