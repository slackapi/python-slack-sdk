import unittest

from slack_sdk.oauth import RedirectUriPageRenderer


class TestInit(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_render_failure_page(self):
        renderer = RedirectUriPageRenderer(
            install_path="/slack/install",
            redirect_uri_path="/slack/oauth_redirect",
        )
        page = renderer.render_failure_page("something-wrong")
        self.assertTrue("Something Went Wrong!" in page)

    def test_render_success_page(self):
        renderer = RedirectUriPageRenderer(
            install_path="/slack/install",
            redirect_uri_path="/slack/oauth_redirect",
        )
        page = renderer.render_success_page(app_id="A111", team_id="T111")
        self.assertTrue("slack://app?team=T111&amp;id=A111" in page)

        page = renderer.render_success_page(app_id="A111", team_id=None)
        self.assertTrue("slack://open" in page)
