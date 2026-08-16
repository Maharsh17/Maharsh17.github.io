#!/usr/bin/env python3
"""Convert GTA San Andreas plain-text game data into JSON.

Pure stdlib. Handles three shapes found in data/:

  .ide  sectioned item definitions   (objs, tobj, cars, peds, weap, ...)
  .ipl  sectioned item placement     (inst, cull, zone, path, ...)
  .dat  flat or ad-hoc tables        (handling.cfg, weapon.dat, ...)

Files with a known column layout get named fields. Everything else is emitted
as positional arrays, which is still far more usable than the raw text.

Usage:
    extract-gamedata.py <data-dir> <out-dir>
"""
import json
import os
import sys

# Named columns for the files worth reading by hand. Trailing columns beyond a
# schema are kept under "extra" rather than dropped.
SCHEMAS = {
    'handling.cfg': [
        'identifier', 'mass', 'turnMass', 'dragMult', 'comX', 'comY', 'comZ',
        'percentSubmerged', 'tractionMultiplier', 'tractionLoss', 'tractionBias',
        'numberOfGears', 'maxVelocity', 'engineAcceleration', 'engineInertia',
        'driveType', 'engineType', 'brakeDeceleration', 'brakeBias', 'abs',
        'steeringLock', 'suspensionForceLevel', 'suspensionDampingLevel',
        # These five were missing in the first pass, which shifted every
        # column after them. The tell was monetaryValue reading -0.14 for a
        # Landstalker; with them present it reads 25000, a plausible price.
        'suspensionHighSpdComDamp', 'suspensionUpperLimit',
        'suspensionLowerLimit', 'suspensionBiasBetweenFrontAndRear',
        'suspensionAntiDiveMultiplier',
        'seatOffsetDistance', 'collisionDamageMultiplier', 'monetaryValue',
        'modelFlags', 'handlingFlags', 'frontLights', 'rearLights', 'animGroup',
    ],
    'weapon.dat': [
        'weaponType', 'fireType', 'targetRange', 'weaponRange', 'modelId1',
        'modelId2', 'weaponSlot', 'animGroup', 'ammoClip', 'damage',
        'fireOffsetX', 'fireOffsetY', 'fireOffsetZ', 'skillLevel',
        'reqStatLevel', 'accuracy', 'moveSpeed',
    ],
}

# Melee rows do NOT share the gun layout. Per weapon.dat's own header:
#   A weaponType, B fireType, C/D ranges, E/F modelIds, I slot,
#   J baseCombo, K numCombos, L flags, M stealthAnimGroup
# There is no damage column. An earlier version reused the gun schema here and
# surfaced numCombos as "damage", which read as every melee weapon doing 1.
MELEE_COLS = [
    'weaponType', 'fireType', 'targetRange', 'weaponRange', 'modelId1',
    'modelId2', 'weaponSlot', 'baseCombo', 'numCombos', 'flags',
    'stealthAnimGroup',
]

IDE_SECTIONS = {
    'objs': ['id', 'modelName', 'txdName', 'drawDistance', 'flags'],
    'tobj': ['id', 'modelName', 'txdName', 'drawDistance', 'flags', 'timeOn', 'timeOff'],
    'cars': ['id', 'modelName', 'txdName', 'type', 'handlingId', 'gameName',
             'anims', 'class', 'frequency', 'flags', 'comprules'],
    'peds': ['id', 'modelName', 'txdName', 'defaultPedType', 'behaviour',
             'animGroup', 'canDriveMask', 'flags', 'animFile', 'radio1', 'radio2'],
    'weap': ['id', 'modelName', 'txdName', 'animName', 'meshCount', 'drawDistance'],
    'hier': ['id', 'modelName', 'txdName'],
    'anim': ['id', 'modelName', 'txdName', 'animName', 'drawDistance', 'flags'],
}

IPL_SECTIONS = {
    'inst': ['id', 'modelName', 'interior', 'posX', 'posY', 'posZ',
             'rotX', 'rotY', 'rotZ', 'rotW', 'lod'],
    'zone': ['name', 'type', 'x1', 'y1', 'z1', 'x2', 'y2', 'z2', 'island', 'label'],
}

