"""Testes unitários de inicialização das views Flet."""

import unittest
from unittest.mock import MagicMock
from memolist.models import ItemList
from memolist.storage import StorageManager
from memolist.ui.views.dashboard_view import DashboardView
from memolist.ui.views.list_edit_view import ListEditView
from memolist.ui.views.review_view import ReviewView
import tempfile
from pathlib import Path


class TestViewsInitialization(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "test_lists.json"
        self.storage = StorageManager(self.file_path)
        self.mock_page = MagicMock()
        self.mock_page.on_keyboard_event = None

        # Seed a test list
        self.test_list = ItemList(
            title="Lista Teste",
            description="Descrição",
            items=["Item 1", "Item 2", "Item 3"],
        )
        self.storage.save_list(self.test_list)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_dashboard_view_init(self):
        view = DashboardView(
            page=self.mock_page,
            storage=self.storage,
            on_review=MagicMock(),
            on_create=MagicMock(),
            on_edit=MagicMock(),
        )
        self.assertIsNotNone(view)
        self.assertEqual(view.app_page, self.mock_page)

    def test_list_edit_view_init(self):
        view_create = ListEditView(
            page=self.mock_page,
            storage=self.storage,
            list_id=None,
            on_back=MagicMock(),
        )
        self.assertIsNotNone(view_create)

        view_edit = ListEditView(
            page=self.mock_page,
            storage=self.storage,
            list_id=self.test_list.id,
            on_back=MagicMock(),
        )
        self.assertIsNotNone(view_edit)

    def test_list_edit_view_bulk_add_dialog(self):
        view = ListEditView(
            page=self.mock_page,
            storage=self.storage,
            list_id=None,
            on_back=MagicMock(),
        )
        view._open_bulk_add_dialog(None)
        self.assertTrue(self.mock_page.show_dialog.called)

    def test_review_view_init(self):
        view = ReviewView(
            page=self.mock_page,
            storage=self.storage,
            list_id=self.test_list.id,
            on_finish=MagicMock(),
        )
        self.assertIsNotNone(view)
        self.assertEqual(view.total_items, 3)
        view.cleanup()

    def test_main_routing(self):
        import main
        # Verify main executes and sets up navigation without raising exceptions
        mock_page = MagicMock()
        mock_page.on_keyboard_event = None
        main.main(mock_page)
        self.assertTrue(mock_page.add.called)


if __name__ == "__main__":
    unittest.main()
