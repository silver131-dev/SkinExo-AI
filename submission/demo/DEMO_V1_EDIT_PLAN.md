# SkinExo-AI DEMO-V1 edit plan

## Master sequence

| Timeline | Picture | Voiceover | Text / captions |
|---|---|---|---|
| 0:00–0:35 | MG01 with GV01/GV02 plates | Scene 1 narration | KF01–KF05 text; burned-in title-safe captions optional only if submission player lacks caption support |
| 0:35–1:05 | MG02 with GV03 plate | Scene 2 narration | KF06–KF10 labels and study-independence limitation |
| 1:05–1:45 | MG03 scientific turn | Scene 3 narration | Exact hero lines and five-axis summary |
| 1:45–2:20 | MG04 plus unchanged fig08 | Scene 4 narration | Frozen metrics and null/not-tested distinction |
| 2:20–3:55 | Real Explorer master recording | Scene 5 narration | Minimal lower thirds only; do not cover real values |
| 3:55–4:07 | Real Explorer provenance select | Scene 6 opening | Provenance label |
| 4:07–4:31 | MG05 test/offline card plus unchanged fig09 | Scene 6 narration | Reproducibility and implemented boundary |
| 4:31–4:43 | MG05 plus GV04 future plate | Scene 6 future narration | Persistent `FUTURE` label |
| 4:43–4:55 | MG06 final lockup | Canonical closing | Product, title, `Context matters.`, optional GitHub URL |

## Track layout

| Track | Content | Rule |
|---|---|---|
| V1 | Primary picture | Motion graphics, existing figures, and Explorer footage only |
| V2 | Text overlays | Frozen on-screen copy; no restated scientific numbers |
| V3 | Captions / safe-area reference | Captions or guide layer; never cover UI values |
| A1 | Final narration | One consistent voice, normalized after edit |
| A2 | Room tone | Low, consistent, no audible loop |
| A3 | Optional music | Omit by default; use only if licensed and scientifically unobtrusive |
| A4 | Optional interface sound | Normally muted; no click effects required |

## Voiceover

- Record the 621-word script scene by scene and as one continuous safety take.
- Delivery target is approximately 126 words per minute.
- Maintain short pauses around `not broad concordance`, `context dependence`, and `observed null is different from not tested`.
- Pronounce decimal similarities digit by digit exactly as scripted.
- Do not improvise claims, abbreviate limitations, or substitute `confidence` for `similarity`.
- Use a clean, untreated recording at 48 kHz / 24-bit when possible.

## Explorer footage

- Use `scene05_explorer_ctx003_master_1920x1080.mov` as one continuous source.
- Preserve native UI timing around the rank cards and WHY expander.
- Straight cuts may remove travel time between scroll stops; avoid jump cuts inside a number or evidence row.
- Never replace a displayed number or component with a motion-graphic overlay.
- If a crop is required, crop from the native 1920 × 1080 master without scaling above 115%.

## Existing figures

- Place fig08 and fig09 unchanged within Pearl White frames.
- Do not recolor, relabel, erase legends, or animate individual scientific marks.
- Use a moving focus window outside the image rather than altering the image itself.
- fig10 and fig11 remain optional backups; the live Explorer is preferred for retrieval.

## Music and sound effects

The preferred master uses narration and subtle room tone only. If music is tested, use a properly licensed, minimal instrumental bed without vocals, percussion accents, medical-monitor sounds, or emotional crescendos. Keep it at least 18 dB below narration and remove it if any scientific word becomes harder to understand.

Do not add whooshes, digital beeps, heartbeats, sparkle sounds, camera shutters, or success chimes. Native click sounds are unnecessary.

## Captions

- Use `DEMO_V1_CAPTIONS.md` as the exact caption script.
- Produce a sidecar WebVTT or SRT file at assembly time.
- Maximum two lines per cue and approximately 42 characters per line when practical.
- Preserve `CTX001`, `CTX002`, `CTX003`, `OBSERVED_NULL`, `NOT_TESTED`, `NES`, `CCK-8`, signs, and four-decimal similarity values.
- Use sentence case; no all-caps captions except controlled state names.

## Color and type

- Work in Rec.709 / sRGB and verify Pearl White remains distinct from browser white.
- Deep Ink is the default text color.
- Use the frozen palette only; Champagne is an accent, never body text.
- Use the system sans-serif stack defined in `app/design_tokens.py` or an embeddable equivalent.

## Export and QA

- Master: 1920 × 1080, 30 fps, progressive, Rec.709.
- Delivery: H.264 high profile or competition-required format, with AAC 48 kHz audio.
- Runtime must be 4:55 or shorter and never exceed 5:00.
- Review the final upload locally at 1080p and 720p.
- Verify captions, figure rights, URL readability, scientific values, and absence of placeholders.
- Do not upload until the recording checklist is fully cleared.
