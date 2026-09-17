"""View do Dashboard do MemoList: visão geral, estatísticas e listas pendentes."""

from typing import Callable
import flet as ft
from memolist.models import ItemList
from memolist.storage import StorageManager
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
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    create_badge,
    show_snackbar,
)


class DashboardView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        storage: StorageManager,
        on_review: Callable[[str], None],
        on_create: Callable[[], None],
        on_edit: Callable[[str], None],
    ):
        super().__init__()
        self.app_page = page
        self.storage = storage
        self.on_review = on_review
        self.on_create = on_create
        self.on_edit = on_edit

        self.expand = True
        self.padding = ft.Padding.all(28)
        self.content = self._build_content()

    def refresh_data(self) -> None:
        self.content = self._build_content()
        self.update()

    def _build_content(self) -> ft.Control:
        stats = self.storage.get_stats()
        all_lists = self.storage.load_all()
        due_lists = [l for l in all_lists if l.is_due]

        # Top Bar
        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.Icons.AUTO_STORIES_ROUNDED, color=PRIMARY, size=32),
                                ft.Text(
                                    "MemoList",
                                    size=26,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_PRIMARY,
                                ),
                            ],
                        ),
                        ft.Text(
                            "Repetição espaçada para sequências e listas ordenadas",
                            size=13,
                            color=TEXT_MUTED,
                        ),
                    ],
                ),
                ft.FilledButton(
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.ADD, size=18, color=TEXT_PRIMARY),
                            ft.Text("Nova Lista", weight=ft.FontWeight.W_600),
                        ],
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY,
                        color=TEXT_PRIMARY,
                        padding=ft.Padding.symmetric(horizontal=18, vertical=12),
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=lambda _: self.on_create(),
                ),
            ],
        )

        # KPI Stats Cards
        stat_cards = ft.Row(
            spacing=16,
            controls=[
                self._build_kpi_card(
                    title="Devidas Hoje",
                    value=str(stats["due_lists"]),
                    icon=ft.Icons.ALARM,
                    color=WARNING if stats["due_lists"] > 0 else SUCCESS,
                    bg_color=WARNING_CONTAINER if stats["due_lists"] > 0 else SUCCESS_CONTAINER,
                ),
                self._build_kpi_card(
                    title="Total de Listas",
                    value=str(stats["total_lists"]),
                    icon=ft.Icons.FORMAT_LIST_NUMBERED,
                    color=PRIMARY,
                    bg_color=PRIMARY_CONTAINER,
                ),
                self._build_kpi_card(
                    title="Itens Cadastrados",
                    value=str(stats["total_items"]),
                    icon=ft.Icons.CHECKLIST,
                    color="#38BDF8",
                    bg_color="#0C4A6E",
                ),
            ],
        )

        # Due Lists Section
        due_section = self._build_due_section(due_lists)

        # All Lists Section
        all_section = self._build_all_lists_section(all_lists)

        return ft.ListView(
            spacing=26,
            expand=True,
            controls=[
                header,
                stat_cards,
                ft.Divider(color=BORDER_COLOR, height=1),
                due_section,
                ft.Divider(color=BORDER_COLOR, height=1),
                all_section,
            ],
        )

    def _build_kpi_card(
        self, title: str, value: str, icon: str, color: str, bg_color: str
    ) -> ft.Container:
        return ft.Container(
            expand=True,
            bgcolor=SURFACE_COLOR,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=ft.BorderRadius.all(12),
            padding=ft.Padding.all(18),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(title, size=12, color=TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                            ft.Text(value, size=28, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                    ft.Container(
                        bgcolor=bg_color,
                        padding=ft.Padding.all(10),
                        border_radius=ft.BorderRadius.all(10),
                        content=ft.Icon(icon, color=color, size=24),
                    ),
                ],
            ),
        )

    def _build_due_section(self, due_lists: list[ItemList]) -> ft.Column:
        header = ft.Row(
            spacing=10,
            controls=[
                ft.Icon(ft.Icons.PLAY_CIRCLE_OUTLINED, color=WARNING if due_lists else SUCCESS, size=20),
                ft.Text("Prontas para Revisão Hoje", size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                create_badge(f"{len(due_lists)} pendentes", WARNING_CONTAINER if due_lists else SUCCESS_CONTAINER, WARNING if due_lists else SUCCESS),
            ],
        )

        if not due_lists:
            content = ft.Container(
                bgcolor=SURFACE_COLOR,
                border=ft.Border.all(1, BORDER_COLOR),
                border_radius=ft.BorderRadius.all(12),
                padding=ft.Padding.all(24),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=12,
                    controls=[
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=SUCCESS, size=24),
                        ft.Text("Parabéns! Todas as listas estão em dia para hoje.", size=14, color=TEXT_SECONDARY),
                    ],
                ),
            )
        else:
            cards = [self._build_due_card(l) for l in due_lists]
            content = ft.Column(spacing=12, controls=cards)

        return ft.Column(spacing=12, controls=[header, content])

    def _build_due_card(self, item_list: ItemList) -> ft.Container:
        return ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.Border.all(1, PRIMARY),
            border_radius=ft.BorderRadius.all(12),
            padding=ft.Padding.all(18),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=6,
                        expand=True,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Text(item_list.title, size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                    create_badge(f"{item_list.item_count} itens", PRIMARY_CONTAINER, PRIMARY),
                                    create_badge(item_list.status_display, WARNING_CONTAINER, WARNING),
                                ],
                            ),
                            ft.Text(
                                item_list.description or "Sem descrição",
                                size=13,
                                color=TEXT_MUTED,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                    ft.FilledButton(
                        content=ft.Row(
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, size=18),
                                ft.Text("Revisar Agora", weight=ft.FontWeight.W_600),
                            ],
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=PRIMARY,
                            color=TEXT_PRIMARY,
                            padding=ft.Padding.symmetric(horizontal=18, vertical=12),
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        on_click=lambda _, lid=item_list.id: self.on_review(lid),
                    ),
                ],
            ),
        )

    def _build_all_lists_section(self, all_lists: list[ItemList]) -> ft.Column:
        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.FOLDER_SPECIAL_OUTLINED, color=TEXT_SECONDARY, size=20),
                        ft.Text("Todas as Listas", size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ],
                ),
            ],
        )

        if not all_lists:
            content = ft.Container(
                bgcolor=SURFACE_COLOR,
                border=ft.Border.all(1, BORDER_COLOR),
                border_radius=ft.BorderRadius.all(12),
                padding=ft.Padding.all(32),
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=40, color=TEXT_MUTED),
                        ft.Text("Nenhuma lista cadastrada ainda.", size=15, color=TEXT_SECONDARY),
                        ft.Text("Clique em 'Nova Lista' para cadastrar sua primeira sequência!", size=13, color=TEXT_MUTED),
                    ],
                ),
            )
        else:
            cards = [self._build_list_row(l) for l in all_lists]
            content = ft.Column(spacing=10, controls=cards)

        return ft.Column(spacing=12, controls=[header, content])

    def _build_list_row(self, item_list: ItemList) -> ft.Container:
        # Status color
        if item_list.is_due:
            status_bg = WARNING_CONTAINER
            status_fg = WARNING
        elif item_list.srs.repetitions == 0 and item_list.srs.last_reviewed is None:
            status_bg = PRIMARY_CONTAINER
            status_fg = PRIMARY
        else:
            status_bg = SUCCESS_CONTAINER
            status_fg = SUCCESS

        return ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=ft.BorderRadius.all(10),
            padding=ft.Padding.symmetric(horizontal=16, vertical=12),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=12,
                        expand=True,
                        controls=[
                            ft.Icon(ft.Icons.LIST_ALT_ROUNDED, color=TEXT_SECONDARY, size=22),
                            ft.Column(
                                spacing=3,
                                expand=True,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Text(item_list.title, size=15, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                                            create_badge(f"{item_list.item_count} itens", SURFACE_CARD, TEXT_SECONDARY),
                                            create_badge(item_list.status_display, status_bg, status_fg),
                                            create_badge(f"EF {item_list.srs.ease_factor}", SURFACE_CARD, TEXT_MUTED),
                                        ],
                                    ),
                                    ft.Text(
                                        item_list.description or "Sem descrição",
                                        size=12,
                                        color=TEXT_MUTED,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=4,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.PLAY_ARROW_ROUNDED,
                                icon_color=PRIMARY,
                                tooltip="Revisar lista",
                                on_click=lambda _, lid=item_list.id: self.on_review(lid),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                icon_color=TEXT_SECONDARY,
                                tooltip="Editar lista e itens",
                                on_click=lambda _, lid=item_list.id: self.on_edit(lid),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=DANGER,
                                tooltip="Excluir lista",
                                on_click=lambda _, lid=item_list.id: self._confirm_delete(item_list),
                            ),
                        ],
                    ),
                ],
            ),
        )

    def _confirm_delete(self, item_list: ItemList) -> None:
        def do_delete(_):
            self.storage.delete_list(item_list.id)
            self.app_page.pop_dialog()
            self.refresh_data()
            show_snackbar(self.app_page, f"Lista '{item_list.title}' excluída com sucesso.")

        def cancel(_):
            self.app_page.pop_dialog()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Excluir lista?"),
            content=ft.Text(f"Tem certeza que deseja excluir a lista '{item_list.title}'? Esta ação não pode ser desfeita."),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel),
                ft.FilledButton("Excluir", bgcolor=DANGER, on_click=do_delete),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.app_page.show_dialog(dialog)
