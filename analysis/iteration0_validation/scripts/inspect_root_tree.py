#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import uproot


def branch_to_dict(tree, name):
    branch = tree[name]
    return {
        "name": name,
        "typename": getattr(branch, "typename", ""),
        "interpretation": str(getattr(branch, "interpretation", "")),
    }


def main():
    parser = argparse.ArgumentParser(description="Inspect the ROOT tree structure.")
    parser.add_argument("root_file")
    parser.add_argument("--tree", default="hodo")
    parser.add_argument("--tag", default="tree")
    parser.add_argument("--out-dir", default=".")
    args = parser.parse_args()

    root_file = Path(args.root_file)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    table_dir = out_dir / "tables"

    with uproot.open(root_file) as f:
        if args.tree not in f:
            raise SystemExit(f"Tree {args.tree} not found in {root_file}")
        tree = f[args.tree]
        branches = [branch_to_dict(tree, name) for name in tree.keys()]
        entries = int(tree.num_entries)

    expected_counts = {"eventID": 1, "prim": 7, "edep": 32, "nph": 32, "tfirst": 32}
    actual_counts = {
        "eventID": sum(1 for b in branches if b["name"] == "eventID"),
        "prim": sum(1 for b in branches if b["name"].startswith("prim_")),
        "edep": sum(1 for b in branches if b["name"].startswith("edep_")),
        "nph": sum(1 for b in branches if b["name"].startswith("nph_")),
        "tfirst": sum(1 for b in branches if b["name"].startswith("tfirst_")),
    }

    payload = {
        "tag": args.tag,
        "file": str(root_file),
        "tree": args.tree,
        "entries": entries,
        "n_branches": len(branches),
        "branches": branches,
        "expected_counts": expected_counts,
        "actual_counts": actual_counts,
    }

    json_path = table_dir / f"{args.tag}_tree.json"
    md_path = table_dir / f"{args.tag}_tree.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        f"# ROOT tree inspection: {args.tag}",
        "",
        f"- File: {root_file}",
        f"- Tree: {args.tree}",
        f"- Entries: {payload['entries']}",
        f"- Branches: {payload['n_branches']}",
        "",
        "## Branch summary",
        "",
        "| Name | Type | Interpretation |",
        "| --- | --- | --- |",
    ]
    for branch in branches:
        lines.append(f"| {branch['name']} | {branch['typename']} | {branch['interpretation']} |")
    lines += [
        "",
        "## Expected layout check",
        "",
        f"- eventID: {actual_counts['eventID']} / {expected_counts['eventID']}",
        f"- prim_*: {actual_counts['prim']} / {expected_counts['prim']}",
        f"- edep_*: {actual_counts['edep']} / {expected_counts['edep']}",
        f"- nph_*: {actual_counts['nph']} / {expected_counts['nph']}",
        f"- tfirst_*: {actual_counts['tfirst']} / {expected_counts['tfirst']}",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"[inspect_root_tree] wrote {json_path}")
    print(f"[inspect_root_tree] wrote {md_path}")


if __name__ == "__main__":
    main()
