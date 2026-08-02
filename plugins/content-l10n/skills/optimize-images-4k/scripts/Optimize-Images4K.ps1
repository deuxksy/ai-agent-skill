[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Root = ".",
    [ValidateRange(1, 100000)]
    [int]$Width = 3840,
    [ValidateRange(1, 100)]
    [int]$Quality = 90,
    [switch]$Apply,
    [switch]$VerifyOnly,
    [switch]$KeepPortrait,
    [switch]$KeepUndersized,
    [switch]$KeepKnownCovers,
    [switch]$NoRename
)

$ErrorActionPreference = "Stop"

function Find-Magick {
    $command = Get-Command magick -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $candidate = Get-ChildItem -Path @(
        "C:\Program Files\ImageMagick-*\magick.exe",
        "C:\Program Files (x86)\ImageMagick-*\magick.exe",
        "$env:LOCALAPPDATA\Programs\ImageMagick-*\magick.exe"
    ) -File -ErrorAction SilentlyContinue | Select-Object -First 1

    if (-not $candidate) {
        throw "ImageMagick magick.exe was not found."
    }
    return $candidate.FullName
}

function Get-Dimensions([string]$Path) {
    $dimensions = & $script:Magick identify -ping -format "%w %h" $Path 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "ImageMagick identify failed."
    }
    $parts = $dimensions -split "\s+"
    return [PSCustomObject]@{ Width = [int]$parts[0]; Height = [int]$parts[1] }
}

$resolvedRoot = (Resolve-Path -LiteralPath $Root).Path
$rootPrefix = $resolvedRoot.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
$script:Magick = Find-Magick
$imageExtensions = @(".jpg", ".jpeg", ".png")
$files = Get-ChildItem -LiteralPath $resolvedRoot -Recurse -File |
    Where-Object { $imageExtensions -contains $_.Extension.ToLowerInvariant() }

$stats = [ordered]@{
    SCANNED = 0
    DELETE_KNOWN_COVER = 0
    DELETE_PORTRAIT = 0
    DELETE_UNDERSIZED = 0
    OPTIMIZE = 0
    RENAME = 0
    UNCHANGED = 0
    FAILED = 0
}

foreach ($file in $files) {
    $stats.SCANNED++
    $temp = Join-Path $file.DirectoryName (".optimize-images-4k-" + [guid]::NewGuid().ToString("N") + ".jpg")
    try {
        if (-not $file.FullName.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "Target is outside the root directory."
        }

        $isKnownCover = $file.Name -like "*-board.jpg" -or
            $file.Name -like "*-poster.jpg" -or
            $file.Name -ieq "warning-cover.png"
        if ($isKnownCover -and -not $KeepKnownCovers) {
            $stats.DELETE_KNOWN_COVER++
            if ($Apply -and -not $VerifyOnly) { Remove-Item -LiteralPath $file.FullName -Force }
            continue
        }

        $dimensions = Get-Dimensions $file.FullName
        if ($dimensions.Height -gt $dimensions.Width -and -not $KeepPortrait) {
            $stats.DELETE_PORTRAIT++
            if ($Apply -and -not $VerifyOnly) { Remove-Item -LiteralPath $file.FullName -Force }
            continue
        }
        if ($dimensions.Width -lt $Width -and -not $KeepUndersized) {
            $stats.DELETE_UNDERSIZED++
            if ($Apply -and -not $VerifyOnly) { Remove-Item -LiteralPath $file.FullName -Force }
            continue
        }

        if ($dimensions.Width -gt $Width) {
            $stats.OPTIMIZE++
            if ($Apply -and -not $VerifyOnly) {
                if ($file.Extension -notin @(".jpg", ".jpeg")) {
                    throw "Only JPEG resize-in-place is supported: $($file.FullName)"
                }
                & $script:Magick -define "jpeg:size=${Width}x${Width}" $file.FullName `
                    -auto-orient -resize "${Width}x" -strip -sampling-factor "4:2:0" `
                    -interlace Plane -quality $Quality $temp 2>$null
                if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $temp)) {
                    throw "ImageMagick conversion failed."
                }
                $outputDimensions = Get-Dimensions $temp
                if ($outputDimensions.Width -ne $Width) {
                    throw "Output width is $($outputDimensions.Width), expected $Width."
                }
                Move-Item -LiteralPath $temp -Destination $file.FullName -Force
            }
        } else {
            $stats.UNCHANGED++
        }

        if (-not $NoRename -and $file.Name -match "-\d+px\.(jpg|jpeg)$") {
            $newName = $file.Name -replace "-\d+px\.(jpg|jpeg)$", "-${Width}px.$($Matches[1])"
            if ($newName -ne $file.Name) {
                $stats.RENAME++
                if ($Apply -and -not $VerifyOnly) {
                    $destination = Join-Path $file.DirectoryName $newName
                    if (Test-Path -LiteralPath $destination) {
                        throw "Rename collision: $destination"
                    }
                    Move-Item -LiteralPath $file.FullName -Destination $destination
                }
            }
        }
    } catch {
        $stats.FAILED++
        Write-Warning "$($file.FullName): $($_.Exception.Message)"
    } finally {
        if (Test-Path -LiteralPath $temp) {
            Remove-Item -LiteralPath $temp -Force
        }
    }
}

$stats.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }
"PORTRAIT_REMAINING=$($stats.DELETE_PORTRAIT)"
"UNDER_WIDTH_REMAINING=$($stats.DELETE_UNDERSIZED)"
"OVER_WIDTH_REMAINING=$($stats.OPTIMIZE)"
"MODE=$(if ($VerifyOnly) { 'VERIFY' } elseif ($Apply) { 'APPLY' } else { 'PREVIEW' })"
