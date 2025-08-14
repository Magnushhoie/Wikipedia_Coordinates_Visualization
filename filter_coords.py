#!/usr/bin/env python3
import csv
import sys
import argparse
import math

def parse_args():
    p = argparse.ArgumentParser(
        description="Filter a CSV to only rows that contain valid latitude/longitude and exactly 5 columns."
    )
    p.add_argument("input", help="Path to input CSV (e.g., coords.csv)")
    p.add_argument(
        "-o", "--output",
        help="Path to write filtered CSV (default: stdout)",
        default="-"
    )
    return p.parse_args()

def detect_coord_indices(row):
    lowered = [c.strip().lower() for c in row]
    lat_candidates = {"lat", "latitude", "lat_dd", "y", "y_coord", "ycoord"}
    lon_candidates = {"lon", "long", "longitude", "lng", "x", "x_coord", "xcoord"}

    try:
        lat_idx = next(i for i, v in enumerate(lowered) if v in lat_candidates)
        lon_idx = next(i for i, v in enumerate(lowered) if v in lon_candidates)
        return lat_idx, lon_idx, True
    except StopIteration:
        return 2, 3, False

def parse_float(s):
    try:
        v = float(str(s).strip())
        if not math.isfinite(v):
            return None
        return v
    except Exception:
        return None

def has_valid_coords(row, lat_idx, lon_idx):
    if max(lat_idx, lon_idx) >= len(row):
        return False
    lat = parse_float(row[lat_idx])
    lon = parse_float(row[lon_idx])
    if lat is None or lon is None:
        return False
    if not (-90.0 <= lat <= 90.0):
        return False
    if not (-180.0 <= lon <= 180.0):
        return False
    return True

def clean_semicolons(row):
    return [str(cell).replace(";", "") for cell in row]

def is_exactly_five_columns(row):
    return len(row) == 5

def main():
    args = parse_args()

    if args.input == "-":
        inf = sys.stdin
    else:
        inf = open(args.input, "r", encoding="utf-8", newline="")

    if args.output == "-":
        outf = sys.stdout
    else:
        outf = open(args.output, "w", encoding="utf-8", newline="")

    try:
        reader = csv.reader(inf, delimiter=",", quotechar='"', skipinitialspace=True)
        writer = csv.writer(outf, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)

        first = next(reader, None)
        if first is None:
            return

        first_clean = clean_semicolons(first)
        lat_idx, lon_idx, header_present = detect_coord_indices(first_clean)

        if header_present:
            if is_exactly_five_columns(first_clean):
                writer.writerow(first_clean)
        else:
            if is_exactly_five_columns(first_clean) and has_valid_coords(first_clean, lat_idx, lon_idx):
                writer.writerow(first_clean)

        for row in reader:
            clean_row = clean_semicolons(row)
            if not is_exactly_five_columns(clean_row):
                continue
            if has_valid_coords(clean_row, lat_idx, lon_idx):
                writer.writerow(clean_row)

    finally:
        if inf is not sys.stdin:
            inf.close()
        if outf is not sys.stdout:
            outf.close()

if __name__ == "__main__":
    main()
