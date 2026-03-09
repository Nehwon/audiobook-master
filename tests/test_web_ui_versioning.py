import unittest

from web import app as web_app


class TestWebUiVersioning(unittest.TestCase):
    def setUp(self):
        self.client = web_app.app.test_client()
        self.old_default = web_app.UI_DEFAULT_VERSION

    def tearDown(self):
        web_app.UI_DEFAULT_VERSION = self.old_default

    def test_index_uses_v2_when_default_is_invalid(self):
        web_app.UI_DEFAULT_VERSION = "broken"
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Dashboard V2", response.data)

    def test_index_can_switch_to_v2_with_query_param_and_set_cookie(self):
        response = self.client.get("/?ui=v2")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Dashboard V2", response.data)
        set_cookie = response.headers.get("Set-Cookie", "")
        self.assertIn("audiobook_ui_version=v2", set_cookie)


    def test_index_hides_obsolete_ui_switch_links(self):
        response = self.client.get("/?ui=v2")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"UI v1", response.data)
        self.assertNotIn(b"UI v2", response.data)
        self.assertNotIn(b"setupUiSwitchLinks", response.data)

    def test_api_ui_version_returns_warning_for_unknown_version(self):
        response = self.client.get("/api/ui/version?ui=unknown")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("warning", payload)
        self.assertEqual(payload["active"], "v2")


    def test_v2_displays_archives_pending_kpi(self):
        response = self.client.get("/?ui=v2")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Archives en attente", response.data)

    def test_logo_asset_route_is_available(self):
        response = self.client.get("/assets/audiobook-manager.jpg")
        self.assertEqual(response.status_code, 200)
        self.assertIn("image", response.content_type)
