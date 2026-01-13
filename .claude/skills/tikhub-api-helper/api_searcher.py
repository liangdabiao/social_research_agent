#!/usr/bin/env python3
"""
TikHub API Searcher
Helps search and find relevant APIs from the OpenAPI specification.
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Any


class TikHubAPISearcher:
    """Search and filter TikHub APIs from OpenAPI specification."""

    def __init__(self, openapi_path: str = None):
        """Initialize the searcher with the OpenAPI JSON file."""
        if openapi_path is None:
            # Default to openapi.json in the parent directory
            script_dir = Path(__file__).parent
            openapi_path = script_dir / "openapi.json"

        self.openapi_path = Path(openapi_path)
        self.data = self._load_openapi()

    def _load_openapi(self) -> Dict[str, Any]:
        """Load the OpenAPI JSON file."""
        with open(self.openapi_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_all_tags(self) -> List[Dict[str, str]]:
        """Get all API tags/categories."""
        return self.data.get('tags', [])

    def search_by_keyword(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search APIs by keyword in summary, description, or path.

        Args:
            keyword: Search keyword (supports English and Chinese)
            limit: Maximum results to return

        Returns:
            List of matching API endpoints with details
        """
        keyword_lower = keyword.lower()
        results = []

        paths = self.data.get('paths', {})

        for path, methods in paths.items():
            for method, details in methods.items():
                # Search in path, summary, description, and operationId
                path_lower = path.lower()
                summary = details.get('summary', '')
                description = details.get('description', '')
                operation_id = details.get('operationId', '')

                # Build searchable text
                searchable_text = f"{path} {summary} {description} {operation_id}".lower()

                if keyword_lower in searchable_text:
                    results.append({
                        'method': method.upper(),
                        'path': path,
                        'summary': summary,
                        'description': description[:200] if description else '',
                        'tags': details.get('tags', []),
                        'operation_id': operation_id,
                        'parameters': details.get('parameters', []),
                        'request_body': details.get('requestBody', {})
                    })

                if len(results) >= limit:
                    return results

        return results

    def search_by_tag(self, tag: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all APIs for a specific tag/category.

        Args:
            tag: Tag name (e.g., 'TikTok-Web-API', 'Douyin-App-V3-API')
            limit: Maximum results to return

        Returns:
            List of API endpoints for the tag
        """
        results = []
        paths = self.data.get('paths', {})

        for path, methods in paths.items():
            for method, details in methods.items():
                if tag in details.get('tags', []):
                    results.append({
                        'method': method.upper(),
                        'path': path,
                        'summary': details.get('summary', ''),
                        'operation_id': details.get('operationId', ''),
                        'parameters': details.get('parameters', []),
                        'request_body': details.get('requestBody', {})
                    })

                if len(results) >= limit:
                    return results

        return results

    def get_api_detail(self, operation_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific API by operation_id.

        Args:
            operation_id: The operation ID of the API

        Returns:
            Detailed API information including parameters, request body, responses
        """
        paths = self.data.get('paths', {})

        for path, methods in paths.items():
            for method, details in methods.items():
                if details.get('operationId') == operation_id:
                    return {
                        'method': method.upper(),
                        'path': path,
                        'summary': details.get('summary', ''),
                        'description': details.get('description', ''),
                        'tags': details.get('tags', []),
                        'parameters': details.get('parameters', []),
                        'request_body': details.get('requestBody', {}),
                        'responses': details.get('responses', {})
                    }

        return None

    def list_popular_apis(self, limit: int = 30) -> List[Dict[str, Any]]:
        """List commonly used/popular APIs."""
        popular_keywords = [
            'fetch_user', 'fetch_post', 'search', 'trending',
            'get_user', 'fetch_video', 'comment', 'like'
        ]

        results = []
        seen = set()

        for keyword in popular_keywords:
            matches = self.search_by_keyword(keyword, limit=10)
            for match in matches:
                key = f"{match['method']}:{match['path']}"
                if key not in seen:
                    seen.add(key)
                    results.append(match)
                    if len(results) >= limit:
                        return results

        return results

    def suggest_api(self, user_query: str) -> List[Dict[str, Any]]:
        """
        Suggest relevant APIs based on natural language query.

        Args:
            user_query: User's natural language query

        Returns:
            List of suggested APIs with relevance scores
        """
        query_lower = user_query.lower()

        # Define keyword mappings for common tasks
        mappings = {
            # User related
            'user profile': ['fetch_user_profile', 'get_user_info'],
            'user info': ['fetch_user_profile', 'get_user_info'],
            '个人信息': ['fetch_user_profile', 'get_user_info'],
            '用户信息': ['fetch_user_profile', 'get_user_info'],

            # Video/Post related
            'video': ['fetch_post', 'fetch_video'],
            'post': ['fetch_post', 'fetch_video'],
            '作品': ['fetch_post', 'fetch_video'],
            '视频': ['fetch_post', 'fetch_video'],
            '单个视频': ['fetch_post_detail', 'fetch_one_video'],

            # Search related
            'search': ['search', 'fetch_search'],
            '搜索': ['search', 'fetch_search'],

            # Comment related
            'comment': ['comment', 'fetch_comment'],
            '评论': ['comment', 'fetch_comment'],

            # Trending/Hot
            'trending': ['trending', 'hot', 'billboard'],
            'hot': ['trending', 'hot', 'billboard'],
            '热门': ['trending', 'hot', 'billboard'],
            '热点': ['trending', 'hot', 'billboard'],
        }

        # First try direct keyword matches
        results = self.search_by_keyword(user_query, limit=10)

        # Then try mapped keywords
        for key, keywords in mappings.items():
            if key in query_lower:
                for kw in keywords:
                    results.extend(self.search_by_keyword(kw, limit=5))

        # Deduplicate results
        seen = set()
        unique_results = []
        for r in results:
            key = f"{r['method']}:{r['path']}"
            if key not in seen:
                seen.add(key)
                unique_results.append(r)

        return unique_results[:15]


def main():
    """CLI interface for the API searcher."""
    if len(sys.argv) < 2:
        print("Usage: python api_searcher.py <search_keyword|tag:TAG_NAME|popular|detail:OPERATION_ID>")
        print("\nExamples:")
        print("  python api_searcher.py user profile")
        print("  python api_searcher.py tag:TikTok-Web-API")
        print("  python api_searcher.py popular")
        print("  python api_searcher.py detail:tiktok_web_fetch_user_profile_get")
        sys.exit(1)

    searcher = TikHubAPISearcher()
    query = sys.argv[1]

    if query.startswith('tag:'):
        # List all APIs for a tag
        tag = query[4:]
        results = searcher.search_by_tag(tag)
        print(f"\n=== APIs for tag: {tag} ({len(results)} results) ===\n")
        for r in results:
            print(f"{r['method']:6} {r['path']}")
            print(f"       └─ {r['summary']}\n")

    elif query.startswith('detail:'):
        # Get detailed info for an operation
        operation_id = query[7:]
        result = searcher.get_api_detail(operation_id)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"No API found with operation_id: {operation_id}")

    elif query == 'popular':
        # List popular APIs
        results = searcher.list_popular_apis()
        print(f"\n=== Popular TikHub APIs ({len(results)} results) ===\n")
        for r in results:
            print(f"{r['method']:6} {r['path'][:60]:60} | {r['tags'][0] if r['tags'] else ''}")
            print(f"       └─ {r['summary'][:80]}\n")

    elif query == 'tags':
        # List all tags
        tags = searcher.get_all_tags()
        print("\n=== Available API Tags/Categories ===\n")
        for tag in tags:
            print(f"  - {tag['name']}: {tag.get('description', '')}")

    else:
        # Keyword search
        results = searcher.search_by_keyword(query)
        print(f"\n=== Search results for '{query}' ({len(results)} results) ===\n")
        for r in results:
            print(f"{r['method']:6} {r['path'][:60]:60} | {r['tags'][0] if r['tags'] else ''}")
            print(f"       └─ {r['summary'][:80]}\n")


if __name__ == '__main__':
    main()
