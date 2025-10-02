# Como Rodar a Aplicação

## Monopoly Simulator API

API REST que simula partidas de um jogo estilo Monopoly com 4 jogadores usando diferentes estratégias de compra.

---

## 🚀 Execução Rápida (Docker - Recomendado)

```bash
# 1. Iniciar a aplicação
docker-compose up --build

# 2. Acessar a API
# API: http://localhost:8000
# Documentação interativa: http://localhost:8000
```

**Parar a aplicação:**
```bash
docker-compose down
```

---

## 📦 Execução Local (sem Docker)

### Pré-requisitos
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager

### Instalação e Execução

```bash
# 1. Instalar dependências
uv sync
uv pip install -e .

# 2. Iniciar a aplicação
uv run start

# OU usar Make
make install
make run

# 3. Acessar a API
# API: http://localhost:8000
# Documentação interativa: http://localhost:8000
```

---

## 🎮 Como Usar a API

### 1. Verificar Health
```bash
curl http://localhost:8000/health
```

### 2. Simular Uma Partida
```bash
curl -X POST http://localhost:8000/game/simulate
```

**Resposta:**
```json
{
  "winner": "impulsive",
  "players": ["impulsive", "demanding", "cautious", "random"]
}
```

### 3. Executar Simulação em Lote (Estatísticas)
```bash
curl -X POST http://localhost:8000/game/stats \
  -H "Content-Type: application/json" \
  -d '{"num_simulations": 300}'
```

**Resposta:**
```json
{
  "total_simulations": 300,
  "timeouts": 12,
  "timeout_rate": 0.04,
  "avg_rounds": 345.2,
  "strategy_statistics": [
    {
      "strategy": "impulsive",
      "wins": 125,
      "win_rate": 0.42,
      "timeouts": 12,
      "avg_rounds_when_won": 287.5
    }
  ],
  "most_winning_strategy": "impulsive"
}
```

---

## 🧪 Testes

### Com Docker
```bash
docker-compose run --rm api pytest -v
```

### Sem Docker
```bash
# Rodar todos os testes
uv run pytest -v

# Rodar arquivo específico
uv run pytest tests/test_strategies.py

# Com cobertura
uv run pytest --cov=app --cov-report=html

# OU usar Make
make test
```

---

## 💻 Desenvolvimento

### Setup Rápido para Desenvolvedores

Se você está contribuindo ou desenvolvendo o projeto:

```bash
# Setup automatizado (recomendado)
./setup-dev.sh

# OU
make setup-dev
```

**O que isso faz:**
- Instala todas as dependências (incluindo ferramentas de dev)
- Configura pre-push hook para verificações de qualidade
- Formata o código inicial
- Roda verificações de qualidade

### Ferramentas de Qualidade de Código

#### Formatar Código (Black)
```bash
make format
# OU
uv run black app/ tests/
```

#### Verificar Linting (Flake8 + Pylint)
```bash
make lint
# OU
uv run flake8 app/ tests/
uv run pylint app/ --recursive=y
```

#### Verificar Tipos (MyPy)
```bash
make typecheck
# OU
uv run mypy app/
```

#### Rodar Tudo de Uma Vez
```bash
make quality
```

### Pre-push Hook

**Importante**: O pre-push hook roda automaticamente antes de cada `git push` e executa:
1. ✓ Formatação (Black)
2. ✓ Linting (Flake8 + Pylint)
3. ✓ Type checking (MyPy)
4. ✓ Testes (Pytest)

Se qualquer verificação falhar, o push é bloqueado. Isso garante que todo código enviado ao repositório tem qualidade.

---

## ⚙️ Configuração (Variáveis de Ambiente)

Você pode configurar a aplicação através de variáveis de ambiente com prefixo `MONOPOLY_`:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `MONOPOLY_DEBUG` | `false` | Modo debug (hot reload) |
| `MONOPOLY_LOG_LEVEL` | `WARNING` | Nível de log (DEBUG, INFO, WARNING, ERROR) |
| `MONOPOLY_API_HOST` | `0.0.0.0` | Host da API |
| `MONOPOLY_API_PORT` | `8000` | Porta da API |

**Exemplo Docker:**
```bash
# Edite docker-compose.yml e ajuste as variáveis de ambiente
```

**Exemplo Local:**
```bash
MONOPOLY_LOG_LEVEL=DEBUG uv run start
```

---

## 📋 Regras do Jogo

- **Tabuleiro**: 20 propriedades com custos (50-200) e aluguéis (10-100) aleatórios
- **Jogadores**: 4 jogadores começam com saldo de 300
- **Turnos**:
  - Rolar 1d6
  - Mover no sentido horário
  - Ao cair em propriedade → comprar (se livre) ou pagar aluguel (se ocupada)
  - Completar uma volta → ganhar salário de 100
- **Eliminação**: Saldo < 0 → jogador eliminado, propriedades liberadas
- **Vitória**: Último jogador restante OU maior saldo após 1000 rodadas

### Estratégias dos Jogadores

1. **Impulsivo**: Sempre compra quando possível
2. **Exigente**: Só compra se aluguel > 50
3. **Cauteloso**: Só compra se saldo após compra ≥ 80
4. **Aleatório**: 50% de chance de comprar

---

## 🏗️ Arquitetura (Resumo)

### Organização em Camadas

```
app/
├── core/              # Contratos e configurações
│   ├── interfaces.py  # Interfaces abstratas (Strategy, Repository, etc.)
│   └── config.py      # Configurações do jogo e aplicação
├── domain/            # Lógica de negócio
│   ├── models.py      # Entidades (Property, Player, Board, GameState)
│   ├── strategies.py  # Implementações de estratégias
│   └── engine.py      # Motor do jogo (regras e execução)
├── application/       # Casos de uso
│   └── simulator.py   # Orquestração de simulações
├── infrastructure/    # Camada de infraestrutura
│   ├── api/           # Endpoints FastAPI
│   └── repositories/  # Implementações de repositórios
└── utils/             # Utilitários
```

### Design Patterns Utilizados

- **Strategy Pattern**: Comportamentos de compra encapsulados
- **Factory Pattern**: Criação centralizada de jogadores
- **Repository Pattern**: Abstração de armazenamento
- **Dependency Injection**: Via FastAPI Depends()
- **Clean Architecture**: Separação em camadas, domínio independente

### Princípios SOLID

- **Dependency Inversion**: Todas as dependências apontam para abstrações (`app/core/interfaces.py`)
- **Single Responsibility**: Cada classe tem uma responsabilidade única
- **Open/Closed**: Extensível via estratégias, sem modificar código existente

---

**Versão**: 1.0.0
**Gerado**: 2025-10-02
