#!/usr/bin/env python3
"""Create evidence crop anchors from product photos using macOS sips.

Usage:
  create_image_evidence_anchors.py input.jpg --out-dir anchors
  create_image_evidence_anchors.py input.jpg --out-dir anchors \
    --crop material=0.35,0.42,0.22,0.18 --crop edge=0.45,0.37,0.18,0.12

Crop format is name=x,y,w,h using relative coordinates from 0 to 1.
The script also creates a 3x3 grid to help agents find feature regions.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)


def image_size(path: Path) -> tuple[int, int]:
    output = run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)])
    width_match = re.search(r"pixelWidth:\s*(\d+)", output)
    height_match = re.search(r"pixelHeight:\s*(\d+)", output)
    if not width_match or not height_match:
        raise RuntimeError(f"Unable to read image size from sips output:\n{output}")
    return int(width_match.group(1)), int(height_match.group(1))


def crop_with_sips(src: Path, dst: Path, left: int, top: int, width: int, height: int) -> None:
    tmp = dst.with_suffix(".tmp" + dst.suffix)
    shutil.copyfile(src, tmp)
    run(["sips", "--cropOffset", str(top), str(left), "-c", str(height), str(width), str(tmp), "--out", str(dst)])
    if tmp.exists():
        tmp.unlink()


def parse_crop(spec: str) -> tuple[str, tuple[float, float, float, float]]:
    if "=" not in spec:
        raise ValueError("crop must be name=x,y,w,h")
    name, values = spec.split("=", 1)
    parts = [float(part.strip()) for part in values.split(",")]
    if len(parts) != 4:
        raise ValueError("crop must have four values: x,y,w,h")
    if not name or not re.match(r"^[a-zA-Z0-9_-]+$", name):
        raise ValueError("crop name must contain only letters, digits, underscore, hyphen")
    if any(part < 0 or part > 1 for part in parts):
        raise ValueError("crop coordinates must be relative values from 0 to 1")
    return name, (parts[0], parts[1], parts[2], parts[3])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--crop", action="append", default=[], help="name=x,y,w,h relative crop")
    args = parser.parse_args()

    if not shutil.which("sips"):
        print("sips is required on macOS", file=sys.stderr)
        return 2
    if not args.image.exists():
        print(f"image not found: {args.image}", file=sys.stderr)
        return 2
    try:
        crop_specs = [parse_crop(spec) for spec in args.crop]
    except ValueError as exc:
        print(f"invalid --crop: {exc}", file=sys.stderr)
        return 2

    args.out_dir.mkdir(parents=True, exist_ok=True)
    width, height = image_size(args.image)
    manifest = {"source": str(args.image), "width": width, "height": height, "anchors": []}

    grid_dir = args.out_dir / "grid"
    grid_dir.mkdir(exist_ok=True)
    for row in range(3):
        for col in range(3):
            left = int(width * col / 3)
            top = int(height * row / 3)
            crop_width = int(width / 3)
            crop_height = int(height / 3)
            name = f"grid_r{row + 1}c{col + 1}"
            dst = grid_dir / f"{name}{args.image.suffix.lower()}"
            crop_with_sips(args.image, dst, left, top, crop_width, crop_height)
            manifest["anchors"].append({"name": name, "path": str(dst), "role": "grid", "relative_box": [col / 3, row / 3, 1 / 3, 1 / 3]})

    for name, (x, y, w, h) in crop_specs:
        left = max(0, min(width - 1, int(width * x)))
        top = max(0, min(height - 1, int(height * y)))
        crop_width = max(1, min(width - left, int(width * w)))
        crop_height = max(1, min(height - top, int(height * h)))
        dst = args.out_dir / f"{name}{args.image.suffix.lower()}"
        crop_with_sips(args.image, dst, left, top, crop_width, crop_height)
        manifest["anchors"].append({"name": name, "path": str(dst), "role": "feature", "relative_box": [x, y, w, h]})

    manifest_path = args.out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

