"""View de Criação e Edição de Listas com ordenação e gerenciamento de itens."""

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
    DANGER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    create_badge,
    show_snackbar,
)


class ListEditView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        storage: StorageManager,
        list_id: str | None,
        on_back: Callable[[], None],
    ):
        super().__init__()
        self.app_page = page
        self.storage = storage
        self.list_id = list_id
        self.on_back = on_back

        self.expand = True
        self.padding = ft.Padding.all(28)

        # Load existing list or create empty
        if self.list_id:
            existing = self.storage.get_by_id(self.list_id)
            if existing:
                self.item_list = existing
                self.is_new = False
            else:
                self.item_list = ItemList()
                self.is_new = True
        else:
            self.item_list = ItemList()
            self.is_new = True

        self.items_copy = list(self.item_list.items)

        # UI Controls
        self.title_field = ft.TextField(
            label="Título da Lista",
            hint_text="Ex: Linha 2 - Verde (Metrô SP)",
            value=self.item_list.title,
            border_color=BORDER_COLOR,
            focused_border_color=PRIMARY,
            text_size=15,
            expand=True,
        )

        self.desc_field = ft.TextField(
            label="Descrição / Dica de Contexto",
            hint_text="Ex: Sequência das estações sentido Vila Madalena -> Vila Prudente",
            value=self.item_list.description,
            border_color=BORDER_COLOR,
            focused_border_color=PRIMARY,
            text_size=14,
            multiline=True,
            min_lines=1,
            max_lines=3,
        )

        self.new_item_field = ft.TextField(
            hint_text="Digite um novo item e tecle Enter...",
            border_color=BORDER_COLOR,
            focused_border_color=PRIMARY,
            text_size=14,
            expand=True,
            on_submit=self._add_single_item,
        )

        self.items_column = ft.Column(spacing=8)
        self._refresh_items_list()

        self.content = self._build_layout()

    def _build_layout(self) -> ft.Control:
        header = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=TEXT_SECONDARY,
                            tooltip="Voltar ao Dashboard",
                            on_click=lambda _: self.on_back(),
                        ),
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(
                                    "Criar Nova Lista" if self.is_new else "Editar Lista",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=TEXT_PRIMARY,
                                ),
                                ft.Text(
                                    "Defina o nome e organize os itens na ordem correta de recordação",
                                    size=13,
                                    color=TEXT_MUTED,
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.OutlinedButton(
                            "Cancelar",
                            style=ft.ButtonStyle(
                                color=TEXT_SECONDARY,
                                side=ft.BorderSide(1, BORDER_COLOR),
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            on_click=lambda _: self.on_back(),
                        ),
                        ft.FilledButton(
                            content=ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.SAVE, size=18),
                                    ft.Text("Salvar Lista", weight=ft.FontWeight.W_600),
                                ],
                            ),
                            style=ft.ButtonStyle(
                                bgcolor=PRIMARY,
                                color=TEXT_PRIMARY,
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            on_click=self._save_list,
                        ),
                    ],
                ),
            ],
        )

        # Meta section
        meta_card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=ft.BorderRadius.all(12),
            padding=ft.Padding.all(20),
            content=ft.Column(
                spacing=16,
                controls=[
                    self.title_field,
                    self.desc_field,
                ],
            ),
        )

        # Item adder section
        adder_card = ft.Container(
            bgcolor=SURFACE_COLOR,
            border=ft.Border.all(1, BORDER_COLOR),
            border_radius=ft.BorderRadius.all(12),
            padding=ft.Padding.all(20),
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.FORMAT_LIST_NUMBERED, color=PRIMARY, size=20),
                                    ft.Text("Itens da Sequência", size=16, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                ],
                            ),
                            ft.TextButton(
                                "Adicionar Vários (Em Lote)",
                                icon=ft.Icons.PLAYLIST_ADD,
                                on_click=self._open_bulk_add_dialog,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=10,
                        controls=[
                            self.new_item_field,
                            ft.FilledButton(
                                content=ft.Row(
                                    spacing=4,
                                    controls=[
                                        ft.Icon(ft.Icons.ADD, size=18),
                                        ft.Text("Adicionar"),
                                    ],
                                ),
                                style=ft.ButtonStyle(
                                    bgcolor=PRIMARY,
                                    color=TEXT_PRIMARY,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=self._add_single_item,
                            ),
                        ],
                    ),
                    ft.Divider(color=BORDER_COLOR, height=1),
                    self.items_column,
                ],
            ),
        )

        return ft.ListView(
            spacing=20,
            expand=True,
            controls=[
                header,
                meta_card,
                adder_card,
            ],
        )

    def _refresh_items_list(self) -> None:
        self.items_column.controls.clear()

        if not self.items_copy:
            self.items_column.controls.append(
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding.all(24),
                    content=ft.Text(
                        "Nenhum item adicionado ainda. Digite acima ou use a adição em lote.",
                        color=TEXT_MUTED,
                        size=13,
                    ),
                )
            )
            return

        for idx, item_text in enumerate(self.items_copy):
            is_first = idx == 0
            is_last = idx == len(self.items_copy) - 1

            row = ft.Container(
                bgcolor=SURFACE_CARD,
                border=ft.Border.all(1, BORDER_COLOR),
                border_radius=ft.BorderRadius.all(8),
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=12,
                            expand=True,
                            controls=[
                                create_badge(f"#{idx + 1}", PRIMARY_CONTAINER, PRIMARY),
                                ft.Text(item_text, size=14, color=TEXT_PRIMARY, weight=ft.FontWeight.W_500),
                            ],
                        ),
                        ft.Row(
                            spacing=2,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_UPWARD,
                                    icon_size=18,
                                    icon_color=TEXT_MUTED if is_first else TEXT_SECONDARY,
                                    disabled=is_first,
                                    tooltip="Mover para cima",
                                    on_click=lambda _, i=idx: self._move_item(i, -1),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_DOWNWARD,
                                    icon_size=18,
                                    icon_color=TEXT_MUTED if is_last else TEXT_SECONDARY,
                                    disabled=is_last,
                                    tooltip="Mover para baixo",
                                    on_click=lambda _, i=idx: self._move_item(i, 1),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_size=18,
                                    icon_color=DANGER,
                                    tooltip="Remover item",
                                    on_click=lambda _, i=idx: self._delete_item(i),
                                ),
                            ],
                        ),
                    ],
                ),
            )
            self.items_column.controls.append(row)

    def _add_single_item(self, _) -> None:
        text = self.new_item_field.value.strip() if self.new_item_field.value else ""
        if not text:
            return
        self.items_copy.append(text)
        self.new_item_field.value = ""
        self._refresh_items_list()
        self.update()
        self.new_item_field.focus()

    def _move_item(self, index: int, offset: int) -> None:
        target = index + offset
        if 0 <= target < len(self.items_copy):
            self.items_copy[index], self.items_copy[target] = self.items_copy[target], self.items_copy[index]
            self._refresh_items_list()
            self.update()

    def _delete_item(self, index: int) -> None:
        if 0 <= index < len(self.items_copy):
            del self.items_copy[index]
            self._refresh_items_list()
            self.update()

    def _open_bulk_add_dialog(self, _) -> None:
        bulk_text_field = ft.TextField(
            hint_text="Cole os itens aqui, um por linha:\nEstação 1\nEstação 2\nEstação 3",
            multiline=True,
            min_lines=6,
            max_lines=12,
            border_color=BORDER_COLOR,
            focused_border_color=PRIMARY,
        )

        def add_bulk(_):
            lines = [line.strip() for line in (bulk_text_field.value or "").splitlines() if line.strip()]
            if lines:
                self.items_copy.extend(lines)
                self._refresh_items_list()
                self.update()
            self.app_page.pop_dialog()

        def cancel(_):
            self.app_page.pop_dialog()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Adicionar Itens em Lote"),
            content=ft.Container(
                width=450,
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    controls=[
                        ft.Text("Insira múltiplos itens de uma vez. Cada linha será um item na ordem informada.", size=13, color=TEXT_SECONDARY),
                        bulk_text_field,
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel),
                ft.FilledButton("Adicionar Todos", bgcolor=PRIMARY, on_click=add_bulk),
            ],
        )
        self.app_page.show_dialog(dialog)

    def _save_list(self, _) -> None:
        title = self.title_field.value.strip() if self.title_field.value else ""
        if not title:
            show_snackbar(self.app_page, "Por favor, preencha o título da lista.", bgcolor=DANGER)
            return

        if not self.items_copy:
            show_snackbar(self.app_page, "Adicione pelo menos um item à lista antes de salvar.", bgcolor=DANGER)
            return

        self.item_list.title = title
        self.item_list.description = (self.desc_field.value or "").strip()
        self.item_list.items = list(self.items_copy)

        self.storage.save_list(self.item_list)
        show_snackbar(self.app_page, f"Lista '{self.item_list.title}' salva com sucesso!", bgcolor=SUCCESS)
        self.on_back()
