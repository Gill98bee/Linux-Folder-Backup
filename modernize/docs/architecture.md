# Architecture overview

This project is organized around a few core ideas:

- A Catalog (SQLite) that records snapshots and file->object mappings.
- An object store that is pluggable (local filesystem, S3, SSH).
- Encryption is applied per-object when enabled using AES-GCM.
- A CLI powered by Typer exposing snapshot lifecycle commands: backup, list, restore, prune.

See the docs/ directory for more detailed HOWTOs and systemd examples.
