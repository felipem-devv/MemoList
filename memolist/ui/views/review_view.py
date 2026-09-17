"""View do Modo de Revisão: fluxo item-a-item estilo Anki com autoavaliação subjetiva final."""

from datetime import datetime, date
from typing import Callable
import flet as ft
from memolist.models import ItemList, ReviewRecord
from memolist.storage import StorageManager
from memolist.srs import calculate_next_review, preview_intervals
from memolist.ui.theme import (
    BG_COLOR,
    SURFACE_COLOR,
    SURFACE_CARD,
    SURFACE_HOVER,
    BORDER_COLOR,
    PRIMARY,
    PRIMARY_CONTAINER,
    SUCCESS,
    SUCCESS_CONTAINER,
    WARNING,
    WARNING_CONTAINER,
    DANGER,
    DANGER_CONTAINER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    create_badge,
    show_snackbar,
)


class ReviewView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        storage: StorageManager,
        list_id: str,
        on_finish: Callable[[], None],
    ):
        super().__init__()
        self.app_page = page
        self.storage = storage
        self.list_id = list_id
        self.on_finish = on_finish

        self.expand = True
        self.padding = ft.Padding.all(28)

        # Load list
        self.item_list = self.storage.get_by_id(list_id)
        if not self.item_list or not self.item_list.items:
            self.content = ft.Text("Lista não encontrada ou sem itens.", color=DANGER)
            return

        # Session state
        self.current_index = 0
        self.is_revealed = False
        self.items_correct = 0
        self.is_completed = False
        self.total_items = len(self.item_list.items)

        # Hook keyboard handler
        self._prev_on_keyboard_event = self.app_page.on_keyboard_event
        self.app_page.on_keyboard_event = self._handle_keyboard_event

        self.content_container = ft.Container(expand=True)
        self.content = self.content_container
        self._render_current_state()

    def cleanup(self) -> None:
        """Restaura o listener original de teclado ao sair da tela."""
        self.app_page.on_keyboard_event = self._prev_on_keyboard_event

    def _render_current_state(self) -> None:
        if self.is_completed:
            self.content_container.content = self._build_final_evaluation_state()
        elif self.is_revealed:
            self.content_container.content = self._build_revealed_item_state()
        else:
            self.content_container.content = self._build_hidden_item_state()

        try:
            if self.page:
                self.update()
        except RuntimeError:
            pass

    def _handle_keyboard_event(self, e: ft.KeyboardEvent) -> None:
        key = e.key.upper() if e.key else ""

        if self.is_completed:
            if key == "1":
                self._apply_final_grade(1)
            elif key == "2":
                self._apply_final_grade(3)
            elif key == "3":
                self._apply_final_grade(4)
            elif key == "4":
                self._apply_final_grade(5)
            return

        if not self.is_revealed:
            if key in (" ", "ENTER", "SPACE"):
                self._reveal_item()
        else:
            if key in ("1", "N", "E"):
                self._grade_single_item(correct=False)
            elif key in ("2", "Y", "A", "ENTER", "SPACE"):
                self._grade_single_item(correct=True)

    def _reveal_item(self) -> None:
        self.is_revealed = True
        self._render_current_state()

    def _grade_single_item(self, correct: bool) -> None:
        if correct:
            self.items_correct += 1

        self.current_index += 1
        self.is_revealed = False

        if self.current_index >= self.total_items:
            self.is_completed = True

        self._render_current_state()

    def _build_header(self) -> ft.Row:
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_color=TEXT_SECONDARY,
                            tooltip="Sair da revisão",
                            on_click=lambda _: self._confirm_exit(),
                        ),
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(self.item_list.title, size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                ft.Text(
                                    self.item_list.description or "Sequência ordenada",
                                    size=12,
                                    color=TEXT_MUTED,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                        ),
                    ],
                ),
                create_badge(
                    f"Item {self.current_index + 1} de {self.total_items}",
                    PRIMARY_CONTAINER,
                    PRIMARY,
                ),
            ],
        )

    def _build_progress_bar(self) -> ft.ProgressBar:
        progress_val = (self.current_index) / self.total_items if self.total_items > 0 else 0
        return ft.ProgressBar(
            value=progress_val,
            color=PRIMARY,
            bgcolor=SURFACE_CARD,
            height=6,
            border_radius=ft.BorderRadius.all(3),
        )

    # -------------------------------------------------------------
    # ESTADO 1: ITEM OCULTO
    # -------------------------------------------------------------
    def _build_hidden_item_state(self) -> ft.Control:
        pos_number = self.current_index + 1

        card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=ft.BorderRadius.all(16),
            padding=ft.Padding.all(40),
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    create_badge(f"Posição #{pos_number}", PRIMARY_CONTAINER, PRIMARY),
                    ft.Icon(ft.Icons.VISIBILITY_OFF_ROUNDED, size=50, color=TEXT_MUTED),
                    ft.Text(
                        "[ ? ? ? ? ? ? ? ? ]",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_MUTED,
                    ),
                    ft.Text(
                        "Recite mentalmente ou em voz alta o item desta posição",
                        size=14,
                        color=TEXT_SECONDARY,
                    ),
                ],
            ),
        )

        show_btn = ft.FilledButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.VISIBILITY, size=20),
                    ft.Text("Mostrar Item", size=16, weight=ft.FontWeight.BOLD),
                ],
            ),
            style=ft.ButtonStyle(
                bgcolor=PRIMARY,
                color=TEXT_PRIMARY,
                padding=ft.Padding.symmetric(horizontal=36, vertical=18),
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=lambda _: self._reveal_item(),
        )

        footer_hint = ft.Text(
            "Dica: você também pode pressionar a tecla [Espaço] para revelar",
            size=12,
            color=TEXT_MUTED,
            text_align=ft.TextAlign.CENTER,
        )

        return ft.Column(
            spacing=20,
            alignment=ft.MainAxisAlignment.START,
            controls=[
                self._build_header(),
                self._build_progress_bar(),
                ft.Container(height=10),
                card,
                ft.Container(height=10),
                ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[show_btn]),
                ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[footer_hint]),
            ],
        )

    # -------------------------------------------------------------
    # ESTADO 2: ITEM REVELADO (COM ACERTEI / ERREI)
    # -------------------------------------------------------------
    def _build_revealed_item_state(self) -> ft.Control:
        pos_number = self.current_index + 1
        item_text = self.item_list.items[self.current_index]

        card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.Border.all(1, PRIMARY),
            border_radius=ft.BorderRadius.all(16),
            padding=ft.Padding.all(40),
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=18,
                controls=[
                    create_badge(f"Posição #{pos_number}", PRIMARY_CONTAINER, PRIMARY),
                    ft.Text(
                        item_text,
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=TEXT_PRIMARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Você lembrou corretamente deste item nesta posição?",
                        size=14,
                        color=TEXT_SECONDARY,
                    ),
                ],
            ),
        )

        errei_btn = ft.FilledButton(
            content=ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.CLOSE, size=18, color=TEXT_PRIMARY),
                    ft.Text("Errei (1)", size=15, weight=ft.FontWeight.BOLD),
                ],
            ),
            style=ft.ButtonStyle(
                bgcolor=DANGER,
                color=TEXT_PRIMARY,
                padding=ft.Padding.symmetric(horizontal=28, vertical=16),
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=lambda _: self._grade_single_item(correct=False),
        )

        acertei_btn = ft.FilledButton(
            content=ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.CHECK, size=18, color=TEXT_PRIMARY),
                    ft.Text("Acertei (2)", size=15, weight=ft.FontWeight.BOLD),
                ],
            ),
            style=ft.ButtonStyle(
                bgcolor=SUCCESS,
                color=TEXT_PRIMARY,
                padding=ft.Padding.symmetric(horizontal=28, vertical=16),
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=lambda _: self._grade_single_item(correct=True),
        )

        footer_hint = ft.Text(
            "Atalhos de teclado: Tecla [1] para Errei, Tecla [2] para Acertei",
            size=12,
            color=TEXT_MUTED,
            text_align=ft.TextAlign.CENTER,
        )

        return ft.Column(
            spacing=20,
            alignment=ft.MainAxisAlignment.START,
            controls=[
                self._build_header(),
                self._build_progress_bar(),
                ft.Container(height=10),
                card,
                ft.Container(height=10),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                    controls=[errei_btn, acertei_btn],
                ),
                ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[footer_hint]),
            ],
        )

    # -------------------------------------------------------------
    # ESTADO 3: AVALIAÇÃO GERAL DA SESSÃO (ANKI STYLE)
    # -------------------------------------------------------------
    def _build_final_evaluation_state(self) -> ft.Control:
        # Previews of intervals
        previews = preview_intervals(
            self.item_list.srs.repetitions,
            self.item_list.srs.interval_days,
            self.item_list.srs.ease_factor,
        )

        pct = round((self.items_correct / self.total_items) * 100) if self.total_items > 0 else 0

        stat_card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=ft.BorderRadius.all(12),
            padding=ft.Padding.all(20),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.INSIGHTS, color=PRIMARY, size=20),
                                    ft.Text(
                                        "Resumo da Sessão (Informativo)",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_PRIMARY,
                                    ),
                                ],
                            ),
                            create_badge(f"{self.items_correct} de {self.total_items} corretos ({pct}%)", PRIMARY_CONTAINER, PRIMARY),
                        ],
                    ),
                    ft.Text(
                        "Este resumo serve como referência para você. A nota geral que você escolher abaixo é o que alimentará o algoritmo de repetição espaçada.",
                        size=13,
                        color=TEXT_MUTED,
                    ),
                ],
            ),
        )

        def make_grade_button(label: str, subtitle: str, interval_days: int, grade: int, color: str, key_num: str):
            interval_text = f"{interval_days} dia" if interval_days == 1 else f"{interval_days} dias"
            return ft.Container(
                expand=True,
                bgcolor=SURFACE_COLOR,
                border=ft.Border.all(1, BORDER_COLOR),
                border_radius=ft.BorderRadius.all(12),
                padding=ft.Padding.all(16),
                ink=True,
                on_click=lambda _: self._apply_final_grade(grade),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                    controls=[
                        ft.Text(f"{label} ({key_num})", size=16, weight=ft.FontWeight.BOLD, color=color),
                        ft.Text(interval_text, size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text(subtitle, size=11, color=TEXT_MUTED),
                    ],
                ),
            )

        btn_errei = make_grade_button("Errei", "Recomeçar ciclo", previews["errei"], 1, DANGER, "1")
        btn_dificil = make_grade_button("Difícil", "Com esforço", previews["dificil"], 3, WARNING, "2")
        btn_bom = make_grade_button("Bom", "Lembrei bem", previews["bom"], 4, SUCCESS, "3")
        btn_facil = make_grade_button("Fácil", "Instantâneo", previews["facil"], 5, PRIMARY, "4")

        buttons_row = ft.Row(
            spacing=14,
            controls=[btn_errei, btn_dificil, btn_bom, btn_facil],
        )

        return ft.Column(
            spacing=24,
            alignment=ft.MainAxisAlignment.START,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.Icon(ft.Icons.CELEBRATION_ROUNDED, color=PRIMARY, size=32),
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Revisão da Lista Concluída!", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                ft.Text(f"Você passou por todos os itens de '{self.item_list.title}'", size=13, color=TEXT_MUTED),
                            ],
                        ),
                    ],
                ),
                stat_card,
                ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text(
                            "Como foi a sua facilidade geral para recordar a sequência completa?",
                            size=15,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_PRIMARY,
                        ),
                        buttons_row,
                    ],
                ),
            ],
        )

    def _apply_final_grade(self, grade: int) -> None:
        # Run SM-2 scheduling
        srs_result = calculate_next_review(
            repetitions=self.item_list.srs.repetitions,
            interval_days=self.item_list.srs.interval_days,
            ease_factor=self.item_list.srs.ease_factor,
            grade=grade,
            base_date=date.today(),
        )

        # Update SRS state on list
        self.item_list.srs.repetitions = srs_result.repetitions
        self.item_list.srs.interval_days = srs_result.interval_days
        self.item_list.srs.ease_factor = srs_result.ease_factor
        self.item_list.srs.next_review = srs_result.next_review.isoformat()
        self.item_list.srs.last_reviewed = datetime.now().isoformat()

        # Add record to review history (items_correct is pure informative history)
        record = ReviewRecord(
            date=datetime.now().isoformat(),
            grade=grade,
            items_correct=self.items_correct,
            items_total=self.total_items,
            interval_days=srs_result.interval_days,
            ease_factor=srs_result.ease_factor,
        )
        self.item_list.review_history.append(record)

        # Save to JSON
        self.storage.save_list(self.item_list)

        # Cleanup keyboard listener and exit
        self.cleanup()

        grade_names = {1: "Errei", 3: "Difícil", 4: "Bom", 5: "Fácil"}
        days_str = f"{srs_result.interval_days} dia" if srs_result.interval_days == 1 else f"{srs_result.interval_days} dias"
        show_snackbar(
            self.app_page,
            f"Revisão salva com nota '{grade_names.get(grade)}'. Próxima revisão em {days_str} ({srs_result.next_review.isoformat()}).",
            bgcolor=SUCCESS,
        )

        self.on_finish()

    def _confirm_exit(self) -> None:
        def do_exit(_):
            self.app_page.pop_dialog()
            self.cleanup()
            self.on_finish()

        def cancel(_):
            self.app_page.pop_dialog()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Interromper revisão?"),
            content=ft.Text("Se você sair agora, o progresso desta sessão de revisão não será salvo."),
            actions=[
                ft.TextButton("Continuar revisando", on_click=cancel),
                ft.FilledButton("Sair", bgcolor=DANGER, on_click=do_exit),
            ],
        )
        self.app_page.show_dialog(dialog)
