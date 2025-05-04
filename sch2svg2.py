import os
import math
import argparse

colors = [
    "#000000",  # BACKGROUND_COLOR          = #000000
    "#ffffff",  # PIN_COLOR                 = #ffffff
    "#ff0000",  # NET_ENDPOINT_COLOR        = #ff0000
    "#00ff00",  # GRAPHIC_COLOR             = #00ff00
    "#0000ff",  # NET_COLOR                 = #0000ff
    "#ffff00",  # ATTRIBUTE_COLOR           = #ffff00
    "#00ffff",  # LOGIC_BUBBLE_COLOR        = #00ffff
    "#bebebe",  # DOTS_GRID_COLOR           = #bebebe
    "#ff0000",  # DETACHED_ATTRIBUTE_COLOR  = #ff0000
    "#00ff00",  # TEXT_COLOR                = #00ff00
    "#00ff00",  # BUS_COLOR                 = #00ff00
    "#ffa500",  # SELECT_COLOR              = #ffa500
    "#ffa500",  # BOUNDINGBOX_COLOR         = #ffa500
    "#00ffff",  # ZOOM_BOX_COLOR            = #00ffff
    "#e5e5e5",  # STROKE_COLOR              = #e5e5e5
    "#bebebe",  # LOCK_COLOR                = #bebebe
    "#00ff00",  # OUTPUT_BACKGROUND_COLOR   = #00ff00
    "#00ff00",  # FREESTYLE1_COLOR          = #00ff00
    "#00ff00",  # FREESTYLE2_COLOR          = #00ff00
    "#00ff00",  # FREESTYLE3_COLOR          = #00ff00
    "#00ff00",  # FREESTYLE4_COLOR          = #00ff00
    "#ffff00",  # JUNCTION_COLOR            = #ffff00
    "#1e1e1e",  # MESH_GRID_MAJOR_COLOR     = #1e1e1e
    "#171717"  # MESH_GRID_MINOR_COLOR     = #171717
]
MIN_THICKNESS = 12  # Minimum thickness of any line.
LINE_SPACING = 1  # Spacing (as a multiple of the font size) between lines of multiline text objects
# Additional folders in which to search for symbols can be included here:
# SYMBOLS = ["/usr/share/gEDA/sym/"]
SYMBOLS = []
# SYMBOLS = ["/Users/matthias/Downloads/geda-gaf-1.10.2/symbols/", "/Users/matthias/Downloads/symbols"]

p = argparse.ArgumentParser(
    description="""Convert a gEDA/gschem schematic file (.sch) or symbol file (.sym) to an .svg image file""")
p.add_argument("-i", "--in-file",
               type=lambda x: x if os.path.isfile(x) and (x.endswith(".sch") or x.endswith(".sym")) else p.error(
                   "File \"{}\" does not exist or is not a schematic or symbol file".format(x)),
               help="A .sch or .sym file from which a schematic is read", required=True)
p.add_argument("-o", "--out-file",
               type=lambda x: x if x.endswith(".svg") else p.error("File \"{}\" must be an .svg file".format(x)),
               help="A .svg file to which an image of the schematic is written")
p.add_argument("--colors", help="A file containing a list of colors")
p.add_argument("-g", dest="gmin", action="store_true", help="Include minor grid lines every 100px")
p.add_argument("-G", dest="gmaj", action="store_true", help="Include major grid lines every 500px")
p.add_argument("-l", "--lib", nargs="*", action="store", help="Directories to be recursively searched for symbol files")
p.add_argument("-t", "--thick", type=int, help="Minimum thickness of lines")
a = p.parse_args()
if a.lib: SYMBOLS += a.lib
if a.thick: MIN_THICKNESS = a.thick
print("Looking for symbols in", SYMBOLS, a.lib)
in_file = a.in_file
out_file = a.out_file or os.path.splitext(in_file)[0] + ".svg"
if a.colors:
    with open(a.colors) as f:
        colors = [l[:7] for l in f]


