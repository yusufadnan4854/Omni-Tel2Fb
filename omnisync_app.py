import os
import json
import customtkinter as ctk

CONFIG_FILE = "automation_config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {
            "credentials": {
                "tg_api_id": "",
                "tg_api_hash": "",
                "tg_session": "",
                "fb_user_token": "",
                "wp_username": "",
                "wp_app_password": ""
            },
            "rules": []
        }
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config_data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=4)

PLATFORMS = ["📢 Telegram", "👥 Facebook", "🌐 Website", "🎥 YouTube"]

class OmniSyncApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.config_data = load_config()

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.title("OmniSync Studio v8.0 - Dynamic Rules Editor & Hashtags")
        self.geometry("1020x730")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.build_sidebar()
        
        self.frames = {}
        for F in (DashboardFrame, CredentialsFrame, RulesFrame):
            frame = F(self, self.config_data, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
            
        self.show_frame("DashboardFrame")

    def build_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="OmniSync\nStudio", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        btns = [
            ("🏠 Dashboard", "DashboardFrame"), 
            ("🔐 Credentials", "CredentialsFrame"), 
            ("⚡ Sync Rules", "RulesFrame")
        ]
        
        for idx, (txt, frm) in enumerate(btns):
            btn = ctk.CTkButton(self.sidebar_frame, text=txt, command=lambda f=frm: self.show_frame(f))
            btn.grid(row=idx+1, column=0, padx=20, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="v8.0 Live Editor", text_color="green")
        self.status_label.grid(row=6, column=0, pady=(0, 20))

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()
        if hasattr(frame, 'on_show'):
            frame.on_show()


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, config, controller):
        super().__init__(parent)
        
        ctk.CTkLabel(self, text="OmniSync Dashboard v8.0", font=("Arial", 26, "bold")).pack(pady=20)
        
        info_text = (
            "What's New in OmniSync Studio v8.0:\n\n"
            "- Live Rules Editor: Click 'Edit' on any active pipeline to load and modify its inputs, outputs, and parameters dynamically.\n"
            "- Granular Hashtag Control: Toggle 'Keep Hashtags' on or off.\n"
            "  * If checked: Only '#' hashtags will be published.\n"
            "  * If unchecked: All hashtags are removed.\n"
            "  * '@' mentions are always stripped out automatically.\n"
            "- Reverted to fixed 1-Hour schedule run for stability."
        )
        
        self.info_box = ctk.CTkTextbox(self, height=300, width=600, font=("Arial", 14))
        self.info_box.insert("0.0", info_text)
        self.info_box.configure(state="disabled")
        self.info_box.pack(pady=20, padx=20, fill="both", expand=True)


class CredentialsFrame(ctk.CTkFrame):
    def __init__(self, parent, config, controller):
        super().__init__(parent)
        self.config = config
        
        self.scroll_area = ctk.CTkScrollableFrame(self)
        self.scroll_area.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkLabel(self.scroll_area, text="API Master Keychains", font=("Arial", 22, "bold")).pack(pady=10, anchor="w")
        
        self.entries = {}
        for key, value in self.config["credentials"].items():
            label_text = key.replace("_", " ").upper()
            ctk.CTkLabel(self.scroll_area, text=label_text, font=("Arial", 11, "bold")).pack(anchor="w", pady=(10, 2))
            
            ent = ctk.CTkEntry(self.scroll_area, width=500, placeholder_text=f"Enter {label_text}...")
            ent.insert(0, value)
            ent.pack(pady=(0, 10), anchor="w")
            self.entries[key] = ent
            
        save_btn = ctk.CTkButton(self, text="Save Keys Locally", fg_color="green", hover_color="#006400", command=self.save_keys)
        save_btn.pack(pady=20)

    def save_keys(self):
        for key, input_box in self.entries.items():
            self.config["credentials"][key] = input_box.get()
        save_config(self.config)
        ctk.CTkLabel(self, text="Saved to automation_config.json!", text_color="green").pack()


