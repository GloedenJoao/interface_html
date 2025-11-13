from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional

import pandas as pd


@dataclass
class StoredView:
    name: str
    query: str
    dataframe: pd.DataFrame
    created_at: dt.datetime = field(default_factory=dt.datetime.utcnow)
    updated_at: dt.datetime = field(default_factory=dt.datetime.utcnow)


class ViewStore:
    def __init__(self) -> None:
        self._views: Dict[str, StoredView] = {}

    def list(self) -> Iterable[StoredView]:
        return self._views.values()

    def get(self, name: str) -> Optional[StoredView]:
        return self._views.get(name)

    def save(self, name: str, query: str, dataframe: pd.DataFrame) -> StoredView:
        stored = StoredView(name=name, query=query, dataframe=dataframe.copy())
        stored.updated_at = stored.created_at
        self._views[name] = stored
        return stored

    def update(self, name: str, query: str, dataframe: pd.DataFrame) -> StoredView:
        if name not in self._views:
            raise KeyError(f"View '{name}' not found")
        stored = self._views[name]
        stored.query = query
        stored.dataframe = dataframe.copy()
        stored.updated_at = dt.datetime.utcnow()
        return stored

    def delete(self, name: str) -> None:
        self._views.pop(name, None)

    def rename(self, old_name: str, new_name: str) -> StoredView:
        if new_name in self._views and new_name != old_name:
            raise KeyError(f"View '{new_name}' already exists")
        stored = self._views.pop(old_name)
        stored.name = new_name
        self._views[new_name] = stored
        return stored

    def clear(self) -> None:
        self._views.clear()


view_store = ViewStore()

