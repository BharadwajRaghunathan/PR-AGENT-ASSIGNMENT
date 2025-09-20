import argparse
from git_integration import GitIntegration
from code_analysis import CodeAnalysis
from feedback_generation import FeedbackGeneration
from app import app  # Optional Flask app

def main():
    parser = argparse.ArgumentParser(description="PR Review Agent")
    parser.add_argument('--repo', required=True, help="Repository name (e.g., owner/repo)")
    parser.add_argument('--pr', type=int, required=True, help="PR number")
    parser.add_argument('--web', action='store_true', help="Run web interface")
    args = parser.parse_args()
    
    if args.web:
        # Run Flask web interface
        app.run(debug=True)
    else:
        # CLI mode
        git = GitIntegration()
        pr_data = git.fetch_pr(args.repo, args.pr)
        
        analyzer = CodeAnalysis()
        analysis_results = []
        for file in pr_data:
            issues = analyzer.analyze_file(file['content'], file['filename'])
            analysis_results.append({'filename': file['filename'], 'issues': issues})
        
        feedback_gen = FeedbackGeneration()
        report = feedback_gen.generate_feedback(analysis_results)
        print(report)

if __name__ == "__main__":
    main()