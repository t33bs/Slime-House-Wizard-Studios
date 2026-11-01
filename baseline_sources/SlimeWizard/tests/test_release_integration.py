import base64
import tempfile
import unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from studio.update_manager import verify_manifest
from studio.resource_checks import bundled_resource_report
from packaging.sign_release import build_manifest

class ReleaseIntegrationTests(unittest.TestCase):
    def test_signed_release_roundtrip(self):
        key = Ed25519PrivateKey.generate()
        raw = key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
        pub = base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()
        with tempfile.TemporaryDirectory() as folder:
            installer = Path(folder) / 'installer.exe'
            installer.write_bytes(b'dummy installer for signing test')
            envelope = build_manifest('0.43.1', installer, 'https://github.com/example/project/releases/download/v0.43.1/installer.exe', raw)
            self.assertEqual(verify_manifest(envelope, pub)['version'], '0.43.1')
            envelope['payload']['size'] += 1
            with self.assertRaises(Exception):
                verify_manifest(envelope, pub)

    def test_offline_resources_present(self):
        self.assertEqual(bundled_resource_report(), [])
