# Flight SQL Lab

Aplicação web em Flask para criação, análise e visualização de dados utilizando consultas SQL sobre um banco de voos fictício. A ferramenta foi pensada para análises exploratórias, construção de dashboards rápidos e experimentação com consultas em memória.

## Sumário
- [Visão geral](#visão-geral)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Tecnologias](#tecnologias)
- [Preparação do ambiente](#preparação-do-ambiente)
- [Executando a aplicação](#executando-a-aplicação)
- [Páginas e funcionalidades](#páginas-e-funcionalidades)
  - [Gerenciamento de views SQL](#gerenciamento-de-views-sql)
  - [Análise de duplicidade](#análise-de-duplicidade)
  - [Construção de dashboards](#construção-de-dashboards)
  - [Sandbox SQL](#sandbox-sql)
- [Como adicionar novas páginas ou rotas](#como-adicionar-novas-páginas-ou-rotas)
- [Testes e validações manuais](#testes-e-validações-manuais)
- [Atualizações para IA](#atualizações-para-ia)

## Visão geral

Ao iniciar a aplicação, um banco SQLite (`app/data/flights.sqlite`) é criado automaticamente com 10.000 registros sintéticos de voos. Todas as páginas utilizam esse banco como fonte base. As views criadas pelos usuários ficam em memória enquanto o servidor estiver ativo e podem ser reutilizadas entre as páginas.

## Estrutura de pastas

```
app/
├── __init__.py        # Fábrica da aplicação Flask
├── dashboard_store.py # Armazenamento em memória do dashboard
├── data/              # Banco SQLite gerado automaticamente
├── database.py        # Utilidades do banco e geração dos dados fictícios
├── routes.py          # Rotas e lógica de negócio das páginas
├── static/
│   └── styles.css     # Estilos customizados
├── templates/         # Layouts HTML (base, views, duplicidade, dashboard, sandbox)
└── views_store.py     # Armazenamento em memória das views SQL
app.py                 # Ponto de entrada para execução local
README.md              # Este arquivo
ai_instructions.md     # Guia rápido para agentes artificiais
requirements.txt       # Dependências Python
```

## Tecnologias

- [Flask](https://flask.palletsprojects.com/) para o servidor web.
- [SQLite](https://www.sqlite.org/) como banco local de desenvolvimento.
- [pandas](https://pandas.pydata.org/) para manipular os resultados das consultas.
- [Plotly](https://plotly.com/python/) para gerar visualizações interativas.
- [Bootstrap 5](https://getbootstrap.com/) via CDN para estilização.

## Preparação do ambiente

1. **Crie e ative um ambiente virtual (opcional, mas recomendado).**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\\Scripts\\activate   # Windows PowerShell
   ```
2. **Instale as dependências.**
   ```bash
   pip install -r requirements.txt
   ```

## Executando a aplicação

1. Garanta que você está na raiz do projeto (`/workspace/interface_html`).
2. Execute o servidor Flask:
   ```bash
   flask --app app run --debug
   ```
   ou
   ```bash
   python app.py
   ```
3. Abra o navegador em `http://127.0.0.1:5000`.

Na primeira execução, o banco SQLite com 10.000 voos fictícios será criado automaticamente em `app/data/flights.sqlite`.

## Páginas e funcionalidades

### Gerenciamento de views SQL
- **Criar view**: selecione a tabela `flights` ou escreva uma consulta `SELECT`/`WITH` para gerar a view.
- **Editar/Atualizar**: reabra a view para alterar o SQL ou clique em “Atualizar” para reexecutar a consulta original.
- **Excluir**: remove a view da memória.
- As views ficam disponíveis para as demais páginas enquanto o servidor estiver ativo.

### Análise de duplicidade
- Escolha uma view carregada em memória e marque as colunas que compõem a chave.
- O sistema informa se há duplicidades, quantas linhas estão duplicadas e exibe as linhas correspondentes ordenadas pela chave.

### Construção de dashboards
- Utilize qualquer view como fonte.
- Tipos de visualização suportados: tabela, linha, barra, pizza e dispersão.
- Campos de configuração:
  - `Coluna X`, `Coluna Y`, `Cor/Agrupamento`, `Tamanho`, `Texto/hover`, `Rótulos (pizza)`, `Valores (pizza)` e `Colunas da tabela` (lista separada por vírgulas).
- **Filtros opcionais**: informe um filtro por linha no formato `coluna operador valor`. Operadores aceitos: `=`, `!=`, `>`, `<`, `>=`, `<=`, `contains`.
- Cada visualização pode ser editada ou removida após adicionada ao dashboard.

### Sandbox SQL
- Consulte livremente as views em memória usando SQL.
- A coluna lateral mostra o esquema de cada view disponível.
- É possível salvar o resultado de uma consulta da sandbox como nova view em memória.

## Como adicionar novas páginas ou rotas

1. Crie a view/função no arquivo `app/routes.py`. Utilize o padrão existente para registrar novas rotas dentro da função `register_routes`.
2. Caso seja necessário estado em memória, avalie criar uma estrutura semelhante a `view_store.py` ou `dashboard_store.py`.
3. Adicione o template correspondente em `app/templates/` e, se preciso, estilos adicionais em `app/static/styles.css`.
4. Inclua a nova rota na barra de navegação em `app/templates/base.html`.
5. Atualize este README e `ai_instructions.md` com instruções relevantes.

## Testes e validações manuais

Como o projeto é uma aplicação web interativa, recomenda-se a seguinte verificação manual após alterações:

1. **Inicialização**: executar `flask --app app run --debug` e confirmar que o banco SQLite é criado sem erros.
2. **Views**: criar, editar, atualizar e excluir uma view. Confirmar que a view aparece nas demais páginas.
3. **Duplicidade**: selecionar diferentes combinações de colunas e validar a contagem de duplicados.
4. **Dashboard**: gerar visualizações de cada tipo, aplicar filtros e testar os botões de edição/remoção.
5. **Sandbox**: executar consultas simples (`SELECT * FROM minha_view LIMIT 10`) e salvar o resultado como nova view.

## Atualizações para IA

- Sempre que novos fluxos forem adicionados, mantenha `README.md` e `ai_instructions.md` atualizados.
- Consulte `ai_instructions.md` para convenções internas, pontos de extensão e orientações específicas para agentes inteligentes.
