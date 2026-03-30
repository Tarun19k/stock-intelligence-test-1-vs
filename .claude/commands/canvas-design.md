# Canvas Design — GSI Dashboard

Generate museum-quality visual assets: Open Graph images, marketing hero art, social visuals.

## GSI asset targets

### Open Graph / Social share image (1200×630px PNG)
Every page share needs this. Background: `#0d1b2a`. Show dashboard screenshot + title overlay.

### Product Hunt thumbnail (240×240px)
Clean mark: upward signal path through globe wireframe. Electric blue on navy.

### Landing page hero art (1440×800px)
Abstract: global market signal lines converging — particle flow from 9 market nodes.
Communicates: "global", "signal", "data in motion". No stock photos.

### Twitter/X card (1200×628px)
Weekly signal snapshot: "Nifty 50: 31 BUY / 12 WATCH / 7 AVOID" with heatmap snippet.

## Design philosophy for GSI visuals
Movement name: **Precision Flow**
- Data moves with purpose — every line has direction and destination
- The globe is a signal grid, not a map
- Colour carries meaning: electric blue = active signal, navy = space/depth, white = clarity
- Typography as data: monospace numbers feel like terminal output — honest, not marketed
- Empty space is intentional — density where it matters, silence where it doesn't

## Technical output
```python
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Canvas size for OG image
img = Image.new('RGB', (1200, 630), color='#0d1b2a')
draw = ImageDraw.Draw(img)
# Add signal lines, text overlays, market node dots
img.save('og-image.png', 'PNG', optimize=True)
```

## Quality standard
Output must look meticulously crafted — not AI-generated clip art.
Perfect alignment, adequate margins, zero overlapping elements.
If it looks like a template, redo it.

## File output targets
```
assets/og-image.png          # 1200×630 — social sharing
assets/ph-thumbnail.png      # 240×240 — Product Hunt
assets/hero.png              # 1440×800 — landing page
assets/twitter-card.png      # 1200×628 — Twitter/X
assets/favicon-32.png        # 32×32 — browser favicon
```
