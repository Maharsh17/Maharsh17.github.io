#!/usr/bin/env python3
"""Decrypt a GTA San Andreas audio stream into Ogg Vorbis.

Pure stdlib. SA stream files are Ogg Vorbis XOR'd with a fixed 16-byte
rotating key, behind an 8064-byte track table.

Only meaningful for a copy of the game you own. See the licensing note in
combined-gta/assets/game/README.md before putting any of this on a website:
the radio-station streams are third-party licensed recordings, which is a
different question from Rockstar's own UI art.

Usage:
    extract-stream.py <stream-file> <out.ogg>
"""
import struct
import sys

KEY = bytes([0xEA, 0x3A, 0xC4, 0xA1, 0x9A, 0xA8, 0x14, 0xF3,
             0x48, 0xB0, 0xD7, 0x27, 0x9D, 0x3A, 0xEB, 0xC0])


def decrypt(data):
    return bytes(data[i] ^ KEY[i % 16] for i in range(len(data)))


def ogg_duration(buf):
    """Seconds, from the last Ogg page's granule position over the sample rate."""
    head = buf.find(b'\x01vorbis')
    if head < 0:
        return None
    rate = struct.unpack_from('<I', buf, head + 12)[0]
    last = buf.rfind(b'OggS')
    if last < 0 or not rate:
        return None
    granule = struct.unpack_from('<Q', buf, last + 6)[0]
    return granule / rate


def main(src, dst):
    raw = open(src, 'rb').read()
    dec = decrypt(raw)

    start = dec.find(b'OggS')
    if start < 0:
        sys.exit("no Ogg stream found; wrong key or not a stream file")

    ogg = dec[start:]
    open(dst, 'wb').write(ogg)

    secs = ogg_duration(ogg)
    mins = f"{int(secs // 60)}:{int(secs % 60):02d}" if secs else "unknown"
    print(f"{dst}  {len(ogg) // 1024}KB  duration {mins}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
