"""MemoList - Sistema de Repetição Espaçada para Listas Ordenadas.

Ponto de entrada principal da aplicação Flet desktop.
"""

import flet as ft
from memolist.storage import StorageManager
from memolist.ui.theme import setup_theme
from memolist.ui.views.dashboard_view import DashboardView
from memolist.ui.views.list_edit_view import ListEditView
from memolist.ui.views.review_view import ReviewView


def main(page: ft.Page) -> None:
    # 1. Configurar Tema e Janela
    setup_theme(page)

    # 2. Inicializar Storage
    storage = StorageManager()

    # 3. Container Principal
    main_container = ft.Container(expand=True)
    page.add(main_container)

    current_review_view: ReviewView | None = None

    def navigate_to(view_name: str, **kwargs) -> None:
        nonlocal current_review_view

        # Limpar handlers anteriores caso esteja saindo da tela de revisão
        if current_review_view is not None:
            current_review_view.cleanup()
            current_review_view = None

        if view_name == "dashboard":
            view = DashboardView(
                page=page,
                storage=storage,
                on_review=lambda lid: navigate_to("review", list_id=lid),
                on_create=lambda: navigate_to("create"),
                on_edit=lambda lid: navigate_to("edit", list_id=lid),
            )
            main_container.content = view
            page.update()

        elif view_name == "create":
            view = ListEditView(
                page=page,
                storage=storage,
                list_id=None,
                on_back=lambda: navigate_to("dashboard"),
            )
            main_container.content = view
            page.update()

        elif view_name == "edit":
            list_id = kwargs.get("list_id")
            view = ListEditView(
                page=page,
                storage=storage,
                list_id=list_id,
                on_back=lambda: navigate_to("dashboard"),
            )
            main_container.content = view
            page.update()

        elif view_name == "review":
            list_id = kwargs.get("list_id", "")
            review_view = ReviewView(
                page=page,
                storage=storage,
                list_id=list_id,
                on_finish=lambda: navigate_to("dashboard"),
            )
            current_review_view = review_view
            main_container.content = review_view
            page.update()

    # Iniciar no Dashboard
    navigate_to("dashboard")


if __name__ == "__main__":
    ft.run(main)
