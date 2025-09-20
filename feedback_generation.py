class FeedbackGeneration:
    """Module for feedback generation with AI suggestions and scoring (AI, Backend tech stack)."""
    def generate_feedback(self, analysis_results):
        """Generates report with score and suggestions."""
        report = "PR Review Feedback:\n"
        total_issues = 0
        all_issues = {}  # Aggregate for suggestions
        for result in analysis_results:
            filename = result['filename']
            issues = result['issues']
            report += f"\nFile: {filename}\n"
            for category, items in issues.items():
                for item in items:
                    report += f"- {category.capitalize()}: {item}\n"
                    total_issues += 1
                all_issues[category] = all_issues.get(category, []) + items
        
        # Scoring
        score = max(0, 100 - (total_issues * 5))
        report += f"\nPR Score: {score}/100\n"
        
        # AI Suggestions (rule-based; use CodeMate Extension for real AI)
        suggestions = self._get_ai_suggestions(all_issues)
        report += "\nRecommendations:\n"
        for sug in suggestions:
            report += f"- {sug}\n"
        
        return report
    
    def _get_ai_suggestions(self, issues):
        """AI-driven suggestions (simulate with rules; integrate CodeMate AI)."""
        suggestions = []
        if issues.get('standards'):
            if any('missing docstring' in item for item in issues['standards']):
                suggestions.append("Add docstrings for readability.")
        if issues.get('bugs'):
            if any('unused variable' in item for item in issues['bugs']):
                suggestions.append("Remove unused variables for performance.")
        # Extend with CodeMate Extension for more (e.g., security checks)
        return suggestions