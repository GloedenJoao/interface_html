# 📌 Instruções para agentes de IA

Este arquivo fornece orientações para agentes autônomos que desejam estender ou manter o projeto **Flight SQL Lab**. Atualize este documento sempre que novas funcionalidades forem incluídas.

## 🗺️ Visão rápida da arquitetura
- **`app/__init__.py`**: cria a instância Flask, inicializa o banco SQLite e registra as rotas.
- **`app/routes.py`**: ponto central com todas as páginas (views, duplicidade, dashboard, sandbox). A função `register_routes(app)` registra todas as rotas.
- **`app/database.py`**: inicialização do banco `flights.sqlite` com 10.000 linhas sintéticas e utilidades para listar/consultar tabelas.
- **`app/views_store.py`**: armazenamento em memória das views criadas. Cada view possui nome, SQL e um `pandas.DataFrame` associado.
- **`app/dashboard_store.py`**: armazenamento em memória das visualizações do dashboard.
- **Templates**: ficam em `app/templates/` e herdam de `base.html`. CSS extra em `app/static/styles.css`.

## 🧭 Convenções internas
- Utilize `view_store` para manipular views existentes. Sempre armazene cópias dos `DataFrame` para evitar mutações inesperadas.
- Visualizações do dashboard devem ser construídas via `build_visualization` (em `app/routes.py`) para garantir aplicação consistente de filtros.
- Filtros seguem o padrão `coluna operador valor` por linha. Para novos operadores, atualize `apply_filters`.
- Toda nova rota deve ser registrada dentro de `register_routes`. Mantenha o padrão de retorno `render_template` com contexto explícito.
- Quando adicionar dependências Python, atualize `requirements.txt`, `README.md` e este arquivo.

## 🧱 Pontos de ancoragem para extensões
- **Novas páginas**: crie funções adicionais em `app/routes.py` e templates correspondentes. Considere adicionar novo item no menu em `base.html`.
- **Novas análises sobre views**: reutilize `view_store` para acessar os dados em memória. Funções auxiliares podem ser adicionadas próximo a `apply_filters`.
- **Novos tipos de gráficos**: expanda `build_visualization` com novos ramos (`elif viz_type == 'novo_tipo'`). Salve o JSON em `result['graph_json']` para manter compatibilidade com o front-end.
- **Integração com bancos externos**: crie adaptadores em `app/database.py` mantendo a geração do banco local para desenvolvimento e testes.

## 🔄 Boas práticas para manutenção
1. **Atualize README.md e ai_instructions.md** sempre que houver mudança de fluxo, dependência ou estrutura.
2. **Documente novos pontos de extensão** adicionando descrições semelhantes às existentes.
3. **Preferir funções puras**: sempre que possível extraia lógicas repetidas do corpo das rotas para funções auxiliares no final de `routes.py`.
4. **Teste manualmente** usando o roteiro indicado em `README.md` após alterações significativas.
5. **Evite acoplamento** entre templates; mantenha componentes compartilhados em `base.html` ou crie _partials_ dedicados.

## ➕ Adicionando novas rotas, páginas, análises ou gráficos
1. Crie/ajuste o controlador em `app/routes.py` e registre-o dentro de `register_routes`.
2. Adicione o template correspondente (ou componente) em `app/templates/`.
3. Se precisar de estado em memória, siga o padrão de `view_store.py` ou `dashboard_store.py`.
4. Inclua o item de navegação em `base.html`.
5. Atualize `README.md` com instruções de uso e este arquivo com as novas orientações.

Mantenha o projeto consistente e amigável para outros agentes! 🤖
