#!/usr/bin/env python3
"""Extract named textures from a RenderWare TXD into PNG.

Pure stdlib: struct for parsing, zlib for PNG deflate. No Pillow, no
RenderWare tooling, nothing Windows-only.

Handles DXT1 and DXT3, which is everything in fronten*.txd and hud.txd.

Usage:
    extract-txd.py <file.txd> <outdir> [name ...]

Textures extracted here come from a retail GTA San Andreas install and are
Rockstar's copyrighted assets. They land in assets/game/ so their provenance
stays obvious and they are trivial to remove.
"""
import struct
import sys
import zlib
import os


def chunks(buf, off, end):
    while off + 12 <= end:
        t, sz, _ver = struct.unpack_from('<III', buf, off)
        yield t, off + 12, sz
        off += 12 + sz


def rgb565(v):
    r = (v >> 11) & 0x1F
    g = (v >> 5) & 0x3F
    b = v & 0x1F
    return (r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2)


def decode_dxt(data, w, h, fmt):
    """Decode DXT1/DXT3 into an RGBA bytearray."""
    out = bytearray(w * h * 4)
    blocks_x = (w + 3) // 4
    blocks_y = (h + 3) // 4
    stride = 8 if fmt == 'DXT1' else 16
    pos = 0

    for by in range(blocks_y):
        for bx in range(blocks_x):
            alpha = None
            if fmt == 'DXT3':
                alpha = data[pos:pos + 8]
                pos += 8
            c0, c1, bits = struct.unpack_from('<HHI', data, pos)
            pos += 8

            r0, g0, b0 = rgb565(c0)
            r1, g1, b1 = rgb565(c1)
            palette = [(r0, g0, b0, 255), (r1, g1, b1, 255)]
            if c0 > c1 or fmt == 'DXT3':
                palette.append(((2 * r0 + r1) // 3, (2 * g0 + g1) // 3,
                                (2 * b0 + b1) // 3, 255))
                palette.append(((r0 + 2 * r1) // 3, (g0 + 2 * g1) // 3,
                                (b0 + 2 * b1) // 3, 255))
            else:
                palette.append(((r0 + r1) // 2, (g0 + g1) // 2,
                                (b0 + b1) // 2, 255))
                palette.append((0, 0, 0, 0))

            for py in range(4):
                for px in range(4):
                    x, y = bx * 4 + px, by * 4 + py
                    if x >= w or y >= h:
                        continue
                    idx = (bits >> (2 * (py * 4 + px))) & 0x3
                    r, g, b, a = palette[idx]
                    if alpha is not None:
                        nib = alpha[(py * 4 + px) // 2]
                        a = (nib & 0x0F) if (px % 2 == 0) else (nib >> 4)
                        a = a * 17  # 4-bit to 8-bit
                    o = (y * w + x) * 4
                    out[o] = r
                    out[o + 1] = g
                    out[o + 2] = b
                    out[o + 3] = a
    return out


def write_png(path, w, h, rgba):
    """Minimal RGBA PNG writer."""
    raw = bytearray()
    for y in range(h):
        raw.append(0)  # filter: none
        raw += rgba[y * w * 4:(y + 1) * w * 4]

    def chunk(tag, data):
        c = tag + data
        return struct.pack('>I', len(data)) + c + struct.pack('>I', zlib.crc32(c) & 0xFFFFFFFF)

    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    open(path, 'wb').write(png)


def extract(txd_path, outdir, wanted):
    buf = open(txd_path, 'rb').read()
    t, off, sz = next(chunks(buf, 0, len(buf)))
    if t != 0x16:
        sys.exit(f"{txd_path}: not a texture dictionary")

    os.makedirs(outdir, exist_ok=True)
    found = []
    for ct, coff, csz in chunks(buf, off, off + sz):
        if ct != 0x15:
            continue
        _st, soff, _ssz = next(chunks(buf, coff, coff + csz))
        name = buf[soff + 8:soff + 40].split(b'\0')[0].decode('latin-1')
        if wanted and name not in wanted:
            continue

        fourcc = buf[soff + 76:soff + 80].decode('latin-1').strip('\0')
        w, h = struct.unpack_from('<HH', buf, soff + 80)
        if fourcc not in ('DXT1', 'DXT3'):
            print(f"  skip {name}: unsupported format {fourcc!r}")
            continue

        data_size = struct.unpack_from('<I', buf, soff + 88)[0]
        data = buf[soff + 92:soff + 92 + data_size]
        rgba = decode_dxt(data, w, h, fourcc)
        out = os.path.join(outdir, f"{name}.png")
        write_png(out, w, h, rgba)
        print(f"  {name}.png  {w}x{h}  {fourcc}  {os.path.getsize(out)//1024}KB")
        found.append(name)

    missing = sorted(set(wanted) - set(found)) if wanted else []
    if missing:
        sys.exit(f"NOT FOUND in {txd_path}: {', '.join(missing)}")
    return found


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    extract(sys.argv[1], sys.argv[2], set(sys.argv[3:]))
