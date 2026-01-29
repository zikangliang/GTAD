import os
import datetime
import requests
import base64
from typing import List, Dict, Optional

class GitHubScraper:
    def __init__(self, token: Optional[str] = None):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
        
        # Fallback to env var if not provided explicitly
        if not token and os.getenv("GITHUB_TOKEN"):
             self.headers["Authorization"] = f"token {os.getenv('GITHUB_TOKEN')}"

    def get_trending_repos(self, limit: int = 10, language: str = None) -> List[Dict]:
        """
        Fetches 'trending' repositories using GitHub Search API.
        Strategy: Search for repositories created in the last 2 days, sorted by stars.
        This finds *new* hot projects.
        """
        # Calculate date 2 days ago
        date_since = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        
        query = f"created:>{date_since}"
        if language:
            query += f" language:{language}"
            
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": limit
        }
        
        try:
            response = requests.get(f"{self.base_url}/search/repositories", headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching trending repos: {e}")
            return []

    def get_readme_content(self, owner: str, repo: str) -> str:
        """
        Fetches and decodes the README content for a repository.
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/readme"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            # GitHub API returns content encoded in base64
            content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
            return content
        except requests.exceptions.RequestException as e:
            print(f"Error fetching README for {owner}/{repo}: {e}")
            return ""

    def filter_repos(self, repos: List[Dict]) -> List[Dict]:
        """
        Basic filtering as per PRD:
        - Exclude non-technical projects (heuristic based on topics/description, 
          though hard to perfect, we can filter by specific keywords if needed).
        For MVP, we pass through most, maybe filter if description contains 'books' or 'list'.
        """
        filtered = []
        exclude_keywords = ["free-programming-books", "awesome", "interview", "roadmap"]
        
        for repo in repos:
            name = repo.get("name", "").lower()
            description = (repo.get("description") or "").lower()
            
            if any(kw in name or kw in description for kw in exclude_keywords):
                continue
                
            filtered.append(repo)
            
        return filtered

if __name__ == "__main__":
    # Test execution
    from dotenv import load_dotenv
    load_dotenv()
    
    scraper = GitHubScraper()
    print("Fetching trending repos...")
    repos = scraper.get_trending_repos(limit=5)
    filtered_repos = scraper.filter_repos(repos)
    
    for repo in filtered_repos:
        print(f"Name: {repo['full_name']}")
        print(f"Stars: {repo['stargazers_count']}")
        print(f"URL: {repo['html_url']}")
        # print(f"Description: {repo['description']}")
        # readme = scraper.get_readme_content(repo['owner']['login'], repo['name'])
        # print(f"README length: {len(readme)}")
        print("-" * 20)
