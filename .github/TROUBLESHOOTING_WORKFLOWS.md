# Troubleshooting GitHub Actions Workflows

## Common Error: Exit Code 128

This error typically indicates a Git authentication or permission issue. Here's how to fix it:

### 1. Check Required Secrets

Ensure these secrets are set in your repository settings (Settings → Secrets and variables → Actions):

- `CLAUDE_CODE_OAUTH_TOKEN` - Required for Claude Code Action
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions (no setup needed)

### 2. Permission Issues

The workflows need proper permissions. We've updated the permissions to:
- `contents: read` - Read repository contents
- `pull-requests: write` - Comment on PRs
- `issues: write` - Interact with issues
- `id-token: write` - For OIDC authentication

### 3. Checkout Configuration

Changed `fetch-depth` from 1 to 0 to ensure full Git history is available, which some actions require.

### 4. Token Configuration

Added explicit `token: ${{ secrets.GITHUB_TOKEN }}` to the checkout action for better authentication.

## Setting Up CLAUDE_CODE_OAUTH_TOKEN

1. Go to https://github.com/settings/tokens
2. Generate a new token with appropriate permissions
3. Add it to your repository secrets as `CLAUDE_CODE_OAUTH_TOKEN`

## Debugging Workflow Failures

1. Check the workflow run logs for specific error messages
2. Verify all required secrets are set
3. Ensure the workflow has proper permissions
4. Check if the Claude Code Action is compatible with your repository settings

## Alternative Solutions

If the Claude Code Action continues to fail, consider:
1. Using the standard Anthropic API instead of the OAuth token
2. Implementing a custom action using the Claude API directly
3. Temporarily disabling the workflow until the issue is resolved