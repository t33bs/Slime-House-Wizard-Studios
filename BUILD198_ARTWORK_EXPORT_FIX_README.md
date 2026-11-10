# SHWS Build 1.9.8 candidate — source-only artwork export repair

**Prepared 2026-11-09 (Eastern).** These are additive/focused repairs for the source tree, using the recovered Build197 source patch; **not** an updated, rebuilt Windows executable. The user's original Build197 portable ZIP and art files were not modified.

## Verified issues

1. The earlier GIF writer silently discarded all source pixels with alpha 1–127 (its cutoff was `<128`). In the supplied `ttnl` cape-flutter export, 653 pixels visible in APNG frame 1 were completely transparent in GIF frame 1. Re-encoding the supplied 8 cape frames and 64 wind-dialogue frames with the new encoder yielded 0 missing and 0 extra *visible pixel locations*, compared frame-for-frame against the APNG sources. No artist-chosen detached pixel is specially filtered.
2. `Export Current Frame` and `Export All Frames` read SAVED pose snapshots but did not call `preserve_pose_draft()` first, unlike other export routes. Thus newly cleaned canvas pixels might not make it into the exported PNG(s). This patch adds one safe export preflight to all four export pathways (frame, frames, animated GIF/APNG, sprite sheet), with pose-ownership verification and a hold for unsaved next poses or pending Slimer moves. It never silently exports an old pose when edited live pixels are uncommitted.

## Source files to replace (relative to current full SHWS source repo)

- `shws_wizard/friendly_animator.py`: export preflight/pose synchronization and guards
- `shws_wizard/studio/gif_export.py`: remove semi-alpha pixel deletion; shared palette reads unpremultiplied RGB for all nonzero-alpha pixels
- `tests/test_build198_artwork_export_integrity.py`: new focused regressions

**These files are NOT a complete source tree.** Apply on top of the Build197 source project, preserve everything else, commit in GitHub Desktop, and run the existing Windows build workflow. Do not drag `.py` files into the old `_internal` folder or rename the Build197 `.exe`: the portable binary must be rebuilt from source on Windows/CI.

## Tests performed here

- 51 targeted pytest cases passed: Build194 Cleaner pose integrity, Build195 canvas reopen, Build196 JSON reopen, Build197 naming, and new Build198 artwork integrity. Build195's current validation module was restored from its matching source patch for the test harness after an older baseline initially produced five unrelated failures.
- Real submitted rig's 72 RGBA APNG frames were independently compared with the saved rig snapshots and with sprite sheet cells: 0 frame mismatches.
- Re-encoded the 64-frame wind/dialogue GIF and 8-frame flutter GIF from the submitted APNGs: 0 visible pixel locations lost or spuriously introduced against each source frame.
- **Not tested:** actual Windows/Qt click workflows, rebuilt EXE, reimport into user's local install, or whether preexisting unsaved Cleaner strokes can be recovered from the supplied files.

## GIF format limitation

GIF has only **binary transparency** and at most **256 palette entries**. A source pixel with alpha 1–254 is represented as visible/opaque instead of being removed. Its opacity (and possibly RGB color, if the palette cannot hold every color) is necessarily approximated. Use the matching exported APNG `.png` or per-frame RGBA PNGs for exact alpha/color/pixel fidelity; those paths remain untouched. Converting an already-lossy old GIF cannot reconstruct lost pixels. The separate sample GIFs were recovered from the supplied APNG files, not the old GIF.

## Protection boundaries

- Never prune detached/floating pixel islands as 'noise'. Do not erase transparent RGB values in the `.rig.json` source or alter its timeline on export.
- Never rewrite a saved timeline frame from an unplaced next-pose draft or a different pose ID.
- Original Build197 portable/archive remains your intact rollback until a rebuilt Build198 candidate passes your Windows visual acceptance.