def locateFile(start, symname):
    ps = os.path.join(start, symname)
    if os.path.isfile(ps) and "gnetman" not in ps:
        return ps
    for x in os.listdir(start):
        px = os.path.join(start, x)
        if os.path.isdir(px):
            rec = locateFile(px, symname)
            if rec is not None: return rec


def parseObjects(cont):
    ts = cont.split("\n")
    i = 0
    bounds = [1e9, 1e9, -1e9, -1e9]
    objs = []
    attributes = []

    # Funkcja pomocnicza do bezpiecznego pobierania i konwersji wartości
    def safe_get_int(lst, idx, default=0):
        if idx >= len(lst):
            return default
        try:
            return int(lst[idx])
        except ValueError:
            try:
                return int(lst[idx], 16)
            except ValueError:
                return default

    while i < len(ts):
        t = ts[i]
        i += 1
        if not t: continue
        if t[0] == "$": continue
        if t[0] == "#": continue
        hs = t.split()
        if not hs: continue
        t = hs[0]

        if t in "LNUP":
            hs1 = safe_get_int(hs, 1)
            hs2 = safe_get_int(hs, 2)
            hs3 = safe_get_int(hs, 3)
            hs4 = safe_get_int(hs, 4)

            bounds[0] = min(bounds[0], hs1)
            bounds[1] = min(bounds[1], hs2)
            bounds[2] = max(bounds[2], hs3)
            bounds[3] = max(bounds[3], hs4)
        if t == "B":
            hs1 = safe_get_int(hs, 1)
            hs2 = safe_get_int(hs, 2)
            hs3 = safe_get_int(hs, 3)
            hs4 = safe_get_int(hs, 4)

            bounds[0] = min(bounds[0], hs1)
            bounds[1] = min(bounds[1], hs2)
            bounds[2] = max(bounds[2], hs1 + hs3)
            bounds[3] = max(bounds[3], hs2 + hs4)
        if t == "T":
            hs1 = safe_get_int(hs, 1)
            hs2 = safe_get_int(hs, 2)

            bounds[0] = min(bounds[0], hs1)
            bounds[1] = min(bounds[1], hs2)
            bounds[2] = max(bounds[2], hs1)
            bounds[3] = max(bounds[3], hs2)
        if t == "A" or t == 'V':
            hs1 = safe_get_int(hs, 1)
            hs2 = safe_get_int(hs, 2)
            hs3 = safe_get_int(hs, 3)
            hs4 = safe_get_int(hs, 4)
            hs5 = safe_get_int(hs, 5)

            bounds[0] = min(bounds[0], hs1 - hs3)
            bounds[1] = min(bounds[1], hs2 - hs3)
            bounds[2] = max(bounds[2], hs1 + hs3)
            bounds[3] = max(bounds[3], hs2 + hs3)

        if t == "C":
            # TODO: identify the size of a component by opening the file
            name = hs[-1]
            if hs[-1] == "EMBEDDED":
                # Load the contents of the component from the embedded content, if available
                loffs = [0, 0]
                pcont = hs[-2]
            else:
                # Otherwise look for a file
                loffs = [int(hs[1]), int(hs[2])]
                for source in SYMBOLS:
                    fn = locateFile(source, name)
                    if fn is None: continue

                    with open(fn) as sym:
                        pcont = sym.read()
                    hs[-1] = fn
                    break
                else:
                    print("Component not found: '{}'".format(name))
                    hs[-1] = None
                    continue
            print(type(pcont), loffs, hs, name)
            if hs[-1] is None: print(pcont)
            compb = parseObjects(pcont)['bounds']
            compb = preTransformCoords(compb, loffs, 0 if "EMBEDDED" in hs[-1] else int(hs[4]),
                                       int(hs[5]))
            bounds[0] = min(bounds[0], compb[0])
            bounds[1] = min(bounds[1], compb[1])
            bounds[2] = max(bounds[2], compb[2])
            bounds[3] = max(bounds[3], compb[3])

        objs.append({"head": t, "type": t, "param": hs[1:], "data": "", "braces": "", "brackets": ""})

        if i < len(ts):
            next = ts[i]
            if next[0] == "[":
                i += 1
                next = ts[i]
                i += 1
                brackets = ""
                while next[0] != "]":
                    brackets += next + "\n"
                    next = ts[i]
                    i += 1
                objs[-1]["brackets"] = brackets
            if i < len(ts):
                next = ts[i]
                if next[0] == "{":
                    i += 1
                    next = ts[i]
                    i += 1
                    braces = ""
                    while next[0] != "}":
                        braces += next + "\n"
                        next = ts[i]
                        i += 1
                    objs[-1]["braces"] = braces
            if t in "TH":
                length = int(hs[-1])
                data = ""
                for x in range(length):
                    data += ts[i] + "\n"
                    i += 1
                objs[-1]["data"] = data

    return {"objects": objs, "bounds": bounds, "attr": attributes}


