#!/usr/bin/env python3
"""
TikHub API Client
Makes HTTP requests to TikHub API endpoints.
"""
import json
import sys
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional, List


class TikHubAPIClient:
    """Client for making requests to TikHub APIs."""

    # Default base URLs
    BASE_URL_CHINA = "https://api.tikhub.dev"
    BASE_URL_INTERNATIONAL = "https://api.tikhub.io"

    # Default token from openapi说明.md
    DEFAULT_TOKEN = "vZdfXsQag0amPbOZ8S3nNTqVRrVysjLT4kjaa6yL0gTnBk/asdaTAi8aA=="

    def __init__(self, api_token: str = None, base_url: str = None, use_china_domain: bool = False):
        """
        Initialize the TikHub API client.

        Args:
            api_token: TikHub API token (uses default if not provided)
            base_url: Custom base URL (auto-detected if not provided)
            use_china_domain: Use China domain (api.tikhub.dev) instead of international
        """
        self.api_token = api_token or self.DEFAULT_TOKEN

        if base_url:
            self.base_url = base_url
        elif use_china_domain:
            self.base_url = self.BASE_URL_CHINA
        else:
            self.base_url = self.BASE_URL_INTERNATIONAL

    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        if path.startswith('http'):
            return path
        # Fix Windows MSYS2 path conversion issue (e.g., C:/Program Files/Git/api/v1/...)
        # If path contains Windows drive letter, extract the actual API path
        if ':' in path and '\\' in path:
            # Extract the part after the last backslash or forward slash that looks like /api/...
            parts = path.replace('\\', '/').split('/')
            for i, part in enumerate(parts):
                if part.startswith('api'):
                    path = '/' + '/'.join(parts[i:])
                    break
        elif path.startswith('C:/') or path.startswith('D:/') or path.startswith('E:/'):
            # Handle Windows path conversion from MSYS2
            parts = path.replace('\\', '/').split('/')
            for i, part in enumerate(parts):
                if part.startswith('api'):
                    path = '/' + '/'.join(parts[i:])
                    break
        return f"{self.base_url}{path}"

    def _build_headers(self, content_type: str = "application/json") -> Dict[str, str]:
        """Build request headers with authorization."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": content_type
        }

    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to TikHub API.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path (e.g., /api/v1/tiktok/web/fetch_user_profile)
            params: Query parameters for GET requests
            body: Request body for POST requests
            headers: Additional headers (will be merged with defaults)

        Returns:
            Response data as dictionary

        Raises:
            urllib.error.URLError: If the request fails
        """
        url = self._build_url(path)

        # Build query string for GET requests
        if params and method.upper() == 'GET':
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"

        # Prepare headers
        req_headers = self._build_headers()
        if headers:
            req_headers.update(headers)

        # Prepare request body
        req_body = None
        if body:
            req_body = json.dumps(body).encode('utf-8')

        # Create request
        req = urllib.request.Request(
            url,
            data=req_body,
            headers=req_headers,
            method=method.upper()
        )

        try:
            # Send request
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data)

        except urllib.error.HTTPError as e:
            error_msg = f"HTTP {e.code}: {e.reason}"
            try:
                error_data = json.loads(e.read().decode('utf-8'))
                return {"error": error_msg, "details": error_data, "status_code": e.code}
            except:
                return {"error": error_msg, "status_code": e.code}

        except urllib.error.URLError as e:
            return {"error": f"Connection error: {e.reason}"}

        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return self.request("GET", path, params=params)

    def post(self, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request."""
        return self.request("POST", path, body=body)


def main():
    """CLI interface for the API client."""
    if len(sys.argv) < 3:
        print("Usage: python api_client.py <METHOD> <PATH> [param1=value1 param2=value2]")
        print("\nExamples:")
        print("  python api_client.py GET /api/v1/health/check")
        print("  python api_client.py GET /api/v1/tiktok/web/fetch_user_profile \"sec_user_id=MS4wLjABAAAA...\"")
        print("  python api_client.py POST /api/v1/tiktok/web/generate_xgnarly '{\"url\": \"https://...\"}'")
        sys.exit(1)

    client = TikHubAPIClient()
    method = sys.argv[1].upper()
    path = sys.argv[2]

    # Parse parameters or body
    params = {}
    body = None

    if len(sys.argv) > 3:
        arg = sys.argv[3]

        # Try parsing as JSON (for POST body)
        if arg.startswith('{'):
            try:
                body = json.loads(arg)
            except json.JSONDecodeError:
                print(f"Invalid JSON: {arg}")
                sys.exit(1)
        else:
            # Parse as key=value pairs
            for arg in sys.argv[3:]:
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    params[key] = value

    # Make the request
    if method == 'GET':
        result = client.get(path, params)
    elif method == 'POST':
        result = client.post(path, body)
    else:
        print(f"Unsupported method: {method}")
        sys.exit(1)

    # Print result
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
