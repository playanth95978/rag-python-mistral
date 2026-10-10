import ast
from pathlib import Path


def test_domain_and_services_are_independent_of_adapters_and_frameworks():
    root = Path(__file__).resolve().parents[2] / "app"
    forbidden = ("fastapi", "httpx", "mistralai", "pydantic", "app.infrastructure", "app.api")
    for layer in ("domain", "services"):
        for path in (root / layer).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8-sig"))
            for node in ast.walk(tree):
                modules = (
                    [alias.name for alias in node.names]
                    if isinstance(node, ast.Import)
                    else [node.module or ""]
                    if isinstance(node, ast.ImportFrom)
                    else []
                )
                for module in modules:
                    assert not any(
                        module == prefix or module.startswith(prefix + ".") for prefix in forbidden
                    ), f"{path}: dépendance interdite {module}"
