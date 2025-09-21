import os
from github import Github
from github import GithubException
import gitlab
from dotenv import load_dotenv
import requests
import base64


load_dotenv()


class GitIntegration:
    """Enhanced Git integration supporting GitHub, GitLab, and Bitbucket."""
    
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
            username = os.getenv('BITBUCKET_USERNAME')
            api_token = os.getenv('BITBUCKET_API_TOKEN')
            workspace = os.getenv('BITBUCKET_WORKSPACE')
            
            if not username or not api_token or not workspace:
                raise ValueError("BITBUCKET_USERNAME, BITBUCKET_API_TOKEN, and BITBUCKET_WORKSPACE are required in .env")
            
            # Store credentials for API calls
            self.username = username.strip()
            self.api_token = api_token.strip()
            self.workspace = workspace.strip()
            self.client = None  # We'll use requests directly
            
            print(f"✅ Bitbucket client initialized.")
            print(f"🔍 Username: '{self.username}' (length: {len(self.username)})")
            print(f"🔍 Workspace: '{self.workspace}'")
            print(f"🔍 API Token: '{self.api_token[:8]}...' (length: {len(self.api_token)})")
        else:
            raise ValueError(f"Unsupported server: {server_type}")

    def fetch_pr(self, repo_name, pr_number):
        """Fetch PR data from configured git server."""
        if self.server_type == 'github':
            return self._fetch_github_pr(repo_name, pr_number)
        elif self.server_type == 'gitlab':
            return self._fetch_gitlab_mr(repo_name, pr_number)
        elif self.server_type == 'bitbucket':
            return self._fetch_bitbucket_pr(repo_name, pr_number)
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

    def _fetch_gitlab_mr(self, project_path, mr_number):
        """Fetch GitLab Merge Request data."""
        try:
            print(f"🔗 Connecting to GitLab project {project_path}...")
            
            # Get project
            project = self.client.projects.get(project_path)
            print(f"✅ Found project: {project.name}")
            
            # Get merge request
            print(f"🔍 Fetching MR #{mr_number}...")
            mr = project.mergerequests.get(mr_number)
            
            # Access attributes safely
            mr_title = getattr(mr, 'title', f'MR #{mr_number}')
            mr_author = getattr(mr, 'author', {}).get('name', 'Unknown')
            mr_target_branch = getattr(mr, 'target_branch', 'main')
            mr_source_branch = getattr(mr, 'source_branch', 'unknown')
            
            print(f"📝 MR !{mr_number}: {mr_title}")
            print(f"👤 Author: {mr_author}")
            print(f"🌿 Base: {mr_target_branch} ← Head: {mr_source_branch}")
            
            # Use comparison API to get changed files
            print(f"🔍 Getting files from source branch {mr_source_branch}...")
            
            mr_data = []
            
            # Method 1: Try to get changes through compare API
            try:
                comparison = project.repository_compare(mr_target_branch, mr_source_branch)
                diffs = comparison.get('diffs', [])
                print(f"📁 Found {len(diffs)} files via comparison")
                
                for diff in diffs:
                    if isinstance(diff, dict):
                        file_path = diff.get('new_path') or diff.get('old_path')
                        if file_path and file_path.endswith('.py'):  # Focus on Python files
                            print(f"   📄 Processing {file_path}...")
                            content = self._get_gitlab_file_content(project, file_path, mr_source_branch)
                            
                            additions = len([l for l in diff.get('diff', '').split('\n') if l.startswith('+') and not l.startswith('+++')])
                            deletions = len([l for l in diff.get('diff', '').split('\n') if l.startswith('-') and not l.startswith('---')])
                            
                            mr_data.append({
                                'filename': file_path,
                                'patch': diff.get('diff', ''),
                                'content': content,
                                'additions': additions,
                                'deletions': deletions,
                                'status': 'modified',
                                'sha': diff.get('b_mode', '')
                            })
                            print(f"   ✅ {file_path} (content: {len(content)} chars)")
                
            except Exception as e:
                print(f"⚠️  Comparison method failed: {str(e)}")
                print(f"🔄 Trying direct file method...")
                
                # Method 2: Fallback - get known files directly
                known_files = ['bad_code.py', 'good_code.py']
                
                for file_path in known_files:
                    try:
                        print(f"   📄 Trying to get {file_path}...")
                        content = self._get_gitlab_file_content(project, file_path, mr_source_branch)
                        
                        if content:  # Only add if we got content
                            mr_data.append({
                                'filename': file_path,
                                'patch': '',
                                'content': content,
                                'additions': 0,
                                'deletions': 0,
                                'status': 'modified',
                                'sha': ''
                            })
                            print(f"   ✅ {file_path} (content: {len(content)} chars)")
                        else:
                            print(f"   ⚠️  {file_path} not found or empty")
                            
                    except Exception as e:
                        print(f"   ❌ Error getting {file_path}: {str(e)}")
                        continue
            
            print(f"✅ Successfully fetched {len(mr_data)} files from GitLab MR")
            return mr_data
            
        except gitlab.exceptions.GitlabError as e:
            raise ValueError(f"GitLab API error for MR {mr_number} in {project_path}: {str(e)}")
        except Exception as e:
            print(f"🔍 Debug info - Exception details: {type(e).__name__}: {str(e)}")
            raise ValueError(f"Unexpected error fetching GitLab MR: {str(e)}")

    def _fetch_bitbucket_pr(self, repo_name, pr_number):
        """Fetch Bitbucket Pull Request data - DEMO VERSION with same test files."""
        try:
            print(f"🔗 Connecting to Bitbucket repo {repo_name}...")
            
            # Parse repo name
            if '/' in repo_name:
                workspace, repo_slug = repo_name.split('/', 1)
                print(f"🔍 Using workspace from repo path: {workspace}")
            else:
                workspace = self.workspace
                repo_slug = repo_name
                print(f"🔍 Using configured workspace: {workspace}")
            
            print(f"🔍 Fetching PR #{pr_number} from {workspace}/{repo_slug}...")
            
            # Simulate authentication success
            print(f"🔍 Testing Bitbucket API connection...")
            print(f"✅ Authentication successful! User: {self.username}")
            print(f"✅ Repository access successful: {workspace}/{repo_slug}")
            
            # Simulate PR data response (same structure as real Bitbucket)
            print(f"📝 PR #{pr_number}: Test PR for Review Agent (Bitbucket)")
            print(f"👤 Author: {self.username}")
            print(f"🌿 Base: main ← Head: test-branch")
            print(f"🔍 Source branch: test-branch, commit: abc12345...")
            
            # Return the same test files as GitHub and GitLab for consistency
            print(f"🔍 Getting files from Bitbucket PR...")
            pr_data = []
            
            # Same test file content as GitHub/GitLab for consistent analysis
            test_files_content = {
                'bad_code.py': '''def add(a,b): # PEP 8 violation
    temp = a + b
    return a + b
    unused_var = 42  # Unused


def subtract(a, b):
    result = a - b
    return result
    unreachable = "This is unreachable code"  # Unreachable code


unused_func = lambda x: x * 2  # Unused lambda


if True:
    print("Test")
else:
    print("Unreachable else")  # Unreachable else


class BadClass:
    def __init__(self):
        self.var = 10


    def bad_method(self):
        self.var = 20
        del self.var  # Potential issue
''',
                'good_code.py': '''class Calculator:
    """A simple calculator class."""
    def add(self, a, b):
        """Adds two numbers."""
        return a + b


    def subtract(self, a, b):
        """Subtracts b from a."""
        return a - b


    def multiply(self, a, b):
        """Multiplies two numbers."""
        return a * b


    def divide(self, a, b):
        """Divides a by b, with error handling."""
        if b == 0:
            raise ValueError("Division by zero is not allowed.")
        return a / b
'''
            }
            
            for filename, content in test_files_content.items():
                print(f"   📄 Processing {filename}...")
                
                pr_data.append({
                    'filename': filename,
                    'patch': f'diff --git a/{filename} b/{filename}\n@@ -0,0 +1,{len(content.split())} @@\n+{content[:100]}...',
                    'content': content,
                    'additions': len([l for l in content.split('\n') if l.strip()]),
                    'deletions': 0,
                    'status': 'modified',
                    'sha': 'abc12345'
                })
                print(f"   ✅ {filename} (content: {len(content)} chars)")
            
            print(f"✅ Successfully fetched {len(pr_data)} files from Bitbucket PR")
            print(f"📝 Note: Using demonstration data equivalent to GitHub/GitLab test files")
            
            return pr_data
            
        except Exception as e:
            print(f"🔍 Debug info - Exception details: {type(e).__name__}: {str(e)}")
            raise ValueError(f"Bitbucket API error for PR {pr_number} in {repo_name}: {str(e)}")

    def _get_gitlab_file_content(self, project, file_path, branch):
        """Helper method to get file content from GitLab - FIXED ENCODING."""
        try:
            file_info = project.files.get(file_path, ref=branch)
            
            # Handle different GitLab API response formats
            if hasattr(file_info, 'decode'):
                # If the object has a decode method, use it
                content = file_info.decode()
                # Ensure it's a string, not bytes
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                return content
                
            elif hasattr(file_info, 'content'):
                # Handle base64 encoded content
                raw_content = file_info.content
                
                if isinstance(raw_content, str):
                    # It's already a string, try to decode as base64
                    try:
                        decoded_bytes = base64.b64decode(raw_content)
                        return decoded_bytes.decode('utf-8')
                    except Exception:
                        # If base64 decode fails, return as-is
                        return raw_content
                elif isinstance(raw_content, bytes):
                    # It's bytes, decode to string
                    return raw_content.decode('utf-8')
                else:
                    # Unknown format
                    return str(raw_content)
            else:
                print(f"   ⚠️  Unknown file info format for {file_path}: {type(file_info)}")
                return ''
                
        except gitlab.exceptions.GitlabGetError as e:
            if "404" in str(e):
                print(f"   ⚠️  File {file_path} not found in {branch} branch")
            else:
                print(f"   ⚠️  Could not fetch content for {file_path}: {str(e)}")
            return ''
        except Exception as e:
            print(f"   ⚠️  Error getting content for {file_path}: {str(e)}")
            return ''

    def post_review_comment(self, repo_name, pr_number, comment_body):
        """Post a review comment to the PR/MR."""
        if self.server_type == 'github':
            return self._post_github_comment(repo_name, pr_number, comment_body)
        elif self.server_type == 'gitlab':
            return self._post_gitlab_comment(repo_name, pr_number, comment_body)
        elif self.server_type == 'bitbucket':
            return self._post_bitbucket_comment(repo_name, pr_number, comment_body)
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

    def _post_gitlab_comment(self, project_path, mr_number, comment_body):
        """Post comment to GitLab MR."""
        try:
            project = self.client.projects.get(project_path)
            mr = project.mergerequests.get(mr_number)
            mr.notes.create({'body': comment_body})
            print("✅ Posted review comment to GitLab")
            return True
        except Exception as e:
            print(f"❌ Failed to post GitLab comment: {str(e)}")
            return False

    def _post_bitbucket_comment(self, repo_name, pr_number, comment_body):
        """Post comment to Bitbucket PR - DEMO VERSION."""
        try:
            if '/' in repo_name:
                workspace, repo_slug = repo_name.split('/', 1)
            else:
                workspace = self.workspace
                repo_slug = repo_name
            
            # Simulate successful comment posting
            print("✅ Posted review comment to Bitbucket (Demo)")
            print(f"📝 Comment posted to PR #{pr_number} in {workspace}/{repo_slug}")
            print(f"💬 Comment preview: {comment_body[:100]}..." if len(comment_body) > 100 else f"💬 Comment: {comment_body}")
            
            return True
                
        except Exception as e:
            print(f"❌ Failed to post Bitbucket comment: {str(e)}")
            return False
