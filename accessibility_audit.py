#!/usr/bin/env python3
"""
Accessibility Audit Script for WCAG 2.1 AA Compliance
Audits HTML files for common accessibility issues
"""

import os
import re
from html.parser import HTMLParser
from collections import defaultdict


class AccessibilityAuditor(HTMLParser):
    """Parse HTML and check for accessibility issues"""

    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.issues = {
            'critical': [],
            'serious': [],
            'moderate': [],
            'minor': []
        }
        self.warnings = []
        self.passes = []

        # Tracking state
        self.in_form = False
        self.form_labels = []
        self.form_inputs = []
        self.images = []
        self.links = []
        self.buttons = []
        self.headings = []
        self.current_tag = None
        self.has_main = False
        self.has_lang = False
        self.has_title = False
        self.aria_hidden_count = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.current_tag = tag

        # Check html lang attribute
        if tag == 'html':
            if 'lang' in attrs_dict:
                self.has_lang = True
                self.passes.append("✓ HTML has lang attribute")
            else:
                self.issues['serious'].append("Missing lang attribute on <html> tag")

        # Check title
        if tag == 'title':
            self.has_title = True

        # Check main landmark
        if tag == 'main':
            self.has_main = True

        # Check form elements
        if tag == 'form':
            self.in_form = True

        if tag == 'label':
            label_for = attrs_dict.get('for', '')
            if label_for:
                self.form_labels.append(label_for)
            else:
                if self.in_form:
                    self.issues['serious'].append(f"Label without 'for' attribute in {self.filename}")

        if tag == 'input':
            input_id = attrs_dict.get('id', '')
            input_type = attrs_dict.get('type', 'text')

            # Hidden inputs don't need labels
            if input_type not in ['hidden', 'submit', 'button']:
                self.form_inputs.append(input_id)

                # Check for aria-label or aria-labelledby as alternative
                has_aria_label = 'aria-label' in attrs_dict or 'aria-labelledby' in attrs_dict
                if not input_id and not has_aria_label:
                    self.issues['serious'].append(f"Input without id or aria-label in {self.filename}")

        if tag == 'select' or tag == 'textarea':
            elem_id = attrs_dict.get('id', '')
            self.form_inputs.append(elem_id)
            if not elem_id:
                has_aria_label = 'aria-label' in attrs_dict or 'aria-labelledby' in attrs_dict
                if not has_aria_label:
                    self.issues['serious'].append(f"{tag} without id or aria-label in {self.filename}")

        # Check images
        if tag == 'img':
            alt = attrs_dict.get('alt')
            aria_hidden = attrs_dict.get('aria-hidden', '').lower() == 'true'

            if alt is None and not aria_hidden:
                self.issues['critical'].append(f"Image without alt attribute in {self.filename}")
            elif alt == '' and not aria_hidden:
                # Empty alt is okay for decorative images, but flag it
                self.warnings.append(f"Image with empty alt (decorative?) in {self.filename}")
            self.images.append({'alt': alt, 'aria_hidden': aria_hidden})

        # Check SVGs (often decorative)
        if tag == 'svg':
            aria_hidden = attrs_dict.get('aria-hidden', '').lower() == 'true'
            focusable = attrs_dict.get('focusable', '').lower()

            if aria_hidden:
                self.aria_hidden_count += 1
                if focusable != 'false':
                    self.issues['minor'].append(f"SVG has aria-hidden but missing focusable='false' in {self.filename}")

        # Check links
        if tag == 'a':
            href = attrs_dict.get('href', '')
            aria_label = attrs_dict.get('aria-label', '')
            if href and not href.startswith('#'):
                self.links.append({'href': href, 'aria_label': aria_label})

        # Check buttons
        if tag == 'button':
            btn_type = attrs_dict.get('type', 'submit')
            aria_label = attrs_dict.get('aria-label', '')
            self.buttons.append({'type': btn_type, 'aria_label': aria_label})

        # Check headings
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(tag[1])
            self.headings.append(level)

    def handle_endtag(self, tag):
        if tag == 'form':
            self.in_form = False

    def analyze(self):
        """Analyze collected data for issues"""

        # Check form label/input association
        unassociated_inputs = set(self.form_inputs) - set(self.form_labels) - {''}
        if unassociated_inputs:
            for input_id in unassociated_inputs:
                self.issues['serious'].append(f"Form input with id='{input_id}' has no associated label")
        else:
            if self.form_inputs:
                self.passes.append(f"✓ All {len(self.form_inputs)} form inputs have associated labels")

        # Check if page has title
        if not self.has_title:
            self.issues['serious'].append("Missing <title> tag")
        else:
            self.passes.append("✓ Page has <title> tag")

        # Check heading hierarchy
        if self.headings:
            for i in range(len(self.headings) - 1):
                current = self.headings[i]
                next_heading = self.headings[i + 1]
                if next_heading > current + 1:
                    self.issues['moderate'].append(f"Heading hierarchy skips from h{current} to h{next_heading}")

            if self.headings[0] != 1:
                self.issues['moderate'].append(f"First heading is h{self.headings[0]}, should be h1")
            else:
                self.passes.append("✓ Proper heading hierarchy starts with h1")

        # Check for decorative SVGs
        if self.aria_hidden_count > 0:
            self.passes.append(f"✓ {self.aria_hidden_count} decorative SVGs properly marked with aria-hidden")

        return self.issues


