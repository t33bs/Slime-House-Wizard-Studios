"""Import-free checks that protect both independently developed editors."""
from pathlib import Path
import ast
import hashlib

ROOT=Path(__file__).resolve().parents[1]


def test_all_core_modules_compile():
    sources=[ROOT/'main.py',* (ROOT/'studio').rglob('*.py'),*(ROOT/'shws_wizard').rglob('*.py')]
    assert len(sources)>30
    for p in sources:
        compile(p.read_bytes(),str(p),'exec')


def test_shs_runtime_source_is_unchanged():
    for p in (ROOT/'studio').rglob('*.py'):
        original=ROOT/'baseline_sources'/'SHS'/p.relative_to(ROOT)
        assert original.is_file(),p
        assert p.read_bytes()==original.read_bytes(),f'Unexpected SHS editor change: {p}'


def test_wizard_has_independent_module_namespace():
    sources=list((ROOT/'shws_wizard').rglob('*.py'))
    assert len(sources)>20
    for p in sources:
        content=p.read_text(encoding='utf8')
        assert 'from studio.' not in content, p
        assert 'import studio.' not in content, p
    assert 'from shws_wizard.studio.pet_suite_model import PetSuiteModel' in (ROOT/'shws_wizard'/'friendly_animator.py').read_text()


def test_wizard_models_same_logic_as_original():
    for p in (ROOT/'shws_wizard'/'studio').rglob('*.py'):
        original=ROOT/'baseline_sources'/'SlimeWizard'/'studio'/p.relative_to(ROOT/'shws_wizard'/'studio')
        assert original.exists()
        expected=original.read_text(encoding='utf8').replace('from studio.','from shws_wizard.studio.').replace('import studio.','import shws_wizard.studio.')
        assert p.read_text(encoding='utf8')==expected, f'Wizard model logic diverged: {p}'


def test_unified_host_contains_real_qt_editors_and_safe_handoff():
    src=(ROOT/'main.py').read_text(encoding='utf8')
    for text in ('self.tabs.addTab(self.studio', 'self.tabs.addTab(self.wizard',
                 'class EmbeddedWizard', 'self._unified_host.studio.open_external_png',
                 'self.wizard.reload_shs_edit()', 'def closeEvent'):
        assert text in src


def test_packaging_has_portable_and_uninstallable_installer():
    workflow=(ROOT/'.github/workflows/build-windows.yml').read_text(encoding='utf8')
    installer=(ROOT/'packaging/SHWS.iss').read_text(encoding='utf8')
    assert '--onedir' in workflow and '--smoke-test' in workflow
    assert 'Compress-Archive' in workflow
    assert 'unins000.exe' in workflow
    assert 'Uninstallable=yes' in installer
    assert 'recursesubdirs' in installer
    assert 'Slime Buddy AI laboratory' not in workflow


def test_originals_retained_for_independent_regressions():
    assert (ROOT/'baseline_sources/SHS/tests').is_dir()
    assert (ROOT/'baseline_sources/SlimeWizard/tests').is_dir()
    assert (ROOT/'baseline_sources/SlimeWizard/friendly_animator.py').read_text() != ''


def test_independent_live_models_and_undisturbed_export_contract():
    from studio.pet_suite_model import PetSuiteModel as SHSModel
    from shws_wizard.studio.pet_suite_model import PetSuiteModel as WizardModel
    shs = SHSModel((128,128))
    wizard = WizardModel((128,128))
    assert SHSModel is not WizardModel
    assert shs.size == wizard.size == (128,128)
    assert shs.parts is not wizard.parts
    source=(ROOT/'shws_wizard'/'studio'/'pet_suite_model.py').read_text(encoding='utf8')
    assert "f'{stem}.png'" in source  # animated PNG extension preserved
    assert "multiple = len(saved) > 1" in source  # no unnecessary animation suffix
