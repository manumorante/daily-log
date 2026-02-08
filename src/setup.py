#!/usr/bin/env python3
"""
Setup interactivo para daily-log.
Crea la configuración inicial pidiendo los tokens necesarios.
"""

import json
import os
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ui

CONFIG_DIR = Path.home() / ".config" / "daily-log"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "github_token": "",
    "github_username": "",
    "shortcut_token": "",
    "anthropic_api_key": "",
    "wakatime_api_key": "",
    "git_repos": [],
    "anthropic_model": "claude-sonnet-4-5-20250929",
}


def ask(prompt: str, default: str = "", secret: bool = False) -> str:
    """Pide input al usuario."""
    suffix = f" [{default}]" if default else ""
    if secret:
        import getpass
        val = getpass.getpass(f"{prompt}{suffix}: ")
    else:
        val = input(f"{prompt}{suffix}: ")
    return val.strip() or default


def find_git_repos(base_dirs: list[str], max_depth: int = 2) -> list[str]:
    """Busca repos git en los directorios dados."""
    repos = []
    for base in base_dirs:
        base = os.path.expanduser(base)
        if not os.path.isdir(base):
            continue
        try:
            result = subprocess.run(
                ["find", base, "-maxdepth", str(max_depth), "-name", ".git", "-type", "d"],
                capture_output=True, text=True, timeout=10,
            )
            for line in result.stdout.strip().split("\n"):
                if line:
                    repo = os.path.dirname(line)
                    repos.append(repo)
        except Exception:
            pass
    return sorted(repos)


def mask(value: str) -> str:
    """Enmascara un token mostrando solo los últimos 4 caracteres."""
    if len(value) <= 4:
        return "****"
    return "****" + value[-4:]


def setup_github(config: dict):
    """Configura GitHub."""
    print(f"  {ui.dim('GitHub')}")
    config["github_username"] = ask(
        "GitHub username", config.get("github_username", "")
    )
    config["github_token"] = ask(
        "GitHub token (ghp_...)", config.get("github_token", ""), secret=True
    ) or config.get("github_token", "")
    print()


def setup_shortcut(config: dict):
    """Configura Shortcut."""
    print(f"  {ui.dim('Shortcut')}")
    config["shortcut_token"] = ask(
        "Shortcut API token", config.get("shortcut_token", ""), secret=True
    ) or config.get("shortcut_token", "")
    print()


def setup_anthropic(config: dict):
    """Configura Anthropic."""
    print(f"  {ui.dim('Claude API')}")
    config["anthropic_api_key"] = ask(
        "Anthropic API key (sk-ant-...)", config.get("anthropic_api_key", ""), secret=True
    ) or config.get("anthropic_api_key", "")
    config["anthropic_model"] = ask(
        "Modelo", config.get("anthropic_model", "claude-sonnet-4-5-20250929")
    )
    print()


def setup_wakatime(config: dict):
    """Configura WakaTime."""
    print(f"  {ui.dim('WakaTime')}")
    config["wakatime_api_key"] = ask(
        "WakaTime API key", config.get("wakatime_api_key", ""), secret=True
    ) or config.get("wakatime_api_key", "")
    print()


def setup_repos(config: dict):
    """Configura repos locales."""
    print(f"  {ui.dim('Git repos locales')}")
    scan = ask("Buscar repos automaticamente? (s/n)", "s")
    if scan.lower() in ("s", "si", "sí", "y", "yes"):
        search_dirs = ask(
            "Directorios a escanear (separados por coma)",
            "~/Code,~/Projects,~/Dev"
        )
        dirs = [d.strip() for d in search_dirs.split(",")]
        repos = find_git_repos(dirs)
        if repos:
            print(f"\n  Encontrados {len(repos)} repos:")
            for i, r in enumerate(repos):
                print(f"    {ui.dim(str(i+1))}. {r}")
            use_all = ask("\nUsar todos? (s/n/numeros separados por coma)", "s")
            if use_all.lower() in ("s", "si", "sí", "y", "yes"):
                config["git_repos"] = repos
            elif use_all.replace(",", "").replace(" ", "").isdigit():
                indices = [int(x.strip()) - 1 for x in use_all.split(",")]
                config["git_repos"] = [repos[i] for i in indices if 0 <= i < len(repos)]
        else:
            ui.skip("No se encontraron repos.")
    else:
        manual = ask("Paths de repos (separados por coma)", "")
        if manual:
            config["git_repos"] = [p.strip() for p in manual.split(",")]
    print()


SECTIONS = [
    ("GitHub", "github", lambda c: bool(c.get("github_token") and c.get("github_username")), setup_github),
    ("Shortcut", "shortcut", lambda c: bool(c.get("shortcut_token")), setup_shortcut),
    ("Claude API", "anthropic", lambda c: bool(c.get("anthropic_api_key")), setup_anthropic),
    ("WakaTime", "wakatime", lambda c: bool(c.get("wakatime_api_key")), setup_wakatime),
    ("Git repos", "repos", lambda c: bool(c.get("git_repos")), setup_repos),
]


def main():
    ui.header("daily-log setup")

    # Cargar config existente o crear nueva
    existing = {}
    if CONFIG_FILE.exists():
        existing = json.loads(CONFIG_FILE.read_text())

    config = {**DEFAULT_CONFIG, **existing}

    # Mostrar estado actual y detectar qué falta
    pending = []
    configured = []
    for name, key, check, setup_fn in SECTIONS:
        if check(config):
            configured.append((name, key, check, setup_fn))
        else:
            pending.append((name, key, check, setup_fn))

    if configured:
        for name, _, _, _ in configured:
            print(f"  {ui.OK} {name}")

    if pending:
        for name, _, _, _ in pending:
            print(f"  {ui.SKIP} {ui.dim(name)}")
        print()

        # Solo configurar lo que falta
        for name, key, check, setup_fn in pending:
            setup_fn(config)
    else:
        print()
        ui.info("Todo configurado.")
        reconf = ask("Reconfigurar algo? (s/n)", "n")
        if reconf.lower() not in ("s", "si", "sí", "y", "yes"):
            print()
            ui.info("Ejecuta: ./daily-log")
            return
        print()
        # Mostrar menú para elegir qué reconfigurar
        for i, (name, _, _, _) in enumerate(SECTIONS):
            print(f"  {ui.dim(str(i+1))}. {name}")
        choices = ask("\nNumeros a reconfigurar (separados por coma)", "")
        if choices:
            indices = [int(x.strip()) - 1 for x in choices.split(",") if x.strip().isdigit()]
            print()
            for i in indices:
                if 0 <= i < len(SECTIONS):
                    SECTIONS[i][3](config)

    # Guardar
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    ui.separator()
    for name, _, check, _ in SECTIONS:
        if check(config):
            print(f"  {ui.OK} {name}")
        else:
            print(f"  {ui.SKIP} {ui.dim(name)}")

    ui.done(f"Config guardada: {CONFIG_FILE}")
    print()
    ui.info("Ejecuta: ./daily-log")


if __name__ == "__main__":
    main()
