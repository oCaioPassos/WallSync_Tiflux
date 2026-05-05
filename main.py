import customtkinter as ctk
import requests
import datetime
from tkinter import messagebox, filedialog
import threading
import json
import os
import time
import re
import tempfile
import subprocess
import pywinstyles
from tkcalendar import Calendar
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageTk

# Cores do Tema Premium Escuro (Padrão Tailwind Zinc)
BG_COLOR = "#09090b"
CARD_COLOR = "#18181b"
BORDER_COLOR = "#27272a"
ACCENT_COLOR = "#3b82f6"
ACCENT_HOVER = "#2563eb"
TEXT_COLOR = "#fafafa"
MUTED_COLOR = "#a1a1aa"
INPUT_BG = "#09090b"
DANGER_COLOR = "#ef4444"
DANGER_HOVER = "#dc2626"
SECONDARY_BTN = "#27272a"
SECONDARY_HOVER = "#3f3f46"
SUCCESS_COLOR = "#22c55e"

ctk.set_appearance_mode("dark")

class TimePicker(ctk.CTkToplevel):
    def __init__(self, parent, current_time_str=None, on_select=None):
        super().__init__(parent)
        self.title("Selecionar Horário")
        self.geometry("320x280")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        
        try:
            pywinstyles.change_header_color(self, color=BG_COLOR)
            pywinstyles.change_border_color(self, color=BORDER_COLOR)
        except Exception:
            pass
            
        self.transient(parent)
        self.grab_set()

        self.on_select = on_select

        if current_time_str is None or current_time_str == "[ Selecionar ]":
            current_time = datetime.datetime.now().time()
        else:
            try:
                current_time = datetime.datetime.strptime(current_time_str, "%H:%M").time()
            except ValueError:
                current_time = datetime.datetime.now().time()

        self.time_frame = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        self.time_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.time_label = ctk.CTkLabel(self.time_frame, text="Horário", font=("Inter", 16, "bold"), text_color=TEXT_COLOR)
        self.time_label.pack(pady=(20, 10))

        self.hm_frame = ctk.CTkFrame(self.time_frame, fg_color="transparent")
        self.hm_frame.pack(pady=10)

        hours = [f"{i:02d}" for i in range(24)]
        self.hour_var = ctk.StringVar(value=f"{current_time.hour:02d}")
        self.hour_cb = ctk.CTkComboBox(self.hm_frame, values=hours, variable=self.hour_var, width=80, font=("Inter", 14), 
                                       fg_color=INPUT_BG, border_color=BORDER_COLOR, text_color=TEXT_COLOR, 
                                       button_color=INPUT_BG, button_hover_color=SECONDARY_HOVER, dropdown_fg_color=CARD_COLOR, dropdown_text_color=TEXT_COLOR)
        self.hour_cb.pack(side="left", padx=5)

        self.colon_label = ctk.CTkLabel(self.hm_frame, text=":", font=("Inter", 18, "bold"), text_color=MUTED_COLOR)
        self.colon_label.pack(side="left")

        minutes = [f"{i:02d}" for i in range(60)]
        self.minute_var = ctk.StringVar(value=f"{current_time.minute:02d}")
        self.minute_cb = ctk.CTkComboBox(self.hm_frame, values=minutes, variable=self.minute_var, width=80, font=("Inter", 14),
                                         fg_color=INPUT_BG, border_color=BORDER_COLOR, text_color=TEXT_COLOR, 
                                         button_color=INPUT_BG, button_hover_color=SECONDARY_HOVER, dropdown_fg_color=CARD_COLOR, dropdown_text_color=TEXT_COLOR)
        self.minute_cb.pack(side="left", padx=5)

        self.btn_confirm = ctk.CTkButton(self.time_frame, text="✔ Confirmar", command=self.confirm, font=("Inter", 14, "bold"), height=45,
                                         fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, text_color="#ffffff", corner_radius=10)
        self.btn_confirm.pack(side="bottom", pady=25)

    def confirm(self):
        try:
            h = int(self.hour_var.get())
            m = int(self.minute_var.get())
            selected_time_str = f"{h:02d}:{m:02d}"
            if self.on_select:
                self.on_select(selected_time_str)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao selecionar horário: {str(e)}")


class DateTimePicker(ctk.CTkToplevel):
    def __init__(self, parent, current_date=None, on_select=None):
        super().__init__(parent)
        self.title("Selecionar Data e Hora")
        self.geometry("600x420")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        
        try:
            pywinstyles.change_header_color(self, color=BG_COLOR)
            pywinstyles.change_border_color(self, color=BORDER_COLOR)
        except Exception:
            pass
            
        self.transient(parent)
        self.grab_set()

        self.on_select = on_select

        if current_date is None:
            current_date = datetime.datetime.now()

        # Frame for Calendar
        self.cal_frame = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        self.cal_frame.pack(side="left", padx=20, pady=20, fill="both", expand=True)

        self.calendar = Calendar(self.cal_frame, selectmode='day', 
                                 locale='pt_BR',
                                 firstweekday='sunday',
                                 year=current_date.year, 
                                 month=current_date.month, 
                                 day=current_date.day,
                                 font="Arial 11",
                                 headersbackground=CARD_COLOR,
                                 headersforeground=MUTED_COLOR,
                                 selectbackground=ACCENT_COLOR,
                                 selectforeground="#ffffff",
                                 normalbackground=INPUT_BG,
                                 normalforeground=TEXT_COLOR,
                                 background=CARD_COLOR,
                                 foreground=TEXT_COLOR,
                                 bordercolor=BORDER_COLOR,
                                 othermonthforeground=MUTED_COLOR,
                                 othermonthbackground=INPUT_BG,
                                 othermonthweforeground=MUTED_COLOR,
                                 othermonthwebackground=INPUT_BG,
                                 webackground=INPUT_BG,
                                 weforeground=TEXT_COLOR)
        self.calendar.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame for Time
        self.time_frame = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        self.time_frame.pack(side="right", padx=(0, 20), pady=20, fill="y")

        self.time_label = ctk.CTkLabel(self.time_frame, text="Horário", font=("Inter", 16, "bold"), text_color=TEXT_COLOR)
        self.time_label.pack(pady=(40, 10))

        # Hours and Minutes
        self.hm_frame = ctk.CTkFrame(self.time_frame, fg_color="transparent")
        self.hm_frame.pack(pady=10, padx=20)

        hours = [f"{i:02d}" for i in range(24)]
        self.hour_var = ctk.StringVar(value=f"{current_date.hour:02d}")
        self.hour_cb = ctk.CTkComboBox(self.hm_frame, values=hours, variable=self.hour_var, width=70, font=("Inter", 14),
                                       fg_color=INPUT_BG, border_color=BORDER_COLOR, text_color=TEXT_COLOR,
                                       button_color=INPUT_BG, button_hover_color=SECONDARY_HOVER, dropdown_fg_color=CARD_COLOR, dropdown_text_color=TEXT_COLOR)
        self.hour_cb.pack(side="left", padx=2)

        self.colon_label = ctk.CTkLabel(self.hm_frame, text=":", font=("Inter", 18, "bold"), text_color=MUTED_COLOR)
        self.colon_label.pack(side="left")

        minutes = [f"{i:02d}" for i in range(60)]
        self.minute_var = ctk.StringVar(value=f"{current_date.minute:02d}")
        self.minute_cb = ctk.CTkComboBox(self.hm_frame, values=minutes, variable=self.minute_var, width=70, font=("Inter", 14),
                                         fg_color=INPUT_BG, border_color=BORDER_COLOR, text_color=TEXT_COLOR,
                                         button_color=INPUT_BG, button_hover_color=SECONDARY_HOVER, dropdown_fg_color=CARD_COLOR, dropdown_text_color=TEXT_COLOR)
        self.minute_cb.pack(side="left", padx=2)

        # Confirm Button
        self.btn_confirm = ctk.CTkButton(self.time_frame, text="✔ Confirmar", command=self.confirm, font=("Inter", 14, "bold"), height=45,
                                         fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, text_color="#ffffff", corner_radius=10)
        self.btn_confirm.pack(side="bottom", pady=20, padx=20, fill="x")

    def confirm(self):
        try:
            cal_date = self.calendar.selection_get()
            h = int(self.hour_var.get())
            m = int(self.minute_var.get())
            selected_datetime = datetime.datetime.combine(cal_date, datetime.time(h, m))
            if self.on_select:
                self.on_select(selected_datetime)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao selecionar data/hora: {str(e)}")


