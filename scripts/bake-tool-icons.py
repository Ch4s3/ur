"""Bake shaded orthographic thumbnails of Ur's voxel models."""
from argparse import ArgumentParser
from pathlib import Path
from itertools import product
import re
import textwrap

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 48, 32
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
PALETTE = [
    (77, 98, 108), (158, 169, 169), (222, 231, 213), (65, 151, 165),
    (239, 188, 94), (111, 162, 101), (63, 111, 159), (195, 103, 78),
    (130, 102, 76), (57, 76, 91), (173, 207, 120), (119, 212, 206),
]
STONE, SLATE, WHITE, TEAL, GOLD, GREEN, BLUE, RED, SOIL, DARK, LIME, CYAN = range(len(PALETTE))
MATERIALS = [GREEN, SOIL, SLATE, TEAL, STONE, GOLD, RED, TEAL, WHITE, BLUE,
             GOLD, LIME, BLUE, SOIL, GREEN, GOLD, GOLD, SLATE, RED, DARK,
             CYAN, GREEN, LIME, SLATE, WHITE, GREEN]
WORSHIP = dict(shrine=37, temple=38, large_temple=39, grand_temple=40, seminary=41)


def model(*boxes):
    voxels = {}
    for x, y, z, w, h, d, colour in boxes:
        for point in product(range(x, x + w), range(y, y + h), range(z, z + d)):
            voxels[point] = colour
    return voxels


def facilities(names):
    # Read literal pieces from the same facility definitions the scene uses.
    source = (ROOT / "lib/ur/landscape.march").read_text()
    body = source.split("pfn facility(", 1)[1].split("pfn frontage(", 1)[0]
    variants = dict(re.findall(r"^      (\d+) ->\s*\n(.*?)(?=^      (?:\d+|_) ->)", body, re.M | re.S))
    result = {}
    for name, kind in names.items():
        boxes = []
        for piece in re.findall(r"A\.piece\(([0-9, ]+)\)", variants[str(kind)]):
            x, y, z, w, h, d, colour = map(int, piece.split(", "))
            boxes.append((x, y, z, w, h, d, MATERIALS[colour]))
        if not boxes:
            raise ValueError(f"Missing voxel geometry for {name}")
        result[name] = model((2, 0, 2, 28, 1, 28, STONE), *boxes)
    return result


def building(roof, floors):
    height = floors * 3 + 1
    return model((1, 0, 1, 12, 1, 11, GREEN),
                 (3, 1, 3, 8, height, 7, WHITE),
                 (2, height + 1, 2, 10, 1, 9, roof),
                 (3, height + 2, 3, 8, 1, 7, roof),
                 (5, 1, 10, 2, 2, 1, DARK),
                 *((x, y, 10, 1, 1, 1, BLUE)
                   for x, y in product((4, 8, 9), range(3, height + 1, 3))),
                 *((11, y, z, 1, 1, 1, BLUE)
                   for y, z in product(range(3, height + 1, 3), (4, 7, 8))))


def vehicle(colour, length):
    return model((1, 1, 2, length, 2, 5, colour), (2, 3, 2, length - 2, 2, 5, WHITE),
                 (2, 3, 7, length - 2, 1, 1, BLUE), (1, 3, 3, 1, 1, 3, BLUE),
                 (2, 0, 2, 2, 2, 1, DARK), (length - 2, 0, 2, 2, 2, 1, DARK),
                 (2, 0, 6, 2, 2, 1, DARK), (length - 2, 0, 6, 2, 2, 1, DARK))


