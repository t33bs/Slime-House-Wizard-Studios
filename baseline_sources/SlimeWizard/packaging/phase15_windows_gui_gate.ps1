# Phase 15 GUI regression gate. Run in a Windows PowerShell terminal at repository root.
# Usage: powershell -ExecutionPolicy Bypass -File packaging\phase15_windows_gui_gate.ps1
$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot '..')
$env:QT_QPA_PLATFORM = 'offscreen'
$tests = @(
 'tests/test_phase15_sequential_slimer.py',
 'tests/test_phase15_repeated_moves_safety.py',
 'tests/test_phase15_repeated_overlay_moves.py',
 'tests/test_phase15_saved_pose_isolation_extra.py',
 'tests/test_phase15_timeline_insertion.py',
 'tests/test_phase15_timeline_history_stability.py',
 'tests/test_phase15_visibility_isolation.py',
 'tests/test_phase15_history_branch_and_pixel_snapshots.py',
 'tests/test_phase15_ui_stability_contract.py'
)
New-Item -ItemType Directory -Force -Path 'test-results' | Out-Null
python -c 'import PySide6; print("PySide6", PySide6.__version__)'
if ($LASTEXITCODE -ne 0) { throw 'PySide6 is missing; install requirements first.' }
python -m pytest -q -ra --junitxml=test-results/phase15-gui.xml @tests 2>&1 | Tee-Object -FilePath test-results/phase15-gui.txt
if ($LASTEXITCODE -ne 0) { throw 'Phase 15 targeted regression tests FAILED. Do not promote this build.' }
python -m pytest -q -ra --junitxml=test-results/full-suite.xml 2>&1 | Tee-Object -FilePath test-results/full-suite.txt
if ($LASTEXITCODE -ne 0) { throw 'Full regression suite FAILED. Do not promote this build.' }
Write-Host 'Phase 15 automated Windows gate passed. Manual GUI playtest is STILL REQUIRED.' -ForegroundColor Green
