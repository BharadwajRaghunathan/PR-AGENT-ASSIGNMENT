from flask import Flask, request, jsonify
import os
import json
import threading
import subprocess
from datetime import datetime
from git_integration import GitIntegration
from code_analysis import CodeAnalysis
from feedback_generation import FeedbackGeneration
from inline_comments import InlineCommentGenerator
from dotenv import load_dotenv
import hmac
import hashlib

load_dotenv()

app = Flask(__name__)

class WebhookServer:
    """Enhanced webhook server for CI/CD integration."""
    
    def __init__(self):
        self.app = app
        self.setup_routes()
        print("🚀 PR Review Agent Webhook Server initialized")
        print("📡 Supports: GitHub, GitLab, Bitbucket webhooks")
        
    def setup_routes(self):
        """Setup webhook endpoints for different platforms."""
        
        @self.app.route('/', methods=['GET'])
        def health_check():
            return jsonify({
                'status': 'healthy',
                'service': 'PR Review Agent Webhook Server',
                'timestamp': datetime.now().isoformat(),
                'supported_platforms': ['github', 'gitlab', 'bitbucket'],
                'endpoints': {
                    'github': '/webhook/github',
                    'gitlab': '/webhook/gitlab', 
                    'bitbucket': '/webhook/bitbucket',
                    'generic': '/webhook/generic'
                }
            })
        
        @self.app.route('/webhook/github', methods=['POST'])
        def github_webhook():
            """Handle GitHub webhook events."""
            return self._handle_github_webhook()
        
        @self.app.route('/webhook/gitlab', methods=['POST'])  
        def gitlab_webhook():
            """Handle GitLab webhook events."""
            return self._handle_gitlab_webhook()
        
        @self.app.route('/webhook/bitbucket', methods=['POST'])
        def bitbucket_webhook():
            """Handle Bitbucket webhook events."""
            return self._handle_bitbucket_webhook()
        
        @self.app.route('/webhook/generic', methods=['POST'])
        def generic_webhook():
            """Handle generic CI/CD webhook events."""
            return self._handle_generic_webhook()
        
        @self.app.route('/review', methods=['POST'])
        def manual_review():
            """Manual review endpoint for testing/API access."""
            return self._handle_manual_review()

    def _verify_github_signature(self, payload_body, signature_header):
        """Verify GitHub webhook signature for security."""
        secret = os.getenv('GITHUB_WEBHOOK_SECRET', '')
        if not secret:
            return True  # Skip verification if no secret configured
            
        if not signature_header:
            return False
        
        try:
            hash_object = hmac.new(
                secret.encode('utf-8'),
                payload_body,
                hashlib.sha256
            )
            expected_signature = "sha256=" + hash_object.hexdigest()
            return hmac.compare_digest(expected_signature, signature_header)
        except Exception as e:
            print(f"❌ Signature verification error: {e}")
            return False

    def _handle_github_webhook(self):
        """Process GitHub webhook events."""
        try:
            # Verify signature for security
            signature = request.headers.get('X-Hub-Signature-256')
            if not self._verify_github_signature(request.data, signature):
                print("❌ GitHub webhook signature verification failed")
                return jsonify({'error': 'Invalid signature'}), 403
            
            payload = request.get_json()
            event_type = request.headers.get('X-GitHub-Event')
            
            print(f"📥 Received GitHub webhook: {event_type}")
            
            # Handle pull request events
            if event_type in ['pull_request', 'pull_request_target']:
                action = payload.get('action')
                
                if action in ['opened', 'synchronize', 'reopened']:
                    pr_data = payload.get('pull_request', {})
                    repo_full_name = payload.get('repository', {}).get('full_name')
                    pr_number = pr_data.get('number')
                    
                    print(f"🎯 Processing GitHub PR #{pr_number} in {repo_full_name}")
                    print(f"🔄 Action: {action}")
                    
                    # Process in background thread to avoid timeout
                    thread = threading.Thread(
                        target=self._process_pr_async,
                        args=('github', repo_full_name, pr_number, payload)
                    )
                    thread.daemon = True
                    thread.start()
                    
                    return jsonify({
                        'status': 'accepted',
                        'message': f'PR #{pr_number} queued for review',
                        'repository': repo_full_name
                    })
                else:
                    return jsonify({'status': 'ignored', 'reason': f'Action {action} not processed'})
            
            return jsonify({'status': 'ignored', 'reason': f'Event {event_type} not processed'})
            
        except Exception as e:
            print(f"❌ GitHub webhook error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    def _handle_gitlab_webhook(self):
        """Process GitLab webhook events."""
        try:
            # Verify GitLab token if configured
            token = request.headers.get('X-Gitlab-Token')
            expected_token = os.getenv('GITLAB_WEBHOOK_TOKEN')
            
            if expected_token and token != expected_token:
                print("❌ GitLab webhook token verification failed")
                return jsonify({'error': 'Invalid token'}), 403
            
            payload = request.get_json()
            event_type = payload.get('object_kind')
            
            print(f"📥 Received GitLab webhook: {event_type}")
            
            if event_type == 'merge_request':
                action = payload.get('object_attributes', {}).get('action')
                
                if action in ['open', 'update', 'reopen']:
                    mr_data = payload.get('object_attributes', {})
                    project_path = payload.get('project', {}).get('path_with_namespace')
                    mr_number = mr_data.get('iid')  # GitLab uses 'iid' for MR number
                    
                    print(f"🎯 Processing GitLab MR !{mr_number} in {project_path}")
                    print(f"🔄 Action: {action}")
                    
                    # Process in background thread
                    thread = threading.Thread(
                        target=self._process_pr_async,
                        args=('gitlab', project_path, mr_number, payload)
                    )
                    thread.daemon = True
                    thread.start()
                    
                    return jsonify({
                        'status': 'accepted',
                        'message': f'MR !{mr_number} queued for review',
                        'project': project_path
                    })
                else:
                    return jsonify({'status': 'ignored', 'reason': f'Action {action} not processed'})
            
            return jsonify({'status': 'ignored', 'reason': f'Event {event_type} not processed'})
            
        except Exception as e:
            print(f"❌ GitLab webhook error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    def _handle_bitbucket_webhook(self):
        """Process Bitbucket webhook events."""
        try:
            payload = request.get_json()
            event_type = request.headers.get('X-Event-Key')
            
            print(f"📥 Received Bitbucket webhook: {event_type}")
            
            if event_type in ['pullrequest:created', 'pullrequest:updated']:
                pr_data = payload.get('pullrequest', {})
                repo_full_name = payload.get('repository', {}).get('full_name')
                pr_number = pr_data.get('id')
                
                print(f"🎯 Processing Bitbucket PR #{pr_number} in {repo_full_name}")
                print(f"🔄 Event: {event_type}")
                
                # Process in background thread
                thread = threading.Thread(
                    target=self._process_pr_async,
                    args=('bitbucket', repo_full_name, pr_number, payload)
                )
                thread.daemon = True
                thread.start()
                
                return jsonify({
                    'status': 'accepted', 
                    'message': f'PR #{pr_number} queued for review',
                    'repository': repo_full_name
                })
            
            return jsonify({'status': 'ignored', 'reason': f'Event {event_type} not processed'})
            
        except Exception as e:
            print(f"❌ Bitbucket webhook error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    def _handle_generic_webhook(self):
        """Handle generic CI/CD webhook calls."""
        try:
            payload = request.get_json()
            
            # Expected format for generic webhooks
            platform = payload.get('platform', 'github')
            repository = payload.get('repository')
            pr_number = payload.get('pr_number') or payload.get('merge_request_iid')
            
            if not all([platform, repository, pr_number]):
                return jsonify({
                    'error': 'Missing required fields',
                    'required': ['platform', 'repository', 'pr_number'],
                    'received': payload
                }), 400
            
            print(f"📥 Received generic webhook: {platform}/{repository}/PR#{pr_number}")
            
            # Process in background thread
            thread = threading.Thread(
                target=self._process_pr_async,
                args=(platform, repository, pr_number, payload)
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'status': 'accepted',
                'message': f'PR #{pr_number} queued for review',
                'platform': platform,
                'repository': repository
            })
            
        except Exception as e:
            print(f"❌ Generic webhook error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    def _handle_manual_review(self):
        """Handle manual review requests via API."""
        try:
            data = request.get_json()
            
            platform = data.get('platform', 'github')
            repository = data.get('repository')
            pr_number = data.get('pr_number')
            post_comments = data.get('post_comments', False)
            
            if not all([repository, pr_number]):
                return jsonify({
                    'error': 'Missing required fields',
                    'required': ['repository', 'pr_number'],
                    'optional': ['platform', 'post_comments']
                }), 400
            
            print(f"🎯 Manual review requested: {platform}/{repository}/PR#{pr_number}")
            
            # Process synchronously for manual requests
            result = self._process_pr_sync(platform, repository, pr_number, post_comments)
            
            return jsonify({
                'status': 'completed',
                'result': result,
                'platform': platform,
                'repository': repository,
                'pr_number': pr_number
            })
            
        except Exception as e:
            print(f"❌ Manual review error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    def _process_pr_async(self, platform, repository, pr_number, webhook_payload=None):
        """Process PR review in background thread."""
        try:
            print(f"🔄 Starting async review: {platform}/{repository}/PR#{pr_number}")
            
            result = self._process_pr_sync(platform, repository, pr_number, post_comments=True)
            
            print(f"✅ Completed async review: {platform}/{repository}/PR#{pr_number}")
            print(f"📊 Found {result.get('total_issues', 0)} total issues")
            
        except Exception as e:
            print(f"❌ Async review failed: {platform}/{repository}/PR#{pr_number}: {str(e)}")

    def _process_pr_sync(self, platform, repository, pr_number, post_comments=False):
        """Synchronously process PR review."""
        try:
            # Initialize integrations
            git_integration = GitIntegration(server_type=platform)
            analyzer = CodeAnalysis()
            inline_generator = InlineCommentGenerator()
            
            # Fetch PR data
            print(f"📥 Fetching {platform} PR #{pr_number} from {repository}...")
            pr_files = git_integration.fetch_pr(repository, pr_number)
            
            if not pr_files:
                return {'error': 'No files found in PR', 'total_issues': 0}
            
            # Analyze each file
            analysis_results = []
            total_issues = 0
            
            for file_data in pr_files:
                if not file_data['filename'].endswith('.py'):
                    continue  # Skip non-Python files
                
                print(f"🔍 Analyzing {file_data['filename']}...")
                issues = analyzer.analyze_file(file_data['content'], file_data['filename'])
                inline_comments = inline_generator.generate_inline_comments(file_data, issues)
                
                file_total_issues = sum(len(issue_list) for issue_list in issues.values())
                total_issues += file_total_issues
                
                analysis_results.append({
                    'filename': file_data['filename'],
                    'issues': issues,
                    'inline_comments': inline_comments,
                    'issue_count': file_total_issues
                })
                
                print(f"📊 {file_data['filename']}: {file_total_issues} issues found")
            
            # Generate comprehensive feedback
            feedback_gen = FeedbackGeneration()
            report = feedback_gen.generate_comprehensive_feedback(analysis_results, pr_files)
            
            # Post comments back to PR if requested
            if post_comments and total_issues > 0:
                try:
                    comment_posted = git_integration.post_review_comment(
                        repository, pr_number, report
                    )
                    if comment_posted:
                        print("✅ Posted comprehensive review to PR")
                    else:
                        print("⚠️  Failed to post review comment")
                except Exception as e:
                    print(f"⚠️  Comment posting failed: {str(e)}")
            
            return {
                'total_issues': total_issues,
                'files_analyzed': len(analysis_results),
                'report': report,
                'analysis_results': analysis_results
            }
            
        except Exception as e:
            print(f"❌ PR processing error: {str(e)}")
            raise

    def run(self, host='0.0.0.0', port=5001, debug=False):
        """Run the webhook server."""
        print(f"🚀 Starting PR Review Agent Webhook Server...")
        print(f"🌐 Server will run on http://{host}:{port}")
        print(f"📡 Webhook endpoints:")
        print(f"   • GitHub:    http://{host}:{port}/webhook/github")
        print(f"   • GitLab:    http://{host}:{port}/webhook/gitlab") 
        print(f"   • Bitbucket: http://{host}:{port}/webhook/bitbucket")
        print(f"   • Generic:   http://{host}:{port}/webhook/generic")
        print(f"   • Manual:    http://{host}:{port}/review")
        print(f"   • Health:    http://{host}:{port}/")
        print()
        
        self.app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    webhook_server = WebhookServer()
    webhook_server.run()
