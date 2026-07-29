import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class HomepageRedesignTests(unittest.TestCase):
    def test_homepage_uses_reference_led_section_sequence(self):
        page = (ROOT / "index.html").read_text()

        expected_ids = [
            "hero",
            "revenue-engine",
            "systems",
            "outcomes",
            "offerings",
            "process",
            "final-cta",
        ]
        positions = [page.index(f'id="{section_id}"') for section_id in expected_ids]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("Your Workforce. Automated.", page)
        self.assertIn("Your Revenue. <span>Accelerated.</span>", page)
        self.assertIn("Your Revenue Engine, Re-Architected.", page)
        self.assertIn("Built Around Business Outcomes.", page)
        self.assertIn("Choose Your Path to AI Speed.", page)

    def test_homepage_contains_original_system_visuals(self):
        page = (ROOT / "index.html").read_text()

        self.assertIn('class="hero-system"', page)
        self.assertIn('aria-label="Augentic OS system architecture"', page)
        for label in ["AUGENTIC OS", "Voice", "CRM", "Email", "Calendar", "Reporting", "Human Oversight"]:
            self.assertIn(label, page)
        self.assertGreaterEqual(page.count("<svg"), 8)

    def test_homepage_dashboard_motion_is_scroll_triggered_and_accessible(self):
        page = (ROOT / "index.html").read_text()

        self.assertIn('data-motion="engine"', page)
        self.assertIn('data-motion="dashboard"', page)
        self.assertGreaterEqual(page.count('data-reveal'), 12)
        self.assertIn("new IntersectionObserver", page)
        self.assertIn("classList.add('motion-ready')", page)
        self.assertIn("classList.add('is-visible')", page)
        self.assertIn("classList.add('is-active')", page)
        self.assertIn("@keyframes dashTrace", page)
        self.assertIn("@keyframes statusPulse", page)
        self.assertIn(".motion-ready [data-reveal]", page)
        self.assertIn(".motion-ready .outcome-shell:not(.is-active) .bar i{width:0!important}", page)
        self.assertIn("prefers-reduced-motion: reduce", page)
        self.assertIn(".motion-ready [data-reveal]{opacity:1;transform:none}", page)

    def test_homepage_preserves_conversion_and_accessibility_basics(self):
        page = (ROOT / "index.html").read_text()

        self.assertEqual(len(re.findall(r"<h1(?:\s|>)", page)), 1)
        self.assertIn('<link rel="canonical" href="https://augenticai.com/">', page)
        self.assertIn('href="/ai-workflow-roi-blueprint/" class="btn-primary">Get My AI Workflow ROI Blueprint</a>', page)
        self.assertIn('aria-label="Open navigation"', page)
        self.assertIn(".hero-visual{width:100%;max-width:650px", page)
        self.assertIn('@media (prefers-reduced-motion: reduce)', page)
        headers = (ROOT / "_headers").read_text()
        self.assertIn("script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com", headers)
        self.assertIn("connect-src 'self' https://cloudflareinsights.com https://fonts.googleapis.com", headers)
        self.assertNotIn("script-src *", headers)
        self.assertNotIn("—", page)


if __name__ == "__main__":
    unittest.main()
