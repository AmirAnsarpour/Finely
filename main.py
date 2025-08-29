import flet as ft
import json
import os
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib
from io import BytesIO
import base64


# --- تنظیم Matplotlib ---
matplotlib.use("Agg")

# --- Color Palette Generator ---
def get_colors(theme="light"):
    if theme == "light":
        return {
            "primary": "#0078D7",
            "background": "#F5F5F5",
            "card": "#FFFFFF",
            "text": "#2C2C2C",
            "text_light": "#6E6E6E",
            "accent": "#00A86B",  # سبز
            "danger": "#D93025",  # قرمز
            "border": "#D0D0D0",
            "hover_bg": "#F0F0F0",
            "header": "#0078D7",
            "surface": "#FFFFFF",
            "shadow": "#CCCCCC",
        }
    else:
        return {
            "primary": "#0091FF",
            "background": "#121212",
            "card": "#1E1E1E",
            "text": "#E0E0E0",
            "text_light": "#B0B0B0",
            "accent": "#00C880",  # سبز روشن
            "danger": "#FF4D4D",  # قرمز روشن
            "border": "#333333",
            "hover_bg": "#2A2A2A",
            "header": "#0091FF",
            "surface": "#252525",
            "shadow": "#333333",
        }

# --- تنظیم رنگ‌های Matplotlib بر اساس تم ---
def update_matplotlib_colors(theme="light"):
    c = get_colors(theme)
    plt.rcParams.update({
        'font.family': 'Vazirmatn',
        'font.sans-serif': ['Vazirmatn', 'Arial', 'Calibri', 'Helvetica'],
        'axes.titleweight': 'bold',
        'axes.titlesize': 13,
        'axes.labelsize': 10,
        'axes.labelweight': 'bold',
        'axes.edgecolor': '#555555' if theme == "dark" else '#333333',
        'axes.linewidth': 0.8,
        'axes.facecolor': c["card"],
        'figure.facecolor': c["card"],
        'grid.color': c["border"],
        'grid.linestyle': '--',
        'grid.alpha': 0.4,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'text.color': c["text"],
        'axes.labelcolor': c["text"],
        'xtick.color': c["text"],
        'ytick.color': c["text"],
        'savefig.transparent': False,
        'savefig.pad_inches': 0.3,
        'savefig.dpi': 120,
        'lines.linewidth': 2.5
    })

# --- Data File ---
DATA_FILE = "data.json"
default_data = {
    "income": [],
    "expenses": [],
    "categories": {
        "income": ["Salary", "Freelance", "Investments", "Gifts", "Other"],
        "expenses": ["Food", "Transport", "Utilities", "Entertainment", "Shopping", "Health", "Other"]
    },
    "theme": "light"
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

# --- Reusable StatCard ---
def StatCard(title, value, color, icon):
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(icon, color=color, size=20),
                ft.Text(title, size=12, color=colors["text_light"], font_family="Vazirmatn")
            ], spacing=6),
            ft.Text(value, size=20, color=colors["text"], weight="bold", font_family="Vazirmatn Bold"),
        ], spacing=4),
        padding=16,
        border=ft.border.all(1, colors["border"]),
        border_radius=6,
        bgcolor=colors["card"],
        width=200,
        height=100
    )

chart_cache = {
    "last_hash": None,
    "income_pie": None,
    "expense_pie": None,
    "monthly_bar": None,
    "net_balance_line": None
}

def get_data_hash():
    return hash(json.dumps(data, sort_keys=True))

def plot_to_image():
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return ft.Image(
        src_base64=img_base64,
        width=600,
        height=300,
        fit=ft.ImageFit.CONTAIN
    )

def create_income_pie(income_data):
    if not income_data:
        return ft.Text("No income data.", italic=True, color=colors["text_light"])
    update_matplotlib_colors(data["theme"])
    labels = list(income_data.keys())
    sizes = list(income_data.values())
    plt.figure(figsize=(5, 4))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
            colors=["#66B2FF", "#99FF99", "#FFD700", "#FF9999", "#C2C2F0"][:len(labels)])
    plt.title("Income Distribution by Category", fontsize=12, fontweight='bold', pad=20)
    return plot_to_image()

def create_expense_pie(expense_data):
    if not expense_data:
        return ft.Text("No expense data.", italic=True, color=colors["text_light"])
    update_matplotlib_colors(data["theme"])
    labels = list(expense_data.keys())
    sizes = list(expense_data.values())
    plt.figure(figsize=(5, 4))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
            colors=["#FF9999", "#FFCC99", "#FF99CC", "#FF6666", "#C2C2F0", "#FFB3E6", "#D93025"][:len(labels)])
    plt.title("Expense Distribution by Category", fontsize=12, fontweight='bold', pad=20)
    return plot_to_image()

