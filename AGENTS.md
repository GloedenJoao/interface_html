# Flight SQL Lab — Agent Guidelines

Este arquivo consolida orientações para qualquer pessoa (humana ou IA) que vá manter ou evoluir o projeto. **Revise-o antes de iniciar uma tarefa e atualize-o sempre que o fluxo de trabalho mudar ou novos padrões forem adotados.**

## 1. Visão geral do projeto
- Aplicação Flask servida a partir de `app/__init__.py` (fábrica da app) e iniciada por `app.py`.
- O banco `SQLite` (`app/data/flights.sqlite`) é criado automaticamente com 10.000 voos sintéticos na inicialização.
- As rotas são registradas via `register_routes(app)` em `app/routes.py` e renderizam templates em `app/templates/`.
- O estado em memória é mantido em duas estruturas:
  - `views_store.py` para views SQL (nome, SQL original e `pandas.DataFrame`).
  - `dashboard_store.py` para widgets e filtros dos dashboards.
- Estilos adicionais ficam em `app/static/styles.css`; Bootstrap 5 é carregado via CDN.

## 2. Convenções de código
- **Rotas**: sempre adicionar novas rotas dentro de `register_routes`. Prefira extrair lógicas auxiliares para funções privadas no final do arquivo.
- **Consultas SQL**: manipule sempre através das funções utilitárias em `app/database.py`. Evite concatenar strings sem sanitização.
- **Views em memória**: utilize as funções expostas por `views_store.py` e sempre armazene cópias dos `DataFrame` para evitar efeitos colaterais.
- **Dashboards**: centralize a criação de gráficos na função `build_visualization` em `routes.py`. Novos tipos devem seguir o padrão `elif viz_type == "novo_tipo"`.
- **Templates**: todos os HTMLs estendem `base.html`. Componentes reutilizáveis devem ser extraídos para blocos Jinja.
- **Estilo Python**: siga PEP 8, mantenha tipagem opcional quando fizer sentido e prefira funções puras reutilizáveis.

## 3. Fluxo de desenvolvimento recomendado
1. **Configurar ambiente**: `python -m venv .venv` (opcional) e `pip install -r requirements.txt`.
2. **Executar a aplicação** para validações manuais: `flask --app app run --debug` ou `python app.py`.
3. **Cenários manuais obrigatórios** após alterações relevantes:
   - Criar/editar/excluir views na página de gerenciamento.
   - Rodar checagem de duplicidade selecionando múltiplas chaves.
   - Montar pelo menos um dashboard de cada tipo e aplicar filtros.
   - Executar consultas na sandbox e salvar resultado como nova view.
4. **Documentação**: sempre que houver mudança de fluxo, atualizar `README.md`, `ai_instructions.md` e este `AGENTS.md`.

## 4. Estrutura de diretórios
```
app/
├── __init__.py        # criação da app Flask e bootstrap do banco
├── dashboard_store.py # estado em memória para dashboards
├── data/              # banco SQLite gerado automaticamente
├── database.py        # utilidades para criar/consultar dados
├── routes.py          # registro das rotas e lógica de negócio
├── static/
│   └── styles.css     # estilos customizados
├── templates/         # templates Jinja (base, views, duplicidade, dashboard, sandbox)
└── views_store.py     # estado das views SQL em memória
app.py                 # entrypoint local
README.md              # documentação principal
ai_instructions.md     # guia rápido para agentes
```
Atualize o diagrama acima quando novos módulos forem adicionados.

## 5. Boas práticas de colaboração
- Crie branches temáticos, mantenha commits pequenos e descritivos.
- Antes de abrir PR, revise lint manualmente (`flake8` ou equivalente se configurado) e execute os cenários manuais.
- Descreva nas PRs as alterações, impactos e passos de validação.
- Registre novos padrões neste arquivo para que futuros contribuidores tenham referência atualizada.

> ⚠️ **Manutenção contínua:** sempre revise e ajuste este documento quando implementar novos fluxos, dependências ou convenções. Ele é a fonte de verdade para qualquer agente que atuar no repositório.
