#!/usr/bin/env python3
"""
Living Evolving Aquarium Generator for GitHub Profile
=====================================================
A dynamic underwater ecosystem that visually evolves based on cumulative
merged pull request milestones for @adityamandre25.

Progression System:
- Tier 1 (0–5 PRs): Starter Shallows (School of Neon Tetras & Playful Clownfish)
- Tier 2 (6–15 PRs): Coral Shallows (Regal Blue Tang unlocked, fish grow +15%)
- Tier 3 (16–30 PRs): Azure Haven (Royal Amazonian Discus unlocked, enhanced iridescence)
- Tier 4 (31–50 PRs): Abyssal Sanctuary (Altum Angelfish unlocked, sweeping fins)
- Tier 5 (51–100 PRs): Imperial Reef (Golden Arowana unlocked, golden dust motes)
- Tier 6 (100+ PRs): Legendary Sovereign Realm (Grand mature ecosystem, maximum size & vitality)
"""

import argparse
import datetime
import json
import math
import os
import random
import sys
import urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CANVAS_WIDTH = 760
CANVAS_HEIGHT = 280
TOTAL_FRAMES = 32
FRAME_DURATION = 75  # ms -> ~13.3 fps, 2.4s seamless loop

EVOLUTION_TIERS = [
    {
        "tier": 1,
        "name": "Starter Shallows",
        "min_prs": 0,
        "max_prs": 5,
        "species": ["tetra", "clownfish"],
        "fish_count": 5,
        "size_multiplier": 1.0,
        "color_richness": 1.0,
        "caustic_intensity": 0.85,
        "description": "A tranquil school of Neon Tetras & agile Clownfish inaugurating the ecosystem.",
    },
    {
        "tier": 2,
        "name": "Coral Shallows",
        "min_prs": 6,
        "max_prs": 15,
        "species": ["tetra", "clownfish", "bluetang"],
        "fish_count": 6,
        "size_multiplier": 1.15,
        "color_richness": 1.15,
        "caustic_intensity": 1.0,
        "description": "Regal Blue Tang unlocked; existing fish gain noticeable scale and vibrancy.",
    },
    {
        "tier": 3,
        "name": "Azure Haven",
        "min_prs": 16,
        "max_prs": 30,
        "species": ["tetra", "clownfish", "bluetang", "discus"],
        "fish_count": 7,
        "size_multiplier": 1.25,
        "color_richness": 1.25,
        "caustic_intensity": 1.15,
        "description": "Royal Amazonian Discus emerges with turquoise striations and deep lighting.",
    },
    {
        "tier": 4,
        "name": "Abyssal Sanctuary",
        "min_prs": 31,
        "max_prs": 50,
        "species": ["tetra", "clownfish", "bluetang", "discus", "angelfish"],
        "fish_count": 8,
        "size_multiplier": 1.35,
        "color_richness": 1.35,
        "caustic_intensity": 1.25,
        "description": "Altum Angelfish glide through lush scenery with sweeping fins.",
    },
    {
        "tier": 5,
        "name": "Imperial Reef",
        "min_prs": 51,
        "max_prs": 100,
        "species": ["tetra", "clownfish", "bluetang", "discus", "angelfish", "dragonfish"],
        "fish_count": 9,
        "size_multiplier": 1.45,
        "color_richness": 1.45,
        "caustic_intensity": 1.35,
        "description": "The Imperial Golden Arowana graces the tank with luminous golden sparkles.",
    },
    {
        "tier": 6,
        "name": "Legendary Sovereign Realm",
        "min_prs": 101,
        "max_prs": 999999,
        "species": ["tetra", "clownfish", "bluetang", "discus", "angelfish", "dragonfish"],
        "fish_count": 10,
        "size_multiplier": 1.60,
        "color_richness": 1.60,
        "caustic_intensity": 1.50,
        "description": "Mature, breathtaking master aquarium celebrating over 100 merged pull requests.",
    },
]

def load_or_init_state(state_path, username="adityamandre25"):
    """Loads persistent aquarium state or initializes a deterministic starter state."""
    if os.path.exists(state_path):
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
                return state
        except Exception as e:
            print(f"[State] Warning reading existing state ({e}), reinitializing.")
            
    tier1 = EVOLUTION_TIERS[0]
    return {
        "username": username,
        "merged_prs": 0,
        "evolution_tier": tier1["tier"],
        "tier_name": tier1["name"],
        "unlocked_species": tier1["species"],
        "fish_count": tier1["fish_count"],
        "size_multiplier": tier1["size_multiplier"],
        "color_richness": tier1["color_richness"],
        "next_milestone_prs": 6,
        "last_synced": datetime.datetime.utcnow().isoformat() + "Z",
        "version": "2.0-evolve",
    }

