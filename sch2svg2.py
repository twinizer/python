import os
import math
import argparse
import sys

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


def parseKiCadSchematic(content):
    """
    Parsuje schemat KiCad i zwraca obiekty do renderowania.
    
    Args:
        content: Zawartość pliku schematu KiCad
        
    Returns:
        Słownik z obiektami do renderowania
    """
    objects = []
    bounds = [0, 0, 1000, 1000]  # Domyślne granice
    
    # Sprawdź, czy to schemat KiCad 5 lub starszy (EESchema)
    if content.startswith("EESchema Schematic"):
        return parseKiCadSchematic5(content)
    # Sprawdź, czy to schemat KiCad 6 lub nowszy (kicad_sch)
    elif content.startswith("(kicad_sch"):
        return parseKiCadSchematic6(content)
    else:
        # Nieznany format schematu
        raise ValueError("Nieobsługiwany format schematu KiCad")

def parseKiCadSchematic5(content):
    """
    Parsuje schemat KiCad 5 (format EESchema).
    
    Args:
        content: Zawartość pliku schematu KiCad
        
    Returns:
        Słownik z obiektami do renderowania
    """
    objects = []
    bounds = [0, 0, 3000, 2000]  # Domyślne granice dla KiCad 5
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Parsuj przewody (Wire)
        if line.startswith("Wire Wire Line"):
            try:
                i += 1
                coords = lines[i].strip().split()
                if len(coords) >= 4:
                    x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
                    objects.append({
                        'type': 'W',
                        'param': ["0", "0", "0", "0", "0", "1"],  # Domyślne parametry
                        'coords': [x1, y1, x2, y2]
                    })
                    # Aktualizuj granice
                    bounds[0] = min(bounds[0], x1, x2)
                    bounds[1] = min(bounds[1], y1, y2)
                    bounds[2] = max(bounds[2], x1, x2)
                    bounds[3] = max(bounds[3], y1, y2)
            except:
                pass
        
        # Parsuj komponenty (Comp)
        elif line.startswith("$Comp"):
            try:
                comp_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("$EndComp"):
                    comp_lines.append(lines[i])
                    i += 1
                
                # Znajdź nazwę komponentu i pozycję
                comp_name = ""
                comp_x, comp_y = 0, 0
                
                for comp_line in comp_lines:
                    if comp_line.strip().startswith("L "):
                        parts = comp_line.strip().split()
                        if len(parts) > 1:
                            comp_name = parts[1]
                    elif comp_line.strip().startswith("P "):
                        parts = comp_line.strip().split()
                        if len(parts) > 2:
                            comp_x, comp_y = int(parts[1]), int(parts[2])
                
                if comp_name:
                    objects.append({
                        'type': 'C',
                        'param': [str(comp_x), str(comp_y), "0", "0", "0", comp_name],
                        'coords': [comp_x, comp_y, comp_x + 100, comp_y + 100]  # Przybliżone wymiary
                    })
                    # Aktualizuj granice
                    bounds[0] = min(bounds[0], comp_x)
                    bounds[1] = min(bounds[1], comp_y)
                    bounds[2] = max(bounds[2], comp_x + 100)
                    bounds[3] = max(bounds[3], comp_y + 100)
            except:
                pass
        
        # Parsuj etykiety (Text)
        elif line.startswith("Text "):
            try:
                parts = line.strip().split()
                if len(parts) > 5:
                    text_type = parts[1]
                    x, y = int(parts[2]), int(parts[3])
                    text = " ".join(parts[5:])
                    
                    objects.append({
                        'type': 'T',
                        'param': ["0", "0", "0", "0", "0", text],
                        'coords': [x, y, x + len(text) * 10, y + 20]  # Przybliżone wymiary
                    })
                    # Aktualizuj granice
                    bounds[0] = min(bounds[0], x)
                    bounds[1] = min(bounds[1], y)
                    bounds[2] = max(bounds[2], x + len(text) * 10)
                    bounds[3] = max(bounds[3], y + 20)
            except:
                pass
        
        i += 1
    
    return {
        'objects': objects,
        'bounds': bounds,
        'unpaired': {},
        'netsegments': {}
    }

