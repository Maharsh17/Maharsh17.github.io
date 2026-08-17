---
title: The byte that lied
date: 2026-08-17
summary: A texture format told me it was uncompressed. It was not. Here is how the file gave itself away.
draft: false
---

This site runs on textures pulled straight out of a retail copy of GTA San
Andreas. The game keeps them in TXD archives, a RenderWare format that is a
tree of chunks, each with a type, a size, and a version. Walking the tree is
easy. Decoding what you find is where it got interesting.

Every texture header has a field called `compression`. On the first pass I
read that byte, saw zero, and wrote a decoder for raw pixel data. What came
out was noise. Not slightly wrong colors, not a flipped channel. Noise.

## Where the truth was

The real answer sits 76 bytes into the header, in a four character code:

```
44 58 54 31   ->  "DXT1"
44 58 54 33   ->  "DXT3"
```

That is the Direct3D format tag, and it is the one the game itself trusts.
The `compression` byte is a RenderWare-level hint that the SA toolchain
never bothered to keep accurate. Plenty of files in the archive have it set
to zero while holding DXT1 blocks.

Once I read the FourCC instead, 100 sprites decoded clean on the first try.

## The part worth remembering

I had two fields claiming to describe the same thing and I picked the one
with the friendlier name. The lesson is not about RenderWare. When a format
gives you two sources for the same fact, the one the runtime reads is the
one that is true. Everything else is documentation, and documentation
drifts.

The decoder is about 200 lines of pure standard library Python. No Pillow,
no bindings. DXT1 is four control bytes and 32 bits of two bit indices per
4x4 block, which sounds worse than it is.
