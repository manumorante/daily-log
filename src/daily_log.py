#!/usr/bin/env python3
"""
Daily Log Generator
Recopila actividad diaria de multiples fuentes y genera un resumen con Claude.
"""

import os
import sys
import json
import urllib.error
from datetime import datetime
from pathlib import Path

# Imports locales
sys.path.insert(0, str(Path(__file__).parent))
import ui
from api import fetch
from collectors import ALL as COLLECTORS

# ─── Config ──────────────────────────────────────────────────────────────────

CONFIG_DIR = Path.home() / ".config" / "daily-log"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOGS_DIR = Path.home() / "daily-logs"

DEFAULT_CONFIG = {
    "github_token": "",
    "github_username": "",
    "shortcut_token": "",
    "anthropic_api_key": "",
    "git_repos": [],
    "anthropic_model": "claude-sonnet-4-5-20250929",
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
        ui.warn(f"Config creada en: {CONFIG_FILE}")
        ui.info("Ejecuta: ./daily-log --setup")
        sys.exit(1)

    config = json.loads(CONFIG_FILE.read_text())

    env_map = {
        "GITHUB_TOKEN": "github_token",
        "GITHUB_USERNAME": "github_username",
        "SHORTCUT_TOKEN": "shortcut_token",
        "ANTHROPIC_API_KEY": "anthropic_api_key",
    }
    for env_key, config_key in env_map.items():
        val = os.environ.get(env_key)
        if val:
            config[config_key] = val

    return config


# ─── Summarizer ──────────────────────────────────────────────────────────────

SUMMARY_PROMPT = """Eres un asistente que genera resumenes diarios de actividad de un desarrollador.

Te voy a dar datos en JSON de diferentes fuentes (GitHub, Shortcut, git local).
Genera un resumen en Markdown del dia con estas secciones:

## Resumen del dia — {date}

### Actividad destacada
Un parrafo breve de 2-3 frases resumiendo lo mas importante del dia.

### Codigo
- Commits relevantes agrupados por repo
- PRs creadas/mergeadas/revisadas

### Tareas (Shortcut)
- Stories completadas
- Stories en progreso

### Notas
- Cualquier observacion relevante sobre patrones de trabajo

Reglas:
- Escribe en espanol
- Se conciso, no repitas info
- Si una seccion esta vacia, omitela
- Los commits de merge o triviales no hace falta listarlos individualmente
- Agrupa commits relacionados
"""


def generate_summary(config: dict, date: str, collected_data: list) -> str:
    api_key = config.get("anthropic_api_key")
    if not api_key:
        return _fallback_summary(date, collected_data)

    model = config.get("anthropic_model", "claude-sonnet-4-5-20250929")
    prompt = (
        SUMMARY_PROMPT.replace("{date}", date)
        + "\n\nDatos del dia:\n```json\n"
        + json.dumps(collected_data, indent=2, ensure_ascii=False)
        + "\n```"
    )

    try:
        result = fetch(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": model,
                "max_tokens": 2048,
                "messages": [{"role": "user", "content": prompt}],
            }).encode("utf-8"),
        )
        return "\n".join(
            b["text"] for b in result.get("content", []) if b.get("type") == "text"
        )

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(body).get("error", {}).get("message", body)
        except Exception:
            detail = body
        ui.err(f"API Claude: {e.code} {e.reason}")
        ui.info(detail)
        return _fallback_summary(date, collected_data)
    except Exception as e:
        ui.err(f"API Claude: {e}")
        return _fallback_summary(date, collected_data)


def _has_changes(log_file: Path, raw: str) -> bool:
    """Compara datos crudos actuales con los del log existente."""
    try:
        content = log_file.read_text()
        # Extraer JSON del bloque <details>
        start = content.find("```json\n")
        end = content.find("\n```\n\n</details>")
        if start == -1 or end == -1:
            return True
        existing_raw = content[start + 8:end]
        return existing_raw.strip() != raw.strip()
    except Exception:
        return True


def _has_activity(collected_data: list) -> bool:
    for source in collected_data:
        if source.get("status") == "skipped" or "error" in source:
            continue
        name = source.get("source", "")
        if name == "github" and (source.get("commits") or source.get("events")):
            return True
        if name == "shortcut" and (source.get("stories_completed") or source.get("stories_updated")):
            return True
        if name == "git_local" and source.get("repos"):
            return True
    return False


