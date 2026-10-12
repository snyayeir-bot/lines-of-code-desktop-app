import os
import sys
import argparse
from collections import defaultdict
from pathlib import Path

# កំណត់ Encoding UTF-8 សម្រាប់ Windows Terminal/Console ដើម្បីចៀសវាង UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, Exception):
        pass

# បញ្ជីកំណត់សម្គាល់ប្រភេទកូដតាមរយៈ Extension នៃ File
EXTENSION_LANGUAGE_MAP = {
    # Web & Scripting
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "React (JSX)",
    ".ts": "TypeScript",
    ".tsx": "React (TSX)",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
    ".less": "Less",
    ".php": "PHP",
    ".rb": "Ruby",
    ".vue": "Vue",
    ".svelte": "Svelte",

    # Systems & Compiled Languages
    ".c": "C",
    ".h": "C/C++ Header",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++ Header",
    ".cs": "C#",
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin Script",
    ".go": "Go",
    ".rs": "Rust",
    ".swift": "Swift",
    ".dart": "Dart",

    # Shell & Scripts
    ".sh": "Shell Script",
    ".bash": "Bash",
    ".ps1": "PowerShell",
    ".bat": "Batch",
    ".cmd": "Batch",
    ".lua": "Lua",
    ".r": "R",

    # Data & Config
    ".sql": "SQL",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".xml": "XML",
    ".md": "Markdown",
    ".toml": "TOML",
    ".ini": "INI",
}

# ថត (Folders) ដែលមិនត្រូវរាប់បញ្ចូល
DEFAULT_IGNORE_DIRS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "env",
    "__pycache__",
    "dist",
    "build",
    ".idea",
    ".vscode",
    ".next",
    ".nuxt",
    "vendor",
    "coverage",
}


def count_lines_in_file(file_path: Path):
    """
    រាប់ចំនួនបន្ទាត់សរុប (Total lines), បន្ទាត់ទទេ (Blank lines),
    និងបន្ទាត់កូដជាក់ស្តែង (Code lines) នៃ file នីមួយៗ
    """
    total_lines = 0
    blank_lines = 0

    try:
        # បើក file ដោយប្រើ utf-8 បើ error នឹងព្យាយាមប្រើ latin-1
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except (UnicodeDecodeError, PermissionError):
            with open(file_path, "r", encoding="latin-1", errors="ignore") as f:
                lines = f.readlines()

        total_lines = len(lines)
        for line in lines:
            if not line.strip():
                blank_lines += 1

        code_lines = total_lines - blank_lines
        return total_lines, blank_lines, code_lines

    except Exception:
        # ប្រសិនបើមានបញ្ហាក្នុងការអាន file (ឧ. file ប្រព័ន្ធ ឬជាប់ permission)
        return 0, 0, 0


def analyze_directory(target_dir: str, custom_ignores=None):
    """
    ស្កេន Folder ទាំងមូល និងបែងចែកទិន្នន័យតាមប្រភេទភាសាកូដ
    """
    root_path = Path(target_dir).resolve()

    ignore_dirs = DEFAULT_IGNORE_DIRS.copy()
    if custom_ignores:
        ignore_dirs.update(custom_ignores)

    # stats[language] = {'files': 0, 'total_lines': 0, 'blank_lines': 0, 'code_lines': 0}
    stats = defaultdict(lambda: {"files": 0, "total_lines": 0, "blank_lines": 0, "code_lines": 0})

    if not root_path.exists():
        print(f"Error: មិនមាន Folder នេះទេ: {root_path}")
        return stats

    for root, dirs, files in os.walk(root_path):
        # មិនស្កេន Folder ដែលស្ថិតក្នុង ignore list
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]

        for filename in files:
            file_path = Path(root) / filename
            ext = file_path.suffix.lower()

            if ext in EXTENSION_LANGUAGE_MAP:
                lang = EXTENSION_LANGUAGE_MAP[ext]
                total_l, blank_l, code_l = count_lines_in_file(file_path)

                stats[lang]["files"] += 1
                stats[lang]["total_lines"] += total_l
                stats[lang]["blank_lines"] += blank_l
                stats[lang]["code_lines"] += code_l

    return stats


def print_results(stats: dict, target_dir: str):
    """
    បង្ហាញលទ្ធផលជាទម្រង់តារាងស្អាត និងងាយស្រួលមើល
    """
    if not stats:
        print("\nមិនមាន File កូដដែលត្រូវបានរកឃើញនៅក្នុង Folder នេះឡើយ។")
        return

    # តម្រៀបតាមចំនួនជួរកូដច្រើនទៅតិច
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]["code_lines"], reverse=True)

    total_files = sum(item["files"] for item in stats.values())
    total_code_lines = sum(item["code_lines"] for item in stats.values())
    total_blank_lines = sum(item["blank_lines"] for item in stats.values())
    total_all_lines = sum(item["total_lines"] for item in stats.values())

    print("\n" + "=" * 76)
    print(f" ស្ថិតិនៃការរាប់កូដ (Code Statistics) សម្រាប់ Folder: {target_dir}")
    print("=" * 76)
    header = f"{'ភាសាកូដ (Language)':<22} | {'Files':<8} | {'Blank Lines':<12} | {'Code Lines':<12} | {'Total Lines':<12}"
    print(header)
    print("-" * 76)

    for lang, data in sorted_stats:
        print(
            f"{lang:<22} | "
            f"{data['files']:<8} | "
            f"{data['blank_lines']:<12,d} | "
            f"{data['code_lines']:<12,d} | "
            f"{data['total_lines']:<12,d}"
        )

    print("-" * 76)
    print(
        f"{'សរុប (TOTAL)':<22} | "
        f"{total_files:<8} | "
        f"{total_blank_lines:<12,d} | "
        f"{total_code_lines:<12,d} | "
        f"{total_all_lines:<12,d}"
    )
    print("=" * 76 + "\n")


def main():
    # ប្រសិនបើ run ដោយមិនដាក់ arguments អ្វីទាំងអស់ នឹងបើកផ្ទាំង UI ដោយស្វ័យប្រវត្តិ
    if len(sys.argv) == 1:
        try:
            import code_counter_gui
            code_counter_gui.main()
            return
        except Exception as e:
            print(f"មិនអាចបើកផ្ទាំង UI បានឡើយ: {e}")
            print("ប្តូរមកដំណើរការតាម Terminal (CLI) វិញ...")

    parser = argparse.ArgumentParser(
        description="កម្មវិធីរាប់ចំនួនជួរកូដ ចំនួន files និងបែងចែកតាមប្រភេទភាសាកូដ (Lines of Code Counter)"
    )
    parser.add_argument(
        "-d", "--dir",
        default=".",
        help="ផ្លូវទៅកាន់ Folder គម្រោង (Directory path) - លំនាំដើមគឺ Folder បច្ចុប្បន្ន",
    )
    parser.add_argument(
        "-i", "--ignore",
        nargs="*",
        default=[],
        help="Folder បន្ថែមដែលចង់រំលងមិនរាប់ (Add extra folder names to ignore)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="បើកផ្ទាំងក្រាហ្វិក UI (Launch Graphical User Interface)",
    )

    args = parser.parse_args()

    if args.gui:
        import code_counter_gui
        code_counter_gui.main()
    else:
        results = analyze_directory(args.dir, custom_ignores=args.ignore)
        print_results(results, args.dir)


if __name__ == "__main__":
    main()
