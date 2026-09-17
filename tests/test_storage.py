"""Testes unitários para persistência JSON do MemoList."""

from pathlib import Path
import tempfile
import unittest
from memolist.models import ItemList
from memolist.storage import StorageManager


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "test_lists.json"
        self.storage = StorageManager(self.file_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_load(self):
        item_list = ItemList(
            title="Lista Teste",
            description="Descrição teste",
            items=["Item 1", "Item 2", "Item 3"],
        )
        self.storage.save_list(item_list)

        loaded = self.storage.get_by_id(item_list.id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.title, "Lista Teste")
        self.assertEqual(len(loaded.items), 3)

    def test_delete(self):
        item_list = ItemList(title="Para Deletar", items=["A", "B"])
        self.storage.save_list(item_list)
        self.assertEqual(len(self.storage.load_all()), 1)

        success = self.storage.delete_list(item_list.id)
        self.assertTrue(success)
        self.assertEqual(len(self.storage.load_all()), 0)


if __name__ == "__main__":
    unittest.main()