def models():
    road = [(0, 0, 0, 10, 1, 14, SLATE), (1, 1, 0, 8, 1, 14, DARK),
            *((4, 2, z, 1, 1, 2, GOLD) for z in (1, 6, 11))]
    plant = [(0, 0, 0, 13, 1, 12, STONE), (1, 1, 2, 8, 5, 8, WHITE),
             (0, 6, 1, 10, 1, 10, TEAL), (10, 1, 7, 2, 12, 2, RED),
             (9, 12, 6, 4, 1, 4, SLATE), (2, 3, 10, 6, 2, 1, BLUE)]
    return {
        **facilities(dict(well=3, desal=4, rain=8, recycle=10, outfall=11, wind=12,
                          solar=13, nuclear=14, biogas=15, waste=17, school=18,
                          clinic=19, fire=20, police=21, **WORSHIP)),
        "road": model(*road),
        "overpass": model((1, 0, 3, 12, 1, 7, DARK), (5, 1, 5, 3, 5, 3, STONE),
                          (3, 6, 0, 7, 2, 14, SLATE), (6, 8, 0, 1, 1, 14, GOLD)),
        "underpass": model((0, 3, 4, 13, 2, 5, SLATE), (3, 0, 0, 7, 1, 14, DARK),
                           (2, 1, 0, 1, 3, 14, STONE), (10, 1, 0, 1, 3, 14, STONE)),
        "road_tunnel": model(*road, (0, 2, 0, 2, 6, 5, STONE), (8, 2, 0, 2, 6, 5, STONE),
                             (0, 8, 0, 10, 2, 5, GREEN), (2, 7, 4, 6, 1, 1, GOLD)),
        "shade_tree": model((0, 0, 0, 8, 2, 8, STONE), (3, 2, 3, 2, 6, 2, GOLD),
                            (0, 6, 0, 8, 4, 8, GREEN), (1, 10, 1, 6, 3, 6, GREEN)),
        "blossom_tree": model((0, 0, 0, 8, 2, 8, STONE), (3, 2, 3, 2, 6, 2, GOLD),
                              (0, 6, 0, 8, 4, 8, RED), (1, 10, 1, 6, 3, 6, WHITE)),
        "columnar_tree": model((0, 0, 0, 8, 2, 8, STONE), (3, 2, 3, 2, 6, 2, GOLD),
                               (1, 5, 1, 6, 8, 6, GREEN), (2, 13, 2, 4, 4, 4, GREEN)),
        "flower_planter": model((0, 0, 0, 10, 3, 9, STONE), (1, 3, 1, 8, 2, 7, GREEN),
                                (2, 5, 2, 3, 2, 2, GOLD), (6, 5, 5, 3, 2, 2, RED)),
        "hedge_planter": model((0, 0, 0, 10, 3, 9, STONE), (1, 3, 1, 8, 4, 7, GREEN),
                               (2, 7, 2, 6, 1, 5, GREEN)),
        "park": model((0, 0, 0, 14, 1, 14, GREEN), (6, 1, 0, 2, 1, 14, GOLD),
                      (2, 1, 3, 1, 5, 1, STONE), (0, 5, 1, 5, 4, 5, GREEN),
                      (9, 1, 8, 4, 1, 4, BLUE), (10, 2, 9, 2, 2, 2, WHITE)),
        "avenue": model((0, 0, 0, 16, 1, 14, SLATE), (1, 1, 0, 14, 1, 14, DARK),
                        (7, 2, 0, 2, 1, 14, GOLD),
                        *((x, 2, z, 1, 1, 2, WHITE) for x, z in product((4, 11), (1, 6, 11)))),
        "promenade": model((0, 0, 0, 15, 1, 14, SLATE), (1, 1, 0, 13, 1, 14, GOLD),
                           (6, 2, 0, 3, 1, 14, WHITE),
                           *((x, 2, z, 2, 3, 2, GREEN) for x, z in product((2, 11), (2, 9)))),
        "path": model((0, 0, 0, 9, 1, 14, GREEN), (3, 1, 0, 3, 1, 14, GOLD),
                      (0, 1, 8, 2, 4, 2, GREEN)),
        "toll": model(*road, (1, 1, 5, 1, 6, 1, TEAL), (8, 1, 5, 1, 6, 1, TEAL),
                      (1, 6, 5, 8, 2, 1, GOLD)),
        "homes": building(RED, 1), "jobs": building(BLUE, 3),
        "mixed": building(TEAL, 2), "height": building(GOLD, 3),
        "zone": model(*((x, 0, z, 5, 2, 5, colour) for x, z, colour in
                        ((0, 0, GREEN), (6, 0, TEAL), (0, 6, GOLD), (6, 6, BLUE)))),
        "bus": vehicle(GOLD, 11), "tram": vehicle(TEAL, 14), "metro": vehicle(BLUE, 12),
        "ferry": model((1, 0, 1, 13, 2, 6, TEAL), (0, 1, 2, 15, 2, 4, WHITE),
                       (3, 3, 2, 9, 2, 4, WHITE), (3, 4, 6, 9, 1, 1, BLUE),
                       (5, 5, 2, 5, 1, 4, TEAL)),
        "stop": model((0, 0, 0, 11, 1, 7, STONE), (1, 1, 1, 1, 5, 1, SLATE),
                      (8, 1, 1, 1, 5, 1, SLATE), (0, 6, 0, 10, 1, 6, TEAL),
                      (2, 1, 2, 6, 1, 2, GOLD)),
        "manage": model((0, 0, 0, 12, 1, 9, DARK), (1, 1, 1, 10, 6, 1, TEAL),
                        *((x, 3, 2, 1, height, 1, GOLD) for x, height in ((3, 1), (5, 2), (7, 3)))),
        "power": model(*((x, 0, z, 2, 2, 1, GOLD) for z, x in enumerate((6, 5, 4, 3, 2, 3, 4, 3, 2, 1)))),
        "plant": model(*plant),
        "geothermal": model(*plant, (3, 7, 3, 2, 3, 2, CYAN), (6, 7, 6, 2, 5, 2, WHITE)),
        "pipe": model((1, 0, 2, 8, 3, 3, BLUE), (7, 0, 4, 3, 3, 8, TEAL),
                      (0, 0, 1, 2, 4, 5, SLATE), (6, 0, 10, 5, 4, 2, SLATE)),
        "water": model((0, 0, 0, 12, 1, 10, BLUE), (2, 1, 2, 8, 1, 6, TEAL),
                       (4, 2, 4, 5, 1, 3, CYAN)),
        "farm": model((0, 0, 0, 13, 1, 11, GREEN), *((x, 1, 1, 2, 1, 9, SOIL)
                      for x in (1, 4, 7, 10)), *((x, 2, z, 1, 2, 1, LIME)
                      for x, z in product((1, 4, 7, 10), (2, 4, 6, 8)))),
        "fish": model((0, 0, 0, 12, 1, 11, BLUE), (2, 1, 3, 8, 2, 4, SLATE),
                      (3, 3, 4, 5, 2, 2, GOLD), (6, 3, 2, 2, 2, 2, WHITE)),
        "depot": model((0, 0, 0, 12, 1, 12, STONE), (1, 1, 1, 10, 6, 10, SLATE),
                       (0, 7, 0, 12, 1, 12, BLUE), (3, 1, 11, 6, 4, 1, DARK),
                       (4, 3, 12, 4, 1, 1, GOLD)),
        "grade": model(*((step, step, step, 12 - 2 * step, 1, 12 - 2 * step, GREEN if step == 4 else SOIL)
                         for step in range(5))),
        "clear": model(*((x, 0, z, 2, 2, 2, RED) for x in range(8) for z in (x, 7 - x))),
        "layers": model(*((0, y, 0, 10, 1, 9, colour)
                          for y, colour in ((0, BLUE), (3, TEAL), (6, LIME)))),
        "survey": model((0, 0, 0, 13, 1, 13, BLUE), (2, 1, 2, 8, 1, 9, GREEN),
                        (3, 2, 2, 5, 2, 5, SOIL), (5, 4, 3, 1, 5, 1, WHITE),
                        (5, 8, 3, 4, 2, 1, GOLD)),
        "pollution": model((0, 0, 0, 13, 1, 10, BLUE), (2, 1, 2, 8, 1, 6, RED),
                           (3, 2, 3, 4, 1, 3, GOLD), (8, 2, 5, 3, 1, 3, SOIL)),
    }


