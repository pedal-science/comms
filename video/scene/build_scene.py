"""Builds the teaser's scene: a dark basement, both pedals on a worn rug, a bare bulb on a cord, the
console's bar screen and a laptop showing the same rig, and one camera per shot (timeline.py).

  blender -b --factory-startup -P scene/build_scene.py -- [--stills F,F,...] [--out work/video.blend]

--stills renders those frames to work/stills/ after saving, for looking at; tools/render renders the
lot.

The pedals come from pedal.project/enclosure, appended from the two .blend files it builds
(console.blend for the Hammond console, pedal.blend for the 1590DD), so the video shows the models
as they are there. Everything else — the room, the light, the cameras — is made here.
"""
import math
import os
import random
import sys

import bpy
from mathutils import Euler, Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import timeline as TL  # noqa: E402

VIDEO = os.path.normpath(os.path.join(HERE, ".."))
WORK = os.path.join(VIDEO, "work")
WORKSPACE = os.path.normpath(os.path.join(VIDEO, "..", ".."))
ENCLOSURE = os.path.join(WORKSPACE, "pedal.project", "enclosure")
CONSOLE_BLEND = os.path.join(ENCLOSURE, "console.blend")
OLD_BLEND = os.path.join(ENCLOSURE, "pedal.blend")
PLATES = os.path.join(WORK, "plates")
MM = 0.001

random.seed(1990)


# ---- Small helpers ----------------------------------------------------------------------------

