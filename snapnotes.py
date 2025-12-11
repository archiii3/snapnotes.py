"""
SnapNotes — Small GitHub-ready Python CLI note-taking tool
Repository name suggestion: snapnotes

What this file contains:
- README (in this file header)
- A single-file CLI app (works with Python 3.8+)

Features:
- add, list, view, delete, search, export commands
- stores notes as JSON in user home (~/.snapnotes/notes.json)
- small and easy to extend

Usage examples:
  python snapnotes.py add "Buy milk" --tags shopping,home
  python snapnotes.py list
  python snapnotes.py search milk
  python snapnotes.py export notes.md

License: MIT
"""

from __future__ import annotations
import argparse
import json
import os
import shutil
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional

APP_DIR = Path.home() / ".snapnotes"
NOTES_FILE = APP_DIR / "notes.json"

@dataclass
class Note:
    id: int
    title: str
    body: str
    tags: List[str]
    created_at: str


def ensure_store() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    if not NOTES_FILE.exists():
        with NOTES_FILE.open("w", encoding="utf-8") as f:
            json.dump({"next_id": 1, "notes": []}, f, ensure_ascii=False, indent=2)


def load_store() -> dict:
    ensure_store()
    with NOTES_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_store(data: dict) -> None:
    tmp = NOTES_FILE.with_suffix('.tmp')
    with tmp.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    shutil.move(str(tmp), str(NOTES_FILE))


def add_note(title: str, body: str, tags: Optional[List[str]]) -> Note:
    data = load_store()
    nid = data.get("next_id", 1)
    note = Note(
        id=nid,
        title=title.strip(),
        body=body.strip(),
        tags=[t.strip() for t in (tags or []) if t.strip()],
        created_at=datetime.utcnow().isoformat() + 'Z'
    )
    data["notes"].append(asdict(note))
    data["next_id"] = nid + 1
    save_store(data)
    return note


def list_notes() -> List[Note]:
    data = load_store()
    return [Note(**n) for n in data.get("notes", [])]


def find_note(note_id: int) -> Optional[Note]:
    for n in list_notes():
        if n.id == note_id:
            return n
    return None


def delete_note(note_id: int) -> bool:
    data = load_store()
    notes = data.get("notes", [])
    new_notes = [n for n in notes if n.get("id") != note_id]
    if len(new_notes) == len(notes):
        return False
    data["notes"] = new_notes
    save_store(data)
    return True


def search_notes(query: str) -> List[Note]:
    q = query.lower()
    result = []
    for n in list_notes():
        if q in n.title.lower() or q in n.body.lower() or any(q in t.lower() for t in n.tags):
            result.append(n)
    return result


def export_notes(path: str, fmt: str = "md") -> Path:
    notes = list_notes()
    out = Path(path)
    if fmt == "md":
        with out.open('w', encoding='utf-8') as f:
            for n in notes:
                f.write(f"# {n.title} (id={n.id})\n")
                f.write(f"_created: {n.created_at}_\n\n")
                if n.tags:
                    f.write(f"**tags:** {', '.join(n.tags)}\n\n")
                f.write(n.body + "\n\n---\n\n")
    else:
        with out.open('w', encoding='utf-8') as f:
            json.dump({"notes": [asdict(n) for n in notes]}, f, ensure_ascii=False, indent=2)
    return out


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="snapnotes", description="Small CLI note tool")
    sub = p.add_subparsers(dest='cmd')

    a_add = sub.add_parser('add', help='Add a new note')
    a_add.add_argument('title', help='Note title')
    a_add.add_argument('--body', '-b', default='', help='Note body (you can use quotes)')
    a_add.add_argument('--tags', '-t', help='Comma-separated tags')

    a_list = sub.add_parser('list', help='List notes')
    a_list.add_argument('--tags', help='Filter by tag (single)')

    a_view = sub.add_parser('view', help='View a note')
    a_view.add_argument('id', type=int, help='Note id')

    a_del = sub.add_parser('delete', help='Delete a note')
    a_del.add_argument('id', type=int, help='Note id')

    a_search = sub.add_parser('search', help='Search notes')
    a_search.add_argument('query', help='Search query')

    a_export = sub.add_parser('export', help='Export notes')
    a_export.add_argument('path', help='Output file path')
    a_export.add_argument('--format', choices=['md', 'json'], default='md')

    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if not args.cmd:
        print("No command provided. Use -h for help.")
        return 1

    if args.cmd == 'add':
        tags = args.tags.split(',') if getattr(args, 'tags', None) else []
        note = add_note(args.title, args.body or '', tags)
        print(f"Added note id={note.id} title={note.title}")
        return 0

    if args.cmd == 'list':
        notes = list_notes()
        if getattr(args, 'tags', None):
            notes = [n for n in notes if getattr(args, 'tags') in n.tags]
        if not notes:
            print("No notes yet.")
            return 0
        for n in notes:
            print(f"[{n.id}] {n.title} ({', '.join(n.tags)})")
        return 0

    if args.cmd == 'view':
        n = find_note(args.id)
        if not n:
            print(f"Note {args.id} not found")
            return 1
        print(f"{n.title} (id={n.id})\ncreated: {n.created_at}\ntags: {', '.join(n.tags)}\n\n{n.body}")
        return 0

    if args.cmd == 'delete':
        ok = delete_note(args.id)
        print("Deleted." if ok else "Note not found.")
        return 0

    if args.cmd == 'search':
        res = search_notes(args.query)
        if not res:
            print("No matches.")
            return 0
        for n in res:
            print(f"[{n.id}] {n.title} — {n.body[:80].replace('\n',' ')}")
        return 0

    if args.cmd == 'export':
        out = export_notes(args.path, fmt=args.format)
        print(f"Exported {out}")
        return 0

    print("Unknown command")
    return 1

if __name__ == '__main__':
    raise SystemExit(main())
