import pathlib
from pip_check_reqs import find_missing_reqs

def is_utf8(file_path):
    try:
        file_path.read_text(encoding="utf-8")
        return True
    except UnicodeDecodeError:
        return False

def main():
    project_root = pathlib.Path(".").resolve()
    requirements_files = list(project_root.glob("requirements*.txt"))

    if not requirements_files:
        print("❌ Aucun fichier requirements*.txt trouvé.")
        return

    print(f"✔ Utilisation de : {requirements_files[0]}")
    py_files = [p for p in project_root.rglob("*.py") if is_utf8(p) and ".venv" not in str(p)]
    print("Fichiers Python analysés :")
    for f in py_files:
        print(f)
    # Fonctions d’ignorance vides (= tout garder)
    ignore_files = lambda filename: False
    ignore_modules = lambda module: False

    missing, unused = find_missing_reqs.find_missing_reqs(
        [project_root],              # liste de dossiers à scanner (pas la liste de fichiers)
        [requirements_files[0]],    # fichiers requirements
        ignore_files_function=lambda f: False,
        ignore_modules_function=lambda m: False
    )


    print("\n📦 Dépendances inutilisées dans requirements.txt :")
    for req in sorted(unused):
        print("  -", req)

    print("\n❗ Modules importés mais manquants dans requirements.txt :")
    for req in sorted(missing):
        print("  -", req)

if __name__ == "__main__":
    main()
