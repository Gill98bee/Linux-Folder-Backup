#!/usr/bin/env python3

#############################
#                           #
#    By Gilbert A. Yeboah   #
#                           #
#############################

# WARNING! This simple script does not come with any guarantees and I will
# not be held responsible for any damage.

"""
backup.py - a simple command-line folder backup utility.

Creates a timestamped .zip archive of a source directory, preserving the
relative folder structure (instead of embedding absolute paths, which the
original version of this script did).

Usage:
    ./backup.py /path/to/folder
    ./backup.py /path/to/folder -o /path/to/output-dir
    ./backup.py /path/to/folder -n my-backup
    ./backup.py /path/to/folder -e "*.log" -e "__pycache__" -e "*.tmp"
    ./backup.py /path/to/folder --dry-run
"""

import argparse
import fnmatch
import os
import sys
import zipfile
from datetime import datetime


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="backup.py",
        description="Create a timestamped zip backup of a folder.",
    )
    parser.add_argument(
        "source",
        help="Path to the folder you want to back up.",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="/tmp",
        help="Directory to save the backup zip file in (default: /tmp).",
    )
    parser.add_argument(
        "-n", "--name",
        default=None,
        help=(
            "Base name for the backup file (default: the source folder's "
            "name). A timestamp is always appended."
        ),
    )
    parser.add_argument(
        "-e", "--exclude",
        action="append",
        default=[],
        metavar="PATTERN",
        help=(
            "Glob pattern to exclude (matched against file/dir names). "
            "Can be used multiple times, e.g. -e '*.log' -e '.git'."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List the files that would be backed up without creating a zip.",
    )
    return parser.parse_args(argv)


def is_excluded(name, patterns):
    return any(fnmatch.fnmatch(name, pattern) for pattern in patterns)


def collect_files(source, patterns):
    """Walk source and yield (absolute_path, relative_arcname) pairs,
    skipping anything that matches an exclude pattern."""
    source = os.path.abspath(source)
    for root, dirs, files in os.walk(source):
        # Prune excluded directories in-place so os.walk skips them.
        dirs[:] = [d for d in dirs if not is_excluded(d, patterns)]

        for file in files:
            if is_excluded(file, patterns):
                continue
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, os.path.dirname(source))
            yield full_path, arcname


def build_backup_filename(source, output_dir, name):
    base_name = name or os.path.basename(os.path.normpath(source)) or "backup"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{base_name}-{timestamp}.zip"
    return os.path.join(output_dir, filename)


def create_backup(source, output_dir, name, patterns, dry_run=False):
    source = os.path.abspath(os.path.expanduser(source))

    if not os.path.isdir(source):
        print(f"Error: source folder does not exist: {source}", file=sys.stderr)
        return 1

    files = list(collect_files(source, patterns))

    if not files:
        print(f"Warning: no files found to back up in {source}", file=sys.stderr)
        return 1

    if dry_run:
        print(f"Dry run: {len(files)} file(s) would be backed up from {source}")
        for _, arcname in files:
            print(f"  {arcname}")
        return 0

    output_dir = os.path.abspath(os.path.expanduser(output_dir))
    os.makedirs(output_dir, exist_ok=True)
    zip_path = build_backup_filename(source, output_dir, name)

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for full_path, arcname in files:
                try:
                    zipf.write(full_path, arcname)
                except (OSError, PermissionError) as exc:
                    print(f"Warning: skipping {full_path}: {exc}", file=sys.stderr)
    except OSError as exc:
        print(f"Error: could not write backup file {zip_path}: {exc}", file=sys.stderr)
        return 1

    print(f"Backup complete: {zip_path} ({len(files)} file(s))")
    return 0


def main(argv=None):
    args = parse_args(argv)
    return create_backup(
        source=args.source,
        output_dir=args.output_dir,
        name=args.name,
        patterns=args.exclude,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    sys.exit(main())
