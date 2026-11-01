"""Phase 3: each Slimer highlight phase retains independent transform controls."""
from pathlib import Path


def test_phase_switch_saves_and_restores_independent_transforms():
    source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    method = source.split('    def slimer_switch_phase(self, name):', 1)[1].split('    def _update_slimer_color_button', 1)[0]
    assert 'self.slimer_phase_transforms[previous]=' in method
    assert 'self.slimer_phase_transforms.get(name,(0,0,0,100))' in method
    assert 'with blocked_signals(spin):' in method
    assert 'self.slimer_selection.mask=self.slimer_phase_masks.get(name' in method


def test_clear_selection_clears_all_phase_transforms():
    source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    method = source.split('    def slimer_clear(self):', 1)[1].split('    def _slimer_erase_original_layers', 1)[0]
    assert 'self.slimer_phase_transforms={}' in method

def test_phase_transforms_do_not_leak_across_creatures_or_tool_reactivation():
    source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    reset = source.split('    def _reset_slimer_for_project_change(self):', 1)[1].split('    def activate_project(', 1)[0]
    toggle = source.split('    def slimer_toggle_mode(', 1)[1].split('    def slimer_finish_selecting(', 1)[0] if '    def slimer_toggle_mode(' in source else source.split('    def slimer_toggle_tool(', 1)[1].split('    def slimer_finish_selecting(', 1)[0]
    assert 'self.slimer_phase_transforms={}' in reset
    assert 'self.slimer_phase_transforms={}' in toggle