def parseAttributes(text):
    if not text.strip(): return []
    ts = text.strip().split("\n")
    i = 0
    attr = []
    while (i < len(ts)):
        key = ""
        value = ""
        head = ts[i]
        i += 1
        hs = head.strip().split(" ")
        length = int(hs[-1])
        if length == 0:
            continue
        else:
            l = ts[i]
            i += 1
            key, value = l.split("=", 1)
            for x in range(length - 1):
                value += ts[i]
                i += 1
            attr.append([hs, key, value])
    return attr


def transformCoords(bounds, coords, localoffset=[0, 0], rot=0, mirror=False, margin=1000):
    if len(coords) == 4: return transformCoords(bounds, coords[:2], localoffset, rot, margin) + transformCoords(bounds,
                                                                                                                coords[
                                                                                                                2:],
                                                                                                                localoffset,
                                                                                                                rot,
                                                                                                                margin)
    x, y = coords
    rx, ry = {
        0: [x, y],
        90: [y, -x],
        180: [-x, -y],
        270: [-y, x]
    }.get(rot, coords)
    if mirror: rx = -rx
    return [(rx + localoffset[0]) - bounds[0] + margin,
            bounds[3] - (ry + localoffset[1]) + margin]  # x - xmin, ymax - y


def preTransformCoords(coords, localoffset=[0, 0], rot=0, mirror=False):
    if len(coords) == 4: 
        return preTransformCoords(coords[:2], localoffset, rot, mirror) + preTransformCoords(
            coords[2:], localoffset, rot, mirror)
    
    # Upewnij się, że coords ma co najmniej 2 elementy
    if len(coords) < 2:
        # Jeśli coords ma mniej niż 2 elementy, dodaj brakujące elementy
        if len(coords) == 0:
            x, y = 0, 0
        else:
            try:
                x = int(coords[0])
            except (ValueError, TypeError):
                try:
                    x = int(coords[0], 16)
                except (ValueError, TypeError):
                    x = 0
            y = 0
    else:
        try:
            x = int(coords[0])
        except (ValueError, TypeError):
            try:
                x = int(coords[0], 16)
            except (ValueError, TypeError):
                x = 0
        try:
            y = int(coords[1])
        except (ValueError, TypeError):
            try:
                y = int(coords[1], 16)
            except (ValueError, TypeError):
                y = 0
        
    if mirror: x = -x
    rx, ry = {
        0: [x, y],
        90: [-y, x],
        180: [-x, -y],
        270: [y, -x]
    }.get(rot, [x, y])
    # if mirror: rx = -rx
    return [(rx + localoffset[0]), (ry + localoffset[1])]


def postTransformCoords(bounds, coords, margin=1000):
    # Upewnij się, że coords ma co najmniej 2 elementy
    if len(coords) < 2:
        # Jeśli coords ma mniej niż 2 elementy, dodaj brakujące elementy
        if len(coords) == 0:
            return [margin, margin]
        else:
            return [coords[0] - bounds[0] + margin, margin]
    
    if len(coords) == 4: 
        return [coords[0] - bounds[0] + margin, bounds[3] - coords[1] + margin,
                coords[2] - bounds[0] + margin, bounds[3] - coords[3] + margin]
                
    return [coords[0] - bounds[0] + margin, bounds[3] - coords[1] + margin]


