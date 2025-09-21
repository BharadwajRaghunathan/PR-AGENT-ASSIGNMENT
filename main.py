import argparse
from git_integration import GitIntegration
from code_analysis import CodeAnalysis
from feedback_generation import FeedbackGeneration
from inline_comments import InlineCommentGenerator
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="PR Review Agent - Multi-Platform Code Review")
    parser.add_argument('--repo', help="Repository name (e.g., owner/repo)")
    parser.add_argument('--pr', type=int, help="PR number")
    parser.add_argument('--platform', choices=['github', 'gitlab', 'bitbucket'], default='github', help="Git platform")
    parser.add_argument('--web', action='store_true', help="Run web interface")
    parser.add_argument('--webhook', action='store_true', help="Run webhook server for CI/CD")
    parser.add_argument('--ci', action='store_true', help="Run in CI/CD mode (auto-detect environment)")
    parser.add_argument('--post-comments', action='store_true', help="Post review comments back to PR")
    args = parser.parse_args()
    
    if args.web:
        # Import Flask app only if --web is used
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    elif args.webhook:
        from webhook_server import WebhookServer
        webhook_server = WebhookServer()
        webhook_server.run()
        
    elif args.ci:
        # CI/CD mode - auto-detect environment
        return run_ci_mode()
        
    else:
        # CLI mode
        if not args.repo or not args.pr:
            print("Error: --repo and --pr are required for CLI mode")
            parser.print_help()
            return 1
            
        return run_cli_mode(args.repo, args.pr, args.platform, args.post_comments)


def run_ci_mode():
    """Run in CI/CD mode with auto-detection."""
    print("🤖 Running in CI/CD mode...")
    
    # Detect CI environment
    if os.getenv('GITHUB_ACTIONS'):
        return run_github_actions_mode()
    elif os.getenv('GITLAB_CI'):
        return run_gitlab_ci_mode()
    elif os.getenv('BITBUCKET_BUILD_NUMBER'):
        return run_bitbucket_pipelines_mode()
    else:
        print("❌ Unknown CI environment. Supported: GitHub Actions, GitLab CI, Bitbucket Pipelines")
        return 1


def run_github_actions_mode():
    """Handle GitHub Actions environment."""
    print("🚀 Detected GitHub Actions environment")
    
    # Get GitHub environment variables
    repo = os.getenv('GITHUB_REPOSITORY')
    pr_number = os.getenv('GITHUB_PR_NUMBER')
    
    if not pr_number:
        # Try to extract from GitHub context
        github_ref = os.getenv('GITHUB_REF', '')
        if 'pull/' in github_ref:
            try:
                pr_number = github_ref.split('pull/')[1].split('/')[0]
            except:
                pass
    
    if not all([repo, pr_number]):
        print("❌ Could not determine repository and PR number from GitHub environment")
        print(f"   Repository: {repo}")
        print(f"   PR Number: {pr_number}")
        return 1
    
    return run_cli_mode(repo, int(pr_number), 'github', post_comments=True)


def run_gitlab_ci_mode():
    """Handle GitLab CI environment."""
    print("🚀 Detected GitLab CI environment")
    
    # Get GitLab environment variables
    project_path = os.getenv('CI_PROJECT_PATH')
    mr_iid = os.getenv('CI_MERGE_REQUEST_IID')
    
    if not all([project_path, mr_iid]):
        print("❌ Could not determine project path and MR number from GitLab environment")
        print(f"   Project Path: {project_path}")
        print(f"   MR IID: {mr_iid}")
        return 1
    
    return run_cli_mode(project_path, int(mr_iid), 'gitlab', post_comments=True)


def run_bitbucket_pipelines_mode():
    """Handle Bitbucket Pipelines environment."""
    print("🚀 Detected Bitbucket Pipelines environment")
    
    # Get Bitbucket environment variables
    repo_full_name = os.getenv('BITBUCKET_REPO_FULL_NAME')
    pr_id = os.getenv('BITBUCKET_PR_ID')
    
    if not all([repo_full_name, pr_id]):
        print("❌ Could not determine repository and PR ID from Bitbucket environment")
        print(f"   Repository: {repo_full_name}")
        print(f"   PR ID: {pr_id}")
        return 1
    
    return run_cli_mode(repo_full_name, int(pr_id), 'bitbucket', post_comments=True)


def run_cli_mode(repo_name, pr_number, platform, post_comments=False):
    """Run CLI analysis mode."""
    print(f"🔍 Fetching PR #{pr_number} from {platform.upper()} repo {repo_name}...")
    
    try:
        git = GitIntegration(server_type=platform)
        pr_data = git.fetch_pr(repo_name, pr_number)
        print(f"✅ Fetched {len(pr_data)} files from PR.")
        
        if not pr_data:
            print("⚠️  No files found in PR.")
            return 0
        
        analyzer = CodeAnalysis()
        inline_generator = InlineCommentGenerator()
        analysis_results = []
        total_issues = 0
        
        for file in pr_data:
            if not file['filename'].endswith('.py'):
                continue  # Skip non-Python files
                
            print(f"🔎 Analyzing {file['filename']} (content: {len(file['content'])} chars)...")
            issues = analyzer.analyze_file(file['content'], file['filename'])
            inline_comments = inline_generator.generate_inline_comments(file, issues)
            
            file_issues = sum(len(lst) for lst in issues.values())
            total_issues += file_issues
            print(f"📊 Found {file_issues} issues in {file['filename']}")
            
            analysis_results.append({
                'filename': file['filename'],
                'issues': issues,
                'inline_comments': inline_comments
            })
        
        feedback_gen = FeedbackGeneration()
        report = feedback_gen.generate_comprehensive_feedback(analysis_results, pr_data)
        
        print("\n" + "="*70)
        print("🎯 COMPREHENSIVE PR REVIEW REPORT")
        print("="*70)
        print(report)
        print("="*70)
        
        # Post comments if requested
        if post_comments and total_issues > 0:
            try:
                comment_posted = git.post_review_comment(repo_name, pr_number, report)
                if comment_posted:
                    print("✅ Posted review comment to PR")
                else:
                    print("⚠️  Failed to post review comment")
            except Exception as e:
                print(f"⚠️  Comment posting failed: {str(e)}")
        
        # Return appropriate exit code for CI
        if total_issues > 20:
            print(f"❌ Too many issues found ({total_issues}). Blocking merge.")
            return 1
        elif total_issues > 0:
            print(f"⚠️  {total_issues} issues found. Consider fixing before merge.")
            return 0
        else:
            print("✅ No issues found!")
            return 0
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
