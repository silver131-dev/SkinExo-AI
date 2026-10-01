"""Presentation-only design tokens for the SkinExo-AI Explorer.

This module contains no data access, scientific classification, or retrieval logic.
"""

from __future__ import annotations


COLORS = {
    "pearl_white": "#F7F5F1",
    "warm_ivory": "#EFEAE2",
    "soft_blush": "#EEDDD9",
    "mist_mint": "#DDEBE5",
    "powder_aqua": "#DCE9EC",
    "pale_lavender": "#E8E2EE",
    "champagne": "#D9C8AE",
    "deep_ink": "#173033",
}

SPACING = {
    "xs": "0.35rem",
    "sm": "0.65rem",
    "md": "1rem",
    "lg": "1.5rem",
    "xl": "2.25rem",
    "xxl": "3.5rem",
}

RADII = {
    "sm": "10px",
    "md": "16px",
    "lg": "24px",
    "pill": "999px",
}

SHADOWS = {
    "soft": "0 12px 38px rgba(23, 48, 51, 0.07)",
    "lifted": "0 18px 54px rgba(23, 48, 51, 0.11)",
    "focus": "0 0 0 3px rgba(217, 200, 174, 0.30)",
}

TYPOGRAPHY = {
    "sans": '"Inter", "Avenir Next", "Segoe UI", "Noto Sans", sans-serif',
    "display": '"Avenir Next", "Inter", "Segoe UI", "Noto Sans", sans-serif',
    "mono": '"SFMono-Regular", Consolas, "Liberation Mono", monospace',
    "hero_size": "clamp(2.7rem, 6vw, 4.9rem)",
    "section_size": "clamp(1.35rem, 2.4vw, 2rem)",
    "body_size": "1rem",
}

TRANSITIONS = {
    "standard": "720ms cubic-bezier(0.22, 1, 0.36, 1)",
    "slow": "880ms cubic-bezier(0.22, 1, 0.36, 1)",
}


