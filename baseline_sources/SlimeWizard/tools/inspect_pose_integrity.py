"""Read-only diagnostics for Slime Wizard saved pose identity and pixels.

Usage from extracted Slime Wizard folder:
    python tools/inspect_pose_integrity.py "C:/path/to/project.rig.json"

Does not save, alter, or upload project content.
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from studio.pet_suite_model import PetSuiteModel


def main():
    parser = argparse.ArgumentParser(description='Inspect saved timeline pose identities without changing files.')
    parser.add_argument('project', help='Slime Wizard project JSON manifest with matching asset folder')
    args = parser.parse_args()
    model = PetSuiteModel.load_project(args.project)
    print('Read-only Slime Wizard pose audit')
    print('Canvas: {} x {}'.format(*model.size))
    for name, poses in model.animations.items():
        print(f'Animation: {name} | {len(poses)} poses')
        prior = None
        for i, pose in enumerate(poses):
            data = model.render(pose).convert('RGBA').tobytes()
            sha = hashlib.sha256(data).hexdigest()[:16]
            ident = model.pose_id(name, i)[:12]
            visible = sum(state.get('visible', True) for state in pose)
            match = 'SAME AS PREVIOUS' if prior == data else 'different from previous'
            if prior is None:
                match = 'first pose'
            print(f'  Pose {i+1:03d}: ID {ident}, pixel SHA {sha}, visible layers {visible}, {match}')
            prior = data
    print('Audit finished; nothing was modified.')


if __name__ == '__main__':
    main()
