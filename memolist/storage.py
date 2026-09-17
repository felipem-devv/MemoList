"""Módulo de persistência em JSON puro para o MemoList."""

import json
from pathlib import Path
import tempfile
import os
from memolist.models import ItemList


DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_DATA_FILE = DEFAULT_DATA_DIR / "lists.json"


class StorageManager:
    def __init__(self, file_path: Path | str | None = None):
        if file_path is None:
            self.file_path = DEFAULT_DATA_FILE
        else:
            self.file_path = Path(file_path)

        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            initial_data = {"version": 1, "lists": []}
            self._write_raw(initial_data)

    def _read_raw(self) -> dict:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"version": 1, "lists": []}

    def _write_raw(self, data: dict) -> None:
        """Escrita atômica para evitar corrupção de arquivo."""
        dir_name = self.file_path.parent
        with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
            json.dump(data, tf, indent=2, ensure_ascii=False)
            temp_path = tf.name

        os.replace(temp_path, self.file_path)

    def load_all(self) -> list[ItemList]:
        raw = self._read_raw()
        lists_data = raw.get("lists", [])
        return [ItemList.from_dict(item) for item in lists_data]

    def get_by_id(self, list_id: str) -> ItemList | None:
        all_lists = self.load_all()
        for l in all_lists:
            if l.id == list_id:
                return l
        return None

    def save_list(self, item_list: ItemList) -> None:
        all_lists = self.load_all()
        index = next((i for i, l in enumerate(all_lists) if l.id == item_list.id), None)
        if index is not None:
            all_lists[index] = item_list
        else:
            all_lists.append(item_list)

        data = {
            "version": 1,
            "lists": [l.to_dict() for l in all_lists]
        }
        self._write_raw(data)

    def delete_list(self, list_id: str) -> bool:
        all_lists = self.load_all()
        filtered = [l for l in all_lists if l.id != list_id]
        if len(filtered) == len(all_lists):
            return False

        data = {
            "version": 1,
            "lists": [l.to_dict() for l in filtered]
        }
        self._write_raw(data)
        return True

    def get_due_lists(self) -> list[ItemList]:
        return [l for l in self.load_all() if l.is_due]

    def get_stats(self) -> dict[str, int]:
        all_lists = self.load_all()
        due_lists = [l for l in all_lists if l.is_due]
        total_items = sum(len(l.items) for l in all_lists)
        return {
            "total_lists": len(all_lists),
            "due_lists": len(due_lists),
            "total_items": total_items,
        }
