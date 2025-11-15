# --------------------------------------------
# Read Build + UBR from registry
# --------------------------------------------

$reg = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion"

$MajorBuild = (Get-ItemProperty -Path $reg -Name CurrentBuild).CurrentBuild
$UBRraw     = (Get-ItemProperty -Path $reg -Name UBR).UBR

Write-Host "Detected Build: $MajorBuild.$UBRraw"
Write-Host ""

# --------------------------------------------
# Convert UBR to decimal (it may be hex)
# --------------------------------------------

# If UBR is hex (like 0x1AF3)
if ($UBRraw -is [string] -and $UBRraw -match "^0x[0-9A-Fa-f]+$") {
    $UBR = [int]("0x" + $UBRraw.Substring(2))
} else {
    # Already decimal
    $UBR = [int]$UBRraw
}

# --------------------------------------------
# Thresholds
# KB5066835 = broken (UBR 6899 - 6900)
# KB5070773 = fixed  (UBR 6901+)
# --------------------------------------------

$BrokenStart = 6899
$FixedStart  = 6901

# --------------------------------------------
# Determine 24H2 / 25H2 branch
# --------------------------------------------

switch ($MajorBuild) {

    26100 {   # Windows 11 24H2
        if ($UBR -lt $BrokenStart) {
            Write-Host "Status: NOT AFFECTED"
            Write-Host "This build is earlier than the KB5066835 WinRE bug."
            break
        }

        if ($UBR -ge $BrokenStart -and $UBR -lt $FixedStart) {
            Write-Host "Status: BROKEN"
            Write-Host "Your build is inside the KB5066835 WinRE mouse/keyboard input bug window."
            break
        }

        if ($UBR -ge $FixedStart) {
            Write-Host "Status: FIXED"
            Write-Host "Your build contains KB5070773 or later. WinRE USB input is repaired."
            break
        }
    }

    26200 {   # Windows 11 25H2
        if ($UBR -lt $BrokenStart) {
            Write-Host "Status: NOT AFFECTED"
            Write-Host "This build is earlier than the KB5066835 WinRE bug."
            break
        }

        if ($UBR -ge $BrokenStart -and $UBR -lt $FixedStart) {
            Write-Host "Status: BROKEN"
            Write-Host "Your build is inside the KB5066835 WinRE mouse/keyboard input bug window."
            break
        }

        if ($UBR -ge $FixedStart) {
            Write-Host "Status: FIXED"
            Write-Host "Your build contains KB5070773 or later. WinRE USB input is repaired."
            break
        }
    }

    default {
        Write-Host "Status: UNKNOWN"
        Write-Host "This script is intended for Windows 11 24H2 (26100.x) and 25H2 (26200.x)."
    }
}
