# Cloudflare Pages Deployment Configuration

This document describes how to configure Cloudflare Pages to automatically deploy the Augentic AI static site when content changes are pushed to GitHub.

## Overview

The deployment pipeline works as follows:

1. Content creators edit content via Decap CMS (`/admin/`)
2. CMS commits changes to `content/` directory in GitHub
3. GitHub Actions workflow (`.github/workflows/deploy.yml`) detects changes
4. Workflow runs `_build_site.py` to generate HTML from markdown
5. Generated HTML is committed back to the repository
6. **Cloudflare Pages webhook detects the commit and deploys the site**

## Cloudflare Pages Configuration

### 1. Connect GitHub Repository

In the Cloudflare Pages dashboard:

1. Navigate to **Workers & Pages** → **Create Application** → **Pages**
2. Select **Connect to Git**
3. Choose the repository: `cora-catchadvisors/augentic-ai`
4. Authorize Cloudflare to access the repository

### 2. Build Settings

Configure the following build settings:

- **Production Branch**: `main`
- **Build Command**: (leave empty - site is pre-built by GitHub Actions)
- **Build Output Directory**: `/` (root directory)
- **Root Directory**: `/` (root directory)

**Important**: Since GitHub Actions already runs `_build_site.py` and commits the generated HTML files, Cloudflare Pages only needs to serve the static files. No build command is required.

### 3. Build Watch Paths (Optional)

To optimize deployments, configure Cloudflare Pages to only trigger on relevant file changes:

**Include Patterns:**
- `*.html`
- `blog/**/*.html`
- `case-studies/**/*.html`
- `*.css`
- `*.js`
- `*.svg`
- `*.xml`

**Exclude Patterns:**
- `content/**`
- `admin/**`
- `.github/**`
- `_build_site.py`
- `requirements.txt`
- `*.md`
- `*.py`

These exclusions prevent unnecessary deployments when only source files change (GitHub Actions will rebuild and commit HTML changes, which will then trigger deployment).

### 4. Environment Variables

No environment variables are required for the static site deployment.

### 5. Deploy Hooks (Webhook)

Cloudflare Pages automatically creates a webhook in your GitHub repository when you connect it. This webhook triggers deployments on every push to the production branch (`main`).

**To verify the webhook is configured:**

1. Go to GitHub repository → **Settings** → **Webhooks**
2. Look for a webhook with URL pattern: `https://api.cloudflare.com/client/v4/pages/webhooks/deploy_hooks/...`
3. Ensure it's configured to trigger on **push** events
4. Verify **Active** checkbox is enabled

### 6. Preview Deployments

Cloudflare Pages automatically creates preview deployments for:
- Pull requests (useful for Decap CMS editorial workflow)
- Non-production branches

**Preview URLs follow the pattern:**
- PR previews: `<commit-hash>.<project-name>.pages.dev`
- Branch previews: `<branch-name>.<project-name>.pages.dev`

This enables content creators to preview their work before merging to production.

## Deployment Flow

### Content Update Flow

```
Content Creator (CMS)
  ↓
Edit content in /admin/
  ↓
Save/Publish (creates Git commit)
  ↓
GitHub receives commit to content/**
  ↓
GitHub Actions workflow triggers
  ↓
Build script runs: python _build_site.py
  ↓
Generated HTML committed to repository
  ↓
Cloudflare Pages webhook receives push notification
  ↓
Cloudflare Pages deploys updated site
  ↓
Site live at augentic.ai
```

### Manual Deployment

You can also trigger manual deployments:

1. In Cloudflare Pages dashboard, go to your project
2. Click **Create Deployment**
3. Select branch `main`
4. Click **Save and Deploy**

## Verification

To verify the webhook is working correctly:

1. Make a content change via CMS or directly edit a markdown file in `content/blog/`
2. Commit and push to `main` branch
3. Check GitHub Actions → verify workflow runs successfully
4. Check Cloudflare Pages dashboard → verify new deployment starts
5. Wait for deployment to complete
6. Visit `https://augentic.ai` → verify changes are live

## Troubleshooting

### Deployment Not Triggering

**Check:**
- GitHub webhook exists and is active (Settings → Webhooks)
- Cloudflare Pages project is connected to correct repository
- Production branch is set to `main`
- Changes were pushed to `main` branch (not a different branch)

### Build Failures

**Note:** Cloudflare Pages should not fail to build since there's no build command. If deployments fail:
- Check that all HTML files are valid
- Verify no symlinks or invalid file paths exist
- Check Cloudflare Pages logs for specific error messages

### GitHub Actions Fails

If GitHub Actions workflow fails:
- Check Python dependencies in `requirements.txt`
- Verify `_build_site.py` runs successfully locally
- Check GitHub Actions logs for error details
- Ensure `GITHUB_TOKEN` has write permissions

## Security Considerations

### CMS Authentication

Decap CMS uses GitHub OAuth for authentication. Configure in Cloudflare Pages:

1. Set up GitHub OAuth App (if not already done)
2. Configure OAuth callback URL: `https://augentic.ai/admin/`
3. Add OAuth client ID to `admin/config.yml` (if using external OAuth provider)

**Note:** For GitHub backend with `publish_mode: editorial_workflow`, Decap CMS creates pull requests instead of direct commits, providing an extra review layer.

### Branch Protection

Consider enabling branch protection on `main`:
- Require pull request reviews (optional for CMS workflow)
- Require status checks to pass (GitHub Actions workflow)
- Include administrators (prevents accidental force pushes)

## Monitoring

### Deployment Notifications

Configure Cloudflare Pages deployment notifications:
1. Go to project **Settings** → **Notifications**
2. Add email addresses or Slack webhook
3. Choose notification triggers:
   - Deployment started
   - Deployment succeeded
   - Deployment failed

### Analytics

Cloudflare provides analytics for:
- Page views
- Unique visitors
- Bandwidth usage
- Geographic distribution

Access via: Cloudflare Pages dashboard → **Analytics** tab

## References

- [Cloudflare Pages Documentation](https://developers.cloudflare.com/pages/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Decap CMS Documentation](https://decapcms.org/docs/)

---

**Last Updated**: 2026-03-03
**Status**: Configuration required - follow steps above to enable automated deployments
