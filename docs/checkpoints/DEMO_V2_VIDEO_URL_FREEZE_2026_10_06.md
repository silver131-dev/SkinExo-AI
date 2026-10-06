# SkinExo-AI — DEMO-V2 Demo Video URL Freeze (2026-10-06)

## Decision and canonical URL

- Final video: **FROZEN**; user Final Master review: **PASS**; creative edit: **LOCKED**.
- YouTube upload: **COMPLETE**, visibility **UNLISTED** (user-reported).
- User incognito playback: **PASS** (user-reported).
- `DEMO_VIDEO_URL`: **FROZEN** as https://youtu.be/optVRKKDNec.
- YouTube video ID: `optVRKKDNec`.
- YouTube thumbnail: **USER SELECTED**. It is not identified by the earlier local preview-frame hash.

The canonical local uploaded source master remains `submission/demo/production/final/SkinExo-AI_DEMO_V2_FINAL.mp4`: **04:58.48**, **1920×1080**, **25 fps**, SHA-256 `ce87e4185724c10ae4a2f535fe32746e24d7ef8b4375c1540d5bf33bb89b6e5f`. This source-file hash was recomputed at the URL-freeze checkpoint and matched the Final Video Freeze record. YouTube's transcoded playback file is not expected to have the same hash.

The previously approved local preview frame remains at `submission/demo/production/review/DEMO_V2_PREVIEW_FRAME_00m02s.png`, but the user chose a different thumbnail for YouTube. Do not present its SHA-256 as the YouTube thumbnail hash.

## Submission documentation updated

- `submission/kaggle_writeup.md` — canonical Demo link.
- `README.md` — current unlisted Demo link, replacing the stale not-recorded sentence.
- `submission/SUBMISSION_CHECKLIST.md` and `submission/final_qa.md` — Demo upload, playback, URL, and Final QA status.
- `submission/S2_CONSISTENCY_AUDIT.md` — dated addendum to its original S2 URL-pending state.
- `submission/S2_RUBRIC_MAPPING.md` — current Demo availability without claiming Kaggle submission.
- `submission/demo_storyboard.md` — identified as a historical production plan; canonical Final URL recorded.

Post-edit search found **zero submission-facing `DEMO_VIDEO_URL` placeholders**. The 2026-10-05 Final Video Freeze Markdown/JSON deliberately retain their at-the-time `DEMO_VIDEO_URL`-not-frozen state; this newer checkpoint supersedes that state without rewriting history. The Technical Report URL remains a separate submission gate.

## Scientific consistency

Public-facing copy and the Final video preserve the maturity boundaries:

| Stage | Capability | Status |
|---|---|---|
| TODAY | Observed Response Retrieval | IMPLEMENTED |
| NEXT | EV Candidate Screening | FUTURE / NOT CURRENTLY IMPLEMENTED |
| FUTURE | Response Prediction | NOT YET IMPLEMENTED |
| LONG-TERM VISION | Skin–EV Response Digital Twin | NOT IMPLEMENTED |

Scientific, numerical, terminology, and Final technical QA remain **PASS**. No scientific result, Explorer source, media asset, narration, caption, thumbnail, or Final MP4 was changed. The full repository test suite passed **22/22** on 2026-10-06.

## Publication boundary and next gate

This checkpoint is URL/documentation only. Do not commit production media, generated audio, or temporary renders. Do not upload another video, update the Final MP4, push automatically, or submit to Kaggle. The URL is frozen; Kaggle submission is **NOT DONE**.

**REVIEW COMMIT → PUSH PUBLIC-V1 (separate authorization) → KAGGLE FINAL QA → SUBMIT**
