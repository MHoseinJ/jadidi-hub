from pathlib import Path

BASE_DIR = Path.home() / ".jadidi"
SOURCES_DIR = BASE_DIR / "sources"
INCLUDE_DIR = BASE_DIR / "include"
LIB_DIR = BASE_DIR / "lib"
CMAKE_DIR = LIB_DIR / "cmake" / "sol2"
ENGINE_SOURCE_DIR = SOURCES_DIR / "jadidi"
BUILDS_DIR = BASE_DIR / "builds"


def ensure_base_dirs():
    for path in (
        BASE_DIR,
        SOURCES_DIR,
        INCLUDE_DIR,
        LIB_DIR,
        CMAKE_DIR,
        BUILDS_DIR,
    ):
        path.mkdir(parents=True, exist_ok=True)