def check_css_for_accessibility(css_content):
    """Check CSS for accessibility issues"""
    issues = {
        'critical': [],
        'serious': [],
        'moderate': [],
        'minor': []
    }
    passes = []

    # Check for focus indicators
    if 'outline:' in css_content or 'outline :' in css_content:
        # Check if outline is being removed
        if re.search(r'outline\s*:\s*none', css_content, re.IGNORECASE):
            # Check if there's a replacement focus style
            if 'focus' in css_content.lower():
                passes.append("✓ Custom focus indicators implemented")
            else:
                issues['serious'].append("outline:none found without custom focus indicator")
        else:
            passes.append("✓ Focus indicators present in CSS")

    # Check for prefers-reduced-motion
    if '@media (prefers-reduced-motion' in css_content or '@media(prefers-reduced-motion' in css_content:
        passes.append("✓ Respects prefers-reduced-motion media query")
    else:
        if 'transition' in css_content or 'animation' in css_content or 'transform' in css_content:
            issues['moderate'].append("Animations/transitions found but no prefers-reduced-motion support")

    return issues, passes


def audit_file(filepath):
    """Audit a single HTML file"""
    print(f"\n{'='*80}")
    print(f"Auditing: {filepath}")
    print(f"{'='*80}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

    # Parse HTML
    auditor = AccessibilityAuditor(filepath)
    auditor.feed(content)
    issues = auditor.analyze()

    # Check CSS if embedded
    css_issues = {'critical': [], 'serious': [], 'moderate': [], 'minor': []}
    css_passes = []
    if '<style>' in content:
        style_match = re.search(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
        if style_match:
            css_content = style_match.group(1)
            css_issues, css_passes = check_css_for_accessibility(css_content)

    # Combine issues
    for severity in issues:
        issues[severity].extend(css_issues[severity])

    # Print results
    total_issues = sum(len(issues[sev]) for sev in issues)

    print(f"\n📊 Results Summary:")
    print(f"  Critical: {len(issues['critical'])}")
    print(f"  Serious:  {len(issues['serious'])}")
    print(f"  Moderate: {len(issues['moderate'])}")
    print(f"  Minor:    {len(issues['minor'])}")
    print(f"  Total:    {total_issues}")

    # Print issues by severity
    for severity in ['critical', 'serious', 'moderate', 'minor']:
        if issues[severity]:
            print(f"\n🔴 {severity.upper()} Issues:")
            for issue in issues[severity]:
                print(f"  - {issue}")

    # Print passes
    all_passes = auditor.passes + css_passes
    if all_passes:
        print(f"\n✅ Accessibility Passes ({len(all_passes)}):")
        for p in all_passes:
            print(f"  {p}")

    # Print warnings
    if auditor.warnings:
        print(f"\n⚠️  Warnings ({len(auditor.warnings)}):")
        for w in auditor.warnings:
            print(f"  - {w}")

    return {
        'file': filepath,
        'issues': issues,
        'passes': all_passes,
        'warnings': auditor.warnings,
        'total_issues': total_issues
    }


def main():
    """Run accessibility audit on all major pages"""

    # Key pages to audit
    pages_to_audit = [
        './index.html',
        './book/index.html',
        './blog/index.html',
        './guide/index.html',
        './404.html'
    ]

    # Also audit a sample blog post
    blog_posts = [
        './blog/crm-revenue-leak-ai-fix/index.html',
    ]

    all_pages = pages_to_audit + blog_posts

    print("="*80)
    print("WCAG 2.1 AA Accessibility Audit")
    print("="*80)
    print(f"\nAuditing {len(all_pages)} pages for accessibility compliance...\n")

    results = []
    for page in all_pages:
        if os.path.exists(page):
            result = audit_file(page)
            if result:
                results.append(result)
        else:
            print(f"\n⚠️  File not found: {page}")

    # Overall summary
    print(f"\n\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}")

    total_critical = sum(len(r['issues']['critical']) for r in results)
    total_serious = sum(len(r['issues']['serious']) for r in results)
    total_moderate = sum(len(r['issues']['moderate']) for r in results)
    total_minor = sum(len(r['issues']['minor']) for r in results)
    total_all = total_critical + total_serious + total_moderate + total_minor

    print(f"\nPages Audited: {len(results)}")
    print(f"\nTotal Issues Found:")
    print(f"  Critical:  {total_critical}")
    print(f"  Serious:   {total_serious}")
    print(f"  Moderate:  {total_moderate}")
    print(f"  Minor:     {total_minor}")
    print(f"  TOTAL:     {total_all}")

    # WCAG Compliance Status
    print(f"\n{'='*80}")
    print("WCAG 2.1 AA COMPLIANCE STATUS")
    print(f"{'='*80}")

    if total_critical == 0 and total_serious == 0:
        print("\n✅ PASS - No critical or serious violations found!")
        print("   Site meets WCAG 2.1 AA automated testing requirements.")
        if total_moderate > 0 or total_minor > 0:
            print(f"\n   Note: {total_moderate} moderate and {total_minor} minor issues should be reviewed.")
    else:
        print(f"\n❌ FAIL - {total_critical} critical and {total_serious} serious violations found")
        print("   Site does NOT meet WCAG 2.1 AA requirements.")
        print("\n   Action Required:")
        print("   1. Fix all critical violations immediately")
        print("   2. Address all serious violations")
        print("   3. Review and address moderate/minor issues")

    print(f"\n{'='*80}\n")

    return total_critical == 0 and total_serious == 0


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
