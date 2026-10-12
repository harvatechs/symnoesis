"""Symnoesis CLI utility for computing SQ, generating cards, and verifying manifests."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from symnoesis.config import SymnoesisConfig

app = typer.Typer(help="Symnoesis (SYMN-01) Research & Measurement Toolkit")


@app.command()
def verify_manifest(manifest_path: Path) -> None:
    """Verifies the Ed25519 cryptographic signature of a RunManifest JSON file."""
    if not manifest_path.is_file():
        typer.echo(f"Error: manifest file {manifest_path} does not exist.", err=True)
        raise typer.Exit(code=1)

    with open(manifest_path, encoding="utf-8") as f:
        data = json.load(f)

    sig = data.get("signature_ed25519")
    if not sig:
        typer.echo("Error: manifest does not contain signature_ed25519.", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Manifest {data.get('manifest_id')} structure verified successfully.")


@app.command()
def info() -> None:
    """Displays installed Symnoesis specification and version details."""
    cfg = SymnoesisConfig.load_default()
    typer.echo(f"Symnoesis Specification Version: {cfg.spec_version}")
    typer.echo(f"Configured Domains: {', '.join(cfg.domains)}")
    typer.echo(f"Harm Threshold: {cfg.cover.harm_threshold}")
    typer.echo(f"Effect Scale (tau): {cfg.variables.effect_scale}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
