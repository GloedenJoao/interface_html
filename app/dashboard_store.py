import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DashboardItem:
    id: str
    name: str
    view_name: str
    viz_type: str
    columns: Dict[str, Optional[str]]
    filters_text: str
    rendered: Dict[str, str] = field(default_factory=dict)


class DashboardStore:
    def __init__(self) -> None:
        self._items: Dict[str, DashboardItem] = {}

    def list(self) -> List[DashboardItem]:
        return list(self._items.values())

    def get(self, item_id: str) -> Optional[DashboardItem]:
        return self._items.get(item_id)

    def add(self, name: str, view_name: str, viz_type: str, columns: Dict[str, Optional[str]], filters_text: str, rendered: Dict[str, str]) -> DashboardItem:
        item_id = uuid.uuid4().hex
        item = DashboardItem(
            id=item_id,
            name=name,
            view_name=view_name,
            viz_type=viz_type,
            columns=columns,
            filters_text=filters_text,
            rendered=rendered,
        )
        self._items[item_id] = item
        return item

    def update(self, item_id: str, name: str, view_name: str, viz_type: str, columns: Dict[str, Optional[str]], filters_text: str, rendered: Dict[str, str]) -> DashboardItem:
        if item_id not in self._items:
            raise KeyError("Dashboard item not found")
        item = self._items[item_id]
        item.name = name
        item.view_name = view_name
        item.viz_type = viz_type
        item.columns = columns
        item.filters_text = filters_text
        item.rendered = rendered
        return item

    def delete(self, item_id: str) -> None:
        self._items.pop(item_id, None)

    def clear(self) -> None:
        self._items.clear()


dashboard_store = DashboardStore()

