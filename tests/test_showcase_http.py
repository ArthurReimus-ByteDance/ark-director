import http.client
import json
import secrets
import threading
import unittest
from http.server import HTTPServer

import test_showcase_selection as fixtures

showcase = fixtures.showcase


class ShowcaseHTTPTests(unittest.TestCase):
    files = fixtures.ShowcaseRegressionTests.files
    def setUp(self):
        fixtures.ShowcaseRegressionTests.setUp(self)
        handler = type('TestHandler', (showcase.ShowcaseHandler,), {
            'proj': self.root,
            'service': self.service,
            'session_token': secrets.token_urlsafe(32),
        })
        self.server = HTTPServer(('127.0.0.1', 0), handler)
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()
        self.addCleanup(self.close_server)
        self.token = handler.session_token
        self.origin = f'http://127.0.0.1:{self.server.server_port}'

    def close_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join(2)

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        self.addCleanup(connection.close)
        connection.request(method, path, body, headers or {})
        response = connection.getresponse()
        return response.status, dict(response.headers), response.read()

    def test_save_requires_origin_and_session_then_reloads(self):
        _, _, body = self.request('GET', '/api/session')
        snapshot = json.loads(body)
        payload = json.dumps({'selections': {'hero': 'new.png'}, 'expected_revision': snapshot['revision']})
        headers = {'Content-Type': 'application/json', 'Origin': self.origin, 'X-Showcase-Token': self.token}
        before = self.files()
        for overrides in ({'Origin': 'https://example.com'}, {'X-Showcase-Token': 'wrong'}):
            status, _, _ = self.request('POST', '/api/select', payload, {**headers, **overrides})
            self.assertEqual(status, 403)
            self.assertEqual(before, self.files())
        status, _, body = self.request('POST', '/api/select', payload, headers)
        self.assertEqual(status, 200, body)
        _, _, body = self.request('GET', '/api/selection')
        self.assertEqual(json.loads(body)['selections'], {'hero': 'new.png'})
        status, _, _ = self.request('POST', '/api/select', payload, headers)
        self.assertEqual(status, 409)

    def test_oversized_request_and_wrong_host_rejected(self):
        headers = {'Content-Type': 'application/json', 'Origin': self.origin, 'X-Showcase-Token': self.token}
        status, _, _ = self.request('POST', '/api/select', 'x' * 65537, headers)
        self.assertEqual(status, 413)
        status, _, _ = self.request('GET', '/api/session', headers={'Host': 'untrusted.test'})
        self.assertEqual(status, 403)

    def test_streamed_byte_ranges_and_path_containment(self):
        media = bytes(range(256)) * 1024
        (self.root / 'video.mp4').write_bytes(media)
        status, headers, body = self.request('GET', '/video.mp4', headers={'Range': 'bytes=100-199'})
        self.assertEqual(status, 206)
        self.assertEqual(body, media[100:200])
        self.assertEqual(headers['Content-Range'], f'bytes 100-199/{len(media)}')
        status, _, body = self.request('GET', '/video.mp4', headers={'Range': 'bytes=-17'})
        self.assertEqual(status, 206)
        self.assertEqual(body, media[-17:])
        status, _, _ = self.request('GET', '/video.mp4', headers={'Range': 'bytes=999999-'})
        self.assertEqual(status, 416)
        for path in ('/../outside.md', '/%2e%2e/outside.md', '/.selection.lock'):
            status, _, _ = self.request('GET', path)
            self.assertEqual(status, 404)


if __name__ == '__main__':
    unittest.main()
