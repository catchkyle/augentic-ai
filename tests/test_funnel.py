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
        self.assertIn("Score My Workflow", page)

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

    def test_funnel_delivers_value_before_contact_capture(self):
        page = (ROOT / "ai-workflow-roi-blueprint" / "index.html").read_text()

        self.assertIn("Score My Workflow", page)
        self.assertIn('src="/assets/blueprint-diagnostic.js"', page)
        self.assertIn('id="diagnostic-step"', page)
        self.assertIn('id="result-step"', page)
        self.assertIn('id="contact-step"', page)
        self.assertIn('id="fit-score"', page)
        self.assertIn('id="capacity-value"', page)
        self.assertIn("70% of repeatable hours", page)
        self.assertIn('href="/ai-workflow-roi-blueprint/sample/"', page)
        self.assertIn("Reviewed by Kyle Burt", page)
        self.assertIn("/api/funnel-event", page)
        self.assertIn("sessionStorage.setItem('augentic_blueprint_result'", page)
        self.assertNotIn("Build My AI Workflow ROI Blueprint", page)

    def test_sample_and_thank_you_keep_hot_leads_in_the_funnel(self):
        sample = (ROOT / "ai-workflow-roi-blueprint" / "sample" / "index.html").read_text()
        thank_you = (ROOT / "ai-workflow-roi-blueprint" / "thank-you" / "index.html").read_text()

        self.assertIn('<meta name="robots" content="noindex, follow">', sample)
        self.assertIn("Illustrative, not a customer result", sample)
        self.assertIn("Decision recommendation", sample)
        self.assertIn('href="/ai-workflow-roi-blueprint/#diagnostic"', sample)
        self.assertIn("augentic_blueprint_result", thank_you)
        self.assertIn("Request Priority Strategy Review", thank_you)
        self.assertIn("/api/blueprint-priority-review", thank_you)
        self.assertIn("/api/funnel-event", thank_you)
        self.assertIn("within one business day", thank_you)

    def test_funnel_light_sections_keep_accessible_contrast_and_landmarks(self):
        page = (ROOT / "ai-workflow-roi-blueprint" / "index.html").read_text()
        self.assertIn(".method-panel>.eyebrow,.trust-head>.eyebrow{color:#745719}", page)
        self.assertIn(".method-list b{font-family:var(--mono);font-size:.56rem;color:#745719}", page)
        self.assertIn(".reviewer span{font-size:.61rem;color:#5e625b}", page)
        self.assertIn(".field small{display:block;font-size:.61rem;color:#666a62", page)
        self.assertIn(".result-metric span{display:block;font-family:var(--mono);font-size:.48rem;color:#696d65", page)
        self.assertIn('<div class="method-panel">', page)
        self.assertNotIn('<aside class="method-panel">', page)

    def test_homepage_routes_primary_action_to_blueprint(self):
        homepage = (ROOT / "index.html").read_text()
        self.assertIn('href="/ai-workflow-roi-blueprint/" class="btn-primary">Get My AI Workflow ROI Blueprint</a>', homepage)


if __name__ == "__main__":
    unittest.main()
