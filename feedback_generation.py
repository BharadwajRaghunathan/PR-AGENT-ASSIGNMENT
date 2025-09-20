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
        for category, items in issues.items():
            for item in items:
                if 'missing docstring' in item.lower() or 'C0116' in item:
                    suggestions.append("Add docstrings to functions for better readability.")
                if 'unused variable' in item.lower() or 'F841' in item:
                    suggestions.append("Remove unused variables to improve performance.")
                if 'missing whitespace' in item.lower() or 'E231' in item:
                    suggestions.append("Add proper spacing after commas to comply with PEP 8.")
        return suggestions