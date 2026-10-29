$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$bundledEncoder = Join-Path $projectRoot '.runtime\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
if (Test-Path -LiteralPath $bundledEncoder) { $encoderPath = $bundledEncoder }
else { $encoderPath = (Get-Command ffmpeg -ErrorAction Stop).Source }
$inputPattern = Join-Path $projectRoot 'animation\frames\frame_%04d.png'
$videoPath = Join-Path $projectRoot 'animation\NJUST_Campus_Flythrough_18s.mp4'
& $encoderPath -y -framerate 24 -start_number 1 -i $inputPattern -frames:v 432 -c:v libx264 -threads 6 -preset medium -crf 19 -pix_fmt yuv420p -movflags +faststart $videoPath
if ($LASTEXITCODE -ne 0) { throw 'Video encoding failed' }