def string2svg(text):
    text = text.split("\\_")
    inside = False
    result = ""
    for x in text:
        if x:
            if inside:
                result += '<tspan text-decoration="overline">{}</tspan>'.format(x)
            else:
                result += '<tspan>{}</tspan>'.format(x)
        inside = not inside
    return result


def polarToCartesian(centerX, centerY, radius, angleInDegrees):
    angleInRadians = (angleInDegrees) * math.pi / 180.0;

    return [
        centerX + (radius * math.cos(angleInRadians)),
        centerY + (radius * math.sin(angleInRadians))
    ];


def getColor(ind, lock):
    return colors[15] if lock else colors[int(ind)]


def writeSymbolObject(out, obj, unpaired, netsegments, bounds, localoffset=[0, 0], rot=0, mirror=False,
                      component_attributes=[], embedded=False, locked=False, slotdef=None):
    par = obj['param']
    # paths
    if obj['type'] == 'H':
        out.write('<path transform="translate({}, {}) rotate({}) scale({}, -1)" d="{}" fill="{}"/>'.format(
            *postTransformCoords(bounds, localoffset), 360 - rot, -1 if mirror else 1,
            obj['data'].strip().replace("\n", " "), colors[int(par[0])]))

    if obj['type'] not in "PNLBTAVU": return
    tcoords = preTransformCoords(par[:4] if obj['type'] in "PNLBU" else par[:2], localoffset, 0 if embedded else rot,
                                 mirror)
    if localoffset == [46500, 47100]: print(obj['type'], par, tcoords)
    # pins
    if obj['type'] in 'P':
        out.write('<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="{}" stroke-width="{}"/>\n'.format(
            *postTransformCoords(bounds, tcoords), getColor(par[4], locked), MIN_THICKNESS))
        target = tcoords[0:2] if par[6] == "0" else tcoords[2:4]
        for x in unpaired:
            if x[:2] == target:
                x[2] += 1
                break
        else:
            unpaired.append(target + [1])
    # nets
    if obj['type'] in 'N':
        out.write('<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="{}" stroke-width="{}"/>\n'.format(
            *postTransformCoords(bounds, tcoords), getColor(par[4], locked), MIN_THICKNESS))
        for x in unpaired:
            if x[:2] == tcoords[:2]:
                x[2] += 1
                break
        else:
            unpaired.append(tcoords[:2] + [1])
        for x in unpaired:
            if x[:2] == tcoords[2:4]:
                x[2] += 1
                break
        else:
            unpaired.append(tcoords[2:4] + [1])

        netsegments.append(tcoords[:4])
    # wires
    if obj['type'] == 'W':
        # Bezpieczne uzyskiwanie dostępu do par[4]
        color_index = par[4] if len(par) > 4 else "0"
        thickness = max(MIN_THICKNESS, int(par[5]) if len(par) > 5 else MIN_THICKNESS)
        
        # Pobierz współrzędne początkowe i końcowe
        start_coords = postTransformCoords(bounds, tcoords[:2])
        end_coords = postTransformCoords(bounds, tcoords[2:4])
        
        out.write('<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="{}" stroke-width="{}px" />\n'.format(
            start_coords[0], start_coords[1], end_coords[0], end_coords[1], 
            getColor(color_index, locked), thickness))
    # labels
    if obj['type'] == 'L':
        # Bezpieczne uzyskiwanie dostępu do par[4]
        color_index = par[4] if len(par) > 4 else "0"
        thickness = max(MIN_THICKNESS, int(par[5]) if len(par) > 5 else MIN_THICKNESS)
        
        # Pobierz współrzędne początkowe i końcowe
        start_coords = postTransformCoords(bounds, tcoords[:2])
        end_coords = postTransformCoords(bounds, tcoords[2:4])
        
        out.write('<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="{}" stroke-width="{}px" />\n'.format(
            start_coords[0], start_coords[1], end_coords[0], end_coords[1], 
            getColor(color_index, locked), thickness))
    # busses
    if obj['type'] == 'U':
        # Bezpieczne uzyskiwanie dostępu do par[4]
        color_index = par[4] if len(par) > 4 else "0"
        
        # Pobierz współrzędne początkowe i końcowe
        start_coords = postTransformCoords(bounds, tcoords[:2])
        end_coords = postTransformCoords(bounds, tcoords[2:4])
        
        out.write('<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="{}" stroke-width="{}px" />\n'.format(
            start_coords[0], start_coords[1], end_coords[0], end_coords[1], 
            getColor(color_index, locked), 30))
    # boxes
    if obj['type'] == 'B':
        box_corners = preTransformCoords([par[0], par[1], par[0] + par[2], par[1] + par[3]], localoffset, rot, mirror)
        out.write(
            '<rect x="{}" y="{}" width="{}" height="{}" stroke="{}" fill="none" stroke-width="{}px" />\n'.format(
                *postTransformCoords(bounds, box_corners[:2]),
                box_corners[2] - box_corners[0], box_corners[3] - box_corners[1],
                getColor(par[4] if len(par) > 4 else "0", locked),
                max(int(par[5]) if len(par) > 5 else MIN_THICKNESS, MIN_THICKNESS)))
    # text
    if obj['type'] == 'T':
        if par[4] == "0": return
        text = obj['data'].strip()
        if "=" in text:
            name = text.split("=", 1)[0]
            for h, key, value in component_attributes:
                if key == name:
                    return
        pos = int(par[7])
        rot += int(par[6])
        if rot == 180:
            # Anchor is flipped but the text is not
            anchor = ["end", "middle", "begin"][2 - int(pos / 3) if mirror else int(pos / 3)]
            baseline = ["hanging", "middle", "baseline"][pos % 3]
        else:
            anchor = ["begin", "middle", "end"][2 - int(pos / 3) if mirror else int(pos / 3)]
            baseline = ["baseline", "middle", "hanging"][pos % 3]
        """
        anchor = ["begin", "middle", "end"][int(pos/3)]
        baseline = ["baseline", "middle", "hanging"][pos%3]"""
        if par[5] == "1" and "=" in text: text = text.split("=", 1)[1]
        if par[5] == "2" and "=" in text: text = text.split("=", 1)[0]
        fontsize = int(int(par[3]) * 1000 / 72)
        v_offset = 0 if baseline == "hanging" else LINE_SPACING * fontsize * text.count("\n")
        if baseline == "middle": v_offset = v_offset / 2
        for i, part in enumerate(text.split("\n")):
            out.write(
                '<text text-anchor="{}" dominant-baseline="{}" transform="translate({}, {}) rotate({})" fill="{}" font-size="{}"><tspan>{}</tspan></text>\n'.format(
                    anchor, baseline,
                    *postTransformCoords(bounds, [tcoords[0], tcoords[1] - i * LINE_SPACING * fontsize + v_offset]),
                    360 - rot if rot != 180 else 0,
                    getColor(par[2], locked), fontsize, string2svg(part))
            )
    # arcs
    if obj['type'] == 'A':
        start = polarToCartesian(par[0], par[1], par[2], par[3])
        end = polarToCartesian(par[0], par[1], par[2], par[3] + par[4])

        largeArcFlag = "0" if par[4] <= 180 else "1";
        m = -1 if mirror else 1

        d = " ".join(str(x) for x in [
            "M", *start,
            "A", par[2], par[2], 0, largeArcFlag, 1, *end
        ])
        out.write(
            '<path transform="translate({}, {}) rotate({}) scale({}, -1)" d="{}" stroke="{}" fill-opacity="0" stroke-width="{}"/>'.format(
                *postTransformCoords(bounds, localoffset), 360 - rot, m, d, getColor(par[5], locked),
                max(int(par[6]), MIN_THICKNESS)))
    # circles
    if obj['type'] == 'V':
        out.write(
            '<circle cx="{0}" cy="{1}" r="{2}" stroke="{3}" fill="{3}" stroke-width="{4}" fill-opacity="{5}"/>\n'.format(
                *postTransformCoords(bounds, tcoords), par[2], getColor(par[3], locked), max(MIN_THICKNESS, par[4]),
                par[9]))

    attr = parseAttributes(obj["braces"])
    pinseq = None
    for h, key, value in attr:
        if key == "pinseq": pinseq = value
    for h, key, value in attr:
        if h[5] == "0": continue
        pos = int(h[8])
        lrot = int(h[7]) if embedded else (int(h[7]) + rot) % 360
        if lrot == 180:
            # Anchor is flipped but the text is not
            anchor = ["end", "middle", "begin"][int(pos / 3)]
            baseline = ["hanging", "middle", "baseline"][pos % 3]
        else:
            anchor = ["begin", "middle", "end"][int(pos / 3)]
            baseline = ["baseline", "middle", "hanging"][pos % 3]
        """
        anchor = ["begin", "middle", "end"][int(pos/3)]
        baseline = ["baseline", "middle", "hanging"][pos%3]"""
        if slotdef and key == "pinnumber" and pinseq is not None: value = slotdef[int(pinseq) - 1]
        if h[6] == "0": text = key + "=" + value
        if h[6] == "1": text = value
        if h[6] == "2": text = key
        out.write(
            '<text text-anchor="{}" dominant-baseline="{}" transform="translate({}, {}) rotate({})" fill="{}" font-size="{}"><tspan>{}</tspan></text>\n'.format(
                anchor, baseline, *postTransformCoords(bounds, [int(h[1]), int(h[2])]),
                360 - lrot if lrot != 180 else 0, getColor(h[3], locked), int(int(h[4]) * 1000 / 72), string2svg(text)))


