"""Programmatic Lumetri Color looks and voice-aware ducking keyframe generator for Premiere Pro."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class LumetriLook:
    name: str
    temperature: float
    tint: float
    exposure: float
    contrast: float
    highlights: float
    shadows: float
    saturation: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


LOOK_CATALOG: dict[str, LumetriLook] = {
    "editorial_teal": LumetriLook("editorial_teal", -6.0, 2.0, 0.15, 18.0, -22.0, 12.0, 108.0),
    "golden_hour": LumetriLook("golden_hour", 11.0, 4.0, 0.20, 14.0, -18.0, 16.0, 112.0),
    "bright_tour": LumetriLook("bright_tour", 3.0, 0.0, 0.35, 12.0, -28.0, 24.0, 106.0),
    "clean_studio": LumetriLook("clean_studio", 0.0, 0.0, 0.10, 15.0, -15.0, 8.0, 104.0),
}


def compute_ducking_envelope(
    speech_ranges: list[tuple[float, float]],
    total_duration: float,
    bed_db: float = -16.5,
    ducked_db: float = -25.0,
    ramp_sec: float = 0.22,
) -> list[tuple[float, float]]:
    """Generate `(time_sec, gain_db)` keyframes dipping music smoothly underneath voiceover segments."""
    points: list[tuple[float, float]] = [(0.0, bed_db)]
    for start, end in sorted(speech_ranges):
        pre = max(0.0, round(start - ramp_sec, 3))
        post = min(total_duration, round(end + ramp_sec, 3))
        points.append((pre, bed_db))
        points.append((round(start, 3), ducked_db))
        points.append((round(end, 3), ducked_db))
        points.append((post, bed_db))
    points.append((round(total_duration, 3), bed_db))
    return points


def generate_lumetri_jsx(look_name: str, video_track_index: int = 2) -> str:
    if look_name not in LOOK_CATALOG:
        raise ValueError(f"Unknown look '{look_name}'. Available: {', '.join(LOOK_CATALOG)}")
    lk = LOOK_CATALOG[look_name]
    return f"""// Auto-generated Lumetri Color Adjustment script ({lk.name})
(function() {{
    var seq = app.project.activeSequence;
    if (!seq) {{ return "ERR_NO_SEQUENCE"; }}
    var track = seq.videoTracks[{video_track_index}];
    if (!track || track.clips.numItems === 0) {{ return "ERR_EMPTY_TRACK"; }}
    var clip = track.clips[0];
    var props = {{
        "Temperature": {lk.temperature},
        "Tint": {lk.tint},
        "Exposure": {lk.exposure},
        "Contrast": {lk.contrast},
        "Highlights": {lk.highlights},
        "Shadows": {lk.shadows},
        "Saturation": {lk.saturation}
    }};
    for (var i = 0; i < clip.components.numItems; i++) {{
        var comp = clip.components[i];
        if (comp.displayName === "Lumetri Color") {{
            for (var p = 0; p < comp.properties.numItems; p++) {{
                var prop = comp.properties[p];
                if (props.hasOwnProperty(prop.displayName)) {{
                    prop.setValue(props[prop.displayName], true);
                }}
            }}
        }}
    }}
    return "OK:{lk.name}";
}})();
"""
