import os
from github import Github
from github import GithubException
from dotenv import load_dotenv

load_dotenv()

class GitIntegration:
    """Module for Git server integration (Git tech stack)."""
    def __init__(self, server_type='github'):
        self.server_type = server_type.lower()
        if self.server_type == 'github':
            token = os.getenv('GITHUB_TOKEN')
            if not token:
                raise ValueError("GITHUB_TOKEN not found in .env")
            self.client = Github(token)
        elif self.server_type == 'gitlab':
            raise NotImplementedError("GitLab support: Install python-gitlab and extend.")
        elif self.server_type == 'bitbucket':
            raise NotImplementedError("Bitbucket support: Install bitbucket-api and extend.")
        else:
            raise ValueError(f"Unsupported server: {server_type}")

    def fetch_pr(self, repo_name, pr_number):
        """Fetches PR data from GitHub (extensible)."""
        try:
            repo = self.client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            files = pr.get_files()
            pr_data = []
            for file in files:
                pr_data.append({
                    'filename': file.filename,
                    'patch': file.patch,
                    'content': repo.get_contents(file.filename, ref=pr.head.sha).decoded_content.decode('utf-8')
                })
            return pr_data
        except GithubException as e:
            raise ValueError(f"Error fetching PR: {e}")