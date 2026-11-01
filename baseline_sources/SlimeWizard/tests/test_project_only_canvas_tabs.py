"""Regression guard: canvas strip is for open creature projects only."""
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()


def test_initial_canvas_tabs_only_create_project():
    init = SOURCE.split('self.change_anim(self.anim.currentText());self.toggle_mode(initial=True);', 1)[1].split('\n', 1)[0]
    assert 'add_workspace_tab("project"' in init
    assert 'add_workspace_tab("animation"' not in init
    assert 'add_workspace_tab("phase"' not in init


def test_workspace_menu_has_no_recipe_or_phase_actions():
    body = SOURCE.split('    def workspace_menu(self):', 1)[1].split('    def turn_part(', 1)[0]
    assert 'New creature project' in body
    assert 'Open another creature' in body
    assert 'Rename current creature' in body
    assert 'Assembly' not in body and 'Rigging' not in body and 'Timeline' not in body


def test_animation_changes_do_not_create_canvas_tabs():
    body = SOURCE.split('    def change_anim(self,name):', 1)[1].split('    def ', 1)[0]
    assert 'select_workspace_key' not in body
    assert "self.model.current=name" in body


def test_only_project_tabs_are_accepted():
    body = SOURCE.split('    def add_workspace_tab(self,kind,name):', 1)[1].split('    def select_workspace_key(', 1)[0]
    assert "if kind != 'project':" in body


def test_timeline_and_all_working_pose_controls_are_preserved():
    # Either the original heading or the cosmetic Phase 99 heading is valid.
    # The guard protects the actual editing controls, not a particular label.
    marker = ("ml.addWidget(QLabel('POSE TIMELINE"
              if "ml.addWidget(QLabel('POSE TIMELINE" in SOURCE
              else "timeline_title=QLabel('▣ POSE TIMELINE")
    layout = SOURCE.split(marker, 1)[1].split('splitter.addWidget(self.scroll_panel(middle))', 1)[0]
    assert 'self.timeline=PoseTimelineList()' in layout or 'self.timeline=QListWidget()' in layout
    for label in ('self.duration=QSpinBox()',
                  'Save Current Pose', 'Restore Previous Pose', 'Duplicate last frame',
                  'Previous frame', 'Next frame', 'Insert pose after selected',
                  'Import Pose PNG', 'Copy pose', 'Remove pose',
                  'Shift pose', 'self.shift_pose(1)'):
        assert label in layout, f'Missing working timeline control: {label}'


def test_workspace_switching_and_closing_have_no_recipe_branches():
    switch = SOURCE.split('    def switch_workspace_tab(self,index):', 1)[1].split('    def workspace_menu(', 1)[0]
    close = SOURCE.split('    def close_workspace_tab(self,index):', 1)[1].split('    def autosave_recovery(', 1)[0]
    assert 'self.activate_project(project_id)' in switch
    assert "kind != 'project'" in switch
    assert 'self.close_creature_project(project_id)' in close
    for body in (switch, close):
        assert 'kind=="animation"' not in body
        assert 'kind=="phase"' not in body
