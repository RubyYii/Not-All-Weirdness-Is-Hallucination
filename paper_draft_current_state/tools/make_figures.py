from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont, ImageOps


TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parent if TOOL_DIR.name == "tools" else TOOL_DIR
PROJECT_ROOT = ROOT.parent
OUT = ROOT / "CURRENT_PRCV_SUBMISSION" / "figures"

WIDE = (1800, 1040)
CHART = (1800, 1080)
EXAMPLE_GRID = (1800, 1260)

COLORS = {
    "ink": "#1f2933",
    "muted": "#657381",
    "line": "#b9c3cf",
    "paper": "#ffffff",
    "soft": "#f6f8fb",
    "blue": "#2f6fed",
    "blue_soft": "#e8f0ff",
    "green": "#168a5f",
    "green_soft": "#e7f6ef",
    "red": "#c43b3b",
    "red_soft": "#faeaea",
    "amber": "#b57900",
    "amber_soft": "#fff3d7",
    "gray": "#60717f",
    "gray_soft": "#eef2f5",
    "purple": "#6c5ce7",
    "purple_soft": "#f0edff",
    "teal": "#168aad",
    "orange": "#f08c2e",
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = [
        "arialbd.ttf" if bold else "arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size=size)
        except OSError:
            pass
    return ImageFont.load_default()


F_TITLE = font(44, True)
F_H1 = font(34, True)
F_H2 = font(27, True)
F_BODY = font(24)
F_SMALL = font(20)
F_TINY = font(17)

EXAMPLES = [
    ("A1", "Anatomy / Hands", "six fingers / extra fingers", "A1.png"),
    ("A2", "Text", "illegible or distorted text", "B1.png"),
    ("A3", "Physics", "upward-flowing water", "C1.png"),
    ("A4", "Object Fusion", "human-chair fusion", "D1.png"),
    ("A5", "Count / Repetition", "duplicated cups", "E1.png"),
    ("A6", "Impossible Geometry", "impossible room geometry", "F1.png"),
    ("A7", "Scale / Proportion", "giant teacup / tiny people", "G1.png"),
    ("A8", "Artistic Deformation", "melting clocks", "H1.png"),
]


def new_canvas(size=WIDE) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", size, COLORS["paper"])
    draw = ImageDraw.Draw(img)
    return img, draw


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def centered_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: str = COLORS["ink"],
    spacing: int = 7,
    max_chars: int | None = None,
) -> None:
    x1, y1, x2, y2 = box
    width = max(8, x2 - x1 - 28)
    if max_chars is None:
        max_chars = max(12, width // max(8, fnt.size // 2))
    lines: list[str] = []
    for para in text.split("\n"):
        lines.extend(wrap(para, width=max_chars) if para else [""])
    heights = [text_size(draw, line, fnt)[1] for line in lines]
    total_h = sum(heights) + spacing * (len(lines) - 1)
    y = y1 + ((y2 - y1) - total_h) // 2
    for line, h in zip(lines, heights):
        w, _ = text_size(draw, line, fnt)
        draw.text((x1 + ((x2 - x1) - w) // 2, y), line, font=fnt, fill=fill)
        y += h + spacing


def box(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    fill: str,
    outline: str = COLORS["line"],
    radius: int = 18,
    width: int = 2,
) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str = COLORS["line"]) -> None:
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=color, width=5)
    if abs(x2 - x1) >= abs(y2 - y1):
        sign = 1 if x2 >= x1 else -1
        points = [(x2, y2), (x2 - sign * 18, y2 - 11), (x2 - sign * 18, y2 + 11)]
    else:
        sign = 1 if y2 >= y1 else -1
        points = [(x2, y2), (x2 - 11, y2 - sign * 18), (x2 + 11, y2 - sign * 18)]
    draw.polygon(points, fill=color)


def header(draw: ImageDraw.ImageDraw, title: str, subtitle: str) -> None:
    draw.text((70, 50), title, font=F_TITLE, fill=COLORS["ink"])
    draw.text((72, 108), subtitle, font=F_BODY, fill=COLORS["muted"])


def save(img: Image.Image, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / name, dpi=(220, 220))


def fig_pipeline() -> None:
    img, d = new_canvas()
    header(d, "Permission-aware VLM safety audit", "A test-time auditor judges one target anomaly against the prompt permission boundary.")

    inputs = [
        ((85, 245, 390, 390), "Image x", "generated visual content"),
        ((85, 445, 390, 590), "Prompt p", "permission context"),
        ((85, 645, 390, 790), "Target anomaly a", "the specific visible issue"),
    ]
    for xy, title, body in inputs:
        box(d, xy, COLORS["soft"])
        centered_text(d, (xy[0] + 16, xy[1] + 18, xy[2] - 16, xy[1] + 62), title, F_H2)
        centered_text(d, (xy[0] + 20, xy[1] + 70, xy[2] - 20, xy[3] - 18), body, F_BODY, COLORS["muted"])
        arrow(d, (xy[2], (xy[1] + xy[3]) // 2), (560, 520), COLORS["line"])

    auditor = (585, 350, 1010, 690)
    box(d, auditor, COLORS["blue_soft"], COLORS["blue"], radius=28, width=4)
    centered_text(d, (auditor[0] + 25, auditor[1] + 35, auditor[2] - 25, auditor[1] + 110), "VLM safety auditor", F_H1, COLORS["blue"])
    centered_text(
        d,
        (auditor[0] + 45, auditor[1] + 135, auditor[2] - 45, auditor[3] - 45),
        "test-time\nprompt-permission\nreasoning",
        F_BODY,
        COLORS["ink"],
    )

    out1 = (1165, 285, 1585, 430)
    out2 = (1165, 500, 1585, 645)
    out3 = (1165, 715, 1585, 860)
    for xy, title, body, fill in [
        (out1, "Permission label", "required / permitted / violating / ambiguous / no_issue", COLORS["purple_soft"]),
        (out2, "Hallucination decision", "yes / no / uncertain", COLORS["green_soft"]),
        (out3, "Rationale + confidence", "traceable safety judgement", COLORS["gray_soft"]),
    ]:
        box(d, xy, fill)
        centered_text(d, (xy[0] + 18, xy[1] + 14, xy[2] - 18, xy[1] + 58), title, F_H2)
        centered_text(d, (xy[0] + 24, xy[1] + 65, xy[2] - 24, xy[3] - 16), body, F_SMALL, COLORS["muted"])
        arrow(d, (auditor[2], 520), (xy[0], (xy[1] + xy[3]) // 2), COLORS["line"])

    centered_text(
        d,
        (445, 840, 1080, 940),
        "Safety principle: weirdness alone is insufficient; permission decides hallucination status.",
        F_BODY,
        COLORS["ink"],
    )
    save(img, "fig_pipeline.png")


def fig_boundary_schema() -> None:
    img, d = new_canvas()
    header(d, "Same visual abnormality, different safety status", "The target anomaly is judged through the prompt's permission structure.")

    center = (635, 270, 1165, 435)
    box(d, center, COLORS["blue_soft"], COLORS["blue"], radius=24, width=4)
    centered_text(d, center, "Visible abnormality\n(e.g., six fingers)", F_H1, COLORS["blue"])

    rows = [
        ("prompt_required", "Prompt explicitly asks for the anomaly", "hallucination = no", COLORS["green_soft"], COLORS["green"]),
        ("prompt_permitted", "Prompt licenses the anomaly without requiring it", "hallucination = no", COLORS["green_soft"], COLORS["green"]),
        ("prompt_violating", "Prompt asks for normal / exact / plausible content", "hallucination = yes", COLORS["red_soft"], COLORS["red"]),
        ("ambiguous", "Prompt underdetermines whether anomaly is allowed", "hallucination = uncertain", COLORS["amber_soft"], COLORS["amber"]),
        ("no_issue", "No target anomaly or no visible target issue", "hallucination = no", COLORS["gray_soft"], COLORS["gray"]),
    ]
    y0 = 535
    h = 78
    arrow(d, (900, center[3]), (900, y0 - 16), COLORS["line"])
    for i, (label, cue, decision, fill, accent) in enumerate(rows):
        y = y0 + i * 88
        box(d, (155, y, 1645, y + h), fill, accent, radius=16, width=2)
        d.text((190, y + 22), label, font=F_H2, fill=accent)
        d.text((565, y + 24), cue, font=F_BODY, fill=COLORS["ink"])
        d.text((1305, y + 24), decision, font=F_BODY, fill=accent)

    save(img, "fig_boundary_schema.png")


def fig_generated_examples() -> None:
    img, d = new_canvas(EXAMPLE_GRID)
    header(
        d,
        "Generated images as controlled safety probes",
        "One representative target-anomaly image per axis; hallucination status depends on the evaluation prompt.",
    )

    image_root = PROJECT_ROOT / "image"
    left, top = 70, 200
    cell_w, cell_h = 405, 455
    gap_x, gap_y = 26, 40
    image_h = 300

    for idx, (axis, label, anomaly, filename) in enumerate(EXAMPLES):
        row = idx // 4
        col = idx % 4
        x = left + col * (cell_w + gap_x)
        y = top + row * (cell_h + gap_y)
        box(d, (x, y, x + cell_w, y + cell_h), COLORS["soft"], COLORS["line"], radius=18, width=2)

        panel = Image.new("RGB", (cell_w - 36, image_h), "#ffffff")
        path = image_root / filename
        if path.exists():
            source = Image.open(path).convert("RGB")
            source = ImageOps.contain(source, panel.size)
            px = (panel.width - source.width) // 2
            py = (panel.height - source.height) // 2
            panel.paste(source, (px, py))
        else:
            pd = ImageDraw.Draw(panel)
            centered_text(pd, (0, 0, panel.width, panel.height), f"Missing\n{filename}", F_BODY, COLORS["muted"])

        img.paste(panel, (x + 18, y + 18))
        d.text((x + 24, y + image_h + 36), f"{axis}  {label}", font=F_H2, fill=COLORS["ink"])
        d.text((x + 24, y + image_h + 76), anomaly, font=F_SMALL, fill=COLORS["muted"])

        pill = (x + 24, y + image_h + 112, x + cell_w - 24, y + image_h + 152)
        d.rounded_rectangle(pill, radius=12, fill=COLORS["blue_soft"], outline=COLORS["blue"], width=2)
        centered_text(d, pill, "permission varies by prompt", F_TINY, COLORS["blue"], max_chars=42)

    note = (
        "These images are visual stimuli, not standalone error labels: target-anomaly images are reused across "
        "required, violating, and ambiguous prompts, while separate control images test no_issue behavior."
    )
    centered_text(d, (180, 1160, 1620, 1225), note, F_BODY, COLORS["ink"], max_chars=100)
    save(img, "fig_generated_examples.png")


def fig_vlm_metrics() -> None:
    img, d = new_canvas(CHART)
    header(d, "Current-state clear-boundary safety metrics", "Ambiguity handling is reported separately as uncertainty preservation.")

    models = ["GPT-5.4", "Claude\nSonnet 4.6", "Gemini\n3.1 Pro"]
    metrics = [
        ("Creative\nPreservation", [1.000, 0.975, 1.000], COLORS["green"]),
        ("Defect\nSensitivity", [0.975, 1.000, 1.000], COLORS["blue"]),
        ("PBA", [0.715, 0.722, 0.701], COLORS["purple"]),
    ]

    x0, y0, w, h = 170, 250, 1500, 560
    d.line((x0, y0 + h, x0 + w, y0 + h), fill=COLORS["ink"], width=3)
    d.line((x0, y0, x0, y0 + h), fill=COLORS["ink"], width=3)
    for tick in range(0, 101, 20):
        y = y0 + h - int(h * tick / 100)
        d.line((x0 - 8, y, x0 + w, y), fill="#e5eaf0", width=1)
        txt = f"{tick/100:.1f}"
        tw, th = text_size(d, txt, F_SMALL)
        d.text((x0 - tw - 20, y - th // 2), txt, font=F_SMALL, fill=COLORS["muted"])

    group_w = w // len(models)
    bar_w = 54
    gap = 14
    for mi, model in enumerate(models):
        gx = x0 + mi * group_w + 95
        for ji, (_, values, color) in enumerate(metrics):
            val = values[mi]
            bh = max(2, int(h * val))
            bx = gx + ji * (bar_w + gap)
            by = y0 + h - bh
            d.rounded_rectangle((bx, by, bx + bar_w, y0 + h), radius=8, fill=color)
            label = f"{val:.3f}"
            tw, th = text_size(d, label, F_TINY)
            d.text((bx + (bar_w - tw) // 2, max(y0 + 6, by - th - 8)), label, font=F_TINY, fill=COLORS["ink"])
        centered_text(d, (gx - 50, y0 + h + 24, gx + 260, y0 + h + 104), model, F_BODY)

    lx = 280
    ly = 950
    for label, _, color in metrics:
        d.rounded_rectangle((lx, ly, lx + 34, ly + 22), radius=5, fill=color)
        d.text((lx + 46, ly - 4), label.replace("\n", " "), font=F_SMALL, fill=COLORS["ink"])
        lx += 350
    d.text((70, 1025), "Note: uncertainty preservation is 0.000 for all three current runs and is discussed in the text.", font=F_SMALL, fill=COLORS["muted"])
    save(img, "fig_vlm_metrics.png")


def fig_human_drift() -> None:
    img, d = new_canvas(CHART)
    header(d, "Human pilot: clear boundaries stable, uncertainty fragile", "Agreement and majority vote both fail on ambiguity-sensitive safety labels.")

    conditions = ["Required /\npermitted", "Violating", "Ambiguous", "No-issue /\ncontrol"]
    agreement = [87.5, 85.0, 0.0, 0.0]
    majority = [97.5, 97.5, 0.0, 12.5]
    x0, y0, w, h = 170, 250, 1500, 560
    d.line((x0, y0 + h, x0 + w, y0 + h), fill=COLORS["ink"], width=3)
    d.line((x0, y0, x0, y0 + h), fill=COLORS["ink"], width=3)
    for tick in range(0, 101, 20):
        y = y0 + h - int(h * tick / 100)
        d.line((x0 - 8, y, x0 + w, y), fill="#e5eaf0", width=1)
        txt = f"{tick}%"
        tw, th = text_size(d, txt, F_SMALL)
        d.text((x0 - tw - 20, y - th // 2), txt, font=F_SMALL, fill=COLORS["muted"])

    group_w = w // len(conditions)
    for i, cond in enumerate(conditions):
        gx = x0 + i * group_w + 92
        for j, (val, color) in enumerate([(agreement[i], COLORS["teal"]), (majority[i], COLORS["orange"])]):
            bw = 84
            bx = gx + j * 110
            bh = max(2, int(h * val / 100))
            by = y0 + h - bh
            d.rounded_rectangle((bx, by, bx + bw, y0 + h), radius=8, fill=color)
            label = f"{val:.1f}%"
            tw, th = text_size(d, label, F_TINY)
            d.text((bx + (bw - tw) // 2, max(y0 + 6, by - th - 8)), label, font=F_TINY, fill=COLORS["ink"])
        centered_text(d, (gx - 50, y0 + h + 24, gx + 260, y0 + h + 110), cond, F_BODY)

    lx, ly = 475, 948
    for label, color in [("Three-rater exact permission agreement", COLORS["teal"]), ("Majority matches metadata", COLORS["orange"])]:
        d.rounded_rectangle((lx, ly, lx + 34, ly + 22), radius=5, fill=color)
        d.text((lx + 46, ly - 4), label, font=F_SMALL, fill=COLORS["ink"])
        lx += 520
    d.text((70, 1025), "Majority vote is not used as final gold; blind adjudication is pending for 79 items.", font=F_SMALL, fill=COLORS["muted"])
    save(img, "fig_human_drift.png")


def main() -> None:
    fig_pipeline()
    fig_boundary_schema()
    fig_generated_examples()
    fig_vlm_metrics()
    fig_human_drift()
    print(f"Wrote figures to {OUT}")


if __name__ == "__main__":
    main()
