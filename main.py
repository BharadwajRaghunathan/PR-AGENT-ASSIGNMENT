import argparse
from git_integration import GitIntegration
from code_analysis import CodeAnalysis
from feedback_generation import FeedbackGeneration
from inline_comments import InlineCommentGenerator
import os

def main():
    parser = argparse.ArgumentParser(description="PR Review Agent - Multi-Platform Code Review")
    parser.add_argument('--repo', help="Repository name (e.g., owner/repo)")
    parser.add_argument('--pr', type=int, help="PR number")
    parser.add_argument('--platform', choices=['github', 'gitlab'], default='github', help="Git platform")
    parser.add_argument('--web', action='store_true', help="Run web interface")
    parser.add_argument('--webhook', action='store_true', help="Run webhook server for CI/CD")
    args = parser.parse_args()
    
    if args.web:
        # Import Flask app only if --web is used
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    elif args.webhook:
        from webhook_server import WebhookServer
        webhook_server = WebhookServer()
        webhook_server.run()
    else:
        # CLI mode
        if not args.repo or not args.pr:
            print("Error: --repo and --pr are required for CLI mode")
            parser.print_help()
            return
            
        print(f"🔍 Fetching PR #{args.pr} from {args.platform.upper()} repo {args.repo}...")
        
        try:
            git = GitIntegration(server_type=args.platform)
            pr_data = git.fetch_pr(args.repo, args.pr)
            print(f"✅ Fetched {len(pr_data)} files from PR.")
            
            analyzer = CodeAnalysis()
            inline_generator = InlineCommentGenerator()
            analysis_results = []
            
            for file in pr_data:
                print(f"🔎 Analyzing {file['filename']} (content: {len(file['content'])} chars)...")
                issues = analyzer.analyze_file(file['content'], file['filename'])
                inline_comments = inline_generator.generate_inline_comments(file, issues)
                
                total_issues = sum(len(lst) for lst in issues.values())
                print(f"📊 Found {total_issues} issues in {file['filename']}")
                
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
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return

if __name__ == "__main__":
    main()