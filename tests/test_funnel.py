import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class FunnelStaticTests(unittest.TestCase):
    def test_landing_page_contains_offer_and_qualification_form(self):
        page = (ROOT / "ai-workflow-roi-blueprint" / "index.html").read_text()

        self.assertIn("AI Workflow ROI Blueprint", page)
        self.assertIn('action="/api/ai-workflow-blueprint"', page)
        self.assertIn('name="email"', page)
        self.assertIn('name="company"', page)
        self.assertIn('name="role"', page)
        self.assertIn('name="companySize"', page)
        self.assertIn('name="workflow"', page)
        self.assertIn('name="monthlyVolume"', page)
        self.assertIn('name="hoursPerMonth"', page)
        self.assertIn('name="systems"', page)
        self.assertIn('name="desiredOutcome"', page)
        self.assertIn('name="budgetReadiness"', page)
        self.assertIn('name="timeline"', page)
        self.assertIn('name="website"', page)
        self.assertIn("Build My AI Workflow ROI Blueprint", page)

    def test_funnel_has_search_metadata_and_safe_thank_you_page(self):
        page = (ROOT / "ai-workflow-roi-blueprint" / "index.html").read_text()
        thank_you = (ROOT / "ai-workflow-roi-blueprint" / "thank-you" / "index.html").read_text()
        sitemap = (ROOT / "sitemap.xml").read_text()

        self.assertIn('<link rel="canonical" href="https://augenticai.com/ai-workflow-roi-blueprint/">', page)
        self.assertIn('<meta name="description"', page)
        self.assertIn('href="/privacy/"', page)
        self.assertNotIn("—", page)
        self.assertIn('<meta name="robots" content="noindex, nofollow">', thank_you)
        self.assertIn("Your request was accepted", thank_you)
        self.assertNotIn("—", thank_you)
        self.assertIn("https://augenticai.com/ai-workflow-roi-blueprint/", sitemap)
        self.assertNotIn("https://augenticai.com/ai-workflow-roi-blueprint/thank-you/", sitemap)

    def test_form_uses_verified_server_capture_and_preserves_attribution(self):
        page = (ROOT / "ai-workflow-roi-blueprint" / "index.html").read_text()

        self.assertNotIn("mailto:", page)
        self.assertIn("fetch(form.action", page)
        self.assertIn("if (!response.ok)", page)
        self.assertIn("/ai-workflow-roi-blueprint/thank-you/", page)
        self.assertIn('id="form-error"', page)
        self.assertIn('name="sourcePage"', page)
        self.assertIn('name="referrer"', page)
        self.assertIn('name="utmSource"', page)
        self.assertIn('name="utmMedium"', page)
        self.assertIn('name="utmCampaign"', page)
        self.assertIn("funnel_form_start", page)
        self.assertIn("generate_lead", page)

    def test_homepage_routes_primary_action_to_blueprint(self):
        homepage = (ROOT / "index.html").read_text()
        self.assertIn('href="/ai-workflow-roi-blueprint/" class="btn-primary">Get My AI Workflow ROI Blueprint</a>', homepage)


if __name__ == "__main__":
    unittest.main()
