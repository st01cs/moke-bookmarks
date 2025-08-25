# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a template repository for managing browser bookmarks using GitHub Issues. Each GitHub issue represents a single browser bookmark, and GitHub Actions automatically generates AI-powered summaries of the bookmark content.

## Project Structure

- `README.md` - Basic project title
- `.github/workflows/summary.yml` - GitHub Actions workflow for AI summarization

## Bookmark Management System

### Core Concept
- **GitHub Issues as Bookmarks**: Each issue represents a browser bookmark with title and URL
- **AI-Powered Summaries**: GitHub Actions automatically summarizes bookmark content using AI inference
- **Automated Workflow**: Triggered when new issues (bookmarks) are created

### GitHub Actions Workflow

The `summary.yml` workflow (`/.github/workflows/summary.yml:1-35`):
- **Trigger**: Runs when new issues are opened
- **Permissions**: Requires `issues: write`, `models: read`, `contents: read`
- **AI Integration**: Uses `actions/ai-inference@v1` to generate summaries
- **Auto-commenting**: Posts AI-generated summaries as issue comments

### Workflow Process
1. New issue created (representing a bookmark)
2. AI analyzes issue title and body
3. Generates one-paragraph summary
4. Posts summary as comment on the issue

## Development Commands

No traditional development commands as this is an issue-based bookmark management system. Management is done through:
- Creating GitHub issues for new bookmarks
- GitHub Actions automatically processes new issues
- AI summaries appear as issue comments

## Architecture Notes

This repository uses GitHub's native features (Issues, Actions, AI inference) rather than traditional code deployment. When working with this system:
- Focus on GitHub issue templates and workflows
- Understand the AI inference action integration
- Consider bookmark categorization through issue labels
- Potential enhancements might include issue templates for consistent bookmark formatting