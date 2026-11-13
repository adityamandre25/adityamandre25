"""
Silky-Smooth Header Generator for ADITYA MANDRE
Features:
- Continuous liquid-smooth width reveal (zero jitter / zero stutter)
- Multi-stop luxury sapphire, electric cyan & specular highlight gradient
- Multi-layer atmospheric ambient bloom (glow1, glow2, glow3)
- Smoothly gliding neon cursor that blinks during hold
- 5.0 second steady hold of the full name
- Graceful opacity fade-out before replay (no sudden snapping)
"""

def build_silky_smooth_header_svg():
    view_w = 540
    view_h = 64
    text_len = 460
    text = "ADITYA MANDRE"
    
    # Cycle timing (in seconds):
    # 0.0s - 2.0s : Liquid smooth reveal (cursor glides, letters unveil)
    # 2.0s - 6.5s : Full name displayed steady & glowing (4.5s hold, cursor blinks)
    # 6.5s - 7.2s : Graceful fade out
    # 7.2s - 7.5s : Reset
    total_dur = 7.5
    
    # Reveal width keytimes:
    # 0 -> 2.0s : 0 -> text_len + 12
    # 2.0s -> 6.5s : text_len + 12 (hold)
    # 6.5s -> 7.2s : fade out (handled by opacity)
    # 7.2s -> 7.5s : 0
    t_type_end = round(2.0 / total_dur, 4)  # ~0.2667
    t_hold_end = round(6.5 / total_dur, 4)  # ~0.8667
    t_fade_end = round(7.2 / total_dur, 4)  # ~0.9600
    
    # Cursor x position:
    # 0 -> 2.0s : 4 -> text_len + 10
    # 2.0s -> 6.5s : text_len + 10
    # 6.5s -> 7.5s : hidden
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" width="{view_w}" height="{view_h}" fill="none">
  <defs>
    <!-- Deep Electric Sapphire Bloom Filter -->
    <filter id="rich-bloom" x="-20%" y="-30%" width="150%" height="170%">
      <feGaussianBlur stdDeviation="2.5" result="glow1" />
      <feGaussianBlur stdDeviation="5.5" result="glow2" />
      <feGaussianBlur stdDeviation="10.0" result="glow3" />
      <feMerge>
        <feMergeNode in="glow3" />
        <feMergeNode in="glow2" />
        <feMergeNode in="glow1" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <!-- 5-Stop Luxury Sapphire & Specular Gradient -->
    <linearGradient id="sapphire-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="25%" stop-color="#60A5FA" />
      <stop offset="50%" stop-color="#93C5FD" />
      <stop offset="75%" stop-color="#3B82F6" />
      <stop offset="100%" stop-color="#2563EB" />
    </linearGradient>

    <!-- Deep Ambient Blue Underglow -->
    <linearGradient id="bloom-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0284C7" />
      <stop offset="50%" stop-color="#2563EB" />
      <stop offset="100%" stop-color="#1D4ED8" />
    </linearGradient>

    <!-- Continuous Liquid Smooth Reveal Clip -->
    <clipPath id="smooth-reveal">
      <rect x="0" y="0" height="{view_h}" width="0">
        <animate attributeName="width"
                 calcMode="linear"
                 keyTimes="0; {t_type_end}; {t_hold_end}; {t_fade_end}; 1"
                 values="0; {text_len + 15}; {text_len + 15}; 0; 0"
                 dur="{total_dur}s"
                 repeatCount="indefinite" />
      </rect>
    </clipPath>
  </defs>

  <style>
    .rich-heading {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', 'SF Pro Display', Roboto, 'Montserrat', sans-serif;
      font-size: 34px;
      font-weight: 850;
      letter-spacing: 5.5px;
      fill: url(#sapphire-grad);
    }}
    .glow-layer {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', 'SF Pro Display', Roboto, 'Montserrat', sans-serif;
      font-size: 34px;
      font-weight: 850;
      letter-spacing: 5.5px;
      fill: url(#bloom-grad);
      filter: url(#rich-bloom);
      opacity: 0.85;
    }}
    .cursor-neon {{
      fill: #38BDF8;
      filter: drop-shadow(0 0 5px #38BDF8);
    }}
  </style>

  <!-- Animated Container with Smooth Opacity Cycle -->
  <g>
    <animate attributeName="opacity"
             calcMode="linear"
             keyTimes="0; {t_hold_end}; {t_fade_end}; 1"
             values="1; 1; 0; 1"
             dur="{total_dur}s"
             repeatCount="indefinite" />

    <!-- Text Layer with Continuous Width Reveal -->
    <g clip-path="url(#smooth-reveal)">
      <text x="4" y="44" class="glow-layer" textLength="{text_len}" lengthAdjust="spacing">{text}</text>
      <text x="4" y="44" class="rich-heading" textLength="{text_len}" lengthAdjust="spacing">{text}</text>
    </g>

    <!-- Smoothly Gliding & Blinking Cursor -->
    <rect y="10" width="3.5" height="38" rx="1.75" class="cursor-neon">
      <!-- Glides from 4 to text_len + 12 then stays docked -->
      <animate attributeName="x"
               calcMode="linear"
               keyTimes="0; {t_type_end}; {t_hold_end}; 1"
               values="4; {text_len + 12}; {text_len + 12}; {text_len + 12}"
               dur="{total_dur}s"
               repeatCount="indefinite" />
      <!-- Subtle blink -->
      <animate attributeName="opacity"
               values="1; 1; 0.2; 0.2; 1"
               keyTimes="0; 0.45; 0.50; 0.95; 1"
               dur="0.85s"
               repeatCount="indefinite" />
    </rect>
  </g>
</svg>
'''
    return svg

if __name__ == "__main__":
    content = build_silky_smooth_header_svg()
    with open("assets/header.svg", "w", encoding="utf-8") as f:
        f.write(content)
    print("Generated silky-smooth assets/header.svg successfully!")
