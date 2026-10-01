# SkinExo-AI Explorer recording plan — DEMO-V1

## Capture specification

| Setting | Locked value |
|---|---|
| Master resolution | 1920 × 1080 |
| Frame rate | 30 fps constant |
| Browser | Chromium-family browser in full-screen presentation mode |
| Browser zoom | 100% |
| OS display scaling | 100% for capture session |
| Streamlit layout | Wide; no developer toolbar or browser sidebar visible |
| Cursor | Standard arrow, deliberate movement, no click halo or cursor trail |
| Capture codec | Lossless or visually lossless intermediate; edit delivery separately |
| Raw capture length | 1:45–2:00 |
| Final Scene 5 allocation | 1:35, from 2:20 to 3:55 |
| Network | Not required after local launch |

Use a clean browser profile. Disable notifications, password prompts, translation bars, extension badges, and operating-system pop-ups. Hide bookmarks and any account avatar if they reveal personal information.

## Pre-record launch

1. Start from the repository root with `streamlit run app/streamlit_app.py`.
2. Confirm the application reports no errors.
3. Open the local URL before capture begins; do not record the terminal or local path.
4. Enter full-screen presentation mode at 1920 × 1080 and 100% zoom.
5. Reload once, then wait three seconds for fonts, tables, and layout to settle.
6. Confirm **Select Context** defaults to **CTX003**.
7. Confirm **Explain retrieved target** defaults to **CTX002**.
8. Return to the top and place the cursor in unused Pearl White space.

## Locked click and scroll path

No exploratory clicking is permitted in the final take.

1. **Open Explorer:** begin at the hero and default CTX003 context.
2. **Show context card:** scroll one controlled step so EV source, recipient, dose, duration, dataset, and key limitations are visible together. Hold three seconds.
3. **Show P/M/E/A/I:** scroll to the Response Overview. Hold long enough to read all five cards and the phenotype indicators.
4. **Show component evidence:** at the Component Explorer, keep P selected briefly, then click **I · Inflammation / Immune Signaling** once. Do not alter activity-state filters.
5. **Open retrieval:** scroll directly to **Response Similarity**. Hold with both cards visible.
6. **Show ranks:** keep CTX002 rank 1 `+0.6053` and CTX001 rank 2 `−0.2755` simultaneously readable.
7. **Select target:** confirm the target selectbox is CTX002. Do not cycle through targets.
8. **Open WHY:** click **WHY THIS MATCH? · CTX003 vs CTX002** once.
9. **Show shared components:** scroll slowly through shared positive/negative response components.
10. **Show differences:** continue through discordant, CTX003-only, CTX002-only, and observed-null differences. Pause where section labels and at least one evidence row are readable.
11. **Show phenotype:** continue to Phenotype Evidence and pause on CCK-8, scratch assay, and the different-timepoint label.
12. **Show reliability:** continue to Reliability & Limitations and pause on recipient-donor independence and EV-preparation independence.
13. **Show provenance:** open Evidence Provenance once and hold the dataset, checkpoint, method, and gene-set release.
14. **Return to overview:** close provenance, then use a single smooth scroll to the CTX003 context/response area for the edit-out handle.

## Scroll map

| Stop | Required visible content | Minimum raw hold |
|---|---|---:|
| A | Hero + selected CTX003 label | 3 s |
| B | Context metadata + key limitations | 5 s |
| C | All five axis cards | 6 s |
| D | P then I component view | 8 s |
| E | Both retrieval rank cards | 8 s |
| F | WHY shared components | 8 s |
| G | WHY context-specific differences | 8 s |
| H | CCK-8, scratch, different-timepoint message | 8 s |
| I | Donor and EV-preparation reliability cards | 8 s |
| J | Provenance panel | 6 s |

## Sections to avoid

- Do not open the About tab during Scene 5.
- Do not switch to CTX001 or CTX002 as the query.
- Do not change state filters, similarity metric, or axis controls beyond the single P-to-I click.
- Do not expose browser history, bookmarks, account details, local filesystem paths, terminal windows, developer tools, or localhost URL text.
- Do not linger on large raw data tables or scroll their internal panes.
- Do not show loading spinners, warnings unrelated to scientific limitations, or failed UI states.
- Do not record mouse searching, accidental clicks, text selection, or scrollbar correction.

## Readability gate

- At 720p playback, `+0.6053`, `−0.2755`, `CCK-8`, `scratch assay`, `24 h`, `72 h`, and the two independence limitations must remain readable.
- Use only real Streamlit footage. Do not reconstruct UI screens in motion-graphics software.
- If five axis cards or both rank cards are not readable at 100% zoom, record a second native-resolution crop; do not digitally enlarge a low-resolution capture.

## Recording-source rule

Record only from the authoritative freeze commit that contains `DEMO_V1_RECORDING_SOURCE.md`. Copy the exact hash from the DEMO-FREEZE-C1 completion report into the D2 capture log before the final take, and require a clean working tree.
