import json
import shutil
from pathlib import Path

from src import paths


def schemas_source_dir():
    return paths.BASE_DIR / ".." / ".." / "schemas"


def bundled_schemas_dir():
    return Path(__file__).resolve().parent.parent / "schemas"


def find_schemas_dir():
    candidates = [
        bundled_schemas_dir(),
        schemas_source_dir(),
    ]

    for candidate in candidates:
        if candidate.is_dir():
            anim = candidate / "animation.schema.json"
            scene = candidate / "scene.schema.json"

            if anim.exists() and scene.exists():
                return candidate

    return None


def ensure_schemas_available(project_root, subdir=".vscode"):
    schemas_dir = find_schemas_dir()

    if not schemas_dir:
        print("Warning: schemas directory not found in jadidi-hub.")
        return None

    target_dir = project_root / subdir / "schemas"
    target_dir.mkdir(parents=True, exist_ok=True)

    for schema_file in ("animation.schema.json", "scene.schema.json"):
        src = schemas_dir / schema_file
        dst = target_dir / schema_file

        if dst.exists():
            dst.unlink()

        shutil.copy2(src, dst)

    return target_dir


def setup_vscode(project_root):
    ensure_schemas_available(project_root, subdir=".vscode")

    vscode_dir = project_root / ".vscode"
    vscode_dir.mkdir(parents=True, exist_ok=True)

    settings_path = vscode_dir / "settings.json"

    settings = {}

    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text())
        except json.JSONDecodeError:
            settings = {}

    json_schemas = settings.get("json.schemas", [])

    animation_schema = {
        "fileMatch": ["**/Animations/*.json", "**/animations/*.json"],
        "url": ".vscode/schemas/animation.schema.json"
    }

    scene_schema = {
        "fileMatch": ["**/Scenes/*.json", "**/scenes/*.json"],
        "url": ".vscode/schemas/scene.schema.json"
    }

    new_schemas = [s for s in json_schemas
                   if ".vscode/schemas/animation.schema.json" not in s.get("url", "")
                   and ".vscode/schemas/scene.schema.json" not in s.get("url", "")]

    new_schemas.extend([animation_schema, scene_schema])
    settings["json.schemas"] = new_schemas

    settings["json.validate.enable"] = True

    settings_path.write_text(json.dumps(settings, indent=4) + "\n")

    print(f"VSCode configured: {settings_path}")
    return settings_path


def setup_zed(project_root):
    ensure_schemas_available(project_root, subdir=".zed")

    zed_dir = project_root / ".zed"
    zed_dir.mkdir(parents=True, exist_ok=True)

    settings_path = zed_dir / "settings.json"

    settings = {}

    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text())
        except json.JSONDecodeError:
            settings = {}

    lsp = settings.setdefault("lsp", {})
    json_ls = lsp.setdefault("json-language-server", {})
    ls_settings = json_ls.setdefault("settings", {})
    json_cfg = ls_settings.setdefault("json", {})
    schemas_list = json_cfg.setdefault("schemas", [])

    animation_entry = {
        "fileMatch": ["Animations/*.json"],
        "url": "./schemas/animation.schema.json"
    }

    scene_entry = {
        "fileMatch": ["Scenes/*.json"],
        "url": "./schemas/scene.schema.json"
    }

    new_schemas = [
        s for s in schemas_list
        if s.get("url") not in (
            "./schemas/animation.schema.json",
            "./schemas/scene.schema.json",
        )
    ]

    new_schemas.extend([scene_entry, animation_entry])
    json_cfg["schemas"] = new_schemas

    settings_path.write_text(json.dumps(settings, indent=2) + "\n")

    print(f"Zed configured: {settings_path}")
    return settings_path


def setup_editor(project_root, editor=None):
    project_root = Path(project_root).expanduser().resolve()

    if not project_root.is_dir():
        raise RuntimeError(f"Project directory does not exist: {project_root}")

    results = []

    if editor in (None, "vscode"):
        results.append(("vscode", setup_vscode(project_root)))

    if editor in (None, "zed"):
        results.append(("zed", setup_zed(project_root)))

    if not results:
        raise RuntimeError(f"Unknown editor: {editor}")

    return 0