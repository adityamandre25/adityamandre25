"""
Script to generate both animated SVG and high-fidelity transparent GIF
for ADITYA MANDRE header with exact textLength calibration
"""

import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def generate_header_svg():
    total_chars = 13
    text = "ADITYA MANDRE"
    text_len = 430
    
    # 13 discrete steps
    key_times = [0.0]
    widths = [0]
    
    type_end = 0.32  # 32% of 6.0s = ~1.9s typing
    for i in range(1, total_chars + 1):
        kt = round((i / total_chars) * type_end, 3)
        w = round((i / total_chars) * text_len + 15, 1)
        key_times.append(kt)
        widths.append(w)
        
    # Hold full name visible until 88% (until 5.28s)
    key_times.append(0.88)
    widths.append(widths[-1])
    
    # Graceful reset
    key_times.append(0.96)
    widths.append(0)
    
    key_times.append(1.0)
    widths.append(0)
    
    kt_str = ";".join(str(k) for k in key_times)
    w_str = ";".join(str(w) for w in widths)
    
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 58" width="460" height="58" fill="none">
  <defs>
    <!-- Vibrant Royal / Electric Blue Glow Filter -->
    <filter id="electric-glow" x="-20%" y="-30%" width="150%" height="160%">
      <feGaussianBlur stdDeviation="3" result="blur1" />
      <feGaussianBlur stdDeviation="6" result="blur2" />
      <feMerge>
        <feMergeNode in="blur2" />
        <feMergeNode in="blur1" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <!-- Clip Path revealing characters letter-by-letter -->
    <clipPath id="type-clip">
      <rect x="0" y="0" height="58" width="0">
        <animate attributeName="width"
                 calcMode="discrete"
                 keyTimes="{kt_str}"
                 values="{w_str}"
                 dur="6s"
                 repeatCount="indefinite" />
      </rect>
    </clipPath>

    <!-- Electric Cyan to Royal Blue Gradient -->
    <linearGradient id="header-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="55%" stop-color="#60A5FA" />
      <stop offset="100%" stop-color="#3B82F6" />
    </linearGradient>
  </defs>

  <style>
    .header-text {{
      font-family: 'JetBrains Mono', 'Fira Code', 'Segoe UI', 'Consolas', monospace;
      font-size: 32px;
      font-weight: 800;
      letter-spacing: 4px;
      fill: url(#header-grad);
    }}
    .glow-layer {{
      font-family: 'JetBrains Mono', 'Fira Code', 'Segoe UI', 'Consolas', monospace;
      font-size: 32px;
      font-weight: 800;
      letter-spacing: 4px;
      fill: #1D4ED8;
      filter: url(#electric-glow);
      opacity: 0.9;
    }}
  </style>

  <!-- Animated Heading -->
  <g clip-path="url(#type-clip)">
    <text x="2" y="42" class="glow-layer" textLength="{text_len}" lengthAdjust="spacing">{text}</text>
    <text x="2" y="42" class="header-text" textLength="{text_len}" lengthAdjust="spacing">{text}</text>
  </g>
</svg>
'''
    return svg_content

def generate_header_gif():
    scale = 2
    w, h = 460 * scale, 58 * scale
    text = "ADITYA MANDRE"
    
    font_path = r"C:\Windows\Fonts\consolab.ttf"
    try:
        font = ImageFont.truetype(font_path, 30 * scale)
    except:
        font = ImageFont.load_default()
        
    fps = 15
    total_dur_sec = 6.0
    total_frames = int(fps * total_dur_sec)
    chars = list(text)
    frames = []
    
    for f in range(total_frames):
        sec = f / float(fps)
        if sec < 1.8:
            char_count = int((sec / 1.8) * len(chars)) + 1
            char_count = min(char_count, len(chars))
        elif sec < 5.2:
            char_count = len(chars)
        else:
            char_count = 0
            
        current_text = "".join(chars[:char_count])
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        
        if current_text:
            glow_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            g_draw = ImageDraw.Draw(glow_img)
            g_draw.text((6 * scale, 10 * scale), current_text, font=font, fill=(37, 99, 235, 180), spacing=4)
            glow_blurred = glow_img.filter(ImageFilter.GaussianBlur(radius=4 * scale))
            img.alpha_composite(glow_blurred)
            
            draw = ImageDraw.Draw(img)
            draw.text((6 * scale, 10 * scale), current_text, font=font, fill=(56, 189, 248, 255), spacing=4)
            
        res = img.resize((460, 58), Image.Resampling.LANCZOS)
        p_img = res.convert("RGBA")
        alpha = p_img.getchannel("A")
        p_res = p_img.convert("RGB").convert("P", palette=Image.Palette.ADAPTIVE, colors=64)
        p_res.paste(0, mask=Image.eval(alpha, lambda a: 255 if a == 0 else 0))
        p_res.info["transparency"] = 0
        frames.append(p_res)
        
    frames[0].save(
        "assets/header.gif",
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / fps),
        loop=0,
        transparency=0,
        disposal=2,
        optimize=True
    )

if __name__ == "__main__":
    with open("assets/header.svg", "w", encoding="utf-8") as f:
        f.write(generate_header_svg())
    print("Generated assets/header.svg")
    generate_header_gif()
    print("Generated assets/header.gif")
