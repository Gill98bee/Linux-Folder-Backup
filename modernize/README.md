# Minimal README for the modernized project

# Backuptool

A modernized, extensible Linux folder backup CLI intended as a portfolio project. It supports local and S3-compatible backends, client-side encryption, snapshot cataloging (SQLite), retention/pruning, and examples for systemd scheduling.

Quickstart (local-only):

```bash
python -m backuptool --help
python -m backuptool backup ~/projects -o ~/backups
python -m backuptool list -o ~/backups
