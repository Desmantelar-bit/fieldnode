#!/usr/bin/env python
"""
Validacao rapida da estrutura atual do FieldNode.

Nao executa servidores. A ideia e pegar erro bobo antes da banca pegar,
porque a banca nao costuma dar desconto por link fossilizado.
"""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


def check(condition, description):
    marker = "OK" if condition else "ERRO"
    print(f"[{marker}] {description}")
    return bool(condition)


def file_contains(path, text):
    target = ROOT / path
    return target.exists() and text in target.read_text(encoding="utf-8")


def main():
    print("\nVALIDACAO FIELDNODE\n")

    checks = [
        check((ROOT / "frontend-next/src/app/dashboard/page.tsx").exists(), "rota Next /dashboard existe"),
        check((ROOT / "frontend-next/src/app/colheitadeiras/page.tsx").exists(), "rota Next /colheitadeiras existe"),
        check((ROOT / "frontend-next/src/app/operarios/page.tsx").exists(), "rota Next /operarios existe"),
        check((ROOT / "frontend-next/src/app/detalhes/page.tsx").exists(), "rota Next /detalhes existe"),
        check((ROOT / "frontend-next/src/components/AppShell.tsx").exists(), "AppShell compartilhado existe"),
        check((ROOT / "frontend-next/tailwind.config.ts").exists(), "tailwind.config.ts existe"),
        check(file_contains("frontend-next/next.config.ts", 'output: "standalone"'), "Next configurado para build standalone"),
        check(file_contains("docker-compose.yml", "frontend:"), "docker-compose sobe frontend"),
        check(file_contains("docker-compose.yml", "FIELDNODE_SERVER_API_URL=http://web:8000/api"), "frontend container aponta para API interna"),
        check(file_contains("setup/urls.py", "api/health/"), "endpoint /api/health/ registrado"),
        check(file_contains("api_tcc/api/views_ingestao.py", "X-API-Key"), "ingestao documenta API key"),
        check(file_contains("api_tcc/api/views_ingestao.py", "_verificar_api_key"), "ingestao valida API key"),
        check(file_contains(".gitignore", ".env"), ".env ignorado pelo git"),
        check(not (ROOT / "frontend-old").exists(), "frontend-old removido"),
        check(not (ROOT / "frontend").exists(), "starter frontend antigo removido"),
    ]

    passed = sum(checks)
    total = len(checks)
    print(f"\nResultado: {passed}/{total}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