FACES = [
    ((0, 1, 0), ((0,1,0), (1,1,0), (1,1,1), (0,1,1))),
    ((1, 0, 0), ((1,0,0), (1,0,1), (1,1,1), (1,1,0))),
    ((0, 0, 1), ((0,0,1), (0,1,1), (1,1,1), (1,0,1))),
]


def project(x, y, z):
    return x - z, 0.5 * (x + z) - y, x + y + z


def raster(voxels):
    projected = [project(x + dx, y + dy, z + dz) for x,y,z in voxels
                 for dx,dy,dz in product((0,1), repeat=3)]
    lo_x, hi_x = min(p[0] for p in projected), max(p[0] for p in projected)
    lo_y, hi_y = min(p[1] for p in projected), max(p[1] for p in projected)
    scale = min((WIDTH - 4) / (hi_x - lo_x), (HEIGHT - 3) / (hi_y - lo_y))
    ox, oy = (WIDTH - scale * (hi_x + lo_x)) / 2, (HEIGHT - scale * (hi_y + lo_y)) / 2
    depth = [[float("-inf")] * WIDTH for _ in range(HEIGHT)]
    pixels = [[None] * WIDTH for _ in range(HEIGHT)]
    for (x, y, z), colour in voxels.items():
        for shade, ((nx, ny, nz), corners) in enumerate(FACES):
            if (x + nx, y + ny, z + nz) in voxels:
                continue
            vertices = [project(x + dx, y + dy, z + dz) for dx,dy,dz in corners]
            a, b, _, d = [(u * scale + ox, v * scale + oy, w) for u,v,w in vertices]
            ux, uy, vx, vy = b[0] - a[0], b[1] - a[1], d[0] - a[0], d[1] - a[1]
            determinant = ux * vy - uy * vx
            xs = [u * scale + ox for u, _, _ in vertices]
            ys = [v * scale + oy for _, v, _ in vertices]
            for row in range(max(0, int(min(ys))), min(HEIGHT, int(max(ys)) + 1)):
                for col in range(max(0, int(min(xs))), min(WIDTH, int(max(xs)) + 1)):
                    px, py = col + .5 - a[0], row + .5 - a[1]
                    u = (px * vy - py * vx) / determinant
                    v = (ux * py - uy * px) / determinant
                    if not (0 <= u <= 1 and 0 <= v <= 1):
                        continue
                    distance = a[2] + u * (b[2] - a[2]) + v * (d[2] - a[2])
                    if distance > depth[row][col]:
                        depth[row][col] = distance
                        pixels[row][col] = colour * 3 + shade
    return pixels


