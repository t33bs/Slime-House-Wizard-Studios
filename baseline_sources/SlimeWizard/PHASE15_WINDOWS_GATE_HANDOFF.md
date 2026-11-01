# Phase 15 Windows GUI validation gate

Run on a Windows development machine with Python, PySide6 and requirements installed:

```powershell
python -m pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File packaging\phase15_windows_gui_gate.ps1
```

The script runs Phase 15 targeted tests and the full suite, saving plain-text logs and JUnit XML in `test-results/`. Any failure exits with an error; do not promote a failing build. Inspect skipped tests carefully: a skipped GUI test is **not** a GUI pass.

After automated checks, manually verify with the portable EXE: Move Original same pixel twice, Undo twice/Redo twice, Copy Pixels source preservation, Apply Move vs Place Frame, re-edit middle saved pose, hide/restore asset in one pose, insert a pose in the middle, and Save/Open/Export. Confirm neighboring frames and transparency after each step.

The Linux environment for this checkpoint does not have PySide6; Windows GUI tests remain unverified. The Phase 14 green build is the fallback. Do not test the installer until requested.
