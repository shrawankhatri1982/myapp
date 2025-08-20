# main.py
from kivy.config import Config
Config.set("kivy", "keyboard_mode", "systemanddock")  # Enter moves focus on mobile keyboards, etc.

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp

from kivymd.app import MDApp
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText
from kivymd.uix.datatables import MDDataTable

import sqlite3, re, csv, os

# --------- CONSTANTS ----------
DB_NAME = "users.db"
EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_RE = re.compile(r"^[6-9]\d{9}$")

KV = """
ScreenManager:
    MDScreen:
        name: "home"
        md_bg_color: 0.05, 0.08, 0.14, 1  # dark blue background

        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(10)
            padding: dp(16)

            # Header
            MDBoxLayout:
                size_hint_y: None
                height: dp(70)
                md_bg_color: 0.07, 0.11, 0.18, 1
                radius: [16,16,16,16]
                padding: dp(12)
                MDLabel:
                    text: "SADANAND COMPUTERS"
                    font_style: "H5"
                    bold: True
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 1,1,1,1

            # Form Card
            MDBoxLayout:
                md_bg_color: 0.09, 0.14, 0.22, 1
                radius: [20,20,20,20]
                padding: dp(16)
                spacing: dp(12)

                MDBoxLayout:
                    orientation: "vertical"
                    spacing: dp(10)

                    MDTextField:
                        id: name_field
                        hint_text: "Name (auto UPPERCASE)"
                        icon_left: "account"
                        mode: "rectangle"
                        size_hint_y: None
                        height: dp(60)
                        on_text_validate: app.focus_next("email_field")

                    MDTextField:
                        id: email_field
                        hint_text: "Email (auto lowercase)"
                        icon_left: "email"
                        mode: "rectangle"
                        size_hint_y: None
                        height: dp(60)
                        on_text_validate: app.focus_next("phone_field")

                    MDTextField:
                        id: phone_field
                        hint_text: "Phone (10 digits, starts 6-9)"
                        icon_left: "phone"
                        mode: "rectangle"
                        input_filter: "int"
                        max_text_length: 10
                        size_hint_y: None
                        height: dp(60)
                        on_text_validate: app.save_data()

                    MDBoxLayout:
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(56)

                        MDRaisedButton:
                            text: "💾 Save"
                            md_bg_color: 0.15, 0.38, 0.96, 1
                            on_release: app.save_data()

                        MDRaisedButton:
                            text: "📑 View / Delete"
                            md_bg_color: 0.09, 0.65, 0.45, 1
                            on_release: app.open_view()

                        MDRaisedButton:
                            text: "📤 Export CSV"
                            md_bg_color: 0.57, 0.18, 0.98, 1
                            on_release: app.export_csv()

            # Footer
            MDBoxLayout:
                size_hint_y: None
                height: dp(44)
                md_bg_color: 0.07, 0.11, 0.18, 1
                radius: [16,16,16,16]
                padding: dp(10)
                MDLabel:
                    text: "Developed By - Shrawan Kumar Khatri"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 1,1,1,1
"""

class SadanandApp(MDApp):
    def build(self):
        self.title = "SADANAND COMPUTERS"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        # DB init
        self.conn = sqlite3.connect(DB_NAME)
        self.cur = self.conn.cursor()
        self.init_db()
        return Builder.load_string(KV)

    # ---------- DB ----------
    def init_db(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT UNIQUE NOT NULL
            )
        """)
        self.conn.commit()

    # ---------- Helpers ----------
    def snack(self, msg):
        MDSnackbar(
            MDSnackbarSupportingText(text=msg),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.13,0.16,0.23,1),
        ).open()

    def focus_next(self, wid_id):
        self.root.ids[wid_id].focus = True

    # ---------- Save ----------
    def save_data(self):
        name  = self.root.ids.name_field.text.strip().upper()   # Name -> UPPER
        email = self.root.ids.email_field.text.strip().lower()  # Email -> lower
        phone = self.root.ids.phone_field.text.strip()

        if not name or not email or not phone:
            self.snack("All fields are required.")
            return
        if not EMAIL_RE.match(email):
            self.snack("Enter a valid email.")
            self.focus_next("email_field"); return
        if not PHONE_RE.match(phone):
            self.snack("Enter valid 10-digit mobile (starts 6-9).")
            self.focus_next("phone_field"); return

        try:
            self.cur.execute("INSERT INTO users(name,email,phone) VALUES (?,?,?)",
                             (name, email, phone))
            self.conn.commit()
            self.snack("Saved ✅")
            # Clear & focus back to Name
            self.root.ids.name_field.text  = ""
            self.root.ids.email_field.text = ""
            self.root.ids.phone_field.text = ""
            self.focus_next("name_field")
        except sqlite3.IntegrityError:
            self.snack("Email or Phone already exists ❌")

    # ---------- View / Delete ----------
    def open_view(self):
        from kivy.lang import Builder as KBuilder
        self.view_screen = KBuilder.load_string(f"""
