import os
from pathlib import Path
import json

config = json.load(open("config.json"))

def _ensure_dir(guild_id: str):
    base = os.path.join(config["stock-storage-path"], str(guild_id))
    os.makedirs(base, exist_ok=True)
    return base

def get_stock_path(guild_id, service_name) -> str:
    base = _ensure_dir(guild_id)
    return os.path.join(base, f"{service_name}.txt")

def read_stock_file(guild_id, service_name) -> list[str]:
    path = get_stock_path(guild_id, service_name)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f if line.strip()]

def write_stock_file(guild_id, service_name, lines: list[str]):
    path = get_stock_path(guild_id, service_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def pop_from_stock_file(guild_id, service_name) -> str | None:
    lines = read_stock_file(guild_id, service_name)
    if not lines:
        return None
    item = lines.pop(0)
    write_stock_file(guild_id, service_name, lines)
    return item

def pop_multiple_from_stock_file(guild_id, service_name, amount: int) -> list[str]:
    lines = read_stock_file(guild_id, service_name)
    popped = lines[:amount]
    remaining = lines[amount:]
    write_stock_file(guild_id, service_name, remaining)
    return popped

def append_to_stock_file(guild_id, service_name, new_lines: list[str]) -> tuple[int, int]:
    existing = set(read_stock_file(guild_id, service_name))
    added = []
    dupes = 0
    for line in new_lines:
        if line in existing:
            dupes += 1
        else:
            added.append(line)
            existing.add(line)
    if added:
        path = get_stock_path(guild_id, service_name)
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(added) + "\n")
    return len(added), dupes

def count_stock_file(guild_id, service_name) -> int:
    return len(read_stock_file(guild_id, service_name))

def delete_stock_file(guild_id, service_name):
    path = get_stock_path(guild_id, service_name)
    if os.path.exists(path):
        os.remove(path)
