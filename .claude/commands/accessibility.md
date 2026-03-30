# Accessibility Audit — GSI Dashboard

Check colour contrast, screen reader support, and keyboard navigation for the dashboard.

## Why this matters for GSI
Retail investors include users with colour vision deficiency (CVD) — 8% of males.
BUY=green, WATCH=yellow, AVOID=red is a CVD problem if colour is the only differentiator.

## Colour contrast checks (WCAG 2.1 AA minimum: 4.5:1 for text)

| Pair | Hex | Contrast ratio | Pass AA? |
|---|---|---|---|
| Primary text on dark bg | `#e8eaf0` on `#0d1b2a` | ~12:1 | ✅ |
| Secondary text on dark bg | `#7eb3ff` on `#0d1b2a` | ~6:1 | ✅ |
| Accent blue on dark bg | `#4fc3f7` on `#0d1b2a` | ~8:1 | ✅ |
| BUY green on dark bg | `#00c853` on `#0d1b2a` | ~6.5:1 | ✅ |
| WATCH yellow on dark bg | `#ffd600` on `#0d1b2a` | ~9:1 | ✅ |
| AVOID red on dark bg | `#ff1744` on `#0d1b2a` | ~5.5:1 | ✅ |

Check tool: https://webaim.org/resources/contrastchecker/

## Colour-blind safe signal display
BUY / WATCH / AVOID must never rely on colour alone.
Current mitigations:
- Verdict badge shows text label ("BUY" / "WATCH" / "AVOID") ✅
- Icon prefix (🟢 / 🟡 / 🔴) ✅
- Plain-English reason always shown alongside verdict ✅

Additional improvement: add shape differentiation (▲ BUY / ■ WATCH / ▼ AVOID).

## Screen reader checks
Streamlit renders React → most content is accessible if proper text labels are used.
Check:
- `st.metric()` labels are descriptive, not just ticker symbols
- Chart alt-text: `st.plotly_chart(fig, ...)` — add `config={'displayModeBar': False}` + title
- Sidebar navigation items have clear text labels (current: emoji + text ✅)
- Error messages use text, not colour alone

## Keyboard navigation
Streamlit handles tab-order automatically for standard widgets.
Custom HTML blocks (unsafe_allow_html) are NOT keyboard accessible.
→ All critical interactions must have a standard Streamlit widget equivalent.

## Audit checklist
- [ ] Run through BUY/WATCH/AVOID with colour-blind simulation (browser DevTools)
- [ ] Tab through sidebar navigation — logical order?
- [ ] All st.metric() labels are meaningful without context
- [ ] Charts have visible titles (not just tooltips)
- [ ] Disclaimer text meets 4.5:1 contrast ratio
- [ ] No information conveyed by colour alone

## Tools
- Browser: Chrome DevTools → Rendering → Emulate vision deficiencies
- Online: WebAIM Contrast Checker, WAVE accessibility evaluator
- Python: `pip install axe-playwright-python` for automated a11y testing