def spans(pixels):
    data = []
    for y, row in enumerate(pixels):
        x = 0
        while x < WIDTH:
            ink = row[x]
            end = x + 1
            while end < WIDTH and row[end] == ink:
                end += 1
            if ink is not None:
                data.extend(ALPHABET[n] for n in (x, y, end - x, ink))
            x = end
    return "".join(data)


def icon_case(name, voxels):
    lines = textwrap.wrap(spans(raster(voxels)), 104, break_on_hyphens=False)
    return f'      "{name}" ->\n' + " ++\n".join(f'        "{line}"' for line in lines)


def refresh_worship(path):
    source = path.read_text()
    start = source.index('      "', source.index("    match icon do"))
    end = source.index('      _ -> ""', start)
    old_cases = re.split(r'(?=^      "[a-z_]+" ->)', source[start:end], flags=re.M)
    cases = {case.split('"', 2)[1]: case.rstrip() for case in old_cases if case}
    cases.update({name: icon_case(name, voxels) for name, voxels in facilities(WORSHIP).items()})
    path.write_text(source[:start] + "\n".join(cases[name] for name in sorted(cases)) + "\n" + source[end:])


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--worship", action="store_true", help="refresh only worship and seminary thumbnails")
    args = parser.parse_args()
    path = ROOT / "lib/ur/tool_icons.march"
    if args.worship:
        refresh_worship(path)
        return
    art = ['-- Generated by scripts/bake-tool-icons.py.',
           'mod Ur.ToolIcons do', '  fn spans(icon : String) : String do', '    match icon do']
    for name, voxels in sorted(models().items()):
        art.append(icon_case(name, voxels))
    art += ['      _ -> ""', '    end', '  end',
            '  fn colour(ink : Int) : (Float, Float, Float, Float) do', '    match ink do']
    for index, rgb in enumerate(PALETTE):
        for shade, light in enumerate((1.12, .76, .93)):
            channels = ", ".join(f"{min(c * light / 255, 1):.3f}" for c in rgb)
            art.append(f'      {index * 3 + shade} -> ({channels}, 1.0)')
    art += ['      _ -> (0.0, 0.0, 0.0, 0.0)', '    end', '  end', 'end', '']
    path.write_text("\n".join(art))


if __name__ == "__main__":
    main()
