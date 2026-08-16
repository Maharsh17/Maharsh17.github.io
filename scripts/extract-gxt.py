#!/usr/bin/env python3
"""Dump a GTA San Andreas .gxt into JSON.

Pure stdlib. SA GXT layout:
    u32 version(4) + u16 charBits(8)
    'TABL' u32 size, then N x (char name[8], u32 offset)
    each table: ['TKEY' u32 size, N x (u32 dataOffset, u32 crcKey)]
                ['TDAT' u32 size, null-terminated strings]

Keys are CRC32 hashes of the original key name, so names are not recoverable.
Values are what matter for reference: exact in-game wording.

Usage:
    extract-gxt.py <american.gxt> <out.json>
"""
import json
import struct
import sys


def parse(path):
    b = open(path, 'rb').read()
    off = 4 if b[4:8] == b'TABL' else 0
    _tag, size = struct.unpack_from('<4sI', b, off)

    tables = []
    p = off + 8
    for _ in range(size // 12):
        name = b[p:p + 8].split(b'\0')[0].decode('latin-1')
        tables.append((name, struct.unpack_from('<I', b, p + 8)[0]))
        p += 12

    result = {}
    for name, toff in tables:
        q = toff
        # Non-MAIN tables repeat their 8-byte name before TKEY.
        if b[q:q + 4] != b'TKEY':
            q += 8
        tag, ksz = struct.unpack_from('<4sI', b, q)
        if tag != b'TKEY':
            continue
        entries = []
        for i in range(ksz // 8):
            doff, crc = struct.unpack_from('<II', b, q + 8 + i * 8)
            entries.append((crc, doff))
        q += 8 + ksz
        dtag, _dsz = struct.unpack_from('<4sI', b, q)
        if dtag != b'TDAT':
            continue
        dat = q + 8
        strings = {}
        for crc, doff in entries:
            s = b[dat + doff:].split(b'\0')[0].decode('latin-1', 'replace')
            strings[f"{crc:08X}"] = s
        result[name] = strings
    return result


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    data = parse(sys.argv[1])
    json.dump(data, open(sys.argv[2], 'w'), indent=1, ensure_ascii=False)
    total = sum(len(v) for v in data.values())
    print(f"{len(data)} tables, {total} strings -> {sys.argv[2]}")