def _fallback_summary(date: str, collected_data: list) -> str:
    lines = [f"## Registro del dia — {date}\n"]

    for source in collected_data:
        name = source.get("source", "unknown")

        if name == "github":
            commits = source.get("commits", [])
            events = source.get("events", [])
            if commits or events:
                lines.append("### GitHub\n")
                for c in commits:
                    lines.append(f"- `{c['sha']}` {c['message']} ({c['repo']})")
                for e in events:
                    lines.append(f"- {e['type']}: {e.get('title', '')} ({e['repo']})")
                lines.append("")

        elif name == "shortcut":
            completed = source.get("stories_completed", [])
            updated = source.get("stories_updated", [])
            if completed or updated:
                lines.append("### Shortcut\n")
                if completed:
                    lines.append("**Completadas:**")
                    for s in completed:
                        lines.append(f"- [{s['type']}] {s['name']} (#{s['id']})")
                if updated:
                    lines.append("**En progreso:**")
                    for s in updated:
                        lines.append(
                            f"- [{s['type']}] {s['name']} (#{s['id']}) — {s['workflow_state']}"
                        )
                lines.append("")

        elif name == "git_local":
            repos = source.get("repos", [])
            if repos:
                lines.append("### Git Local\n")
                for repo in repos:
                    lines.append(f"**{repo['name']}**")
                    for c in repo.get("commits", []):
                        lines.append(f"- `{c['sha']}` {c['message']}")
                lines.append("")

    return "\n".join(lines)


# ─── Main ────────────────────────────────────────────────────────────────────


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Daily Log Generator")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="Fecha del log (YYYY-MM-DD)")
    parser.add_argument("--no-ai", action="store_true",
                        help="Generar log sin resumen de AI")
    parser.add_argument("--output-dir", default=str(LOGS_DIR),
                        help=f"Directorio de salida (default: {LOGS_DIR})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostrar datos recopilados sin generar el log")
    parser.add_argument("--setup", action="store_true",
                        help="Ejecutar el setup interactivo")
    args = parser.parse_args()

    if args.setup:
        setup_script = Path(__file__).parent / "setup.py"
        os.execvp(sys.executable, [sys.executable, str(setup_script)])

    date = args.date
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ui.header(f"daily-log {ui.dim(date)}")

    config = load_config()

    # Verificar fuentes configuradas
    missing = []
    if not config.get("github_token") or not config.get("github_username"):
        missing.append("GitHub (token / username)")
    if not config.get("shortcut_token"):
        missing.append("Shortcut (token)")
    if not config.get("git_repos"):
        missing.append("Git repos locales")

    if len(missing) == 3:
        ui.warn("No hay ninguna fuente de datos configurada:")
        for m in missing:
            ui.item(ui.dim(m))
        print()
        ui.info("Ejecuta: ./daily-log --setup")
        print()
        sys.exit(1)

    if missing:
        ui.warn("Fuentes sin configurar (se omitiran):")
        for m in missing:
            ui.item(ui.dim(m))
        ui.info("Puedes completar con: ./daily-log --setup")
        print()

    # Recopilar datos
    collected = []
    for name, collector in COLLECTORS:
        print(f"  {ui.dim('▸')} {name}", end="  ", flush=True)
        try:
            data = collector(config, date)
            status = data.get("status", "ok")
            if status == "skipped":
                print(ui.dim(f"○ {data.get('reason', '')}"))
            elif "error" in data:
                print(f"{ui.WARN} {ui.yellow(data['error'])}")
            else:
                print(ui.OK)
            collected.append(data)
        except Exception as e:
            print(f"{ui.ERR} {ui.red(str(e))}")
            collected.append({"source": name.lower(), "error": str(e)})

    if args.dry_run:
        print()
        ui.info("Datos recopilados:")
        print(json.dumps(collected, indent=2, ensure_ascii=False))
        return

    # Ruta del log
    year_month = date[:7].replace("-", "/")
    log_dir = output_dir / year_month
    log_file = log_dir / f"{date}.md"
    short_path = str(log_file).replace(str(Path.home()), "~")

    # Comprobar si hay datos nuevos
    has_data = _has_activity(collected)

    raw = json.dumps(collected, indent=2, ensure_ascii=False)

    if log_file.exists() and not _has_changes(log_file, raw):
        ui.separator()
        ui.info(f"Sin cambios nuevos. Log existente: {short_path}")
    else:
        # Generar resumen
        ui.separator()
        if args.no_ai:
            ui.run("Generando log (sin AI)...")
            summary = _fallback_summary(date, collected)
        else:
            ui.run("Generando resumen con Claude...")
            summary = generate_summary(config, date, collected)

        # Guardar
        log_dir.mkdir(parents=True, exist_ok=True)

        output = (
            summary
            + "\n\n---\n\n"
            + "<details>\n<summary>Datos crudos</summary>\n\n"
            + f"```json\n{raw}\n```\n\n"
            + "</details>\n"
        )

        log_file.write_text(output)
        ui.done(f"Log guardado: {short_path}")

    # Ofrecer abrir
    if log_file.exists():
        print()
        try:
            choice = input(f"  {ui.dim('Abrir? (s/n)')} [{ui.dim('s')}]: ").strip()
            if choice.lower() not in ("n", "no"):
                import subprocess
                subprocess.Popen(["open", str(log_file)])
        except (KeyboardInterrupt, EOFError):
            pass


if __name__ == "__main__":
    main()
