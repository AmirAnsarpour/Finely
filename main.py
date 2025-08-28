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
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans', 'Calibri', 'Helvetica'],
    'axes.titleweight': 'bold',
    'axes.titlesize': 13,
    'axes.labelsize': 10,
    'axes.labelweight': 'bold',
    'axes.edgecolor': '#333333',
    'axes.linewidth': 0.8,
    'axes.facecolor': '#F8F9FA',
    'figure.facecolor': '#F8F9FA',
    'grid.color': '#CCCCCC',
    'grid.linestyle': '--',
    'grid.alpha': 0.4,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'text.color': '#2C2C2C',
    'axes.labelcolor': '#2C2C2C',
    'xtick.color': '#2C2C2C',
    'ytick.color': '#2C2C2C',
    'savefig.transparent': False,
    'savefig.pad_inches': 0.3,
    'savefig.dpi': 120,
    'lines.linewidth': 2.5
})

# --- Color Palette ---
colors = {
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
}

# --- Data File ---
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

# بارگذاری داده
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

# --- کش چارت‌ها (برای سرعت بالا) ---
chart_cache = {
    "last_hash": None,
    "income_pie": None,
    "expense_pie": None,
    "monthly_bar": None,
    "net_balance_line": None
}

def get_data_hash():
    return hash(json.dumps(data, sort_keys=True))

# --- تبدیل plt به ft.Image ---
def plot_to_image():
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches='tight')
    plt.close()  # مهم: بستن صحیح فیگور
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return ft.Image(
        src_base64=img_base64,
        width=600,
        height=300,
        fit=ft.ImageFit.CONTAIN
    )

# --- چارت: درآمد بر اساس دسته ---
def create_income_pie(income_data):
    if not income_data:
        return ft.Text("No income data.", italic=True, color=colors["text_light"])
    labels = list(income_data.keys())
    sizes = list(income_data.values())
    plt.figure(figsize=(5, 4))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
            colors=["#66B2FF", "#99FF99", "#FFD700", "#FF9999", "#C2C2F0"][:len(labels)])
    plt.title("Income Distribution by Category", fontsize=12, fontweight='bold', pad=20)
    return plot_to_image()

# --- چارت: مخارج بر اساس دسته ---
def create_expense_pie(expense_data):
    if not expense_data:
        return ft.Text("No expense data.", italic=True, color=colors["text_light"])
    labels = list(expense_data.keys())
    sizes = list(expense_data.values())
    plt.figure(figsize=(5, 4))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90,
            colors=["#FF9999", "#FFCC99", "#FF99CC", "#FF6666", "#C2C2F0", "#FFB3E6", "#D93025"][:len(labels)])
    plt.title("Expense Distribution by Category", fontsize=12, fontweight='bold', pad=20)
    return plot_to_image()

# --- چارت: مقایسه ماهانه درآمد و مخارج ---
def create_monthly_bar(monthly_data):
    if not monthly_data:
        return ft.Text("No monthly data.", italic=True, color=colors["text_light"])

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

