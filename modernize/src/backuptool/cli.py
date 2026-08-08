"""CLI for backuptool."""

from pathlib import Path
import getpass
import typer
from rich.console import Console

from .core import BackupManager
from .encrypt import Passphrase

app = typer.Typer(help="Backuptool: modern folder backup CLI")
console = Console()


def _load_passphrase(passphrase: str | None) -> Passphrase:
    if passphrase:
        return Passphrase.from_passphrase(passphrase)
    env = None
    return Passphrase.prompt_if_needed(env)


@app.command()
def backup(
    source: Path = typer.Argument(..., help="Source folder to back up"),
    output: Path = typer.Option(Path("~/backups"), help="Output/store root"),
    name: str | None = typer.Option(None, "-n", help="Snapshot name"),
    passphrase: str | None = typer.Option(None, "--passphrase", help="Encryption passphrase (optional)"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Create a snapshot of SOURCE and store it in OUTPUT."""
    mgr = BackupManager(output.expanduser())
    pp = _load_passphrase(passphrase)
    snapshot_id = mgr.create_snapshot(source.expanduser(), name=name, passphrase=pp, dry_run=dry_run)
    if snapshot_id and not dry_run:
        console.print(f"Created snapshot [green]{snapshot_id}[/]")


@app.command()
def list(output: Path = typer.Option(Path("~/backups"), help="Output/store root")):
    """List existing snapshots."""
    mgr = BackupManager(output.expanduser())
    snaps = mgr.list_snapshots()
    for s in snaps:
        console.print(f"- {s['id']}  {s['created_at']}  {s['name']}")


@app.command()
def prune(
    output: Path = typer.Option(Path("~/backups")),
    keep_last: int = typer.Option(30, help="Keep last N snapshots"),
    keep_days: int = typer.Option(90, help="Also keep snapshots not older than N days"),
):
    """Prune snapshots according to retention rules."""
    mgr = BackupManager(output.expanduser())
    removed = mgr.prune(keep_last=keep_last, keep_days=keep_days)
    console.print(f"Pruned {removed} snapshot(s)")


@app.command()
def restore(
    snapshot_id: str = typer.Argument(...),
    target: Path = typer.Argument(..., help="Path to restore into"),
    output: Path = typer.Option(Path("~/backups")) ,
    passphrase: str | None = typer.Option(None, "--passphrase", help="Decryption passphrase (if used)"),
):
    """Restore a snapshot into TARGET."""
    mgr = BackupManager(output.expanduser())
    pp = _load_passphrase(passphrase)
    mgr.restore_snapshot(snapshot_id, target.expanduser(), passphrase=pp)

