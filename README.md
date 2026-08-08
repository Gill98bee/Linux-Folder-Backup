# Linux-Folder-Backup

A simple, dependency-free Python command-line tool that creates a timestamped
`.zip` backup of a folder — your home directory, a web folder, a project
folder, etc. It only uses Python's standard library (`zipfile`, `argparse`,
`os`), so there is nothing extra to install.

## Requirements

- Python 3.6+ (uses f-strings and the standard library only)

## Usage

Make the script executable once:

```bash
chmod +x backup.py
```

Then run it, pointing it at the folder you want to back up:

```bash
./backup.py /path/to/your/folder
```

or

```bash
python3 backup.py /path/to/your/folder
```

By default the backup zip is written to `/tmp` and named after the source
folder plus a timestamp, e.g. `/tmp/folder-20260808-153000.zip`.

### Options

| Flag | Description |
|---|---|
| `-o`, `--output-dir DIR` | Directory to save the backup zip in (default: `/tmp`) |
| `-n`, `--name NAME` | Base name for the backup file (default: source folder's name) |
| `-e`, `--exclude PATTERN` | Glob pattern to exclude; can be used multiple times |
| `--dry-run` | List the files that would be backed up without creating a zip |
| `-h`, `--help` | Show usage information |

### Examples

Back up your home folder to `~/backups`:

```bash
./backup.py ~ -o ~/backups
```

Give the backup a custom name:

```bash
./backup.py /var/www -n website-backup
```

Exclude log files, `.git` folders, and `node_modules`:

```bash
./backup.py ./my-project -e "*.log" -e ".git" -e "node_modules"
```

Preview what would be included without creating a zip:

```bash
./backup.py ./my-project --dry-run
```

## Notes

- Relative folder structure is preserved inside the zip archive.
- Files that can't be read (permission errors, etc.) are skipped with a
  warning instead of stopping the whole backup.
- If you edited this script on Windows and see errors when running it on
  Linux, convert the line endings with `dos2unix`:

  ```bash
  sudo apt install dos2unix
  dos2unix backup.py
  ```

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE).

## Disclaimer

This script comes with no guarantees. Always verify your backups before
relying on them, and test on non-critical data first.