# --- چارت: روند تراز مالی (Net Balance Trend) ---
def create_net_balance_line(monthly_data):
    if not monthly_data:
        return ft.Text("No data for balance trend.", italic=True, color=colors["text_light"])

    months = sorted(monthly_data.keys())
    month_labels = [f"{m[5:]}/{m[:4][2:]}" for m in months]
    balances = [monthly_data[m]["income"] - monthly_data[m]["expenses"] for m in months]

    plt.figure(figsize=(7, 4))
    plt.plot(month_labels, balances, marker='o', linewidth=2.5, color=colors["primary"], label="Net Balance")

    # رنگ‌دهی مثبت/منفی
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
    page.title = "Finely"
    page.theme_mode = ft.ThemeMode.LIGHT
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
            content=ft.Text("Finely", size=18, weight="bold", color=colors["header"], font_family="Vazirmatn Bold"),
            padding=ft.padding.only(left=16, top=16, bottom=16)
        ),
        trailing=ft.Container(
            padding=ft.padding.only(bottom=16),
            content=ft.Text("v1.0.0", size=12, color=colors["text_light"])
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

        stats = ft.Row(
            controls=[
                StatCard("Income", fmt(total_income), colors["accent"], "trending_up"),
                StatCard("Expenses", fmt(total_expenses), colors["danger"], "trending_down"),
                StatCard("Balance", fmt(net_balance), colors["primary"], "account_balance_wallet"),
            ],
            spacing=16,
            wrap=True
        )

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
                ft.Text("➕ Add Income", size=16, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
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
                ft.Text("➖ Add Expense", size=16, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
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
                    title=ft.Text(label, size=14, color=colors["text"], font_family="Vazirmatn"),
                    subtitle=ft.Text(f"{tx['category']} • {tx['date']}", size=12, color=colors["text_light"], font_family="Vazirmatn"),
                    trailing=ft.Text(amount, color=color, size=14, weight="bold"),
                )
            )

        recent_section = ft.Container(
            content=ft.Column([
                ft.Text("📌 Recent Transactions", size=18, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
                ft.Divider(height=1, color=colors["border"]),
                *recent_tx
            ]),
            border=ft.border.all(1, colors["border"]),
            border_radius=6,
            bgcolor=colors["card"],
            padding=12,
            margin=ft.margin.only(top=20)
        )

        content_area.content = ft.Column([
            ft.Text("Dashboard", size=24, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
            ft.Divider(height=24, color="transparent"),
            stats,
            ft.Row([income_form, expense_form], spacing=20, wrap=True),
            recent_section
        ], scroll=ft.ScrollMode.HIDDEN, spacing=20, expand=True)
        page.update()

    # --- REPORTS با تمام چارت‌ها ---
    def show_reports():
        # گردآوری داده‌ها
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

        # آمار کلی
        total_income = sum(m["income"] for m in monthly.values())
        total_expenses = sum(m["expenses"] for m in monthly.values())
        net_balance = total_income - total_expenses

        # --- کس چارت‌ها ---
        current_hash = get_data_hash()
        if chart_cache["last_hash"] != current_hash:
            chart_cache["income_pie"] = create_income_pie(income_by_cat)
            chart_cache["expense_pie"] = create_expense_pie(expense_by_cat)
            chart_cache["monthly_bar"] = create_monthly_bar(monthly)
            chart_cache["net_balance_line"] = create_net_balance_line(monthly)
            chart_cache["last_hash"] = current_hash

        # --- نمایش ---
        content_area.content = ft.Column(
            controls=[
                ft.Text("Financial Reports", size=24, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
                ft.Divider(height=20, color="transparent"),

                # آمار کلی
                ft.Row([
                    StatCard("Total Income", f"{total_income:,.2f}", colors["accent"], "paid"),
                    StatCard("Total Expenses", f"{total_expenses:,.2f}", colors["danger"], "payments"),
                    StatCard("Net Balance", f"{net_balance:,.2f}", colors["primary"], "balance"),
                ], spacing=16, wrap=True),

                ft.Divider(height=20, color="transparent"),

                # چارت‌های دایره‌ای
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("📈 Income by Category", size=16, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
                            chart_cache["income_pie"]
                        ], spacing=10),
                        expand=True,
                        padding=10
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("💸 Expenses by Category", size=16, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
                            chart_cache["expense_pie"]
                        ], spacing=10),
                        expand=True,
                        padding=10
                    )
                ], spacing=20, expand=True),

                ft.Divider(height=20, color="transparent"),

                # چارت میله‌ای
                ft.Container(
                    content=ft.Column([
                        ft.Text("📅 Monthly Income vs Expenses", size=16, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
                        chart_cache["monthly_bar"]
                    ], spacing=10),
                    padding=10
                ),

                ft.Divider(height=20, color="transparent"),

                # چارت تراز
                ft.Container(
                    content=ft.Column([
                        ft.Text("💰 Net Balance Trend", size=16, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
                        chart_cache["net_balance_line"]
                    ], spacing=10),
                    padding=10
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            spacing=20,
            expand=True
        )
        page.update()

    # --- SETTINGS ---
    def show_settings():
        inc_list = ft.Column(spacing=4)
        exp_list = ft.Column(spacing=4)
        new_inc = create_text_field("New Income Category", colors["accent"], width=220)
        new_exp = create_text_field("New Expense Category", colors["danger"], width=220)
        status = ft.Text("", size=13, font_family="Vazirmatn")

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
            ft.Text("Settings", size=24, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
            ft.Divider(height=20, color="transparent"),

            ft.Text("Income Categories", size=16, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
            ft.Row([new_inc, create_button("Add", colors["accent"], lambda e: add_cat("income", new_inc, inc_list))], spacing=10),
            ft.Container(inc_list, border=ft.border.all(1, colors["border"]), border_radius=6, bgcolor=colors["card"], margin=ft.margin.only(bottom=16)),

            ft.Text("Expense Categories", size=16, weight="bold", color=colors["text"], font_family="Vazirmatn Bold"),
            ft.Row([new_exp, create_button("Add", colors["danger"], lambda e: add_cat("expenses", new_exp, exp_list))], spacing=10),
            ft.Container(exp_list, border=ft.border.all(1, colors["border"]), border_radius=6, bgcolor=colors["card"], margin=ft.margin.only(bottom=16)),

            status
        ], scroll=ft.ScrollMode.HIDDEN, spacing=16, expand=True)
        page.update()

    # --- Navigation Handler ---
    def on_rail_change(e):
        index = e.control.selected_index
        views = [show_dashboard, show_reports, show_settings]
        views[index]()
        content_area.update()

    rail.on_change = on_rail_change

    # --- اضافه کردن به صفحه ---
    page.add(
        ft.Row([
            rail,
            ft.VerticalDivider(width=1, color=colors["border"]),
            content_area
        ], expand=True)
    )

    # نمایش اولیه
    show_dashboard()

# --- اجرای برنامه ---
ft.app(target=main, assets_dir="assets")