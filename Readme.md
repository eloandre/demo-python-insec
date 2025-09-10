
# Insecure Python App (Flask) - Para fins educacionais

**AVISO**: Esta aplicação é INTENCIONALMENTE insegura. Use apenas em ambientes isolados (VMs, containers, sandboxes).

## O que contém
- app.py (Flask) com vulnerabilidades:
  - Credenciais / API key hardcoded
  - SQL Injection (consulta construída por concatenação)
  - XSS reflexivo (renderização sem escape)
  - RCE simulada (não executa)
- requirements.txt com versões antigas / pacotes exemplares maliciosos
- Dockerfile para rodar em container isolado
- terraform/main.tf com IaC inseguro (exposição de SGs e RDS públicos)