class RulesFrame(ctk.CTkFrame):
    def __init__(self, parent, config, controller):
        super().__init__(parent)
        self.config = config
        self.editing_index = None # Keeps track of which rule index is currently being edited
        
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(top_frame, text="Create & Modify Pipelines", font=("Arial", 18, "bold")).grid(row=0, column=0, padx=10, pady=10, columnspan=3, sticky="w")
        
        self.src_var = ctk.StringVar(value=PLATFORMS[0])
        self.dest_var = ctk.StringVar(value=PLATFORMS[1])
        
        # Source Platform Choice
        ctk.CTkLabel(top_frame, text="Source Platform:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.opt_src = ctk.CTkOptionMenu(top_frame, values=PLATFORMS, variable=self.src_var)
        self.opt_src.grid(row=1, column=1, padx=10, pady=5)
        self.entry_src_id = ctk.CTkEntry(top_frame, placeholder_text="Source ID(s) (Comma-separated, e.g. chan1, UCxxxx)")
        self.entry_src_id.grid(row=1, column=2, padx=10, pady=5, ipadx=100)

        # Destination Platform Choice
        ctk.CTkLabel(top_frame, text="Destination Platform:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.opt_dest = ctk.CTkOptionMenu(top_frame, values=PLATFORMS, variable=self.dest_var)
        self.opt_dest.grid(row=2, column=1, padx=10, pady=5)
        self.entry_dest_id = ctk.CTkEntry(top_frame, placeholder_text="Destination ID(s) (Comma-separated, e.g. id1, id2)")
        self.entry_dest_id.grid(row=2, column=2, padx=10, pady=5, ipadx=100)

        # Sync Media Checkboxes
        filters_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        filters_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.chk_txt = ctk.CTkCheckBox(filters_frame, text="Allow Text")
        self.chk_txt.pack(side="left", padx=8)
        self.chk_img = ctk.CTkCheckBox(filters_frame, text="Allow Image")
        self.chk_img.pack(side="left", padx=8)
        self.chk_vid = ctk.CTkCheckBox(filters_frame, text="Allow Video")
        self.chk_vid.pack(side="left", padx=8)
        self.chk_title_only = ctk.CTkCheckBox(filters_frame, text="Title Only")
        self.chk_title_only.pack(side="left", padx=8)
        self.chk_hashtags = ctk.CTkCheckBox(filters_frame, text="Keep Hashtags")
        self.chk_hashtags.pack(side="left", padx=8)
        
        self.chk_txt.select()
        self.chk_img.select()
        self.chk_vid.select()

        # Limits Configuration Row
        timing_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        timing_frame.grid(row=4, column=0, columnspan=3, pady=10)

        ctk.CTkLabel(timing_frame, text="Min Words Limit:").pack(side="left", padx=5)
        self.entry_min_words = ctk.CTkEntry(timing_frame, width=80)
        self.entry_min_words.insert(0, "60")
        self.entry_min_words.pack(side="left", padx=10)

        ctk.CTkLabel(timing_frame, text="Past Lookback Period (Hours):").pack(side="left", padx=5)
        self.entry_lookback = ctk.CTkEntry(timing_frame, width=80)
        self.entry_lookback.insert(0, "1")
        self.entry_lookback.pack(side="left", padx=10)
        
        # Submit/Edit button
        self.btn_submit = ctk.CTkButton(top_frame, text="+ Add Connection Route", command=self.add_rule)
        self.btn_submit.grid(row=5, column=0, columnspan=3, pady=15)

        self.list_area = ctk.CTkScrollableFrame(self)
        self.list_area.pack(expand=True, fill="both", padx=10, pady=10)

    def on_show(self):
        for widget in self.list_area.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.list_area, text="Active Pipelines List:", font=("Arial", 16, "bold")).pack(pady=10, anchor="w")
        for i, rule in enumerate(self.config.get("rules", [])):
            card = ctk.CTkFrame(self.list_area)
            card.pack(fill="x", padx=10, pady=5)
            
            title_sync_status = "YES" if rule.get('title_only', False) else "NO"
            tag_sync_status = "YES" if rule.get('keep_hashtags', False) else "NO"
            summary = f" {rule['source']} ➔ {rule['destination']}   |   T: {rule['txt']}  |  I: {rule.get('img', True)}  |  V: {rule['vid']}  |  Title Only: {title_sync_status}  |  Hashtags: {tag_sync_status}  |  Words: {rule.get('min_words', 60)}"
            desc = f"Mapping: {rule['source_id']} ➔ {rule['dest_id']}"
            
            ctk.CTkLabel(card, text=summary, font=("Arial", 11, "bold")).pack(anchor="w", padx=10, pady=(5,0))
            ctk.CTkLabel(card, text=desc, text_color="gray", font=("Arial", 10)).pack(anchor="w", padx=10, pady=(0, 5))
            
            # Action Buttons: Edit and Delete
            ctk.CTkButton(card, text="✏ Edit", fg_color="goldenrod", width=60, hover_color="#8B8000", command=lambda idx=i: self.start_edit(idx)).place(relx=0.8, rely=0.2)
            ctk.CTkButton(card, text="🗑 Delete", fg_color="red", width=60, hover_color="#550000", command=lambda idx=i: self.delete_rule(idx)).place(relx=0.9, rely=0.2)
            
    def start_edit(self, index):
        self.editing_index = index
        rule = self.config["rules"][index]
        
        self.src_var.set(rule.get('source', PLATFORMS[0]))
        self.dest_var.set(rule.get('destination', PLATFORMS[1]))
        
        self.entry_src_id.delete(0, 'end')
        self.entry_src_id.insert(0, rule.get('source_id', ''))
        
        self.entry_dest_id.delete(0, 'end')
        self.entry_dest_id.insert(0, rule.get('dest_id', ''))
        
        # Checkboxes Toggle
        self.toggle_checkbox(self.chk_txt, rule.get('txt', True))
        self.toggle_checkbox(self.chk_img, rule.get('img', True))
        self.toggle_checkbox(self.chk_vid, rule.get('vid', True))
        self.toggle_checkbox(self.chk_title_only, rule.get('title_only', False))
        self.toggle_checkbox(self.chk_hashtags, rule.get('keep_hashtags', False))
        
        self.entry_min_words.delete(0, 'end')
        self.entry_min_words.insert(0, str(rule.get('min_words', 60)))
        
        self.entry_lookback.delete(0, 'end')
        self.entry_lookback.insert(0, str(rule.get('lookback_hours', 1.0)))
        
        self.btn_submit.configure(text="💾 Update Connection Route", fg_color="#D4AF37", hover_color="#996515")

    def toggle_checkbox(self, checkbox, val):
        if val:
            checkbox.select()
        else:
            checkbox.deselect()

    def add_rule(self):
        try:
            min_words_limit = int(self.entry_min_words.get() or 60)
            lookback_hours = float(self.entry_lookback.get() or 1)
        except ValueError:
            min_words_limit = 60
            lookback_hours = 1.0

        r = {
            "source": self.src_var.get(), 
            "source_id": self.entry_src_id.get(),
            "destination": self.opt_dest.get(), 
            "dest_id": self.entry_dest_id.get(),
            "txt": bool(self.chk_txt.get()), 
            "img": bool(self.chk_img.get()),
            "vid": bool(self.chk_vid.get()),
            "title_only": bool(self.chk_title_only.get()),
            "keep_hashtags": bool(self.chk_hashtags.get()), # Allow/Block Hashtags selector
            "min_words": min_words_limit,
            "lookback_hours": lookback_hours
        }

        if self.editing_index is not None:
            # Overwrite existing index in list
            self.config["rules"][self.editing_index] = r
            self.editing_index = None
            self.btn_submit.configure(text="+ Add Connection Route", fg_color="#1f538d", hover_color="#14375e")
        else:
            self.config["rules"].append(r)

        save_config(self.config)
        self.entry_src_id.delete(0, 'end')
        self.entry_dest_id.delete(0, 'end')
        self.on_show()

    def delete_rule(self, index):
        self.config["rules"].pop(index)
        save_config(self.config)
        self.on_show()

if __name__ == "__main__":
    app = OmniSyncApp()
    app.mainloop()