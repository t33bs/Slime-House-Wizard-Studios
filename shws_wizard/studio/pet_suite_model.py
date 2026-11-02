"""Friendly Animator's editable asset/pose model.

Frame poses contain per-frame geometry. Source PNGs are preserved separately.
"""
import base64
import binascii
import io
import json
import math
import os
import tempfile
import shutil
import hashlib
import uuid
from copy import deepcopy
from pathlib import Path
from PIL import Image
from .creature_rig import CreatureRig

class PetSuiteModel(CreatureRig):
    def __init__(self, size=(128, 128)):
        super().__init__(size)
        self.originals = []
        # Per-pose recovery is kept separate from live artwork and exports.
        self.pose_recovery = {}
        self.pose_recovery_limit = 5
        self.pose_ids = {}  # Stable identities, independent of timeline positions.
        self.current = 'Idle / Breathing'
        self.frame_durations = {}  # milliseconds per frame, keyed by animation
        self.anchors = {}  # part index -> local anchor (x, y) in source pixels
        self.angles = {}  # part index -> degrees counterclockwise around joint
        self.attachments = {}  # child index -> {parent, offset_x, offset_y}; offsets are pixel coordinates
        self.unplaced_next_pose = None  # Pending canvas draft, keyed to saved pose identity.

    def import_part(self, name, image, width=None, height=None):
        original = image.convert('RGBA').copy()
        w, h = width or original.width, height or original.height
        self.add_part(name, original.resize((int(w), int(h)), Image.Resampling.NEAREST))
        self.originals.append(original)

    def remove_unconfirmed_part(self, index):
        """Remove a provisional asset and reindex rig metadata safely.

        Only a newly appended, unconfirmed Slimer asset may be removed here.
        Existing pose snapshots must not be rewritten or renumbered.
        """
        if index != len(self.parts) - 1 or index < 0:
            raise ValueError('Only the newest unconfirmed layer can be cancelled safely.')
        self.parts.pop(index)
        self.originals.pop(index)
        self.angles.pop(index, None)
        self.anchors.pop(index, None)
        self.attachments.pop(index, None)
        # A source asset may have been attached to the provisional destination.
        # Detach it rather than leaving a dangling parent index.
        for child, link in list(self.attachments.items()):
            if int(link.get('parent', -1)) == index:
                self.attachments.pop(child)

    def set_anchor(self, index, x, y):
        """Set an easy-to-see joint marker on a part in its current pixel coordinates."""
        if not 0 <= index < len(self.parts):
            raise ValueError("Choose a body part first.")
        part = self.parts[index]
        self.anchors[index] = [max(0, min(part["image"].width, int(x))),
                               max(0, min(part["image"].height, int(y)))]

    def rotate_part(self, index, degrees):
        """Set a non-destructive rotation in degrees about this part's joint dot."""
        if not 0 <= index < len(self.parts):
            raise ValueError('Choose a body part first.')
        self.angles[index] = float(degrees) % 360

    def render_part(self, index, state):
        """Render a part on a full transparent canvas so its joint stays stationary."""
        source = self._decode_source(state['source_png']) if state.get('source_png') else self.originals[index]
        w = max(1, int(state.get('width', self.parts[index]['image'].width)))
        h = max(1, int(state.get('height', self.parts[index]['image'].height)))
        part = source.resize((w, h), Image.Resampling.NEAREST)
        layer = Image.new('RGBA', self.size)
        x, y = int(state['x']), int(state['y'])
        # Copy source RGBA without applying its alpha twice.
        # The final render() performs the intended alpha composite once.
        layer.paste(part, (x, y))
        angle = float(state.get('angle', self.angles.get(index, 0)))
        if angle % 360:
            ax, ay = self.anchors.get(index, [w // 2, h // 2])
            # Joint coordinates are stored relative to the current resized part.
            layer = layer.rotate(angle, Image.Resampling.NEAREST,
                                 center=(x + ax, y + ay), expand=False)
        return layer

    def anchor_position(self, index):
        part = self.parts[index]
        ax, ay = self.anchors.get(index, [part["image"].width // 2, part["image"].height // 2])
        return part["x"] + ax, part["y"] + ay

    def attach(self, child, parent):
        """Attach a part to another part at its current position (no visual jump)."""
        if child == parent or not (0 <= child < len(self.parts) and 0 <= parent < len(self.parts)):
            raise ValueError('Choose two different, existing body parts.')
        ancestor = parent
        visited = set()
        while True:
            if ancestor == child or ancestor in visited:
                raise ValueError('That connection would create a loop.')
            visited.add(ancestor)
            if ancestor not in self.attachments:
                break
            ancestor = int(self.attachments[ancestor]['parent'])
            if not 0 <= ancestor < len(self.parts):
                raise ValueError('An attachment references a missing body part.')
        c, p = self.parts[child], self.parts[parent]
        self.attachments[child] = {'parent': parent, 'offset_x': c['x']-p['x'], 'offset_y': c['y']-p['y']}

    def detach(self, child):
        self.attachments.pop(child, None)

    def move_with_children(self, index, dx, dy):
        """Move a parent and descendants together; moving a child changes its attachment offset."""
        if not 0 <= index < len(self.parts):
            return
        def move(node, visited):
            if node in visited:
                raise ValueError('Circular creature attachment detected.')
            visited.add(node)
            self.parts[node]['x'] += int(dx)
            self.parts[node]['y'] += int(dy)
            for child, link in self.attachments.items():
                if link['parent'] == node:
                    move(child, visited)
            visited.remove(node)
        # Validate before mutating anything, so malformed saved rigs cannot half-move.
        def validate(node, seen):
            if node in seen:
                raise ValueError('Circular creature attachment detected.')
            seen.add(node)
            for child, link in self.attachments.items():
                if link['parent'] == node:
                    if not 0 <= child < len(self.parts):
                        raise ValueError('An attachment references a missing body part.')
                    validate(child, seen)
            seen.remove(node)
        validate(index, set())
        move(index, set())
        if index in self.attachments:
            self.attachments[index]['offset_x'] += int(dx)
            self.attachments[index]['offset_y'] += int(dy)

    def resize_part(self, index, width, height):
        source = self.originals[index]
        self.parts[index]['image'] = source.resize((max(1, int(width)), max(1, int(height))), Image.Resampling.NEAREST)

    def flip_part(self, index, axis):
        """Flip the selected PNG source, retaining its current displayed dimensions."""
        if not 0 <= index < len(self.parts):
            raise ValueError('Select an asset before flipping.')
        if axis not in ('horizontal', 'vertical'):
            raise ValueError('Flip direction must be horizontal or vertical.')
        source = self.originals[index]
        w, h = self.parts[index]['image'].size
        method = Image.Transpose.FLIP_LEFT_RIGHT if axis == 'horizontal' else Image.Transpose.FLIP_TOP_BOTTOM
        self.originals[index] = source.transpose(method)
        self.resize_part(index, w, h)
        if index in self.anchors:
            x, y = self.anchors[index]
            self.anchors[index] = [w - x if axis == 'horizontal' else x,
                                   h - y if axis == 'vertical' else y]

    def reset_part_size(self, index):
        """Restore imported pixel dimensions without changing position."""
        if not 0 <= index < len(self.parts):
            raise ValueError('Select an asset before resetting its size.')
        self.resize_part(index, *self.originals[index].size)

    def center_part(self, index, axis='both'):
        """Center the selected part on the creature canvas, in pixel coordinates."""
        if not 0 <= index < len(self.parts):
            raise ValueError('Select an asset before centering.')
        if axis not in ('horizontal', 'vertical', 'both'):
            raise ValueError('Invalid alignment axis.')
        part = self.parts[index]
        if axis in ('horizontal', 'both'):
            part['x'] = (self.size[0] - part['image'].width) // 2
        if axis in ('vertical', 'both'):
            part['y'] = (self.size[1] - part['image'].height) // 2

    def _sync_pose_ids(self, animation):
        """Ensure legacy timelines receive unique identities without altering pixels."""
        frames = self.animations.get(animation, [])
        ids = self.pose_ids.setdefault(animation, [])
        # Recovery is keyed by pose ID across the entire project, not by
        # (animation, pose ID). A legacy/corrupt file may reuse an ID in two
        # different animations; reserve those IDs before repairing this list.
        seen = {pose_id for other, values in self.pose_ids.items()
                if other != animation and isinstance(values, list)
                for pose_id in values if isinstance(pose_id, str) and pose_id}
        for i in range(len(frames)):
            if i >= len(ids):
                ids.append(uuid.uuid4().hex)
            if not isinstance(ids[i], str) or not ids[i] or ids[i] in seen:
                ids[i] = uuid.uuid4().hex
            seen.add(ids[i])
        del ids[len(frames):]
        return ids

    def pose_id(self, animation, index):
        ids = self._sync_pose_ids(animation)
        if not 0 <= index < len(ids):
            raise IndexError('Choose an existing timeline pose.')
        return ids[index]

    def save_frame(self, animation=None):
        """Append a new pose with its own identity, including the legacy GUI path."""
        name = animation or self.current
        return self.insert_frame(name, len(self.animations.get(name, [])))

    def insert_frame(self, animation, index, pose=None):
        """Insert an independent editable pose at the requested frame position."""
        frames = self.animations.setdefault(animation, [])
        index = max(0, min(int(index), len(frames)))
        self._sync_pose_ids(animation)
        frames.insert(index, deepcopy(self.snapshot() if pose is None else pose))
        self.pose_ids[animation].insert(index, uuid.uuid4().hex)
        self._sync_durations(animation, count=len(frames)-1)
        self.frame_durations[animation].insert(index, self.frame_durations[animation][index-1] if index > 0 and index-1 < len(self.frame_durations[animation]) else 125)
        return index

    def merged_working_pose(self, source_pose, name):
        """Create a one-layer *new* pose from the rendered source pose.

        Existing source poses and their independent per-part PNG snapshots are
        never rewritten.  Append a new full-canvas RGBA asset whose pixels are
        the exact visible composite; retain old part states hidden in the new
        pose for model-index stability and older-pose round trips.  The caller
        inserts the returned pose as a new frame and clears its old draft key.
        """
        if len(source_pose) > len(self.parts):
            raise ValueError('Source pose refers to unavailable asset layers.')
        rendered = self.render(source_pose).convert('RGBA').copy()
        self.import_part(name, rendered)
        # The model retains a global asset table so snapshots from previous
        # poses can still address their independent original layers.  Preserve
        # all source states exactly except for their NEW pose visibility.
        combined = self.snapshot()
        for i, state in enumerate(source_pose):
            combined[i] = deepcopy(state)
        for state in combined[:-1]:
            state['visible'] = False
        combined[-1]['visible'] = True
        return combined

    def copy_frame(self, animation, index):
        frames = self.animations.get(animation, [])
        if not 0 <= index < len(frames):
            raise IndexError('Choose a saved pose to copy.')
        return self.insert_frame(animation, index + 1, frames[index])

    def delete_frame(self, animation, index):
        frames = self.animations.get(animation, [])
        if not 0 <= index < len(frames):
            raise IndexError('Choose a saved pose to remove.')
        self._sync_durations(animation)
        self.frame_durations[animation].pop(index)
        removed_id = self.pose_id(animation, index)
        self.pose_ids[animation].pop(index)
        self.pose_recovery.pop(removed_id, None)
        return frames.pop(index)

    def move_frame(self, animation, index, direction):
        frames = self.animations.get(animation, [])
        destination = index + direction
        if not (0 <= index < len(frames) and 0 <= destination < len(frames)):
            return index
        ids = self._sync_pose_ids(animation)
        frames[index], frames[destination] = frames[destination], frames[index]
        ids[index], ids[destination] = ids[destination], ids[index]
        self._sync_durations(animation)
        times = self.frame_durations[animation]
        times[index], times[destination] = times[destination], times[index]
        return destination

    def reorder_frame(self, animation, source, target):
        """Move a saved pose, its stable identity, and duration together."""
        frames = self.animations.get(animation, [])
        if not (0 <= source < len(frames) and 0 <= target < len(frames)):
            return source
        if source == target:
            return source
        ids = self._sync_pose_ids(animation)
        times = self._sync_durations(animation)
        frames.insert(target, frames.pop(source))
        ids.insert(target, ids.pop(source))
        times.insert(target, times.pop(source))
        return target

    def _sync_durations(self, animation, count=None):
        count = len(self.animations.get(animation, [])) if count is None else count
        times = self.frame_durations.setdefault(animation, [])
        while len(times) < count:
            times.append(125)
        del times[count:]
        return times

    def set_frame_duration(self, animation, index, milliseconds):
        times = self._sync_durations(animation)
        if not 0 <= index < len(times):
            raise IndexError('Choose a saved pose first.')
        times[index] = max(40, min(2000, int(milliseconds)))

    def frame_duration(self, animation, index):
        times = self._sync_durations(animation)
        return times[index] if 0 <= index < len(times) else 125

    def playback_frame_at(self, animation, elapsed_ms):
        times = self._sync_durations(animation)
        if not times:
            return 0
        position = int(elapsed_ms) % sum(times)
        for index, duration in enumerate(times):
            if position < duration:
                return index
            position -= duration
        return len(times) - 1

    def _store_pose_recovery(self, animation, index):
        """Retain an immutable copy before overwriting an existing timeline pose."""
        frames = self.animations.get(animation, [])
        if not 0 <= index < len(frames):
            raise IndexError('Choose an existing pose to edit.')
        key = self.pose_id(animation, index)
        versions = self.pose_recovery.setdefault(key, [])
        versions.append(deepcopy(frames[index]))
        del versions[:-self.pose_recovery_limit]

    def restore_previous_pose(self, animation, index):
        """Recover the last saved version without touching any other pose."""
        key = self.pose_id(animation, index)
        versions = self.pose_recovery.get(key, [])
        if not versions:
            return False
        frames = self.animations.get(animation, [])
        if not 0 <= index < len(frames):
            raise IndexError('Choose an existing pose to recover.')
        previous = versions.pop()
        frames[index] = deepcopy(previous)
        if not versions:
            self.pose_recovery.pop(key, None)
        return True

    def save_pose_at(self, animation, index):
        """Save only the selected pose, retaining its previous saved pixels."""
        frames = self.animations.setdefault(animation, [])
        if not 0 <= index < len(frames):
            raise IndexError('Choose an existing pose to edit.')
        updated = deepcopy(self.snapshot())
        if updated != frames[index]:
            self._store_pose_recovery(animation, index)
            frames[index] = updated
        return deepcopy(frames[index])

    def erase_pose_source_pixels(self, animation, frame_index, part_index, indices):
        """Copy-on-write erase of one saved frame's source pixels.

        Never mutates live part buffers or another frame's source. The caller
        must separately validate rendered selection provenance before erasing.
        """
        from shws_wizard.studio.pixel_source_mapping import erase_planned_source_pixels
        frames = self.animations.get(animation, [])
        if not 0 <= frame_index < len(frames):
            raise IndexError('Choose an existing pose to edit.')
        if not 0 <= part_index < len(frames[frame_index]):
            raise IndexError('Choose an existing part in that pose.')
        state = frames[frame_index][part_index]
        if not state.get('source_png'):
            raise ValueError('Saved pose has no independent source image.')
        source = self._decode_source(state['source_png'])
        updated = erase_planned_source_pixels(source, indices)
        if updated.tobytes() == source.tobytes():
            return False
        replacement = deepcopy(frames[frame_index])
        replacement[part_index]['source_png'] = self._encode_source(updated)
        self._store_pose_recovery(animation, frame_index)
        frames[frame_index] = replacement
        return True

    def erase_selected_pose_pixels(self, animation, frame_index, part_index, selection_mask):
        """Safely move a complete rendered selection out of one saved pose.

        This intentionally supports only a single visible, unattached part.
        Multi-layer compositing and inherited rig transforms require a separate
        provenance planner; refusing them avoids silently erasing wrong pixels.
        """
        from .pixel_source_mapping import rendered_source_indices, plan_complete_source_erase
        frames = self.animations.get(animation, [])
        if not 0 <= frame_index < len(frames):
            raise IndexError('Choose an existing pose to edit.')
        pose = frames[frame_index]
        if not 0 <= part_index < len(pose):
            raise IndexError('Choose an existing part in that pose.')
        if selection_mask.size != tuple(self.size):
            raise ValueError('Selection must match the canvas size.')
        if selection_mask.mode != 'L':
            raise ValueError('Selection must be a grayscale L mask.')
        if self.attachments:
            raise ValueError('Attached parts require resolved rig provenance.')
        visible = [i for i, state in enumerate(pose) if state.get('visible', True)]
        if visible != [part_index]:
            raise ValueError('Saved-pose erase currently requires one visible part.')
        state = pose[part_index]
        if not state.get('source_png'):
            raise ValueError('Saved pose has no independent source image.')
        source = self._decode_source(state['source_png'])
        width = int(state.get('width', source.width))
        height = int(state.get('height', source.height))
        x, y = int(state['x']), int(state['y'])
        angle = float(state.get('angle', self.angles.get(part_index, 0)))
        anchor = self.anchors.get(part_index, [width // 2, height // 2])
        mapping = rendered_source_indices(source.size, self.size, x, y, width, height,
                                          angle, anchor)
        alpha = self.render_part(part_index, state).getchannel('A')
        plan = plan_complete_source_erase(mapping, alpha, selection_mask)
        if plan is None:
            raise ValueError('Selection includes only part of a transformed source pixel.')
        for label, opacity, selected in zip(mapping.get_flattened_data(),
                                            alpha.get_flattened_data(),
                                            selection_mask.get_flattened_data()):
            if selected and (label <= 0 or opacity == 0):
                raise ValueError('Selection includes pixels outside the visible source.')
        return self.erase_pose_source_pixels(animation, frame_index, part_index, plan)

    def edit_pose_at(self, animation, index, changes):
        """Apply per-part geometry to one pose without changing any other pose.

        This is deliberately anatomy-agnostic: parts may be any shape or size.
        """
        frames = self.animations.get(animation, [])
        if not 0 <= index < len(frames):
            raise IndexError('Choose an existing pose to edit.')
        pose = deepcopy(frames[index])
        for part_index, geometry in changes.items():
            if not 0 <= part_index < len(pose):
                raise IndexError('Choose an existing part.')
            for key, value in geometry.items():
                if key not in ('x','y','width','height','angle','visible'):
                    raise ValueError('Unknown pose property: ' + key)
                if key in ('width','height') and int(value) < 1:
                    raise ValueError('A part must be at least one pixel in size.')
                pose[part_index][key] = value
        if pose != frames[index]:
            self._store_pose_recovery(animation, index)
            frames[index] = pose
        return deepcopy(pose)

    @staticmethod
    def _encode_source(image):
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode('ascii')

    @staticmethod
    def _decode_source(encoded):
        with Image.open(io.BytesIO(base64.b64decode(encoded))) as image:
            return image.convert('RGBA').copy()

    def snapshot(self):
        return [dict(source_png=self._encode_source(self.originals[i]), name=p['name'], x=int(p['x']), y=int(p['y']),
                     width=p['image'].width, height=p['image'].height, angle=self.angles.get(i, 0),
                     visible=p.get('visible', True)) for i, p in enumerate(self.parts)]

    def replace_frame_image(self, animation, index, image, *, mode='exact', base_pose=None):
        """Place an RGBA PNG in one pose without mutating any other pose.

        ``exact`` stores the imported PNG's original RGBA pixels verbatim;
        transparent pixels stay transparent, even when their RGB is black.
        ``overlay`` first renders a distinct *previous* pose, then composites
        the PNG above it as one editable working image.  The source pose and
        all existing layer snapshots, IDs, durations and sources remain intact.
        Hidden inherited states are kept only for cross-pose layer indexing.
        """
        frames=self.animations.get(animation,[])
        if not 0<=index<len(frames):
            raise IndexError('Choose a saved pose first.')
        if image.size!=tuple(self.size):
            raise ValueError('Replacement PNG must match the creature canvas size.')
        if mode not in ('exact', 'overlay'):
            raise ValueError('Unknown PNG pose import mode.')
        if mode == 'overlay':
            if base_pose is None:
                raise ValueError('Overlay import requires the previous pose snapshot.')
            # Render from the SAVED source snapshot, never the live model after
            # appending an asset or switching timeline frames.
            underlying = self.render(base_pose).convert('RGBA').copy()
            underlying.alpha_composite(image.convert('RGBA'))
            imported_image = underlying
        else:
            imported_image = image.convert('RGBA').copy()
        # Import as a new part rather than overwriting any shared source asset.
        label = f'Pose {index+1} over previous artwork' if mode == 'overlay' else f'Frame {index+1} PNG edit'
        self.import_part(label,imported_image)
        new_index=len(self.parts)-1
        state=self.snapshot()[new_index]
        # The replacement is a full frame: old layers must not show through.
        pose=deepcopy(frames[index])
        for old in pose:old['visible']=False
        pose.append(state)
        if pose != frames[index]:
            self._store_pose_recovery(animation, index)
        frames[index]=pose
        return new_index

    def apply_pose(self, pose):
        # Newly imported parts must not leak into earlier, shorter pose snapshots.
        for i in range(len(pose),len(self.parts)):
            self.parts[i]["visible"]=False
        for i, state in enumerate(pose):
            if i >= len(self.parts):
                break
            p = self.parts[i]
            if state.get('source_png'):
                self.originals[i] = self._decode_source(state['source_png'])
            p['x'], p['y'] = int(state['x']), int(state['y'])
            p['visible'] = state.get('visible', True)
            self.resize_part(i, state.get('width', p['image'].width), state.get('height', p['image'].height))
            self.angles[i] = float(state.get('angle', 0))

    def resolved_pose(self, pose=None):
        """Return positions and angles with parent transforms applied, without edits."""
        states = deepcopy(pose if pose is not None else self.snapshot())
        n = min(len(states), len(self.parts))
        original_angles = [float(states[i].get('angle', 0)) for i in range(n)]
        pivots = []
        for i in range(n):
            state = states[i]
            w = int(state.get('width', self.parts[i]['image'].width))
            h = int(state.get('height', self.parts[i]['image'].height))
            ax, ay = self.anchors.get(i, [w // 2, h // 2])
            pivots.append((float(state['x']) + ax, float(state['y']) + ay, ax, ay))

        def point_through(node, x, y, visited=None):
            visited = set() if visited is None else visited
            if node in visited:
                raise ValueError('Circular creature attachment detected.')
            visited.add(node)
            px, py, _, _ = pivots[node]
            angle = math.radians(original_angles[node])
            dx, dy = x - px, y - py
            x = px + dx * math.cos(angle) + dy * math.sin(angle)
            y = py - dx * math.sin(angle) + dy * math.cos(angle)
            link = self.attachments.get(node)
            if link is not None:
                parent = int(link['parent'])
                if not 0 <= parent < n:
                    raise ValueError('An attachment references a missing body part.')
                return point_through(parent, x, y, visited)
            return x, y

        def parent_angle(index, visited=None):
            visited = set() if visited is None else visited
            if index in visited:
                raise ValueError('Circular creature attachment detected.')
            visited.add(index)
            angle = original_angles[index]
            link = self.attachments.get(index)
            if link is not None:
                parent = int(link['parent'])
                if not 0 <= parent < n:
                    raise ValueError('An attachment references a missing body part.')
                angle += parent_angle(parent, visited)
            return angle

        for i in range(n):
            px, py, ax, ay = pivots[i]
            link = self.attachments.get(i)
            if link is not None:
                parent = int(link['parent'])
                if not 0 <= parent < n:
                    raise ValueError('An attachment references a missing body part.')
                px, py = point_through(parent, px, py)
            states[i]['x'] = round(px - ax)
            states[i]['y'] = round(py - ay)
            states[i]['angle'] = parent_angle(i)
        return states[:n]

    def render(self, pose=None):
        canvas = Image.new('RGBA', self.size)
        for i, state in enumerate(self.resolved_pose(pose)):
            if not state.get('visible', True):
                continue
            canvas.alpha_composite(self.render_part(i, state))
        return canvas

    def save_project(self, path):
        path = Path(path)
        # Stage immutable PNG assets in a fresh sibling directory. Never
        # overwrite the files referenced by the last committed manifest.
        asset_dir = f'{path.stem}_assets_{uuid.uuid4().hex}'
        folder = path.parent / asset_dir
        folder.mkdir(parents=True, exist_ok=False)
        try:
            for i, image in enumerate(self.originals):
                image.save(folder / f'original_{i:03d}.png')
        except BaseException:
            shutil.rmtree(folder, ignore_errors=True)
            raise
        data = dict(version=3, asset_dir=asset_dir, size=list(self.size), parts=self.snapshot(),
                    animations=self.animations, frame_durations=self.frame_durations,
                    pose_ids={name: self._sync_pose_ids(name)[:] for name in self.animations},
                    pose_recovery={pose_id: deepcopy(history[-self.pose_recovery_limit:])
                                   for pose_id, history in self.pose_recovery.items()
                                   if history and any(pose_id in ids for ids in self.pose_ids.values())},
                    current=self.current, attachments=self.attachments, anchors=self.anchors, angles=self.angles)
        # An unplaced NEXT pose must survive Save Creature and reopen without
        # silently overwriting an earlier saved frame. The editable live draft
        # is already serialized in `parts`; keep only its stable owner marker.
        unplaced = getattr(self, 'unplaced_next_pose', None)
        if unplaced is not None:
            data['unplaced_next_pose'] = dict(unplaced)
        # Commit the project manifest last. A failed/interrupted write must not
        # truncate the previously saved JSON file.
        temporary = None
        committed = False
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                             dir=path.parent, prefix=f'.{path.name}.',
                                             suffix='.tmp', delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(data, stream, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
            committed = True
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
            if not committed:
                shutil.rmtree(folder, ignore_errors=True)


    @classmethod
    def load_project(cls, path):
        path = Path(path)
        from .project_recovery import diagnose_project_assets, require_project_assets
        from .project_validation import validate_project_file
        data = validate_project_file(path)
        report = diagnose_project_assets(path)
        missing = bool(report['missing'])
        if not missing:
            # Keep the established full-PNG integrity checks on ordinary rigs.
            from .project_png_validation import validate_project_pngs
            validate_project_pngs(path, data)
        elif any(not isinstance(state.get('source_png'), str) or not state['source_png']
                 for i, state in enumerate(data['parts'])
                 if not (report['asset_folder'] / f'original_{i:03d}.png').is_file()
                 and not (report['asset_folder'] / f'part_{i:03d}.png').is_file()):
            # Legacy JSONs may embed original artwork, but missing actual
            # artwork with NO embedded fallback must still fail safely.
            require_project_assets(path)
        folder = report['asset_folder']
        # Decode all sources before creating any model state; never write to
        # an original project or reconstruct a missing folder during Open.
        images = []
        for i, state in enumerate(data['parts']):
            original_path = folder / f'original_{i:03d}.png'
            if not original_path.is_file():
                original_path = folder / f'part_{i:03d}.png'
            if original_path.is_file():
                with Image.open(original_path) as image:
                    if image.format != 'PNG':
                        raise ValueError(f'Invalid project artwork: {original_path.name} is not a PNG.')
                    image.load()
                    images.append(image.convert('RGBA').copy())
            else:
                encoded = state['source_png']
                if len(encoded) > 48 * 1024 * 1024:
                    raise ValueError(f'Embedded artwork for part {i+1} exceeds the safe import limit.')
                try:
                    raw = base64.b64decode(encoded, validate=True)
                    with Image.open(io.BytesIO(raw)) as image:
                        if image.format != 'PNG':
                            raise ValueError('Embedded artwork is not PNG.')
                        image.load()
                        images.append(image.convert('RGBA').copy())
                except (ValueError, OSError, binascii.Error) as exc:
                    raise ValueError(f'Cannot open creature: embedded PNG artwork for part {i+1} '
                                     'is damaged. The project was not changed.') from exc
        model = cls(data['size'])
        for state, image in zip(data['parts'], images):
            model.import_part(state['name'], image,
                              state.get('width', image.width), state.get('height', image.height))
            model.parts[-1]['x'] = int(state['x'])
            model.parts[-1]['y'] = int(state['y'])
            model.parts[-1]['visible'] = state.get('visible', True)
        model.animations = data.get('animations', {})
        model.pose_ids = data.get('pose_ids', {})
        for animation in model.animations: model._sync_pose_ids(animation)
        valid_ids = {pose_id for ids in model.pose_ids.values() for pose_id in ids}
        raw_recovery = data.get('pose_recovery', {})
        if isinstance(raw_recovery, dict):
            model.pose_recovery = {pose_id: deepcopy(history[-model.pose_recovery_limit:])
                                   for pose_id, history in raw_recovery.items()
                                   if pose_id in valid_ids and isinstance(history, list)
                                   and all(isinstance(pose, list) for pose in history)}
        model.frame_durations = data.get('frame_durations', {})
        for animation in model.animations: model._sync_durations(animation)
        model.current = data.get('current', 'Idle / Breathing')
        model.unplaced_next_pose = data.get('unplaced_next_pose')
        model.attachments = {int(k): v for k, v in data.get('attachments', {}).items()}
        model.anchors = {int(k): v for k, v in data.get('anchors', {}).items()}
        model.angles = {int(k): float(v) for k, v in data.get('angles', {}).items()}
        return model


    def content_fingerprint(self):
        """Stable digest of editable content, including original PNG pixels."""
        payload = dict(size=self.size, parts=self.snapshot(), animations=self.animations,
                       frame_durations=self.frame_durations, current=self.current,
                       anchors=self.anchors, angles=self.angles, attachments=self.attachments,
                       unplaced_next_pose=getattr(self, 'unplaced_next_pose', None))
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode('utf-8'))
        for original in self.originals:
            digest.update(str(original.size).encode('ascii'))
            digest.update(original.tobytes())
        return digest.hexdigest()

    def export(self, folder, basename='creature', columns=4, spacing=0):
        """Export a transparent atlas with real per-pose timing and pixel rectangles.

        This overrides CreatureRig.export, whose generic 125ms timing is not
        suitable for authored animation timelines. No live project data changes.
        """
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        frames, entries = [], []
        for animation, poses in self.animations.items():
            for index, pose in enumerate(poses):
                frames.append(self.render(pose).convert('RGBA'))
                entries.append({'animation': animation, 'frame': index,
                                'duration_ms': self.frame_duration(animation, index)})
        if not frames:
            frames = [self.render().convert('RGBA')]
            entries = [{'animation': 'Idle', 'frame': 0, 'duration_ms': 125}]
        columns = max(1, min(int(columns), len(frames)))
        spacing = max(0, int(spacing))
        width, height = self.size
        rows = math.ceil(len(frames) / columns)
        atlas = Image.new('RGBA', (columns * width + (columns - 1) * spacing,
                                   rows * height + (rows - 1) * spacing))
        for index, frame in enumerate(frames):
            x = (index % columns) * (width + spacing)
            y = (index // columns) * (height + spacing)
            atlas.alpha_composite(frame, (x, y))
            entries[index]['rect'] = {'x': x, 'y': y, 'w': width, 'h': height}
        png_path = folder / f'{basename}_sheet.png'
        json_path = folder / f'{basename}_sheet.json'
        atlas.save(png_path)
        json_path.write_text(json.dumps({'version': 1, 'frame_size': [width, height],
                                         'sheet_size': list(atlas.size), 'frames': entries},
                                        indent=2), encoding='utf-8')
        return png_path

    def export_individual_frames(self, folder, basename='creature'):
        """Export independent transparent PNGs and their pose timing metadata."""
        folder = Path(folder)
        entries = []
        used = set()
        for animation, poses in self.animations.items():
            if not poses:
                continue
            safe = ''.join(ch if ch.isalnum() or ch in '-_' else '_' for ch in animation).strip('_') or 'animation'
            unique = safe
            suffix = 2
            while unique.casefold() in used:
                unique = f'{safe}_{suffix}'
                suffix += 1
            used.add(unique.casefold())
            for index, pose in enumerate(poses):
                name = f'{basename}_{unique}_{index+1:04d}.png'
                entries.append((name, self.render(pose).convert('RGBA'), animation, index))
        if not entries:
            raise ValueError('Add and save at least one animation pose before exporting.')
        folder.mkdir(parents=True, exist_ok=True)
        manifest = []
        for name, frame, animation, index in entries:
            frame.save(folder / name, 'PNG')
            manifest.append({'file': name, 'animation': animation, 'frame': index,
                             'duration_ms': self.frame_duration(animation, index),
                             'loop': True})
        metadata = folder / f'{basename}_frames.json'
        metadata.write_text(json.dumps({'version': 1, 'frame_size': list(self.size),
                                        'frames': manifest}, indent=2), encoding='utf-8')
        return [folder / name for name, _, _, _ in entries], metadata

    def export_animations(self, folder, basename='creature', gif=True, apng=True):
        """Export looping GIFs and animated PNGs without renaming single animations."""
        folder = Path(folder)
        saved = [(animation, poses) for animation, poses in self.animations.items() if poses]
        if not saved:
            raise ValueError('Add and save at least one animation pose before exporting.')
        if not (gif or apng):
            raise ValueError('Select GIF and/or APNG to export.')
        folder.mkdir(parents=True, exist_ok=True)
        exported = []
        used_names = set()
        multiple = len(saved) > 1
        for animation, poses in saved:
            frames = [self.render(pose).convert('RGBA') for pose in poses]
            durations = [self.frame_duration(animation, i) for i in range(len(poses))]
            # Only multi-animation exports need an animation label to avoid
            # overwriting one animation with another. Collapse separators for
            # readable names like Idle_Breathing, not Idle___Breathing.
            stem = str(basename)
            if multiple:
                safe = ''.join(ch if ch.isalnum() or ch in '-_' else '_' for ch in animation)
                safe = '_'.join(part for part in safe.split('_') if part) or 'animation'
                candidate = safe
                suffix = 2
                while candidate.casefold() in used_names:
                    candidate = f'{safe}_{suffix}'
                    suffix += 1
                used_names.add(candidate.casefold())
                stem = f'{basename}_{candidate}'
            if gif:
                from .gif_export import encode_gif
                output = folder / f'{stem}.gif'
                encode_gif(frames, durations, output)
                exported.append(output)
            if apng:
                # APNG is animated PNG content; .png plays correctly in Brave.
                from .apng_export import encode_apng
                output = folder / f'{stem}.png'
                encode_apng(frames, durations, output)
                exported.append(output)
        return exported

    def reorder_part(self, index, offset):
        target = index + offset
        if not (0 <= index < len(self.parts) and 0 <= target < len(self.parts)):
            return False
        self.parts[index], self.parts[target] = self.parts[target], self.parts[index]
        self.originals[index], self.originals[target] = self.originals[target], self.originals[index]
        for frames in self.animations.values():
            for pose in frames:
                if index < len(pose) and target < len(pose):
                    pose[index], pose[target] = pose[target], pose[index]
        def remap(i):
            return target if i == index else index if i == target else i
        self.attachments = {remap(child): {**link, 'parent': remap(link['parent'])}
                            for child, link in self.attachments.items()}
        self.anchors = {remap(i): anchor for i, anchor in self.anchors.items()}
        self.angles = {remap(i): angle for i, angle in self.angles.items()}
        return True
