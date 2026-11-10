"""Generate and register all HyperFrames fragments for the play-school redesign walkthrough.

Every fragment is a timed section (data-tl-start/end in TIMELINE ms); children are animated on the master timeline.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FR = ROOT / "work" / "frags"
FR.mkdir(parents=True, exist_ok=True)
ANCH = json.load(open(ROOT.parent / "stage" / "out" / "anchors.json"))
SCHOOL = "Little Sprouts"
NAVY = "#16213e"
IMG_TOP = 240

# ------------------------------------------------------------------ timeline (from edit/time-map.json)
TM = {p["piece_id"]: (p["start_tl_ms"], p["end_tl_ms"]) for p in json.load(open(ROOT / "edit" / "time-map.json"))["pieces"]}
INTRO, EXTB, FACADE, DOOR, WALKIN, RECEP, HALLB, PLAY, TRAIN, ARCHB, ARCH, THRU, BACKB, CLASS, KITCH, STORE, PLAN, OUTRO = (
    TM[f"P{i:03d}"] for i in range(1, 19))
TOTAL = OUTRO[1]

ZONES = [("01", "Entrance", "#ff6b6b"), ("02", "Reception", "#ffa94d"), ("03", "Play hall", "#ffd43b"),
         ("04", "Learning wing", "#9775fa"), ("05", "Classroom", "#69db7c"), ("06", "Snack station", "#38d9a9"),
         ("07", "Store", "#f783ac")]
ZC = {z[0]: z[2] for z in ZONES}
TT_C = "#4dabf7"


def dur(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                         capture_output=True, text=True).stdout.strip()
    return int(float(out) * 1000)


SFX = {k: (a, dur(ROOT / "hf" / "media" / f"{a}.wav")) for k, a in
       {"whoosh": "X0015", "pop": "X0016", "swoosh": "X0017", "riser": "X0018"}.items()}

CSS = f"""
.piece{{background:transparent!important}}
.sec{{position:absolute;inset:0;}}
.band{{position:absolute;left:0;width:1080px;background:{NAVY};}}
.band.top{{top:0;height:{IMG_TOP}px}} .band.bot{{top:1680px;height:240px}}
.tw{{position:absolute;left:0;top:0;width:1080px;height:{IMG_TOP}px;display:flex;align-items:center;padding:0 52px;gap:28px}}
.num{{flex:0 0 auto;width:104px;height:104px;border-radius:50%;display:flex;align-items:center;justify-content:center;
     font:900 44px Inter;color:{NAVY};box-shadow:0 6px 16px rgba(0,0,0,.35)}}
