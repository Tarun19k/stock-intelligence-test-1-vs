# Algorithmic Art — GSI Dashboard

Generate generative p5.js art for loading screens, marketing animations, and visual identity.

## GSI art concepts

### Loading screen animation (dashboard cold start)
Philosophy: **Market Convergence**
9 market nodes (dots) at globe positions. Particles stream from each node toward centre,
forming a unified signal. Seeded randomness — same seed = same animation per session.
Output: Self-contained HTML, embeds in Streamlit via st.components.v1.html()

### Signal field visualisation (alternative Insights tab view)
Philosophy: **Signal Terrain**
Perlin noise field where elevation = Momentum Score, colour = BUY/WATCH/AVOID verdict.
Each ticker is a particle moving through the signal landscape.
Output: p5.js artifact with seed navigation

### Landing page hero animation
Philosophy: **Precision Flow**
Directed particle streams from 9 market locations (globe coordinates), converging into
a central signal node. Colour-coded by market status (open=blue, closed=dim).
Output: Standalone HTML embed for GitHub Pages landing page

## Technical requirements (from skill spec)
```javascript
// Always seed randomness for reproducibility
randomSeed(seed);
noiseSeed(seed);
```

Self-contained HTML artifact. No external files except p5.js from CDN.
Include: seed navigation (prev/next/random), parameter sliders, PNG download.

## Streamlit embedding
```python
import streamlit.components.v1 as components
with open('loading_animation.html', 'r') as f:
    components.html(f.read(), height=400)
```

## Quality standard
Must feel "meticulously crafted through countless iterations" — not random noise.
Particle systems must have emergent beauty: clear composition, not visual noise.
Test at multiple seeds (at least 10) before shipping.

## Where NOT to use generative art
- Inside the main dashboard data panels — distracts from signal data
- As chart backgrounds — reduces readability
- In printed reports — not appropriate context
