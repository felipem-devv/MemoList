"""Teste de integração ponta a ponta do ciclo de vida da lista e revisão."""

from datetime import date
from pathlib import Path
import tempfile
import unittest
from memolist.models import ItemList
from memolist.storage import StorageManager
from memolist.srs import calculate_next_review


class TestEndToEndFlow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "lists.json"
        self.storage = StorageManager(self.file_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_full_review_lifecycle(self):
        # 1. Criar lista com 5 itens
        items = ["Estação A", "Estação B", "Estação C", "Estação D", "Estação E"]
        new_list = ItemList(
            title="Linha Teste",
            description="Sentido A -> E",
            items=items,
        )
        self.storage.save_list(new_list)

        # 2. Verificar que ela está devida inicialmente
        due_lists = self.storage.get_due_lists()
        self.assertEqual(len(due_lists), 1)
        self.assertEqual(due_lists[0].id, new_list.id)

        # 3. Simular revisão: usuário acerta 4 e erra 1
        items_correct = 4
        total_items = len(items)
        user_chosen_grade = 4  # Bom

        # Calcular SM-2
        srs_result = calculate_next_review(
            repetitions=new_list.srs.repetitions,
            interval_days=new_list.srs.interval_days,
            ease_factor=new_list.srs.ease_factor,
            grade=user_chosen_grade,
            base_date=date(2026, 9, 16),
        )

        # Atualizar lista
        new_list.srs.repetitions = srs_result.repetitions
        new_list.srs.interval_days = srs_result.interval_days
        new_list.srs.ease_factor = srs_result.ease_factor
        new_list.srs.next_review = srs_result.next_review.isoformat()
        new_list.srs.last_reviewed = "2026-09-16T17:50:00"

        from memolist.models import ReviewRecord
        record = ReviewRecord(
            date="2026-09-16T17:50:00",
            grade=user_chosen_grade,
            items_correct=items_correct,
            items_total=total_items,
            interval_days=srs_result.interval_days,
            ease_factor=srs_result.ease_factor,
        )
        new_list.review_history.append(record)

        # Salvar
        self.storage.save_list(new_list)

        # 4. Recarregar do JSON e validar
        reloaded = self.storage.get_by_id(new_list.id)
        self.assertIsNotNone(reloaded)
        self.assertEqual(reloaded.srs.repetitions, 1)
        self.assertEqual(reloaded.srs.interval_days, 2)  # Bom na 1a rep = 2 dias
        self.assertEqual(reloaded.srs.next_review, "2026-09-18")
        self.assertEqual(len(reloaded.review_history), 1)
        self.assertEqual(reloaded.review_history[0].items_correct, 4)
        self.assertEqual(reloaded.review_history[0].items_total, 5)
        self.assertEqual(reloaded.review_history[0].grade, 4)


if __name__ == "__main__":
    unittest.main()
