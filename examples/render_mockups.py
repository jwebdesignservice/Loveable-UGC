"""Render carousel slide mockups as PNGs in 9:16 and 1:1.

Outputs to examples/png-9x16/ and examples/png-1x1/.
"""
from PIL import Image, ImageDraw, ImageFont
import os

FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"

PAPER = (240, 235, 226)
INK = (22, 21, 19)
MUTED = (107, 102, 96)
DARK_BG = (22, 21, 19)
DARK_INK = (241, 237, 229)
DARK_MUTED = (140, 134, 125)


def font(size, bold=False, mono=False, serif=False, serif_bold=False):
    if serif_bold:
        path = FONT_SERIF_BOLD
    elif serif:
        path = FONT_SERIF
    elif mono:
        path = FONT_MONO
    elif bold:
        path = FONT_BOLD
    else:
        path = FONT_REG
    return ImageFont.truetype(path, size)


def wrap(text, fnt, max_w, d):
    out = []
    for paragraph in text.split('\n'):
        words = paragraph.split(' ')
        line = []
        for w in words:
            test = ' '.join(line + [w])
            bb = d.textbbox((0, 0), test, font=fnt)
            if bb[2] - bb[0] > max_w and line:
                out.append(' '.join(line))
                line = [w]
            else:
                line.append(w)
        if line:
            out.append(' '.join(line))
    return out


def draw_wrapped(d, xy, text, fnt, fill, max_w, lh_factor=1.15):
    lines = wrap(text, fnt, max_w, d)
    x, y = xy
    bb = d.textbbox((0, 0), 'Mg', font=fnt)
    lh = int((bb[3] - bb[1]) * lh_factor)
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def slide_number(d, W, H, num, color):
    if not num:
        return
    f = font(int(W * 0.024))
    d.text((W - int(W * 0.075), int(W * 0.045)), num, font=f, fill=color, anchor='ra')


def slide_text(W, H, headline, sub=None, body=None, footer=None, num=None, dark=False):
    bg = DARK_BG if dark else PAPER
    ink = DARK_INK if dark else INK
    muted = DARK_MUTED if dark else MUTED
    img = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(img)
    pad = int(W * 0.085)
    slide_number(d, W, H, num, muted)

    y = int(H * 0.17) if H > W else int(H * 0.14)
    f_head = font(int(W * 0.082), bold=True)
    y = draw_wrapped(d, (pad, y), headline, f_head, ink, W - pad * 2, 1.08)

    if sub:
        y += int(W * 0.025)
        f_sub = font(int(W * 0.034))
        y = draw_wrapped(d, (pad, y), sub, f_sub, muted, W - pad * 2, 1.3)

    if body:
        y += int(W * 0.06)
        f_body = font(int(W * 0.04))
        y = draw_wrapped(d, (pad, y), body, f_body, ink, W - pad * 2, 1.4)

    if footer:
        f_foot = font(int(W * 0.028))
        d.text((pad, H - int(W * 0.085)), footer, font=f_foot, fill=muted)

    return img


