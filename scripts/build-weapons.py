#!/usr/bin/env python3
"""Join weapon.dat stats to the HUD sprite set and emit data/weapons.json.

Stats come from the game's own weapon.dat (via extract-gamedata.py). Sprites
come from the fan-made HUD recreation. Only weapons present in BOTH are
emitted, so every card on the page has real numbers and real art. Weapons with
no sprite (detonator, night vision, spraycan) are reported and skipped rather
than shown with a placeholder.

Usage:
    build-weapons.py <weapon.dat.json> <sprite-dir> <out.json>
"""
import json
import os
import shutil
import sys

# weaponType in weapon.dat -> sprite basename in the HUD recreation.
SPRITES = {
    # guns
    'PISTOL': 'pistol', 'PISTOL_SILENCED': 'silencedpistol',
    'DESERT_EAGLE': 'deserteagle', 'SHOTGUN': 'shotgun', 'SAWNOFF': 'sawnoff',
    'SPAS12': 'combatshotgun', 'MICRO_UZI': 'microuzi', 'MP5': 'mp5',
    'TEC9': 'tec9', 'AK47': 'ak47', 'M4': 'm4', 'COUNTRYRIFLE': 'sniper',
    'SNIPERRIFLE': 'sniper2', 'MINIGUN': 'minigun', 'RLAUNCHER': 'rpg',
    'GRENADE': 'grenade', 'TEARGAS': 'teargas', 'MOLOTOV': 'molotov',
    'SATCHEL_CHARGE': 'landmine', 'CAMERA': 'camera',
    # melee
    'UNARMED': 'fist', 'BRASSKNUCKLE': 'brassknuckles', 'GOLFCLUB': 'golfclub',
    'NIGHTSTICK': 'nitestick', 'KNIFE': 'knife', 'BASEBALLBAT': 'bat',
    'SHOVEL': 'shovel', 'POOLCUE': 'poolcue', 'KATANA': 'katana',
    'CHAINSAW': 'chainsaw', 'DILDO1': None, 'FLOWERS': None, 'CANE': 'cane',
}

LABELS = {
    'PISTOL': '9mm', 'PISTOL_SILENCED': 'Silenced 9mm',
    'DESERT_EAGLE': 'Desert Eagle', 'SHOTGUN': 'Shotgun',
    'SAWNOFF': 'Sawn-off Shotgun', 'SPAS12': 'Combat Shotgun',
    'MICRO_UZI': 'Micro SMG', 'MP5': 'SMG', 'TEC9': 'Tec-9', 'AK47': 'AK-47',
    'M4': 'M4', 'COUNTRYRIFLE': 'Rifle', 'SNIPERRIFLE': 'Sniper Rifle',
    'MINIGUN': 'Minigun', 'RLAUNCHER': 'Rocket Launcher', 'GRENADE': 'Grenade',
    'TEARGAS': 'Tear Gas', 'MOLOTOV': 'Molotov Cocktail',
    'SATCHEL_CHARGE': 'Satchel Charge', 'CAMERA': 'Camera',
    'UNARMED': 'Fists', 'BRASSKNUCKLE': 'Brass Knuckles',
    'GOLFCLUB': 'Golf Club', 'NIGHTSTICK': 'Nightstick', 'KNIFE': 'Knife',
    'BASEBALLBAT': 'Baseball Bat', 'SHOVEL': 'Shovel', 'POOLCUE': 'Pool Cue',
    'KATANA': 'Katana', 'CHAINSAW': 'Chainsaw', 'CANE': 'Cane',
}


def main(stats_path, sprite_dir, out_path):
    data = json.load(open(stats_path))
    out_dir = os.path.dirname(out_path)
    asset_dir = os.path.join(os.path.dirname(out_dir), 'assets', 'weapons')
    os.makedirs(asset_dir, exist_ok=True)

    best = {}

    def consider(row, kind):
        wt = row.get('weaponType')
        if not isinstance(wt, str):
            return
        # Guns list one row per skill level; keep the standard (1) tier, or
        # the only row for weapons that have just one.
        skill = row.get('skillLevel')
        prev = best.get(wt)
        if prev and prev['_skill'] == 1:
            return
        best[wt] = {
            '_skill': skill if isinstance(skill, int) else 0,
            'type': wt,
            'kind': kind,
            'name': LABELS.get(wt, wt.replace('_', ' ').title()),
            # Melee rows carry no damage or clip in weapon.dat. They get
            # combo count instead, which is the stat the file actually has.
            'damage': row.get('damage') if kind == 'gun' else None,
            'clip': row.get('ammoClip') if kind == 'gun' else None,
            'range': row.get('weaponRange'),
            'accuracy': row.get('accuracy') if kind == 'gun' else None,
            'combos': row.get('numCombos') if kind == 'melee' else None,
        }

    for row in data.get('guns', []):
        consider(row, 'gun')
    for row in data.get('melee', []):
        consider(row, 'melee')

    weapons, missing = [], []
    for wt, w in best.items():
        sprite = SPRITES.get(wt)
        if not sprite:
            missing.append(wt)
            continue
        src = os.path.join(sprite_dir, sprite + '.png')
        if not os.path.exists(src):
            missing.append(f"{wt} (no {sprite}.png)")
            continue
        shutil.copy2(src, os.path.join(asset_dir, sprite + '.png'))
        w.pop('_skill')
        w['sprite'] = sprite + '.png'
        weapons.append(w)

    weapons.sort(key=lambda w: (w['kind'] == 'melee', -(w['damage'] or 0), w['name']))
    json.dump({'source': 'weapon.dat', 'weapons': weapons},
              open(out_path, 'w'), indent=1)

    print(f"{len(weapons)} weapons -> {out_path}")
    print(f"sprites copied -> {asset_dir}")
    if missing:
        print(f"skipped (no sprite): {', '.join(sorted(missing))}")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
