import unittest

from web import app as web_app


class TestWebUiVersioning(unittest.TestCase):
    def setUp(self):
        self.client = web_app.app.test_client()
        self.old_default = web_app.UI_DEFAULT_VERSION

    def tearDown(self):
        web_app.UI_DEFAULT_VERSION = self.old_default

    def test_index_uses_v1_when_default_is_invalid(self):
        web_app.UI_DEFAULT_VERSION = "broken"
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Nginx UI", response.data)

    def test_index_can_switch_to_v2_with_query_param_and_set_cookie(self):
        response = self.client.get("/?ui=v2")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"UI v2 preview", response.data)
        set_cookie = response.headers.get("Set-Cookie", "")
        self.assertIn("audiobook_ui_version=v2", set_cookie)


    def test_index_exposes_ui_switch_links(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"UI v1", response.data)
        self.assertIn(b"UI v2", response.data)
        self.assertIn(b"/?ui=v2", response.data)
        self.assertIn(b"setupUiSwitchLinks", response.data)

    def test_api_ui_version_returns_warning_for_unknown_version(self):
        response = self.client.get("/api/ui/version?ui=unknown")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("warning", payload)
        self.assertEqual(payload["active"], web_app.UI_DEFAULT_VERSION)
