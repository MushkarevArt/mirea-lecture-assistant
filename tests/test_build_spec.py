"""Check the actual spec's binary selection without invoking PyInstaller."""

import ast
from pathlib import Path
from types import SimpleNamespace


def test_build_keeps_python_but_rejects_unrelated_native_tool_dlls():
    spec = Path(__file__).resolve().parents[1] / "MireaLectureAssistant.spec"
    tree = ast.parse(spec.read_text(encoding="utf-8"))
    selections = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and isinstance(node.value, ast.ListComp)
        and any(
            isinstance(name, ast.Name) and name.id == "qt_runtime_names"
            for name in ast.walk(node.value)
        )
        and any(
            isinstance(target, ast.Attribute) and target.attr == "binaries"
            for target in node.targets
        )
    ]
    assert len(selections) == 1
    root = r"C:\cache\codex-runtimes\codex-primary-runtime\dependencies"
    python = ("python312.dll", root + r"\python\python312.dll", "BINARY")
    ssl = ("_ssl.pyd", root + r"\python\DLLs\_ssl.pyd", "BINARY")
    qt = (r"PySide6\Qt6Core.dll", r"C:\project\.venv\PySide6\Qt6Core.dll", "BINARY")
    foreign_icu = ("icuuc.dll", root + r"\native\poppler\Library\bin\icuuc.dll", "BINARY")
    old_vc = ("vcruntime140.dll", root + r"\python\vcruntime140.dll", "BINARY")
    selected = eval(
        compile(ast.Expression(selections[0]), str(spec), "eval"),
        {
            "a": SimpleNamespace(binaries=[python, ssl, qt, foreign_icu, old_vc]),
            "qt_runtime_names": {"vcruntime140.dll"},
        },
    )
    assert selected == [python, ssl, qt]
