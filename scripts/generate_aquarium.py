#!/usr/bin/env python3
"""
Digital Aquarium Generator for GitHub Profile
==============================================
Generates a living pixel-art dark underwater aquarium animated GIF populated with
dynamic Nishikigoi (koi fish) influenced by GitHub contributions and milestones.

Features:
- Seamless infinite loop (48 frames @ 20 fps / 50ms)
- Multi-species koi ecosystem: Kohaku, Taisho Sanke, Showa, Asagi/Shusui,
  Platinum Ogon, Baby Fry, and the Rare Golden Yamabuki Koi.
- Realistic carangiform swimming locomotion (Lighthill slender-body wave).
- Deep navy oceanic aesthetic with caustics, rising bubbles, swaying flora, and sparkles.
- Scales 2x with nearest-neighbor interpolation for crisp retro pixel art.
"""

import argparse
import json
import math
import os
import random
import sys
import urllib.request
from PIL import Image, ImageDraw

WIDTH = 420
HEIGHT = 140
FRAMES = 48
FPS = 20

def fetch_activity(username, token=None):
    """Fetch GitHub profile activity to dynamically configure the aquarium ecosystem."""
    headers = {"User-Agent": "DigitalAquarium/2.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    stats = {
        "username": username,
        "repos": 12,
        "recent_activity": 25,
        "unlocked_gold": True,
        "unlocked_species": ["kohaku", "sanke", "asagi", "showa", "platinum", "gold", "fry"]
    }
    
    try:
        url = f"https://api.github.com/users/{username}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode())
            stats["repos"] = data.get("public_repos", 12)
            
        events_url = f"https://api.github.com/users/{username}/events/public?per_page=100"
        req_ev = urllib.request.Request(events_url, headers=headers)
        with urllib.request.urlopen(req_ev, timeout=6) as resp_ev:
            events = json.loads(resp_ev.read().decode())
            pushes = [e for e in events if e.get("type") == "PushEvent"]
            stats["recent_activity"] = len(pushes)
    except Exception as e:
        print(f"[Aquarium] Offline/sandbox mode or rate-limit reached ({e}). Using full ecosystem roster.")
        
    return stats