MDScreen:
    name: "view"
    md_bg_color: 0.05, 0.08, 0.14, 1
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(12)
        spacing: dp(10)

        MDBoxLayout:
            size_hint_y: None
            height: dp(60)
            md_bg_color: 0.07,0.11,0.18,1
            radius: [16,16,16,16]
            padding: dp(12)
            MDLabel:
                text: "Saved Records"
                font_style: "H6"
                bold: True

        MDBoxLayout:
            id: table_holder
            md_bg_color: 0.09, 0.14, 0.22, 1
            radius: [16,16,16,16]

        MDBoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(10)
            MDRaisedButton:
                text: "🗑 Delete Selected"
                md_bg_color: 0.94, 0.26, 0.26, 1
                on_release: app.delete_selected()
            MDRaisedButton:
                text: "✖ Exit (Back)"
                md_bg_color: 0.2, 0.25, 0.32, 1
                on_release: app.close_view()
""")
        self.root.add_widget(self.view_screen)
        self.root.current = "view"

        # Table with checkboxes (multi-select)
        self.table = MDDataTable(
            use_pagination=True,
            rows_num=12,
            check=True,
            column_data=[
                ("ID", dp(60)),
                ("Name", dp(200)),
                ("Email", dp(240)),
                ("Phone", dp(160)),
            ],
            row_data=self.fetch_rows(),
        )
        self.table.bind(on_check_press=self.on_check_press)
        self.view_screen.ids.table_holder.add_widget(self.table)
        self._selected = set()
        Window.bind(on_keyboard=self._android_back_handler)

    def fetch_rows(self):
        self.cur.execute("SELECT id,name,email,phone FROM users ORDER BY id DESC")
        return [tuple(r) for r in self.cur.fetchall()]

    def on_check_press(self, table, row):
        if row in self._selected:
            self._selected.remove(row)
        else:
            self._selected.add(row)

    def delete_selected(self):
        if not self._selected:
            self.snack("No rows selected.")
            return
        ids = [int(r[0]) for r in self._selected]
        q = ",".join(["?"]*len(ids))
        self.cur.execute(f"DELETE FROM users WHERE id IN ({q})", ids)
        self.conn.commit()
        self._selected.clear()
        # Refresh table; stay on same screen
        self.table.row_data = self.fetch_rows()
        self.snack("Deleted selected record(s).")

    def close_view(self):
        Window.unbind(on_keyboard=self._android_back_handler)
        self.root.remove_widget(self.view_screen)
        self.root.current = "home"

    def _android_back_handler(self, window, key, *args):
        if key == 27:  # Android back button
            self.close_view()
            return True
        return False

    # ---------- Export ----------
    def export_csv(self):
        path = os.path.join(os.getcwd(), "users.csv")  # App sandbox folder
        self.cur.execute("SELECT name,email,phone FROM users ORDER BY id")
        rows = self.cur.fetchall()
        if not rows:
            self.snack("No data to export.")
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Name","Email","Phone"])
            w.writerows(rows)
        self.snack("Exported: users.csv")

if __name__ == "__main__":
    SadanandApp().run()
