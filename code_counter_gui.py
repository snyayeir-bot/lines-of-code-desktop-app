import os
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageTk

# មុខងារស្វែងរកទីតាំងឯកសារ (ដំណើរការទាំងធម្មតា និងពេល build ជា .exe)
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

# ==============================================================================
# មុខងារបង្កើត LOGO APP (ស្វ័យប្រវត្តិកាត់គែមទទេ 100% ឱ្យធំពេញក្រឡាលើ Desktop)
# ==============================================================================
def generate_app_logo_from_source(force=False):
    """
    ពិនិត្យ និងបង្កើត app_logo.png និង app_logo.ico (ពហុកម្រិត 16px ដល់ 256px) 
    ដោយប្រើប្រាស់ Master Ultra-HD Icon ស្អាតកម្រិត Premium
    """
    app_dir = os.path.abspath(os.path.dirname(__file__))
    source_file = os.path.join(app_dir, "logo-png.jfif")
    if not os.path.exists(source_file):
        source_file = os.path.join(app_dir, "Logocomntcode.jfif")

    ico_path = os.path.join(app_dir, "app_logo.ico")
    png_path = os.path.join(app_dir, "app_logo.png")

    if not os.path.exists(source_file):
        return

    # ប្រសិនបើមាន icon រួចហើយ ហើយមិន force ទេ មិនបាច់ធ្វើឡើងវិញ
    if not force and os.path.exists(ico_path) and os.path.exists(png_path):
        return

    try:
        from PIL import ImageFilter
        raw_img = Image.open(source_file).convert("RGBA")
        w, h = raw_img.size
        if w > 1900 and h > 1000:
            raw_img = raw_img.crop((930, 320, 1822, 1215))

        bbox = raw_img.getbbox()
        if bbox:
            clean_badge = raw_img.crop(bbox)
        else:
            clean_badge = raw_img

        bw, bh = clean_badge.size
        max_b = max(bw, bh)
        badge_sq = Image.new("RGBA", (max_b, max_b), (0, 0, 0, 0))
        badge_sq.paste(clean_badge, ((max_b - bw)//2, (max_b - bh)//2))

        # បង្កើត Master Icon 1024x1024 ជាមួយ Ambient Aura
        master_size = 1024
        canvas = Image.new("RGBA", (master_size, master_size), (0, 0, 0, 0))
        target_badge_size = 920
        badge_resized = badge_sq.resize((target_badge_size, target_badge_size), Image.Resampling.LANCZOS)

        # Ambient Glow
        glow_layer = Image.new("RGBA", (target_badge_size + 40, target_badge_size + 40), (14, 165, 233, 140))
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=25))
        glow_offset = ((master_size - glow_layer.width)//2, (master_size - glow_layer.height)//2)
        canvas.paste(glow_layer, glow_offset, glow_layer)

        badge_offset = ((master_size - target_badge_size)//2, (master_size - target_badge_size)//2)
        canvas.paste(badge_resized, badge_offset, badge_resized)

        canvas.save(png_path, format="PNG")
        
        # រក្សាទុក ICO បែប Windows Compliant (DIB សម្រាប់ 16-128px និង PNG សម្រាប់ 256px)
        # ដើម្បីឱ្យ Windows Explorer និង Desktop បង្ហាញ Icon លើ .exe យ៉ាងច្បាស់ 100%
        import struct
        import io
        
        img_src = canvas
        dib_sizes = [16, 24, 32, 48, 64, 128]
        entries = []
        images_data = []
        
        for sz in dib_sizes:
            frame = img_src.resize((sz, sz), Image.Resampling.LANCZOS)
            bgra_bytes = bytearray()
            for y_pix in range(sz - 1, -1, -1):
                for x_pix in range(sz):
                    r_p, g_p, b_p, a_p = frame.getpixel((x_pix, y_pix))
                    bgra_bytes.extend([b_p, g_p, r_p, a_p])
            row_bytes = (sz + 31) // 32 * 4
            and_mask = bytearray(row_bytes * sz)
            bih = struct.pack('<IIIHHIIIIII', 40, sz, sz * 2, 1, 32, 0, len(bgra_bytes) + len(and_mask), 0, 0, 0, 0)
            dib_data = bih + bgra_bytes + and_mask
            images_data.append(dib_data)
            entries.append({'w': sz, 'h': sz, 'colors': 0, 'reserved': 0, 'planes': 1, 'bpp': 32, 'size': len(dib_data)})
            
        frame_256 = img_src.resize((256, 256), Image.Resampling.LANCZOS)
        bio = io.BytesIO()
        frame_256.save(bio, format='PNG')
        png_data = bio.getvalue()
        images_data.append(png_data)
        entries.append({'w': 0, 'h': 0, 'colors': 0, 'reserved': 0, 'planes': 1, 'bpp': 32, 'size': len(png_data)})
        
        cur_offset = 6 + 16 * len(entries)
        for e in entries:
            e['offset'] = cur_offset
            cur_offset += e['size']
            
        ico_bytes = bytearray()
        ico_bytes.extend(struct.pack('<HHH', 0, 1, len(entries)))
        for e in entries:
            ico_bytes.extend(struct.pack('<BBBBHHII', e['w'], e['h'], e['colors'], e['reserved'], e['planes'], e['bpp'], e['size'], e['offset']))
        for d in images_data:
            ico_bytes.extend(d)
            
        with open(ico_path, 'wb') as f_ico:
            f_ico.write(ico_bytes)
            
        print("✅ បានបង្កើត Master app_logo.png និង app_logo.ico Windows-compliant ជោគជ័យ!")
    except Exception as e:
        print(f"បញ្ហាក្នុងការបង្កើត logo: {e}")


def build_desktop_exe():
    """
    Build កម្មវិធីជា .exe ជាមួយ PyInstaller
    និងចម្លងទៅកាន់ Desktop ដោយផ្ទាល់ ព្រមទាំងបង្កើត Shortcut ធំស្អាត
    """
    import subprocess
    import shutil

    generate_app_logo_from_source(force=False)
    app_dir = os.path.abspath(os.path.dirname(__file__))

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        f'--icon={os.path.join(app_dir, "app_logo.ico")}',
        f'--add-data={os.path.join(app_dir, "app_logo.ico")};.',
        f'--add-data={os.path.join(app_dir, "app_logo.png")};.',
        f'--add-data={os.path.join(app_dir, "logo-png.jfif")};.',
        "--hidden-import=windnd",
        "--hidden-import=PIL",
        "--hidden-import=PIL.ImageTk",
        "--exclude-module=torch",
        "--exclude-module=scipy",
        "--exclude-module=matplotlib",
        "--name=LinesOfCodeCounter",
        "--clean", "-y",
        os.path.join(app_dir, "code_counter_gui.py")
    ]
    print("⏳ កំពុងដំណើរការ Build កម្មវិធី...")
    subprocess.run(cmd, check=True)

    # ចម្លងទៅកាន់ Desktop
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    built_exe = os.path.join(app_dir, "dist", "LinesOfCodeCounter.exe")
    if os.path.exists(built_exe):
        target_exe = os.path.join(desktop, "LinesOfCodeCounter.exe")
        shutil.copy2(built_exe, target_exe)
        print(f"✅ បានចម្លង {target_exe} ទៅ Desktop ជោគជ័យ!")

        # បង្កើត/Update Shortcut (.lnk) លើ Desktop ជាមួយ Icon ធំច្បាស់
        try:
            lnk_path = os.path.join(desktop, "Lines of Code Counter.lnk").replace("\\", "/")
            exe_target = target_exe.replace("\\", "/")
            ico_target = os.path.join(app_dir, "app_logo.ico").replace("\\", "/")
            clean_app_dir = app_dir.replace("\\", "/")
            ps_script = (
                f'$ws = New-Object -ComObject WScript.Shell; '
                f'$s = $ws.CreateShortcut("{lnk_path}"); '
                f'$s.TargetPath = "{exe_target}"; '
                f'$s.IconLocation = "{ico_target},0"; '
                f'$s.WorkingDirectory = "{clean_app_dir}"; '
                f'$s.Save()'
            )
            subprocess.run(["powershell", "-Command", ps_script], check=False)
            print("✅ បានបង្កើត Shortcut លើ Desktop ជាមួយ Icon ធំច្បាស់ជោគជ័យ!")
        except Exception as e:
            print(f"Warning shortcut creation: {e}")


# ព្យាយាម import windnd ឬ tkinterdnd2 សម្រាប់មុខងារ Drag & Drop
HAS_WINDND = False
try:
    import windnd
    HAS_WINDND = True
except ImportError:
    pass

# នាំចូលមុខងារ scan ពី code_counter
from code_counter import EXTENSION_LANGUAGE_MAP, DEFAULT_IGNORE_DIRS, analyze_directory


class CodeCounterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lines of Code Counter - កម្មវិធីរាប់ជួរកូដ")
        self.root.geometry("880x680")
        self.root.minsize(780, 560)

        # កំណត់ Icon សម្រាប់ផ្ទាំងកម្មវិធី (Window Icon)
        self.set_window_icon()

        # កំណត់ Style សម្រាប់ UI
        self.setup_styles()

        self.current_folder = ""
        self.is_scanning = False
        self.logo_image = None  # រក្សាទុក reference កុំឱ្យ garbage collected
        self.drop_logo_image = None

        self.create_widgets()
        self.setup_drag_and_drop()

    def set_window_icon(self):
        icon_path = resource_path("app_logo.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                try:
                    # ករណីមួយចំនួន iconphoto ដំណើរការល្អជាមួយ png
                    png_path = resource_path("app_logo.png")
                    if os.path.exists(png_path):
                        img = tk.PhotoImage(file=png_path)
                        self.root.iconphoto(True, img)
                except Exception:
                    pass

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # កំណត់ពុម្ពអក្សរ និងពណ៌
        self.bg_color = "#f4f6f9"
        self.primary_color = "#2563eb"
        self.primary_hover = "#1d4ed8"
        self.card_bg = "#ffffff"
        self.border_color = "#cbd5e1"

        self.root.configure(bg=self.bg_color)

        style.configure(".", font=("Segoe UI", 10), background=self.bg_color)
        style.configure("Treeview", 
                        background="#ffffff", 
                        fieldbackground="#ffffff", 
                        font=("Segoe UI", 10), 
                        rowheight=28)
        style.configure("Treeview.Heading", 
                        font=("Segoe UI", 10, "bold"), 
                        background="#e2e8f0", 
                        foreground="#1e293b")
        style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", "#1e3a8a")])

    def create_widgets(self):
        # 1. Header Frame ជាមួយ Logo ធំច្បាស់បែប Premium Dark Glassmorphic
        header_frame = tk.Frame(self.root, bg="#0b0f19", padx=26, pady=18)
        header_frame.pack(fill="x")

        # បន្ទាត់ពន្លឺ Neon Accent Line ខាងក្រោម Header
        accent_line = tk.Frame(self.root, bg="#0ea5e9", height=2)
        accent_line.pack(fill="x")

        # បង្ហាញ Logo ធំច្បាស់ក្នុង Header (ទំហំ 86x86)
        logo_path = resource_path("app_logo.png")
        if not os.path.exists(logo_path):
            logo_path = resource_path("logo-png.jfif")
        if not os.path.exists(logo_path):
            logo_path = resource_path("Logocomntcode.jfif")

        pil_raw = None
        if os.path.exists(logo_path):
            try:
                pil_raw = Image.open(logo_path)
                pil_header = pil_raw.resize((86, 86), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(pil_header)
                logo_lbl = tk.Label(header_frame, image=self.logo_image, bg="#0b0f19")
                logo_lbl.pack(side="left", padx=(0, 20))
            except Exception as e:
                print(f"Error loading header logo: {e}")

        title_box = tk.Frame(header_frame, bg="#0b0f19")
        title_box.pack(side="left", fill="both", expand=True)

        title_row = tk.Frame(title_box, bg="#0b0f19")
        title_row.pack(anchor="w")

        title_lbl = tk.Label(
            title_row,
            text="Lines of Code Counter",
            font=("Segoe UI", 18, "bold"),
            fg="#f8fafc",
            bg="#0b0f19",
        )
        title_lbl.pack(side="left")

        pro_badge = tk.Label(
            title_row,
            text="PRO v2.0",
            font=("Segoe UI", 8, "bold"),
            fg="#38bdf8",
            bg="#0c4a6e",
            padx=7,
            pady=2,
            relief="flat",
        )
        pro_badge.pack(side="left", padx=(10, 0))

        subtitle_lbl = tk.Label(
            title_box,
            text="កម្មវិធីរាប់ចំនួនជួរកូដ • បែងចែកតាមភាសាកូដ • គាំទ្រ Drag & Drop ពី Desktop",
            font=("Segoe UI", 10),
            fg="#94a3b8",
            bg="#0b0f19",
        )
        subtitle_lbl.pack(anchor="w", pady=(4, 0))

        # Main Content Container
        main_container = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=14)
        main_container.pack(fill="both", expand=True)

        # 2. Drag & Drop Zone / Folder Selector
        self.drop_frame = tk.Frame(
            main_container,
            bg="#ffffff",
            bd=2,
            relief="groove",
            padx=16,
            pady=16,
            cursor="hand2",
        )
        self.drop_frame.pack(fill="x", pady=(0, 14))

        # បង្ហាញ Logo ធំច្បាស់ចំកណ្តាល Drop Zone
        if pil_raw:
            try:
                pil_drop = pil_raw.resize((68, 68), Image.Resampling.LANCZOS)
                self.drop_logo_image = ImageTk.PhotoImage(pil_drop)
                self.drop_icon = tk.Label(
                    self.drop_frame,
                    image=self.drop_logo_image,
                    bg="#ffffff",
                )
            except Exception:
                self.drop_icon = tk.Label(
                    self.drop_frame,
                    text="📁",
                    font=("Segoe UI", 28),
                    bg="#ffffff",
                )
        else:
            self.drop_icon = tk.Label(
                self.drop_frame,
                text="📁",
                font=("Segoe UI", 28),
                bg="#ffffff",
            )
        self.drop_icon.pack(pady=(0, 4))

        self.drop_text = tk.Label(
            self.drop_frame,
            text="អូស និងទម្លាក់ (Drag & Drop) Folder កូដចូលទីនេះ",
            font=("Segoe UI", 12, "bold"),
            fg="#1e293b",
            bg="#ffffff",
        )
        self.drop_text.pack(pady=(2, 4))

        self.folder_label = tk.Label(
            self.drop_frame,
            text="មិនទាន់បានជ្រើសរើស Folder ណាមួយទេ",
            font=("Segoe UI", 9, "italic"),
            fg="#64748b",
            bg="#ffffff",
            wraplength=600,
        )
        self.folder_label.pack(pady=(0, 8))

        btn_box = tk.Frame(self.drop_frame, bg="#ffffff")
        btn_box.pack()

        self.browse_btn = tk.Button(
            btn_box,
            text="📂 ជ្រើសរើស Folder (Browse)",
            command=self.browse_folder,
            font=("Segoe UI", 10, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
        )
        self.browse_btn.pack(side="left", padx=5)

        self.start_btn = tk.Button(
            btn_box,
            text="🚀 ចាប់ផ្ដើមរាប់កូដ",
            command=self.start_scan_thread,
            font=("Segoe UI", 10, "bold"),
            bg="#16a34a",
            fg="#ffffff",
            activebackground="#15803d",
            activeforeground="#ffffff",
            relief="flat",
            padx=16,
            pady=6,
            state="disabled",
            cursor="hand2",
        )
        self.start_btn.pack(side="left", padx=5)

        self.build_btn = tk.Button(
            btn_box,
            text="📦 Build .exe ទៅ Desktop",
            command=self.start_build_thread,
            font=("Segoe UI", 10, "bold"),
            bg="#7c3aed",
            fg="#ffffff",
            activebackground="#6d28d9",
            activeforeground="#ffffff",
            relief="flat",
            padx=14,
            pady=6,
            cursor="hand2",
        )
        self.build_btn.pack(side="left", padx=5)

        # ចុចលើ drop_frame ដើម្បីជ្រើសរើស Folder ផងដែរ
        self.drop_frame.bind("<Button-1>", lambda e: self.browse_folder())
        self.drop_icon.bind("<Button-1>", lambda e: self.browse_folder())
        self.drop_text.bind("<Button-1>", lambda e: self.browse_folder())

        # 3. Summary Cards (ចំនួនសរុប)
        cards_frame = tk.Frame(main_container, bg=self.bg_color)
        cards_frame.pack(fill="x", pady=(0, 14))

        self.card_files = self.create_card(cards_frame, "📁 ចំនួន Files", "0", "#0284c7")
        self.card_code = self.create_card(cards_frame, "💻 ជួរកូដ (Code Lines)", "0", "#16a34a")
        self.card_blank = self.create_card(cards_frame, "📄 ជួរទទេ (Blank)", "0", "#ea580c")
        self.card_total = self.create_card(cards_frame, "📈 ជួរសរុប (Total)", "0", "#7c3aed")

        self.card_files.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.card_code.pack(side="left", fill="both", expand=True, padx=3)
        self.card_blank.pack(side="left", fill="both", expand=True, padx=3)
        self.card_total.pack(side="left", fill="both", expand=True, padx=(6, 0))

        # 4. Result Treeview Table
        table_frame = tk.Frame(main_container, bg="#ffffff", bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True)

        columns = ("lang", "files", "code", "blank", "total", "percent")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("lang", text="ភាសាកូដ (Language)", anchor="w")
        self.tree.heading("files", text="Files", anchor="center")
        self.tree.heading("code", text="Code Lines", anchor="e")
        self.tree.heading("blank", text="Blank Lines", anchor="e")
        self.tree.heading("total", text="Total Lines", anchor="e")
        self.tree.heading("percent", text="ភាគរយ (%)", anchor="center")

        self.tree.column("lang", width=180, anchor="w")
        self.tree.column("files", width=90, anchor="center")
        self.tree.column("code", width=120, anchor="e")
        self.tree.column("blank", width=110, anchor="e")
        self.tree.column("total", width=120, anchor="e")
        self.tree.column("percent", width=90, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 5. Status Bar
        self.status_var = tk.StringVar(value="ត្រៀមរួចរាល់ - សូមទម្លាក់ Folder ឬជ្រើសរើសដើម្បីចាប់ផ្ដើម។")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Segoe UI", 9),
            bg="#e2e8f0",
            fg="#334155",
            anchor="w",
            padx=16,
            pady=6,
        )
        status_bar.pack(fill="x", side="bottom")

    def create_card(self, parent, title, val, color):
        frame = tk.Frame(parent, bg="#ffffff", bd=1, relief="solid")
        # Top color accent bar
        accent = tk.Frame(frame, bg=color, height=3)
        accent.pack(fill="x")
        content = tk.Frame(frame, bg="#ffffff", padx=14, pady=10)
        content.pack(fill="both", expand=True)
        lbl_title = tk.Label(content, text=title, font=("Segoe UI", 9, "bold"), fg="#64748b", bg="#ffffff")
        lbl_title.pack(anchor="w")
        lbl_val = tk.Label(content, text=val, font=("Segoe UI", 17, "bold"), fg=color, bg="#ffffff")
        lbl_val.pack(anchor="w", pady=(3, 0))
        frame.val_label = lbl_val
        return frame

    def setup_drag_and_drop(self):
        """
        បើកដំណើរការ Drag and Drop លើ Windows ដោយប្រើ windnd
        """
        if HAS_WINDND:
            try:
                windnd.hook_dropfiles(self.root, func=self.on_drop_files)
                windnd.hook_dropfiles(self.drop_frame, func=self.on_drop_files)
            except Exception as e:
                print(f"Drag and drop hook warning: {e}")
        else:
            self.drop_text.config(text="ចុចប៊ូតុង Browse ដើម្បីជ្រើសរើស Folder")

    def on_drop_files(self, files):
        """
        ត្រូវបានហៅនៅពេលអ្នកប្រើប្រាស់អូស និងទម្លាក់ File/Folder
        """
        if not files:
            return

        # windnd អាចផ្ដល់ជា bytes ឬ string
        first_item = files[0]
        if isinstance(first_item, bytes):
            folder_path = first_item.decode("utf-8", errors="ignore")
        else:
            folder_path = str(first_item)

        # ប្រសិនបើទម្លាក់ File យក Folder មេរបស់វា
        p = Path(folder_path)
        if p.is_file():
            folder_path = str(p.parent)

        if Path(folder_path).is_dir():
            self.set_selected_folder(folder_path)
            # រាប់កូដដោយស្វ័យប្រវត្តិតែម្ដង
            self.start_scan_thread()
        else:
            messagebox.showwarning("ការជូនដំណឹង", "សូមទម្លាក់ Folder គម្រោងកូដ (Directory) ត្រឹមត្រូវ។")

    def browse_folder(self):
        folder = filedialog.askdirectory(title="ជ្រើសរើស Folder គម្រោងកូដ")
        if folder:
            self.set_selected_folder(folder)
            self.start_scan_thread()

    def set_selected_folder(self, folder_path):
        self.current_folder = folder_path
        self.folder_label.config(text=f"📂 Folder: {folder_path}", fg="#0369a1", font=("Segoe UI", 9, "bold"))
        self.start_btn.config(state="normal")
        self.status_var.set(f"បានជ្រើសរើស Folder: {folder_path}")

    def start_scan_thread(self):
        if not self.current_folder or self.is_scanning:
            return

        self.is_scanning = True
        self.browse_btn.config(state="disabled")
        self.start_btn.config(state="disabled")
        self.status_var.set("⏳ កំពុងដំណើរការស្កេន និងរាប់កូដ សូមរង់ចាំបន្តិច...")

        # ដំណើរការលើ Background Thread ដើម្បីកុំឱ្យ UI គាំង (Freeze)
        thread = threading.Thread(target=self.run_scan, daemon=True)
        thread.start()

    def run_scan(self):
        try:
            stats = analyze_directory(self.current_folder)
            self.root.after(0, self.update_ui_with_results, stats)
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
        finally:
            self.is_scanning = False

    def show_error(self, err_msg):
        self.browse_btn.config(state="normal")
        self.start_btn.config(state="normal")
        self.status_var.set(f"មានបញ្ហា: {err_msg}")
        messagebox.showerror("Error", f"មានបញ្ហាក្នុងការស្កេន: {err_msg}")

    def update_ui_with_results(self, stats):
        self.browse_btn.config(state="normal")
        self.start_btn.config(state="normal")

        # សម្អាត Treeview ចាស់
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not stats:
            self.status_var.set("❌ មិនមាន File កូដដែលត្រូវបានរកឃើញនៅក្នុង Folder នេះឡើយ។")
            self.card_files.val_label.config(text="0")
            self.card_code.val_label.config(text="0")
            self.card_blank.val_label.config(text="0")
            self.card_total.val_label.config(text="0")
            return

        total_files = sum(item["files"] for item in stats.values())
        total_code_lines = sum(item["code_lines"] for item in stats.values())
        total_blank_lines = sum(item["blank_lines"] for item in stats.values())
        total_all_lines = sum(item["total_lines"] for item in stats.values())

        # បច្ចុប្បន្នភាព Card តម្លៃសរុប
        self.card_files.val_label.config(text=f"{total_files:,}")
        self.card_code.val_label.config(text=f"{total_code_lines:,}")
        self.card_blank.val_label.config(text=f"{total_blank_lines:,}")
        self.card_total.val_label.config(text=f"{total_all_lines:,}")

        # តម្រៀបតាមចំនួនជួរកូដច្រើនទៅតិច
        sorted_stats = sorted(stats.items(), key=lambda x: x[1]["code_lines"], reverse=True)

        for lang, data in sorted_stats:
            percent = (data["code_lines"] / total_code_lines * 100) if total_code_lines > 0 else 0
            self.tree.insert(
                "",
                "end",
                values=(
                    lang,
                    f"{data['files']:,}",
                    f"{data['code_lines']:,}",
                    f"{data['blank_lines']:,}",
                    f"{data['total_lines']:,}",
                    f"{percent:.1f}%",
                ),
            )

        self.status_var.set(
            f"✅ រាប់រួចរាល់! សរុប {total_files:,} files | {total_code_lines:,} ជួរកូដ | {total_all_lines:,} ជួរសរុប"
        )

    def start_build_thread(self):
        """ដំណើរការ Build EXE នៅលើ background thread ដើម្បីកុំឱ្យ UI គាំង"""
        if getattr(self, "is_building", False):
            return

        self.is_building = True
        self.build_btn.config(state="disabled")
        self.status_var.set("⏳ កំពុងដំណើរការ Build .exe ដាក់លើ Desktop សូមរង់ចាំបន្តិច...")

        threading.Thread(target=self.run_build_thread, daemon=True).start()

    def run_build_thread(self):
        try:
            build_desktop_exe()
            self.root.after(0, self.on_build_success)
        except Exception as e:
            self.root.after(0, self.on_build_error, str(e))

    def on_build_success(self):
        self.is_building = False
        self.build_btn.config(state="normal")
        self.status_var.set("🎉 Build ជោគជ័យ! ឯកសារ LinesOfCodeCounter.exe ត្រូវបានដាក់លើ Desktop រួចរាល់។")
        messagebox.showinfo("ជោគជ័យ", "បាន Build កម្មវិធីជា .exe និងដាក់លើ Desktop របស់លោកអ្នកដោយជោគជ័យ!")

    def on_build_error(self, err_msg):
        self.is_building = False
        self.build_btn.config(state="normal")
        self.status_var.set(f"❌ បរាជ័យក្នុងការ Build: {err_msg}")
        messagebox.showerror("Error", f"មានបញ្ហាក្នុងការ Build: {err_msg}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--build":
        build_desktop_exe()
        return

    try:
        # ស្វ័យប្រវត្តិកាត់គែមទទេ 100% និងបង្កើត app_logo.png / app_logo.ico ជាមុនសិន
        generate_app_logo_from_source(force=False)

        root = tk.Tk()
        app = CodeCounterGUI(root)
        root.mainloop()
    except Exception as e:
        import traceback
        err_text = traceback.format_exc()
        try:
            from tkinter import messagebox
            r = tk.Tk()
            r.withdraw()
            messagebox.showerror("Lines of Code Counter - Error", f"មានបញ្ហាក្នុងការបើកកម្មវិធី:\n{err_text}")
            r.destroy()
        except Exception:
            print(f"Error: {err_text}")


if __name__ == "__main__":
    main()
