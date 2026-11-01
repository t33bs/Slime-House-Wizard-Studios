import json
import tempfile
import unittest
from pathlib import Path
from studio.asset_versions import inspect_asset_versions, cleanup_asset_versions


class AssetVersionsTests(unittest.TestCase):
    def test_inspect_and_explicit_cleanup_preserve_current_and_unrelated(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'cat.rig.json'
            prefix = project.stem + '_assets_'
            active = root / (prefix + 'a' * 32)
            old = root / (prefix + 'b' * 32)
            other = root / ('other_assets_' + 'c' * 32)
            for folder in (active, old, other):
                folder.mkdir()
                (folder / 'original_000.png').write_bytes(b'pixels')
            project.write_text(json.dumps({'asset_dir': active.name}))
            result = inspect_asset_versions(project)
            self.assertEqual(result['orphans'], [old])
            self.assertEqual(cleanup_asset_versions(project), [])
            self.assertTrue(old.exists())
            self.assertEqual(cleanup_asset_versions(project, confirmed=True), [])
            removed = cleanup_asset_versions(project, confirmed=True, backup_inventory_complete=True)
            self.assertEqual(len(removed), 1)
            self.assertEqual(removed[0].name, old.name)
            self.assertTrue(removed[0].parent.samefile(old.parent))
            self.assertTrue(active.exists())
            self.assertTrue(other.exists())

    def test_cleanup_allows_equivalent_active_path_spellings(self):
        # Windows can resolve a short 8.3 directory name to a long name
        # between the first inspection and the safety recheck.
        from unittest.mock import patch
        from studio import asset_versions
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'cat.json'
            active = root / ('cat_assets_' + 'a' * 32)
            old = root / ('cat_assets_' + 'b' * 32)
            active.mkdir(); old.mkdir()
            (root / 'alias').mkdir()
            project.write_text(json.dumps({'asset_dir': active.name}))
            real_inspect = asset_versions.inspect_asset_versions
            calls = [0]

            def alternate_spelling(path):
                result = real_inspect(path)
                calls[0] += 1
                if calls[0] == 1:
                    # The same directory via an equivalent but different
                    # lexical spelling (the cross-platform form of the bug).
                    result['active'] = root / 'alias' / '..' / active.name
                return result

            with patch.object(asset_versions, 'inspect_asset_versions', alternate_spelling):
                removed = asset_versions.cleanup_asset_versions(
                    project, confirmed=True, backup_inventory_complete=True)
            self.assertEqual(len(removed), 1)
            self.assertEqual(removed[0].name, old.name)
            self.assertTrue(removed[0].parent.samefile(old.parent))
            self.assertFalse(old.exists())
            self.assertTrue(active.exists())

    def test_legacy_manifest_disables_cleanup(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / 'cat.json'
            project.write_text('{"version": 1}')
            self.assertFalse(inspect_asset_versions(project)['safe_to_clean'])
            self.assertEqual(cleanup_asset_versions(project, confirmed=True), [])

    def test_other_manifest_reference_protects_old_version(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'cat.json'
            prefix = 'cat_assets_'
            active = root / (prefix + 'a' * 32)
            old = root / (prefix + 'b' * 32)
            active.mkdir(); old.mkdir()
            (root / 'alias').mkdir()
            project.write_text(json.dumps({'asset_dir': active.name}))
            (root / 'backup.json').write_text(json.dumps({'asset_dir': old.name}))
            self.assertEqual(cleanup_asset_versions(project, confirmed=True, backup_inventory_complete=True), [])
            self.assertTrue(old.exists())

    def test_external_backup_reference_blocks_deletion(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            work = root / 'work'; backup = root / 'backups' / 'snapshots'
            work.mkdir(); backup.mkdir(parents=True)
            project = work / 'cat.json'
            active = work / ('cat_assets_' + 'a' * 32)
            old = work / ('cat_assets_' + 'b' * 32)
            active.mkdir(); old.mkdir()
            (root / 'alias').mkdir()
            project.write_text(json.dumps({'asset_dir': active.name}))
            (backup / 'previous.json').write_text(json.dumps({'asset_dir': old.name}))
            self.assertEqual(cleanup_asset_versions(project, confirmed=True,
                backup_roots=[root / 'backups'], backup_inventory_complete=True), [])
            self.assertTrue(old.exists())

    def test_unknown_backup_location_blocks_cleanup(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'cat.json'
            active = root / ('cat_assets_' + 'a' * 32)
            old = root / ('cat_assets_' + 'b' * 32)
            active.mkdir(); old.mkdir()
            (root / 'alias').mkdir()
            project.write_text(json.dumps({'asset_dir': active.name}))
            self.assertEqual(cleanup_asset_versions(project, confirmed=True), [])
            self.assertEqual(cleanup_asset_versions(project, confirmed=True,
                backup_roots=[root / 'missing'], backup_inventory_complete=True), [])
            self.assertTrue(old.exists())

class AssetRecoveryReportTests(unittest.TestCase):
    def test_report_lists_active_available_and_missing_referenced_versions(self):
        from studio.asset_versions import report_asset_recovery
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            work = root / 'work'; backups = root / 'backups'
            work.mkdir(); backups.mkdir()
            project = work / 'cat.json'
            a = 'cat_assets_' + 'a' * 32
            b = 'cat_assets_' + 'b' * 32
            c = 'cat_assets_' + 'c' * 32
            (work / a).mkdir(); (work / b).mkdir()
            (work / a / 'frame.png').write_bytes(b'png')
            project.write_text(json.dumps({'asset_dir': a}))
            (backups / 'old.json').write_text(json.dumps({'asset_dir': c}))
            report = report_asset_recovery(project, backup_roots=[backups])
            versions = {v['name']: v for v in report['versions']}
            self.assertEqual(versions[a]['status'], 'active')
            self.assertEqual(versions[a]['png_count'], 1)
            self.assertEqual(versions[b]['status'], 'available')
            self.assertEqual(versions[c]['status'], 'missing')
            self.assertEqual(len(versions[c]['referenced_by']), 1)
            self.assertTrue((work / b).exists())

    def test_report_warns_on_missing_backup_and_malformed_manifest(self):
        from studio.asset_versions import report_asset_recovery
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'cat.json'
            project.write_text(json.dumps({'asset_dir': 'cat_assets_' + 'a' * 32}))
            (root / 'broken.json').write_text('{')
            report = report_asset_recovery(project, backup_roots=[root / 'missing'])
            self.assertGreaterEqual(len(report['warnings']), 2)
            self.assertEqual(report['versions'][0]['status'], 'missing')
