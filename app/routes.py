from __future__ import annotations

import json
import sqlite3
from ast import literal_eval
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
)

from .dashboard_store import dashboard_store
from .database import get_connection, list_tables
from .views_store import StoredView, view_store

ALLOWED_SQL_PREFIXES = ("SELECT", "WITH")


def register_routes(app: Flask) -> None:
    @app.context_processor
    def inject_globals() -> Dict[str, List[StoredView]]:
        return {"views_in_memory": list(view_store.list())}

    @app.route("/")
    def index():
        return redirect(url_for("manage_views"))

    @app.route("/views", methods=["GET", "POST"])
    def manage_views():
        database_path = app.config["DATABASE_PATH"]
        tables = list_tables(database_path)
        error = None
        success = None
        edit_name = request.args.get("edit")
        edit_view = view_store.get(edit_name) if edit_name else None

        if request.method == "POST":
            original_name = request.form.get("original_name") or None
            view_name = (request.form.get("view_name") or "").strip()
            query_source = request.form.get("query_source", "table")
            sql_query = ""

            if not view_name:
                error = "Informe um nome para a view."
            else:
                if query_source == "table":
                    table_name = request.form.get("table_name")
                    if not table_name:
                        error = "Selecione uma tabela."
                    else:
                        sql_query = f"SELECT * FROM {table_name}"
                else:
                    sql_query = (request.form.get("sql_query") or "").strip()
                    if not sql_query:
                        error = "Informe a consulta SQL."
                    elif not sql_query.upper().startswith(ALLOWED_SQL_PREFIXES):
                        error = "Somente consultas iniciando com SELECT ou WITH são permitidas."

            if not error:
                try:
                    dataframe = execute_sql_query(database_path, sql_query)
                except Exception as exc:  # pragma: no cover - feedback to UI
                    error = f"Erro ao executar a consulta: {exc}"
                else:
                    try:
                        if original_name:
                            if original_name != view_name:
                                view_store.rename(original_name, view_name)
                            view_store.update(view_name, sql_query, dataframe)
                        else:
                            if view_store.get(view_name):
                                raise KeyError(
                                    f"Já existe uma view chamada '{view_name}'."
                                )
                            view_store.save(view_name, sql_query, dataframe)
                        success = f"View '{view_name}' salva com sucesso."
                    except KeyError as exc:
                        error = str(exc)

        views = list(view_store.list())
        return render_template(
            "views.html",
            tables=tables,
            views=views,
            error=error,
            success=success,
            edit_view=edit_view,
        )

    @app.route("/views/<view_name>/delete", methods=["POST"])
    def delete_view(view_name: str):
        view_store.delete(view_name)
        return redirect(url_for("manage_views"))

    @app.route("/views/<view_name>/refresh", methods=["POST"])
    def refresh_view(view_name: str):
        database_path = app.config["DATABASE_PATH"]
        stored = view_store.get(view_name)
        if stored is None:
            return redirect(url_for("manage_views"))

        try:
            dataframe = execute_sql_query(database_path, stored.query)
        except Exception:
            # Mantém os dados antigos se der erro na consulta original
            pass
        else:
            view_store.update(view_name, stored.query, dataframe)
        return redirect(url_for("manage_views"))

    @app.route("/views/<view_name>/edit")
    def edit_view(view_name: str):
        if not view_store.get(view_name):
            return redirect(url_for("manage_views"))
        return redirect(url_for("manage_views", edit=view_name))

    @app.route("/duplicates", methods=["GET", "POST"])
    def duplicates():
        selected_view_name = request.values.get("view_name")
        selected_columns = request.values.getlist("columns")
        error = None
        duplicates_df: Optional[pd.DataFrame] = None
        duplicates_count = 0
        columns: List[str] = []
        has_duplicates = False

        stored_view = view_store.get(selected_view_name) if selected_view_name else None
        if stored_view is not None:
            columns = list(stored_view.dataframe.columns)

        if request.method == "POST" and stored_view is not None:
            if not selected_columns:
                error = "Selecione ao menos uma coluna para verificar duplicidade."
            else:
                df = stored_view.dataframe
                duplicated_mask = df.duplicated(subset=selected_columns, keep=False)
                duplicates_df = df.loc[duplicated_mask]
                if not duplicates_df.empty:
                    duplicates_df = duplicates_df.sort_values(selected_columns)
                duplicates_count = int(df.duplicated(subset=selected_columns).sum())
                has_duplicates = duplicates_count > 0

        duplicates_html = (
            duplicates_df.to_html(classes="table table-striped table-sm", index=False)
            if duplicates_df is not None and not duplicates_df.empty
            else None
        )

        return render_template(
            "duplicates.html",
            views=list(view_store.list()),
            selected_view=selected_view_name,
            columns=columns,
            selected_columns=selected_columns,
            duplicates_html=duplicates_html,
            duplicates_count=duplicates_count,
            has_duplicates=has_duplicates,
            error=error,
        )

    @app.route("/dashboard", methods=["GET", "POST"])
    def dashboard():
        error = None
        success = None
        preview = None
        selected_view_name = request.values.get("view_name")
        edit_item_id = request.args.get("edit_id")
        edit_item = dashboard_store.get(edit_item_id) if edit_item_id else None
        if not selected_view_name and edit_item is not None:
            selected_view_name = edit_item.view_name

        if request.method == "POST":
            action = request.form.get("action")
            selected_view_name = request.form.get("view_name") or None
            viz_type = request.form.get("viz_type") or "table"
            viz_name = (request.form.get("viz_name") or viz_type.title()).strip()
            filters_text = request.form.get("filters") or ""
            columns = {
                "x": _clean(request.form.get("x_column")),
                "y": _clean(request.form.get("y_column")),
                "color": _clean(request.form.get("color_column")),
                "size": _clean(request.form.get("size_column")),
                "text": _clean(request.form.get("text_column")),
                "names": _clean(request.form.get("names_column")),
                "values": _clean(request.form.get("value_column")),
                "table_columns": _clean(request.form.get("table_columns")),
            }
            item_id = request.form.get("item_id") or None

            if action in {"preview", "add", "update"}:
                if not selected_view_name:
                    error = "Escolha uma view para construir a visualização."
                else:
                    result = build_visualization(selected_view_name, viz_type, columns, filters_text)
                    if "error" in result:
                        error = result["error"]
                    else:
                        preview = result
                        if action == "add":
                            dashboard_store.add(
                                viz_name,
                                selected_view_name,
                                viz_type,
                                columns,
                                filters_text,
                                result,
                            )
                            success = f"Visualização '{viz_name}' adicionada ao dashboard."
                        elif action == "update" and item_id:
                            dashboard_store.update(
                                item_id,
                                viz_name,
                                selected_view_name,
                                viz_type,
                                columns,
                                filters_text,
                                result,
                            )
                            success = f"Visualização '{viz_name}' atualizada."

        view_columns = _get_view_columns(selected_view_name)

        return render_template(
            "dashboard.html",
            views=list(view_store.list()),
            dashboard_items=dashboard_store.list(),
            selected_view=selected_view_name,
            view_columns=view_columns,
            preview=preview,
            error=error,
            success=success,
            edit_item=edit_item,
        )

    @app.route("/dashboard/<item_id>/delete", methods=["POST"])
    def delete_dashboard_item(item_id: str):
        dashboard_store.delete(item_id)
        return redirect(url_for("dashboard"))

    @app.route("/dashboard/<item_id>/edit")
    def edit_dashboard_item(item_id: str):
        if not dashboard_store.get(item_id):
            return redirect(url_for("dashboard"))
        return redirect(url_for("dashboard", edit_id=item_id))

    @app.route("/sandbox", methods=["GET", "POST"])
    def sandbox():
        sql_query = request.form.get("sql_query") if request.method == "POST" else ""
        new_view_name = (request.form.get("new_view_name") or "").strip()
        action = request.form.get("action") if request.method == "POST" else None
        error = None
        success = None
        result_html = None

        if request.method == "POST":
            if not sql_query:
                error = "Informe uma consulta SQL."
            else:
                try:
                    dataframe = execute_on_views(sql_query)
                except Exception as exc:
                    error = f"Erro ao executar a consulta: {exc}"
                else:
                    result_html = dataframe.to_html(
                        classes="table table-striped table-sm", index=False
                    )
                    if action == "save" and new_view_name:
                        if view_store.get(new_view_name):
                            error = f"Já existe uma view chamada '{new_view_name}'."
                        else:
                            view_store.save(new_view_name, sql_query, dataframe)
                            success = f"View '{new_view_name}' criada a partir da sandbox."

        view_summaries = _build_view_summaries()

        return render_template(
            "sandbox.html",
            sql_query=sql_query,
            result_html=result_html,
            error=error,
            success=success,
            view_summaries=view_summaries,
        )


