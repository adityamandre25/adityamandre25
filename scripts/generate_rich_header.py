"""
Premium Rich Header Generator for ADITYA MANDRE
Features:
- Luxury Electric Sapphire & Cyan Multi-Stop Radiant Gradient
- Layered Atmospheric Bloom & Specular Highlights
- Sleek Terminal/Executive Cursor Animation
- Discrete Letter-by-Letter Typing Reveal
- Long 5.5s Steady Display Hold (No rapid distracting loops)
- Modern Geometric Sans Typography with Wide Letter Tracking
"""

def build_rich_header_svg():
    text = "ADITYA MANDRE"
    total_chars = len(text) # 13
    
    # Timing configuration
    total_dur = 7.5  # seconds for a complete luxurious cycle
    type_dur = 1.8   # seconds to type out (138ms per char)
    hold_dur = 5.0   # seconds to stay fully visible
    fade_dur = 0.7   # seconds to gracefully fade and reset
    
    # Calculate keyTimes and widths
    # Canvas dimensions
    view_w = 540
    view_h = 64
    text_len = 460
    
    key_times = [0.0]
    widths = [0]
    
    type_fraction = type_dur / total_dur # 0.24
    for i in range(1, total_chars + 1):
        kt = round((i / total_chars) * type_fraction, 4)
        # width reveals up to that character
        w = round((i / total_chars) * text_len + 16, 1)
        key_times.append(kt)
        widths.append(w)
        
    # Hold fully typed until hold end
    hold_end = round((type_dur + hold_dur) / total_dur, 4) # ~0.9067
    key_times.append(hold_end)
    widths.append(widths[-1])
    
    # Fade / reset
    reset_start = round(hold_end + 0.05, 4)
    key_times.append(reset_start)
    widths.append(0)
    
    key_times.append(1.0)
    widths.append(0)
    
    kt_str = ";".join(str(k) for k in key_times)
    w_str = ";".join(str(w) for w in widths)
    
    # Cursor keyTimes
    # Cursor moves along with the typing width, then blinks during the hold, then disappears
    cursor_widths = [0] + [w for w in widths[1:-2]] + [0, 0]
    c_w_str = ";".join(str(w) for w in cursor_widths)
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" width="{view_w}" height="{view_h}" fill="none">
  <defs>
    <!-- Multi-Stage Deep Electric Bloom -->
    <filter id="rich-bloom" x="-20%" y="-30%" width="150%" height="170%">
      <feGaussianBlur stdDeviation="2.5" result="glow1" />
      <feGaussianBlur stdDeviation="5.5" result="glow2" />
      <feGaussianBlur stdDeviation="11.0" result="glow3" />
      <feMerge>
        <feMergeNode in="glow3" />
        <feMergeNode in="glow2" />
        <feMergeNode in="glow1" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <!-- Luxury Multi-Stop Sapphire, Electric Cyan & Specular Gradient -->
    <linearGradient id="rich-sapphire-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="25%" stop-color="#60A5FA" />
      <stop offset="50%" stop-color="#93C5FD" />
      <stop offset="75%" stop-color="#3B82F6" />
      <stop offset="100%" stop-color="#2563EB" />
    </linearGradient>

    <!-- Deep Ambient Underglow Gradient -->
    <linearGradient id="ambient-glow-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0284C7" />
      <stop offset="50%" stop-color="#2563EB" />
      <stop offset="100%" stop-color="#1D4ED8" />
    </linearGradient>

    <!-- Reveal Clip Path -->
    <clipPath id="reveal-clip">
      <rect x="0" y="0" height="{view_h}" width="0">
        <animate attributeName="width"
                 calcMode="discrete"
                 keyTimes="{kt_str}"
                 values="{w_str}"
                 dur="{total_dur}s"
                 repeatCount="indefinite" />
      </rect>
    </clipPath>

    <!-- Cursor Clip Path -->
    <clipPath id="cursor-clip">
      <rect x="0" y="8" height="42" width="4">
        <animate attributeName="x"
                 calcMode="discrete"
                 keyTimes="{kt_str}"
                 values="{c_w_str}"
                 dur="{total_dur}s"
                 repeatCount="indefinite" />
      </rect>
    </clipPath>
  </defs>

  <style>
    .rich-text {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', 'SF Pro Display', Roboto, 'Montserrat', sans-serif;
      font-size: 34px;
      font-weight: 850;
      letter-spacing: 5.5px;
      fill: url(#rich-sapphire-grad);
    }}
    .glow-backdrop {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', 'SF Pro Display', Roboto, 'Montserrat', sans-serif;
      font-size: 34px;
      font-weight: 850;
      letter-spacing: 5.5px;
      fill: url(#ambient-glow-grad);
      filter: url(#rich-bloom);
      opacity: 0.85;
    }}
    .cursor-bar {{
      fill: #38BDF8;
      filter: drop-shadow(0 0 6px #38BDF8);
    }}
  </style>

  <!-- Group with letter-by-letter reveal -->
  <g clip-path="url(#reveal-clip)">
    <!-- Ambient Luminous Glow Layer -->
    <text x="4" y="44" class="glow-backdrop" textLength="{text_len}" lengthAdjust="spacing">{text}</text>
    <!-- Crisp Foreground Vector Layer -->
    <text x="4" y="44" class="rich-text" textLength="{text_len}" lengthAdjust="spacing">{text}</text>
  </g>

  <!-- Sleek Typing Cursor -->
  <g clip-path="url(#cursor-clip)">
    <rect x="0" y="10" width="3.5" height="38" rx="1.5" class="cursor-bar">
      <!-- Cursor blink animation -->
      <animate attributeName="opacity"
               values="1; 1; 0; 0; 1"
               keyTimes="0; 0.45; 0.50; 0.95; 1"
               dur="0.85s"
               repeatCount="indefinite" />
    </rect>
  </g>
</svg>
'''
    return svg

if __name__ == "__main__":
    content = build_rich_header_svg()
    with open("assets/header.svg", "w", encoding="utf-8") as f:
        f.write(content)
    print("Generated rich assets/header.svg successfully!")