def draw_preview(d, box, kind):
    x1, y1, x2, y2 = box
    bw = x2 - x1
    bh = y2 - y1
    radius = int(bw * 0.03)
    inner_pad = int(bw * 0.06)

    if kind == 'dark':
        d.rounded_rectangle(box, radius=radius, fill=(26, 26, 26))
        dot_color = (68, 68, 68)
        pill_bg = (255, 255, 255)
        pill_text = (17, 17, 17)
        head_color = (240, 240, 240)
        body_color = (160, 160, 160)
        grid_color = (42, 42, 42)
        pill_label = 'v1.0 — out now'
        head_text = 'Stop scheduling.\nStart showing up.'
        body_text = "The AI that books your week so you don't have to."
    elif kind == 'warm':
        d.rounded_rectangle(box, radius=radius, fill=(243, 236, 225))
        dot_color = (212, 204, 192)
        pill_bg = (17, 17, 17)
        pill_text = (255, 255, 255)
        head_color = (26, 26, 26)
        body_color = (90, 83, 75)
        grid_color = (230, 221, 205)
        pill_label = 'Book a visit'
        head_text = "Joe's Plumbing"
        body_text = 'Family-owned. Same-day service across the city since 1987.'
    elif kind == 'before':
        d.rounded_rectangle(box, radius=radius, fill=(221, 221, 221))
        _draw_before(d, box)
        return

    cx = x1 + inner_pad
    cy = y1 + inner_pad
    r = int(bw * 0.012)
    for i in range(3):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=dot_color)
        cx += int(bw * 0.045)

    pill_y = y1 + inner_pad + int(bw * 0.07)
    fp = font(int(bw * 0.03))
    tb = d.textbbox((0, 0), pill_label, font=fp)
    tw = tb[2] - tb[0]
    pill_h = int(bw * 0.07)
    pill_x2 = x1 + inner_pad + tw + int(bw * 0.06)
    d.rounded_rectangle(
        (x1 + inner_pad, pill_y, pill_x2, pill_y + pill_h),
        radius=pill_h // 2, fill=pill_bg
    )
    d.text((x1 + inner_pad + int(bw * 0.03), pill_y + int(pill_h * 0.18)),
           pill_label, font=fp, fill=pill_text)

    h_y = pill_y + int(bw * 0.13)
    fh = font(int(bw * 0.062), bold=True)
    for line in head_text.split('\n'):
        d.text((x1 + inner_pad, h_y), line, font=fh, fill=head_color)
        h_y += int(bw * 0.072)

    b_y = h_y + int(bw * 0.015)
    fb = font(int(bw * 0.03))
    for line in wrap(body_text, fb, bw - inner_pad * 2, d):
        d.text((x1 + inner_pad, b_y), line, font=fb, fill=body_color)
        b_y += int(bw * 0.042)

    grid_h = int(bw * 0.13)
    gy1 = y2 - inner_pad - grid_h
    gw = (bw - inner_pad * 2 - int(bw * 0.025)) // 2
    d.rounded_rectangle((x1 + inner_pad, gy1, x1 + inner_pad + gw, gy1 + grid_h),
                        radius=int(bw * 0.018), fill=grid_color)
    d.rounded_rectangle((x1 + inner_pad + gw + int(bw * 0.025), gy1,
                         x1 + inner_pad + gw * 2 + int(bw * 0.025), gy1 + grid_h),
                        radius=int(bw * 0.018), fill=grid_color)


def _draw_before(d, box):
    x1, y1, x2, y2 = box
    bw = x2 - x1
    inner_pad = int(bw * 0.06)
    cx = x1 + inner_pad
    cy = y1 + inner_pad
    r = int(bw * 0.012)
    for _ in range(3):
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(170, 170, 170))
        cx += int(bw * 0.045)

    h_y = y1 + inner_pad + int(bw * 0.06)
    fh = font(int(bw * 0.055), serif_bold=True)
    head = "Welcome to Joe's Plumbing!!!"
    d.text((x1 + inner_pad, h_y), head, font=fh, fill=(0, 0, 180))
    tb = d.textbbox((x1 + inner_pad, h_y), head, font=fh)
    d.line((tb[0], tb[3] + 2, tb[2], tb[3] + 2), fill=(0, 0, 180), width=3)

    b_y = h_y + int(bw * 0.085)
    fb = font(int(bw * 0.03), serif=True)
    body = 'We are the best plumbers in town. Click here for quote. Family owned since 1987.'
    for line in wrap(body, fb, bw - inner_pad * 2, d):
        d.text((x1 + inner_pad, b_y), line, font=fb, fill=(85, 85, 85))
        b_y += int(bw * 0.04)

    btn_y = b_y + int(bw * 0.025)
    btn = 'CLICK HERE NOW'
    fbt = font(int(bw * 0.032), bold=True)
    tb = d.textbbox((0, 0), btn, font=fbt)
    tw = tb[2] - tb[0]
    btn_pad_x = int(bw * 0.035)
    btn_h = int(bw * 0.08)
    d.rectangle((x1 + inner_pad, btn_y, x1 + inner_pad + tw + btn_pad_x * 2, btn_y + btn_h),
                fill=(255, 255, 0), outline=(204, 0, 0), width=3)
    d.text((x1 + inner_pad + btn_pad_x, btn_y + int(btn_h * 0.22)), btn, font=fbt, fill=(0, 0, 0))

    grid_h = int(bw * 0.13)
    gy1 = y2 - inner_pad - grid_h
    gw = (bw - inner_pad * 2 - int(bw * 0.025)) // 2
    d.rectangle((x1 + inner_pad, gy1, x1 + inner_pad + gw, gy1 + grid_h), fill=(192, 192, 192))
    d.rectangle((x1 + inner_pad + gw + int(bw * 0.025), gy1,
                 x1 + inner_pad + gw * 2 + int(bw * 0.025), gy1 + grid_h), fill=(192, 192, 192))


