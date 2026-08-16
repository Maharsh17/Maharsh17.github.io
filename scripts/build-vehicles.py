#!/usr/bin/env python3
"""Match each project to a real GTA San Andreas vehicle by derived stats.

The match is computed, not assigned. Two repo metrics map onto two vehicle
metrics, and we pick the nearest real vehicle in that 2D space:

    repo total bytes      -> vehicle mass          (bigger repo, heavier car)
    days since last push  -> vehicle maxVelocity   (recent work, faster car)

Both axes are normalised to percentile rank within their own population, so
the comparison is scale-free and no hand-tuned constants decide the outcome.

Vehicle display names ("Landstalker") live in american.gxt but under a hash
that is not plain CRC32 of the vehicles.ide key, so they are resolved by
prefix-matching the model name instead. Match rate is reported.

Usage:
    build-vehicles.py <handling.cfg.json> <vehicles.ide.json> <gxt.json> \
                      <projects.json> <overrides.json> <out.json>
"""
import json
import sys
from datetime import date


def rank(values):
    """Percentile rank 0..1 for each value, ties share a rank."""
    order = sorted(set(values))
    if len(order) < 2:
        return {v: 0.5 for v in values}
    return {v: order.index(v) / (len(order) - 1) for v in values}


def resolve_names(vehicles, gxt):
    """Map model name -> display name by prefix match against GXT strings."""
    pool = set()
    for table in gxt.values():
        for s in table.values():
            if isinstance(s, str) and 2 < len(s) < 24 and s[:1].isupper():
                pool.add(s)

    by_lower = {}
    for s in pool:
        by_lower.setdefault(s.lower(), s)

    names, hits = {}, 0
    for v in vehicles:
        model = str(v.get('modelName', '')).lower()
        if not model:
            continue
        best = None
        for low, orig in by_lower.items():
            if low.startswith(model) and (best is None or len(low) < len(best[0])):
                best = (low, orig)
        if best:
            names[model] = best[1]
            hits += 1
        else:
            names[model] = model.title()
    return names, hits


def main(handling_p, vehicles_p, gxt_p, projects_p, overrides_p, out_p):
    handling = json.load(open(handling_p))
    vehicles = json.load(open(vehicles_p)).get('cars', [])
    gxt = json.load(open(gxt_p))
    projects = json.load(open(projects_p))
    overrides = json.load(open(overrides_p))

    names, hits = resolve_names(vehicles, gxt)
    handling_to_model = {}
    for v in vehicles:
        hid = str(v.get('handlingId', '')).upper()
        if hid:
            handling_to_model.setdefault(hid, str(v.get('modelName', '')).lower())

    # Only vehicles that are actually cars in vehicles.ide, with usable stats.
    pool = []
    for h in handling:
        hid = str(h.get('identifier', '')).upper()
        model = handling_to_model.get(hid)
        mass, vel = h.get('mass'), h.get('maxVelocity')
        if not model or not isinstance(mass, (int, float)) or not isinstance(vel, (int, float)):
            continue
        pool.append({'id': hid, 'model': model, 'name': names.get(model, model.title()),
                     'mass': float(mass), 'speed': float(vel),
                     'value': h.get('monetaryValue')})
    if not pool:
        sys.exit("no vehicles with usable stats")

    mass_rank = rank([v['mass'] for v in pool])
    speed_rank = rank([v['speed'] for v in pool])

    # Repo metrics.
    repos = projects.get('repos', [])
    sizes, ages = {}, {}
    today = date.today()
    for r in repos:
        n = r['nameWithOwner']
        sizes[n] = sum(l.get('size', 0) for l in r.get('languages', []))
        try:
            y, m, d = (int(x) for x in r['pushedAt'].split('-'))
            ages[n] = (today - date(y, m, d)).days
        except Exception:
            ages[n] = 9999

    size_rank = rank(list(sizes.values()))
    age_rank = rank(list(ages.values()))

    out = {}
    for key, o in overrides.items():
        if key not in sizes:
            continue
        want_mass = size_rank[sizes[key]]
        want_speed = 1.0 - age_rank[ages[key]]      # recent push -> fast
        best, best_d = None, None
        for v in pool:
            dm = mass_rank[v['mass']] - want_mass
            ds = speed_rank[v['speed']] - want_speed
            d = dm * dm + ds * ds
            if best_d is None or d < best_d:
                best, best_d = v, d
        out[key] = {
            'vehicle': best['name'],
            'mass': best['mass'],
            'topSpeed': best['speed'],
            'value': best['value'],
            'why': f"{sizes[key] // 1024}KB of code, last pushed {ages[key]} days ago",
        }

    json.dump({'source': 'handling.cfg + vehicles.ide', 'garage': out},
              open(out_p, 'w'), indent=1)
    print(f"{len(out)} projects matched from a pool of {len(pool)} vehicles")
    print(f"display names resolved from GXT: {hits}/{len(names)}")
    for k, v in out.items():
        print(f"  {k.split('/')[-1]:<26} -> {v['vehicle']:<16} "
              f"{v['topSpeed']:.0f} top speed, {v['mass']:.0f}kg")


if __name__ == '__main__':
    if len(sys.argv) != 7:
        sys.exit(__doc__)
    main(*sys.argv[1:])