def create_monthly_bar(monthly_data):
    if not monthly_data:
        return ft.Text("No monthly data.", italic=True, color=colors["text_light"])
    update_matplotlib_colors(data["theme"])
    months = sorted(monthly_data.keys())
    month_labels = [f"{m[5:]}/{m[:4][2:]}" for m in months]
    incomes = [monthly_data[m]["income"] for m in months]
    expenses = [monthly_data[m]["expenses"] for m in months]

    x = range(len(months))
    width = 0.35

    plt.figure(figsize=(7, 4))
    plt.bar([i - width/2 for i in x], incomes, width, label="Income", color=colors["accent"], alpha=0.8)
    plt.bar([i + width/2 for i in x], expenses, width, label="Expenses", color=colors["danger"], alpha=0.8)
    plt.xlabel("Month (MM/YY)", fontsize=10)
    plt.ylabel("Amount", fontsize=10)
    plt.title("Monthly Income vs Expenses", fontsize=12, fontweight='bold', pad=15)
    plt.xticks(x, month_labels, rotation=0, fontsize=9)
    plt.yticks(fontsize=9)
    plt.legend(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.tight_layout(pad=2.0)
    return plot_to_image()

def create_net_balance_line(monthly_data):
    if not monthly_data:
        return ft.Text("No data for balance trend.", italic=True, color=colors["text_light"])
    update_matplotlib_colors(data["theme"])
    months = sorted(monthly_data.keys())
    month_labels = [f"{m[5:]}/{m[:4][2:]}" for m in months]
    balances = [monthly_data[m]["income"] - monthly_data[m]["expenses"] for m in months]

    plt.figure(figsize=(7, 4))
    plt.plot(month_labels, balances, marker='o', linewidth=2.5, color=colors["primary"], label="Net Balance")

    for i, bal in enumerate(balances):
        color = colors["accent"] if bal >= 0 else colors["danger"]
        plt.plot(i, bal, 'o', color=color)
        plt.text(i, bal + (10 if bal >= 0 else -15), f"{bal:,.0f}", fontsize=8, ha='center', va='center')

    plt.axhline(0, color=colors["text_light"], linewidth=1, linestyle='--')
    plt.xlabel("Month (MM/YY)", fontsize=10)
    plt.ylabel("Net Balance", fontsize=10)
    plt.title("Monthly Net Balance Trend", fontsize=12, fontweight='bold', pad=15)
    plt.xticks(rotation=0, fontsize=9)
    plt.yticks(fontsize=9)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout(pad=2.0)
    return plot_to_image()


# --- Main App ---
def main(page: ft.Page):
    global data, colors
    colors = get_colors(data["theme"])

    page.title = "Finely"
    page.window_icon = "assets/icon/icon-tra.png"
    page.theme_mode = ft.ThemeMode.DARK if data["theme"] == "dark" else ft.ThemeMode.LIGHT
    page.bgcolor = colors["background"]
    page.fonts = {
        "Vazirmatn": "fonts/Vazirmatn-Medium.ttf",
        "Vazirmatn Bold": "fonts/Vazirmatn-Bold.ttf",
    }
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 1000
    page.window_min_height = 700

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

    # --- Navigation Rail ---
    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=80,
        min_extended_width=180,
        group_alignment=0,
        bgcolor=colors["card"],
        elevation=1,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Dashboard"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.INSIGHTS_OUTLINED,
                selected_icon=ft.Icons.INSIGHTS,
                label="Reports"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings"
            ),
        ],
        leading=ft.Container(
            content=ft.Column([
                ft.Image(
                    src= "assets/icon/icon-tra.png",
                    width=70,
                    fit=ft.ImageFit.CONTAIN
                ),
            ],
        ),
    ))

    nav_container = ft.Container(
        content=rail,
        border_radius=ft.BorderRadius(
            top_left=16,
            bottom_left=16,
            top_right=0,
            bottom_right=0
        ),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        width=80,  
        bgcolor=colors["card"],
    )

    content_area = ft.Container(
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

        stats_row = ft.Row(
            controls=[
                StatCard("Total Income", fmt(total_income), colors["accent"], "paid"),
                StatCard("Total Expenses", fmt(total_expenses), colors["danger"], "payments"),
                StatCard("Net Balance", fmt(net_balance), colors["primary"], "account_balance_wallet"),
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            wrap=True
        )

        amount_inc = create_text_field("Amount", colors["accent"], width=145)
        source_inc = create_text_field("Source", colors["accent"], width=145)
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
                ft.Row([
                    ft.Icon("add", color=colors["accent"], size=18),
                    ft.Text("Add Income", size=16, weight="bold", color=colors["text"], font_family="Vazirmatn Bold")
                ], spacing=6),
                ft.Divider(height=10, color="transparent"),
                ft.Row([amount_inc, source_inc], spacing=10),
                cat_inc,
                ft.ElevatedButton(
                    "Add Income",
                    style=ft.ButtonStyle(bgcolor=colors["accent"], color=colors["card"]),
                    on_click=add_income,
                    height=36
                )
            ], spacing=10),
            padding=16,
            border=ft.border.all(1, colors["border"]),
            border_radius=8,
            bgcolor=colors["card"],
            width=400
        )

        # --- فرم مخارج ---
        amount_exp = create_text_field("Amount", colors["danger"], width=145)
        desc_exp = create_text_field("Description", colors["danger"], width=145)
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
                ft.Row([
                    ft.Icon("remove", color=colors["danger"], size=18),
                    ft.Text("Add Expense", size=16, weight="bold", color=colors["text"], font_family="Vazirmatn Bold")
                ], spacing=6),
                ft.Divider(height=10, color="transparent"),
                ft.Row([amount_exp, desc_exp], spacing=10),
                cat_exp,
                ft.ElevatedButton(
                    "Add Expense",
                    style=ft.ButtonStyle(bgcolor=colors["danger"], color=colors["card"]),
                    on_click=add_expense,
                    height=36
                )
            ], spacing=10),
            padding=16,
            border=ft.border.all(1, colors["border"]),
            border_radius=8,
            bgcolor=colors["card"],
            width=400
        )

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
            icon = "paid" if tx['type'] == 'income' else "payments"
            recent_tx.append(
                ft.ListTile(
                    leading=ft.Container(
                        content=ft.Icon(icon, color=color, size=18),
                        width=32, height=32,
                        bgcolor=f"{color}10",
                        border_radius=16,
                        alignment=ft.alignment.center
                    ),
                    title=ft.Text(label, size=14, color=colors["text"], font_family="Vazirmatn"),
                    subtitle=ft.Text(f"{tx['category']} • {tx['date']}", size=12, color=colors["text_light"], font_family="Vazirmatn"),
                    trailing=ft.Text(amount, color=color, size=14, weight="bold"),
                    dense=True
                )
            )

        recent_section = ft.Container(
            content=ft.Column([
                ft.Text("📌 Recent Transactions", size=18, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
                ft.Divider(height=1, color=colors["border"]),
                *recent_tx
            ]),
            padding=12,
            border=ft.border.all(1, colors["border"]),
            border_radius=8,
            bgcolor=colors["card"],
            margin=ft.margin.only(top=20)
        )

        left_col = ft.Column(
            controls=[
                stats_row,
                ft.Row([income_form, expense_form], spacing=20, alignment=ft.MainAxisAlignment.CENTER, wrap=True),
                recent_section
            ],
            spacing=20,
            expand=True,
        )

        content_area.content = ft.Column(
            controls=[
                ft.Text("Dashboard", size=24, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
                ft.Divider(height=20, color="transparent"),
                left_col
            ],
            scroll=ft.ScrollMode.HIDDEN,
            spacing=20,
            expand=True,
        )
        page.update()
    
    # --- REPORTS ---
    def show_reports():
        monthly = defaultdict(lambda: {"income": 0.0, "expenses": 0.0})
        income_by_cat = defaultdict(float)
        expense_by_cat = defaultdict(float)

        for inc in data["income"]:
            month_key = inc["date"][:7]
            monthly[month_key]["income"] += inc["amount"]
            income_by_cat[inc["category"]] += inc["amount"]

        for exp in data["expenses"]:
            month_key = exp["date"][:7]
            monthly[month_key]["expenses"] += exp["amount"]
            expense_by_cat[exp["category"]] += exp["amount"]

        total_income = sum(m["income"] for m in monthly.values())
        total_expenses = sum(m["expenses"] for m in monthly.values())
        net_balance = total_income - total_expenses

        current_hash = get_data_hash()
        if chart_cache["last_hash"] != current_hash:
            chart_cache["income_pie"] = create_income_pie(income_by_cat)
            chart_cache["expense_pie"] = create_expense_pie(expense_by_cat)
            chart_cache["monthly_bar"] = create_monthly_bar(monthly)
            chart_cache["net_balance_line"] = create_net_balance_line(monthly)
            chart_cache["last_hash"] = current_hash

        stats_row = ft.Row(
            controls=[
                StatCard("Total Income", f"{total_income:,.2f}", colors["accent"], "paid"),
                StatCard("Total Expenses", f"{total_expenses:,.2f}", colors["danger"], "payments"),
                StatCard("Net Balance", f"{net_balance:,.2f}", colors["primary"], "account_balance_wallet"),
            ],
            spacing=16,
            alignment=ft.MainAxisAlignment.CENTER,
            wrap=True
        )

        def chart_container(title, chart, icon):
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, color=colors["primary"], size=18),
                        ft.Text(title, size=16, weight="bold", color=colors["text"], font_family="Vazirmatn Bold")
                    ], spacing=6),
                    ft.Divider(height=1, color=colors["border"]),
                    ft.Container(
                        content=chart,
                        alignment=ft.alignment.center,
                        padding=ft.padding.only(top=10)
                    )
                ]),
                padding=16,
                border=ft.border.all(1, colors["border"]),
                border_radius=8,
                bgcolor=colors["card"],
                expand=True
            )

        charts_row_1 = ft.Row(
            controls=[
                chart_container("Income by Category", chart_cache["income_pie"], "pie_chart"),
                chart_container("Expenses by Category", chart_cache["expense_pie"], "pie_chart")
            ],
            spacing=20,
            expand=True
        )

        charts_row_2 = ft.Row(
            controls=[
                chart_container("Monthly Income vs Expenses", chart_cache["monthly_bar"], "bar_chart"),
                chart_container("Net Balance Trend", chart_cache["net_balance_line"], "show_chart")
            ],
            spacing=20,
            expand=True
        )

        content_area.content = ft.Column(
            controls=[
                ft.Text("Financial Reports", size=24, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
                ft.Divider(height=20, color="transparent"),
                stats_row,
                ft.Divider(height=20, color="transparent"),
                charts_row_1,
                ft.Divider(height=20, color="transparent"),
                charts_row_2
            ],
            scroll=ft.ScrollMode.HIDDEN,
            spacing=20,
            expand=True,
        )
        page.update()
    
    # --- SETTING ---
    def show_settings():
        status = ft.Text("", size=13, font_family="Vazirmatn")

        # --- Theme Selector ---
        theme_dropdown = ft.Dropdown(
            label="Theme",
            value=data["theme"],
            options=[
                ft.dropdown.Option("light", "Light Mode"),
                ft.dropdown.Option("dark", "Dark Mode")
            ],
            border_color=colors["border"],
            focused_border_color=colors["primary"],
            label_style=ft.TextStyle(color=colors["text_light"], size=13),
            text_style=ft.TextStyle(color=colors["text"], size=14),
            width=220,
            color=colors["text"]
        )

        def change_theme(e):
            new_theme = theme_dropdown.value
            if new_theme not in ["light", "dark"]:
                return
            data["theme"] = new_theme
            save_data(data)
            status.value = "✅ Theme saved. Please restart the app to apply changes."
            status.color = colors["accent"]
            page.update()

        theme_button = ft.ElevatedButton(
            "Apply Theme",
            style=ft.ButtonStyle(
                bgcolor=colors["primary"],
                color=colors["card"],
                padding=ft.padding.symmetric(horizontal=20, vertical=10)
            ),
            on_click=change_theme
        )

        # --- Category Management ---
        def create_category_manager(cat_type: str, color: str):
            list_view = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
            new_field = create_text_field(f"New {cat_type.capitalize()} Category", color, width=200)

            def add_cat(e):
                val = new_field.value.strip()
                if not val:
                    status.value = "⚠️ Category name cannot be empty."
                    status.color = colors["text_light"]
                elif val in data["categories"][cat_type]:
                    status.value = f"⚠️ Category '{val}' already exists."
                    status.color = colors["text_light"]
                else:
                    data["categories"][cat_type].append(val)
                    save_data(data)
                    new_field.value = ""
                    status.value = f"✅ '{val}' added."
                    status.color = colors["accent"]
                    refresh_categories()
                page.update()

            def delete_cat(name):
                data["categories"][cat_type].remove(name)
                save_data(data)
                status.value = f"🗑️ '{name}' deleted."
                status.color = colors["danger"]
                refresh_categories()
                page.update()

            def refresh_categories():
                list_view.controls.clear()
                for cat in data["categories"][cat_type]:
                    list_view.controls.append(
                        ft.ListTile(
                            leading=ft.Container(
                                content=ft.Text(cat[0].upper(), size=14, color=color),
                                width=30, height=30,
                                bgcolor=f"{color}20",
                                border_radius=15,
                                alignment=ft.alignment.center
                            ),
                            title=ft.Text(cat, size=14, color=colors["text"]),
                            trailing=ft.IconButton(
                                icon="delete",
                                icon_size=16,
                                icon_color=colors["danger"],
                                on_click=lambda e, c=cat: delete_cat(c)
                            ),
                        )
                    )
                page.update()

            refresh_categories()

            return ft.Container(
                content=ft.Column([
                    ft.Text(f"{cat_type.capitalize()} Categories", size=16, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
                    ft.Divider(height=1, color=colors["border"]),
                    ft.Row([
                        new_field,
                        ft.ElevatedButton(
                            "Add",
                            style=ft.ButtonStyle(bgcolor=color, color=colors["card"]),
                            on_click=add_cat,
                            height=40
                        )
                    ], spacing=10),
                    ft.Container(
                        content=list_view,
                        height=180,
                        padding=ft.padding.only(top=8),
                        bgcolor=colors["surface"],
                        border_radius=8,
                        border=ft.border.all(1, colors["border"])
                    )
                ]),
                padding=16,
                border=ft.border.all(1, colors["border"]),
                border_radius=8,
                bgcolor=colors["card"]
            )

        income_cat_manager = create_category_manager("income", colors["accent"])
        expense_cat_manager = create_category_manager("expenses", colors["danger"])

        # --- Appearance Section ---
        appearance_section = ft.Container(
            content=ft.Column([
                ft.Text("Appearance", size=16, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
                ft.Divider(height=1, color=colors["border"]),
                ft.Row([
                    theme_dropdown,
                    theme_button
                ], spacing=10, alignment=ft.MainAxisAlignment.START),
                ft.Container(
                    content=ft.Text(
                        "💡 Theme changes will take effect after restarting the app.",
                        size=12,
                        color=colors["text_light"]
                    ),
                    margin=ft.margin.only(top=8)
                )
            ]),
            padding=16,
            height=315,
            border=ft.border.all(1, colors["border"]),
            border_radius=8,
            bgcolor=colors["card"],
        )

        # --- About Section ---
        about_section = ft.Container(
            content=ft.Column([
                ft.Text("About Finely", size=16, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
                ft.Divider(height=1, color=colors["border"]),
                ft.ListTile(
                    title=ft.Text("Version", weight="bold", color=colors["text"]),
                    subtitle=ft.Text("1.0.0", color=colors["text_light"])
                ),
                ft.ListTile(
                    title=ft.Text("Developer", weight="bold", color=colors["text"]),
                    subtitle=ft.Text("Amir Ansarpour", color=colors["text_light"])
                ),
                ft.ListTile(
                    title=ft.Text("Data File", weight="bold", color=colors["text"]),
                    subtitle=ft.Text(f"Location: {os.path.abspath(DATA_FILE)}", size=11, color=colors["text_light"])
                )
            ]),
            padding=16,
            height=315,
            border=ft.border.all(1, colors["border"]),
            border_radius=8,
            bgcolor=colors["card"]
        )

        # --- چیدمان جدید: دسته‌ها سمت چپ، تم و درباره سمت راست ---
        left_col = ft.Column(
            controls=[
                income_cat_manager,
                expense_cat_manager
            ],
            spacing=16,
            expand=True
        )

        right_col = ft.Column(
            controls=[
                appearance_section,
                about_section
            ],
            spacing=16,
            expand=True
        )

        content_area.content = ft.Column([
            ft.Text("Settings", size=24, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
            ft.Divider(height=24, color="transparent"),
            ft.Row([
                ft.Container(left_col, expand=True, padding=ft.padding.only(right=8)),
                ft.Container(right_col, expand=True, padding=ft.padding.only(left=8))
            ], spacing=16, expand=True),
            ft.Divider(height=12, color="transparent"),
            status
        ], scroll=ft.ScrollMode.HIDDEN, spacing=12, expand=True)

        page.update()

    # --- Navigation Handler ---
    def on_rail_change(e):
        index = e.control.selected_index
        views = [show_dashboard, show_reports, show_settings]
        views[index]()
        content_area.update()

    rail.on_change = on_rail_change

    page.add(
        ft.Row([
            nav_container,
            ft.VerticalDivider(width=20, color=colors["border"]),
            content_area
        ], spacing=0, expand=True)
    )

    show_dashboard()

ft.app(target=main, assets_dir="assets", view=ft.FLET_APP)
