# Exemplos de API

## Healthcheck

```bash
curl -u evora:troque_esta_senha http://localhost:8000/api/health
```

## Simular conversa

```bash
curl -X POST http://localhost:8000/api/simulate-message \
  -u evora:troque_esta_senha \
  -H "Content-Type: application/json" \
  -d '{"from_phone":"5516999999999","profile_name":"Carlos","text":"Tenho um lead"}'
```

## Próxima resposta

```bash
curl -X POST http://localhost:8000/api/simulate-message \
  -u evora:troque_esta_senha \
  -H "Content-Type: application/json" \
  -d '{"from_phone":"5516999999999","profile_name":"Carlos","text":"Mariana"}'
```

## Listar leads

```bash
curl -u evora:troque_esta_senha http://localhost:8000/api/leads
```

## Resumo do dashboard

```bash
curl -u evora:troque_esta_senha http://localhost:8000/api/dashboard/summary
```
