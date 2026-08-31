import json
import shutil
import stat
import struct
import subprocess
from pathlib import Path

from src import engine
from src import paths

PROJECT_DIRS = [
    "Fonts",
    "Scenes",
    "Scripts",
    "Shaders",
]

SPRITE_VERTEX_SHADER = """#version 330 core
layout (location = 0) in vec2 aPos;
layout (location = 1) in vec2 aTexCoord;

out vec2 TexCoord;

uniform mat4 model;
uniform mat4 projection;

void main() {
    gl_Position = projection * model * vec4(aPos, 0.0, 1.0);
    TexCoord = aTexCoord;
}
"""

SPRITE_FRAGMENT_SHADER = """#version 330 core
in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D image;
uniform vec4 spriteColor;

void main() {
    FragColor = spriteColor * texture(image, TexCoord);
}
"""

IDE_DIR_CANDIDATES = [
    "ide autocompletion",
    "ide_autocompletion",
    "ide-autocompletion",
    "IDE Autocompletion",
]

SYSTEM_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/liberation/LiberationSans-Regular.ttf",
]


def assets_dir():
    return paths.BASE_DIR / "assets"


def local_icon():
    return assets_dir() / "icon.bmp"


def local_font():
    return assets_dir() / "font.ttf"


def normalize_name(name):
    return "".join(ch for ch in name.lower() if ch.isalnum())


def find_ide_autocompletion_dir():
    source = paths.ENGINE_SOURCE_DIR

    if not source.exists():
        return None

    for name in IDE_DIR_CANDIDATES:
        candidate = source / name

        if candidate.is_dir():
            return candidate

    wanted = {normalize_name(name) for name in IDE_DIR_CANDIDATES}

    for child in source.iterdir():
        if child.is_dir() and normalize_name(child.name) in wanted:
            return child

    for child in source.iterdir():
        if child.is_dir():
            normalized = normalize_name(child.name)

            if "ide" in normalized and "autocompletion" in normalized:
                return child

    return None


def make_bmp():
    file_size = 58
    offset = 54

    header = struct.pack("<2sIHHI", b"BM", file_size, 0, 0, offset)
    info = struct.pack(
        "<IiiHHIIiiII",
        40,
        1,
        1,
        1,
        24,
        0,
        4,
        2835,
        2835,
        0,
        0,
    )
    pixel = b"\x00\x00\xff\x00"

    return header + info + pixel


def find_binary(version=None):
    builds_dir = paths.BUILDS_DIR

    if version:
        version = engine.safe_name(version)
        binary = builds_dir / version / "jadidi"

        if binary.exists():
            return binary

        raise RuntimeError(f"Engine binary not found: {binary}")

    try:
        current_version = engine.get_version_name()
        binary = builds_dir / current_version / "jadidi"

        if binary.exists():
            return binary
    except Exception:
        pass

    if builds_dir.exists():
        candidates = sorted(
            builds_dir.iterdir(),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        for candidate in candidates:
            binary = candidate / "jadidi"

            if binary.exists():
                return binary

    raise RuntimeError(
        "Engine binary not found. Run: python main.py engine-build"
    )


def write_config(project_root):
    config_path = project_root / "config.json"

    if config_path.exists():
        return

    config = {
        "window": {
            "fullscreen": False,
            "height": 720,
            "icon": "icon.bmp",
            "renderer": "opengl",
            "title": project_root.name,
            "width": 1280,
        }
    }

    config_path.write_text(json.dumps(config, indent=4) + "\n")


def write_home_scene(project_root):
    home_path = project_root / "Scenes" / "home.json"

    if home_path.exists():
        return

    home_path.write_text('{ "objects": [] }\n')


def write_shaders(project_root):
    shaders_dir = project_root / "Shaders"

    vert_path = shaders_dir / "sprite.vert"
    frag_path = shaders_dir / "sprite.frag"

    if not vert_path.exists():
        vert_path.write_text(SPRITE_VERTEX_SHADER.lstrip())

    if not frag_path.exists():
        frag_path.write_text(SPRITE_FRAGMENT_SHADER.lstrip())


def copy_icon(project_root):
    icon_path = project_root / "icon.bmp"

    if icon_path.exists():
        return

    if local_icon().exists():
        shutil.copy2(local_icon(), icon_path)
        return

    icon_path.write_bytes(make_bmp())


def copy_font(project_root):
    font_path = project_root / "Fonts" / "font.ttf"

    if font_path.exists():
        return

    if local_font().exists():
        shutil.copy2(local_font(), font_path)
        return

    for candidate in SYSTEM_FONT_CANDIDATES:
        candidate_path = Path(candidate)

        if candidate_path.exists():
            shutil.copy2(candidate_path, font_path)
            return

    font_path.write_bytes(b"")
    print(f"Warning: created empty {font_path}. Replace it with a real TTF font.")


def copy_ide_autocompletion(project_root, ide_dir):
    target = project_root / ide_dir.name

    if target.exists():
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()

    shutil.copytree(ide_dir, target)

    return target


def write_gitignore(project_root):
    gitignore_path = project_root / ".gitignore"

    if gitignore_path.exists():
        return

    gitignore_path.write_text("jadidi\n")


def run_git_init(project_root):
    if not shutil.which("git"):
        raise RuntimeError("git is not installed")

    subprocess.run(
        ["git", "init"],
        cwd=project_root,
        check=True,
    )


def create_project(path, version=None, git_init=False):
    project_root = Path(path).expanduser().resolve()

    if project_root.exists() and project_root.is_file():
        raise RuntimeError(f"{project_root} is a file")

    if project_root.exists() and any(project_root.iterdir()):
        raise RuntimeError(f"{project_root} is not empty")

    ide_dir = find_ide_autocompletion_dir()

    if not ide_dir:
        raise RuntimeError(
            "ide autocompletion directory not found in engine source"
        )

    project_root.mkdir(parents=True, exist_ok=True)

    for directory in PROJECT_DIRS:
        (project_root / directory).mkdir(parents=True, exist_ok=True)

    write_config(project_root)
    write_home_scene(project_root)
    write_shaders(project_root)
    copy_icon(project_root)
    copy_font(project_root)

    ide_target = copy_ide_autocompletion(project_root, ide_dir)

    binary_src = find_binary(version)
    binary_dst = project_root / "jadidi"

    shutil.copy2(binary_src, binary_dst)
    binary_dst.chmod(
        binary_dst.stat().st_mode
        | stat.S_IXUSR
        | stat.S_IXGRP
        | stat.S_IXOTH
    )

    print(f"Project created: {project_root}")
    print(f"Engine binary: {binary_dst}")
    print(f"Binary source: {binary_src}")
    print(f"IDE autocompletion: {ide_target}")

    if git_init:
        write_gitignore(project_root)
        run_git_init(project_root)
        print(f"Git repository initialized: {project_root / '.git'}")

    return 0