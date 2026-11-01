import base64
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from studio.update_manager import parse_version, verify_manifest, check_update, download_verified_installer

class FakeResponse(io.BytesIO):
    pass

class UpdaterTests(unittest.TestCase):
    def setUp(self):
        self.private = Ed25519PrivateKey.generate()
        self.public = base64.b64encode(self.private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)).decode()
        self.data = b'installer bytes'
        self.payload = {'version':'0.43.0','installer_url':'https://github.com/example/repo/releases/download/v0.43.0/Setup.exe','sha256':hashlib.sha256(self.data).hexdigest(),'size':len(self.data)}

    def signed(self, payload=None):
        payload = payload or self.payload
        canonical=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
        return {'payload':payload,'signature':base64.b64encode(self.private.sign(canonical)).decode()}

    def test_versions_are_numeric(self):
        self.assertGreater(parse_version('v0.43.0'),parse_version('0.9.0'))
        with self.assertRaises(ValueError):parse_version('0.42.0-beta')

    def test_valid_signed_update(self):
        self.assertEqual(verify_manifest(self.signed(),self.public),self.payload)

    def test_modified_payload_rejected(self):
        envelope=self.signed();envelope['payload']['size']+=1
        with self.assertRaises(Exception):verify_manifest(envelope,self.public)

    def test_unsigned_feed_rejected(self):
        with self.assertRaises(Exception):verify_manifest({'payload':self.payload},self.public)

    def test_insecure_download_url_rejected(self):
        payload=dict(self.payload,installer_url='http://example.com/file.exe')
        with self.assertRaises(ValueError):verify_manifest(self.signed(payload),self.public)

    def test_newer_only(self):
        raw=json.dumps(self.signed()).encode()
        opener=lambda request,timeout: FakeResponse(raw)
        self.assertIsNone(check_update('0.43.0','https://example.org/manifest.json',self.public,opener))
        self.assertEqual(check_update('0.42.0','https://example.org/manifest.json',self.public,opener)['version'],'0.43.0')

    def test_download_verified(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/'Setup.exe'
            download_verified_installer(self.payload,target,lambda request,timeout:FakeResponse(self.data))
            self.assertEqual(target.read_bytes(),self.data)

    def test_bad_download_keeps_existing_file(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/'Setup.exe';target.write_bytes(b'old valid installer')
            with self.assertRaises(ValueError):download_verified_installer(self.payload,target,lambda request,timeout:FakeResponse(b'bad'))
            self.assertEqual(target.read_bytes(),b'old valid installer')
            self.assertFalse((Path(td)/'Setup.exe.partial').exists())

if __name__=='__main__':unittest.main()
