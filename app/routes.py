from flask import render_template, request
from app import app
from git_integration import GitIntegration
from code_analysis import CodeAnalysis
from feedback_generation import FeedbackGeneration

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        repo = request.form['repo']
        pr_number = int(request.form['pr'])
        
        git = GitIntegration()
        pr_data = git.fetch_pr(repo, pr_number)
        
        analyzer = CodeAnalysis()
        analysis_results = []
        for file in pr_data:
            issues = analyzer.analyze_file(file['content'], file['filename'])
            analysis_results.append({'filename': file['filename'], 'issues': issues})
        
        feedback_gen = FeedbackGeneration()
        report = feedback_gen.generate_feedback(analysis_results)
        
        return render_template('index.html', report=report)
    
    return render_template('index.html', report=None)