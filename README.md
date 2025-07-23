# API FastAPI com Cache Redis

Este projeto implementa uma API FastAPI para gerenciamento de livros com cache utilizando Redis. A API inclui endpoints para listar e adicionar livros, com caching para otimizar a performance do endpoint de listagem.

## Pré-requisitos

- Python 3.8+
- Redis instalado localmente ou via Docker
- Bibliotecas Python: `fastapi`, `uvicorn`, `redis`, `pydantic`

## Configuração do Ambiente

### 1. Instalar Dependências Python

Crie um ambiente virtual e instale as dependências:

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install fastapi uvicorn redis pydantic
```
# livros-api
