"""Static safety checks for the approved Phase 103 PORTABLE Windows release.

The earlier suite hard-coded the retired Friendly Animator installer/upgrade
workflow. Phase 103 is distributed as a portable ZIP with no installer. These
checks intentionally continue protecting test-before-build, GUI smoke,
resource bundling and release integrity without requiring an installer.
"""
import unittest
from pathlib import Path

from studio.release_config import APP_VERSION

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github/workflows/build-friendly-animator.yml'


def workflow_source():
    return WORKFLOW.read_text(encoding='utf-8')


class WindowsReleasePipelineTests(unittest.TestCase):
    def test_windows_ci_builds_portable_exe_and_smokes_it(self):
        workflow = workflow_source()
        for term in ('runs-on: windows-latest',
                     'python -I -m PyInstaller --noconfirm --clean --onedir --windowed',
                     '--name SlimeWizard',
                     'studio/assets/wizard_slime.ico',
                     '--add-data "studio/assets;studio/assets"',
                     'dist/SlimeWizard/SlimeWizard.exe',
                     "Test-Path 'dist/SlimeWizard/_internal'",
                     '--smoke-test', 'ExitCode'):
            with self.subTest(term=term):
                self.assertIn(term, workflow)

    def test_pyinstaller_isolation_avoids_local_packaging_module_shadow(self):
        # Our own packaging/ directory is an importable package, so a normal
        # `python -m PyInstaller` launch from repo root hides PyPI packaging.
        workflow = workflow_source()
        self.assertIn('python -I -c "import packaging.requirements; import PyInstaller;', workflow)
        self.assertIn('python -I -m PyInstaller', workflow)
        self.assertNotIn('python -m PyInstaller --noconfirm', workflow)
        self.assertTrue((ROOT / 'packaging/__init__.py').exists())

    def test_gui_smoke_checks_window_transitions_and_resources(self):
        code = (ROOT / 'friendly_animator.py').read_text(encoding='utf-8')
        self.assertIn("'--smoke-test' in sys.argv", code)
        for term in ('showMinimized', 'showMaximized', 'showNormal',
                     'bundled_resource_report'):
            with self.subTest(term=term):
                self.assertIn(term, code)

    def test_legacy_installer_config_remains_valid_but_is_not_run(self):
        # Keeping the optional installer spec in source is fine; it is not
        # part of this portable-only release workflow.
        iss = (ROOT / 'packaging/FriendlyAnimator.iss').read_text(encoding='utf-8')
        self.assertIn(f'#define AppVersion "{APP_VERSION}"', iss)
        self.assertIn('UninstallDisplayIcon', iss)
        self.assertIn('PrivilegesRequired=lowest', iss)
        self.assertNotIn('[UninstallDelete]', iss)
        workflow = workflow_source()
        for retired_step in ('ISCC.exe', 'Windows-Installer',
                             '/VERYSILENT', 'unins000.exe'):
            with self.subTest(retired_step=retired_step):
                self.assertNotIn(retired_step, workflow)

    def test_release_pipeline_produces_portable_zip_and_checksum(self):
        workflow = workflow_source()
        for term in ("Compress-Archive -Path 'dist/SlimeWizard'",
                     'SlimeWizard-Phase103-Windows-Portable.zip',
                     'Get-FileHash -Algorithm SHA256',
                     'SlimeWizard-Phase103-SHA256.txt',
                     'SlimeWizard-Phase103-Windows-Portable',
                     'actions/upload-artifact@v4',
                     'if-no-files-found: error'):
            with self.subTest(term=term):
                self.assertIn(term, workflow)

    def test_smoke_checks_actual_window_states_and_resizing(self):
        code = (ROOT / 'friendly_animator.py').read_text(encoding='utf-8')
        for term in ('window.isMinimized()', 'window.isMaximized()',
                     'screen.availableGeometry()', 'window.resize(',
                     '(800,600)', '(1280,720)', '(1920,1080)'):
            with self.subTest(term=term):
                self.assertIn(term, code)

    def test_windows_runner_records_qt_diagnostics(self):
        workflow = workflow_source()
        self.assertIn('Record Windows display and Qt runtime diagnostics', workflow)
        self.assertIn('PySide6.__version__', workflow)

    def test_github_release_retains_python_313_and_two_test_gates(self):
        workflow = workflow_source()
        self.assertIn("python-version: '3.13'", workflow)
        self.assertIn('python -m unittest discover -s tests -q', workflow)
        self.assertIn('python -u -m pytest -vv --tb=short', workflow)
        self.assertNotIn('pytest -vv -x', workflow)  # collect all errors, never hide failures
        self.assertIn('if: always()', workflow)  # publish test logs even on failure
        self.assertLess(workflow.index('Run existing unittest regressions'),
                        workflow.index('Build portable Windows EXE folder'))
        self.assertLess(workflow.index('Run full pytest and GUI regressions'),
                        workflow.index('Build portable Windows EXE folder'))


class WindowsBuildTimeoutTests(unittest.TestCase):
    def test_windows_build_and_gui_checks_have_time_limits(self):
        workflow = workflow_source()
        self.assertIn('runs-on: windows-latest\n    timeout-minutes: 45', workflow)
        for name, limit in (
            ('Run existing unittest regressions', 10),
            ('Run full pytest and GUI regressions', 15),
            ('Build portable Windows EXE folder', 10),
            ('Verify packaged GUI starts', 5),
            ('Package portable ZIP and checksum', 5),
        ):
            with self.subTest(name=name):
                self.assertIn(f'- name: {name}\n        shell: pwsh\n        timeout-minutes: {limit}', workflow)


class WindowsPytestGateTests(unittest.TestCase):
    def test_windows_ci_runs_pytest_before_packaging(self):
        workflow = workflow_source()
        pytest_command = ('python -u -m pytest -vv --tb=short --durations=20 '
                          '--timeout=120 --timeout-method=thread tests')
        self.assertIn(pytest_command, workflow)
        self.assertIn('Pytest regression suite failed', workflow)
        self.assertIn('SlimeWizard-Phase103-Windows-Test-Logs', workflow)
        self.assertLess(workflow.index(pytest_command),
                        workflow.index('python -I -m PyInstaller --noconfirm'))
