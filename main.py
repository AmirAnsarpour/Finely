import flet as ft
import json
import os
from datetime import datetime
from collections import defaultdict
import calendar

# --- Color Palette (OpenWrt-inspired) ---
colors = {
    "primary": "#0078D7",   # Blue
    "background": "#F5F5F5",  # Light gray
    "card": "#FFFFFF",      # White
    "text": "#2C2C2C",      # Dark text
    "text_light": "#6E6E6E", # Muted
    "accent": "#00A86B",    # Green for income
    "danger": "#D93025",    # Red for expenses
    "border": "#D0D0D0",    # Light border
    "hover_bg": "#F0F0F0",  # Hover background
    "header": "#0078D7",
}

# Data file
DATA_FILE = "data.json"
default_data = {
    "income": [],
    "expenses": [],
    "categories": {
        "income": ["Salary", "Freelance", "Investments", "Gifts", "Other"],
        "expenses": ["Food", "Transport", "Utilities", "Entertainment", "Shopping", "Health", "Other"]
    }
}

# --- JSON Functions ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return default_data
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            for key in default_data:
                if key == "categories":
                    for cat_type in default_data["categories"]:
                        if cat_type not in data["categories"]:
                            data["categories"][cat_type] = default_data["categories"][cat_type]
                else:
                    if key not in data:
                        data[key] = default_data[key]
            return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return default_data

def save_data(data_to_save):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data_to_save, file, indent=4)
    except Exception as e:
        print(f"Save error: {e}")

data = load_data()
save_data(data)

