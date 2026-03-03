#!/usr/bin/env python3
"""Migration script to convert POSTS_FALLBACK to markdown files with frontmatter."""

import os
import sys
import argparse
import re
from html.parser import HTMLParser


class HTMLToMarkdownConverter(HTMLParser):
    """Convert HTML to Markdown."""

    def __init__(self):
        super().__init__()
        self.markdown = []
        self.current_tag = None
        self.list_level = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.current_tag = 'p'
        elif tag == 'h2':
            self.current_tag = 'h2'
        elif tag == 'h3':
            self.current_tag = 'h3'
        elif tag == 'strong':
            self.markdown.append('**')
        elif tag == 'em':
            self.markdown.append('*')
        elif tag == 'div':
            # Handle div tags (like x-credit)
            self.current_tag = 'div'

    def handle_endtag(self, tag):
        if tag == 'p':
            self.markdown.append('\n\n')
            self.current_tag = None
        elif tag == 'h2':
            self.markdown.append('\n\n')
            self.current_tag = None
        elif tag == 'h3':
            self.markdown.append('\n\n')
            self.current_tag = None
        elif tag == 'strong':
            self.markdown.append('**')
        elif tag == 'em':
            self.markdown.append('*')
        elif tag == 'div':
            self.markdown.append('\n\n')
            self.current_tag = None

    def handle_data(self, data):
        data = data.strip()
        if data:
            if self.current_tag == 'h2':
                self.markdown.append(f'## {data}')
            elif self.current_tag == 'h3':
                self.markdown.append(f'### {data}')
            else:
                self.markdown.append(data)

    def get_markdown(self):
        result = ''.join(self.markdown)
        # Clean up multiple newlines
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result.strip()


def html_to_markdown(html_content):
    """Convert HTML content to Markdown."""
    converter = HTMLToMarkdownConverter()
    converter.feed(html_content)
    return converter.get_markdown()


def load_posts_fallback():
    """Load POSTS_FALLBACK from _build_site.py by evaluating it."""
    try:
        with open('_build_site.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Find the POSTS_FALLBACK section
        # It starts with "POSTS_FALLBACK = [" and ends before the next top-level assignment
        start_marker = 'POSTS_FALLBACK = ['
        start_idx = content.find(start_marker)

        if start_idx == -1:
            raise ValueError("POSTS_FALLBACK not found in _build_site.py")

        # Find the matching closing bracket
        # We need to count brackets to find the correct end
        bracket_count = 0
        i = start_idx + len(start_marker) - 1  # Start at the opening bracket
        in_string = False
        string_char = None

        while i < len(content):
            char = content[i]

            # Handle string delimiters
            if char in ['"', "'"]:
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char and content[i-1] != '\\':
                    in_string = False
                    string_char = None

            # Count brackets only when not in a string
            if not in_string:
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        # Found the closing bracket
                        end_idx = i + 1
                        break

            i += 1
        else:
            raise ValueError("Could not find closing bracket for POSTS_FALLBACK")

        # Extract the POSTS_FALLBACK definition
        posts_code = content[start_idx:end_idx]

        # Evaluate the code to get the list
        # Create a safe namespace
        namespace = {}
        exec(posts_code, namespace)
        return namespace['POSTS_FALLBACK']

    except Exception as e:
        print(f"Error loading POSTS_FALLBACK: {e}")
        sys.exit(1)


def convert_post_to_markdown(post):
    """Convert a post dict to markdown content with frontmatter."""
    # Convert HTML body to markdown
    body_markdown = html_to_markdown(post['body'])

    # Build frontmatter
    frontmatter = f"""---
slug: {post['slug']}
title: "{post['title']}"
date: {post['date']}
category: {post['category']}
description: "{post['description']}"
reading_time: {post['reading_time']}
featured: {str(post['featured']).lower()}
"""

    # Add x_credit if present
    if post.get('x_credit'):
        # Escape quotes in x_credit
        x_credit = post['x_credit'].replace('"', '\\"')
        frontmatter += f'x_credit: "{x_credit}"\n'

    frontmatter += "---\n\n"

    return frontmatter + body_markdown


def migrate_posts(dry_run=False):
    """Migrate POSTS_FALLBACK to markdown files."""
    print("Loading POSTS_FALLBACK from _build_site.py...")
    posts = load_posts_fallback()

    print(f"Found {len(posts)} posts to migrate")

    # Ensure content/blog directory exists
    content_dir = "content/blog"
    if not dry_run:
        os.makedirs(content_dir, exist_ok=True)

    # Migrate each post
    for post in posts:
        slug = post['slug']
        filename = f"{slug}.md"
        filepath = os.path.join(content_dir, filename)

        # Convert post to markdown
        markdown_content = convert_post_to_markdown(post)

        if dry_run:
            print(f"[DRY RUN] Would create: {filepath}")
            print(f"  Title: {post['title']}")
            print(f"  Category: {post['category']}")
            print(f"  Featured: {post['featured']}")
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"Created: {filepath}")

    if dry_run:
        print("\nDry run complete. No files were created.")
    else:
        print(f"\nMigration complete. Created {len(posts)} markdown files in {content_dir}/")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate POSTS_FALLBACK to markdown files with frontmatter"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without actually creating files'
    )

    args = parser.parse_args()

    try:
        migrate_posts(dry_run=args.dry_run)
        print("OK")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
