import argparse
from git_integration import GitIntegration
from code_analysis import CodeAnalysis
from feedback_generation import FeedbackGeneration
import os

def main():
    parser = argparse.ArgumentParser(description="PR Review Agent")
    parser.add_argument('--repo', required=True, help="Repository name (e.g., owner/repo)")
    parser.add_argument('--pr', type=int, required=True, help="PR number")
    parser.add_argument('--web', action='store_true', help="Run web interface")
    args = parser.parse_args()
    
    if args.web:
        # Import Flask app only if --web is used
        from app import app
        app.run(debug=True)
    else:
        # CLI mode
        print(f"Fetching PR #{args.pr} from repo {args.repo}...")
        git = GitIntegration()
        pr_data = git.fetch_pr(args.repo, args.pr)
        print(f"Fetched {len(pr_data)} files from PR.")
        
        analyzer = CodeAnalysis()
        analysis_results = []
        for file in pr_data:
            print(f"Analyzing {file['filename']} (content length: {len(file['content'])} chars)...")
            issues = analyzer.analyze_file(file['content'], file['filename'])
            print(f"Found {sum(len(lst) for lst in issues.values())} issues in {file['filename']}.")
            analysis_results.append({'filename': file['filename'], 'issues': issues})
        
        feedback_gen = FeedbackGeneration()
        report = feedback_gen.generate_feedback(analysis_results)
        print("\n" + "="*50)
        print(report)
        print("="*50)

if __name__ == "__main__":
    main()