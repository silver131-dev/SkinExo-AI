# SkinExo-AI DEMO-V1 recording gate

Do not begin the final Explorer capture or video assembly until every **REQUIRED BEFORE RECORDING** item is checked.

## Version lock

| Item | Current value | Status |
|---|---|---|
| Branch | `public-v1` | DOCUMENTED |
| VISUAL-V1 UI | Included in the authoritative DEMO-FREEZE-C1 commit | FROZEN |
| Final recording commit | Commit containing `DEMO_V1_RECORDING_SOURCE.md`; exact hash is in the C1 completion report | FROZEN EXTERNALLY |
| Public GitHub URL | `https://github.com/silver131-dev/SkinExo-AI` | FROZEN |

Before capture, copy the exact DEMO-FREEZE-C1 hash into the D2 recording log and verify it with `git rev-parse HEAD`. Do not infer the recording version from file timestamps.

## Required before recording

- [x] VISUAL-V1 included in the authoritative DEMO-FREEZE-C1 commit.
- [ ] Exact C1 hash copied into the D2 recording log and verified against `git rev-parse HEAD`.
- [x] Explorer tests pass: 17/17.
- [x] Streamlit health check passes.
- [x] Frozen Atlas counts rechecked: 3 contexts, 339 components, 1,017 records.
- [x] Frozen CTX003 retrieval rechecked: CTX002 `+0.6053`, CTX001 `−0.2755`.
- [x] Narration frozen at 621 words.
- [x] Runtime frozen at 4:55 with five-second safety margin.
- [x] Six scenes frozen.
- [x] Thirty keyframes frozen.
- [x] On-screen text frozen.
- [x] Claim audit passes with zero unsupported positive claims.
- [x] Explorer click path frozen.
- [x] Browser resolution, zoom, cursor, and scroll plan frozen.
- [ ] Four generated visual plates created and accepted. — D2 BLOCKER
- [ ] Six motion graphics assembled from the frozen plan. — D2 BLOCKER
- [ ] Explorer master recording captured from the recording commit. — D2 BLOCKER
- [ ] All asset filenames and hashes added to the asset manifest. — D2 BLOCKER
- [x] GitHub URL frozen and readable.
- [x] Demo and Technical Report URL placeholders are not visible anywhere in the Explorer recording path.
- [x] No raw data, licensed PDF, local path, personal account, or browser notification is required on screen.

## Required before final assembly

- [ ] Narration recorded and checked against the frozen script.
- [ ] Caption timings conformed to final voiceover without wording changes.
- [ ] Existing figures inserted unchanged.
- [ ] Generated visuals pass copyright, scientific-boundary, and advertising-style review.
- [ ] Live Explorer footage contains no exploratory clicking or accidental UI state.
- [ ] All `FUTURE` material remains visibly labeled.
- [ ] No metric is called accuracy, probability, confidence, or prediction score.
- [ ] Music license documented, or music omitted.
- [ ] Final frame includes only the verified GitHub URL.

## Required before upload

- [ ] Runtime is 4:55 or shorter and never exceeds 5:00.
- [ ] 1080p review passes.
- [ ] 720p readability review passes.
- [ ] Captions enabled and checked.
- [ ] `+0.6053`, `−0.2755`, `+0.8563`, `9`, and `1.000` match frozen artifacts.
- [ ] No scientific result, state, classification, or reliability record changed during editing.
- [ ] No placeholder URL appears in rendered video or description.
- [ ] Final file and sidecar-caption hashes recorded.

## Current recording blockers

1. Exact C1 hash must be copied from the completion report into the D2 recording log.
2. Four generated visual plates are specified but not generated.
3. Six motion graphics are specified but not assembled.
4. The Explorer master has not been recorded, as required by D1’s stop condition.

**Recording gate: CLOSED until these blockers are resolved in DEMO-V1-D2.**
