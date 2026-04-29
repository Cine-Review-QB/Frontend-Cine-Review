# Frontend-Cine-Review

Frontend da plataforma **CineReviews** — uma aplicação web estilo Letterboxd / Stremio onde usuários descobrem filmes, escrevem reviews, seguem outros usuários e acompanham um ranking semanal.

Construído com [Reflex](https://reflex.dev/) (framework full-stack em Python que compila para Next.js + FastAPI) e TailwindV4.

> **Status:** projeto recém-iniciado. Atualmente exibe apenas a página de boas-vindas padrão do Reflex. Páginas e estado de domínio ainda serão implementados.

---

## Sumário

- [Arquitetura](#arquitetura)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Executando](#executando)
- [Build de produção](#build-de-produção)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Integração com o backend](#integração-com-o-backend)
- [Roadmap](#roadmap)

---

## Arquitetura

Este frontend é um dos componentes da plataforma CineReviews, que segue arquitetura de microsserviços:

```
   ┌──────────────────┐
   │  Frontend Reflex │ ◀── você está aqui
   └────────┬─────────┘
            │ HTTPS + Bearer JWT
            ▼
   ┌──────────────────┐
   │   API Gateway    │  (Cine-Api-Gateway · Go)
   └────────┬─────────┘
            │
   ┌────────┼────────────┬───────────────┐
   ▼        ▼            ▼               ▼
 Auth   Content        Review         Auth0
(Java) (Python/Flask) (Python)      (externo)
```

O frontend **nunca chama serviços de domínio diretamente** — toda requisição passa pelo Gateway, que cuida de autenticação JWT, rate limiting e roteamento.

---

## Requisitos

- **Python 3.10+**
- **Node/Bun** — instalados automaticamente pelo Reflex na primeira execução de `reflex init`
- (Opcional) [`uv`](https://docs.astral.sh/uv/) para gerenciar dependências

---

## Instalação

```bash
# Clone o repositório
git clone https://github.com/Cine-Review-QB/Frontend-Cine-Review.git
cd Frontend-Cine-Review

# Opção A — uv (recomendado)
uv sync

# Opção B — pip + venv
python -m venv .venv
source .venv/bin/activate         # Linux/macOS
# .venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Inicializa o projeto Reflex (apenas na primeira vez — baixa Bun e cria .web/)
uv run reflex init
```

---

## Executando

```bash
# Modo dev (frontend :3000 + backend interno :8000)
uv run reflex run
```

Abra http://localhost:3000 no navegador.

Outras opções úteis:

```bash
uv run reflex run --frontend-only       # apenas o front
uv run reflex run --backend-only        # apenas o backend Reflex
uv run reflex run --loglevel debug      # logs detalhados
```

---

## Build de produção

```bash
uv run reflex export
```

O Reflex gera um build estático otimizado em `.web/_static/` (frontend) e empacota o backend Python para deploy.

---

## Estrutura do projeto

```
Frontend-Cine-Review/
├── rxconfig.py                  # configuração global do Reflex
├── cine_review/                 # pacote Python da aplicação
│   ├── __init__.py
│   └── cine_review.py           # State, páginas e instância `app = rx.App()`
├── assets/                      # arquivos estáticos (favicon, imagens, ...)
├── pyproject.toml
├── requirements.txt
├── uv.lock
└── README.md
```

### Plugins ativos (`rxconfig.py`)

- `SitemapPlugin` — gera `sitemap.xml` automaticamente.
- `TailwindV4Plugin` — habilita Tailwind v4 nos componentes.

---

## Integração com o backend

| Serviço              | Rota pública (via Gateway) | Função                                    |
|----------------------|-----------------------------|-------------------------------------------|
| `Cine-Users`         | `/auth/*`                  | perfil do usuário, sincronia com Auth0    |
| `Cine-Content`       | `/movies/*`                | catálogo de filmes                        |
| `Cine-Review`        | `/reviews/*`               | reviews, follows, likes, ranking semanal  |

A URL base do Gateway deve ser configurável por ambiente (ex.: `http://localhost:8000` em dev, URL de produção quando deployado).

Padrão sugerido para chamadas — sempre dentro de event handlers do `State`:

```python
import httpx, reflex as rx

class State(rx.State):
    movies: list[dict] = []

    async def load_movies(self):
        async with httpx.AsyncClient() as client:
            r = await client.get("http://localhost:8000/movies/")
            self.movies = r.json().get("movies", [])
```

---

## Roadmap

- [ ] Página inicial com lista paginada de filmes (consome `Cine-Content`)
- [ ] Detalhes do filme + reviews associadas
- [ ] Login via Auth0 (OAuth2 Authorization Code)
- [ ] Perfil do usuário e escrita/edição de review
- [ ] Feed social (follows + likes)
- [ ] Ranking semanal de filmes mais bem avaliados
- [ ] Tema escuro/claro com Tailwind
- [ ] Deploy do frontend (Vercel) e backend Reflex (AWS EC2)

---

## Referências

- [Reflex — documentação oficial](https://reflex.dev/docs/getting-started/introduction/)
- [TailwindV4 plugin do Reflex](https://reflex.dev/docs/styling/tailwind/)
