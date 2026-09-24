#!/usr/bin/env python3
"""Sample an author-hosted GLB mesh into the deck's lightweight cloud format."""
import argparse
import json
import math
from pathlib import Path
import struct

from PIL import Image


COMPONENTS = {
    5120: ("b", 1),
    5121: ("B", 1),
    5122: ("h", 2),
    5123: ("H", 2),
    5125: ("I", 4),
    5126: ("f", 4),
}
WIDTHS = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def read_glb(path):
    raw = path.read_bytes()
    magic, version, length = struct.unpack_from("<III", raw, 0)
    if magic != 0x46546C67 or version != 2 or length != len(raw):
        raise ValueError(f"Unsupported GLB header: {path}")
    document = binary = None
    offset = 12
    while offset < len(raw):
        size, kind = struct.unpack_from("<II", raw, offset)
        offset += 8
        chunk = raw[offset:offset + size]
        offset += size
        if kind == 0x4E4F534A:
            document = json.loads(chunk)
        elif kind == 0x004E4942:
            binary = chunk
    if document is None or binary is None:
        raise ValueError(f"Missing JSON or binary chunk: {path}")
    return document, binary


def accessor_values(document, binary, index):
    accessor = document["accessors"][index]
    view = document["bufferViews"][accessor["bufferView"]]
    code, size = COMPONENTS[accessor["componentType"]]
    width = WIDTHS[accessor["type"]]
    stride = view.get("byteStride", size * width)
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    values = []
    for item in range(accessor["count"]):
        values.append(struct.unpack_from("<" + code * width, binary, start + item * stride))
    return values


def sample_cloud(glb_path, image_path, maximum):
    document, binary = read_glb(glb_path)
    primitive = document["meshes"][0]["primitives"][0]
    points = accessor_values(document, binary, primitive["attributes"]["POSITION"])
    uvs = accessor_values(document, binary, primitive["attributes"]["TEXCOORD_0"])
    if len(points) != len(uvs):
        raise ValueError("Positions and texture coordinates do not match")
    step = max(1, math.ceil(len(points) / maximum))
    texture = Image.open(image_path).convert("RGB")
    sampled_points, colors = [], []
    for point, uv in zip(points[::step], uvs[::step]):
        x = min(texture.width - 1, max(0, round(float(uv[0]) * (texture.width - 1))))
        y = min(texture.height - 1, max(0, round((1.0 - float(uv[1])) * (texture.height - 1))))
        sampled_points.append([round(float(value), 6) for value in point])
        colors.append(list(texture.getpixel((x, y))))
    return sampled_points, colors, step


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("glb", type=Path)
    parser.add_argument("image", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--maximum", type=int, default=18000)
    args = parser.parse_args()
    points, colors, step = sample_cloud(args.glb, args.image, args.maximum)
    payload = {
        "kind": "cloud",
        "points": points,
        "colors": colors,
        "source_url": args.source_url,
        "sampling": f"Every {step}th decoded vertex, capped at {args.maximum}",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, separators=(",", ":")))
    print(f"Wrote {len(points):,} points to {args.output}")


if __name__ == "__main__":
    main()