class ScriptPickerModal(ctk.CTkToplevel):
    def __init__(self, parent, token, on_select=None):
        super().__init__(parent)
        self.title("Selecionar Script (Wallpaper)")
        self.geometry("600x500")
        self.minsize(500, 400)
        self.configure(fg_color=BG_COLOR)
        
        try:
            pywinstyles.change_header_color(self, color=BG_COLOR)
            pywinstyles.change_border_color(self, color=BORDER_COLOR)
        except Exception:
            pass
            
        self.transient(parent)
        self.grab_set()
        
        self.on_select = on_select
        self.token = token
        
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self.header_frame, placeholder_text="Pesquisar...", textvariable=self.search_var, 
                                         font=("Inter", 14), height=40, fg_color=INPUT_BG, border_color=BORDER_COLOR, 
                                         text_color=TEXT_COLOR, placeholder_text_color=MUTED_COLOR)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.fetch_scripts())
        
        self.btn_search = ctk.CTkButton(self.header_frame, text="Pesquisar", width=100, height=40, font=("Inter", 14, "bold"),
                                        command=self.fetch_scripts, fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER)
        self.btn_search.pack(side="left", padx=(0, 10))
        
        self.loading_label = ctk.CTkLabel(self, text="Carregando scripts...", font=("Inter", 14), text_color=MUTED_COLOR)
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=CARD_COLOR, corner_radius=12, border_color=BORDER_COLOR, border_width=1)
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.scripts_data = []
        self.selected_id_var = ctk.IntVar(value=0)
        
        self.btn_confirm = ctk.CTkButton(self, text="✔ Confirmar Seleção", command=self.confirm, font=("Inter", 14, "bold"), height=45,
                                         fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, text_color="#ffffff", corner_radius=10)
        self.btn_confirm.pack(fill="x", padx=20, pady=(0, 20))
        
        self.fetch_scripts()

    def fetch_scripts(self, limit=15):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        self.loading_label.pack(after=self.header_frame, pady=10)
        self.update_idletasks()
        
        def run_fetch():
            import urllib.parse
            term = self.search_var.get().strip()
            # As requested, there is a space after wallpaper
            raw_search = f"wallpaper {term}" if term else "wallpaper "
            
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}", "Accept": "application/json"}
            all_scripts = []
            page = 1
            
            try:
                while True:
                    url = "https://app.tiflux.com/equipment/rmm/scripts"
                    params = {
                        "page": page,
                        "search": raw_search,
                        "limit": limit,
                        "run_type": "execution"
                    }
                    response = requests.get(url, headers=headers, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        scripts = data.get("data", [])
                        all_scripts.extend(scripts)
                        if len(scripts) < limit:
                            break
                        page += 1
                    else:
                        self.after(0, lambda r=response.status_code: messagebox.showerror("Erro API", f"Status code: {r}"))
                        self.after(0, self.loading_label.pack_forget)
                        return
                        
                self.scripts_data = all_scripts
                self.scripts_data.sort(key=lambda x: x.get("created_at", ""), reverse=True)
                self.after(0, self.populate_list)
            except Exception as e:
                self.after(0, lambda err=str(e): messagebox.showerror("Erro", f"Falha na comunicação: {err}"))
                self.after(0, self.loading_label.pack_forget)
                
        threading.Thread(target=run_fetch, daemon=True).start()

    def populate_list(self):
        self.loading_label.pack_forget()
        if not self.scripts_data:
            ctk.CTkLabel(self.scroll_frame, text="Nenhum script encontrado.", font=("Inter", 14), text_color=MUTED_COLOR).pack(pady=20)
            return
            
        for script in self.scripts_data:
            script_id = script.get("id")
            script_name = script.get("name")
            display_text = f"[{script_id}] {script_name}"
            
            rb = ctk.CTkRadioButton(self.scroll_frame, text=display_text, variable=self.selected_id_var, value=script_id,
                                    font=("Inter", 14), text_color=TEXT_COLOR, hover_color=SECONDARY_HOVER)
            rb.pack(anchor="w", padx=10, pady=10)
            
    def confirm(self):
        selected_id = self.selected_id_var.get()
        if selected_id == 0:
            messagebox.showwarning("Aviso", "Por favor, selecione um script.")
            return
            
        selected_name = next((s["name"] for s in self.scripts_data if s["id"] == selected_id), "")
        if self.on_select:
            self.on_select(selected_id, selected_name)
        self.destroy()


class ScheduleManagerModal(ctk.CTkToplevel):
    DIAS_SEMANA = {0: "Segunda", 1: "Terça", 2: "Quarta", 3: "Quinta", 4: "Sexta", 5: "Sábado", 6: "Domingo"}

    def __init__(self, parent, token):
        super().__init__(parent)
        self.title("Consultar Agendamentos — WallSync Tiflux")
        self.geometry("800x700")
        self.minsize(650, 500)
        self.configure(fg_color=BG_COLOR)
        try:
            pywinstyles.change_header_color(self, color=BG_COLOR)
            pywinstyles.change_border_color(self, color=BORDER_COLOR)
        except Exception:
            pass
        self.transient(parent)
        self.grab_set()

        self.token = token
        self.item_vars = {}
        self.day_vars = {}
        self.day_item_ids = {}
        self.is_deleting = False

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(24, 12))
        ctk.CTkLabel(header, text="📋 Consultar Agendamentos", font=("Inter", 20, "bold"), text_color=TEXT_COLOR).pack(side="left")

        # Search
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.pack(fill="x", padx=24, pady=(0, 10))
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(sf, placeholder_text="Pesquisar por nome do script...", textvariable=self.search_var,
                                         font=("Inter", 14), height=40, fg_color=INPUT_BG, border_color=BORDER_COLOR,
                                         text_color=TEXT_COLOR, placeholder_text_color=MUTED_COLOR)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.refresh())
        ctk.CTkButton(sf, text="🔄 Buscar", width=100, height=40, font=("Inter", 14, "bold"),
                      command=self.refresh, fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER).pack(side="left")

        # Status
        stf = ctk.CTkFrame(self, fg_color="transparent")
        stf.pack(fill="x", padx=24, pady=(0, 6))
        self.status_label = ctk.CTkLabel(stf, text="Carregando...", font=("Inter", 13), text_color=MUTED_COLOR)
        self.status_label.pack(side="left")
        self.selected_label = ctk.CTkLabel(stf, text="0 selecionados", font=("Inter", 13, "bold"), text_color=ACCENT_COLOR)
        self.selected_label.pack(side="right")

        # Scroll list
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=CARD_COLOR, corner_radius=12, border_color=BORDER_COLOR, border_width=1)
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        self.scroll.grid_columnconfigure(0, weight=1)

        # Actions
        af = ctk.CTkFrame(self, fg_color="transparent")
        af.pack(fill="x", padx=24, pady=(0, 24))
        self.btn_sel_all = ctk.CTkButton(af, text="☑ Selecionar Todos", width=170, height=45, font=("Inter", 14, "bold"),
                                         fg_color=SECONDARY_BTN, hover_color=SECONDARY_HOVER, text_color=TEXT_COLOR,
                                         corner_radius=10, command=self.toggle_select_all)
        self.btn_sel_all.pack(side="left", padx=(0, 10))
        self.btn_delete = ctk.CTkButton(af, text="🗑️ Excluir Selecionados", width=210, height=45, font=("Inter", 14, "bold"),
                                        fg_color=DANGER_COLOR, hover_color=DANGER_HOVER, text_color="#ffffff",
                                        corner_radius=10, command=self.delete_selected)
        self.btn_delete.pack(side="right")

        self._all_selected = False
        self.refresh()

    # ---------- Fetch ----------
    def refresh(self):
        self.status_label.configure(text="Carregando agendamentos...")
        for w in self.scroll.winfo_children():
            w.destroy()
        self.item_vars.clear()
        self.day_vars.clear()
        self.day_item_ids.clear()
        self._all_selected = False
        self._update_count()
        threading.Thread(target=self._fetch_thread, daemon=True).start()

    def _fetch_thread(self):
        search = self.search_var.get().strip()
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}", "Accept": "application/json"}
        all_data, page, limit = [], 1, 15
        try:
            while True:
                r = None
                for attempt in range(3):
                    try:
                        r = requests.get("https://app.tiflux.com/equipment/rmm/batch_script_actions",
                                         headers=headers, params={"limit": limit, "page": page, "search": search, "order_by": ""}, timeout=30)
                        break
                    except requests.exceptions.Timeout:
                        if attempt < 2:
                            time.sleep(2)
                            continue
                        raise
                if r is None or r.status_code != 200:
                    sc = r.status_code if r else 0
                    self.after(0, lambda s=sc: messagebox.showerror("Erro API", f"Status: {s}"))
                    self.after(0, lambda: self.status_label.configure(text="Erro ao carregar."))
                    return
                body = r.json()
                data = body.get("data", [])
                all_data.extend(data)
                total = body.get("total", 0)
                if self.winfo_exists():
                    self.after(0, lambda t=total, c=len(all_data): self.status_label.configure(
                        text=f"Carregando... {c}/{t} agendamentos") if self.winfo_exists() else None)
                if len(all_data) >= total or len(data) == 0:
                    break
                page += 1
        except Exception as e:
            if self.winfo_exists():
                self.after(0, lambda err=str(e): messagebox.showerror("Erro", f"Falha: {err}"))
                self.after(0, lambda: self.status_label.configure(text="Erro de conexão."))
            return

        from collections import defaultdict
        grouped = defaultdict(list)
        for item in all_data:
            try:
                dt = datetime.datetime.fromisoformat(item["scheduled_date"])
                item["_dt"] = dt
                grouped[dt.strftime("%Y-%m-%d")].append(item)
            except Exception:
                continue
        for k in grouped:
            grouped[k].sort(key=lambda x: x["_dt"])
        self.after(0, lambda: self._populate(sorted(grouped.keys()), grouped, len(all_data)))

    # ---------- Populate ----------
    def _populate(self, sorted_days, grouped, total):
        self.status_label.configure(text=f"{total} agendamento(s) encontrado(s)")
        self.day_items_frames = {}
        self.day_toggle_btns = {}
        if total == 0:
            ctk.CTkLabel(self.scroll, text="Nenhum agendamento encontrado.", font=("Inter", 14), text_color=MUTED_COLOR).pack(pady=30)
            return
        for day_key in sorted_days:
            items = grouped[day_key]
            dt0 = items[0]["_dt"]
            day_name = self.DIAS_SEMANA.get(dt0.weekday(), "")
            day_display = dt0.strftime("%d/%m/%Y")
            scripts = set(it.get("script_name", "?") for it in items)
            scripts_txt = ", ".join(scripts) if len(scripts) <= 2 else f"{next(iter(scripts))} (+{len(scripts)-1})"

            # Day frame
            df = ctk.CTkFrame(self.scroll, fg_color=INPUT_BG, corner_radius=10, border_width=1, border_color=BORDER_COLOR)
            df.pack(fill="x", padx=8, pady=(0, 10))
            df.grid_columnconfigure(0, weight=1)

            # Day header
            dvar = ctk.BooleanVar(value=False)
            self.day_vars[day_key] = dvar
            self.day_item_ids[day_key] = []
            hdr = ctk.CTkFrame(df, fg_color="transparent")
            hdr.pack(fill="x", padx=12, pady=(12, 6))

            # Toggle button (+/-)
            toggle_btn = ctk.CTkButton(hdr, text="+", width=30, height=30, font=("Inter", 16, "bold"),
                                       fg_color=SECONDARY_BTN, hover_color=SECONDARY_HOVER, text_color=TEXT_COLOR,
                                       corner_radius=6, command=lambda dk=day_key: self._toggle_day_expand(dk))
            toggle_btn.pack(side="left", padx=(0, 8))
            self.day_toggle_btns[day_key] = toggle_btn

            ctk.CTkCheckBox(hdr, text="", variable=dvar, width=24, fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER,
                            border_color=BORDER_COLOR, command=lambda dk=day_key: self._on_day_toggle(dk)).pack(side="left", padx=(0, 8))
            ctk.CTkLabel(hdr, text=f"📅 {day_display} ({day_name})", font=("Inter", 15, "bold"), text_color=TEXT_COLOR).pack(side="left")
            ctk.CTkLabel(hdr, text=f"{len(items)} agend.", font=("Inter", 13), text_color=MUTED_COLOR).pack(side="right", padx=(10, 0))
            ctk.CTkLabel(hdr, text=scripts_txt, font=("Inter", 12), text_color=MUTED_COLOR).pack(side="right")

            # Items container (starts hidden)
            items_frame = ctk.CTkFrame(df, fg_color="transparent")
            self.day_items_frames[day_key] = items_frame

            for it in items:
                sid = it["id"]
                iv = ctk.BooleanVar(value=False)
                self.item_vars[sid] = iv
                self.day_item_ids[day_key].append(sid)
                hora = it["_dt"].strftime("%H:%M")
                row = ctk.CTkFrame(items_frame, fg_color="transparent")
                row.pack(fill="x", padx=(36, 12), pady=2)
                ctk.CTkCheckBox(row, text="", variable=iv, width=24, fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER,
                                border_color=BORDER_COLOR, command=lambda dk=day_key: self._on_item_toggle(dk)).pack(side="left", padx=(0, 8))
                ctk.CTkLabel(row, text=f"🕒 {hora}", font=("Inter", 13, "bold"), text_color=TEXT_COLOR).pack(side="left", padx=(0, 10))
                ctk.CTkLabel(row, text=it.get("script_name", "—"), font=("Inter", 13), text_color=MUTED_COLOR).pack(side="left")
                ctk.CTkLabel(row, text=f"ID {sid}", font=("Inter", 11), text_color="#52525b").pack(side="right")

            ctk.CTkFrame(df, fg_color="transparent", height=6).pack()

    def _toggle_day_expand(self, day_key):
        frame = self.day_items_frames.get(day_key)
        btn = self.day_toggle_btns.get(day_key)
        if frame is None:
            return
        if frame.winfo_ismapped():
            frame.pack_forget()
            btn.configure(text="+")
        else:
            frame.pack(fill="x", after=frame.master.winfo_children()[0])
            btn.configure(text="−")

    # ---------- Selection helpers ----------
    def _on_day_toggle(self, day_key):
        val = self.day_vars[day_key].get()
        for sid in self.day_item_ids[day_key]:
            self.item_vars[sid].set(val)
        self._update_count()

    def _on_item_toggle(self, day_key):
        ids = self.day_item_ids[day_key]
        all_checked = all(self.item_vars[sid].get() for sid in ids)
        self.day_vars[day_key].set(all_checked)
        self._update_count()

    def _update_count(self):
        n = sum(1 for v in self.item_vars.values() if v.get())
        self.selected_label.configure(text=f"{n} selecionado(s)")

    def toggle_select_all(self):
        self._all_selected = not self._all_selected
        for v in self.item_vars.values():
            v.set(self._all_selected)
        for v in self.day_vars.values():
            v.set(self._all_selected)
        self._update_count()
        self.btn_sel_all.configure(text="☐ Desmarcar Todos" if self._all_selected else "☑ Selecionar Todos")

    # ---------- Delete ----------
    def delete_selected(self):
        if self.is_deleting:
            return
        ids = [sid for sid, v in self.item_vars.items() if v.get()]
        if not ids:
            messagebox.showinfo("Aviso", "Nenhum agendamento selecionado.")
            return
        confirm = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Você está prestes a excluir {len(ids)} agendamento(s).\n\n"
            "Essa ação não pode ser desfeita.\nDeseja continuar?"
        )
        if not confirm:
            return
        self.is_deleting = True
        self.btn_delete.configure(state="disabled", text="Excluindo...")
        threading.Thread(target=self._run_delete, args=(ids,), daemon=True).start()

    def _run_delete(self, ids):
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        ok, fail = 0, 0
        errors_detail = []

        def do_delete(sid):
            try:
                r = requests.put(f"https://app.tiflux.com/equipment/rmm/batch_script_actions/{sid}/cancel_scripts",
                                 headers=headers, timeout=15)
                return sid, r.status_code in (200, 201, 204), r.status_code, r.text[:200]
            except Exception as e:
                return sid, False, 0, str(e)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(do_delete, sid): sid for sid in ids}
            for future in as_completed(futures):
                sid, success, status, detail = future.result()
                if success:
                    ok += 1
                else:
                    fail += 1
                    errors_detail.append(f"ID {sid}: Status {status} — {detail}")

        def finalize():
            self.is_deleting = False
            self.btn_delete.configure(state="normal", text="🗑️ Excluir Selecionados")
            msg = f"✅ {ok} excluído(s) com sucesso."
            if fail > 0:
                msg += f"\n❌ {fail} falha(s) na exclusão."
                msg += f"\n\nDetalhes dos erros:\n" + "\n".join(errors_detail[:10])
            messagebox.showinfo("Resultado da Exclusão", msg)
            self.refresh()

        self.after(0, finalize)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WallSync Tiflux")
        self.geometry("1100x680")
        self.minsize(960, 600)
        self.configure(fg_color=BG_COLOR)
        
        # Aplica dark mode nativo para a barra de título e bordas
        try:
            pywinstyles.change_header_color(self, color=BG_COLOR)
            pywinstyles.change_border_color(self, color=BORDER_COLOR)
        except Exception:
            pass

        # Fontes padrão
        self.font_title = ctk.CTkFont(family="Inter", size=24, weight="bold")
        self.font_subtitle = ctk.CTkFont(family="Inter", size=16, weight="bold")
        self.font_text = ctk.CTkFont(family="Inter", size=14)
        self.font_text_bold = ctk.CTkFont(family="Inter", size=14, weight="bold")
        self.font_btn = ctk.CTkFont(family="Inter", size=14, weight="bold")
        self.font_log = ctk.CTkFont(family="Consolas", size=13)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==================== SIDEBAR ====================
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color=CARD_COLOR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)
        
        # Logo com ícone
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, padx=20, pady=(40, 40), sticky="ew")
        
        self.logo_icon = ctk.CTkLabel(self.logo_frame, text="🔄", font=ctk.CTkFont(size=32))
        self.logo_icon.pack(pady=(0, 5))
        self.logo_label = ctk.CTkLabel(self.logo_frame, text="WallSync\nTiflux", font=self.font_title, text_color=TEXT_COLOR, justify="center")
        self.logo_label.pack()

        # Botões da Sidebar
        self.btn_start = ctk.CTkButton(self.sidebar, text="▶ Iniciar Agendamentos", font=self.font_btn, height=50, corner_radius=12,
                                       fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, text_color="#ffffff", command=self.start_process)
        self.btn_start.grid(row=1, column=0, padx=24, pady=10, sticky="ew")

        self.btn_cancel = ctk.CTkButton(self.sidebar, text="⏹ Cancelar Execução", font=self.font_btn, height=50, corner_radius=12,
                                        fg_color=SECONDARY_BTN, hover_color=SECONDARY_BTN, text_color=MUTED_COLOR, state="disabled", command=self.cancel_process)
        self.btn_cancel.grid(row=2, column=0, padx=24, pady=10, sticky="ew")

        self.btn_export = ctk.CTkButton(self.sidebar, text="📥 Exportar Logs", font=self.font_btn, height=50, corner_radius=12,
                                        fg_color="transparent", border_width=2, border_color=BORDER_COLOR, hover_color=SECONDARY_HOVER, text_color=TEXT_COLOR, command=self.export_logs)
        self.btn_export.grid(row=3, column=0, padx=24, pady=10, sticky="ew")

        self.btn_manage = ctk.CTkButton(self.sidebar, text="📋 Consultar Agendamentos", font=self.font_btn, height=50, corner_radius=12,
                                        fg_color="transparent", border_width=2, border_color=BORDER_COLOR, hover_color=SECONDARY_HOVER, text_color=TEXT_COLOR, command=self.open_schedule_manager)
        self.btn_manage.grid(row=4, column=0, padx=24, pady=10, sticky="ew")

        # Versão ou Footer
        self.footer_label = ctk.CTkLabel(self.sidebar, text="v1.0.0\nPowered by Caio Master", font=ctk.CTkFont(family="Inter", size=12), text_color=MUTED_COLOR, justify="center")
        self.footer_label.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # ==================== MAIN CONTENT ====================
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_scroll.grid_columnconfigure(0, weight=1)

        # --- CARD 1: Configurações da API ---
        self.card_api = ctk.CTkFrame(self.main_scroll, corner_radius=16, fg_color=CARD_COLOR, border_width=1, border_color=BORDER_COLOR)
        self.card_api.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.card_api.grid_columnconfigure(1, weight=1)
        
        self.header_api = ctk.CTkFrame(self.card_api, fg_color="transparent")
        self.header_api.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=(20, 15))
        ctk.CTkLabel(self.header_api, text="Configurações da API", font=self.font_subtitle, text_color=TEXT_COLOR).pack(side="left")
        
        # Token
        ctk.CTkLabel(self.card_api, text="Bearer Token", font=self.font_text, text_color=MUTED_COLOR).grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")
        self.entry_token = ctk.CTkEntry(self.card_api, placeholder_text="Insira o seu Bearer Token", font=self.font_text, show="*", height=40,
                                        fg_color=INPUT_BG, border_color=BORDER_COLOR, text_color=TEXT_COLOR, placeholder_text_color=MUTED_COLOR)
        self.entry_token.grid(row=1, column=1, padx=(0, 10), pady=(0, 15), sticky="ew")
        self.entry_token.bind("<FocusOut>", lambda e: self.save_current_state())
        
        self.token_visible = False
        self.btn_show_token = ctk.CTkButton(self.card_api, text="👁 Mostrar", width=90, height=40, font=self.font_text_bold, command=self.toggle_token_visibility, 
                                            fg_color="transparent", border_width=1, border_color=BORDER_COLOR, hover_color=SECONDARY_HOVER, text_color=TEXT_COLOR, corner_radius=8)
        self.btn_show_token.grid(row=1, column=2, padx=(0, 20), pady=(0, 15))

        # Script ID
        ctk.CTkLabel(self.card_api, text="Script Selecionado", font=self.font_text, text_color=MUTED_COLOR).grid(row=2, column=0, padx=20, pady=(0, 25), sticky="w")
        
        self.script_frame = ctk.CTkFrame(self.card_api, fg_color="transparent")
        self.script_frame.grid(row=2, column=1, columnspan=2, padx=(0, 20), pady=(0, 25), sticky="ew")
        
        self.selected_script_id = None
        self.selected_script_name = ""
        self.script_var = ctk.StringVar(value="🔍 Clique para selecionar o Script")
        
        self.btn_select_script = ctk.CTkButton(self.script_frame, textvariable=self.script_var, font=self.font_text, height=40,
                                               fg_color=INPUT_BG, border_color=BORDER_COLOR, border_width=1, text_color=TEXT_COLOR, 
                                               hover_color=SECONDARY_HOVER, anchor="w", command=self.open_script_modal)
        self.btn_select_script.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_clear_script = ctk.CTkButton(self.script_frame, text="✖ Limpar", width=80, height=40, font=self.font_text_bold, 
                                              fg_color="transparent", border_width=1, border_color=BORDER_COLOR, hover_color=SECONDARY_HOVER, 
                                              text_color=MUTED_COLOR, corner_radius=8, command=self.clear_script)
        self.btn_clear_script.pack(side="left")

        # --- Preview do Wallpaper ---
        self.preview_frame = ctk.CTkFrame(self.card_api, fg_color=INPUT_BG, corner_radius=10, border_width=1, border_color=BORDER_COLOR)
        self.preview_frame.grid(row=3, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="ew")

        # Título do preview
        self.preview_header = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
        self.preview_header.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(self.preview_header, text="🖼️ Preview do Wallpaper", font=("Inter", 14, "bold"), text_color=TEXT_COLOR).pack(side="left")

        self.btn_preview = ctk.CTkButton(self.preview_header, text="🔎 Abrir em Tela Cheia", font=("Inter", 12, "bold"), height=30, width=160,
                                         fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, text_color="#ffffff",
                                         corner_radius=8, command=self.open_preview_fullscreen, state="disabled")
        self.btn_preview.pack(side="right")

        # Área da imagem
        self.preview_img_container = ctk.CTkFrame(self.preview_frame, fg_color="#09090b", corner_radius=8, height=200)
        self.preview_img_container.pack(fill="x", padx=16, pady=(10, 14))
        self.preview_img_container.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(self.preview_img_container, text="Nenhum script selecionado", font=("Inter", 13), text_color=MUTED_COLOR)
        self.preview_label.pack(expand=True)

        self.preview_image_label = None
        self.preview_photo = None
        self.wallpaper_temp_path = None

        self.config_file = "config.json"
        self.load_config()

        # --- CARD 2: Parâmetros de Agendamento ---
        self.card_sched = ctk.CTkFrame(self.main_scroll, corner_radius=16, fg_color=CARD_COLOR, border_width=1, border_color=BORDER_COLOR)
        self.card_sched.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.card_sched.grid_columnconfigure(1, weight=1)

        self.header_sched = ctk.CTkFrame(self.card_sched, fg_color="transparent")
        self.header_sched.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 15))
        ctk.CTkLabel(self.header_sched, text="Parâmetros de Agendamento", font=self.font_subtitle, text_color=TEXT_COLOR).pack(side="left")

        # Início e Fim (Datas)
        self.dates_frame = ctk.CTkFrame(self.card_sched, fg_color="transparent")
        self.dates_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 15))
        self.dates_frame.grid_columnconfigure((0, 1), weight=1)

        # Início
        self.start_frame = ctk.CTkFrame(self.dates_frame, fg_color="transparent")
        self.start_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(self.start_frame, text="Data/Hora Início", font=self.font_text, text_color=MUTED_COLOR).pack(anchor="w", pady=(0, 5))
        self.start_date_val = None
        self.start_date_var = ctk.StringVar(value="📅 Selecionar")
        self.btn_start_date = ctk.CTkButton(self.start_frame, textvariable=self.start_date_var, command=lambda: self.open_datetime_picker("start"), 
                                            font=self.font_text, height=42, corner_radius=8, fg_color=INPUT_BG, border_color=BORDER_COLOR, border_width=1, text_color=TEXT_COLOR, hover_color=SECONDARY_HOVER)
        self.btn_start_date.pack(fill="x")

        # Fim
        self.end_frame = ctk.CTkFrame(self.dates_frame, fg_color="transparent")
        self.end_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(self.end_frame, text="Data/Hora Fim", font=self.font_text, text_color=MUTED_COLOR).pack(anchor="w", pady=(0, 5))
        self.end_date_val = None
        self.end_date_var = ctk.StringVar(value="📅 Selecionar")
        self.btn_end_date = ctk.CTkButton(self.end_frame, textvariable=self.end_date_var, command=lambda: self.open_datetime_picker("end"), 
                                          font=self.font_text, height=42, corner_radius=8, fg_color=INPUT_BG, border_color=BORDER_COLOR, border_width=1, text_color=TEXT_COLOR, hover_color=SECONDARY_HOVER)
        self.btn_end_date.pack(fill="x")

        # Intervalo
        self.interval_frame = ctk.CTkFrame(self.card_sched, fg_color="transparent")
        self.interval_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 15))
        ctk.CTkLabel(self.interval_frame, text="Intervalo de Envio (minutos)", font=self.font_text, text_color=MUTED_COLOR).pack(anchor="w", pady=(0, 5))
        self.entry_interval = ctk.CTkEntry(self.interval_frame, placeholder_text="Ex: 30", width=200, font=self.font_text, height=40,
                                           fg_color=INPUT_BG, border_color=BORDER_COLOR, text_color=TEXT_COLOR, placeholder_text_color=MUTED_COLOR)
        self.entry_interval.pack(anchor="w")

        # Expediente
        self.exp_container = ctk.CTkFrame(self.card_sched, fg_color=INPUT_BG, corner_radius=8, border_width=1, border_color=BORDER_COLOR)
        self.exp_container.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20, pady=(5, 25))
        self.exp_container.grid_columnconfigure(1, weight=1)

        self.chk_expediente_var = ctk.BooleanVar(value=False)
        self.chk_expediente = ctk.CTkCheckBox(self.exp_container, text="Considerar horário de expediente (ignorar fora do horário)", variable=self.chk_expediente_var, 
                                              font=self.font_text_bold, text_color=TEXT_COLOR, command=self.toggle_expediente, 
                                              fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, border_color=BORDER_COLOR)
        self.chk_expediente.grid(row=0, column=0, columnspan=2, padx=15, pady=15, sticky="w")

        self.exp_times_frame = ctk.CTkFrame(self.exp_container, fg_color="transparent")
        # Grid placement is managed in toggle_expediente
        
        self.exp_times_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.exp_start_inner = ctk.CTkFrame(self.exp_times_frame, fg_color="transparent")
        self.exp_start_inner.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(self.exp_start_inner, text="Horário Início", font=self.font_text, text_color=MUTED_COLOR).pack(anchor="w", pady=(0, 5))
        self.exp_start_var = ctk.StringVar(value="🕒 08:00")
        self.btn_exp_start = ctk.CTkButton(self.exp_start_inner, textvariable=self.exp_start_var, command=lambda: self.open_time_picker("start"), 
                                           font=self.font_text, height=42, corner_radius=8, fg_color=CARD_COLOR, border_color=BORDER_COLOR, border_width=1, text_color=TEXT_COLOR, hover_color=SECONDARY_HOVER)
        self.btn_exp_start.pack(fill="x")

        self.exp_end_inner = ctk.CTkFrame(self.exp_times_frame, fg_color="transparent")
        self.exp_end_inner.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ctk.CTkLabel(self.exp_end_inner, text="Horário Fim", font=self.font_text, text_color=MUTED_COLOR).pack(anchor="w", pady=(0, 5))
        self.exp_end_var = ctk.StringVar(value="🕒 18:00")
        self.btn_exp_end = ctk.CTkButton(self.exp_end_inner, textvariable=self.exp_end_var, command=lambda: self.open_time_picker("end"), 
                                         font=self.font_text, height=42, corner_radius=8, fg_color=CARD_COLOR, border_color=BORDER_COLOR, border_width=1, text_color=TEXT_COLOR, hover_color=SECONDARY_HOVER)
        self.btn_exp_end.pack(fill="x")

        self.toggle_expediente()

        # Dias da Semana
        self.days_container = ctk.CTkFrame(self.card_sched, fg_color=INPUT_BG, corner_radius=8, border_width=1, border_color=BORDER_COLOR)
        self.days_container.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 25))
        self.days_container.grid_columnconfigure(0, weight=1)

        self.chk_no_weekends_var = ctk.BooleanVar(value=False)
        self.chk_no_weekends = ctk.CTkCheckBox(self.days_container, text="Não considerar finais de semana (Sáb/Dom)", variable=self.chk_no_weekends_var, 
                                               font=self.font_text_bold, text_color=TEXT_COLOR, command=self.toggle_weekends, 
                                               fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, border_color=BORDER_COLOR)
        self.chk_no_weekends.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        ctk.CTkLabel(self.days_container, text="Considerar dias específicos:", font=self.font_text, text_color=MUTED_COLOR).grid(row=1, column=0, padx=15, pady=(5, 5), sticky="w")

        self.days_frame = ctk.CTkFrame(self.days_container, fg_color="transparent")
        self.days_frame.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        self.day_vars = {}
        days_config = [("Dom", 6), ("Seg", 0), ("Ter", 1), ("Qua", 2), ("Qui", 3), ("Sex", 4), ("Sáb", 5)]
        for i, (day_name, day_idx) in enumerate(days_config):
            var = ctk.BooleanVar(value=True)
            self.day_vars[day_idx] = var
            chk = ctk.CTkCheckBox(self.days_frame, text=day_name, variable=var, font=self.font_text, text_color=TEXT_COLOR, width=60, 
                                  fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, border_color=BORDER_COLOR, command=self.update_weekend_chk)
            chk.grid(row=0, column=i, padx=(0, 10), pady=5)

        # --- CARD 3: Logs de Execução ---
        self.card_logs = ctk.CTkFrame(self.main_scroll, corner_radius=16, fg_color=CARD_COLOR, border_width=1, border_color=BORDER_COLOR)
        self.card_logs.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        self.card_logs.grid_columnconfigure(0, weight=1)
        self.card_logs.grid_rowconfigure(1, weight=1)

        self.header_logs = ctk.CTkFrame(self.card_logs, fg_color="transparent")
        self.header_logs.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 15))
        ctk.CTkLabel(self.header_logs, text="Console de Execução", font=self.font_subtitle, text_color=TEXT_COLOR).pack(side="left")
        
        # Barra de progresso
        self.progress_frame = ctk.CTkFrame(self.card_logs, fg_color="transparent")
        self.progress_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_remove()

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=14, corner_radius=7,
                                                fg_color=INPUT_BG, progress_color=ACCENT_COLOR, border_width=0)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(self.progress_frame, text="0%", font=("Inter", 13, "bold"), text_color=ACCENT_COLOR, width=50)
        self.progress_label.grid(row=0, column=1)

        self.log_box = ctk.CTkTextbox(self.card_logs, height=250, state="disabled", font=self.font_log, 
                                      fg_color=INPUT_BG, border_color=BORDER_COLOR, border_width=1, text_color=MUTED_COLOR)
        self.log_box.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.card_logs.grid_rowconfigure(2, weight=1)

        # Variáveis de Controle
        self.is_cancelled = False
        self.is_running = False
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if "token" in config and config["token"]:
                        self.entry_token.insert(0, config["token"])
                    if "script_id" in config and config["script_id"]:
                        self.selected_script_id = config["script_id"]
                        self.selected_script_name = config.get("script_name", "")
                        self.script_var.set(f"[{self.selected_script_id}] {self.selected_script_name}")
                        self.btn_clear_script.configure(text_color=DANGER_COLOR, hover_color=DANGER_HOVER)
                        if config.get("token"):
                            self.load_wallpaper_preview(self.selected_script_id)
            except Exception as e:
                print(f"Erro ao carregar configuração: {e}")

    def save_current_state(self):
        token = self.entry_token.get().strip()
        self.save_config(token, self.selected_script_id, self.selected_script_name)

    def on_closing(self):
        self.save_current_state()
        self.destroy()

    def save_config(self, token, script_id, script_name=""):
        try:
            config = {
                "token": token,
                "script_id": script_id,
                "script_name": script_name
            }
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")

    def open_script_modal(self):
        token = self.entry_token.get().strip()
        if not token:
            messagebox.showwarning("Aviso", "Insira o Bearer Token primeiro para buscar scripts.")
            return
        ScriptPickerModal(self, token, on_select=self.on_script_selected)
        
    def on_script_selected(self, script_id, script_name):
        self.selected_script_id = script_id
        self.selected_script_name = script_name
        self.script_var.set(f"[{script_id}] {script_name}")
        self.btn_clear_script.configure(text_color=DANGER_COLOR, hover_color=DANGER_HOVER)
        self.save_config(self.entry_token.get().strip(), script_id, script_name)
        self.load_wallpaper_preview(script_id)

    def clear_script(self):
        self.selected_script_id = None
        self.selected_script_name = ""
        self.script_var.set("🔍 Clique para selecionar o Script")
        self.btn_clear_script.configure(text_color=MUTED_COLOR, hover_color=SECONDARY_HOVER)
        self.save_config(self.entry_token.get().strip(), None, "")
        self._clear_preview()

    def _clear_preview(self):
        if self.preview_image_label:
            self.preview_image_label.destroy()
            self.preview_image_label = None
        self.preview_photo = None
        self.wallpaper_temp_path = None
        self.preview_img_container.configure(height=200)
        self.preview_label.configure(text="Nenhum script selecionado")
        self.preview_label.pack(expand=True)
        self.btn_preview.configure(state="disabled")

    def load_wallpaper_preview(self, script_id):
        self.preview_label.configure(text="⏳ Carregando preview...")
        if self.preview_image_label:
            self.preview_image_label.destroy()
            self.preview_image_label = None
        self.btn_preview.configure(state="disabled")
        threading.Thread(target=self._fetch_wallpaper_thread, args=(script_id,), daemon=True).start()

    def _fetch_wallpaper_thread(self, script_id):
        token = self.entry_token.get().strip()
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}", "Accept": "application/json"}
        try:
            r = requests.get(f"https://app.tiflux.com/equipment/rmm/scripts/{script_id}",
                             headers=headers, timeout=30)
            if r.status_code != 200:
                self.after(0, lambda: self.preview_label.configure(text="🖼️ Preview não disponível"))
                return
            data = r.json()
            content = data.get("content", "") or data.get("data", {}).get("content", "")
            if not content:
                self.after(0, lambda: self.preview_label.configure(text="🖼️ Preview não disponível"))
                return

            match = re.search(r'DownloadFile\(["\']?(https?://[^\s"\'\)]+\.(?:png|jpg|jpeg|bmp|webp))', content, re.IGNORECASE)
            if not match:
                match = re.search(r'(https?://[^\s"\'\)]+\.(?:png|jpg|jpeg|bmp|webp))', content, re.IGNORECASE)
            if not match:
                self.after(0, lambda: self.preview_label.configure(text="🖼️ URL do wallpaper não encontrada"))
                return

            img_url = match.group(1)
            img_r = requests.get(img_url, timeout=30)
            if img_r.status_code != 200:
                self.after(0, lambda: self.preview_label.configure(text="🖼️ Falha ao baixar imagem"))
                return

            ext = os.path.splitext(img_url.split('?')[0])[1] or ".png"
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext, prefix="wallsync_")
            tmp.write(img_r.content)
            tmp.close()
            self.wallpaper_temp_path = tmp.name

            img = Image.open(tmp.name)
            # Calculate thumbnail to fill container width
            img.thumbnail((600, 280), Image.LANCZOS)
            self.after(0, lambda im=img: self._show_thumbnail(im))
        except Exception as e:
            self.after(0, lambda: self.preview_label.configure(text=f"🖼️ Erro: {str(e)[:60]}"))

    def _show_thumbnail(self, img):
        self.preview_photo = ImageTk.PhotoImage(img)
        self.preview_label.pack_forget()
        if self.preview_image_label:
            self.preview_image_label.destroy()
        self.preview_image_label = ctk.CTkLabel(self.preview_img_container, text="", image=self.preview_photo)
        self.preview_image_label.pack(expand=True)
        self.preview_img_container.configure(height=img.height + 20)
        self.btn_preview.configure(state="normal")

    def open_preview_fullscreen(self):
        if self.wallpaper_temp_path and os.path.exists(self.wallpaper_temp_path):
            os.startfile(self.wallpaper_temp_path)

    def open_schedule_manager(self):
        token = self.entry_token.get().strip()
        if not token:
            messagebox.showwarning("Aviso", "Insira o Bearer Token primeiro.")
            return
        ScheduleManagerModal(self, token)

    def export_logs(self):
        log_content = self.log_box.get("1.0", "end-1c")
        if not log_content.strip():
            messagebox.showinfo("Exportar", "Não há logs para exportar.")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Salvar Logs Como"
        )
        if filepath:
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(log_content)
                messagebox.showinfo("Sucesso", "Logs exportados com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao exportar logs: {str(e)}")

    def toggle_weekends(self):
        if self.chk_no_weekends_var.get():
            self.day_vars[5].set(False)
            self.day_vars[6].set(False)
        else:
            self.day_vars[5].set(True)
            self.day_vars[6].set(True)

    def update_weekend_chk(self):
        if self.day_vars[5].get() or self.day_vars[6].get():
            self.chk_no_weekends_var.set(False)
        elif not self.day_vars[5].get() and not self.day_vars[6].get():
            self.chk_no_weekends_var.set(True)

    def toggle_expediente(self):
        if self.chk_expediente_var.get():
            self.exp_times_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=(0, 15))
        else:
            self.exp_times_frame.grid_remove()

    def open_time_picker(self, target):
        current_time_str = self.exp_start_var.get().replace("🕒 ", "") if target == "start" else self.exp_end_var.get().replace("🕒 ", "")
        
        def on_select(selected_time_str):
            if target == "start":
                self.exp_start_var.set(f"🕒 {selected_time_str}")
            else:
                self.exp_end_var.set(f"🕒 {selected_time_str}")
                
        TimePicker(self, current_time_str=current_time_str, on_select=on_select)

    def toggle_token_visibility(self):
        if self.token_visible:
            self.entry_token.configure(show="*")
            self.btn_show_token.configure(text="👁 Mostrar")
            self.token_visible = False
        else:
            self.entry_token.configure(show="")
            self.btn_show_token.configure(text="🔒 Ocultar")
            self.token_visible = True

    def open_datetime_picker(self, target):
        current_dt = None
        if target == "start" and self.start_date_val:
            current_dt = self.start_date_val
        elif target == "end" and self.end_date_val:
            current_dt = self.end_date_val

        def on_select(selected_dt):
            formatted_str = selected_dt.strftime("%d/%m/%Y %H:%M")
            if target == "start":
                self.start_date_var.set(f"📅 {formatted_str}")
                self.start_date_val = selected_dt
            elif target == "end":
                self.end_date_var.set(f"📅 {formatted_str}")
                self.end_date_val = selected_dt

        DateTimePicker(self, current_date=current_dt, on_select=on_select)

    def log(self, message):
        """Adiciona uma mensagem na caixa de log de forma segura para threads."""
        def update():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", message + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.after(0, update)

    def cancel_process(self):
        self.is_cancelled = True
        self.log("\n[!] SOLICITAÇÃO DE CANCELAMENTO RECEBIDA. Abortando próximos envios...")
        self.btn_cancel.configure(state="disabled", fg_color=SECONDARY_BTN, hover_color=SECONDARY_BTN, text_color=MUTED_COLOR)

    def start_process(self):
        if getattr(self, 'is_running', False):
            return
            
        token = self.entry_token.get().strip()
        script_id = self.selected_script_id
        interval_str = self.entry_interval.get().strip()

        # Validações
        if not all([token, script_id, interval_str]):
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos obrigatórios (Token, Script, Intervalo).")
            return

        if not self.start_date_val or not self.end_date_val:
            messagebox.showwarning("Aviso", "Por favor, selecione as datas de início e fim.")
            return

        try:
            interval_min = int(interval_str)
            if interval_min <= 0:
                raise ValueError("O intervalo deve ser maior que zero.")
        except ValueError:
            messagebox.showerror("Erro", "O Intervalo deve ser um número inteiro válido.")
            return

        if self.start_date_val > self.end_date_val:
            messagebox.showerror("Erro", "A data/hora de início deve ser anterior ou igual à data/hora de fim.")
            return

        use_expediente = self.chk_expediente_var.get()
        exp_start_time = None
        exp_end_time = None

        if use_expediente:
            exp_start_str = self.exp_start_var.get().replace("🕒 ", "")
            exp_end_str = self.exp_end_var.get().replace("🕒 ", "")
            if exp_start_str == "08:00" and exp_end_str == "18:00" and not hasattr(self, 'changed_time'):
                # it's ok, use defaults if user wants 08 to 18
                pass
            if exp_start_str == "Selecionar" or exp_end_str == "Selecionar" or "]" in exp_start_str:
                messagebox.showwarning("Aviso", "Selecione os horários de início e fim do expediente.")
                return
            try:
                exp_start_time = datetime.datetime.strptime(exp_start_str, "%H:%M").time()
                exp_end_time = datetime.datetime.strptime(exp_end_str, "%H:%M").time()
            except ValueError:
                messagebox.showerror("Erro", "Formato de horário do expediente inválido.")
                return

        self.save_config(token, script_id, self.selected_script_name)

        # Reseta flag de cancelamento e atualiza botões
        self.is_cancelled = False
        self.is_running = True
        self.btn_start.configure(state="disabled")
        self.btn_cancel.configure(state="normal", fg_color=DANGER_COLOR, hover_color=DANGER_HOVER, text_color="#ffffff")
        
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        
        allowed_days = [day_idx for day_idx, var in self.day_vars.items() if var.get()]
        if not allowed_days:
            messagebox.showwarning("Aviso", "Selecione pelo menos um dia da semana para execução.")
            return

        self.log(f"Iniciando processo de agendamento...")
        self.log(f"Script selecionado: [{script_id}] {self.selected_script_name}")
        self.log(f"De {self.start_date_val.strftime('%d/%m/%Y %H:%M')} até {self.end_date_val.strftime('%d/%m/%Y %H:%M')} a cada {interval_min} min.\n")
        


        threading.Thread(
            target=self.run_schedule, 
            args=(token, script_id, self.start_date_val, self.end_date_val, interval_min, use_expediente, exp_start_time, exp_end_time, allowed_days), 
            daemon=True
        ).start()

    def run_schedule(self, token, script_id, start_date, end_date, interval_min, use_expediente, exp_start_time, exp_end_time, allowed_days):
        url = "https://app.tiflux.com/equipment/rmm/batch_script_actions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        payloads = []
        current_time = start_date
        now = datetime.datetime.now()
        skipped_past = 0
        while current_time <= end_date:
            if current_time.weekday() not in allowed_days:
                current_time += datetime.timedelta(minutes=interval_min)
                continue

            if use_expediente:
                if not (exp_start_time <= current_time.time() <= exp_end_time):
                    current_time += datetime.timedelta(minutes=interval_min)
                    continue

            # Ignorar horários que já passaram
            if current_time <= now:
                skipped_past += 1
                current_time += datetime.timedelta(minutes=interval_min)
                continue

            formatted_date = current_time.strftime("%Y-%m-%dT%H:%M:%S.000-03:00")
            display_date = current_time.strftime("%d/%m/%Y %H:%M")
            
            payload = {
                "operating_system": "windows",
                "script_id": script_id,
                "scheduled_date": formatted_date,
                "execution_type": "clients",
                "client_ids": []
            }
            payloads.append((display_date, formatted_date, payload))
            current_time += datetime.timedelta(minutes=interval_min)

        total_success = 0
        total_errors = 0
        total_requests = len(payloads)

        if skipped_past > 0:
            self.log(f"[!] {skipped_past} horário(s) ignorado(s) por já terem passado.")

        if total_requests == 0:
            self.log("[!] Nenhum agendamento válido para enviar. Todos os horários já passaram ou foram filtrados.")
            self.after(0, lambda: self.btn_start.configure(state="normal"))
            self.after(0, lambda: self.btn_cancel.configure(state="disabled", fg_color=SECONDARY_BTN, hover_color=SECONDARY_BTN, text_color=MUTED_COLOR))
            return

        self.log(f"[*] Preparados {total_requests} agendamentos. Enviando em paralelo...")

        # Mostrar barra de progresso
        completed_count = [0]
        self.after(0, lambda: self.progress_frame.grid())
        self.after(0, lambda: self.progress_bar.configure(progress_color=ACCENT_COLOR))
        self.after(0, lambda: self.progress_bar.set(0))
        self.after(0, lambda: self.progress_label.configure(text="0%", text_color=ACCENT_COLOR))

        def send_request(data):
            display_str, api_date_str, payload_data = data
            
            if getattr(self, 'is_cancelled', False):
                return display_str, 0, "", "Cancelado"
                
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(url, json=payload_data, headers=headers, timeout=15)
                    return display_str, response.status_code, response.text, None
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return display_str, None, None, "Timeout da API"
                except Exception as e:
                    return display_str, None, None, str(e)

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_date = {executor.submit(send_request, p): p[0] for p in payloads}
            
            for future in as_completed(future_to_date):
                display_str, status_code, text, err = future.result()
                
                if err == "Cancelado":
                    continue
                elif err:
                    self.log(f"    [!] {display_str} - Erro de conexão: {err}")
                    total_errors += 1
                elif status_code in (200, 201, 204):
                    self.log(f"    [+] {display_str} - Sucesso! (Status {status_code})")
                    total_success += 1
                else:
                    self.log(f"    [-] {display_str} - Falha! Status {status_code} | {text}")
                    total_errors += 1

                # Atualizar barra de progresso
                completed_count[0] += 1
                pct = completed_count[0] / total_requests
                pct_text = f"{int(pct * 100)}%"
                self.after(0, lambda p=pct, t=pct_text: self._update_progress(p, t))

        self.log("-" * 40)
        if getattr(self, 'is_cancelled', False):
            self.log("Processo INTERROMPIDO pelo usuário!")
        else:
            self.log("Processo FINALIZADO com sucesso!")
            
        self.log(f"Agendamentos concluídos: {total_success}")
        self.log(f"Erros encontrados: {total_errors}")
        
        def finalize():
            self.btn_start.configure(state="normal")
            self.btn_cancel.configure(state="disabled", fg_color=SECONDARY_BTN, hover_color=SECONDARY_BTN, text_color=MUTED_COLOR)
            self.is_running = False
            # Esconder barra de progresso após 3s
            self.after(3000, lambda: self.progress_frame.grid_remove())

            if total_errors > 0:
                messagebox.showwarning(
                    "Atenção: Possível Erro com Clientes", 
                    "Ocorreram erros em alguns agendamentos.\n\n"
                    "Dica: Se você pesquisou ou agendou para um cliente que não "
                    "possui equipamentos offline (ou ativos adequados), a Tiflux recusará "
                    "o envio retornando erro.\n\n"
                    "Lembre-se de utilizar a opção Exportar Logs para conferir os erros retornados."
                )

        self.after(0, finalize)

    def _update_progress(self, pct, text):
        self.progress_bar.set(pct)
        self.progress_label.configure(text=text)
        if pct >= 1.0:
            self.progress_bar.configure(progress_color=SUCCESS_COLOR)
            self.progress_label.configure(text_color=SUCCESS_COLOR)

if __name__ == "__main__":
    app = App()
    app.mainloop()
