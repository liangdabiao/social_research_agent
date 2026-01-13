# Social Media Research Toolkit

A comprehensive research toolkit for conducting deep web research and social media data collection using Claude Code and the TikHub API. This toolkit enables comprehensive analysis of social media influencers, trends, and cross-cultural impact through parallel multi-agent research methodologies.

## Overview

This repository contains a sophisticated social media research system that combines Claude Code's Agent Skills with specialized tools for deep research and social media data collection. The toolkit has been used to generate detailed research reports on influential figures like Li Ziqi and Yao Ming, demonstrating its capability for comprehensive social media analysis.

## Features

- **Parallel Research Agents**: Deploy multiple subagents simultaneously for faster, more comprehensive research
- **Multi-Platform Social Media API Access**: Integrated with TikHub API for access to TikTok, Douyin, Xiaohongshu, Instagram, YouTube, Twitter, Reddit, Bilibili, Weibo, and Zhihu
- **Adaptive Tool Selection**: Automatically chooses the best tools for different content types (web search, content fetching, JavaScript rendering)
- **Structured Research Reports**: Generates comprehensive, well-cited research reports with quantitative data and qualitative analysis
- **Cross-Cultural Analysis**: Specialized for analyzing social media influence across different cultural contexts

## Architecture

The toolkit consists of four main skills:

### 1. Deep Research Lead Agent (`deep-research`)
- Coordinates comprehensive research processes
- Classifies queries and determines optimal research strategy
- Deploys parallel subagents for efficient research
- Synthesizes findings into final reports

### 2. Research Subagent (`research-subagent`)
- Executes focused research tasks delegated by the lead agent
- Uses web tools efficiently with a maximum of 20 tool calls
- Employs OODA (Observe, Orient, Decide, Act) methodology

### 3. TikHub API Helper (`tikhub-api-helper`)
- Searches and queries TikHub APIs for social media data
- Supports 14+ social media platforms with thousands of API endpoints
- Includes tools for API discovery and client requests

### 4. Citations Agent (`citations`)
- Adds proper citations to research reports
- Uses footnote or inline citation formats
- Maintains source integrity and trustworthiness

## Supported Platforms

| Platform | APIs Available | Use Cases |
|----------|---------------|-----------|
| TikTok Web | 58 endpoints | User profiles, video details, comments, search |
| TikTok App | 76 endpoints | Full app functionality access |
| Douyin Web | 76 endpoints | Chinese domestic platform data |
| Douyin App | 45 endpoints | Mobile app data |
| Xiaohongshu | 26 endpoints | Chinese lifestyle sharing platform |
| Instagram | 26 endpoints | User profiles, posts, engagement |
| YouTube | 16 endpoints | Video content and engagement |
| Twitter/X | 13 endpoints | Tweet data and user activity |
| Reddit | 23 endpoints | Community discussions |
| Bilibili | 24 endpoints | Chinese video platform |
| Weibo | 33 endpoints | Chinese microblogging |
| Zhihu | 32 endpoints | Chinese Q&A platform |

## Usage

### Starting a Research Task

To initiate deep research on a topic:

```
/deep-research [your research topic here]
```

### Using TikHub API

To search for relevant APIs:

```bash
# Search by keyword
python .claude/skills/tikhub-api-helper/api_searcher.py "user profile"

# List APIs by category
python .claude/skills/tikhub-api-helper/api_searcher.py tag:TikTok-Web-API

# Get detailed API info
python .claude/skills/tikhub-api-helper/api_searcher.py detail:OPERATION_ID

# Make API requests
python .claude/skills/tikhub-api-helper/api_client.py GET /api/v1/tiktok/web/fetch_user_profile "sec_user_id=USER_ID"
```

### Research Process

1. **Query Classification**: The system determines if research requires depth-first, breadth-first, or straightforward approaches
2. **Parallel Execution**: Multiple subagents work simultaneously on different aspects
3. **Tool Selection**: Appropriate tools selected based on content type
4. **Data Collection**: Information gathered from multiple sources
5. **Synthesis**: Findings combined into comprehensive report
6. **Citation**: Proper citations added to enhance trust

## Example Research Reports

The toolkit has generated detailed reports including:

- **Li Ziqi's Influence in Foreign Media**: Analysis of her global impact, cultural significance, and media reception across different cultures
- **Yao Ming's International Influence**: Comprehensive study of his role as a cultural bridge between China and the US, career impact, and ongoing influence

These reports demonstrate the toolkit's ability to:
- Analyze cross-cultural reception and influence
- Gather quantitative metrics and qualitative assessments
- Synthesize information from diverse sources
- Provide nuanced cultural context

## Configuration

The toolkit uses Claude Code's permission system configured in `.claude/settings.local.json`. Ensure proper permissions are granted for:
- Web search and content fetching
- Bash command execution for API tools
- Playwright browser automation
- Skill execution

## Research Methodology

The toolkit employs a systematic approach to research:

1. **Assessment**: Analyze the query and identify key concepts and required data points
2. **Planning**: Determine optimal research strategy and subagent deployment
3. **Execution**: Parallel research using appropriate tools and methods
4. **Verification**: Cross-reference information across multiple sources
5. **Synthesis**: Combine findings into comprehensive, structured reports
6. **Citation**: Add proper attribution and source verification

## Best Practices

- Use specific, well-defined research queries for optimal results
- Allow sufficient time for parallel agents to complete comprehensive research
- Verify critical information across multiple sources
- Consider cultural context when analyzing social media influence
- Use TikHub API for structured social media data rather than web scraping

## Contributing

Contributions to improve research methodologies, add new API integrations, or enhance report quality are welcome. Please follow the existing skill architecture and maintain the parallel research approach.

## License

This research toolkit is provided as-is for educational and research purposes.

## Acknowledgments

This toolkit leverages Claude Code's Agent Skills functionality and integrates with the TikHub API service for comprehensive social media research capabilities.