#!/usr/bin/env python3
import csv
import json
import random
import re
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

XLSX = Path("/N/scratch/ssomalra/BMEG_project/Data_Final.xlsx")
OUTDIR = Path("/N/scratch/ssomalra/BMEG_project/splits")
TRAIN_RATIO = 0.7
SEED = 42

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

def cell_ref_to_index(ref):
    m = re.fullmatch(r"([A-Z]+)(\d+)", ref)
    letters, row = m.groups()
    col = 0
    for ch in letters:
        col = col * 26 + (ord(ch) - ord("A") + 1)
    return col - 1, int(row) - 1

def load_shared_strings(zf):
    try:
        root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    strings = []
    for si in root.findall("m:si", NS):
        parts = []
        t = si.find("m:t", NS)
        if t is not None and t.text:
            parts.append(t.text)
        else:
            for run in si.findall("m:r", NS):
                tt = run.find("m:t", NS)
                if tt is not None and tt.text:
                    parts.append(tt.text)
        strings.append("".join(parts))
    return strings

def read_sheet(xlsx_path):
    with zipfile.ZipFile(xlsx_path) as zf:
        shared = load_shared_strings(zf)
        sheet = ET.fromstring(zf.read("xl/worksheets/sheet1.xml"))

    rows = {}
    for row in sheet.findall(".//m:sheetData/m:row", NS):
        r_idx = int(row.attrib["r"]) - 1
        for cell in row.findall("m:c", NS):
            c_idx, _ = cell_ref_to_index(cell.attrib["r"])
            v = cell.find("m:v", NS)
            text = ""
            if v is not None and v.text is not None:
                text = shared[int(v.text)] if cell.attrib.get("t") == "s" else v.text
            rows.setdefault(r_idx, {})[c_idx] = text

    max_row = max(rows)
    max_col = max(max(cols) for cols in rows.values())
    grid = []
    for r in range(max_row + 1):
        grid.append([rows.get(r, {}).get(c, "") for c in range(max_col + 1)])
    return grid

def extract_subject_groups(grid):
    header = grid[0]
    subject_idx = header.index("Subject")
    group_idx = header.index("Group")  # left-most Group column
    subject_to_group = {}
    for row in grid[1:]:
        if subject_idx >= len(row) or group_idx >= len(row):
            continue
        subject = row[subject_idx].strip()
        group = row[group_idx].strip()
        if not subject or not group or group == "Total":
            continue
        subject_to_group[subject] = group
    return subject_to_group

def stratified_split(subject_to_group, train_ratio, seed):
    rng = random.Random(seed)
    grouped = defaultdict(list)
    for subject, group in subject_to_group.items():
        grouped[group].append(subject)

    train, test = [], []
    test_ratio = 1 - train_ratio

    for group in sorted(grouped):
        subjects = sorted(grouped[group])
        rng.shuffle(subjects)
        n_test = round(len(subjects) * test_ratio)
        if len(subjects) > 1:
            n_test = max(1, min(len(subjects) - 1, n_test))
        else:
            n_test = 0

        test_subjects = set(subjects[:n_test])
        for subject in subjects:
            row = (subject, group)
            if subject in test_subjects:
                test.append(row)
            else:
                train.append(row)

    return sorted(train), sorted(test)

def write_txt(path, rows):
    with open(path, "w") as f:
        for subject, _ in rows:
            f.write(subject + "\n")

def write_csv(path, rows, split_name):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["subject", "group", "split"])
        for subject, group in rows:
            w.writerow([subject, group, split_name])

grid = read_sheet(XLSX)
subject_to_group = extract_subject_groups(grid)
train, test = stratified_split(subject_to_group, TRAIN_RATIO, SEED)

OUTDIR.mkdir(parents=True, exist_ok=True)
write_txt(OUTDIR / "train_subjects.txt", train)
write_txt(OUTDIR / "test_subjects.txt", test)
write_csv(OUTDIR / "train_subjects.csv", train, "train")
write_csv(OUTDIR / "test_subjects.csv", test, "test")

summary = {
    "total_subjects": len(subject_to_group),
    "train_subjects": len(train),
    "test_subjects": len(test),
    "subject_counts_by_group": dict(Counter(subject_to_group.values())),
    "train_counts_by_group": dict(Counter(g for _, g in train)),
    "test_counts_by_group": dict(Counter(g for _, g in test)),
    "seed": SEED,
    "train_ratio": TRAIN_RATIO,
}
with open(OUTDIR / "split_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(json.dumps(summary, indent=2))
