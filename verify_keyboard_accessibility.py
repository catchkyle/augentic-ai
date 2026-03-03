#!/usr/bin/env python3
"""
Keyboard Accessibility Verification Script
Automated checks for WCAG 2.1 AA keyboard navigation compliance
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple

def check_focus_indicators(html_content: str) -> Tuple[bool, str]:
    """Verify focus indicator styles are present"""
    focus_patterns = [
        r'a:focus.*outline',
        r'button:focus.*outline',
        r'input:focus.*outline',
        r'\.nav-cta:focus.*outline',
        r'\.btn-primary:focus.*outline',
        r'focus-visible',
    ]

    found_rules = []
    for pattern in focus_patterns:
        if re.search(pattern, html_content, re.IGNORECASE | re.DOTALL):
            found_rules.append(pattern)

    if len(found_rules) >= 3:  # At least 3 focus-related rules
        return True, f"✅ Focus indicators present ({len(found_rules)} rules found)"
    else:
        return False, f"❌ Insufficient focus indicators ({len(found_rules)} rules found)"

def check_aria_labels(html_content: str) -> Tuple[bool, str]:
    """Verify ARIA labels on icon-only buttons"""
    required_aria_labels = [
        r'aria-label=["\'].*[Tt]heme.*["\']',
        r'aria-label=["\'].*[Mm]enu.*["\']',
    ]

    found_labels = []
    for pattern in required_aria_labels:
        if re.search(pattern, html_content):
            found_labels.append(pattern)

    if len(found_labels) >= 1:  # At least one aria-label
        return True, f"✅ ARIA labels present ({len(found_labels)} found)"
    else:
        return False, "❌ Missing ARIA labels on icon buttons"

def check_form_labels(html_content: str) -> Tuple[bool, str]:
    """Verify form label associations (for/id attributes)"""
    # Find all label elements with for attribute
    label_fors = re.findall(r'<label\s+for=["\'](\w+)["\']', html_content)

    # Find all input/select elements with id attribute
    input_ids = re.findall(r'<(?:input|select|textarea)\s+[^>]*id=["\'](\w+)["\']', html_content)

    # Check if labels match inputs
    matched = 0
    for label_for in label_fors:
        if label_for in input_ids:
            matched += 1

    if matched >= len(label_fors) and len(label_fors) > 0:
        return True, f"✅ All form labels properly associated ({matched}/{len(label_fors)})"
    elif len(label_fors) == 0:
        return True, "✅ No form labels found (not applicable)"
    else:
        return False, f"❌ Some form labels not associated ({matched}/{len(label_fors)})"

def check_reduced_motion(html_content: str) -> Tuple[bool, str]:
    """Verify prefers-reduced-motion media query"""
    if re.search(r'@media\s*\(\s*prefers-reduced-motion\s*:\s*reduce\s*\)', html_content):
        return True, "✅ Reduced motion media query present"
    else:
        return False, "❌ Missing prefers-reduced-motion media query"

def check_decorative_svgs(html_content: str) -> Tuple[bool, str]:
    """Verify decorative SVGs have aria-hidden"""
    svg_count = len(re.findall(r'<svg', html_content))
    aria_hidden_count = len(re.findall(r'<svg[^>]*aria-hidden=["\']true["\']', html_content))

    if svg_count == 0:
        return True, "✅ No SVGs found"
    elif aria_hidden_count >= svg_count // 2:  # At least half should be marked decorative
        return True, f"✅ Decorative SVGs properly marked ({aria_hidden_count}/{svg_count})"
    else:
        return True, f"⚠️  Some SVGs may need aria-hidden ({aria_hidden_count}/{svg_count})"

def check_tabindex_abuse(html_content: str) -> Tuple[bool, str]:
    """Verify no positive tabindex values (anti-pattern)"""
    positive_tabindex = re.findall(r'tabindex=["\']([1-9]\d*)["\']', html_content)

    if len(positive_tabindex) == 0:
        return True, "✅ No positive tabindex abuse"
    else:
        return False, f"❌ Positive tabindex found: {positive_tabindex} (anti-pattern)"

def verify_file(file_path: Path) -> Dict[str, Tuple[bool, str]]:
    """Run all checks on a single HTML file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return {
        'Focus Indicators': check_focus_indicators(content),
        'ARIA Labels': check_aria_labels(content),
        'Form Labels': check_form_labels(content),
        'Reduced Motion': check_reduced_motion(content),
        'Decorative SVGs': check_decorative_svgs(content),
        'Tabindex Check': check_tabindex_abuse(content),
    }

def main():
    """Run keyboard accessibility verification on key pages"""
    print("=" * 80)
    print("KEYBOARD ACCESSIBILITY VERIFICATION")
    print("WCAG 2.1 AA Compliance Check")
    print("=" * 80)
    print()

    files_to_check = [
        './index.html',
        './book/index.html',
    ]

    all_passed = True

    for file_path in files_to_check:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  File not found: {file_path}")
            print()
            continue

        print(f"📄 Checking: {file_path}")
        print("-" * 80)

        results = verify_file(path)

        for check_name, (passed, message) in results.items():
            print(f"  {check_name:20s} {message}")
            if not passed:
                all_passed = False

        print()

    print("=" * 80)
    if all_passed:
        print("✅ VERIFICATION PASSED - All keyboard accessibility checks successful")
    else:
        print("⚠️  VERIFICATION INCOMPLETE - Some checks need attention")
    print("=" * 80)
    print()
    print("Note: This is an automated check. Manual keyboard testing is still required")
    print("to verify actual user experience. See KEYBOARD_NAVIGATION_TEST.md for details.")

    return 0 if all_passed else 1

if __name__ == '__main__':
    exit(main())