def parseKiCadSchematic6(content):
    """
    Parsuje schemat KiCad 6 (format kicad_sch).
    
    Args:
        content: Zawartość pliku schematu KiCad
        
    Returns:
        Słownik z obiektami do renderowania
    """
    objects = []
    bounds = [0, 0, 3000, 2000]  # Domyślne granice dla KiCad 6
    
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Parsuj przewody (wire)
        if line.startswith("(wire"):
            try:
                wire_lines = []
                while i < len(lines) and not lines[i].strip().endswith(")"):
                    wire_lines.append(lines[i])
                    i += 1
                wire_lines.append(lines[i])  # Dodaj linię kończącą
                
                wire_text = " ".join(wire_lines)
                
                # Wyciągnij współrzędne za pomocą wyrażeń regularnych
                import re
                pts = re.findall(r'\(pts \(xy ([0-9.-]+) ([0-9.-]+)\) \(xy ([0-9.-]+) ([0-9.-]+)\)\)', wire_text)
                
                if pts:
                    x1, y1, x2, y2 = float(pts[0][0]), float(pts[0][1]), float(pts[0][2]), float(pts[0][3])
                    objects.append({
                        'type': 'W',
                        'param': ["0", "0", "0", "0", "0", "1"],  # Domyślne parametry
                        'coords': [x1, y1, x2, y2]
                    })
                    # Aktualizuj granice
                    bounds[0] = min(bounds[0], x1, x2)
                    bounds[1] = min(bounds[1], y1, y2)
                    bounds[2] = max(bounds[2], x1, x2)
                    bounds[3] = max(bounds[3], y1, y2)
            except:
                pass
        
        # Parsuj symbole (symbol)
        elif line.startswith("(symbol"):
            try:
                symbol_lines = []
                symbol_depth = 1
                i += 1
                
                while i < len(lines) and symbol_depth > 0:
                    if lines[i].strip().startswith("(symbol"):
                        symbol_depth += 1
                    elif lines[i].strip() == ")":
                        symbol_depth -= 1
                    
                    symbol_lines.append(lines[i])
                    i += 1
                
                symbol_text = " ".join(symbol_lines)
                
                # Wyciągnij nazwę i pozycję za pomocą wyrażeń regularnych
                import re
                lib_id = re.findall(r'\(lib_id "([^"]+)"\)', symbol_text)
                at = re.findall(r'\(at ([0-9.-]+) ([0-9.-]+) ([0-9.-]+)\)', symbol_text)
                
                if lib_id and at:
                    comp_name = lib_id[0]
                    comp_x, comp_y = float(at[0][0]), float(at[0][1])
                    
                    objects.append({
                        'type': 'C',
                        'param': [str(comp_x), str(comp_y), "0", "0", "0", comp_name],
                        'coords': [comp_x, comp_y, comp_x + 100, comp_y + 100]  # Przybliżone wymiary
                    })
                    # Aktualizuj granice
                    bounds[0] = min(bounds[0], comp_x)
                    bounds[1] = min(bounds[1], comp_y)
                    bounds[2] = max(bounds[2], comp_x + 100)
                    bounds[3] = max(bounds[3], comp_y + 100)
            except:
                pass
        
        # Parsuj teksty (text)
        elif line.startswith("(text"):
            try:
                text_lines = []
                while i < len(lines) and not lines[i].strip().endswith(")"):
                    text_lines.append(lines[i])
                    i += 1
                text_lines.append(lines[i])  # Dodaj linię kończącą
                
                text_text = " ".join(text_lines)
                
                # Wyciągnij tekst i pozycję za pomocą wyrażeń regularnych
                import re
                text_content = re.findall(r'"([^"]+)"', text_text)
                at = re.findall(r'\(at ([0-9.-]+) ([0-9.-]+)[^)]*\)', text_text)
                
                if text_content and at:
                    text = text_content[0]
                    x, y = float(at[0][0]), float(at[0][1])
                    
                    objects.append({
                        'type': 'T',
                        'param': ["0", "0", "0", "0", "0", text],
                        'coords': [x, y, x + len(text) * 10, y + 20]  # Przybliżone wymiary
                    })
                    # Aktualizuj granice
                    bounds[0] = min(bounds[0], x)
                    bounds[1] = min(bounds[1], y)
                    bounds[2] = max(bounds[2], x + len(text) * 10)
                    bounds[3] = max(bounds[3], y + 20)
            except:
                pass
        
        i += 1
    
    return {
        'objects': objects,
        'bounds': bounds,
        'unpaired': {},
        'netsegments': {}
    }

