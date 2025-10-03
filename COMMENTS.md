# Como Rodar a Aplicação

> **API REST** que simula partidas de um jogo estilo Monopoly com 4 jogadores usando diferentes estratégias de compra.

---

## 🚀 Execução (Docker - Recomendado)

```bash
# Iniciar aplicação
make docker-up
```

**Acessar:**
- API: http://localhost:8000
- Documentação interativa: http://localhost:8000/docs

**Parar aplicação:**
```bash
make docker-down
```

**Ver logs:**
```bash
make docker-logs
```

---

## 🎮 Usar a API

### Health Check
```bash
curl http://localhost:8000/health
```

### Simular Uma Partida
```bash
curl -X POST http://localhost:8000/game/simulate
```

**Resposta:**
```json
{
  "winner": "impulsive",
  "rounds": 342,
  "timeout": false,
  "players": ["impulsive", "demanding", "cautious", "random"]
}
```

### Executar Simulação em Lote (300 partidas)
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

### Rodar Testes no Docker
```bash
# Testes unitários
make docker-test-unit

# Testes de integração
make docker-test-integration
```

### Rodar Testes Localmente (requer make setup-dev)
```bash
make test-unit        # Testes unitários (fast, ~0.1s)
make test-integration # Testes de integração (API, E2E, ~0.9s)
make coverage         # Coverage (apenas unit tests)
```

---

## 💻 Desenvolvimento

### Setup Inicial para Desenvolvedores

```bash
# Setup automatizado (recomendado)
make setup-dev
```

**O que isso faz:**
- Instala dependências (Python 3.12 + uv necessário)
- Configura pre-push hook para verificações de qualidade
- Formata código inicial
- Roda verificações de qualidade

### Comandos de Qualidade de Código

```bash
make format    # Formatar código
make lint      # Linters (Flake8 + Pylint)
make typecheck # Type checking (MyPy)
make quality   # Rodar tudo (format + lint + typecheck)
```

### Pre-push Hook

**Importante**: O pre-push hook roda automaticamente antes de cada `git push`:
1. ✓ Formatação (Black)
2. ✓ Linting (Flake8 + Pylint)
3. ✓ Type checking (MyPy)
4. ✓ Testes unitários (Pytest)

Se qualquer verificação falhar, o push é bloqueado.

**Bypass** (não recomendado):
```bash
git push --no-verify
```

---

## ⚙️ Configuração

Variáveis de ambiente no `docker-compose.yml`:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `MONOPOLY_DEBUG` | `false` | Modo debug |
| `MONOPOLY_LOG_LEVEL` | `INFO` | Nível de log (DEBUG, INFO, WARNING, ERROR) |
| `MONOPOLY_API_HOST` | `0.0.0.0` | Host da API |
| `MONOPOLY_API_PORT` | `8000` | Porta da API |

---

## 📋 Regras do Jogo

- **Tabuleiro**: 20 propriedades com custos (50-200) e aluguéis (10-100) aleatórios
- **Jogadores**: 4 jogadores começam com saldo de 300
- **Turnos**:
  - Rolar 1d6 e mover no sentido horário
  - Cair em propriedade → comprar (se livre) ou pagar aluguel (se ocupada)
  - Completar uma volta → ganhar salário de 100
- **Eliminação**: Saldo < 0 → jogador eliminado, propriedades liberadas
- **Vitória**: Último jogador restante OU maior saldo após 1000 rodadas (timeout)

### Estratégias dos Jogadores

1. **Impulsivo** (`impulsive`): Sempre compra quando possível
2. **Exigente** (`demanding`): Só compra se aluguel > 50
3. **Cauteloso** (`cautious`): Só compra se saldo após compra ≥ 80
4. **Aleatório** (`random`): 50% de chance de comprar

---

## 📚 Mais Informações

Para detalhes de arquitetura, design patterns e princípios SOLID, consulte o [README.md](README.md).

**Versão**: 1.0.0
