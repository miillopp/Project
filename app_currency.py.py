import requests
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import ctypes

# Настройка сглаживания шрифтов и четкости интерфейса
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        
        # Размеры окна
        width, height = 750, 950
        self.center_window(self.root, width, height)
        
        # --- ЦВЕТОВАЯ ПАЛИТРА ---
        self.colors = {
            'bg': '#0a1610',
            'card': '#16261e',
            'accent': '#c5f031',
            'text': '#ffffff',
            'text_dim': '#8a9c92',
            'border': '#2a3b30'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        self.history = []
        self.currencies = {
            "USD": "Доллар США", "EUR": "Евро", "RUB": "Рубль РФ",
            "KZT": "Тенге", "BYN": "Белорусский рубль", "GBP": "Фунт",
            "CNY": "Юань", "TRY": "Лира", "CHF": "Франк",
            "JPY": "Иена", "CAD": "Доллар (Кан)", "AUD": "Доллар (Австр)"
        }
        
        self.setup_styles()
        self.setup_ui()

    def center_window(self, window, width, height):
        """Функция для центрирования окна на экране"""
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        font_main = ('Segoe UI', 11)
        font_bold = ('Segoe UI', 11, 'bold')

        style.configure("Treeview", 
                        background=self.colors['card'], 
                        foreground=self.colors['text'], 
                        fieldbackground=self.colors['card'], 
                        rowheight=35,
                        font=font_main,
                        borderwidth=0)
        style.configure("Treeview.Heading", 
                        background=self.colors['border'], 
                        foreground=self.colors['accent'], 
                        font=font_bold,
                        borderwidth=0)
        
        style.configure("TCombobox", padding=8)
        self.root.option_add('*TCombobox*Listbox.font', font_main)

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg=self.colors['bg'], padx=30, pady=20)
        main_frame.pack(fill="both", expand=True)

        header = tk.Frame(main_frame, bg=self.colors['bg'])
        header.pack(fill="x", pady=(0, 20))
        
        tk.Label(header, text="CURRENCY", font=("Verdana", 20, "bold"), 
                 bg=self.colors['bg'], fg=self.colors['text']).pack(side="left")
        tk.Label(header, text="CONVERTER", font=("Verdana", 20, "bold"), 
                 bg=self.colors['bg'], fg=self.colors['accent']).pack(side="left", padx=5)

        lbl_table = tk.Label(main_frame, text="📊 Справочник валют", font=("Segoe UI", 12, "bold"), 
                             bg=self.colors['bg'], fg=self.colors['text_dim'])
        lbl_table.pack(anchor="w", pady=(0, 5))

        table_container = tk.Frame(main_frame, bg=self.colors['card'], highlightthickness=1, highlightbackground=self.colors['border'])
        table_container.pack(fill="x", pady=(0, 20))

        self.tree = ttk.Treeview(table_container, columns=("code", "name"), show="headings", height=6)
        self.tree.heading("code", text="  Код", anchor="w")
        self.tree.heading("name", text="  Валюта", anchor="w")
        self.tree.column("code", width=120, anchor="w")
        self.tree.column("name", width=430, anchor="w")
        
        for code, name in self.currencies.items():
            self.tree.insert("", "end", values=(f"  {code}", f"  {name}"))
        
        self.tree.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        input_card = tk.Frame(main_frame, bg=self.colors['card'], padx=20, pady=20, 
                              highlightthickness=1, highlightbackground=self.colors['border'])
        input_card.pack(fill="x")

        row_cur = tk.Frame(input_card, bg=self.colors['card'])
        row_cur.pack(fill="x", pady=(0, 15))

        self.from_var = tk.StringVar(value="USD")
        self.from_cb = ttk.Combobox(row_cur, textvariable=self.from_var, values=list(self.currencies.keys()), state="readonly", width=10, font=("Segoe UI", 13))
        self.from_cb.pack(side="left", expand=True)

        tk.Button(row_cur, text="⇄", command=self.swap, font=("Segoe UI", 16), 
                  bg=self.colors['card'], fg=self.colors['accent'], relief="flat", bd=0, cursor="hand2").pack(side="left", padx=20)

        self.to_var = tk.StringVar(value="RUB")
        self.to_cb = ttk.Combobox(row_cur, textvariable=self.to_var, values=list(self.currencies.keys()), state="readonly", width=10, font=("Segoe UI", 13))
        self.to_cb.pack(side="left", expand=True)

        tk.Label(input_card, text="Сумма для перевода:", font=("Segoe UI", 10), bg=self.colors['card'], fg=self.colors['text_dim']).pack(anchor="w")
        self.amount_var = tk.StringVar(value="100.00")
        self.entry = tk.Entry(input_card, textvariable=self.amount_var, font=("Segoe UI", 24, "bold"), 
                               bg=self.colors['bg'], fg=self.colors['text'], justify="center", relief="flat", insertbackground="white")
        self.entry.pack(fill="x", pady=10, ipady=10)

        self.btn = tk.Button(main_frame, text="КОНВЕРТИРОВАТЬ", command=self.convert, 
                             bg=self.colors['accent'], fg=self.colors['bg'], font=("Segoe UI", 14, "bold"), 
                             relief="flat", bd=0, cursor="hand2")
        self.btn.pack(fill="x", pady=20, ipady=15)

        self.res_label = tk.Label(main_frame, text="---", font=("Segoe UI", 28, "bold"), 
                                  bg=self.colors['bg'], fg=self.colors['text'])
        self.res_label.pack(pady=10)

        tk.Button(main_frame, text="📜 Показать историю поиска", command=self.open_history, 
                  bg=self.colors['bg'], fg=self.colors['accent'], font=("Segoe UI", 10, "underline"), 
                  relief="flat", cursor="hand2").pack(side="bottom", pady=10)

    def swap(self):
        f, t = self.from_var.get(), self.to_var.get()
        self.from_var.set(t)
        self.to_var.set(f)

    def convert(self):
        try:
            amt = float(self.amount_var.get().replace(",", "."))
            base, target = self.from_var.get(), self.to_var.get()
            self.btn.config(state="disabled", text="ЗАГРУЗКА...")
            threading.Thread(target=self._fetch, args=(amt, base, target), daemon=True).start()
        except:
            messagebox.showerror("Ошибка", "Введите число")

    def _fetch(self, amt, base, target):
        try:
            url = f"https://open.er-api.com/v6/latest/{base}"
            data = requests.get(url).json()
            rate = data["rates"][target]
            total = amt * rate
            self.history.append(f"[{datetime.now().strftime('%H:%M')}] {amt} {base} → {total:.2f} {target}")
            self.root.after(0, lambda: self.res_label.config(text=f"{total:,.2f} {target}"))
        except:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", "Нет связи"))
        finally:
            self.root.after(0, lambda: self.btn.config(state="normal", text="КОНВЕРТИРОВАТЬ"))

    def open_history(self):
        h_win = tk.Toplevel(self.root)
        h_win.title("История поиска")
        # Центрируем окно истории
        self.center_window(h_win, 500, 480)
        h_win.configure(bg=self.colors['card'])
        
        tk.Label(h_win, text="ПОСЛЕДНИЕ ОПЕРАЦИИ", font=("Segoe UI", 12, "bold"), 
                 bg=self.colors['card'], fg=self.colors['accent']).pack(pady=15)
        
        listbox = tk.Listbox(h_win, bg=self.colors['bg'], fg=self.colors['text'], 
                             font=("Segoe UI", 11), relief="flat", borderwidth=10)
        listbox.pack(fill="both", expand=True, padx=20, pady=10)
        
        for item in reversed(self.history):
            listbox.insert("end", item)
            
        tk.Button(h_win, text="ЗАКРЫТЬ", command=h_win.destroy, 
                  bg=self.colors['accent'], fg=self.colors['bg'], 
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=5).pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()