.ttl{{font:700 52px/1.08 Poppins;color:#fff}}
.sub{{font:500 29px/1.3 Poppins;color:#aebbd8;margin-top:8px}}
.chips{{position:absolute;left:0;top:1680px;width:1080px;height:240px;display:flex;flex-wrap:wrap;align-content:center;
       justify-content:center;gap:14px;padding:0 36px}}
.chip{{font:700 27px Poppins;color:{NAVY};background:#fff;border-radius:999px;padding:9px 22px 9px 16px;display:flex;align-items:center;gap:10px}}
.chip i{{display:block;width:16px;height:16px;border-radius:50%}}
.imgbox{{position:absolute;left:0;top:{IMG_TOP}px;width:1080px;height:1440px;overflow:hidden}}
.imgbox img{{position:absolute;left:0;top:0;width:1080px;height:1440px}}
.tag{{position:absolute;top:{IMG_TOP + 26}px;font:700 28px Poppins;letter-spacing:3px;color:#fff;padding:9px 20px;border-radius:10px}}
.tag.b{{left:26px;background:rgba(10,14,30,.62)}} .tag.a{{right:26px;background:#2f9e44}}
.divider{{position:absolute;left:0;top:{IMG_TOP}px;width:6px;height:1440px;background:#fff;box-shadow:0 0 22px rgba(0,0,0,.45)}}
.knob{{position:absolute;left:-27px;top:690px;width:60px;height:60px;border-radius:50%;background:#fff;box-shadow:0 4px 14px rgba(0,0,0,.4);
      font:900 26px Inter;color:{NAVY};display:flex;align-items:center;justify-content:center}}
.pin{{position:absolute;width:34px;height:34px;margin:-17px 0 0 -17px;border-radius:50%;background:#fff;border:8px solid #ff6b6b;
     box-shadow:0 3px 12px rgba(0,0,0,.45)}}
.ln{{position:absolute;height:4px;background:#fff;transform-origin:0 50%;box-shadow:0 1px 4px rgba(0,0,0,.35)}}
.lbl{{position:absolute;font:700 29px/1 Poppins;color:{NAVY};background:#fff;border-radius:14px;padding:13px 18px;
     box-shadow:0 8px 20px rgba(0,0,0,.3);white-space:nowrap;display:flex;align-items:center;gap:10px}}
.lbl i{{display:block;width:14px;height:14px;border-radius:50%}}
.prog{{position:absolute;left:60px;top:1745px;width:960px;display:flex;gap:10px}}
.prog div{{flex:1;height:10px;border-radius:5px;background:rgba(255,255,255,.18)}}
.progtxt{{position:absolute;left:60px;top:1785px;width:960px;display:flex;justify-content:space-between;font:500 21px Poppins;color:#8794b5}}
.progtxt span.on{{color:#fff;font-weight:700}}
.card{{position:absolute;left:40px;width:1000px;background:#fff;border-radius:28px;padding:30px 36px;box-shadow:0 18px 40px rgba(0,0,0,.4)}}
.card h3{{font:700 40px Poppins;color:{NAVY};display:flex;align-items:center;gap:14px}}
.card h3 b{{font:700 22px Poppins;color:#fff;padding:6px 14px;border-radius:8px;letter-spacing:2px}}
.card ul{{list-style:none;margin-top:16px}}
.card li{{font:500 31px/1.25 Poppins;color:#343a40;display:flex;align-items:center;gap:16px;margin-top:12px}}
.card li i{{flex:0 0 auto;width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;
           font:900 22px Inter;color:#fff;font-style:normal}}
.full{{position:absolute;inset:0;background:{NAVY}}}
"""


class Frag:
    def __init__(self, fid, start, end, z, kind="graphic"):
        self.fid, self.start, self.end, self.z, self.kind = fid, start, end, z, kind
        self.html, self.js, self.css = [], [], []

    def write(self):
        h = FR / f"{self.fid}.html"
        if self.kind == "audio":
            h.write_text("".join(self.html))
        else:
            h.write_text(f'<div id="{self.fid}" data-tl-start="{self.start}" data-tl-end="{self.end}">'
                         f'<div class="sec" id="{self.fid}-in">' + "".join(self.html) + "</div></div>")
        j = FR / f"{self.fid}.js"
        j.write_text("\n".join(self.js) + "\n")
        args = [sys.executable, str(ROOT / "tools" / "hf_build.py"), "frag", "--root", str(ROOT), "--id", self.fid,
                "--html", str(h), "--js", str(j), "--start-tl-ms", str(self.start), "--end-tl-ms", str(self.end),
                "--z", str(self.z), "--kind", self.kind, "--style", "custom-redesign"]
        if self.css:
            c = FR / f"{self.fid}.css"
            c.write_text("\n".join(self.css))
            args += ["--css", str(c)]
        r = subprocess.run(args, capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip())

    def T(self, ms):
        return f"T({int(ms)})"


# ------------------------------------------------------------------ building blocks
def top_band(f, num, color, title, sub, num_text=None):
    i = f.fid
    f.html.append(f'<div class="band top"></div><div class="tw" id="{i}-tw">'
                  f'<div class="num" id="{i}-num" style="background:{color}">{num_text or num}</div>'
                  f'<div><div class="ttl" id="{i}-ttl">{title}</div><div class="sub" id="{i}-sub">{sub}</div></div></div>')
    f.js.append(f'tl.fromTo("#{i}-num",{{scale:0,rotation:-90}},{{scale:1,rotation:0,duration:0.5,ease:"back.out(2.2)"}},{f.T(f.start + 60)});')
    f.js.append(f'tl.fromTo("#{i}-ttl",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:0.45,ease:"power3.out"}},{f.T(f.start + 160)});')
    f.js.append(f'tl.fromTo("#{i}-sub",{{opacity:0,x:-30}},{{opacity:1,x:0,duration:0.45,ease:"power3.out"}},{f.T(f.start + 300)});')


def bottom_chips(f, chips, at):
    i = f.fid
    items = "".join(f'<div class="chip" id="{i}-c{k}"><i style="background:{c}"></i>{t}</div>' for k, (t, c) in enumerate(chips))
    f.html.append(f'<div class="band bot"></div><div class="chips">{items}</div>')
    for k in range(len(chips)):
        f.js.append(f'tl.fromTo("#{i}-c{k}",{{opacity:0,y:24}},{{opacity:1,y:0,duration:0.35,ease:"back.out(1.8)"}},{f.T(at + k * 140)});')


def progress(f, idx):
    i = f.fid
    bars = "".join(f'<div style="background:{ZONES[k][2] if k <= idx else "rgba(255,255,255,.18)"}"></div>' for k in range(len(ZONES)))
    txt = "".join(f'<span class="{"on" if k == idx else ""}">{ZONES[k][1]}</span>' for k in range(len(ZONES)))
    f.html.append(f'<div class="band bot"></div><div class="prog" id="{i}-pg">{bars}</div><div class="progtxt">{txt}</div>')
    f.js.append(f'tl.fromTo("#{i}-pg",{{opacity:0}},{{opacity:1,duration:0.4}},{f.T(f.start + 200)});')


def before_after(f, before, after, kb=True, wipe_at=600):
    i, s0, s1 = f.fid, f.start, f.end
    f.html.append(f'<div class="imgbox"><img src="media/{before}.jpg"></div>'
                  f'<div class="imgbox" id="{i}-ac" style="clip-path:inset(0 100% 0 0)"><img id="{i}-ai" src="media/{after}.jpg"></div>'
                  f'<div class="divider" id="{i}-dv"><div class="knob">&#x2194;</div></div>'
                  f'<div class="tag b" id="{i}-tb">BEFORE</div><div class="tag a" id="{i}-ta">AFTER</div>')
    a = s0 + wipe_at
    f.js += [
        f'tl.set("#{i}-ac",{{clipPath:"inset(0 100% 0 0)"}},{f.T(s0)});',
        f'tl.set("#{i}-dv",{{x:-3,opacity:0}},{f.T(s0)}); tl.set("#{i}-ta",{{opacity:0}},{f.T(s0)});',
        f'tl.fromTo("#{i}-tb",{{opacity:0,y:-12}},{{opacity:1,y:0,duration:0.3}},{f.T(s0 + 100)});',
        f'tl.to("#{i}-dv",{{opacity:1,duration:0.15}},{f.T(a - 120)});',
        f'tl.to("#{i}-ac",{{clipPath:"inset(0 0% 0 0)",duration:1.3,ease:"power2.inOut"}},{f.T(a)});',
        f'tl.to("#{i}-dv",{{x:1077,duration:1.3,ease:"power2.inOut"}},{f.T(a)});',
        f'tl.fromTo("#{i}-ta",{{opacity:0,y:-12}},{{opacity:1,y:0,duration:0.3}},{f.T(a + 700)});',
        f'tl.to("#{i}-ac",{{clipPath:"inset(0 55% 0 0)",duration:0.55,ease:"power2.inOut"}},{f.T(a + 1450)});',
        f'tl.to("#{i}-dv",{{x:483,duration:0.55,ease:"power2.inOut"}},{f.T(a + 1450)});',
        f'tl.to("#{i}-ac",{{clipPath:"inset(0 0% 0 0)",duration:0.6,ease:"power2.inOut"}},{f.T(a + 2250)});',
        f'tl.to("#{i}-dv",{{x:1077,duration:0.6,ease:"power2.inOut"}},{f.T(a + 2250)});',
        f'tl.to(["#{i}-dv","#{i}-tb"],{{opacity:0,duration:0.25}},{f.T(a + 2850)});',
    ]
    if kb:
        hold = (s1 - (a + 2900)) / 1000
        f.js.append(f'tl.fromTo("#{i}-ai",{{scale:1}},{{scale:1.06,duration:{hold:.3f},ease:"none",transformOrigin:"50% 55%"}},{f.T(a + 2900)});')
    return a


def callouts(f, scene, opts, at, color):
    """opts: list of (index into anchors, side, dy, dx_override_or_None)"""
    i = f.fid
    A = ANCH[scene]
    for k, (idx, side, dy, label) in enumerate(opts):
        an = A[idx]
        px, py = an["x"], an["y"] + IMG_TOP
        if label is None:
            label = an["label"]
        L = 52
        if side == "right":
            lx, ly = px + L, py + dy
            lab_style = f"left:{lx}px;top:{ly - 27}px"
        elif side == "left":
            lx, ly = px - L, py + dy
            lab_style = f"right:{1080 - lx}px;top:{ly - 27}px"
        elif side == "above":
            lx, ly = px, py - 70 + dy
            lab_style = f"left:{lx}px;top:{ly - 27}px;translate:-50% 0"
        else:  # below
            lx, ly = px, py + 70 + dy
            lab_style = f"left:{lx}px;top:{ly - 27}px;translate:-50% 0"
        ex, ey = (lx, ly)
        ln_len = math.hypot(ex - px, ey - py)
        ang = math.degrees(math.atan2(ey - py, ex - px))
        t = at + k * 320
        f.html.append(f'<div class="ln" id="{i}-l{k}" style="left:{px}px;top:{py - 2}px;width:{ln_len:.0f}px;transform:rotate({ang:.1f}deg)"></div>'
                      f'<div class="pin" id="{i}-p{k}" style="left:{px}px;top:{py}px;border-color:{color}"></div>'
                      f'<div class="lbl" id="{i}-b{k}" style="{lab_style}"><i style="background:{color}"></i>{label}</div>')
        f.js += [f'tl.fromTo("#{i}-p{k}",{{scale:0}},{{scale:1,duration:0.4,ease:"back.out(3)"}},{f.T(t)});',
                 f'tl.fromTo("#{i}-l{k}",{{scaleX:0}},{{scaleX:1,duration:0.25,ease:"power2.out"}},{f.T(t + 120)});',
                 f'tl.fromTo("#{i}-b{k}",{{opacity:0,scale:0.7}},{{opacity:1,scale:1,duration:0.35,ease:"back.out(2)"}},{f.T(t + 220)});']


def fade_edges(f, fin=True, fout=True, inner=None):
    sel = inner or f"#{f.fid}-in"
    if fin:
        f.js.append(f'tl.fromTo("{sel}",{{opacity:0}},{{opacity:1,duration:0.22,ease:"none"}},{f.T(f.start)});')
    if fout:
        f.js.append(f'tl.to("{sel}",{{opacity:0,duration:0.22,ease:"none"}},{f.T(f.end - 220)});')


def footage_overlay(fid, span, zone_idx, title, sub, z=20):
    f = Frag(fid, span[0], span[1], z)
    top_band(f, "", "#ffffff", title, sub, num_text="&#9654;")
    f.html.append(f'<div class="tag b" id="{fid}-tg">BEFORE · REAL FOOTAGE</div>')
    f.js.append(f'tl.fromTo("#{fid}-tg",{{opacity:0,y:-12}},{{opacity:1,y:0,duration:0.3}},{f.T(span[0] + 250)});')
    progress(f, zone_idx)
    return f


# ------------------------------------------------------------------ sections
frags = []

# theme + intro -------------------------------------------------------
f = Frag("intro", *INTRO, 30)
f.css.append(CSS)
f.css.append(f"""
.ishade{{position:absolute;left:0;top:{IMG_TOP}px;width:1080px;height:1440px;background:linear-gradient(180deg,rgba(22,33,62,.25),rgba(22,33,62,.82) 55%,rgba(22,33,62,.92))}}
.ikick{{position:absolute;left:0;width:1080px;top:880px;text-align:center}}
.ikick span{{font:700 26px Poppins;letter-spacing:5px;color:{NAVY};background:#ffd43b;padding:10px 22px;border-radius:10px}}
.ih1{{position:absolute;left:0;width:1080px;text-align:center;font:700 104px/1.02 Poppins;color:#fff}}
.ih2{{position:absolute;left:0;width:1080px;text-align:center;font:500 46px/1.2 Poppins;color:#fff}}
.ih3{{position:absolute;left:90px;width:900px;text-align:center;font:500 31px/1.4 Poppins;color:#c5d1eb}}
.logo{{width:104px;height:104px;border-radius:50%;background:#ffd43b;display:flex;align-items:center;justify-content:center}}
""")
f.html.append('<div class="ishade" id="intro-sh"></div>')
f.html.append('<div class="band top"></div><div class="tw"><div class="logo" id="intro-lg">'
              '<svg width="70" height="70" viewBox="-1 -1 2 2"><path d="M0,0.55 L0,-0.05" stroke="#2f9e44" stroke-width="0.13" stroke-linecap="round"/>'
              '<path d="M0,-0.05 C-0.1,-0.6 -0.7,-0.6 -0.75,-0.35 C-0.5,0 -0.15,0.05 0,-0.05Z" fill="#51cf66"/>'
              '<path d="M0,-0.1 C0.1,-0.7 0.7,-0.7 0.8,-0.45 C0.55,-0.05 0.15,0 0,-0.1Z" fill="#37b24d"/></svg></div>'
              f'<div><div class="ttl" id="intro-t">{SCHOOL}</div><div class="sub" id="intro-s">Play School &amp; Teacher Training Centre</div></div></div>')
f.html.append('<div class="ikick" id="intro-k"><span>DESIGN CONCEPT</span></div>'
              '<div class="ih1" id="intro-h1" style="top:960px">From home</div>'
              '<div class="ih1" id="intro-h2" style="top:1070px;color:#ffd43b">to play school</div>'
              '<div class="ih2" id="intro-h3" style="top:1205px">&amp; teacher training centre</div>'
              '<div class="ih3" id="intro-h4" style="top:1330px">Same walls, new purpose: only paint, murals, furniture &amp; décor. No structural changes.</div>')
f.html.append('<div class="band bot"></div><div class="chips" id="intro-ch"><div class="chip"><i style="background:#ff6b6b"></i>Before</div>'
              '<div class="chip" style="background:transparent;color:#fff;padding:0">&#x2192;</div><div class="chip"><i style="background:#2f9e44"></i>After</div>'
              '<div class="chip" style="background:transparent;color:#aebbd8;font-weight:500">room-by-room walkthrough</div></div>')
f.js += [f'tl.fromTo("#intro-lg",{{scale:0}},{{scale:1,duration:0.5,ease:"back.out(2)"}},T(100));',
         'tl.fromTo("#intro-t",{opacity:0,x:-30},{opacity:1,x:0,duration:0.5},T(200));',
         'tl.fromTo("#intro-s",{opacity:0,x:-30},{opacity:1,x:0,duration:0.5},T(330));',
         'tl.fromTo("#intro-sh",{opacity:0},{opacity:1,duration:0.6},T(0));',
         'tl.fromTo("#intro-k",{opacity:0,y:20},{opacity:1,y:0,duration:0.4},T(350));',
         'tl.fromTo("#intro-h1",{opacity:0,y:40},{opacity:1,y:0,duration:0.55,ease:"power3.out"},T(500));',
         'tl.fromTo("#intro-h2",{opacity:0,y:40},{opacity:1,y:0,duration:0.55,ease:"power3.out"},T(700));',
         'tl.fromTo("#intro-h3",{opacity:0,y:30},{opacity:1,y:0,duration:0.5},T(950));',
         'tl.fromTo("#intro-h4",{opacity:0},{opacity:1,duration:0.6},T(1250));',
         'tl.fromTo("#intro-ch",{opacity:0},{opacity:1,duration:0.5},T(1500));',
         f'tl.to(["#intro-sh","#intro-k","#intro-h1","#intro-h2","#intro-h3","#intro-h4"],{{opacity:0,duration:0.35}},T({INTRO[1] - 350}));']
frags.append(f)

# exterior before -----------------------------------------------------
frags.append(footage_overlay("extb", EXTB, 0, "The house today", "Real walkthrough footage · before"))

# 01 facade -----------------------------------------------------------
f = Frag("facade", *FACADE, 20)
a = before_after(f, "X0002", "X0003")
top_band(f, "01", ZC["01"], "Entrance &amp; facade", "Paint, signboard &amp; floor banners · no structural change")
callouts(f, "ext_wide", [(4, "left", 30, "Terrace · outdoor play"), (3, "right", -55, "2nd floor · Training"),
                         (2, "left", -80, "1st floor · Classrooms"), (0, "left", -80, "Signboard"),
                         (1, "right", 60, "Rainbow door + paint")], a + 3000, ZC["01"])
bottom_chips(f, [("Signboard", ZC["01"]), ("Sky-blue paint", "#74c0fc"), ("Rainbow door", "#ffd43b"),
                 ("Floor banners", "#ff8787"), ("Planters", "#69db7c")], a + 3100)
fade_edges(f, fin=True, fout=False)
frags.append(f)

# 01 door -------------------------------------------------------------
f = Frag("door", *DOOR, 20)
a = before_after(f, "X0004", "X0005")
top_band(f, "01", ZC["01"], "A welcoming entrance", "First impression for parents &amp; kids")
callouts(f, "door", [(0, "right", -150, "Rainbow door surround"), (1, "left", -120, "Timings &amp; admissions board"),
                     (2, "left", 130, "Planters + welcome mat"), (3, "left", 60, "Hopscotch on the pavement")], a + 3000, ZC["01"])
bottom_chips(f, [("Golden door", "#fab005"), ("Crayon wall art", "#ff922b"), ("Timings board", "#1c7ed6"), ("Hopscotch", "#69db7c")], a + 3100)
fade_edges(f, fin=False, fout=True)
frags.append(f)

# walk in -------------------------------------------------------------
frags.append(footage_overlay("walkin", WALKIN, 1, "Walking in", "Real footage · the front door &amp; main hall"))

# 02 reception --------------------------------------------------------
f = Frag("recep", *RECEP, 20)
a = before_after(f, "X0006", "X0007")
top_band(f, "02", ZC["02"], "Reception &amp; parents' corner", "Front of the hall, right by the entrance")
callouts(f, "hall_entry", [(0, "left", 170, "Welcome desk"), (1, "right", 90, "Footprint trail to class"),
                           (2, "above", -60, "Play hall beyond")], a + 3000, ZC["02"])
bottom_chips(f, [("Welcome desk", ZC["02"]), ("Notice board", "#c8a165"), ("Shoe rack", "#74c0fc"), ("Plants", "#69db7c")], a + 3100)
fade_edges(f)
frags.append(f)

# hall before -----------------------------------------------------------
frags.append(footage_overlay("hallb", HALLB, 2, "The main hall", "Real footage · about 4 m × 9.5 m"))

# 03 play hall ----------------------------------------------------------
f = Frag("play", *PLAY, 20)
a = before_after(f, "X0008", "X0009")
top_band(f, "03", ZC["03"], "Play hall", "Soft-play zone · 9 AM – 1 PM")
mats = dict(ANCH["hall_arch"][1])
callouts(f, "hall_arch", [(3, "above", -150, "Mural · Play, Learn, Grow"), (4, "right", -150, "Alphabet train wall"),
                          (0, "left", -60, "Slide into the ball pool"), (2, "right", 90, "Toy storage cubes"),
                          (5, "left", 130, "Soft foam blocks")], a + 3000, "#f59f00")
bottom_chips(f, [("Foam floor mats", "#74c0fc"), ("Slide + ball pool", "#f783ac"), ("Toy cubes", "#ffd43b"),
                 ("Wall murals", "#69db7c"), ("LED panels", "#ced4da"), ("Ceiling repaired", "#ffffff")], a + 3100)
fade_edges(f, fin=True, fout=False)
frags.append(f)

# 03b training mode -----------------------------------------------------
f = Frag("train", *TRAIN, 20)
i = "train"
f.html.append(f'<div class="imgbox"><img src="media/X0009.jpg"></div>'
              f'<div class="imgbox" id="{i}-tc"><img id="{i}-ti" src="media/X0010.jpg"></div>'
              f'<div class="tag a" id="{i}-tg" style="background:{TT_C}">AFTER 2 PM</div>')
f.js += [f'tl.fromTo("#{i}-tc",{{opacity:0}},{{opacity:1,duration:0.9,ease:"power1.inOut"}},{f.T(TRAIN[0] + 500)});',
         f'tl.fromTo("#{i}-tg",{{opacity:0,y:-12}},{{opacity:1,y:0,duration:0.3}},{f.T(TRAIN[0] + 900)});',
         f'tl.fromTo("#{i}-ti",{{scale:1}},{{scale:1.05,duration:{(TRAIN[1] - TRAIN[0] - 1400) / 1000:.2f},ease:"none",transformOrigin:"50% 50%"}},{f.T(TRAIN[0] + 1400)});']
top_band(f, "TT", TT_C, "Same hall · teacher training", "After 2 PM the play hall becomes a training room", num_text="TT")
callouts(f, "hall_training", [(0, "above", -70, "Pull-down screen"), (1, "left", 0, "Ceiling projector"),
                              (2, "left", 225, "Seats for trainees"), (3, "right", 15, "Resource &amp; book shelf")], TRAIN[0] + 1700, TT_C)
bottom_chips(f, [("Projector + screen", TT_C), ("8–16 seats", "#e64980"), ("Trainer desk", "#f59f00"), ("Library shelf", "#69db7c")], TRAIN[0] + 1800)
fade_edges(f, fin=False, fout=True)
frags.append(f)

# approach arch ---------------------------------------------------------
frags.append(footage_overlay("archb", ARCHB, 3, "Towards the arch", "Real footage · the way to the back rooms"))

# 04 arch -----------------------------------------------------------------
f = Frag("arch", *ARCH, 20)
a = before_after(f, "X0011", "X0012")
top_band(f, "04", ZC["04"], "Rainbow arch · learning wing", "The arch becomes the gateway to the classrooms")
callouts(f, "arch", [(0, "right", 0, "Rainbow arch = class entrance"), (1, "right", 40, "Brighter corridor lighting"),
                     (2, "right", -30, "Footprints guide the kids")], a + 3000, ZC["04"])
bottom_chips(f, [("Painted rainbow arch", ZC["04"]), ("Footprint path", "#ff8787"), ("LED lighting", "#ced4da")], a + 3100)
fade_edges(f)
frags.append(f)

frags.append(footage_overlay("thru", THRU, 3, "Into the corridor", "Real footage · learning wing"))
frags.append(footage_overlay("backb", BACKB, 4, "The back room", "Real footage · brightened so you can see it"))

# 05 classroom ------------------------------------------------------------
f = Frag("class", *CLASS, 20)
a = before_after(f, "X0013", "X0014")
top_band(f, "05", ZC["05"], "Classroom 1 · playgroup", "Calm, bright &amp; organised")
callouts(f, "backroom", [(4, "above", -40, "Labelled storage on the loft"), (0, "left", -70, "Whiteboard + ABC strip"),
                         (5, "above", -40, "Number line 1–10"), (3, "below", 30, "Art display"),
                         (1, "left", 120, "Alphabet rug · circle time"), (2, "below", 150, "Kids' tables &amp; chairs")], a + 3000, "#2f9e44")
bottom_chips(f, [("Whiteboard", "#ced4da"), ("Alphabet rug", "#ff8787"), ("Kids' tables", "#4dabf7"),
                 ("Art wall", "#ff922b"), ("Loft storage", "#b197fc"), ("LED lights", "#ffffff")], a + 3100)
fade_edges(f)
frags.append(f)


# 06 / 07 kitchen + store (real footage + plan card) -------------------------
def plan_card(fid, span, num, title, sub, items, color, card_top):
    f = Frag(fid, span[0], span[1], 20)
    top_band(f, num, color, title, sub)
    f.html.append(f'<div class="tag b" id="{fid}-tg">REAL FOOTAGE · PLANNED USE</div>')
    lis = "".join(f'<li id="{fid}-li{k}"><i style="background:{color}">&#10003;</i>{t}</li>' for k, t in enumerate(items))
    f.html.append(f'<div class="card" id="{fid}-cd" style="top:{card_top}px"><h3><b style="background:{color}">PLAN</b>{title}</h3><ul>{lis}</ul></div>')
    f.js += [f'tl.fromTo("#{fid}-tg",{{opacity:0}},{{opacity:1,duration:0.3}},{f.T(span[0] + 250)});',
             f'tl.fromTo("#{fid}-cd",{{opacity:0,y:60}},{{opacity:1,y:0,duration:0.5,ease:"power3.out"}},{f.T(span[0] + 450)});']
    for k in range(len(items)):
        f.js.append(f'tl.fromTo("#{fid}-li{k}",{{opacity:0,x:-24}},{{opacity:1,x:0,duration:0.3}},{f.T(span[0] + 800 + k * 260)});')
    progress(f, int(num) - 1)
    return f


frags.append(plan_card("kitch", KITCH, "06", "Snack &amp; hygiene station", "The existing kitchen, re-used (no plumbing changes)",
                       ["Child-height hand-wash + step stools", "Lunch-box &amp; water-bottle rack", "Hand-washing chart",
                        "Pastel cabinet fronts, safety latches"], ZC["06"], 1130))
frags.append(plan_card("store", STORE, "07", "Resource store", "Small room with built-in shelves",
                       ["Labelled bins for toys &amp; teaching aids", "Staff lockers &amp; records", "First-aid kit + fire extinguisher",
                        "Spare stationery for training"], ZC["07"], 1130))

# floor plan ---------------------------------------------------------------
f = Frag("plan", *PLAN, 40)
P0 = PLAN[0]
f.css.append(f"""
.ph{{position:absolute;left:0;width:1080px;text-align:center;font:700 64px Poppins;color:#fff}}
.ps{{position:absolute;left:0;width:1080px;text-align:center;font:500 30px Poppins;color:#aebbd8}}
.fl{{position:absolute;left:50px;width:980px;height:250px;border-radius:26px;background:#20305a;overflow:hidden;box-shadow:0 14px 30px rgba(0,0,0,.35)}}
.fl .tab{{position:absolute;left:0;top:0;width:190px;height:250px;display:flex;flex-direction:column;align-items:center;justify-content:center;
         font:900 30px/1.05 Inter;color:{NAVY};text-align:center}}
.fl .tab small{{font:700 18px Poppins;margin-top:8px;letter-spacing:1px}}
.fl .ft{{position:absolute;left:220px;top:26px;font:700 40px Poppins;color:#fff}}
.fl .fc{{position:absolute;left:220px;top:92px;width:740px;display:flex;flex-wrap:wrap;gap:10px}}
.fl .fc span{{font:700 24px Poppins;color:{NAVY};background:#fff;border-radius:999px;padding:7px 16px}}
.pnote{{position:absolute;left:0;width:1080px;top:1800px;text-align:center;font:500 22px Poppins;color:#8794b5}}
.gp{{position:absolute;left:0;top:0;width:1080px;height:1920px}}
.zn{{position:absolute;border-radius:18px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;
     font:700 30px/1.15 Poppins;color:{NAVY};box-shadow:inset 0 0 0 4px rgba(255,255,255,.55)}}
.zn small{{font:500 21px/1.25 Poppins;margin-top:6px;color:#2b3550}}
.zb{{position:absolute;font:700 24px Poppins;color:#fff;background:{TT_C};border-radius:12px;padding:10px 16px;box-shadow:0 8px 18px rgba(0,0,0,.35)}}
""")
f.html.append('<div class="full"></div>')
# part A: stacked floors
f.html.append(f'<div id="plan-a"><div class="ph" style="top:190px" id="plan-h">Floor by floor</div>'
              f'<div class="ps" style="top:285px" id="plan-s">Where everything goes in the building</div>')
floors = [("TERRACE", "#38d9a9", "Outdoor play", ["Artificial grass", "Sand &amp; water play", "Garden corner", "Existing green shade"], "proposed"),
          ("2ND<br>FLOOR", TT_C, "Teacher Training Centre", ["Training hall", "Demo classroom", "Resource library", "Office"], "proposed"),
          ("1ST<br>FLOOR", "#ff8787", "Classrooms", ["Nursery", "LKG", "UKG", "Nap &amp; quiet room", "Kids' toilets"], "proposed"),
          ("GROUND<br>FLOOR", "#ffd43b", "Play &amp; welcome", ["Reception", "Play hall*", "Classroom 1", "Snack station", "Store"], "filmed ✓")]
tops = [420, 770, 1120, 1470]
for k, (tab, col, title, chips, tagtxt) in enumerate(floors):
    ch = "".join(f"<span>{c}</span>" for c in chips)
    f.html.append(f'<div class="fl" id="plan-f{k}" style="top:{tops[k]}px"><div class="tab" style="background:{col}">{tab}<small>{tagtxt.upper()}</small></div>'
                  f'<div class="ft">{title}</div><div class="fc">{ch}</div></div>')
f.html.append('<div class="pnote" id="plan-n">*Play hall doubles as a training room after 2 PM · upper floors not filmed: proposed use</div></div>')
f.js += [f'tl.fromTo("#plan-h",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.5}},T({P0 + 150}));',
         f'tl.fromTo("#plan-s",{{opacity:0}},{{opacity:1,duration:0.5}},T({P0 + 400}));',
         f'tl.fromTo("#plan-n",{{opacity:0}},{{opacity:1,duration:0.5}},T({P0 + 5200}));']
for k, delay in zip([3, 2, 1, 0], [700, 1700, 2700, 3700]):
    f.js.append(f'tl.fromTo("#plan-f{k}",{{opacity:0,y:80,scale:0.96}},{{opacity:1,y:0,scale:1,duration:0.6,ease:"back.out(1.4)"}},T({P0 + delay}));')
f.js.append(f'tl.to("#plan-a",{{opacity:0,duration:0.45}},T({P0 + 7000}));')
# part B: ground floor plan (schematic)
g = ['<div id="plan-b" class="gp">', '<div class="ph" style="top:120px" id="plan-bh">Ground floor plan</div>',
     '<div class="ps" style="top:212px">Schematic · not to scale</div>']
zones = [("pz1", 120, 330, 400, 330, ZC["05"], "Classroom 1", "Playgroup · nursery"),
         ("pz2", 560, 330, 400, 190, ZC["06"], "Snack &amp; hygiene", "existing kitchen"),
         ("pz3", 560, 540, 400, 120, ZC["07"], "Store", "resources"),
         ("pz4", 120, 700, 840, 700, ZC["03"], "Play hall", "mats · slide · ball pool · murals"),
         ("pz5", 120, 1420, 840, 270, ZC["02"], "Reception", "welcome desk · notice board · shoe rack")]
for zid, x, y, w, h, col, t, s in zones:
    g.append(f'<div class="zn" id="{zid}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{col}">{t}<small>{s}</small></div>')
g.append(f'<div class="zn" id="pz6" style="left:140px;top:672px;width:150px;height:56px;background:{ZC["04"]};color:#fff;font-size:22px;border-radius:28px 28px 8px 8px">ARCH</div>')
g.append(f'<div class="zn" id="pz7" style="left:140px;top:1700px;width:180px;height:64px;background:{ZC["01"]};color:#fff;font-size:24px">ENTRANCE</div>')
g.append(f'<div class="zb" id="pzb" style="left:520px;top:1150px">After 2 PM → teacher training</div>')
g.append('<svg class="gp" id="pzpath" viewBox="0 0 1080 1920"><path d="M230,1690 L230,1450 L205,1150 L230,860 L215,700 L270,560"'
         ' fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" stroke-dasharray="2 26" id="pzp"/></svg>')
g.append('<div class="ps" style="top:1800px;font-size:26px;color:#fff">● ● ●  footprint path: entrance → arch → classroom</div>')
g.append("</div>")
f.html.append("".join(g))
B0 = P0 + 7200
f.js.append(f'tl.fromTo("#plan-b",{{opacity:0}},{{opacity:1,duration:0.45}},T({B0}));')
for k, zid in enumerate(["pz5", "pz4", "pz6", "pz1", "pz2", "pz3", "pz7"]):
    f.js.append(f'tl.fromTo("#{zid}",{{opacity:0,scale:0.9}},{{opacity:1,scale:1,duration:0.4,ease:"back.out(1.6)"}},T({B0 + 300 + k * 330}));')
f.js.append(f'tl.fromTo("#pzp",{{strokeDashoffset:700,opacity:0}},{{strokeDashoffset:0,opacity:1,duration:1.6,ease:"none"}},T({B0 + 2700}));')
f.js.append(f'tl.fromTo("#pzb",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.4}},T({B0 + 3400}));')
f.js.append(f'tl.to("#plan-in",{{opacity:0,duration:0.3}},T({PLAN[1] - 300}));')
frags.append(f)

# outro --------------------------------------------------------------------
f = Frag("outro", *OUTRO, 40)
O0 = OUTRO[0]
f.css.append("""
.og{position:absolute;width:480px;height:640px;border-radius:24px;overflow:hidden;box-shadow:0 16px 36px rgba(0,0,0,.45)}
.og img{width:100%;height:100%;object-fit:cover}
.og span{position:absolute;left:14px;bottom:14px;font:700 24px Poppins;color:#16213e;background:#fff;border-radius:10px;padding:6px 12px}
.ol{position:absolute;left:0;width:1080px;text-align:center;font:500 28px Poppins;color:#fff}
""")
f.html.append('<div class="full"></div><div class="ph" style="top:110px" id="out-h">Same walls. New purpose.</div>')
grid = [("X0003", "Entrance", 40, 270), ("X0009", "Play hall", 560, 270), ("X0010", "Teacher training", 40, 950), ("X0014", "Classroom", 560, 950)]
for k, (aid, lab, x, y) in enumerate(grid):
    f.html.append(f'<div class="og" id="out-g{k}" style="left:{x}px;top:{y}px"><img src="media/{aid}.jpg"><span>{lab}</span></div>')
f.html.append('<div class="ol" style="top:1640px" id="out-l1">✓ No structural changes &nbsp; ✓ Paint &amp; décor &nbsp; ✓ Kid-safe furniture</div>'
              '<div class="ol" style="top:1700px;color:#ffd43b" id="out-l2">Play school by day · teacher training after 2 PM</div>'
              f'<div class="ps" style="top:1790px" id="out-l3">{SCHOOL} · design concept</div>')
f.js += [f'tl.fromTo("#out-h",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.5}},T({O0 + 150}));']
for k in range(4):
    f.js.append(f'tl.fromTo("#out-g{k}",{{opacity:0,scale:0.85}},{{opacity:1,scale:1,duration:0.5,ease:"back.out(1.6)"}},T({O0 + 450 + k * 220}));')
f.js += [f'tl.fromTo("#out-l1",{{opacity:0}},{{opacity:1,duration:0.5}},T({O0 + 1700}));',
         f'tl.fromTo("#out-l2",{{opacity:0}},{{opacity:1,duration:0.5}},T({O0 + 2100}));',
         f'tl.fromTo("#out-l3",{{opacity:0}},{{opacity:1,duration:0.5}},T({O0 + 2500}));',
         f'tl.to("#outro-in",{{opacity:0,duration:0.8}},T({OUTRO[1] - 800}));']
f.js.append(f'tl.fromTo("#outro-in",{{opacity:0}},{{opacity:1,duration:0.3}},T({O0}));')
frags.append(f)

# audio --------------------------------------------------------------------
au = Frag("audio", 0, TOTAL, 1, kind="audio")
music = f'<audio id="aud-music" src="media/X0019.wav" data-tl-start="0" data-tl-end="{TOTAL}" data-volume="0.55"></audio>'
cues = []
for k, s in enumerate([FACADE, DOOR, RECEP, PLAY, ARCH, CLASS]):
    cues.append(("whoosh", s[0] + 600 - 80))
    cues.append(("swoosh", s[0] + 600 + 1450 - 60))
cues.append(("whoosh", TRAIN[0] + 450))
cues.append(("riser", PLAN[0] - SFX["riser"][1] + 250))
for k in range(4):
    cues.append(("pop", PLAN[0] + [700, 1700, 2700, 3700][k] + 60))
cues.append(("whoosh", PLAN[0] + 7100))
cues.append(("whoosh", OUTRO[0]))
for k, (name, t) in enumerate(cues):
    aid, d = SFX[name]
    vol = {"whoosh": 0.5, "swoosh": 0.32, "riser": 0.4, "pop": 0.45}[name]
    cues_html = f'<audio id="aud-sfx{k}" src="media/{aid}.wav" data-tl-start="{max(0, int(t))}" data-tl-end="{max(0, int(t)) + d}" data-volume="{vol}"></audio>'
    music += cues_html
au.html.append(music)
frags.append(au)

for fr in frags:
    fr.write()
print("fragments:", len(frags))
