# Demo GIF Creator — GSI Dashboard

Create animated GIFs and short screen recordings for Product Hunt, Reddit, and landing page.

## GSI demo GIF types

### Product Hunt hero GIF (800×500, <3MB)
Sequence: App loads → sidebar: select India → search "Reliance" → Dashboard tab →
signal badge animates in → Insights tab → SEBI disclaimer visible → back to Home
Duration: 15–20 seconds, looping

### Reddit post GIF (480×300, <2MB)
Sequence: One clear feature demo — e.g., Weinstein Stage panel with stage label,
or Portfolio Allocator weights chart, or Global Intelligence map
Duration: 5–8 seconds

### Slack/Social emoji GIF (128×128, <200KB)
Purpose: "GSI is live" announcement, market open/close status indicator
Duration: <3 seconds

## Tools
```bash
pip install Pillow imageio numpy
# For screen recording → GIF conversion:
# Use QuickTime (Mac) → record → convert with ffmpeg
ffmpeg -i recording.mov -vf "fps=15,scale=800:-1" -loop 0 output.gif
# Optimise:
gifsicle --optimize=3 output.gif -o output_opt.gif
```

## Programmatic GIF for signal animation (Pillow approach)
```python
import imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

frames = []
for step in animation_steps:
    img = Image.new('RGB', (800, 500), color='#0d1b2a')
    draw = ImageDraw.Draw(img)
    # Draw frame content
    frames.append(np.array(img))

imageio.mimsave('gsi_demo.gif', frames, fps=12, loop=0)
```

## Easing for smooth signal badge reveal
Use `ease_out` easing for verdict badge appearing:
```python
def ease_out(t): return 1 - (1 - t) ** 3
alpha = int(ease_out(frame / total_frames) * 255)
```

## Content rules for demo GIFs
- Never show specific stock price targets in marketing GIFs
- Include "Educational only — not investment advice" text overlay or caption
- Show verdicts (BUY/WATCH/AVOID) but never imply they are recommendations
- Use demo tickers (RELIANCE.NS, AAPL, NESN.SW) — widely recognised, avoid obscure picks
- Subtitle: "Signal visualisation for self-directed research"