SECTION_KEYWORDS = set(IDE_SECTIONS) | set(IPL_SECTIONS) | {
    'end', '2dfx', 'txdp', 'path', 'cull', 'grge', 'enex', 'pick', 'jump',
    'tcyc', 'auzo', 'mult', 'carsgen', 'occl', 'lodm', 'trwt',
}


def clean(text):
    for raw in text.replace('\r', '').split('\n'):
        line = raw.split('#')[0].strip()
        if line.startswith(';') or line.startswith('//'):
            continue
        if line:
            yield line


def split_fields(line):
    if ',' in line:
        return [f.strip() for f in line.split(',')]
    return line.split()


def coerce(v):
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        return v


def parse_sectioned(text, schemas):
    out = {}
    section = None
    for line in clean(text):
        low = line.lower()
        if low in SECTION_KEYWORDS:
            section = None if low == 'end' else low
            if section:
                out.setdefault(section, [])
            continue
        if section is None:
            continue
        fields = [coerce(f) for f in split_fields(line)]
        cols = schemas.get(section)
        if cols:
            row = dict(zip(cols, fields))
            if len(fields) > len(cols):
                row['extra'] = fields[len(cols):]
            out[section].append(row)
        else:
            out[section].append(fields)
    return out


def _row(fields, cols):
    if not cols:
        return fields
    row = dict(zip(cols, fields))
    if len(fields) > len(cols):
        row['extra'] = fields[len(cols):]
    return row


def parse_weapon_dat(text):
    """weapon.dat carries three record types with different layouts.

    '$' gun data, '£' melee data, '%' per-weapon skill timings. Feeding all
    three through one schema silently produces misaligned garbage, so they are
    split apart here and keyed separately.
    """
    out = {'guns': [], 'melee': [], 'skills': []}
    for line in clean(text):
        prefix, rest = line[0], line[1:].strip()
        if prefix not in '$£%':
            continue
        fields = [coerce(f) for f in split_fields(rest)]
        if len(fields) < 2:
            continue
        if prefix == '$':
            out['guns'].append(_row(fields, SCHEMAS['weapon.dat']))
        elif prefix == '£':
            out['melee'].append(_row(fields, MELEE_COLS))
        else:
            out['skills'].append(fields)
    return out


def parse_flat(text, name):
    if name == 'weapon.dat':
        return parse_weapon_dat(text)
    cols = SCHEMAS.get(name)
    rows = []
    for line in clean(text):
        if line.startswith('$'):
            line = line[1:].strip()
        fields = [coerce(f) for f in split_fields(line)]
        if len(fields) < 2:
            continue
        rows.append(_row(fields, cols))
    return rows


def main(src, dst):
    os.makedirs(dst, exist_ok=True)
    summary = []

    targets = []
    for root, _dirs, files in os.walk(src):
        for f in files:
            if f.lower().endswith(('.ide', '.ipl', '.dat', '.cfg')):
                targets.append(os.path.join(root, f))

    for path in sorted(targets):
        rel = os.path.relpath(path, src)
        name = os.path.basename(path).lower()
        try:
            text = open(path, encoding='latin-1').read()
        except OSError:
            continue

        if name.endswith('.ide'):
            data = parse_sectioned(text, IDE_SECTIONS)
            count = sum(len(v) for v in data.values())
        elif name.endswith('.ipl'):
            data = parse_sectioned(text, IPL_SECTIONS)
            count = sum(len(v) for v in data.values())
        else:
            data = parse_flat(text, name)
            count = sum(len(v) for v in data.values()) if isinstance(data, dict) else len(data)

        if not count:
            continue

        out = os.path.join(dst, rel.replace(os.sep, '__') + '.json')
        json.dump(data, open(out, 'w'), indent=1)
        summary.append((rel, count))

    total = sum(c for _, c in summary)
    print(f"{len(summary)} files, {total} rows -> {dst}")
    for rel, c in sorted(summary, key=lambda x: -x[1])[:15]:
        print(f"  {c:>7}  {rel}")
    return summary


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
