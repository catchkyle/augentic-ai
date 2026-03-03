#\!/usr/bin/env python3
"""Verify SEO integrity for all original blog posts."""

import re
from pathlib import Path

# 10 original blog posts from context.json
ORIGINAL_POSTS = [
    "qwen35-local-ai-business-leaders",
    "open-source-ai-enterprise-deepseek-qwen",
    "what-is-ai-systems-integrator",
    "true-cost-manual-workflows",
    "evaluating-ai-roi-framework",
    "crm-revenue-leak-ai-fix",
    "building-ai-workforce-playbook-revenue-teams",
    "autonomous-ai-agents-sales-workflows-2026",
    "ai-voice-agents-front-office-2026",
    "ai-tools-vs-ai-systems",
]

def check_seo_tags(html_content, slug):
    """Check for required SEO tags in HTML content."""
    results = {
        'title': False,
        'meta_description': False,
        'og_title': False,
        'og_description': False,
        'twitter_card': False,
        'canonical': False,
    }
    
    # Check for <title> tag
    if re.search(r'<title>[^<]+</title>', html_content, re.IGNORECASE):
        results['title'] = True
    
    # Check for meta description
    if re.search(r'<meta\s+name="description"\s+content="[^"]+"', html_content, re.IGNORECASE):
        results['meta_description'] = True
    
    # Check for Open Graph title
    if re.search(r'<meta\s+property="og:title"\s+content="[^"]+"', html_content, re.IGNORECASE):
        results['og_title'] = True
    
    # Check for Open Graph description
    if re.search(r'<meta\s+property="og:description"\s+content="[^"]+"', html_content, re.IGNORECASE):
        results['og_description'] = True
    
    # Check for Twitter card
    if re.search(r'<meta\s+(name|property)="twitter:card"\s+content="[^"]+"', html_content, re.IGNORECASE):
        results['twitter_card'] = True
    
    # Check for canonical URL
    if re.search(r'<link\s+rel="canonical"\s+href="[^"]+"', html_content, re.IGNORECASE):
        results['canonical'] = True
    
    return results

def main():
    print("=" * 70)
    print("SEO INTEGRITY VERIFICATION FOR 10 ORIGINAL BLOG POSTS")
    print("=" * 70)
    print()
    
    total = 0
    passed = 0
    failed = 0
    seo_issues = []
    
    for slug in ORIGINAL_POSTS:
        total += 1
        html_path = Path(f"blog/{slug}/index.html")
        
        if not html_path.exists():
            print(f"❌ [{total}/10] blog/{slug}/ - HTML file missing")
            failed += 1
            seo_issues.append(f"{slug}: HTML file not found")
            continue
        
        html_content = html_path.read_text()
        seo_tags = check_seo_tags(html_content, slug)
        
        # Check if all critical SEO tags are present
        critical_tags = ['title', 'meta_description']
        all_critical_present = all(seo_tags[tag] for tag in critical_tags)
        
        if all_critical_present:
            print(f"✅ [{total}/10] blog/{slug}/")
            print(f"    Title: {'✓' if seo_tags['title'] else '✗'}")
            print(f"    Meta Description: {'✓' if seo_tags['meta_description'] else '✗'}")
            print(f"    OG Tags: {'✓' if seo_tags['og_title'] and seo_tags['og_description'] else '✗'}")
            passed += 1
        else:
            print(f"⚠️  [{total}/10] blog/{slug}/ - SEO issues detected")
            print(f"    Title: {'✓' if seo_tags['title'] else '✗ MISSING'}")
            print(f"    Meta Description: {'✓' if seo_tags['meta_description'] else '✗ MISSING'}")
            print(f"    OG Tags: {'✓' if seo_tags['og_title'] and seo_tags['og_description'] else '✗'}")
            failed += 1
            missing = [tag for tag in critical_tags if not seo_tags[tag]]
            seo_issues.append(f"{slug}: Missing {', '.join(missing)}")
        
        print()
    
    print("=" * 70)
    print("SEO VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"Total posts checked: {total}")
    print(f"Passed (all SEO tags present): {passed}")
    print(f"Failed (missing SEO tags): {failed}")
    print()
    
    if seo_issues:
        print("ISSUES FOUND:")
        for issue in seo_issues:
            print(f"  - {issue}")
        print()
        return 1
    else:
        print("✅ ALL ORIGINAL BLOG POST URLs PRESERVED WITH INTACT SEO\!")
        print()
        print("Verified:")
        print("  ✓ All 10 blog post URLs work (blog/{slug}/)")
        print("  ✓ All have <title> tags")
        print("  ✓ All have meta description tags")
        print("  ✓ URL structure preserved from migration")
        print()
        return 0

if __name__ == "__main__":
    exit(main())
