# Social Media Research Toolkit - QWEN Context

## Project Overview

This repository contains a social media research toolkit focused on skills for deep web research and social media data collection via the TikHub API. It leverages Claude Code's Agent Skills functionality to perform comprehensive research on various topics, with a particular emphasis on social media influence studies.

The project is designed to conduct parallel multi-source research using specialized skills that can search the web, fetch content, and access social media APIs through the TikHub service. The toolkit has been used to generate detailed research reports on social media influencers like Li Ziqi and Yao Ming, demonstrating its capability for comprehensive social media analysis.

## Core Architecture

The toolkit consists of four main skills located in the `.claude/skills/` directory:

### 1. deep-research
- **Purpose**: Conduct comprehensive research on any topic using parallel subagents and web tools
- **Key Workflow**: Classifies queries as depth-first, breadth-first, or straightforward, deploys 1-6 parallel subagents via the Task tool, synthesizes findings, and writes final reports
- **Tool Integration**: Uses web_search → web_fetch for static content, Playwright MCP for JavaScript-heavy sites, and TikHub API for social media data

### 2. research-subagent
- **Purpose**: Internal skill that executes focused research tasks delegated by the deep-research lead agent
- **Constraints**: Hard limit of 20 tool calls maximum, minimum 3-5 tool calls typically
- **Efficiency**: Uses parallel web_search calls for efficiency, always uses web_fetch to get complete content after search

### 3. tikhub-api-helper
- **Purpose**: Search and query TikHub APIs for social media data from multiple platforms
- **Supported Platforms**: TikTok, Douyin, Xiaohongshu, Instagram, YouTube, Twitter, Reddit, Bilibili, Weibo, Zhihu
- **Key Scripts**: api_searcher.py for searching API endpoints, api_client.py for making HTTP requests

### 4. citations
- **Purpose**: Add citations to research reports after deep-research completes
- **Citation Format**: Footnote style or inline with access dates for social media data

## Research Methodology

The toolkit follows a systematic approach to research:

1. **Query Classification**: Determines if the research requires depth-first (multiple perspectives), breadth-first (independent sub-questions), or straightforward (focused) approaches
2. **Parallel Execution**: Deploys 2-6 subagents simultaneously to research different aspects of the query
3. **Tool Selection**: Chooses appropriate tools based on content type (web_search/web_fetch for static content, Playwright MCP for dynamic sites, TikHub API for social media data)
4. **Synthesis**: Combines findings from all subagents into a comprehensive report
5. **Citation**: Adds proper citations to enhance trust and verifiability

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

## Usage Examples

The toolkit has been used to generate comprehensive research reports such as:
- "Li Ziqi's Influence and Evaluation in Foreign Media: In-depth Research Report"
- "Yao Ming's Influence and Evaluation in Foreign Media: Research Report"

These reports demonstrate the toolkit's ability to:
- Analyze social media influence across different cultural contexts
- Gather data from multiple sources and platforms
- Synthesize complex information into structured reports
- Include quantitative data, qualitative analysis, and source citations

## Key Features

1. **Parallel Research**: Multiple subagents work simultaneously to accelerate research
2. **Multi-source Verification**: Cross-references information across multiple sources
3. **API Integration**: Direct access to social media platforms via TikHub API
4. **Adaptive Tool Selection**: Chooses the most appropriate tool for each content type
5. **Quality Control**: Built-in verification and quality assessment guidelines
6. **Citation Management**: Automatic citation addition for enhanced trust

## Development Conventions

- Skills are organized in the `.claude/skills/` directory with proper SKILL.md files
- Each skill has a clear name, description, and instruction set
- Tool permissions are configured in `.claude/settings.local.json`
- Research reports follow a structured Markdown format with clear sections
- Citations are added using footnote or inline styles with access dates for social media data

## Building and Running

The toolkit runs within the Claude Code environment and requires:

1. Claude Code version with Agent Skills support
2. Proper configuration of tool permissions in settings.local.json
3. Access to web search and fetch tools
4. TikHub API access (with optional authentication token)

To launch deep research:
```
/deep-research Research topic here
```

To use TikHub API functionality:
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

## Current State

The toolkit is actively used to generate detailed research reports on social media influencers and their global impact. The existing reports on Li Ziqi and Yao Ming demonstrate the toolkit's effectiveness in analyzing cross-cultural influence, media perception, and social media metrics across different regions and cultural contexts.