def parseSchematic(content):
    """
    Parsuje schemat i zwraca obiekty do renderowania.
    
    Args:
        content: Zawartość pliku schematu
        
    Returns:
        Słownik z obiektami do renderowania
    """
    # Sprawdź, czy to schemat KiCad
    if content.startswith("EESchema Schematic") or content.startswith("(kicad_sch"):
        try:
            return parseKiCadSchematic(content)
        except Exception as e:
            print(f"Błąd podczas parsowania schematu KiCad: {e}")
            # Jeśli parsowanie KiCad nie powiodło się, spróbuj parsować jako gEDA
            return parseObjects(content)
    else:
        # Spróbuj parsować jako gEDA
        return parseObjects(content)

if __name__ == "__main__":
    # Parsowanie argumentów wiersza poleceń
    parser = argparse.ArgumentParser(description='Konwertuje schemat KiCad do SVG')
    parser.add_argument('-i', '--input', required=True, help='Plik wejściowy schematu KiCad')
    parser.add_argument('-o', '--output', required=True, help='Plik wyjściowy SVG')
    parser.add_argument('-v', '--verbose', action='store_true', help='Wyświetlaj szczegółowe informacje')
    
    args = parser.parse_args()
    
    try:
        # Sprawdź, czy plik wejściowy istnieje
        if not os.path.exists(args.input):
            print(f"Błąd: Plik wejściowy {args.input} nie istnieje.")
            sys.exit(1)
        
        # Upewnij się, że katalog wyjściowy istnieje
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        
        # Parsuj schemat
        print(f"Parsowanie schematu {args.input}...")
        
        try:
            with open(args.input, 'r') as f:
                content = f.read()
        except Exception as e:
            print(f"Błąd podczas odczytu pliku: {e}")
            sys.exit(1)
        
        try:
            parsed = parseSchematic(content)
            
            if not parsed:
                print("Błąd: Nie udało się sparsować schematu.")
                sys.exit(1)
                
            objects = parsed.get('objects', [])
            bounds = parsed.get('bounds', [0, 0, 1000, 1000])
            unpaired = parsed.get('unpaired', {})
            netsegments = parsed.get('netsegments', {})
            
            # Generuj SVG
            print(f"Generowanie pliku SVG {args.output}...")
            
            with open(args.output, 'w') as out:
                out.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
                out.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{bounds[2] - bounds[0] + 2000}" height="{bounds[3] - bounds[1] + 2000}">\n')
                out.write('<rect width="100%" height="100%" fill="white"/>\n')
                
                # Dodaj obiekty do SVG
                for obj in objects:
                    try:
                        writeSymbolObject(out, obj, unpaired, netsegments, bounds)
                    except Exception as e:
                        if args.verbose:
                            print(f"Błąd podczas generowania obiektu {obj.get('type', 'unknown')}: {e}")
                        continue
                
                out.write('</svg>\n')
            
            print(f"Plik SVG został wygenerowany: {args.output}")
            sys.exit(0)
            
        except Exception as e:
            print(f"Błąd podczas parsowania schematu: {e}")
            
            # Generuj prosty plik SVG z informacją o błędzie
            with open(args.output, 'w') as out:
                out.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
                out.write('<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">\n')
                out.write('<rect width="100%" height="100%" fill="white"/>\n')
                out.write(f'<text x="50" y="50" font-family="Arial" font-size="20" fill="black">Schemat: {os.path.basename(args.input)}</text>\n')
                out.write('<text x="50" y="80" font-family="Arial" font-size="16" fill="black">Nie można wygenerować podglądu schematu.</text>\n')
                out.write(f'<text x="50" y="110" font-family="Arial" font-size="16" fill="red">Błąd: {str(e)}</text>\n')
                out.write('</svg>\n')
            
            sys.exit(1)
    
    except Exception as e:
        print(f"Nieoczekiwany błąd: {e}")
        sys.exit(1)