with open(in_file) as f:
    cont = f.read()
    with open(out_file, "w") as out:
        parse = parseObjects(cont)
        bounds = parse['bounds']
        out.write('''<svg viewBox="0 0 {0} {1}" xmlns="http://www.w3.org/2000/svg">
<rect x="0" y="0" width="{0}" height="{1}" style="fill:{2};" />\n'''.format(bounds[2] - bounds[0] + 2000,
                                                                            bounds[3] - bounds[1] + 2000, colors[0]))

        # Insert grid lines first so they appear at the bottom
        if a.gmin:
            gmin_x1 = 100 - ((bounds[0] - 1000) % 100)
            gmin_x2 = bounds[2] - bounds[0] + 2000
            gmin_y1 = 100 if (bounds[3] + 1000) % 100 == 0 else (bounds[3] + 1000) % 100
            gmin_y2 = bounds[3] - bounds[1] + 2000
            while gmin_x1 < gmin_x2:
                out.write(
                    '<line x1="{0}" y1="0" x2="{0}" y2="{1}" stroke="{2}" stroke-thickness="{3}"/>\n'.format(gmin_x1,
                                                                                                             gmin_y2,
                                                                                                             colors[23],
                                                                                                             1))
                gmin_x1 += 100
            while gmin_y1 < gmin_y2:
                out.write(
                    '<line x1="0" y1="{0}" x2="{1}" y2="{0}" stroke="{2}" stroke-thickness="{3}"/>\n'.format(gmin_y1,
                                                                                                             gmin_x2,
                                                                                                             colors[23],
                                                                                                             1))
                gmin_y1 += 100

        if a.gmaj:
            gmaj_x1 = 500 - ((bounds[0] - 1000) % 500)
            gmaj_x2 = bounds[2] - bounds[0] + 2000
            gmaj_y1 = 500 if (bounds[3] + 1000) % 500 == 0 else (bounds[3] + 1000) % 500
            gmaj_y2 = bounds[3] - bounds[1] + 2000
            while gmaj_x1 < gmaj_x2:
                out.write(
                    '<line x1="{0}" y1="0" x2="{0}" y2="{1}" stroke="{2}" stroke-thickness="{3}"/>\n'.format(gmaj_x1,
                                                                                                             gmaj_y2,
                                                                                                             colors[22],
                                                                                                             2))
                gmaj_x1 += 500
            while gmaj_y1 < gmaj_y2:
                out.write(
                    '<line x1="0" y1="{0}" x2="{1}" y2="{0}" stroke="{2}" stroke-thickness="{3}"/>\n'.format(gmaj_y1,
                                                                                                             gmaj_x2,
                                                                                                             colors[22],
                                                                                                             2))
                gmaj_y1 += 500

        unpaired = []
        netsegments = []
        for obj in parse['objects']:
            par = obj['param']
            if obj['type'] in "LNPBTHVAU":
                writeSymbolObject(out, obj, unpaired, netsegments, bounds)

            if obj['type'] == 'C':
                # Parse a component
                angle = int(par[3])
                mirror = par[4] == "1"
                name = par[-1]
                if obj['brackets']:
                    # Load the contents of the component from the embedded content, if available
                    loffs = [0, 0]
                    pcont = obj['brackets']
                else:
                    # Otherwise look for a file
                    loffs = [int(par[0]), int(par[1])]
                    if par[-1] is None: continue
                    with open(par[-1]) as sym:
                        pcont = sym.read()
                pbrac = parseObjects(pcont)
                comp_attr = parseAttributes(obj['braces'])
                slotdef = []
                slot = None
                for h, key, value in comp_attr:
                    if key == "slot": slot = value
                for x in pbrac["attr"]:
                    if x[0] == "slotdef":
                        x = x[1].split(":")
                        if slot == x[0]: slotdef = [y.strip() for y in x[1].split(",")]
                for pobj in pbrac['objects']:
                    writeSymbolObject(out, pobj, unpaired, netsegments, bounds, loffs, angle, mirror, comp_attr,
                                      par[-1].startswith("EMBEDDED"), par[2] == "0", slotdef)

                # Add in the attributes
                for h, key, value in comp_attr:
                    if h[5] == "0": continue
                    pos = int(h[8])
                    lrot = int(h[7])
                    if lrot == 180:
                        # Anchor is flipped but the text is not
                        anchor = ["end", "middle", "begin"][int(pos / 3)]
                        baseline = ["hanging", "middle", "baseline"][pos % 3]
                    else:
                        anchor = ["begin", "middle", "end"][int(pos / 3)]
                        baseline = ["baseline", "middle", "hanging"][pos % 3]
                    """
                    anchor = ["begin", "middle", "end"][int(pos/3)]
                    baseline = ["baseline", "middle", "hanging"][pos%3]"""
                    if slotdef and key == "pinnumber" and pinseq is not None: value = slotdef[int(pinseq) - 1]
                    if h[6] == "0": text = key + "=" + value
                    if h[6] == "1": text = value
                    if h[6] == "2": text = key
                    out.write(
                        '<text text-anchor="{}" dominant-baseline="{}" transform="translate({}, {}) rotate({})" fill="{}" font-size="{}"><tspan>{}</tspan></text>\n'.format(
                            anchor, baseline, *postTransformCoords(bounds, [int(h[1]), int(h[2])]),
                            360 - lrot if lrot != 180 else 0, getColor(h[3], par[2] == "0"), int(int(h[4]) * 1000 / 72),
                            string2svg(text)))

        for x in unpaired:
            # Verify that the enpoint does not actually connect to a net
            for s in netsegments:
                if ((s[3] - s[1]) * (x[0] - s[0]) == (x[1] - s[1]) * (
                        s[2] - s[0]) and  # If the point is on an an infinite line through the segment
                        min(s[1], s[3]) <= x[1] <= max(s[1], s[3]) and  # and the point is on the segment
                        min(s[0], s[2]) <= x[0] <= max(s[0], s[2]) and
                        not (x[0] in [s[0], s[2]] and x[1] in [s[1], s[
                            3]])):  # and the point is not on one of the endpoints of the segment
                    x[2] += 2  # Add two because the segment continues in both directions

            if x[2] > 2:
                out.write(
                    '<circle cx="{}" cy="{}" r="25" fill="#ffff00" />\n'.format(*postTransformCoords(bounds, x[:2])))
            if x[2] == 1:
                out.write('<rect x="{}" y="{}" width="60" height="60" style="fill:red;" />\n'.format(
                    *transformCoords(bounds, [x[0] - 30, x[1] + 30])))

        out.write("</svg>\n")