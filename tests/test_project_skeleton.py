from pathlib import Path


ROOT_FILES = [
    "main.py",
    "requirements.txt",
    "app/__init__.py",
    "ui/__init__.py",
    "services/__init__.py",
    "services/excel/__init__.py",
    "services/transform/__init__.py",
    "services/chart/__init__.py",
    "services/logging/__init__.py",
]


def test_project_skeleton_exists():
    for path in ROOT_FILES:
        assert Path(path).exists(), path


def test_claude_md_mentions_run_and_test_commands():
    content = Path("CLAUDE.md").read_text(encoding="utf-8")
    assert "python main.py" in content
    assert "pytest" in content


def test_packaging_files_exist():
    assert Path("desktop-data-analyzer.spec").exists()
    assert Path("scripts/build_exe.py").exists()


def test_claude_md_mentions_build_command():
    content = Path("CLAUDE.md").read_text(encoding="utf-8")
    assert "python scripts/build_exe.py" in content


def test_user_guide_exists():
    assert Path("docs/user-guide.md").exists()