def collection(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    return c


def node(nt, kind, loc=(0, 0), **inputs):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in inputs.items():
        if k in n.inputs:
            n.inputs[k].default_value = v
        else:
            setattr(n, k, v)
    return n


def link(nt, a, b):
    nt.links.new(a, b)


def material(name, color=(0.5, 0.5, 0.5), rough=0.5, metal=0.0, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit is not None:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


def mesh_object(name, verts, faces, coll, mat=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(name, me)
    coll.objects.link(o)
    if mat:
        o.data.materials.append(mat)
    return o


def box(name, size, loc, coll, mat=None, rot=(0, 0, 0)):
    sx, sy, sz = (s / 2 for s in size)
    v = [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
         (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    o = mesh_object(name, v, f, coll, mat)
    o.location = loc
    o.rotation_euler = rot
    return o


def bevel(o, width, segments=3):
    m = o.modifiers.new("Bevel", "BEVEL")
    m.width = width
    m.segments = segments
    m.limit_method = "ANGLE"
    return m


def smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True


# ---- Materials for the room -------------------------------------------------------------------

def concrete():
    """A basement floor: grey concrete, darker where things have been spilt and dragged, with
    damp patches that catch the bulb."""
    m = bpy.data.materials.new("Concrete")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = node(nt, "ShaderNodeTexCoord", (-1400, 0))
    big = node(nt, "ShaderNodeTexNoise", (-1150, 300), Scale=1.2, Detail=6.0, Roughness=0.6)
    fine = node(nt, "ShaderNodeTexNoise", (-1150, 0), Scale=38.0, Detail=10.0, Roughness=0.7)
    stain = node(nt, "ShaderNodeTexVoronoi", (-1150, -300), Scale=2.6)
    for t in (big, fine, stain):
        link(nt, tc.outputs["Object"], t.inputs["Vector"])
    ramp = node(nt, "ShaderNodeValToRGB", (-850, 300))
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.055, 0.052, 0.048, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.16, 0.155, 0.145, 1)
    link(nt, big.outputs["Fac"], ramp.inputs["Fac"])
    mixf = node(nt, "ShaderNodeMix", (-600, 200), data_type="RGBA", blend_type="MULTIPLY")
    mixf.inputs[0].default_value = 0.55
    link(nt, ramp.outputs["Color"], mixf.inputs[6])
    link(nt, fine.outputs["Color"], mixf.inputs[7])
    st = node(nt, "ShaderNodeMapRange", (-850, -300), **{"From Min": 0.0, "From Max": 0.35})
    link(nt, stain.outputs["Distance"], st.inputs["Value"])
    darken = node(nt, "ShaderNodeMix", (-350, 100), data_type="RGBA", blend_type="MULTIPLY")
    link(nt, st.outputs["Result"], darken.inputs[0])
    link(nt, mixf.outputs[2], darken.inputs[6])
    darken.inputs[7].default_value = (0.45, 0.42, 0.38, 1)
    link(nt, darken.outputs[2], b.inputs["Base Color"])
    # Damp: smooth where the big noise is low.
    wet = node(nt, "ShaderNodeMapRange", (-600, -100), **{"From Min": 0.32, "From Max": 0.48,
                                                           "To Min": 0.18, "To Max": 0.85})
    link(nt, big.outputs["Fac"], wet.inputs["Value"])
    link(nt, wet.outputs["Result"], b.inputs["Roughness"])
    bump = node(nt, "ShaderNodeBump", (-300, -300), Strength=0.25, Distance=0.002)
    link(nt, fine.outputs["Fac"], bump.inputs["Height"])
    link(nt, bump.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Specular IOR Level"].default_value = 0.5
    return m


def rug_image():
    """The rug, painted by tools/make_textures.py, on a pile that drinks the light."""
    m = bpy.data.materials.new("Rug")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = node(nt, "ShaderNodeTexImage", (-500, 100))
    tex.image = bpy.data.images.load(os.path.join(WORK, "tex", "rug.png"))
    link(nt, tex.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.97
    b.inputs["Sheen Weight"].default_value = 0.5
    b.inputs["Sheen Roughness"].default_value = 0.6
    pile = node(nt, "ShaderNodeTexNoise", (-500, -250), Scale=1600.0, Detail=1.0)
    bump = node(nt, "ShaderNodeBump", (-250, -250), Strength=0.3, Distance=0.0015)
    link(nt, pile.outputs["Fac"], bump.inputs["Height"])
    knots = node(nt, "ShaderNodeTexImage", (-500, -500))
    knots.image = bpy.data.images.load(os.path.join(WORK, "tex", "rug_height.png"))
    knots.image.colorspace_settings.name = "Non-Color"
    bump2 = node(nt, "ShaderNodeBump", (-50, -350), Strength=0.6, Distance=0.002)
    link(nt, knots.outputs["Color"], bump2.inputs["Height"])
    link(nt, bump.outputs["Normal"], bump2.inputs["Normal"])
    link(nt, bump2.outputs["Normal"], b.inputs["Normal"])
    return m


def blocks():
    """Painted cinder block for the back wall: courses of 440 x 215 mm, mortar between."""
    m = bpy.data.materials.new("CinderBlock")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = node(nt, "ShaderNodeTexCoord", (-1200, 0))
    brick = node(nt, "ShaderNodeTexBrick", (-900, 0), Scale=1.0, **{"Mortar Size": 0.012,
                                                                     "Brick Width": 0.44,
                                                                     "Row Height": 0.215})
    brick.inputs["Color1"].default_value = (0.20, 0.205, 0.19, 1)
    brick.inputs["Color2"].default_value = (0.17, 0.175, 0.165, 1)
    brick.inputs["Mortar"].default_value = (0.09, 0.09, 0.085, 1)
    mapping = node(nt, "ShaderNodeMapping", (-1050, 0))
    mapping.inputs["Rotation"].default_value = (math.pi / 2, 0, 0)
    link(nt, tc.outputs["Object"], mapping.inputs["Vector"])
    link(nt, mapping.outputs["Vector"], brick.inputs["Vector"])
    grime = node(nt, "ShaderNodeTexNoise", (-900, -300), Scale=0.8, Detail=8.0)
    link(nt, tc.outputs["Object"], grime.inputs["Vector"])
    mul = node(nt, "ShaderNodeMix", (-500, 0), data_type="RGBA", blend_type="MULTIPLY")
    mul.inputs[0].default_value = 0.8
    link(nt, brick.outputs["Color"], mul.inputs[6])
    link(nt, grime.outputs["Color"], mul.inputs[7])
    link(nt, mul.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.9
    bump = node(nt, "ShaderNodeBump", (-300, -300), Strength=0.4)
    link(nt, brick.outputs["Fac"], bump.inputs["Height"])
    link(nt, bump.outputs["Normal"], b.inputs["Normal"])
    return m


def grille():
    """Amp grille cloth: a dark basket weave with a faint fleck."""
    m = bpy.data.materials.new("GrilleCloth")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = node(nt, "ShaderNodeTexCoord", (-900, 0))
    w = node(nt, "ShaderNodeTexWave", (-650, 0), Scale=180.0, Distortion=0.0, wave_type="BANDS")
    w2 = node(nt, "ShaderNodeTexWave", (-650, -250), Scale=180.0, bands_direction="Y")
    for t in (w, w2):
        link(nt, tc.outputs["UV"], t.inputs["Vector"])
    mx = node(nt, "ShaderNodeMix", (-400, 0), data_type="RGBA", blend_type="MULTIPLY")
    mx.inputs[0].default_value = 1.0
    link(nt, w.outputs["Color"], mx.inputs[6])
    link(nt, w2.outputs["Color"], mx.inputs[7])
    ramp = node(nt, "ShaderNodeValToRGB", (-200, 0))
    ramp.color_ramp.elements[0].color = (0.02, 0.02, 0.02, 1)
    ramp.color_ramp.elements[1].color = (0.12, 0.11, 0.09, 1)
    link(nt, mx.outputs[2], ramp.inputs["Fac"])
    link(nt, ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.9
    return m


# ---- The room ---------------------------------------------------------------------------------

def room():
    coll = collection("Room")
    floor = mesh_object("Floor", [(-12, -12, 0), (12, -12, 0), (12, 12, 0), (-12, 12, 0)], [(0, 1, 2, 3)],
                        coll, concrete())
    wall = mesh_object("BackWall", [(-8, 3.2, 0), (8, 3.2, 0), (8, 3.2, 4), (-8, 3.2, 4)], [(0, 3, 2, 1)],
                       coll, blocks())
    side = mesh_object("SideWall", [(-3.4, -6, 0), (-3.4, 6, 0), (-3.4, 6, 4), (-3.4, -6, 4)], [(0, 1, 2, 3)],
                       coll, blocks())
    # The rug, a little skew, with the pedals on it.
    rw, rd = 2.1, 1.45
    r = mesh_object("Rug", [(-rw / 2, -rd / 2, 0.004), (rw / 2, -rd / 2, 0.004), (rw / 2, rd / 2, 0.004),
                            (-rw / 2, rd / 2, 0.004)], [(0, 1, 2, 3)], coll, rug_image())
    uv = r.data.uv_layers.new()
    for i, loop in enumerate(r.data.loops):
        uv.data[i].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][loop.vertex_index]
    r.rotation_euler = (0, 0, math.radians(-4))
    r.location = (-0.05, 0.05, 0)
    # A cab and a head against the wall, mostly in the dark: a hint of the room's use.
    tolex = material("Tolex", (0.012, 0.012, 0.012), rough=0.55)
    piping = material("Piping", (0.5, 0.48, 0.42), rough=0.4)
    cab = box("AmpCab", (0.76, 0.36, 0.76), (1.35, 1.55, 0.38), coll, tolex, rot=(0, 0, math.radians(-18)))
    bevel(cab, 0.012)
    front = box("AmpGrille", (0.68, 0.01, 0.68), (0, -0.181, 0.0), coll, grille())
    front.parent = cab
    uvf = front.data.uv_layers.new()
    for i, loop in enumerate(front.data.loops):
        uvf.data[i].uv = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0), (1, 0), (1, 1), (0, 1)][loop.vertex_index]
    head = box("AmpHead", (0.74, 0.27, 0.27), (1.33, 1.58, 0.895), coll, tolex, rot=(0, 0, math.radians(-18)))
    bevel(head, 0.01)
    panel = box("AmpPanel", (0.66, 0.01, 0.11), (0, -0.137, 0.03), coll, material("AmpPanel", (0.03, 0.03, 0.03),
                                                                                  rough=0.35, metal=0.6))
    panel.parent = head
    lamp = mesh_object("AmpPilot", [], [], coll)
    lamp_mat = material("PilotRed", (0.8, 0.02, 0.01), emit=(1.0, 0.03, 0.0), strength=60.0)
    pilot = box("AmpPilotJewel", (0.012, 0.01, 0.012), (0.28, -0.142, 0.03), coll, lamp_mat)
    pilot.parent = head
    bpy.data.objects.remove(lamp)
    for k in range(5):
        kn = box(f"AmpKnob{k}", (0.018, 0.02, 0.018), (-0.22 + k * 0.09, -0.15, 0.03), coll,
                 material("ChickenHead", (0.01, 0.01, 0.01), rough=0.3))
        kn.parent = head
    # A flight case beside the rug with the laptop on it.
    case = box("FlightCase", (0.62, 0.42, 0.48), (-1.15, 0.55, 0.24), coll,
               material("CasePly", (0.02, 0.02, 0.022), rough=0.5), rot=(0, 0, math.radians(14)))
    bevel(case, 0.008)
    edges = material("CaseEdge", (0.55, 0.55, 0.56), rough=0.3, metal=1.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            c = box(f"CaseCorner{sx}{sy}", (0.04, 0.04, 0.485), (sx * 0.295, sy * 0.195, 0), coll, edges)
            c.parent = case
    return coll


def glass_material():
    """A clear envelope, unlit: the bulb's own light sits a few centimetres inside it and would
    blow any lit surface out. It is transparent, with a warm rim where the glass is seen edge on."""
    m = bpy.data.materials.new("BulbGlassClear")
    m.use_nodes = True
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = True     # the far side, seen from inside, would glow all over
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    out = nt.nodes["Material Output"]
    lw = node(nt, "ShaderNodeLayerWeight", (-700, 200), Blend=0.4)
    pw = node(nt, "ShaderNodeMath", (-500, 200), operation="POWER")
    pw.inputs[1].default_value = 2.0
    link(nt, lw.outputs["Facing"], pw.inputs[0])
    tr = node(nt, "ShaderNodeBsdfTransparent", (-300, 50))
    em = node(nt, "ShaderNodeEmission", (-300, -100), Strength=0.0)
    em.inputs["Color"].default_value = (1.0, 0.62, 0.32, 1)
    em.name = "GlassRim"
    mix = node(nt, "ShaderNodeMixShader", (-100, 0))
    link(nt, pw.outputs[0], mix.inputs[0])
    link(nt, tr.outputs[0], mix.inputs[1])
    link(nt, em.outputs[0], mix.inputs[2])
    link(nt, mix.outputs[0], out.inputs["Surface"])
    return m


def bulb(coll):
    """A bare clear-glass bulb on its flex, from a ceiling we never see: a glowing filament in a
    glass pear under a porcelain-pale socket. It swings. Returns the pivot, the light and the
    filament, whose glow is keyed with the light (lighting())."""
    pivot = bpy.data.objects.new("BulbPivot", None)
    pivot.location = BULB_PIVOT
    coll.objects.link(pivot)
    flex = bpy.data.curves.new("Flex", "CURVE")
    flex.dimensions = "3D"
    flex.bevel_depth = 0.0025
    sp = flex.splines.new("POLY")
    sp.points.add(1)
    sp.points[0].co = (0, 0, 0, 1)
    sp.points[1].co = (0, 0, -1.43, 1)
    fo = bpy.data.objects.new("Flex", flex)
    fo.data.materials.append(material("FlexBlack", (0.01, 0.01, 0.01), rough=0.6))
    coll.objects.link(fo)
    fo.parent = pivot
    bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=0.05, vertices=32, location=(0, 0, -1.455))
    socket = bpy.context.active_object
    socket.name = "BulbSocket"
    socket.data.materials.append(material("Bakelite", (0.012, 0.009, 0.007), rough=0.45))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.013, depth=0.016, vertices=32, location=(0, 0, -1.486))
    cap = bpy.context.active_object
    cap.name = "BulbCap"
    cap.data.materials.append(material("BulbBrass", (0.5, 0.36, 0.16), rough=0.35, metal=1.0))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(0, 0, -1.528), segments=48, ring_count=24)
    glass = bpy.context.active_object
    glass.name = "BulbGlass"
    glass.scale = (1, 1, 1.3)
    glass.data.materials.append(glass_material())
    for o in (socket, cap, glass):
        smooth(o)
        for c in o.users_collection:
            c.objects.unlink(o)
        coll.objects.link(o)
        o.parent = pivot
        o.visible_shadow = False
    # The filament: a squiggle of hot wire on two supports.
    fil = bpy.data.curves.new("Filament", "CURVE")
    fil.dimensions = "3D"
    fil.bevel_depth = 0.0007
    fsp = fil.splines.new("POLY")
    pts = []
    for i in range(41):
        u = i / 40
        x = -0.012 + 0.024 * u
        pts.append((x, 0.0015 * math.sin(u * math.pi * 14), -1.53 + 0.004 * math.sin(u * math.pi) - 0.0006 * math.cos(u * math.pi * 14)))
    fsp.points.add(len(pts) - 1)
    for p, co in zip(fsp.points, pts):
        p.co = (*co, 1)
    fil_o = bpy.data.objects.new("Filament", fil)
    fil_mat = material("FilamentHot", (1.0, 0.5, 0.2), emit=(1.0, 0.45, 0.12), strength=400.0)
    fil_o.data.materials.append(fil_mat)
    coll.objects.link(fil_o)
    fil_o.parent = pivot
    fil_o.visible_shadow = False
    wires = bpy.data.curves.new("Supports", "CURVE")
    wires.dimensions = "3D"
    wires.bevel_depth = 0.0004
    for x in (-0.012, 0.012):
        w = wires.splines.new("POLY")
        w.points.add(1)
        w.points[0].co = (x * 0.4, 0, -1.495, 1)
        w.points[1].co = (x, 0, -1.53, 1)
    wo = bpy.data.objects.new("Supports", wires)
    wo.data.materials.append(material("SupportWire", (0.4, 0.4, 0.4), rough=0.3, metal=1.0))
    coll.objects.link(wo)
    wo.parent = pivot
    wo.visible_shadow = False
    light = bpy.data.lights.new("Bulb", "POINT")
    light.energy = 40.0
    light.color = (1.0, 0.6, 0.3)
    light.shadow_soft_size = 0.012
    light.volume_factor = 0.35       # a halo in the haze, not a fog bank
    light.specular_factor = 0.3      # a sheen on the screen glass, not a hole in it
    lo = bpy.data.objects.new("Bulb", light)
    lo.location = (0, 0, -1.53)
    coll.objects.link(lo)
    lo.parent = pivot
    # The swing: a slow pendulum that dies away, with a second, smaller sway across it.
    for f in range(0, TL.FRAMES + 1, 2):
        t = f / TL.FPS
        a = math.radians(9.0) * math.sin(2 * math.pi * t / 2.9) * (0.75 + 0.25 * math.cos(t / 7))
        b2 = math.radians(4.0) * math.sin(2 * math.pi * t / 3.7 + 1.2)
        pivot.rotation_euler = (a, b2, 0)
        pivot.keyframe_insert("rotation_euler", frame=f)
    return pivot, lo, fil_o


def haze(coll):
    """A cube of thin smoke over the set, so the bulb has a beam to cut."""
    o = box("Haze", (9, 9, 4), (0, 0, 2), coll)
    m = bpy.data.materials.new("Haze")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    out = nt.nodes["Material Output"]
    vol = node(nt, "ShaderNodeVolumePrincipled", (-300, 0))
    vol.inputs["Density"].default_value = 0.02
    vol.inputs["Anisotropy"].default_value = 0.55
    vol.inputs["Color"].default_value = (0.8, 0.8, 0.82, 1)
    noise = node(nt, "ShaderNodeTexNoise", (-700, 0), Scale=0.6, Detail=3.0)
    dens = node(nt, "ShaderNodeMapRange", (-500, 0), **{"To Min": 0.006, "To Max": 0.03})
    link(nt, noise.outputs["Fac"], dens.inputs["Value"])
    link(nt, dens.outputs["Result"], vol.inputs["Density"])
    link(nt, vol.outputs["Volume"], out.inputs["Volume"])
    o.data.materials.append(m)
    return o


# ---- More of the room: the window, the tube, the laptop, the cables ---------------------------

def window(coll):
    """A high window on the left wall with its blinds half shut. A cold streetlight comes through
    them, and the haze turns the gaps into beams."""
    # The left wall, with a hole for the window: four panels around it.
    wall = bpy.data.objects["SideWall"]
    bpy.data.objects.remove(wall)
    mat = bpy.data.materials["CinderBlock"]
    x = -3.4
    y0, y1, z0, z1 = -0.3, 1.3, 1.25, 2.35
    for name, (ya, yb, za, zb) in {"Below": (-6, 6, 0, z0), "Above": (-6, 6, z1, 4),
                                   "Left": (-6, y0, z0, z1), "Right": (y1, 6, z0, z1)}.items():
        mesh_object("SideWall" + name, [(x, ya, za), (x, yb, za), (x, yb, zb), (x, ya, zb)], [(0, 1, 2, 3)],
                    coll, mat)
    slat_mat = material("Blind", (0.35, 0.34, 0.31), rough=0.5)
    n = 22
    for i in range(n):
        z = z0 + (i + 0.5) * (z1 - z0) / n
        s = box(f"Slat{i:02d}", (0.004, y1 - y0, 0.042), (x + 0.03, (y0 + y1) / 2, z), coll, slat_mat,
                rot=(0, math.radians(70), 0))
        s.visible_camera = True
    spot = bpy.data.lights.new("Streetlight", "SPOT")
    spot.energy = 1400.0
    spot.color = (0.55, 0.78, 1.0)
    spot.spot_size = math.radians(20)
    spot.spot_blend = 0.3
    spot.shadow_soft_size = 0.002
    o = bpy.data.objects.new("Streetlight", spot)
    o.location = (-6.2, 0.9, 3.4)
    d = (Vector((-0.1, 0.1, 0.0)) - o.location).normalized()
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    coll.objects.link(o)
    return o


def tube(coll):
    """A fluorescent tube on the back wall, cold and not quite right."""
    m = material("TubeGlow", (0.8, 0.9, 0.85), emit=(0.7, 1.0, 0.85), strength=6.0)
    t = box("Tube", (1.2, 0.03, 0.03), (-0.6, 3.17, 2.45), coll, m)
    bevel(t, 0.012, 4)
    lt = bpy.data.lights.new("TubeLight", "AREA")
    lt.shape = "RECTANGLE"
    lt.size, lt.size_y = 1.2, 0.05
    lt.energy = 40.0
    lt.color = (0.7, 1.0, 0.85)
    lo = bpy.data.objects.new("TubeLight", lt)
    lo.location = (-0.6, 3.1, 2.42)
    lo.rotation_euler = (math.radians(105), 0, 0)
    coll.objects.link(lo)
    # It stutters now and then.
    emit = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    rng = random.Random(4)
    for f in range(0, TL.FRAMES, 3):
        on = rng.random() > 0.12
        emit.default_value = 6.0 if on else 0.4
        emit.keyframe_insert("default_value", frame=f)
        lt.energy = 40.0 if on else 3.0
        lt.keyframe_insert("energy", frame=f)
    return t


BULB_PIVOT = (0.45, -0.1, 2.6)    # front right of the console, so its reflection misses the screen
LAPTOP_SCREEN_CENTER = None
LAPTOP_SCREEN_NORMAL = None


def laptop(coll):
    """An old laptop on the flight case, lid up, running ljoss: the same rig as the pedal."""
    global LAPTOP_SCREEN_CENTER, LAPTOP_SCREEN_NORMAL
    case = bpy.data.objects["FlightCase"]
    alu = material("LaptopShell", (0.018, 0.018, 0.02), rough=0.55)
    keys = material("LaptopKeys", (0.008, 0.008, 0.009), rough=0.6)
    w, d = 0.33, 0.23
    top = case.matrix_world @ Vector((0, 0, 0.245))
    rot = case.rotation_euler.z + math.radians(-28)
    base_m = Matrix.Translation(top + Vector((0.02, -0.03, 0.0))) @ Matrix.Rotation(rot, 4, "Z")
    base = box("LaptopBase", (w, d, 0.016), (0, 0, 0.008), coll, alu)
    base.matrix_world = base_m @ Matrix.Translation((0, 0, 0.008))
    bevel(base, 0.004)
    kb = box("LaptopKeys", (w * 0.86, d * 0.42, 0.001), (0, 0, 0), coll, keys)
    kb.matrix_world = base_m @ Matrix.Translation((0, 0.025, 0.0165))
    hinge = base_m @ Matrix.Translation((0, d / 2, 0.016)) @ Matrix.Rotation(math.radians(-18), 4, "X")
    lid = box("LaptopLid", (w, 0.008, d - 0.01), (0, 0, 0), coll, alu)
    lid.matrix_world = hinge @ Matrix.Translation((0, 0.004, (d - 0.01) / 2))
    bevel(lid, 0.003)
    # The panel: 16:10, a hair in front of the lid.
    sw, sh = w * 0.9, (w * 0.9) * 10 / 16
    m = bpy.data.materials.new("LaptopScreen")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0, 0, 0, 1)
    b.inputs["Roughness"].default_value = 0.15
    b.inputs["Coat Weight"].default_value = 0.2
    tex = node(nt, "ShaderNodeTexImage", (-500, 0))
    sequence(tex, os.path.join(PLATES, "laptop"))
    link(nt, tex.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 1.0
    panel = mesh_object("LaptopScreen", [(-sw / 2, 0, -sh / 2), (sw / 2, 0, -sh / 2), (sw / 2, 0, sh / 2),
                                         (-sw / 2, 0, sh / 2)], [(0, 1, 2, 3)], coll, m)
    uv = panel.data.uv_layers.new()
    for i, loop in enumerate(panel.data.loops):
        uv.data[i].uv = [(0, 0), (1, 0), (1, 1), (0, 1)][loop.vertex_index]
    panel.matrix_world = hinge @ Matrix.Translation((0, -0.0005, (d - 0.01) / 2 + 0.008))
    LAPTOP_SCREEN_CENTER = panel.matrix_world.translation.copy()
    LAPTOP_SCREEN_NORMAL = (panel.matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()
    glow = bpy.data.lights.new("LaptopGlow", "AREA")
    glow.size, glow.shape = 0.3, "SQUARE"
    glow.energy = 2.0
    glow.color = (0.75, 0.82, 1.0)
    go = bpy.data.objects.new("LaptopGlow", glow)
    go.location = LAPTOP_SCREEN_CENTER + LAPTOP_SCREEN_NORMAL * 0.05
    go.rotation_euler = LAPTOP_SCREEN_NORMAL.to_track_quat("-Z", "Y").to_euler()     # it shines outward
    coll.objects.link(go)
    return panel


def sequence(tex, folder):
    """An image node showing folder/NNNN.png on frame NNNN (numbered from 0)."""
    img = bpy.data.images.load(os.path.join(folder, "0000.png"))
    img.source = "SEQUENCE"
    tex.image = img
    u = tex.image_user
    u.frame_duration = TL.FRAMES
    u.frame_start = 0
    u.frame_offset = -1           # measured: with 0, frame f shows file f + 1
    u.use_auto_refresh = True
    tex.interpolation = "Cubic"


def cable(name, points, coll, radius=0.0035, mat=None):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 3
    cu.resolution_u = 24
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(points) - 1)
    for p, co in zip(sp.bezier_points, points):
        p.co = co
        p.handle_left_type = p.handle_right_type = "AUTO"
    o = bpy.data.objects.new(name, cu)
    o.data.materials.append(mat or bpy.data.materials["CableRubber"])
    coll.objects.link(o)
    return o


def plug(name, at, direction, coll):
    """A straight 1/4-inch plug sitting in a jack: a nickel barrel and a black boot."""
    nickel = bpy.data.materials.get("PlugNickel") or material("PlugNickel", (0.6, 0.6, 0.58), rough=0.25, metal=1.0)
    boot = bpy.data.materials["CableRubber"]
    q = direction.to_track_quat("Z", "Y")
    parts = []
    for i, (r, l0, l1, m) in enumerate(((0.0062, 0.0, 0.018, nickel), (0.0075, 0.018, 0.075, boot))):
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=l1 - l0, vertices=24)
        c = bpy.context.active_object
        c.name = f"{name}_{i}"
        for uc in c.users_collection:
            uc.objects.unlink(c)
        coll.objects.link(c)
        c.data.materials.append(m)
        c.location = at + direction * ((l0 + l1) / 2)
        c.rotation_mode = "QUATERNION"
        c.rotation_quaternion = q
        smooth(c)
        parts.append(c)
    return at + direction * 0.075


def cables(coll):
    material("CableRubber", (0.006, 0.006, 0.006), rough=0.45)
    out_dir = (CONSOLE_AT.to_3x3() @ Vector((0, 1, 0))).normalized()
    # Guitar in, from the floor behind the pedal.
    jack = console_point(401, 218.7, 32)
    end = plug("PlugGuitar", jack, out_dir, coll)
    cable("CableGuitar", [end, end + out_dir * 0.06 + Vector((0, 0, -0.02)), Vector((0.62, 0.42, 0.008)),
                          Vector((0.85, 0.85, 0.008)), Vector((0.7, 1.35, 0.008)), Vector((1.05, 2.4, 0.008))], coll)
    # Out L and R, to the amp.
    for i, x in enumerate((273, 307)):
        jack = console_point(x, 218.7, 32)
        end = plug(f"PlugOut{i}", jack, out_dir, coll)
        cable(f"CableOut{i}", [end, end + out_dir * 0.07 + Vector((0, 0, -0.02)),
                               Vector((0.25 + 0.04 * i, 0.55, 0.008)), Vector((0.75 + 0.05 * i, 0.95, 0.008)),
                               Vector((1.18 + 0.06 * i, 1.32, 0.01)), Vector((1.25 + 0.06 * i, 1.38, 0.2))], coll)
    # Power: USB-C away to the left.
    jack = console_point(62, 218.7, 32)
    cable("CablePower", [jack + out_dir * 0.03, jack + out_dir * 0.09 + Vector((0, 0, -0.02)),
                         Vector((-0.35, 0.55, 0.008)), Vector((-0.9, 0.9, 0.008)), Vector((-1.9, 1.4, 0.008))],
          coll, radius=0.0022)
    # A patch lead from the old pedal, coiled loose on the rug.
    a = old_point(188, 70, 18)
    cable("CableOld", [a, a + Vector((0.06, 0.0, -0.01)), Vector((-0.17, -0.3, 0.008)), Vector((-0.08, -0.47, 0.008)),
                       Vector((-0.3, -0.58, 0.008)), Vector((-0.5, -0.42, 0.008))], coll, radius=0.003)


# ---- The pedals -------------------------------------------------------------------------------

def append_collections(blend, names):
    with bpy.data.libraries.load(blend, link=False) as (src, dst):
        dst.collections = [n for n in names if n in src.collections]
    return {c.name: c for c in dst.collections if c}


def instance(name, coll, parent_coll, matrix):
    e = bpy.data.objects.new(name, None)
    e.instance_type = "COLLECTION"
    e.instance_collection = coll
    e.matrix_world = matrix
    parent_coll.objects.link(e)
    return e


CONSOLE_AT = Matrix.Translation((0.08, 0.02, 0.004)) @ Matrix.Rotation(math.radians(-7), 4, "Z")
OLD_AT = Matrix.Translation((-0.38, -0.15, 0.004)) @ Matrix.Rotation(math.radians(11), 4, "Z")
CONSOLE_OFF = Vector((217.41, 109.335, -5.5))
OLD_OFF = Vector((94.0, 59.5, -3.2))


def console_point(x, y, z):
    """A point in console.py's frame (mm) to the world."""
    return CONSOLE_AT @ ((Vector((x, y, z)) - CONSOLE_OFF) * MM)


def old_point(x, y, z):
    """A point in the old model's layout frame (mm) to the world."""
    return OLD_AT @ ((Vector((x, y, z)) - OLD_OFF) * MM)


def split_by_material(obj, prefix, name):
    """Split the faces using a material whose name starts with `prefix` into their own object,
    beside the original and in its collections. Returns the new object."""
    import bmesh
    want = {i for i, s in enumerate(obj.material_slots) if s.material and s.material.name.startswith(prefix)}
    if not want:
        return None
    part = obj.copy()
    part.data = obj.data.copy()
    part.name = name
    for c in obj.users_collection:
        c.objects.link(part)

    def keep(me, matching):
        bm = bmesh.new()
        bm.from_mesh(me)
        gone = [f for f in bm.faces if (f.material_index in want) != matching]
        bmesh.ops.delete(bm, geom=gone, context="FACES")
        bm.to_mesh(me)
        bm.free()
    keep(part.data, True)
    keep(obj.data, False)
    return part


def key_linear(obj):
    if obj.animation_data and obj.animation_data.action:
        for fc in fcurves_of(obj.animation_data.action):
            for k in fc.keyframe_points:
                k.interpolation = "LINEAR"


def fcurves_of(action):
    """F-curves of an action, across the layered-action API (Blender 4.4+) and the old one."""
    if hasattr(action, "fcurves") and len(getattr(action, "fcurves", [])):
        return list(action.fcurves)
    out = []
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            for bag in getattr(strip, "channelbags", []):
                out.extend(bag.fcurves)
    return out


def press(cap, frames, depth):
    """Footswitch presses: down in a frame, held, back up. Along the cap's own -Z, in the
    collection's millimetres."""
    rest = cap.location.copy()
    axis = cap.matrix_basis.to_3x3() @ Vector((0, 0, -1))
    keys = {}
    for f in frames:
        for df, k in ((-1, 0.0), (1, 1.0), (4, 1.0), (7, 0.0)):
            keys[f + df] = max(keys.get(f + df, 0.0), k)
    for f in sorted(keys):
        cap.location = rest + axis * depth * keys[f]
        cap.keyframe_insert("location", frame=f)
    cap.location = rest
    key_linear(cap)


def turn(knob, start, end, degrees):
    """Turn a knob about its own axis between two frames."""
    knob.rotation_mode = "QUATERNION"
    q0 = knob.matrix_basis.to_quaternion()
    for f, a in ((start, 0.0), (end, degrees)):
        knob.rotation_quaternion = q0 @ Euler((0, 0, math.radians(a))).to_quaternion()
        knob.keyframe_insert("rotation_quaternion", frame=f)


def pedals():
    src = append_collections(CONSOLE_BLEND, ["Console_Case", "Console_Cover", "Console_Screen", "Console_Inside"])
    old = append_collections(OLD_BLEND, ["Pedal_Closed"])
    # The old model's labels name their font by a relative path that was right where pedal.blend was
    # first built and is not now: find the font by its file name instead.
    for font in bpy.data.fonts:
        if font.filepath.startswith("<") or os.path.exists(bpy.path.abspath(font.filepath)):
            continue
        name = os.path.basename(font.filepath)
        for d in ("/System/Library/Fonts/Supplemental", "/System/Library/Fonts", "/Library/Fonts",
                  os.path.expanduser("~/Library/Fonts")):
            if os.path.exists(os.path.join(d, name)):
                font.filepath = os.path.join(d, name)
                break
        else:
            print("WARNING: no font", name, "- the old pedal's labels fall back to Blender's own")
    hold = collection("PedalSources")
    for c in list(src.values()) + list(old.values()):
        hold.children.link(c)
    bpy.context.view_layer.layer_collection.children["PedalSources"].exclude = True
    scene_coll = collection("Pedals")
    scale = Matrix.Scale(MM, 4)
    inst = {}
    for k, c in src.items():
        inst[k] = instance("I_" + k, c, scene_coll, CONSOLE_AT @ scale)
    inst["Old"] = instance("I_Old", old["Pedal_Closed"], scene_coll, OLD_AT @ scale)

    # The console's footswitches: the chrome caps move.
    by_switch = {}
    for n in ("1", "2", "3", "4", "5", "Tuner"):
        fs = bpy.data.objects[f"Footswitch_{n}"]
        by_switch["T" if n == "Tuner" else int(n)] = split_by_material(fs, "Chrome", f"FootswitchCap_{n}")
    for sw, cap in by_switch.items():
        frames = [f for f, s in TL.PRESSES if s == sw]
        if frames:
            press(cap, frames, 3.2)

    # The old pedal's footswitches, and the LED above B answering its press.
    for n in ("A", "B", "C"):
        fs = bpy.data.objects.get(f"Footswitch_{n}")
        cap = split_by_material(fs, "Chrome", f"OldCap_{n}") if fs else None
        frames = [f for f, s in TL.OLD_PRESSES if s == n]
        if cap and frames:
            press(cap, frames, 3.0)
    # LED_2 is modelled off: it gets a copy of the lit green, dark until B's press lands.
    led, lit = bpy.data.objects.get("LED_2"), bpy.data.materials.get("LED_green_on")
    if led and lit:
        m = lit.copy()
        m.name = "LED_2_switching"
        for slot in led.material_slots:
            if slot.material and slot.material.name.startswith("LED_green_off"):
                slot.material = m
        s = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
        on = s.default_value
        for f, v in ((0, 0.0), (TL.OLD_LED_ON - 1, 0.0), (TL.OLD_LED_ON, on), (TL.FRAMES - 1, on)):
            s.default_value = v
            s.keyframe_insert("default_value", frame=f)
        for fc in fcurves_of(m.node_tree.animation_data.action):
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"
    # Its screen sits under an acrylic window, which EEVEE refracts from the world (black) unless it
    # traces what is behind it.
    acrylic = bpy.data.materials.get("Acrylic")
    if acrylic:
        acrylic.use_raytrace_refraction = True

    # The bar screen plays the plates.
    m = bpy.data.materials["BarScreen"]
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = next((n for n in nt.nodes if n.type == "TEX_IMAGE"), None) or node(nt, "ShaderNodeTexImage", (-500, 0))
    sequence(tex, os.path.join(PLATES, "bar"))
    link(nt, tex.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 2.0
    b.inputs["Coat Weight"].default_value = 0.5
    b.inputs["Coat Roughness"].default_value = 0.12
    b.inputs["Roughness"].default_value = 0.3

    # The lid comes off for the look inside.
    for f0, f1 in (TL.span("inside"),):
        for k in ("Console_Cover", "Console_Screen"):
            e = inst[k]
            for f, v in ((f0 - 1, False), (f0, True), (f1, True), (f1 + 1, False)):
                e.hide_render = v
                e.keyframe_insert("hide_render", frame=f)
    return inst


# ---- Light ------------------------------------------------------------------------------------

def area(name, coll, loc, target, size, energy, color=(1, 1, 1), shape="SQUARE", size_y=None):
    lt = bpy.data.lights.new(name, "AREA")
    lt.shape = shape
    lt.size = size
    if size_y:
        lt.size_y = size_y
    lt.energy = energy
    lt.color = color
    o = bpy.data.objects.new(name, lt)
    o.location = loc
    d = (Vector(target) - Vector(loc)).normalized()
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    coll.objects.link(o)
    return o


def key_energy(light, keys, constant=False):
    for f, v in keys:
        light.energy = v
        light.keyframe_insert("energy", frame=f)
    if constant and light.animation_data:
        for fc in fcurves_of(light.animation_data.action):
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"


def lighting(coll, bulb_light, filament):
    centre = console_point(217, 109, 40)
    # A black box in a dark room is drawn by its edges. A cool rim from behind and above, from the
    # window's side; a warm kicker low behind the right end, raking the top. Both are narrow, so they
    # light the case and not the rug or the haze.
    rim = area("Rim", coll, centre + Vector((-0.7, 1.0, 0.75)), centre, 0.2, 20.0, (0.55, 0.75, 1.0))
    rim.data.spread = math.radians(50)
    rim.data.volume_factor = 0.2
    kick = area("Kicker", coll, console_point(217 + 520, 218 + 380, 140), console_point(217, 120, 70), 0.06, 6.0,
                (1.0, 0.5, 0.2))
    kick.data.spread = math.radians(30)
    kick.data.volume_factor = 0.0
    # The screen lights what is in front of it.
    sc = console_point(217, 104, 69)
    sn = (console_point(217, 104 - 100 * math.sin(math.radians(15)), 69 + 100 * math.cos(math.radians(15))) - sc).normalized()
    glow = area("ScreenGlow", coll, sc + sn * 0.01, sc + sn, 0.2, 0.0, (0.85, 0.7, 0.55), shape="RECTANGLE", size_y=0.05)
    g = 1.5
    b0 = TL.BOOT
    keys = [(0, 0.0), (b0, 0.0), (b0 + 1, 2.0 * g), (b0 + 2, 0.15 * g), (b0 + 5, 0.8 * g), (b0 + 8, g)]
    for f0, f1 in (TL.span("inside"),):
        keys += [(f0 - 1, g), (f0, 0.0), (f1, 0.0), (f1 + 1, g)]
    key_energy(glow.data, keys, constant=True)
    # Red, low and raking, for the look inside.
    rake = area("RedRake", coll, console_point(-120, 140, 70), console_point(250, 140, 10), 0.12, 0.0,
                (1.0, 0.08, 0.03))
    keys = [(0, 0.0)]
    for f0, f1 in (TL.span("inside"),):
        keys += [(f0 - 1, 0.0), (f0, 45.0), (f1, 45.0), (f1 + 1, 0.0)]
    key_energy(rake.data, keys, constant=True)
    # The strobe, on the beat and on every stomp from "loud" on: a hard, narrow head from the
    # front, so it hits the pedal and the rug round it and the room stays dark.
    strobe = area("Strobe", coll, centre + Vector((-0.3, -1.2, 0.9)), centre, 0.15, 0.0, (0.95, 0.97, 1.0))
    strobe.data.spread = math.radians(45)
    strobe.data.volume_factor = 0.5
    keys = [(0, 0.0)]
    loud = TL.span("stomp")[0]
    flashes = set(TL.STROBE) | {f for f, _ in TL.PRESSES if f >= loud} | {f + 1 for f, _ in TL.PRESSES if f >= loud}
    for f in range(loud - 4, TL.FRAMES):
        keys.append((f, 160.0 if f in flashes else 0.0))
    key_energy(strobe.data, keys, constant=True)
    # The bulb: dark, a flicker, on; dimmed under the strobe; dying at the end.
    B = 40.0
    (i0, i1), (s0, s1), (e0, _) = TL.span("inside"), TL.span("strobe"), TL.span("end")
    d = e0 + 12                         # it starts to die a beat into the last shot
    e_bulb = [(0, 0.0), (5, 0.0), (6, B), (7, 0.0), (9, 0.0), (10, B * 1.3), (11, B * 0.3), (13, B),
              (15, B), (i0 - 1, B), (i0, B * 0.25), (i1, B * 0.25), (i1 + 1, B), (s0 - 1, B), (s0, B * 0.25),
              (s1, B * 0.25), (s1 + 1, B), (d, B), (d + 6, B * 0.3), (d + 7, B * 0.8), (d + 10, B * 0.1),
              (d + 14, B * 0.45), (d + 18, 0.0), (TL.FRAMES - 1, 0.0)]
    key_energy(bulb_light.data, e_bulb, constant=True)
    s = filament.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for f, v in e_bulb:
        s.default_value = v * 10.0
        s.keyframe_insert("default_value", frame=f)
    rim_e = bpy.data.materials["BulbGlassClear"].node_tree.nodes["GlassRim"].inputs["Strength"]
    for f, v in e_bulb:
        rim_e.default_value = v * 0.08
        rim_e.keyframe_insert("default_value", frame=f)
    for mat in (filament.data.materials[0], bpy.data.materials["BulbGlassClear"]):
        for fc in fcurves_of(mat.node_tree.animation_data.action):
            for k in fc.keyframe_points:
                k.interpolation = "CONSTANT"
    return rim


# ---- Cameras ----------------------------------------------------------------------------------

def bulb_position(frame):
    t = frame / TL.FPS
    a = math.radians(9.0) * math.sin(2 * math.pi * t / 2.9) * (0.75 + 0.25 * math.cos(t / 7))
    b2 = math.radians(4.0) * math.sin(2 * math.pi * t / 3.7 + 1.2)
    return Vector(BULB_PIVOT) + Euler((a, b2, 0)).to_matrix() @ Vector((0, 0, -1.53))


def ease(t):
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def smooth_noise(seed, t, freq):
    """Smooth 1D noise in [-1, 1]: a few sines with random phases."""
    r = random.Random(seed)
    return sum(math.sin(2 * math.pi * (freq * (k + 1) * 0.7) * t + r.random() * 6.28) / (k + 1)
               for k in range(3)) / 1.83


C = console_point
O = old_point


def shots():
    """Each shot: lens, f-stop, shake, and a pose(t) for t in [0, 1] -> (position, target, roll,
    focus distance or None)."""
    S = {}

    def fixed(p0, p1, t0, t1, roll=0.0, roll1=None):
        return lambda t: (lerp(p0, p1, ease(t)), lerp(t0, t1, ease(t)), lerp(roll, roll if roll1 is None else roll1, t),
                          None)

    def bulb_pose(t):
        f = t * (TL.span("bulb")[1] - TL.span("bulb")[0])
        tgt = bulb_position(f)
        return (Vector(BULB_PIVOT) + Vector((0.25, -0.54, -1.63)) + Vector((0.0, 0.03, 0.0)) * t, tgt, 0.0, None)
    S["bulb"] = dict(lens=85, fstop=1.8, shake=0.6, pose=bulb_pose)
    S["floor"] = dict(lens=18, fstop=2.0, shake=0.5,
                      pose=fixed(Vector((1.05, 1.25, 0.05)), Vector((0.66, 0.68, 0.06)),
                                 Vector((0.35, 0.3, 0.04)), C(380, 250, 25), roll=-4, roll1=-2))
    S["wake"] = dict(lens=35, fstop=2.2, shake=0.4,
                     pose=fixed(C(-300, -720, 420), C(-190, -560, 330), C(217, 100, 50), C(217, 100, 55)))
    S["press1"] = dict(lens=85, fstop=6.3, shake=0.5, focus_bias=-0.006,
                       pose=fixed(C(262, -118, 36), C(244, -100, 40), C(217.4, 34.8, 60), C(217.4, 34.8, 58), roll=3))
    S["flick1"] = dict(lens=50, fstop=5.6, shake=0.6,
                       pose=fixed(C(20, -20, 235), C(55, -12, 215), C(270, 104, 69), C(255, 104, 69), roll=-9, roll1=-7))
    # Switch 2, low from the front left, rim-lit against the screen behind it.
    S["press2"] = dict(lens=65, fstop=8.0, shake=0.6, focus_bias=-0.006,
                       pose=fixed(C(100, -110, 44), C(110, -100, 46), C(137.4, 34.8, 62), C(137.4, 34.8, 62), roll=-4))
    S["flick2"] = dict(lens=85, fstop=11.0, shake=0.5,
                       pose=fixed(C(217, -150, 255), C(205, -136, 248), C(217, 104, 69), C(214, 104, 69), roll=2))

    def whip(t):
        k = ease(min(1.0, max(0.0, (t - 0.2) / 0.25)))
        tgt = lerp(C(137, 35, 55), C(378, 112, 82), k)
        return (lerp(C(310, -270, 205), C(320, -255, 200), t), tgt, lerp(-4, 5, k), None)
    S["whip"] = dict(lens=50, fstop=2.2, shake=0.5, pose=whip)

    # Switch 3 sharp low in the frame, the screen soft above it; then the focus pulls to the screen.
    def rack(t):
        pos = lerp(C(225, -95, 118), C(222, -86, 113), ease(t))
        near = (C(217.4, 34.8, 62) - pos).length - 0.006
        far = (C(217, 104, 69) - pos).length
        k = ease(min(1.0, max(0.0, (t - 0.25) / 0.4)))
        return (pos, C(217, 66, 60), 4.0, lerp(near, far, k))
    S["rack"] = dict(lens=65, fstop=1.4, shake=0.3, pose=rack)
    S["touch"] = dict(lens=50, fstop=4.0, shake=0.25,
                      pose=fixed(C(212, -75, 240), C(220, -52, 218), C(238, 104, 69), C(242, 104, 69), roll=-2, roll1=1))

    def laptop_shot(t):
        c, n = LAPTOP_SCREEN_CENTER, LAPTOP_SCREEN_NORMAL
        side = n.cross(Vector((0, 0, 1))).normalized()
        p0 = c + n * 0.85 + side * 0.25 + Vector((0, 0, -0.18))
        p1 = c + n * 0.62 + side * 0.16 + Vector((0, 0, -0.14))
        return (lerp(p0, p1, ease(t)), c + Vector((0, 0, -0.01)), 3.0, None)
    S["laptop"] = dict(lens=50, fstop=2.0, shake=0.35, pose=laptop_shot)

    # A slow drift along the screen, so the touch in the middle of it is not smeared.
    def bar_shot(t):
        x = lerp(165, 300, t)
        return (C(x, -85, 215), C(x + 15, 104, 69), 0.0, None)
    S["bar"] = dict(lens=40, fstop=5.6, shake=0.25, pose=bar_shot)

    def monitor(t):
        c, n = LAPTOP_SCREEN_CENTER, LAPTOP_SCREEN_NORMAL
        side = n.cross(Vector((0, 0, 1))).normalized()
        p = c + n * lerp(0.36, 0.3, ease(t)) + side * 0.05
        return (p, c + side * 0.02, -6.0, None)
    S["monitor"] = dict(lens=50, fstop=2.8, shake=0.45, pose=monitor)
    # Both pedals side by side, low across the rug, the camera drifting in: the old box on the left.
    oc, cc = O(94, 59.5, 0), C(217.4, 109.3, 0)
    mid = (oc + cc) / 2
    along = (cc - oc).normalized()
    front = Vector((along.y, -along.x, 0.0))
    S["both"] = dict(lens=35, fstop=4.0, shake=0.3,
                     pose=fixed(mid + front * 1.1 + along * 0.02 + Vector((0, 0, 0.3)),
                                mid + front * 0.95 + along * 0.1 + Vector((0, 0, 0.25)),
                                mid + along * 0.07 + Vector((0, 0, 0.02)), mid + along * 0.08 + Vector((0, 0, 0.02)),
                                roll=-2))
    # The old box from the front left and a little above: its orange top, the three switches, B
    # going down and its LED coming on, the little screen behind.
    S["old"] = dict(lens=50, fstop=8.0, shake=0.4,
                    pose=fixed(O(-60, -130, 140), O(-40, -115, 128), O(94, 33, 45), O(94, 35, 45), roll=4))
    S["inside"] = dict(lens=45, fstop=1.8, shake=0.25,
                       pose=fixed(C(110, 40, 175), C(160, 80, 125), C(200, 160, 10), C(215, 140, 10)))
    S["rear"] = dict(lens=40, fstop=2.2, shake=0.3,
                     pose=fixed(C(560, 520, 70), C(500, 470, 60), C(300, 218, 32), C(290, 218, 32), roll=3))
    S["stomp"] = dict(lens=65, fstop=8.0, shake=1.6, focus_bias=-0.006,
                      pose=fixed(C(232, -82, 30), C(228, -76, 31), C(217.4, 34.8, 60), C(217.4, 34.8, 60), roll=-6))
    S["strobe"] = dict(lens=35, fstop=2.5, shake=1.2,
                       pose=fixed(C(-190, -430, 330), C(-150, -385, 305), C(217, 95, 55), C(217, 95, 55), roll=8, roll1=4))
    S["low"] = dict(lens=22, fstop=2.5, shake=0.8,
                    pose=fixed(C(217, -540, 12), C(225, -480, 13), C(217, 80, 220), C(217, 80, 200)))
    S["end"] = dict(lens=35, fstop=2.8, shake=0.2,
                    pose=fixed(C(217, -900, 520), C(217, -1500, 820), C(217, 100, 40), C(217, 100, 40)))
    return S


def look(pos, target, roll):
    q = (target - pos).to_track_quat("-Z", "Y")
    return q @ Euler((0, 0, math.radians(roll))).to_quaternion()


def cameras(scene, coll):
    S = shots()
    cams = {}
    for name, a, b in TL.SHOTS:
        if name.startswith("c_"):
            continue
        spec = S[name]
        cam = bpy.data.cameras.new("CAM_" + name)
        cam.lens = spec["lens"]
        cam.sensor_width = 36
        cam.clip_start = 0.005
        cam.dof.use_dof = True
        cam.dof.aperture_fstop = spec["fstop"]
        o = bpy.data.objects.new("CAM_" + name, cam)
        o.rotation_mode = "QUATERNION"
        coll.objects.link(o)
        cams[name] = (o, spec)
    # Keys: every frame of the shot, and of the cuts that borrow it (posed mid-move).
    plan = []
    for name, a, b in TL.SHOTS:
        if name.startswith("c_"):
            plan.append((name[2:], a, b, 0.35, 0.65))
        else:
            plan.append((name, a, b, 0.0, 1.0))
    for name, a, b, t0, t1 in plan:
        o, spec = cams[name]
        n = max(1, b - a)
        for f in range(a, b + 1):
            t = lerp(t0, t1, (f - a) / n)
            pos, tgt, roll, focus = spec["pose"](t)
            sh = spec["shake"]
            dist = (tgt - pos).length
            jitter = Vector((smooth_noise(hash(name) % 997, f / TL.FPS, 0.9),
                             smooth_noise(hash(name) % 991 + 1, f / TL.FPS, 0.8),
                             smooth_noise(hash(name) % 983 + 2, f / TL.FPS, 0.7))) * (0.006 * sh * dist)
            o.location = pos
            o.rotation_quaternion = look(pos, tgt + jitter, roll + 0.8 * sh * smooth_noise(7, f / TL.FPS, 0.6))
            # A close-up focuses on the near face of what it looks at, not its middle.
            o.data.dof.focus_distance = focus if focus is not None else dist + spec.get("focus_bias", 0.0)
            o.keyframe_insert("location", frame=f)
            o.keyframe_insert("rotation_quaternion", frame=f)
            o.data.dof.keyframe_insert("focus_distance", frame=f)
    # Cut to each shot's camera at its first frame.
    for name, a, b in TL.SHOTS:
        m = scene.timeline_markers.new(name, frame=a)
        m.camera = cams[name[2:] if name.startswith("c_") else name][0]
    scene.camera = cams["bulb"][0]
    return cams


# ---- Render settings --------------------------------------------------------------------------

def render_settings(scene):
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.fps = TL.FPS
    scene.frame_start = 0
    scene.frame_end = TL.FRAMES - 1
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.render.use_motion_blur = True
    scene.render.motion_blur_shutter = 0.5
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_depth = "16"
    ee = scene.eevee
    ee.taa_render_samples = 48
    ee.use_raytracing = True
    ee.volumetric_tile_size = "4"
    ee.volumetric_samples = 64
    ee.volumetric_end = 12.0
    ee.use_volumetric_shadows = True
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - High Contrast"
    scene.view_settings.exposure = -0.6
    w = bpy.data.worlds.new("Dark")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.002, 0.002, 0.0025, 1)
    scene.world = w


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = os.path.join(WORK, "video.blend")
    stills = []
    if "--out" in argv:
        out = argv[argv.index("--out") + 1]
    if "--stills" in argv:
        stills = [int(x) for x in argv[argv.index("--stills") + 1].split(",")]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "Teaser"
    render_settings(scene)
    room_coll = room()
    window(room_coll)
    tube(room_coll)
    pivot, bulb_light, filament = bulb(room_coll)
    haze(room_coll)
    laptop(room_coll)
    pedals()
    cables(collection("Cables"))
    lighting(collection("Lights"), bulb_light, filament)
    cameras(scene, collection("Cameras"))
    bpy.ops.wm.save_as_mainfile(filepath=out, relative_remap=False)
    for f in stills:
        scene.frame_set(f)
        scene.render.filepath = os.path.join(WORK, "stills", f"{f:04d}.png")
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