def execute_sql_query(database_path: str, sql_query: str) -> pd.DataFrame:
    connection = get_connection(database_path)
    try:
        return pd.read_sql_query(sql_query, connection)
    finally:
        connection.close()


def execute_on_views(sql_query: str) -> pd.DataFrame:
    memory_connection = sqlite3.connect(":memory:")
    try:
        for stored in view_store.list():
            stored.dataframe.to_sql(stored.name, memory_connection, index=False, if_exists="replace")
        return pd.read_sql_query(sql_query, memory_connection)
    finally:
        memory_connection.close()


def build_visualization(view_name: str, viz_type: str, columns: Dict[str, Optional[str]], filters_text: str) -> Dict[str, str]:
    stored_view = view_store.get(view_name)
    if stored_view is None:
        return {"error": "View selecionada não existe mais."}

    dataframe = stored_view.dataframe.copy()
    try:
        dataframe = apply_filters(dataframe, filters_text)
    except ValueError as exc:
        return {"error": str(exc)}

    if viz_type == "table":
        selected_columns = _parse_columns_list(columns.get("table_columns"), dataframe.columns)
        if selected_columns:
            missing = [col for col in selected_columns if col not in dataframe.columns]
            if missing:
                return {"error": f"Colunas inexistentes para tabela: {', '.join(missing)}"}
            dataframe = dataframe[selected_columns]
        return {
            "type": "table",
            "table_html": dataframe.head(500).to_html(
                classes="table table-striped table-sm", index=False
            ),
        }

    if dataframe.empty:
        return {"error": "Não há dados para gerar o gráfico após aplicar os filtros."}

    if viz_type == "line":
        x, y = columns.get("x"), columns.get("y")
        if not x or not y:
            return {"error": "Informe as colunas X e Y para o gráfico de linha."}
        fig = px.line(
            dataframe,
            x=x,
            y=y,
            color=columns.get("color") or None,
        )
    elif viz_type == "bar":
        x, y = columns.get("x"), columns.get("y")
        if not x or not y:
            return {"error": "Informe as colunas X e Y para o gráfico de barras."}
        fig = px.bar(
            dataframe,
            x=x,
            y=y,
            color=columns.get("color") or None,
        )
    elif viz_type == "scatter":
        x, y = columns.get("x"), columns.get("y")
        if not x or not y:
            return {"error": "Informe as colunas X e Y para o gráfico de dispersão."}
        fig = px.scatter(
            dataframe,
            x=x,
            y=y,
            color=columns.get("color") or None,
            size=columns.get("size") or None,
            hover_name=columns.get("text") or None,
        )
    elif viz_type == "pie":
        names, values = columns.get("names"), columns.get("values")
        if not names or not values:
            return {"error": "Informe as colunas de rótulo e valor para o gráfico de pizza."}
        fig = px.pie(dataframe, names=names, values=values)
    else:
        return {"error": f"Tipo de visualização desconhecido: {viz_type}"}

    return {
        "type": "chart",
        "graph_json": json.dumps(fig, cls=PlotlyJSONEncoder),
    }


