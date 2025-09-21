import os
from github import Github
from github import GithubException
import gitlab
from dotenv import load_dotenv
import requests

load_dotenv()

class GitIntegration:
    """Enhanced Git integration supporting GitHub and GitLab."""
    
    def __init__(self, server_type='github'):
        self.server_type = server_type.lower()
        
        if self.server_type == 'github':
            token = os.getenv('GITHUB_TOKEN')
            if not token:
                raise ValueError("GITHUB_TOKEN not found in .env")
            self.client = Github(token)
            print("✅ GitHub client initialized.")
            
        elif self.server_type == 'gitlab':
            token = os.getenv('GITLAB_TOKEN')
            gitlab_url = os.getenv('GITLAB_URL', 'https://gitlab.com')
            if not token:
                raise ValueError("GITLAB_TOKEN not found in .env")
            self.client = gitlab.Gitlab(gitlab_url, private_token=token)
            print("✅ GitLab client initialized.")
            
        elif self.server_type == 'bitbucket':
            # Future enhancement - placeholder
            raise NotImplementedError("Bitbucket support coming soon. Install atlassian-python-api.")
        else:
            raise ValueError(f"Unsupported server: {server_type}")

    def fetch_pr(self, repo_name, pr_number):
        """Fetch PR data from configured git server."""
        if self.server_type == 'github':
            return self._fetch_github_pr(repo_name, pr_number)
        elif self.server_type == 'gitlab':
            return self._fetch_gitlab_pr(repo_name, pr_number)
        else:
            raise NotImplementedError(f"PR fetching not implemented for {self.server_type}")

    def _fetch_github_pr(self, repo_name, pr_number):
        """Fetch GitHub PR data."""
        try:
            print(f"🔗 Connecting to GitHub repo {repo_name}...")
            repo = self.client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            print(f"📝 PR #{pr_number}: {pr.title}")
            print(f"👤 Author: {pr.user.login}")
            print(f"🌿 Base: {pr.base.ref} ← Head: {pr.head.ref}")
            
            files = list(pr.get_files())
            print(f"📁 Found {len(files)} files in PR")
            
            pr_data = []
            for file in files:
                try:
                    content_obj = repo.get_contents(file.filename, ref=pr.head.sha)
                    content = content_obj.decoded_content if content_obj.decoded_content else b''
                    pr_data.append({
                        'filename': file.filename,
                        'patch': file.patch or '',
                        'content': content.decode('utf-8') if content else '',
                        'additions': file.additions,
                        'deletions': file.deletions,
                        'status': file.status,
                        'sha': file.sha
                    })
                    print(f"   📄 {file.filename} (+{file.additions}/-{file.deletions})")
                except Exception as e:
                    print(f"   ⚠️  Could not fetch content for {file.filename}: {str(e)}")
                    pr_data.append({
                        'filename': file.filename,
                        'patch': file.patch or '',
                        'content': '',
                        'additions': file.additions,
                        'deletions': file.deletions,
                        'status': file.status,
                        'sha': file.sha
                    })
                    
            return pr_data
            
        except GithubException as e:
            raise ValueError(f"GitHub API error for PR {pr_number} in {repo_name}: {str(e)}")

    def _fetch_gitlab_pr(self, repo_name, mr_number):
        """Fetch GitLab Merge Request data."""
        try:
            print(f"🔗 Connecting to GitLab project {repo_name}...")
            project = self.client.projects.get(repo_name)
            mr = project.mergerequests.get(mr_number)
            print(f"📝 MR #{mr_number}: {mr.title}")
            print(f"👤 Author: {mr.author['name']}")
            print(f"🌿 Base: {mr.target_branch} ← Head: {mr.source_branch}")
            
            changes = mr.changes()
            files = changes.get('changes', [])
            print(f"📁 Found {len(files)} files in MR")
            
            pr_data = []
            for file in files:
                try:
                    # Get file content from source branch
                    file_info = project.files.get(file['new_path'], ref=mr.source_branch)
                    content = file_info.decode().decode('utf-8')
                    
                    pr_data.append({
                        'filename': file['new_path'],
                        'patch': file.get('diff', ''),
                        'content': content,
                        'additions': 0,  # GitLab API doesn't provide exact counts easily
                        'deletions': 0,
                        'status': 'modified',
                        'sha': file.get('new_file', {}).get('blob_id', '')
                    })
                    print(f"   📄 {file['new_path']}")
                except Exception as e:
                    print(f"   ⚠️  Could not fetch content for {file['new_path']}: {str(e)}")
                    pr_data.append({
                        'filename': file['new_path'],
                        'patch': file.get('diff', ''),
                        'content': '',
                        'additions': 0,
                        'deletions': 0,
                        'status': 'modified',
                        'sha': ''
                    })
                    
            return pr_data
            
        except gitlab.exceptions.GitlabError as e:
            raise ValueError(f"GitLab API error for MR {mr_number} in {repo_name}: {str(e)}")

    def post_review_comment(self, repo_name, pr_number, comment_body):
        """Post a review comment to the PR/MR."""
        if self.server_type == 'github':
            return self._post_github_comment(repo_name, pr_number, comment_body)
        elif self.server_type == 'gitlab':
            return self._post_gitlab_comment(repo_name, pr_number, comment_body)
        else:
            raise NotImplementedError(f"Comment posting not implemented for {self.server_type}")

    def _post_github_comment(self, repo_name, pr_number, comment_body):
        """Post comment to GitHub PR."""
        try:
            repo = self.client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            pr.create_issue_comment(comment_body)
            print("✅ Posted review comment to GitHub")
            return True
        except Exception as e:
            print(f"❌ Failed to post GitHub comment: {str(e)}")
            return False

    def _post_gitlab_comment(self, repo_name, mr_number, comment_body):
        """Post comment to GitLab MR."""
        try:
            project = self.client.projects.get(repo_name)
            mr = project.mergerequests.get(mr_number)
            mr.notes.create({'body': comment_body})
            print("✅ Posted review comment to GitLab")
            return True
        except Exception as e:
            print(f"❌ Failed to post GitLab comment: {str(e)}")
            return False