def explorer_css() -> str:
    """Return the offline CSS theme used by the Streamlit presentation layer."""

    c = COLORS
    return f"""
<style>
  :root {{
    --pearl-white: {c['pearl_white']};
    --warm-ivory: {c['warm_ivory']};
    --soft-blush: {c['soft_blush']};
    --mist-mint: {c['mist_mint']};
    --powder-aqua: {c['powder_aqua']};
    --pale-lavender: {c['pale_lavender']};
    --champagne: {c['champagne']};
    --deep-ink: {c['deep_ink']};
    --line: rgba(23, 48, 51, 0.16);
    --line-strong: rgba(23, 48, 51, 0.30);
    --glass: rgba(247, 245, 241, 0.78);
    --transition: {TRANSITIONS['standard']};
  }}

  html, body, [class*="css"], [data-testid="stAppViewContainer"] {{
    font-family: {TYPOGRAPHY['sans']};
    color: var(--deep-ink);
  }}

  [data-testid="stAppViewContainer"] {{
    background:
      radial-gradient(circle at 8% 2%, rgba(238, 221, 217, 0.58), transparent 29rem),
      radial-gradient(circle at 94% 12%, rgba(220, 233, 236, 0.70), transparent 32rem),
      linear-gradient(155deg, var(--pearl-white) 0%, #faf9f6 58%, var(--warm-ivory) 100%);
  }}

  [data-testid="stHeader"] {{
    background: rgba(247, 245, 241, 0.78);
    backdrop-filter: blur(18px);
    border-bottom: 1px solid rgba(23, 48, 51, 0.07);
  }}

  .block-container {{
    max-width: 1240px;
    padding-top: 2.3rem;
    padding-bottom: 4.5rem;
  }}

  h1, h2, h3, h4, [data-testid="stHeadingWithActionElements"] {{
    font-family: {TYPOGRAPHY['display']};
    color: var(--deep-ink);
    letter-spacing: -0.025em;
  }}

  h1 {{
    font-size: {TYPOGRAPHY['hero_size']} !important;
    line-height: 0.98 !important;
    letter-spacing: -0.055em !important;
    margin: 0.15rem 0 0.55rem !important;
  }}

  h2 {{ margin-top: 2.4rem !important; }}
  p, li, label {{ color: var(--deep-ink); }}

  .skinexo-hero {{
    position: relative;
    overflow: hidden;
    padding: 1.35rem 1.55rem 1.45rem;
    margin-bottom: 0.5rem;
    border: 1px solid rgba(23, 48, 51, 0.12);
    border-radius: {RADII['lg']};
    background: linear-gradient(120deg, rgba(247,245,241,0.92), rgba(221,235,229,0.62));
    box-shadow: {SHADOWS['soft']};
    backdrop-filter: blur(20px);
  }}

  .skinexo-hero::after {{
    content: "";
    position: absolute;
    width: 12rem;
    height: 12rem;
    right: -4rem;
    top: -5rem;
    border: 1px solid rgba(217, 200, 174, 0.65);
    border-radius: 50%;
    box-shadow: inset 0 0 0 1.5rem rgba(232, 226, 238, 0.16);
    pointer-events: none;
  }}

  .skinexo-eyebrow, .section-kicker {{
    color: var(--deep-ink);
    font-size: 0.72rem;
    font-weight: 760;
    letter-spacing: 0.16em;
    text-transform: uppercase;
  }}

  .skinexo-subtitle {{
    max-width: 880px;
    margin: 0.1rem 0 0.45rem;
    font-size: clamp(1.25rem, 2.5vw, 2rem);
    font-weight: 590;
    line-height: 1.12;
  }}

  .skinexo-support {{
    max-width: 820px;
    color: rgba(23, 48, 51, 0.78);
    font-size: 1.02rem;
    line-height: 1.65;
  }}

  .skinexo-principle {{
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    margin-top: 0.75rem;
    padding: 0.45rem 0.75rem;
    border-radius: {RADII['pill']};
    background: rgba(232, 226, 238, 0.68);
    border: 1px solid rgba(23, 48, 51, 0.12);
    font-size: 0.82rem;
    font-weight: 650;
  }}

  div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: var(--glass);
    border: 1px solid var(--line) !important;
    border-radius: {RADII['md']} !important;
    box-shadow: {SHADOWS['soft']};
    backdrop-filter: blur(16px);
    transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition);
  }}

  div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    border-color: rgba(217, 200, 174, 0.88) !important;
    box-shadow: {SHADOWS['lifted']};
    transform: translateY(-2px);
  }}

  [data-testid="stMetric"] {{
    min-height: 7.2rem;
    padding: 0.95rem 1rem;
    border: 1px solid var(--line);
    border-radius: {RADII['md']};
    background: rgba(247, 245, 241, 0.76);
  }}

  [data-testid="stMetricLabel"] {{
    font-size: 0.72rem;
    font-weight: 730;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }}

  [data-testid="stMetricValue"] {{
    color: var(--deep-ink);
    font-size: 1.03rem;
    font-weight: 620;
    line-height: 1.32;
    white-space: normal;
  }}

  [data-baseweb="tab-list"] {{
    gap: 0.35rem;
    padding: 0.25rem;
    background: rgba(239, 234, 226, 0.70);
    border: 1px solid var(--line);
    border-radius: {RADII['pill']};
  }}

  [data-baseweb="tab"] {{
    border-radius: {RADII['pill']};
    color: var(--deep-ink);
    font-weight: 650;
    transition: background var(--transition);
  }}

  [aria-selected="true"][data-baseweb="tab"] {{
    background: rgba(247, 245, 241, 0.94);
    box-shadow: 0 3px 14px rgba(23, 48, 51, 0.08);
  }}

  div[data-testid="stExpander"] {{
    border: 1px solid var(--line);
    border-radius: {RADII['md']};
    background: rgba(247, 245, 241, 0.70);
    box-shadow: {SHADOWS['soft']};
  }}

  [data-testid="stDataFrame"] {{
    border: 1px solid var(--line);
    border-radius: {RADII['md']};
    overflow: hidden;
  }}

  .axis-letter {{
    display: inline-grid;
    place-items: center;
    width: 2.15rem;
    height: 2.15rem;
    margin-right: 0.42rem;
    border-radius: 50%;
    background: var(--deep-ink);
    color: var(--pearl-white);
    font-weight: 800;
    letter-spacing: 0;
  }}

  .evidence-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    margin: 0.18rem 0.18rem 0.18rem 0;
    padding: 0.3rem 0.55rem;
    border: 1px solid var(--line-strong);
    border-radius: {RADII['pill']};
    color: var(--deep-ink);
    font-size: 0.74rem;
    font-weight: 720;
  }}

  .state-positive {{ background: var(--mist-mint); border-left: 4px solid var(--deep-ink); }}
  .state-negative {{ background: var(--powder-aqua); border-left: 4px double var(--deep-ink); }}
  .state-null {{ background: var(--warm-ivory); border: 1px dashed var(--deep-ink); }}
  .state-not-tested {{ background: var(--pale-lavender); border: 1px dotted var(--deep-ink); }}
  .state-mixed {{ background: var(--soft-blush); border-left: 4px solid var(--champagne); }}

  .evidence-row {{
    padding: 0.72rem 0.8rem;
    margin: 0.42rem 0;
    border: 1px solid var(--line);
    border-radius: {RADII['sm']};
    background: rgba(247, 245, 241, 0.78);
  }}

  .evidence-row strong {{ color: var(--deep-ink); }}
  .evidence-meta {{ color: rgba(23, 48, 51, 0.72); font-size: 0.79rem; line-height: 1.45; }}

  .rank-kicker {{
    color: rgba(23, 48, 51, 0.72);
    font-size: 0.7rem;
    font-weight: 780;
    letter-spacing: 0.13em;
    text-transform: uppercase;
  }}

  .rank-one {{ border-top: 5px solid var(--champagne) !important; }}
  .rank-two {{ border-top: 5px solid var(--powder-aqua) !important; }}

  [data-testid="stAlert"] {{
    border: 1px solid var(--line);
    border-radius: {RADII['md']};
    color: var(--deep-ink);
  }}

  hr {{ border-color: rgba(23, 48, 51, 0.10) !important; margin: 2.5rem 0 !important; }}

  a {{ color: var(--deep-ink) !important; text-decoration-color: var(--champagne) !important; }}
  code {{ font-family: {TYPOGRAPHY['mono']}; }}

  @media (max-width: 760px) {{
    .block-container {{ padding: 1.2rem 1rem 3rem; }}
    .skinexo-hero {{ padding: 1rem; }}
    h1 {{ font-size: 2.65rem !important; }}
  }}

  @media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }}
  }}
</style>
"""
