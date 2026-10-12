# 📊 Lines of Code Desktop App (LOC Counter Pro)

កម្មវិធីកុំព្យូទ័រ Desktop (GUI) សម្រាប់រាប់ចំនួនបន្ទាត់កូដ (Lines of Code) ចំនួន Files និងបែងចែកតាមប្រភេទភាសាកូដដោយស្វ័យប្រវត្តិ ព្រមទាំងគាំទ្រមុខងារ Drag & Drop ពី Windows Desktop ដោយផ្ទាល់។

---

## ✨ លក្ខណៈពិសេសចម្បង (Features)

- **📥 គាំទ្រ Drag & Drop:** គ្រាន់តែអូស Folder គម្រោងកូដពី File Explorer មកទម្លាក់ចូលផ្ទាំងកម្មវិធី វានឹងចាប់ផ្ដើមស្កេន និងរាប់ដោយស្វ័យប្រវត្តិតែម្ដង។
- **📂 បែងចែកតាមភាសាកូដ (Auto Language Detection):**
  - **Web & Scripting:** Python, JavaScript, TypeScript, React (JSX/TSX), HTML, CSS, SCSS, Sass, Less, PHP, Ruby, Vue, Svelte
  - **Systems & Compiled:** C, C++, C#, Java, Kotlin, Go, Rust, Swift, Dart
  - **Scripts & Data:** Bash, PowerShell, Batch, SQL, JSON, YAML, XML, Markdown, Lua, R
- **📈 ស្ថិតិលម្អិត (Detailed Breakdown):**
  - ចំនួន Files សរុប
  - ជួរកូដជាក់ស្ដែង (Code Lines)
  - ជួរទទេ (Blank Lines)
  - ជួរសរុប (Total Lines)
  - ភាគរយ (%) តាមប្រភេទភាសាកូដ
- **⚡ Background Multi-Threading:** ដំណើរការស្កេននៅខាងក្រោយ មិនធ្វើឱ្យផ្ទាំងកម្មវិធីគាំង (Freeze) ទោះជាគម្រោងមានទំហំធំយ៉ាងណាក៏ដោយ។
- **🎨 Modern Dark Glassmorphic UI:** រចនាប័ទ្មទំនើប ទាក់ទាញ ជាមួយ Logo រំលេចពន្លឺ Neon 3D Rim Light។
- **📦 One-Click Build to Standalone EXE:** អាចចុចប៊ូតុង Build ចេញជាឯកសារ `.exe` ដាក់លើ Desktop បានភ្លាមៗ។

---

## 🚀 របៀបតម្លើង និងដំណើរការ (Installation & Usage)

### ១. លក្ខខណ្ឌតម្រូវ (Requirements)
- Python 3.10+
- បណ្ណាល័យដែលត្រូវការ៖
  ```bash
  pip install pillow windnd pyinstaller
  ```

### ២. ដំណើរការផ្ទាំងកម្មវិធី (Run GUI)
```bash
python code_counter_gui.py
```
*(ឬ Double-click លើ `run_ui.bat`)*

### ៣. ដំណើរការតាម Terminal (CLI Mode)
```bash
# រាប់ Folder បច្ចុប្បន្ន
python code_counter.py

# រាប់ Folder ផ្សេងទៀត
python code_counter.py -d "C:/Path/To/Your/Project"
```

### ៤. Build ជាឯកសារ .EXE (Build Standalone Executable)
```bash
python code_counter_gui.py --build
```
*(ឬចុចប៊ូតុង **"📦 Build .exe ទៅ Desktop"** នៅក្នុងកម្មវិធី)*

---

## 📁 រចនាសម្ព័ន្ធឯកសារ (Project Structure)

```text
lines-of-code-desktop-app/
├── code_counter_gui.py     # កូដផ្ទាំង UI ក្រាហ្វិក Desktop ពេញលេញ
├── code_counter.py         # កូដម៉ាស៊ីនស្កេនកូដ (Core Engine / CLI)
├── app_logo.png            # រូប Logo កម្រិតច្បាស់ខ្ពស់ (Master 1024x1024)
├── app_logo.ico            # Windows Multi-Resolution Icon (16px ដល់ 256px)
├── logo-png.jfif           # រូបភាព Logo ដើម
├── build_exe.bat           # Script សម្រាប់ build ជា .exe ដោយ 1-click
├── run_ui.bat              # Script សម្រាប់បើក UI ដោយ 1-click
├── .gitignore              # បញ្ជី ignore ឯកសារ build & cache
└── README.md               # ឯកសារណែនាំគម្រោង
```

---

## 📝 អាជ្ញាប័ណ្ណ (License)
គម្រោងនេះបង្កើតឡើងក្រោមអាជ្ញាប័ណ្ណ **MIT License**។