def apply_filters(dataframe: pd.DataFrame, filters_text: str) -> pd.DataFrame:
    if not filters_text:
        return dataframe

    filtered = dataframe.copy()
    for line in filters_text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 3:
            raise ValueError(
                "Filtro inválido. Use o formato 'coluna operador valor', um por linha."
            )
        column, operator, raw_value = parts[0], parts[1], " ".join(parts[2:])
        if column not in filtered.columns:
            raise ValueError(f"Coluna '{column}' não encontrada na view.")

        value = _parse_value(raw_value)
        series = filtered[column]

        if operator == "=":
            mask = series == value
        elif operator == "!=":
            mask = series != value
        elif operator == ">":
            mask = series > value
        elif operator == "<":
            mask = series < value
        elif operator == ">=":
            mask = series >= value
        elif operator == "<=":
            mask = series <= value
        elif operator.lower() == "contains":
            mask = series.astype(str).str.contains(str(value), case=False, na=False)
        else:
            raise ValueError(
                "Operador inválido. Utilize =, !=, >, <, >=, <= ou contains."
            )
        filtered = filtered.loc[mask]
    return filtered


def _parse_value(raw_value: str):
    text = raw_value.strip()
    try:
        return literal_eval(text)
    except (ValueError, SyntaxError):
        return text.strip("\"")


def _parse_columns_list(value: Optional[str], available: List[str]) -> List[str]:
    if not value:
        return []
    columns = [item.strip() for item in value.split(",") if item.strip()]
    return [col for col in columns if col in available]


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _get_view_columns(view_name: Optional[str]) -> List[str]:
    if not view_name:
        return []
    stored_view = view_store.get(view_name)
    if stored_view is None:
        return []
    return list(stored_view.dataframe.columns)


def _build_view_summaries() -> List[Tuple[str, List[Tuple[str, str]]]]:
    summaries = []
    for stored in view_store.list():
        columns: List[Tuple[str, str]] = []
        for column in stored.dataframe.columns:
            dtype = str(stored.dataframe[column].dtype)
            columns.append((column, dtype))
        summaries.append((stored.name, columns))
    return summaries

