"""Testes unitários para o módulo SM-2 do MemoList."""

from datetime import date, timedelta
import unittest
from memolist.srs import calculate_next_review, preview_intervals


class TestSRS(unittest.TestCase):
    def test_ease_factor_penalty_on_errei(self):
        """Verifica se grade=1 (Errei) penaliza o Ease Factor em -0.54 e reseta repetições."""
        base_date = date(2026, 9, 16)
        res = calculate_next_review(
            repetitions=2,
            interval_days=6,
            ease_factor=2.50,
            grade=1,
            base_date=base_date,
        )
        self.assertEqual(res.repetitions, 0)
        self.assertEqual(res.interval_days, 1)
        self.assertAlmostEqual(res.ease_factor, 1.96)
        self.assertEqual(res.next_review, base_date + timedelta(days=1))

    def test_ease_factor_minimum_floor(self):
        """Verifica se o Ease Factor nunca cai abaixo de 1.30."""
        res = calculate_next_review(
            repetitions=0,
            interval_days=1,
            ease_factor=1.40,
            grade=1,
        )
        self.assertEqual(res.ease_factor, 1.30)

    def test_initial_intervals_option_b(self):
        """Verifica os intervalos diferenciados da 1ª e 2ª repetição (Opção B - Anki style)."""
        # Repetition 0
        res_dificil_0 = calculate_next_review(0, 0, 2.50, grade=3)
        res_bom_0 = calculate_next_review(0, 0, 2.50, grade=4)
        res_facil_0 = calculate_next_review(0, 0, 2.50, grade=5)

        self.assertEqual(res_dificil_0.interval_days, 1)
        self.assertEqual(res_bom_0.interval_days, 2)
        self.assertEqual(res_facil_0.interval_days, 4)

        # Repetition 1
        res_dificil_1 = calculate_next_review(1, 1, 2.36, grade=3)
        res_bom_1 = calculate_next_review(1, 2, 2.50, grade=4)
        res_facil_1 = calculate_next_review(1, 4, 2.60, grade=5)

        self.assertEqual(res_dificil_1.interval_days, 3)
        self.assertEqual(res_bom_1.interval_days, 6)
        self.assertEqual(res_facil_1.interval_days, 8)

    def test_preview_intervals(self):
        """Verifica se preview_intervals reflete fielmente as previsões."""
        previews = preview_intervals(repetitions=0, interval_days=0, ease_factor=2.50)
        self.assertEqual(previews["errei"], 1)
        self.assertEqual(previews["dificil"], 1)
        self.assertEqual(previews["bom"], 2)
        self.assertEqual(previews["facil"], 4)

        previews_rep1 = preview_intervals(repetitions=1, interval_days=2, ease_factor=2.50)
        self.assertEqual(previews_rep1["errei"], 1)
        self.assertEqual(previews_rep1["dificil"], 3)
        self.assertEqual(previews_rep1["bom"], 6)
        self.assertEqual(previews_rep1["facil"], 8)


if __name__ == "__main__":
    unittest.main()
