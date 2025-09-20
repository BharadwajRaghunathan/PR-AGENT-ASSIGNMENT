class FeedbackGeneration:
    """Module for feedback generation with AI suggestions and scoring (AI, Backend tech stack)."""
    def generate_feedback(self, analysis_results):
        """Generates report with score and suggestions."""
        report = "PR Review Feedback:\n"
        total_issues = 0
        all_issues = {}
        for result in analysis_results:
            filename = result['filename']
            issues = result['issues']
            report += f"\nFile: {filename}\n"
            if not any(issues.values()):
                report += "- No issues detected\n"
            for category, items in issues.items():
                for item in items:
                    report += f"- {category.capitalize()}: {item}\n"
                    total_issues += 1
                all_issues[category] = all_issues.get(category, []) + items
        
        # Scoring
        score = max(0, 100 - (total_issues * 5))
        report += f"\nPR Score: {score}/100\n"
        
        # AI Suggestions
        suggestions = self._get_ai_suggestions(all_issues)
        report += "\nRecommendations:\n"
        if suggestions:
            for sug in suggestions:
                report += f"- {sug}\n"
        else:
            report += "- No additional recommendations.\n"
        
        return report
    
    def _get_ai_suggestions(self, issues):
        """AI-driven suggestions (simulate with rules; integrate CodeMate AI)."""
        suggestions = []
        if issues.get('standards'):
            if any('missing docstring' in item.lower() or 'E231' in item for item in issues['standards']):
                suggestions.append("Add docstrings to functions for better readability.")
        if issues.get('bugs'):
            if any('unused variable' in item.lower() or 'F841' in item for item in issues['bugs']):
                suggestions.append("Remove unused variables to improve performance.")
        return suggestions