import json, sys
sys.path.insert(0, "tools")
from vecommon import Project, envelope, save_json, input_hashes
prj = Project(".")
FIT = {"mode": "fit", "crop": {"x": 0, "y": 0, "w": 1, "h": 1}}
CUT = {"type": "cut", "duration_ms": 0, "owner": "rough-cut"}
def seg(i, a, b, rate, reason, gain=-10.0):
    return {"seg_id": f"E{i:03d}", "source_id": "S1", "in_src_ms": a, "out_src_ms": b, "rate": rate, "reframe": FIT,
            "audio": {"gain_db": gain, "fade_in_ms": 120, "fade_out_ms": 120}, "transition_in": CUT, "reason": reason, "words": None}
def ins(i, after, dur, reason):
    return {"ins_id": f"N{i:03d}", "after_seg_id": after, "asset_id": "X0001", "in_src_ms": 0, "out_src_ms": dur, "rate": 1.0,
            "audio": "mute", "reason": reason}
segments = [
    seg(1, 0, 1000, 0.25, "intro: top of the building, slowed under the title card"),
    seg(2, 1000, 3800, 1.0, "BEFORE: tilt down the facade"),
    seg(3, 3800, 8000, 1.0, "BEFORE: front door, unlock, step inside"),
    seg(4, 8000, 12300, 1.0, "BEFORE: the main hall"),
    seg(5, 12300, 14100, 1.0, "BEFORE: approaching the arch"),
    seg(6, 14100, 16400, 1.15, "BEFORE: through the arch into the corridor"),
    seg(7, 16400, 19900, 1.0, "BEFORE: back room (exposure-corrected)"),
    seg(8, 19900, 21600, 0.45, "kitchen, slowed under the snack-station card"),
    seg(9, 21600, 24150, 0.65, "small store room, slowed under the resource-store card"),
]
inserts = [
    ins(1, "E002", 7200, "AFTER reveal: facade"),
    ins(2, "E002", 6000, "AFTER reveal: entrance door"),
    ins(3, "E003", 6500, "AFTER reveal: reception"),
    ins(4, "E004", 8000, "AFTER reveal: play hall"),
    ins(5, "E004", 6500, "AFTER: same hall in teacher-training mode"),
    ins(6, "E005", 5500, "AFTER reveal: rainbow arch / learning wing"),
    ins(7, "E007", 7000, "AFTER reveal: classroom"),
    ins(8, "E009", 14000, "floor-by-floor zoning plan"),
    ins(9, "E009", 7000, "outro summary"),
]
data = prj.load_project()
edl = envelope("edl/2", data["project_id"], "rough-cut", input_hashes(prj, ["work/mezzanine/S1.mp4"]))
edl.update({"edl_version": 1, "fps": 30, "canvas": data["brief"]["canvas"], "duplicates_allowed": False,
            "profile": "default", "segments": segments, "inserts": inserts,
            "removed": [{"rm_id": "R001", "source_id": "S1", "start_src_ms": 24150, "end_src_ms": 24167, "category": "tail", "evidence": {"note": "last frame"}, "confidence": "high", "audit_flag": False}],
            "notes": "No speech in the source: scene-based structural edit (walkthrough order kept). AFTER sections are "
                     "inserts of a navy plate fully covered by before/after fragments."})
save_json(prj.p("edit/edl.json"), edl)
print("edl written", sum((s['out_src_ms']-s['in_src_ms'])/s['rate'] for s in segments) + sum(i['out_src_ms'] for i in inserts))
