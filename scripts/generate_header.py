"""
Generates rich, silky-smooth assets/header.svg and assets/header.gif for ADITYA MANDRE
"""

from generate_rich_header import build_silky_smooth_header_svg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def update_header_gif():
    scale = 2
    w, h = 540 * scale, 64 * scale
    text = "ADITYA MANDRE"
    
    font_path = r"C:\Windows\Fonts\segoeuib.ttf"
    try:
        font = ImageFont.truetype(font_path, 32 * scale)
    except:
        font = ImageFont.load_default()
        
    fps = 16
    total_dur_sec = 7.5
    total_frames = int(fps * total_dur_sec)
    chars = list(text)
    frames = []
    
    for f in range(total_frames):
        sec = f / float(fps)
        if sec < 2.0:
            char_count = int((sec / 2.0) * len(chars)) + 1
            char_count = min(char_count, len(chars))
        elif sec < 6.5:
            char_count = len(chars)
        else:
            char_count = 0
            
        current_text = "".join(chars[:char_count])
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        
        if current_text:
            # Multi-layer rich sapphire glow
            glow_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            g_draw = ImageDraw.Draw(glow_img)
            g_draw.text((12 * scale, 12 * scale), current_text, font=font, fill=(37, 99, 235, 180), spacing=8)
            glow_blurred = glow_img.filter(ImageFilter.GaussianBlur(radius=5 * scale))
            img.alpha_composite(glow_blurred)
            
            # Sharp foreground text with rich electric cyan-blue
            draw = ImageDraw.Draw(img)
            draw.text((12 * scale, 12 * scale), current_text, font=font, fill=(56, 189, 248, 255), spacing=8)
            
            # Blinking cursor during typing and hold
            if (int(sec * 3) % 2 == 0) and sec < 6.5:
                bbox = draw.textbbox((12 * scale, 12 * scale), current_text, font=font, spacing=8)
                cur_x = bbox[2] + 4 * scale
                draw.rectangle([cur_x, 14 * scale, cur_x + 3 * scale, 48 * scale], fill=(96, 165, 250, 240))
                
        res = img.resize((540, 64), Image.Resampling.LANCZOS)
        p_img = res.convert("RGBA")
        alpha = p_img.getchannel("A")
        p_res = p_img.convert("RGB").convert("P", palette=Image.Palette.ADAPTIVE, colors=96)
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
    print("Updated assets/header.gif successfully!")

if __name__ == "__main__":
    with open("assets/header.svg", "w", encoding="utf-8") as f:
        f.write(build_silky_smooth_header_svg())
    print("Updated assets/header.svg successfully!")
    update_header_gif()
