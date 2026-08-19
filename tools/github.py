"""
GitHub Public Repository Info Tool for NOVA Agent.
Fetches repository metadata from the public GitHub REST API without requiring authentication.
"""
from typing import Any, Dict, Optional
import requests


def github_repo_info(owner: str, repo: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch public repository information from GitHub API.
    
    Args:
        owner: The GitHub username or organization (e.g. 'google', 'facebook'), or full 'owner/repo' string.
        repo: The repository name (e.g. 'gemini-api', 'react'). Optional if 'owner/repo' is provided in owner.
        
    Returns:
        A dictionary containing repository details (stars, forks, language, description, etc.) or error info.
    """
    if not owner or not str(owner).strip():
        return {
            "status": "error",
            "error": "Please provide a valid GitHub owner and repository name.",
        }

    owner_str = str(owner).strip()
    repo_str = str(repo).strip() if repo else ""

    # Support cases where user or LLM passed "owner/repo" in the owner parameter
    if "/" in owner_str and not repo_str:
        parts = owner_str.split("/", 1)
        owner_str, repo_str = parts[0].strip(), parts[1].strip()

    if not owner_str or not repo_str:
        return {
            "status": "error",
            "owner": owner_str,
            "repo": repo_str,
            "error": "Both repository owner (user/org) and repository name are required (e.g. 'google/gemini-api').",
        }

    # Clean URL components
    owner_str = owner_str.strip("/")
    repo_str = repo_str.strip("/")

    api_url = f"https://api.github.com/repos/{owner_str}/{repo_str}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "NOVA-Smart-Action-Agent/1.0",
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            license_info = data.get("license") or {}
            license_name = license_info.get("name") if isinstance(license_info, dict) else None

            return {
                "status": "success",
                "repository_name": data.get("name"),
                "full_name": data.get("full_name"),
                "description": data.get("description") or "No description provided.",
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "open_issues": data.get("open_issues_count", 0),
                "primary_language": data.get("language") or "Not specified",
                "is_private": data.get("private", False),
                "visibility": data.get("visibility", "public"),
                "default_branch": data.get("default_branch", "main"),
                "license": license_name or "Not specified",
                "html_url": data.get("html_url"),
                "created_at": data.get("created_at"),
                "updated_at": data.get("updated_at"),
                "topics": data.get("topics", []),
                "error": None,
            }

        elif response.status_code == 404:
            return {
                "status": "error",
                "owner": owner_str,
                "repo": repo_str,
                "error": f"Repository '{owner_str}/{repo_str}' was not found on GitHub. Please check the owner and repository name.",
            }

        elif response.status_code == 403:
            return {
                "status": "error",
                "owner": owner_str,
                "repo": repo_str,
                "error": "GitHub API rate limit exceeded or access forbidden. Please try again later.",
            }

        else:
            return {
                "status": "error",
                "owner": owner_str,
                "repo": repo_str,
                "error": f"GitHub API responded with HTTP status code {response.status_code}.",
            }

    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "owner": owner_str,
            "repo": repo_str,
            "error": "GitHub API request timed out. Please check your internet connection.",
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "owner": owner_str,
            "repo": repo_str,
            "error": "Network connection error while connecting to GitHub API.",
        }
    except Exception as e:
        return {
            "status": "error",
            "owner": owner_str,
            "repo": repo_str,
            "error": f"Unexpected error during GitHub repository lookup: {str(e)}",
        }
