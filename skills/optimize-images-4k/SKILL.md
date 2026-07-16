---
name: optimize-images-4k
description: ImageMagick으로 image 모음을 정리·최적화해 4K landscape 출력 생성. Use when 세로 이미지 삭제, 최소 너비 미만 이미지 삭제, wider JPEG를 3840px로 resize(aspect ratio 유지), 해상도 suffix rename(-6000px.jpg→-3840px.jpg), cover 파일 제거, 또는 image 모음 검증이 필요할 때.
---

# Optimize Images 4K

Use `scripts/Optimize-Images4K.ps1` instead of rebuilding fragile ImageMagick loops.

## Workflow

1. Confirm ImageMagick is installed. The script discovers `magick.exe` from `PATH` and common Windows install locations.
2. Run a preview first:

```powershell
& scripts/Optimize-Images4K.ps1 -Root <target>
```

3. Report preview counts. Obtain confirmation before destructive work unless the user already explicitly requested deletion or conversion.
4. Apply the requested cleanup and conversion:

```powershell
& scripts/Optimize-Images4K.ps1 -Root <target> -Apply
```

5. Verify separately:

```powershell
& scripts/Optimize-Images4K.ps1 -Root <target> -VerifyOnly
```

## Defaults

- Recurse through all subdirectories.
- Process `.jpg` and `.jpeg`.
- Delete images where height is greater than width.
- Delete images where width is less than `3840`.
- Resize images wider than `3840` to exactly `3840px`, preserving aspect ratio.
- Optimize JPEGs with metadata stripping, 4:2:0 sampling, progressive encoding, and quality 90.
- Rename a trailing resolution suffix such as `-6000px.jpg` to `-3840px.jpg`.
- Delete `*-board.jpg`, `*-poster.jpg`, and `warning-cover.png`.
- Leave images already exactly 3840px wide uncompressed.

## Options

- Use `-Width <pixels>` for a target other than 3840.
- Use `-Quality <1-100>` to change JPEG quality.
- Use `-KeepPortrait`, `-KeepUndersized`, or `-KeepKnownCovers` to disable deletions.
- Use `-NoRename` to preserve filenames.

## Safety Rules

- Never add `--` before Windows source paths in ImageMagick conversion commands; it can strip path separators in this environment.
- Replace an original only after the temporary output exists and verifies at the target width.
- Never overwrite a rename collision.
- Treat `FAILED=0`, `PORTRAIT_REMAINING=0`, `UNDER_WIDTH_REMAINING=0`, and `OVER_WIDTH_REMAINING=0` as required completion evidence.