def create_background():
    """Generates the deep navy oceanic backdrop with textured bottom gravel and stones."""
    bg = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(bg)
    
    # Deep underwater navy gradient
    for y in range(HEIGHT):
        ratio = y / float(HEIGHT)
        r = int(14 * (1 - ratio) + 4 * ratio)
        g = int(34 * (1 - ratio) + 8 * ratio)
        b = int(62 * (1 - ratio) + 18 * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))
        
    # Bottom gravel substrate (y: 128..140)
    gravel_palette = [
        (15, 23, 42, 255),
        (30, 41, 59, 255),
        (51, 65, 85, 255),
        (71, 85, 105, 255),
        (12, 74, 110, 255),
    ]
    rng = random.Random(1337)
    for y in range(128, HEIGHT):
        for x in range(WIDTH):
            if y == 128 and rng.random() > 0.4:
                continue
            bg.putpixel((x, y), rng.choice(gravel_palette))
            
    # Resting rocks on gravel
    rocks = [(45, 127, 16, 7), (115, 128, 18, 6), (250, 127, 22, 9), (345, 128, 18, 7)]
    for rx, ry, rw, rh in rocks:
        for ox in range(-rw // 2, rw // 2):
            for oy in range(-rh // 2, rh // 2):
                if (ox * ox) / (rw * rw / 4.0) + (oy * oy) / (rh * rh / 4.0) <= 1.0:
                    px = rx + ox
                    py = ry + oy
                    if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                        col = (30, 41, 59, 255) if oy > 0 else (71, 85, 105, 255)
                        bg.putpixel((px, py), col)
                        
    return bg

def draw_light_rays(frame_img, t):
    """Draws subtle shimmering ambient caustics/light rays filtering down from surface."""
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    rays = [
        (55, 115, 24, 0.0),
        (155, 215, 34, 1.3),
        (275, 335, 28, 2.6),
        (365, 415, 20, 4.1),
    ]
    for top_x, bot_x, w, phase in rays:
        alpha = int(12 + 6 * math.sin(2 * math.pi * t + phase))
        col = (56, 189, 248, alpha)
        poly = [
            (top_x, 0),
            (top_x + w, 0),
            (bot_x + int(w * 1.5), HEIGHT - 15),
            (bot_x, HEIGHT - 15)
        ]
        draw.polygon(poly, fill=col)
        
    frame_img.alpha_composite(overlay)

def draw_surface_ripples(frame_img, t):
    """Draws animated tension ripples along the water surface."""
    draw = ImageDraw.Draw(frame_img)
    for x in range(WIDTH):
        w1 = math.sin(2 * math.pi * (t * 2.0 + x / 60.0))
        w2 = math.cos(2 * math.pi * (t * 3.0 - x / 40.0))
        sy = int(round(1.5 + 0.8 * w1 + 0.5 * w2))
        draw.point((x, sy), fill=(125, 211, 252, 180))
        if sy > 1:
            draw.point((x, sy - 1), fill=(56, 189, 248, 110))

def draw_plants(frame_img, t, foreground=False):
    """Draws pixel-art aquatic plants swaying gracefully with water current."""
    draw = ImageDraw.Draw(frame_img)
    plant_groups = [
        (12, 75, 5, 0.0, False),
        (25, 85, 6, 0.5, True),
        (38, 65, 4, 1.1, False),
        (90, 45, 3, 2.0, False),
        (310, 50, 4, 3.2, False),
        (385, 80, 5, 1.8, False),
        (398, 90, 7, 2.4, True),
        (410, 70, 4, 0.8, True),
    ]
    for px, max_h, count, phase, is_fg in plant_groups:
        if is_fg != foreground:
            continue
        for leaf in range(count):
            leaf_h = int(max_h * (0.65 + 0.35 * math.sin(leaf * 1.7)))
            leaf_offset_x = (leaf - count // 2) * 3
            leaf_phase = phase + leaf * 0.4
            
            for step in range(leaf_h):
                progress = step / float(leaf_h)
                y = 130 - step
                sway = 7.0 * (progress ** 1.8) * math.sin(2 * math.pi * (t + leaf_phase))
                x = int(round(px + leaf_offset_x + sway))
                
                if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                    if is_fg:
                        col = (16, 185, 129, 240) if progress < 0.7 else (52, 211, 153, 255)
                    else:
                        col = (5, 150, 105, 210) if progress < 0.7 else (16, 185, 129, 220)
                    draw.point((x, y), fill=col)
                    if is_fg and progress < 0.8:
                        draw.point((x + 1, y), fill=(4, 120, 87, 180))

def draw_bubbles(frame_img, t):
    """Draws rising aeration bubbles wobbling upwards."""
    draw = ImageDraw.Draw(frame_img)
    streams = [
        {"x": 75, "speed": 1.2, "n": 6, "wobble_freq": 3.0, "amp": 2.5},
        {"x": 195, "speed": 1.0, "n": 5, "wobble_freq": 2.5, "amp": 2.0},
        {"x": 265, "speed": 1.3, "n": 7, "wobble_freq": 3.5, "amp": 3.0},
        {"x": 365, "speed": 1.1, "n": 5, "wobble_freq": 2.8, "amp": 2.2},
    ]
    dist = 124.0
    for st in streams:
        for i in range(st["n"]):
            phase_i = i / float(st["n"])
            cur_prog = (t + phase_i) % 1.0
            y = int(128 - cur_prog * dist)
            wobble = st["amp"] * math.sin(2 * math.pi * (cur_prog * st["wobble_freq"] + phase_i * 4))
            x = int(round(st["x"] + wobble))
            
            if 0 <= x < WIDTH and 2 <= y < HEIGHT:
                alpha = int(160 + 80 * (1.0 - cur_prog * 0.4))
                if i % 3 == 0:
                    draw.point((x, y), fill=(224, 242, 254, alpha))
                    draw.point((x + 1, y), fill=(186, 230, 253, alpha - 40))
                    draw.point((x, y + 1), fill=(186, 230, 253, alpha - 40))
                else:
                    draw.point((x, y), fill=(224, 242, 254, alpha))

def get_koi_color(i, dist, max_dist, progress, species):
    """Calculates pixel colors for authentic Nishikigoi varieties with shading and patterns."""
    norm_y = dist / (max_dist if max_dist > 0 else 1)
    is_fin = progress > 0.84
    
    if species == "gold":
        # Yamabuki Ogon (Golden Koi Milestone)
        if is_fin:
            return (254, 240, 138, 200) if abs(norm_y) > 0.6 else (245, 158, 11, 230)
        if norm_y < -0.4:
            return (254, 240, 138, 255)
        elif norm_y < 0.25:
            return (251, 191, 36, 255) if (i % 2 == 0) else (245, 158, 11, 255)
        else:
            return (217, 119, 6, 255)
            
    elif species == "kohaku":
        # Scarlet and Pearl White
        is_red = (0.07 <= progress <= 0.28) or (0.42 <= progress <= 0.68)
        if is_fin:
            return (241, 245, 249, 180)
        if is_red:
            return (255, 107, 74, 255) if norm_y < -0.4 else ((234, 56, 32, 255) if norm_y < 0.3 else (185, 28, 28, 255))
        else:
            return (255, 255, 255, 255) if norm_y < -0.3 else ((241, 245, 249, 255) if norm_y < 0.3 else (203, 213, 225, 255))

    elif species == "sanke":
        # Taisho Sanke (White, Scarlet, Black)
        is_red = (0.08 <= progress <= 0.26) or (0.48 <= progress <= 0.70)
        is_black = (0.32 <= progress <= 0.44 and norm_y < 0.2) or (0.74 <= progress <= 0.82)
        if is_fin:
            return (241, 245, 249, 180)
        if is_black:
            return (30, 41, 59, 255) if norm_y < 0 else (15, 23, 42, 255)
        elif is_red:
            return (255, 99, 71, 255) if norm_y < 0 else (220, 38, 38, 255)
        else:
            return (255, 255, 255, 255) if norm_y < 0 else (226, 232, 240, 255)

    elif species == "asagi":
        # Shusui / Asagi (Cyan-Indigo Scaled Dorsal + Coral Belly & Fins)
        if is_fin:
            return (251, 113, 133, 210)
        if norm_y > 0.3:
            return (244, 63, 94, 255)
        else:
            is_net = (i + int(norm_y * 3)) % 2 == 0
            return (56, 189, 248, 255) if is_net else (14, 116, 144, 255)

    elif species == "showa":
        # Showa Sanshoku (Inky Shadow Black + Crimson + White)
        is_red = (0.20 <= progress <= 0.38) or (0.58 <= progress <= 0.72)
        is_white = (0.40 <= progress <= 0.54 and norm_y > -0.2)
        if is_fin:
            return (30, 41, 59, 200)
        if is_white:
            return (248, 250, 252, 255)
        elif is_red:
            return (239, 68, 68, 255) if norm_y < 0 else (185, 28, 28, 255)
        else:
            return (30, 41, 59, 255) if norm_y < 0 else (15, 23, 42, 255)

    elif species == "platinum":
        # Platinum Ogon (Metallic Pearl Silver)
        if is_fin:
            return (224, 242, 254, 170)
        return (255, 255, 255, 255) if norm_y < -0.3 else ((224, 231, 255, 255) if norm_y < 0.2 else (186, 200, 225, 255))

    else:
        # Baby Fry (Playful Mini Koi)
        if is_fin:
            return (254, 215, 170, 180)
        return (251, 146, 60, 255) if norm_y < 0 else (234, 88, 12, 255)

def render_koi_sprite(swim_cycle, length, species, facing_left):
    """Renders one pixel-art fish sprite in its dynamic undulating posture."""
    margin = 8
    w = length + margin * 2
    h = 24
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    swim_phase = swim_cycle * 2 * math.pi
    
    for i in range(length):
        progress = i / float(length)
        # Undulation: head steady, body and tail wagging with phase delay
        dy = 2.6 * (progress ** 1.8) * math.sin(swim_phase - progress * 4.2)
        
        if progress < 0.22:
            ht = 1.0 + 3.4 * math.sin((progress / 0.22) * math.pi / 2)
        elif progress < 0.68:
            ht = 4.4 * math.cos(((progress - 0.22) / 0.46) * math.pi * 0.42)
        elif progress < 0.84:
            ht = 1.4 - 0.4 * ((progress - 0.68) / 0.16)
        else:
            fin_p = (progress - 0.84) / 0.16
            ht = 1.0 + 3.8 * fin_p
            
        cy = (h / 2.0) + dy
        y_top = int(round(cy - ht))
        y_bottom = int(round(cy + ht))
        
        for y in range(y_top, y_bottom + 1):
            px = margin + i
            py = y
            if 0 <= px < w and 0 <= py < h:
                c = get_koi_color(i, y - cy, ht, progress, species)
                if c[3] > 0:
                    img.putpixel((px, py), c)
                    
    # Eye
    eye_x = margin + int(length * 0.16)
    eye_prog = 0.16
    eye_dy = 2.6 * (eye_prog ** 1.8) * math.sin(swim_phase - eye_prog * 4.2)
    eye_y = int(round((h / 2.0) + eye_dy - 1.2))
    img.putpixel((eye_x, eye_y), (15, 23, 42, 255))
    img.putpixel((eye_x + 1, eye_y - 1), (255, 255, 255, 220))
    
    # Whisker / Barbel
    mouth_x = margin + 1
    mouth_y = int(round((h / 2.0) + 1.2))
    w_col = (250, 204, 21, 200) if species == "gold" else (226, 232, 240, 180)
    img.putpixel((mouth_x - 1, mouth_y), w_col)
    
    # Pectoral Fin flutter
    fin_flutter = math.sin(swim_phase * 1.5)
    fin_x = margin + int(length * 0.32)
    fin_prog = 0.32
    fin_base_y = int(round((h / 2.0) + 2.6 * (fin_prog ** 1.8) * math.sin(swim_phase - fin_prog * 4.2) + 2.0))
    fin_col = (253, 224, 71, 210) if species == "gold" else (241, 245, 249, 190)
    if species == "asagi":
        fin_col = (251, 113, 133, 210)
    if fin_flutter > -0.2:
        img.putpixel((fin_x, fin_base_y), fin_col)
        img.putpixel((fin_x - 1, fin_base_y + 1), fin_col)
        if fin_flutter > 0.3:
            img.putpixel((fin_x - 2, fin_base_y + 2), fin_col)

    if facing_left:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
        
    return img

def build_aquarium(output_path="assets/aquarium.gif", username="adityamandre25", token=None):
    """Builds and writes the complete digital aquarium GIF."""
    print(f"[Aquarium] Initializing aquarium for @{username}...")
    activity = fetch_activity(username, token)
    
    bg = create_background()
    
    # Dynamic School of Fish
    fish_roster = [
        {"species": "gold", "x0": 210, "y0": 62, "ax": 110, "ay": 14, "kx": 1, "ky": 2, "phi": 0.0, "wag": 6, "len": 32, "fg": True},
        {"species": "kohaku", "x0": 130, "y0": 42, "ax": 85, "ay": 10, "kx": 1, "ky": 1, "phi": 1.4, "wag": 6, "len": 28, "fg": True},
        {"species": "sanke", "x0": 290, "y0": 85, "ax": 95, "ay": 12, "kx": 1, "ky": 1, "phi": 3.1, "wag": 6, "len": 27, "fg": False},
        {"species": "asagi", "x0": 220, "y0": 102, "ax": 80, "ay": 8, "kx": 1, "ky": 2, "phi": 4.6, "wag": 8, "len": 26, "fg": False},
        {"species": "showa", "x0": 95, "y0": 78, "ax": 70, "ay": 15, "kx": 1, "ky": 1, "phi": 2.2, "wag": 6, "len": 29, "fg": True},
        {"species": "platinum", "x0": 320, "y0": 38, "ax": 75, "ay": 9, "kx": 1, "ky": 1, "phi": 5.1, "wag": 8, "len": 25, "fg": False},
        {"species": "fry", "x0": 170, "y0": 28, "ax": 55, "ay": 11, "kx": 2, "ky": 2, "phi": 0.7, "wag": 12, "len": 15, "fg": True},
    ]
    
    frames = []
    print(f"[Aquarium] Rendering {FRAMES} looping animation frames...")
    
    for f in range(FRAMES):
        t = f / float(FRAMES)
        frame_img = bg.copy()
        
        # 1. Ambient lighting caustics
        draw_light_rays(frame_img, t)
        
        # 2. Surface ripples
        draw_surface_ripples(frame_img, t)
        
        # 3. Background aquatic plants
        draw_plants(frame_img, t, foreground=False)
        
        # 4. Swim simulation and rendering
        for pass_fg in [False, True]:
            for fish in fish_roster:
                if fish["fg"] != pass_fg:
                    continue
                    
                angle_x = 2 * math.pi * fish["kx"] * t + fish["phi"]
                angle_y = 2 * math.pi * fish["ky"] * t + fish["phi"]
                x = fish["x0"] + fish["ax"] * math.cos(angle_x)
                y = fish["y0"] + fish["ay"] * math.sin(angle_y)
                
                vx = -2 * math.pi * fish["kx"] * fish["ax"] * math.sin(angle_x)
                facing_left = (vx < 0)
                
                swim_cycle = (t * fish["wag"]) % 1.0
                sprite = render_koi_sprite(swim_cycle, fish["len"], fish["species"], facing_left)
                
                # Rare golden koi luminous sparkles
                if fish["species"] == "gold":
                    sparkle_draw = ImageDraw.Draw(frame_img)
                    sp_x = int(x + (38 if facing_left else -6) + 4 * math.sin(t * 12))
                    sp_y = int(y + 6 * math.cos(t * 8))
                    sparkle_draw.point((sp_x, sp_y), fill=(254, 240, 138, 200))
                    sparkle_draw.point((sp_x + 1, sp_y), fill=(255, 255, 255, 220))
                    
                paste_x = int(round(x - sprite.width // 2))
                paste_y = int(round(y - sprite.height // 2))
                frame_img.alpha_composite(sprite, (paste_x, paste_y))
                
        # 5. Foreground plants
        draw_plants(frame_img, t, foreground=True)
        
        # 6. Rising aeration bubbles
        draw_bubbles(frame_img, t)
        
        # 7. Scale 2x with NEAREST interpolation for authentic crisp pixel art
        scaled_frame = frame_img.resize((WIDTH * 2, HEIGHT * 2), Image.Resampling.NEAREST)
        
        # Convert to P mode without dithering for sharp pixels and low file size
        p_frame = scaled_frame.convert("RGB").convert("P", palette=Image.Palette.ADAPTIVE, colors=128, dither=Image.Dither.NONE)
        frames.append(p_frame)
        
    print(f"[Aquarium] Compiling optimized GIF to {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=50,
        loop=0,
        optimize=True
    )
    size_kb = os.path.getsize(output_path) / 1024
    print(f"[Aquarium] Done! Output: {output_path} ({size_kb:.1f} KB)")

def main():
    parser = argparse.ArgumentParser(description="Generate Digital Aquarium for GitHub Profile")
    parser.add_argument("--username", default="adityamandre25", help="GitHub username")
    parser.add_argument("--output", default="assets/aquarium.gif", help="Output GIF path")
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN"), help="GitHub token")
    args = parser.parse_args()
    
    build_aquarium(output_path=args.output, username=args.username, token=args.token)

if __name__ == "__main__":
    main()