def save_state(state_path, state):
    """Persists aquarium state to JSON file."""
    os.makedirs(os.path.dirname(os.path.abspath(state_path)), exist_ok=True)
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    print(f"[State] Saved persistent state to {state_path}")

def fetch_merged_pr_count(username, token=None):
    """
    Fetches exact cumulative merged pull requests authored by the user using GitHub Search API.
    Returns (count, success_flag).
    """
    query = f"type:pr+author:{username}+is:merged"
    url = f"https://api.github.com/search/issues?q={query}"
    headers = {"User-Agent": "EvolvingAquarium/2.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["Accept"] = "application/vnd.github+json"
        
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            count = data.get("total_count", 0)
            print(f"[GitHub API] Verified {count} merged PRs for @{username}.")
            return count, True
    except Exception as e:
        print(f"[GitHub API] Network or rate limit warning ({e}). Using persistent historical count.")
        return 0, False

def get_tier_config(merged_prs):
    """Returns the matching evolution tier configuration for a given merged PR count."""
    for tier in reversed(EVOLUTION_TIERS):
        if merged_prs >= tier["min_prs"]:
            return tier
    return EVOLUTION_TIERS[0]

def render_species_vector(species, length_px, swim_cycle=0.0, facing_left=False, color_richness=1.0):
    """
    Renders high-resolution, anti-aliased vector fish sprites with species-accurate
    anatomy, hydrodynamic silhouettes, and smooth swimming undulation.
    """
    scale = 2
    L = int(length_px * scale)
    H = int(L * 0.70)
    if species == "angelfish":
        H = int(L * 1.10)
    elif species == "discus":
        H = int(L * 0.95)
        
    img = Image.new("RGBA", (L + 40 * scale, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx = 20 * scale
    cy = H // 2
    
    n_pts = 42
    xs = np.linspace(0, L, n_pts)
    wave_phase = swim_cycle * 2 * math.pi
    
    # Lighthill slender-body locomotion wave
    dys = [2.0 * scale * ((x / L) ** 1.8) * math.sin(wave_phase - (x / L) * 4.2) for x in xs]
    
    top_pts = []
    bot_pts = []
    
    for i, (x, dy) in enumerate(zip(xs, dys)):
        p = x / L
        if species == "clownfish":
            if p < 0.22:
                ht = math.sin((p / 0.22) * math.pi / 2) * (L * 0.18)
            elif p < 0.72:
                ht = (L * 0.18) * math.cos(((p - 0.22) / 0.50) * math.pi * 0.44)
            elif p < 0.86:
                ht = (L * 0.065) * (1.0 - (p - 0.72) / 0.35)
            else:
                ht = (L * 0.045) + (p - 0.86) / 0.14 * (L * 0.11)
        elif species == "bluetang":
            if p < 0.25:
                ht = math.sin((p / 0.25) * math.pi / 2) * (L * 0.22)
            elif p < 0.75:
                ht = (L * 0.22) * math.cos(((p - 0.25) / 0.50) * math.pi * 0.45)
            elif p < 0.88:
                ht = (L * 0.06)
            else:
                ht = (L * 0.04) + (p - 0.88) / 0.12 * (L * 0.12)
        elif species == "discus":
            if p < 0.88:
                ht = math.sin((p / 0.88) * math.pi) * (L * 0.32)
            else:
                ht = (L * 0.05) + (p - 0.88) / 0.12 * (L * 0.13)
        elif species == "angelfish":
            if p < 0.35:
                ht = math.sin((p / 0.35) * math.pi / 2) * (L * 0.28)
            elif p < 0.75:
                ht = (L * 0.28) * (1.0 - ((p - 0.35) / 0.40) ** 1.3)
            elif p < 0.88:
                ht = (L * 0.05)
            else:
                ht = (L * 0.04) + (p - 0.88) / 0.12 * (L * 0.14)
        elif species == "dragonfish":
            if p < 0.18:
                ht = math.sin((p / 0.18) * math.pi / 2) * (L * 0.12)
            elif p < 0.82:
                ht = (L * 0.12) * math.cos(((p - 0.18) / 0.64) * math.pi * 0.28)
            elif p < 0.90:
                ht = (L * 0.06)
            else:
                ht = (L * 0.04) + (p - 0.90) / 0.10 * (L * 0.09)
        else: # tetra
            if p < 0.20:
                ht = math.sin((p / 0.20) * math.pi / 2) * (L * 0.11)
            elif p < 0.70:
                ht = (L * 0.11) * math.cos(((p - 0.20) / 0.50) * math.pi * 0.40)
            elif p < 0.85:
                ht = (L * 0.04)
            else:
                ht = (L * 0.03) + (p - 0.85) / 0.15 * (L * 0.08)
                
        top_pts.append((cx + x, cy + dy - ht))
        bot_pts.append((cx + x, cy + dy + ht))
        
    polygon = top_pts + bot_pts[::-1]
    
    # Species Pattern & Pigment Rendering
    if species == "clownfish":
        draw.polygon(polygon, fill=(249, 115, 22, 255))
        for bp in [0.22, 0.52, 0.80]:
            bx = cx + int(L * bp)
            bw = int(L * 0.07)
            idx = int(bp * (n_pts - 1))
            yt = top_pts[idx][1] - 2
            yb = bot_pts[idx][1] + 2
            draw.rectangle([bx - bw//2, yt, bx + bw//2, yb], fill=(255, 255, 255, 245))
            draw.line([(bx - bw//2, yt), (bx - bw//2, yb)], fill=(15, 23, 42, 255), width=int(1.5*scale))
            draw.line([(bx + bw//2, yt), (bx + bw//2, yb)], fill=(15, 23, 42, 255), width=int(1.5*scale))
            
    elif species == "bluetang":
        draw.polygon(polygon, fill=(29, 78, 216, 255))
        pal_pts = []
        for i in range(int(n_pts * 0.2), int(n_pts * 0.75)):
            pal_pts.append(top_pts[i])
        for i in range(int(n_pts * 0.75), int(n_pts * 0.2), -1):
            px = xs[i]
            py = cy + dys[i] + (L * 0.03)
            pal_pts.append((cx + px, py))
        if len(pal_pts) > 2:
            draw.polygon(pal_pts, fill=(15, 23, 42, 255))
        tail_pts = []
        for i in range(int(n_pts * 0.86), n_pts):
            tail_pts.append(top_pts[i])
        for i in range(n_pts - 1, int(n_pts * 0.86) - 1, -1):
            tail_pts.append(bot_pts[i])
        draw.polygon(tail_pts, fill=(250, 204, 21, 255))
        
    elif species == "discus":
        draw.polygon(polygon, fill=(14, 165, 233, 255))
        for line_y in range(-int(L*0.25), int(L*0.25), int(4*scale)):
            pts = []
            for i in range(int(n_pts * 0.15), int(n_pts * 0.85)):
                px = xs[i]
                py = cy + dys[i] + line_y
                pts.append((cx + px, py))
            if len(pts) > 1:
                col = (245, 158, 11, 160) if (line_y // int(4*scale)) % 2 == 0 else (56, 189, 248, 200)
                draw.line(pts, fill=col, width=int(1.5*scale))
        draw.line(top_pts[int(n_pts*0.1):], fill=(239, 68, 68, 220), width=int(2*scale))
        draw.line(bot_pts[int(n_pts*0.1):], fill=(239, 68, 68, 220), width=int(2*scale))
        
    elif species == "angelfish":
        draw.polygon(polygon, fill=(226, 232, 240, 255))
        for bp in [0.26, 0.46, 0.66]:
            bx = cx + int(L * bp)
            idx = int(bp * (n_pts - 1))
            draw.line([(bx, top_pts[idx][1]), (bx, bot_pts[idx][1])], fill=(30, 41, 59, 220), width=int(2.5*scale))
        d_idx = int(n_pts * 0.35)
        d_base = top_pts[d_idx]
        d_tip = (d_base[0] - int(L * 0.08), d_base[1] - int(L * 0.45))
        draw.polygon([d_base, d_tip, top_pts[int(n_pts * 0.6)]], fill=(203, 213, 225, 200))
        v_idx = int(n_pts * 0.28)
        v_base = bot_pts[v_idx]
        v_tip = (v_base[0] + int(L * 0.05), v_base[1] + int(L * 0.48))
        draw.line([v_base, v_tip], fill=(255, 255, 255, 220), width=int(1.5*scale))
        
    elif species == "dragonfish":
        draw.polygon(polygon, fill=(245, 158, 11, 255))
        for i in range(int(n_pts * 0.15), int(n_pts * 0.85), 2):
            px = cx + xs[i]
            py = cy + dys[i]
            draw.arc([px - int(L*0.04), py - int(L*0.06), px + int(L*0.04), py + int(L*0.06)], 0, 180, fill=(254, 240, 138, 220), width=int(1.5*scale))
        chin_pt = bot_pts[1]
        draw.line([chin_pt, (chin_pt[0] - int(L * 0.06), chin_pt[1] + int(L * 0.03))], fill=(250, 204, 21, 240), width=int(1.5*scale))
        
    else: # tetra
        draw.polygon(polygon, fill=(15, 23, 42, 255))
        stripe_pts = []
        for i in range(int(n_pts * 0.08), int(n_pts * 0.82)):
            stripe_pts.append((cx + xs[i], cy + dys[i] - int(L * 0.02)))
        draw.line(stripe_pts, fill=(56, 189, 248, 255), width=int(3*scale))
        scarlet_pts = []
        for i in range(int(n_pts * 0.40), int(n_pts * 0.84)):
            scarlet_pts.append(bot_pts[i])
        for i in range(int(n_pts * 0.84), int(n_pts * 0.40) - 1, -1):
            scarlet_pts.append((cx + xs[i], cy + dys[i] + int(L * 0.01)))
        if len(scarlet_pts) > 2:
            draw.polygon(scarlet_pts, fill=(239, 68, 68, 240))

    # Eye
    eye_x = cx + int(L * 0.13)
    eye_y = cy + dys[int(n_pts * 0.13)] - int(L * 0.03)
    eye_r = max(int(L * 0.032), 2 * scale)
    draw.ellipse([eye_x - eye_r, eye_y - eye_r, eye_x + eye_r, eye_y + eye_r], fill=(251, 191, 36, 255) if species=="dragonfish" else (226, 232, 240, 255))
    draw.ellipse([eye_x - eye_r//2, eye_y - eye_r//2, eye_x + eye_r//2, eye_y + eye_r//2], fill=(15, 23, 42, 255))
    draw.ellipse([eye_x + eye_r//4, eye_y - eye_r//2, eye_x + eye_r//2, eye_y - eye_r//4], fill=(255, 255, 255, 240))
    
    res = img.resize((img.width // scale, img.height // scale), Image.Resampling.LANCZOS)
    if facing_left:
        res = res.transpose(Image.FLIP_LEFT_RIGHT)
        
    return res

def build_aquarium_animation(bg_path, output_path, tier_config):
    """
    Composites the active tier roster, light rays, rising bubbles, and marine motes
    onto the cinematic underwater scenery.
    """
    print(f"[Aquarium] Building animation for Tier {tier_config['tier']} ({tier_config['name']})...")
    bg_orig = Image.open(bg_path).convert("RGBA")
    
    w, h = bg_orig.size
    target_ratio = CANVAS_WIDTH / float(CANVAS_HEIGHT)
    if (w / float(h)) > target_ratio:
        crop_w = int(h * target_ratio)
        left = (w - crop_w) // 2
        bg_crop = bg_orig.crop((left, 0, left + crop_w, h))
    else:
        crop_h = int(w / target_ratio)
        top = (h - crop_h) // 2
        bg_crop = bg_orig.crop((0, top, w, top + crop_h))
        
    bg_base = bg_crop.resize((CANVAS_WIDTH, CANVAS_HEIGHT), Image.Resampling.LANCZOS)
    
    size_mult = tier_config["size_multiplier"]
    all_fish = [
        {"species": "tetra", "x0": 210, "y0": 95, "ax": 80, "ay": 14, "kx": 2, "ky": 1, "phi": 0.4, "wag": 8, "base_len": 38, "fg": True},
        {"species": "tetra", "x0": 260, "y0": 120, "ax": 75, "ay": 12, "kx": 2, "ky": 1, "phi": 0.9, "wag": 8, "base_len": 36, "fg": False},
        {"species": "clownfish", "x0": 160, "y0": 195, "ax": 95, "ay": 22, "kx": 1, "ky": 2, "phi": 1.6, "wag": 6, "base_len": 54, "fg": True},
        {"species": "tetra", "x0": 580, "y0": 85, "ax": 85, "ay": 15, "kx": 2, "ky": 1, "phi": 2.2, "wag": 8, "base_len": 40, "fg": True},
        {"species": "clownfish", "x0": 420, "y0": 210, "ax": 85, "ay": 18, "kx": 1, "ky": 2, "phi": 3.8, "wag": 6, "base_len": 48, "fg": False},
        {"species": "bluetang", "x0": 340, "y0": 175, "ax": 130, "ay": 16, "kx": 1, "ky": 2, "phi": 4.1, "wag": 6, "base_len": 58, "fg": False},
        {"species": "discus", "x0": 270, "y0": 150, "ax": 115, "ay": 18, "kx": 1, "ky": 1, "phi": 1.2, "wag": 4, "base_len": 72, "fg": False},
        {"species": "angelfish", "x0": 530, "y0": 145, "ax": 105, "ay": 20, "kx": 1, "ky": 1, "phi": 3.4, "wag": 4, "base_len": 68, "fg": True},
        {"species": "dragonfish", "x0": 390, "y0": 105, "ax": 155, "ay": 24, "kx": 1, "ky": 2, "phi": 0.0, "wag": 4, "base_len": 110, "fg": True},
        {"species": "dragonfish", "x0": 370, "y0": 120, "ax": 140, "ay": 20, "kx": 1, "ky": 2, "phi": 3.14, "wag": 4, "base_len": 100, "fg": False},
    ]
    
    roster = []
    unlocked_set = set(tier_config["species"])
    for f in all_fish:
        if f["species"] in unlocked_set:
            f_copy = dict(f)
            f_copy["len"] = int(f["base_len"] * size_mult)
            roster.append(f_copy)
            if len(roster) >= tier_config["fish_count"]:
                break
                
    rng = np.random.RandomState(42)
    n_motes = 28
    mote_x0 = rng.uniform(20, CANVAS_WIDTH - 20, n_motes)
    mote_y0 = rng.uniform(20, CANVAS_HEIGHT - 30, n_motes)
    mote_r = rng.uniform(1.0, 2.2, n_motes)
    mote_speed = rng.uniform(0.7, 1.5, n_motes)
    bubble_xs = [120, 290, 480, 650]
    
    rgb_frames = []
    print(f"[Aquarium] Rendering {TOTAL_FRAMES} frames...")
    
    for f in range(TOTAL_FRAMES):
        t = f / float(TOTAL_FRAMES)
        frame = bg_base.copy()
        
        # 1. Caustics
        caustic_layer = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), (0, 0, 0, 0))
        c_draw = ImageDraw.Draw(caustic_layer)
        for i, bx in enumerate([160, 380, 590]):
            alpha = int((12 + 6 * math.sin(2 * math.pi * t + i * 2.1)) * tier_config["caustic_intensity"])
            poly = [(bx - 25, 0), (bx + 35, 0), (bx + 75, CANVAS_HEIGHT), (bx + 5, CANVAS_HEIGHT)]
            c_draw.polygon(poly, fill=(186, 230, 253, min(alpha, 45)))
        frame.alpha_composite(caustic_layer)
        
        # 2. Fish
        for pass_fg in [False, True]:
            for fish in roster:
                if fish["fg"] != pass_fg:
                    continue
                ax_t = 2 * math.pi * fish["kx"] * t + fish["phi"]
                ay_t = 2 * math.pi * fish["ky"] * t + fish["phi"]
                x = fish["x0"] + fish["ax"] * math.cos(ax_t)
                y = fish["y0"] + fish["ay"] * math.sin(ay_t)
                
                vx = -2 * math.pi * fish["kx"] * fish["ax"] * math.sin(ax_t)
                facing_left = (vx < 0)
                
                swim_cycle = (t * fish["wag"]) % 1.0
                sprite = render_species_vector(
                    fish["species"],
                    fish["len"],
                    swim_cycle,
                    facing_left,
                    tier_config["color_richness"]
                )
                
                if not pass_fg:
                    alpha_channel = sprite.split()[3]
                    sprite.putalpha(alpha_channel.point(lambda p: int(p * 0.82)))
                    
                if fish["species"] == "dragonfish":
                    sp_draw = ImageDraw.Draw(frame)
                    for sp_i in range(3):
                        sp_phase = (t * 3.0 + sp_i * 0.33) % 1.0
                        sp_x = x + (fish["len"] * 0.5 if facing_left else -fish["len"] * 0.5) - sp_phase * 22
                        sp_y = y + math.sin(sp_phase * 6.28) * 6
                        sp_draw.ellipse([sp_x - 2, sp_y - 2, sp_x + 2, sp_y + 2], fill=(254, 240, 138, int(220 * (1 - sp_phase))))
                        
                paste_x = int(round(x - sprite.width // 2))
                paste_y = int(round(y - sprite.height // 2))
                frame.alpha_composite(sprite, (paste_x, paste_y))
                
        # 3. Bubbles
        b_draw = ImageDraw.Draw(frame)
        for st_x in bubble_xs:
            for b_i in range(4):
                b_phase = (t + b_i / 4.0) % 1.0
                by = int(CANVAS_HEIGHT - 18 - b_phase * (CANVAS_HEIGHT - 36))
                bx = int(st_x + 5 * math.sin(b_phase * 12.0 + b_i))
                b_rad = 2 if b_i % 2 == 0 else 3
                b_alpha = int(170 * (1.0 - b_phase * 0.35))
                b_draw.ellipse([bx - b_rad, by - b_rad, bx + b_rad, by + b_rad], outline=(224, 242, 254, b_alpha), width=1)
                b_draw.point((bx - 1, by - 1), fill=(255, 255, 255, b_alpha))
                
        # 4. Marine Motes
        for m_i in range(n_motes):
            mx = int(mote_x0[m_i] + 7 * math.sin(2 * math.pi * t + m_i))
            my = int((mote_y0[m_i] - t * 24 * mote_speed[m_i]) % (CANVAS_HEIGHT - 35) + 15)
            mr = mote_r[m_i]
            b_draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(186, 230, 253, int(85 + 35 * math.sin(t * 6 + m_i))))
            
        rgb_frames.append(frame.convert("RGB"))
        
    print("[Aquarium] Quantizing palette with global master color table...")
    palette_sample = rgb_frames[len(rgb_frames) // 2].convert("P", palette=Image.Palette.ADAPTIVE, colors=160)
    quantized_frames = [f.quantize(palette=palette_sample, dither=Image.Dither.NONE) for f in rgb_frames]
    
    print(f"[Aquarium] Compiling optimized animated GIF to {output_path}...")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    quantized_frames[0].save(
        output_path,
        save_all=True,
        append_images=quantized_frames[1:],
        duration=FRAME_DURATION,
        loop=0,
        optimize=True
    )
    sz_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"[Aquarium] Done! Output: {output_path} ({sz_mb:.2f} MB)")

def main():
    parser = argparse.ArgumentParser(description="Living Evolving Aquarium Generator")
    parser.add_argument("--username", default="adityamandre25", help="GitHub username")
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN"), help="GitHub token")
    parser.add_argument("--output", default="assets/aquarium.gif", help="Output GIF path")
    parser.add_argument("--state", default="assets/aquarium_state.json", help="Persistent state path")
    parser.add_argument("--bg", default="assets/aquarium_background.jpg", help="Background scene image path")
    parser.add_argument("--force", action="store_true", help="Force visual regeneration even if PR count didn't change")
    parser.add_argument("--preview-tier", type=int, default=None, help="Preview a specific evolution tier (1-6)")
    args = parser.parse_args()
    
    state = load_or_init_state(args.state, args.username)
    prev_prs = state.get("merged_prs", 0)
    
    if args.preview_tier is not None:
        tier_idx = max(1, min(6, args.preview_tier)) - 1
        tier_config = EVOLUTION_TIERS[tier_idx]
        current_prs = tier_config["min_prs"]
        print(f"[Aquarium] Running in PREVIEW mode for Tier {tier_config['tier']}: {tier_config['name']}")
    else:
        live_prs, success = fetch_merged_pr_count(args.username, args.token)
        if success:
            current_prs = max(live_prs, prev_prs)
        else:
            current_prs = prev_prs
        tier_config = get_tier_config(current_prs)
        
    next_milestone = 6
    for t in EVOLUTION_TIERS:
        if t["min_prs"] > current_prs:
            next_milestone = t["min_prs"]
            break
            
    state["merged_prs"] = current_prs
    state["evolution_tier"] = tier_config["tier"]
    state["tier_name"] = tier_config["name"]
    state["unlocked_species"] = tier_config["species"]
    state["fish_count"] = tier_config["fish_count"]
    state["size_multiplier"] = tier_config["size_multiplier"]
    state["color_richness"] = tier_config["color_richness"]
    state["next_milestone_prs"] = next_milestone
    state["last_synced"] = datetime.datetime.utcnow().isoformat() + "Z"
    
    save_state(args.state, state)
    
    needs_build = args.force or (not os.path.exists(args.output)) or (current_prs != prev_prs) or (args.preview_tier is not None)
    if needs_build:
        build_aquarium_animation(args.bg, args.output, tier_config)
    else:
        print(f"[Aquarium] State up-to-date ({current_prs} PRs). Skipping visual rebuild.")

if __name__ == "__main__":
    main()