def slide_with_preview(W, H, headline, sub, preview_type, num):
    img = Image.new('RGB', (W, H), PAPER)
    d = ImageDraw.Draw(img)
    pad = int(W * 0.085)
    slide_number(d, W, H, num, MUTED)

    y = int(H * 0.09) if H > W else int(H * 0.07)
    f_head = font(int(W * 0.072), bold=True)
    y = draw_wrapped(d, (pad, y), headline, f_head, INK, W - pad * 2, 1.08)

    if sub:
        y += int(W * 0.022)
        f_sub = font(int(W * 0.032))
        y = draw_wrapped(d, (pad, y), sub, f_sub, MUTED, W - pad * 2, 1.3)

    y += int(W * 0.045)
    preview_box = (pad, y, W - pad, H - pad)
    draw_preview(d, preview_box, preview_type)
    return img


def slide_prompt(W, H, prompt_text, label, num, dark=False):
    bg = DARK_BG if dark else PAPER
    ink = DARK_INK if dark else INK
    muted = DARK_MUTED if dark else MUTED
    img = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(img)
    pad = int(W * 0.085)
    slide_number(d, W, H, num, muted)

    card_x1 = pad
    card_y1 = int(H * 0.22) if H > W else int(H * 0.18)
    card_x2 = W - pad
    card_y2 = H - pad - int(W * 0.04)
    d.rounded_rectangle((card_x1, card_y1, card_x2, card_y2),
                        radius=int(W * 0.025), fill=(255, 255, 255))

    inner = int(W * 0.055)
    f_lbl = font(int(W * 0.025), bold=True)
    d.text((card_x1 + inner, card_y1 + inner), label.upper(), font=f_lbl, fill=MUTED)

    f_p = font(int(W * 0.04), mono=True)
    y = card_y1 + inner + int(W * 0.06)
    for line in wrap(prompt_text, f_p, card_x2 - card_x1 - inner * 2, d):
        d.text((card_x1 + inner, y), line, font=f_p, fill=(26, 26, 26))
        y += int(W * 0.058)

    return img


slides = [
    {'name': 'c1-s1-revamp-before',
     'render': lambda W, H: slide_with_preview(W, H, "this homepage\nis rough.", "found this in the wild today", 'before', "1 / 3")},
    {'name': 'c1-s2-revamp-after',
     'render': lambda W, H: slide_with_preview(W, H, "one prompt\nin lovable.", "no figma. no code.", 'warm', "2 / 3")},
    {'name': 'c1-s3-revamp-cta',
     'render': lambda W, H: slide_text(W, H, "4 minutes.\nthat's it.", None,
                                       "lovable wrote every line of this site. i just told it what the business does.",
                                       "comment 'revamp' if you want yours done →", "3 / 3")},

    {'name': 'c2-s1-prompt-hook',
     'render': lambda W, H: slide_text(W, H, "i gave lovable\n18 words.", "this is what came back ↓", None, None, "1 / 4")},
    {'name': 'c2-s2-prompt-text',
     'render': lambda W, H: slide_prompt(W, H, "dark editorial landing page for an AI scheduling tool. one hero, three features, pricing, FAQ.",
                                         "the prompt", "2 / 4")},
    {'name': 'c2-s3-prompt-result',
     'render': lambda W, H: slide_with_preview(W, H, "here's what\nit built.", None, 'dark', "3 / 4")},
    {'name': 'c2-s4-prompt-cta',
     'render': lambda W, H: slide_text(W, H, "steal the prompt.", "save this for the next site you build", None,
                                       "following for more →", "4 / 4", dark=True)},

    {'name': 'c3-s1-mistake-bad',
     'render': lambda W, H: slide_with_preview(W, H, "everyone using\nlovable does this.",
                                               "and it's why every site looks the same", 'dark', "1 / 3")},
    {'name': 'c3-s2-mistake-fix',
     'render': lambda W, H: slide_text(W, H, "do this instead.", None,
                                       "'build faster, ship better'\n↓\nsay what the thing actually is.",
                                       "specificity > vibes.", "2 / 3")},
    {'name': 'c3-s3-mistake-prompt',
     'render': lambda W, H: slide_prompt(W, H,
                                         "the hero headline must name the exact product and who it's for. no buzzwords. no 'build faster' style copy.",
                                         "add this to every prompt", "3 / 3")},
]


os.makedirs('examples/png-9x16', exist_ok=True)
os.makedirs('examples/png-1x1', exist_ok=True)

for s in slides:
    s['render'](1080, 1920).save(f"examples/png-9x16/{s['name']}.png", optimize=True)
    s['render'](1080, 1080).save(f"examples/png-1x1/{s['name']}.png", optimize=True)
    print(s['name'])

print('Done.')
