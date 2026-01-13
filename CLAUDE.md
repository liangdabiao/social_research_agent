# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This repository contains a social media research toolkit focused on skills for deep web research and social media data collection via the TikHub API.

## Skills Architecture

Located in `.claude/skills/`, this repo provides three main skills:

### 1. deep-research
**Purpose**: Conduct comprehensive research on any topic using parallel subagents and web tools.

**Key Workflow**:
- Classify queries as depth-first, breadth-first, or straightforward
- Deploy 1-6 parallel subagents via the `Task` tool with `general-purpose` subagent_type
- Subagents use `web_search` → `web_fetch` OR Playwright MCP for JavaScript-heavy sites
- Synthesize findings and write final report (never delegate report writing)

**When to use**: For any research query requiring comprehensive investigation from multiple sources.

### 2. research-subagent
**Purpose**: Internal skill - executes focused research tasks delegated by deep-research lead agent.

**Constraints**:
- Hard limit: 20 tool calls maximum
- Minimum 3-5 tool calls typically
- Use parallel web_search calls (2+) for efficiency
- Always use `web_fetch` to get complete content after search
- Use Playwright MCP (`mcp__playwright__navigate` + `mcp__playwright__snapshot`) for modern web apps/JavaScript-heavy sites

### 3. tikhub-api-helper
**Purpose**: Search and query TikHub APIs for social media data from TikTok, Douyin, Xiaohongshu, Instagram, YouTube, Twitter, Reddit, and more.

**Key Scripts**:
- `api_searcher.py`: Search for relevant API endpoints by keyword, tag, or operation ID
- `api_client.py`: Make HTTP requests to TikHub API endpoints

**Usage Pattern**:
```bash
# Search for APIs
python .claude/skills/tikhub-api-helper/api_searcher.py "user profile"
python .claude/skills/tikhub-api-helper/api_searcher.py tag:TikTok-Web-API
python .claude/skills/tikhub-api-helper/api_searcher.py tags  # List all categories

# Get detailed API info
python .claude/skills/tikhub-api-helper/api_searcher.py detail:OPERATION_ID

# Make API requests
python .claude/skills/tikhub-api-helper/api_client.py GET /api/v1/tiktok/web/fetch_user_profile "sec_user_id=USER_ID"
```

**Base URLs**:
- China users: `https://api.tikhub.dev` (bypasses GFW)
- International: `https://api.tikhub.io`

**Authentication**: Uses default development token. Production users set `TIKHUB_TOKEN` environment variable.

### 4. citations
**Purpose**: Add citations to research reports after deep-research completes.

**Citation Format**: Footnote style or inline with access dates for social media data.

## Supported Platforms (TikHub API)

| Platform | Tag | APIs |
|----------|-----|------|
| TikTok Web | `TikTok-Web-API` | User profiles, video details, comments, search |
| TikTok App | `TikTok-App-V3-API` | 76 endpoints |
| Douyin Web | `Douyin-Web-API` | 76 endpoints |
| Douyin App | `Douyin-App-V3-API` | 45 endpoints |
| Douyin Search | `Douyin-Search-API` | 20 endpoints |
| Douyin Billboard | `Douyin-Billboard-API` | Trending/hot topics |
| Xiaohongshu | `Xiaohongshu-Web-API` | 26 endpoints |
| Instagram | `Instagram-V2-API` | 26 endpoints |
| YouTube | `YouTube-Web-API` | 16 endpoints |
| Twitter | `Twitter-Web-API` | 13 endpoints |
| Reddit | `Reddit-APP-API` | 23 endpoints |
| Bilibili | `Bilibili-Web-API` | 24 endpoints |
| Weibo | `Weibo-Web-V2-API` | 33 endpoints |
| Zhihu | `Zhihu-Web-API` | 32 endpoints |

Use `python .claude/skills/tikhub-api-helper/api_searcher.py tags` for full list.

## Research Tool Selection

**For Social Media Data**: Always prefer TikHub API over web scraping
- Structured, reliable data
- Proper rate limiting
- No JavaScript rendering issues
- Supports both Chinese and international platforms

**For General Web Research**:
1. Start with `web_search` for broad queries
2. Use `web_fetch` for static content (blogs, articles, docs)
3. Use Playwright MCP for:
   - Single Page Applications (React/Vue/Angular)
   - News sites with dynamic content
   - Social platforms (when TikHub API unavailable)
   - E-commerce sites
   - Sites with infinite scroll/lazy loading
   - Paywalls or login walls potentially bypassed by rendering

## Common Patterns

**Launching Deep Research**:
```
/deep-research Research topic here
```

**TikHub API Workflow**:
1. Use `api_searcher.py` to find relevant endpoints
2. Use `api_searcher.py detail:OPERATION_ID` to get parameters
3. Use `api_client.py` to make the request
4. Format results for user

**Rate Limits**:
- TikHub API: 10 QPS per endpoint
- Timeout: 30-60 seconds
- Max retry: 3 on error
