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


def test_shs_source_changes_are_limited_to_approved_tools_and_saving():
    # All other SHS modules remain byte-for-byte identical to the source baseline.
    for p in (ROOT/'studio').rglob('*.py'):
        if p.name in ('app.py','chameleon_tool.py','reference_viewer.py'):
            continue
        original=ROOT/'baseline_sources'/'SHS'/p.relative_to(ROOT)
        assert original.is_file(),p
        assert p.read_bytes()==original.read_bytes(),f'Unexpected SHS module change: {p}'
    original=(ROOT/'baseline_sources/SHS/studio/app.py').read_text(encoding='utf8')
    runtime=(ROOT/'studio/app.py').read_text(encoding='utf8')
    before,after=ast.parse(original),ast.parse(runtime)
    def methods(tree):
        return {n.name:n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    b,a=methods(before),methods(after)
    allowed={
        'cursor_for_tool','__init__','mousePressEvent','chameleon_at',
        'reset_chameleon_sample','save_project_as','load_project','new_project',
        'setup_classic_menus','closeEvent','open_external_png','change_size',
        'clear_canvas','restore_snapshot','install_beginner_helpers',
        'save_external_png','sample_color_at','activate_tool',
        'toggle_reference_window','reference_visibility_changed','sample_reference_at',
    }
    assert set(a)-set(b)=={'chameleon_at','reset_chameleon_sample','save_project_as',
                           'activate_paint_bucket','toggle_reference_window',
                           'reference_visibility_changed','sample_reference_at'}
    assert set(b)-set(a)==set()
    for name in set(b)-allowed:
        assert ast.dump(a[name],include_attributes=False)==ast.dump(b[name],include_attributes=False),name
    assert 'from .chameleon_tool import sample_2x2, stamp_2x2' in runtime
    assert 'from .reference_viewer import ReferenceDock' in runtime
    viewer=(ROOT/'studio/reference_viewer.py').read_text(encoding='utf8')
    assert 'class ReferenceDock(QDockWidget)' in viewer
    assert 'class ReferenceDock(QDockWidget)' not in original
    assert 'shws_wizard' not in viewer
    assert 'self.reference_dock=ReferenceDock(self)' in runtime
    assert 'self.chameleon_sample=None' in runtime
    # Build 1.5 may add only the linked-PNG completion signal and keyboard binding.
    main_window = next(n for n in after.body if isinstance(n,ast.ClassDef) and n.name=='MainWindow')
    assert 'self._linked_png_save_callback=None' in runtime
    assert "('P',self.activate_universal_brush),('B',self.activate_paint_bucket)" in runtime
    assert 'callback(str(target.resolve()))' in runtime


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
        if p.name in ('asset_hit_test.py', 'export_diagnostics.py'):
            # Build 1.4 adds one pure, isolated hit-test helper; all original
            # Wizard model modules remain protected by their baseline checks.
            assert not original.exists()
            continue
        assert original.exists()
        expected=original.read_text(encoding='utf8').replace('from studio.','from shws_wizard.studio.').replace('import studio.','import shws_wizard.studio.')
        actual=p.read_text(encoding='utf8')
        if p.name in ('pet_suite_model.py', 'project_validation.py'):
            # Build1.1 explicitly adds unplaced-next-pose persistence to these
            # two Wizard modules. Verify every OTHER existing function stays
            # AST-identical to the approved standalone baseline.
            before=ast.parse(expected)
            after=ast.parse(actual)
            def methods(tree):
                found={}
                for node in ast.walk(tree):
                    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                        found[node.name]=ast.dump(node,include_attributes=False)
                return found
            b,a=methods(before),methods(after)
            allowed=({'__init__','save_project','load_project','content_fingerprint'}
                     if p.name=='pet_suite_model.py' else {'validate_project_data'})
            for name in b:
                if name not in allowed:
                    assert a.get(name)==b[name],f'Changed baseline Wizard method {p}:{name}'
            assert set(a)==set(b),f'Unexpected method added/removed in {p}'
        elif p.name == 'ui_pixel_theme.py':
            # Build 1.3 adds a strictly append-only, scoped layout style.
            # The Phase 99–103 approved QSS must remain byte-for-byte intact.
            assert actual.startswith(expected), f'Existing Wizard styles changed: {p}'
            extra=actual[len(expected):]
            assert 'BUILD13_CANVAS_TIMELINE_QSS' in extra
            assert extra.strip().endswith('PIXEL_THEME_QSS += BUILD13_CANVAS_TIMELINE_QSS')
        elif p.name == 'apng_export.py':
            # Build 1.9.1 uses full-frame SOURCE replacement and verifies
            # decoded RGBA before atomically publishing an APNG.
            assert 'disposal=1, blend=0' in actual
            assert 'os.replace(temporary, output)' in actual
            assert "decoded.convert('RGBA').tobytes() != expected.tobytes()" in actual
        else:
            assert actual==expected, f'Wizard model logic diverged: {p}'


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
