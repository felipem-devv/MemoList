"""Configurações de tema, paleta de cores e estilos para o MemoList."""

import flet as ft

# Cores Principais (Tema Escuro Moderno - Slate / Indigo / Emerald)
BG_COLOR = "#0B0F19"           # Fundo profundo
SURFACE_COLOR = "#151D2F"      # Superfície dos cards
SURFACE_CARD = "#1E293B"       # Card interno
SURFACE_HOVER = "#27354E"      # Hover state
BORDER_COLOR = "#2A374E"       # Bordas sutis

PRIMARY = "#6366F1"            # Indigo vibrante
PRIMARY_CONTAINER = "#312E81"  # Indigo escuro para badges
SUCCESS = "#10B981"            # Emerald (Acertei / Fácil)
SUCCESS_CONTAINER = "#064E3B"
WARNING = "#F59E0B"            # Amber (Médio / Difícil)
WARNING_CONTAINER = "#78350F"
DANGER = "#EF4444"             # Rose/Red (Errei)
DANGER_CONTAINER = "#7F1D1D"

TEXT_PRIMARY = "#F8FAFC"
TEXT_SECONDARY = "#94A3B8"
TEXT_MUTED = "#64748B"


def setup_theme(page: ft.Page) -> None:
    page.title = "MemoList • SRS para Listas Ordenadas"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG_COLOR
    page.padding = 0
    if hasattr(page, "window") and page.window is not None:
        try:
            page.window.min_width = 850
            page.window.min_height = 600
            page.window.width = 1100
            page.window.height = 760
        except Exception:
            pass


def create_badge(text: str, bg_color: str, text_color: str = TEXT_PRIMARY) -> ft.Container:
    return ft.Container(
        content=ft.Text(text, size=11, weight=ft.FontWeight.W_600, color=text_color),
        bgcolor=bg_color,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        border_radius=ft.BorderRadius.all(12),
    )


def show_snackbar(page: ft.Page, message: str, bgcolor: str = SURFACE_CARD) -> None:
    try:
        page.show_dialog(ft.SnackBar(content=ft.Text(message), bgcolor=bgcolor))
    except Exception:
        pass