# --- Main App ---
def main(page: ft.Page):
    page.title = "Finely"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = colors["background"]
    page.fonts = {
        "Inter": "fonts/Inter-Regular.ttf",
        "Inter Bold": "fonts/Inter-Bold.ttf",
    }
    page.window_width = 1000
    page.window_height = 700
    page.window_min_width = 800
    page.window_min_height = 600

    # --- Utility Functions ---
    def create_text_field(label, color, width=300):
        return ft.TextField(
            label=label,
            border_color=colors["border"],
            focused_border_color=color,
            label_style=ft.TextStyle(color=colors["text_light"], size=13),
            text_style=ft.TextStyle(color=colors["text"], size=14),
            border_width=1,
            filled=False,
            height=48,
            width=width,
            content_padding=10,
            cursor_color=color,
            color=colors["text"]
        )

    def create_dropdown(label, options, color, width=300):
        return ft.Dropdown(
            label=label,
            options=[ft.dropdown.Option(opt) for opt in options],
            border_color=colors["border"],
            focused_border_color=color,
            label_style=ft.TextStyle(color=colors["text_light"], size=13),
            text_style=ft.TextStyle(color=colors["text"], size=14),
            border_width=1,
            width=width,
            color=colors["text"]
        )

    def create_button(text, color, on_click):
        return ft.ElevatedButton(
            text=text,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=4),
                bgcolor=color,
                color=colors["card"],
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ),
            on_click=on_click
        )

    # --- Navigation Rail ---
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        extended=False,
        min_width=80,
        min_extended_width=180,
        group_alignment=0,
        bgcolor=colors["card"],
        elevation=1,
        destinations=[
            ft.NavigationRailDestination(icon="dashboard", selected_icon="dashboard", label="Dashboard"),
            ft.NavigationRailDestination(icon="insights", selected_icon="insights", label="Reports"),
            ft.NavigationRailDestination(icon="settings", selected_icon="settings", label="Settings"),
        ],
        leading=ft.Container(
            content=ft.Text("Finely", size=18, weight="bold", color=colors["header"], font_family="Inter Bold"),
            padding=ft.padding.only(left=16, top=16, bottom=16)
        ),
        trailing=ft.Container(
            padding=ft.padding.only(bottom=16),
            content=ft.Text("v1.0", size=12, color=colors["text_light"])
        )
    )

    content_area = ft.Container(
        padding=ft.padding.all(24),
        expand=True,
        bgcolor=colors["background"],
    )

    # --- DASHBOARD ---
    def show_dashboard():
        total_income = sum(item["amount"] for item in data["income"])
        total_expenses = sum(item["amount"] for item in data["expenses"])
        net_balance = total_income - total_expenses

        def fmt(n):
            return f"{n:,.2f}"

        def StatCard(title, value, color, icon):
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, color=color, size=20),
                        ft.Text(title, size=12, color=colors["text_light"], font_family="Inter")
                    ], spacing=6),
                    ft.Text(value, size=20, color=colors["text"], weight="bold", font_family="Inter Bold"),
                ], spacing=4),
                padding=16,
                border=ft.border.all(1, colors["border"]),
                border_radius=6,
                bgcolor=colors["card"],
                width=200,
                height=100
            )

        stats = ft.Row(
            controls=[
                StatCard("Income", fmt(total_income), colors["accent"], "trending_up"),
                StatCard("Expenses", fmt(total_expenses), colors["danger"], "trending_down"),
                StatCard("Balance", fmt(net_balance), colors["primary"], "account_balance_wallet"),
            ],
            spacing=16,
            wrap=True
        )

        # --- فرم درآمد ---
        amount_inc = create_text_field("Amount", colors["accent"], width=120)
        source_inc = create_text_field("Source", colors["accent"], width=120)
        cat_inc = create_dropdown("Category", data["categories"]["income"], colors["accent"])

        def add_income(e):
            try:
                amt = float(amount_inc.value)
                src = source_inc.value.strip()
                cat = cat_inc.value
                if not src or not cat or amt <= 0: raise ValueError("Invalid input")
                data["income"].append({
                    "amount": amt,
                    "source": src,
                    "category": cat,
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
                save_data(data)
                amount_inc.value = source_inc.value = ""; cat_inc.value = None
                page.snack_bar = ft.SnackBar(ft.Text("✅ Income added!", size=14), bgcolor=colors["accent"])
                page.snack_bar.open = True
                show_dashboard()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"❌ Error: {ex}", size=14), bgcolor=colors["danger"])
                page.snack_bar.open = True
            page.update()

        income_form = ft.Container(
            content=ft.Column([
                ft.Text("➕ Add Income", size=16, weight="bold", color=colors["text"], font_family="Inter Bold"),
                ft.Divider(height=12, color="transparent"),
                ft.Row([amount_inc, source_inc], spacing=10),
                cat_inc,
                ft.ElevatedButton("Add Income", style=ft.ButtonStyle(bgcolor=colors["accent"], color=colors["card"]), on_click=add_income, height=36)
            ], spacing=8),
            padding=16,
            border=ft.border.all(1, colors["border"]),
            border_radius=6,
            bgcolor=colors["card"],
            width=380
        )

        # --- فرم مخارج ---
        amount_exp = create_text_field("Amount", colors["danger"], width=120)
        desc_exp = create_text_field("Description", colors["danger"], width=120)
        cat_exp = create_dropdown("Category", data["categories"]["expenses"], colors["danger"])

        def add_expense(e):
            try:
                amt = float(amount_exp.value)
                desc = desc_exp.value.strip()
                cat = cat_exp.value
                if not desc or not cat or amt <= 0: raise ValueError("Invalid input")
                data["expenses"].append({
                    "amount": amt,
                    "description": desc,
                    "category": cat,
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
                save_data(data)
                amount_exp.value = desc_exp.value = ""; cat_exp.value = None
                page.snack_bar = ft.SnackBar(ft.Text("✅ Expense added!", size=14), bgcolor=colors["accent"])
                page.snack_bar.open = True
                show_dashboard()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"❌ Error: {ex}", size=14), bgcolor=colors["danger"])
                page.snack_bar.open = True
            page.update()

        expense_form = ft.Container(
            content=ft.Column([
                ft.Text("➖ Add Expense", size=16, weight="bold", color=colors["text"], font_family="Inter Bold"),
                ft.Divider(height=12, color="transparent"),
                ft.Row([amount_exp, desc_exp], spacing=10),
                cat_exp,
                ft.ElevatedButton("Add Expense", style=ft.ButtonStyle(bgcolor=colors["danger"], color=colors["card"]), on_click=add_expense, height=36)
            ], spacing=8),
            padding=16,
            border=ft.border.all(1, colors["border"]),
            border_radius=6,
            bgcolor=colors["card"],
            width=380
        )

        # --- تراکنش‌های اخیر ---
        recent_tx = []
        all_tx = (
            [{"type": "income", **tx} for tx in data["income"]] +
            [{"type": "expense", **tx} for tx in data["expenses"]]
        )
        all_tx.sort(key=lambda x: x["date"], reverse=True)

        for tx in all_tx[:5]:
            amount = f"{'+' if tx['type']=='income' else '-'} {tx['amount']:,.2f}"
            color = colors["accent"] if tx['type'] == 'income' else colors["danger"]
            label = tx.get("source", tx.get("description", "Unknown"))
            icon = "add" if tx['type'] == 'income' else "remove"

            recent_tx.append(
                ft.ListTile(
                    dense=True,
                    leading=ft.Container(
                        content=ft.Icon(icon, color=color, size=16),
                        width=28, height=28,
                        bgcolor=f"{color}10",
                        border_radius=14,
                        alignment=ft.alignment.center
                    ),
                    title=ft.Text(label, size=14, color=colors["text"], font_family="Inter"),
                    subtitle=ft.Text(f"{tx['category']} • {tx['date']}", size=12, color=colors["text_light"], font_family="Inter"),
                    trailing=ft.Text(amount, color=color, size=14, weight="bold"),
                )
            )

        recent_section = ft.Container(
            content=ft.Column([
                ft.Text("📌 Recent Transactions", size=18, weight="bold", color=colors["text"], font_family="Inter Bold"),
                ft.Divider(height=1, color=colors["border"]),
                *recent_tx
            ]),
            border=ft.border.all(1, colors["border"]),
            border_radius=6,
            bgcolor=colors["card"],
            padding=12,
            margin=ft.margin.only(top=20)
        )

        # --- نمایش نهایی داشبورد ---
        content_area.content = ft.Column([
            ft.Text("Dashboard", size=24, weight="bold", color=colors["text"], font_family="Inter Bold"),
            ft.Divider(height=24, color="transparent"),
            stats,
            ft.Row([income_form, expense_form], spacing=20, wrap=True),
            recent_section
        ], scroll=ft.ScrollMode.HIDDEN, spacing=20, expand=True)
        page.update()

    # --- REPORTS ---
    def show_reports():
        monthly = defaultdict(lambda: {"income": 0.0, "expenses": 0.0})
        for inc in data["income"]: monthly[inc["date"][:7]]["income"] += inc["amount"]
        for exp in data["expenses"]: monthly[exp["date"][:7]]["expenses"] += exp["amount"]

        if not monthly:
            content_area.content = ft.Container(
                content=ft.Text("No data available for reports.", size=16, color=colors["text_light"], font_family="Inter"),
                alignment=ft.alignment.center,
                padding=20
            )
            return

        max_val = max(max(m["income"], m["expenses"]) for m in monthly.values())

        monthly_charts = []
        for month_year in sorted(monthly.keys(), reverse=True):
            m_data = monthly[month_year]
            year, mon = month_year.split("-")
            month_name = f"{calendar.month_abbr[int(mon)]} {year}"
            inc_width = (m_data["income"] / max_val) * 200 if max_val > 0 else 0
            exp_width = (m_data["expenses"] / max_val) * 200 if max_val > 0 else 0

            monthly_charts.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(month_name, size=14, weight="bold", color=colors["text"], font_family="Inter"),
                        ft.Row([
                            ft.Container(bgcolor=colors["accent"], width=inc_width, height=12, border_radius=6),
                            ft.Text(f"{m_data['income']:,.2f}", size=12, color=colors["text_light"], font_family="Inter")
                        ]),
                        ft.Row([
                            ft.Container(bgcolor=colors["danger"], width=exp_width, height=12, border_radius=6),
                            ft.Text(f"{m_data['expenses']:,.2f}", size=12, color=colors["text_light"], font_family="Inter")
                        ])
                    ], spacing=6),
                    padding=12,
                    border=ft.border.all(1, colors["border"]),
                    border_radius=6,
                    bgcolor=colors["card"],
                    margin=ft.margin.only(bottom=8)
                )
            )

        content_area.content = ft.Column([
            ft.Text("Financial Reports", size=24, weight="bold", color=colors["text"], font_family="Inter Bold"),
            ft.Divider(height=20, color="transparent"),
            ft.Text("Monthly Overview", size=16, weight="bold", color=colors["text"], font_family="Inter Bold"),
            *monthly_charts
        ], scroll=ft.ScrollMode.ADAPTIVE, spacing=16, expand=True)
        page.update()

    # --- SETTINGS ---
    def show_settings():
        inc_list = ft.Column(spacing=4)
        exp_list = ft.Column(spacing=4)
        new_inc = create_text_field("New Income Category", colors["accent"], width=220)
        new_exp = create_text_field("New Expense Category", colors["danger"], width=220)
        status = ft.Text("", size=13, font_family="Inter")

        def refresh_cats():
            nonlocal inc_list, exp_list
            inc_list.controls.clear()
            for cat in data["categories"]["income"]:
                row = ft.Container(
                    content=ft.Row([
                        ft.Text(cat, size=14, color=colors["text"]),
                        ft.IconButton("delete", icon_size=16, icon_color=colors["danger"], on_click=lambda e, c=cat: delete_cat("income", c))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(vertical=4, horizontal=8),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, colors["border"])),
                )
                inc_list.controls.append(row)

            exp_list.controls.clear()
            for cat in data["categories"]["expenses"]:
                row = ft.Container(
                    content=ft.Row([
                        ft.Text(cat, size=14, color=colors["text"]),
                        ft.IconButton("delete", icon_size=16, icon_color=colors["danger"], on_click=lambda e, c=cat: delete_cat("expenses", c))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.padding.symmetric(vertical=4, horizontal=8),
                    border=ft.border.only(bottom=ft.border.BorderSide(1, colors["border"])),
                )
                exp_list.controls.append(row)

        def delete_cat(cat_type, name):
            if name in data["categories"][cat_type]:
                data["categories"][cat_type].remove(name)
                save_data(data)
                status.value = f"🗑️ '{name}' deleted."
                status.color = colors["danger"]
                refresh_cats()
            page.update()

        def add_cat(cat_type, field, cat_list):
            val = field.value.strip()
            if not val:
                status.value = "⚠️ Category name cannot be empty."
                status.color = colors["text_light"]
            elif val in data["categories"][cat_type]:
                status.value = f"⚠️ '{val}' already exists."
                status.color = colors["text_light"]
            else:
                data["categories"][cat_type].append(val)
                save_data(data)
                field.value = ""
                status.value = f"✅ '{val}' added."
                status.color = colors["accent"]
                refresh_cats()
            page.update()

        refresh_cats()

        content_area.content = ft.Column([
            ft.Text("Settings", size=24, weight="bold", color=colors["text"], font_family="Inter Bold"),
            ft.Divider(height=20, color="transparent"),

            ft.Text("Income Categories", size=16, weight="bold", color=colors["text"], font_family="Inter Bold"),
            ft.Row([new_inc, create_button("Add", colors["accent"], lambda e: add_cat("income", new_inc, inc_list))], spacing=10),
            ft.Container(inc_list, border=ft.border.all(1, colors["border"]), border_radius=6, bgcolor=colors["card"], margin=ft.margin.only(bottom=16)),

            ft.Text("Expense Categories", size=16, weight="bold", color=colors["text"], font_family="Inter Bold"),
            ft.Row([new_exp, create_button("Add", colors["danger"], lambda e: add_cat("expenses", new_exp, exp_list))], spacing=10),
            ft.Container(exp_list, border=ft.border.all(1, colors["border"]), border_radius=6, bgcolor=colors["card"], margin=ft.margin.only(bottom=16)),

            status
        ], scroll=ft.ScrollMode.HIDDEN, spacing=16, expand=True)
        page.update()

    # --- NAVIGATION HANDLER ---
    def on_rail_change(e):
        page.overlay.clear()
        index = e.control.selected_index
        views = [show_dashboard, show_reports, show_settings]
        views[index]()
        content_area.update()

    rail.on_change = on_rail_change

    # --- اضافه کردن به صفحه ---
    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1, color=colors["border"]),
                content_area
            ],
            expand=True
        )
    )

    # نمایش اولیه
    show_dashboard()

# --- اجرای برنامه ---
ft.app(target=main, assets_dir="assets")