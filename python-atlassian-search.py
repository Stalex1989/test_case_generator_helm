"""
Atlassian Search & Test Case Generator
A local Python tool that searches Jira and Confluence, then generates test cases using Claude AI
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import requests
from requests.auth import HTTPBasicAuth
import json

app = Flask(__name__)
CORS(app)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Atlassian Search & Test Case Generator</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 32px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .credentials-box {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }
        input[type="text"], input[type="email"], input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .search-box input {
            flex: 1;
        }
        button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #5568d3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .results-section {
            margin-top: 30px;
        }
        .results-box {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .result-item {
            background: white;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 10px;
            border-left: 4px solid #667eea;
        }
        .result-title {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 5px;
        }
        .result-description {
            color: #666;
            font-size: 14px;
            margin-bottom: 8px;
        }
        .result-meta {
            font-size: 12px;
            color: #999;
        }
        .error {
            background: #f8d7da;
            border: 2px solid #f5c6cb;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .success {
            background: #d4edda;
            border: 2px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .test-cases {
            background: #e7f3ff;
            border: 2px solid #2196F3;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        .test-cases pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Atlassian Search & Test Case Generator</h1>
        <p class="subtitle">Search Jira & Confluence, then generate AI-powered test cases</p>

        <div class="credentials-box">
            <h3 style="margin-bottom: 15px;">⚙️ Configuration</h3>
            <div class="grid">
                <div class="form-group">
                    <label>Atlassian Email:</label>
                    <input type="email" id="email" placeholder="your-email@example.com">
                </div>
                <div class="form-group">
                    <label>API Token:</label>
                    <input type="password" id="token" placeholder="Your Atlassian API token">
                </div>
            </div>
            <div class="form-group">
                <label>Atlassian Base URL:</label>
                <input type="text" id="baseUrl" value="https://edocgroup.atlassian.net" placeholder="https://your-domain.atlassian.net">
            </div>
            <p style="font-size: 12px; color: #856404; margin-top: 10px;">
                💡 Create API token at: <a href="https://id.atlassian.com/manage-profile/security/api-tokens" target="_blank">Atlassian Settings</a>
            </p>
        </div>

        <div class="form-group">
            <label>🔎 Search Query:</label>
            <div class="search-box">
                <input type="text" id="searchQuery" placeholder="e.g., shopping list feature" onkeypress="if(event.key==='Enter') searchAtlassian()">
                <button onclick="searchAtlassian()" id="searchBtn">Search</button>
            </div>
        </div>

        <div id="errorMsg" style="display:none;" class="error"></div>
        <div id="successMsg" style="display:none;" class="success"></div>

        <div id="results" style="display:none;" class="results-section">
            <h3>📋 Jira Results (<span id="jiraCount">0</span>)</h3>
            <div id="jiraResults" class="results-box"></div>

            <h3>📄 Confluence Results (<span id="confluenceCount">0</span>)</h3>
            <div id="confluenceResults" class="results-box"></div>

            <div style="text-align: center; margin-top: 30px;">
                <button onclick="generateTestCases()" id="generateBtn" style="font-size: 18px; padding: 15px 40px; background: #28a745;">
                    ✨ Generate Test Cases with AI
                </button>
            </div>
        </div>

        <div id="testCases" style="display:none;" class="test-cases">
            <h3 style="margin-bottom: 15px;">✅ Generated Test Cases</h3>
            <pre id="testCasesContent"></pre>
            <button onclick="copyTestCases()" style="margin-top: 15px; background: #6c757d;">📋 Copy to Clipboard</button>
        </div>
    </div>

    <script>
        let searchResults = null;

        function showError(msg) {
            document.getElementById('errorMsg').textContent = msg;
            document.getElementById('errorMsg').style.display = 'block';
            document.getElementById('successMsg').style.display = 'none';
        }

        function showSuccess(msg) {
            document.getElementById('successMsg').textContent = msg;
            document.getElementById('successMsg').style.display = 'block';
            document.getElementById('errorMsg').style.display = 'none';
        }

        function hideMessages() {
            document.getElementById('errorMsg').style.display = 'none';
            document.getElementById('successMsg').style.display = 'none';
        }

        async function searchAtlassian() {
            const email = document.getElementById('email').value;
            const token = document.getElementById('token').value;
            const baseUrl = document.getElementById('baseUrl').value;
            const query = document.getElementById('searchQuery').value;

            if (!email || !token || !query) {
                showError('Please fill in all fields');
                return;
            }

            hideMessages();
            const searchBtn = document.getElementById('searchBtn');
            searchBtn.disabled = true;
            searchBtn.innerHTML = '<span class="spinner"></span>Searching...';

            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ email, token, baseUrl, query })
                });

                const data = await response.json();

                if (!response.ok) {
                    showError(data.error || 'Search failed');
                    return;
                }

                searchResults = data;
                displayResults(data);
                showSuccess(`Found ${data.jira.length} Jira tickets and ${data.confluence.length} Confluence pages`);

            } catch (err) {
                showError('Search failed: ' + err.message);
            } finally {
                searchBtn.disabled = false;
                searchBtn.innerHTML = 'Search';
            }
        }

        function displayResults(data) {
            document.getElementById('jiraCount').textContent = data.jira.length;
            document.getElementById('confluenceCount').textContent = data.confluence.length;

            const jiraHtml = data.jira.map(issue => `
                <div class="result-item">
                    <div class="result-title">${issue.key}: ${issue.fields.summary}</div>
                    <div class="result-description">${(issue.fields.description || 'No description').substring(0, 200)}...</div>
                    <div class="result-meta">Status: ${issue.fields.status.name} | Type: ${issue.fields.issuetype.name}</div>
                </div>
            `).join('') || '<p>No Jira tickets found</p>';

            const confluenceHtml = data.confluence.map(page => `
                <div class="result-item">
                    <div class="result-title">${page.title}</div>
                    <div class="result-meta">Type: ${page.type}</div>
                </div>
            `).join('') || '<p>No Confluence pages found</p>';

            document.getElementById('jiraResults').innerHTML = jiraHtml;
            document.getElementById('confluenceResults').innerHTML = confluenceHtml;
            document.getElementById('results').style.display = 'block';
            document.getElementById('testCases').style.display = 'none';
        }

        async function generateTestCases() {
            if (!searchResults) {
                showError('No search results to generate test cases from');
                return;
            }

            hideMessages();
            const generateBtn = document.getElementById('generateBtn');
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<span class="spinner"></span>Generating Test Cases...';

            try {
                const response = await fetch('/generate-tests', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ 
                        query: document.getElementById('searchQuery').value,
                        results: searchResults 
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    showError(data.error || 'Test case generation failed');
                    return;
                }

                document.getElementById('testCasesContent').textContent = data.testCases;
                document.getElementById('testCases').style.display = 'block';
                showSuccess('Test cases generated successfully!');

            } catch (err) {
                showError('Generation failed: ' + err.message);
            } finally {
                generateBtn.disabled = false;
                generateBtn.innerHTML = '✨ Generate Test Cases with AI';
            }
        }

        function copyTestCases() {
            const text = document.getElementById('testCasesContent').textContent;
            navigator.clipboard.writeText(text).then(() => {
                showSuccess('Test cases copied to clipboard!');
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.json
        email = data['email']
        token = data['token']
        base_url = data['baseUrl'].rstrip('/')
        query = data['query']
        
        auth = HTTPBasicAuth(email, token)
        
        # Search Jira
        jira_results = []
        try:
            jira_url = f"{base_url}/rest/api/3/search"
            jira_params = {'jql': f'text ~ "{query}"', 'maxResults': 10}
            jira_response = requests.get(jira_url, auth=auth, params=jira_params, timeout=10)
            
            if jira_response.status_code == 200:
                jira_data = jira_response.json()
                jira_results = jira_data.get('issues', [])
        except Exception as e:
            print(f"Jira search error: {e}")
        
        # Search Confluence
        confluence_results = []
        try:
            confluence_url = f"{base_url}/wiki/rest/api/content/search"
            confluence_params = {'cql': f'text ~ "{query}"', 'limit': 10}
            confluence_response = requests.get(confluence_url, auth=auth, params=confluence_params, timeout=10)
            
            if confluence_response.status_code == 200:
                confluence_data = confluence_response.json()
                confluence_results = confluence_data.get('results', [])
        except Exception as e:
            print(f"Confluence search error: {e}")
        
        return jsonify({
            'jira': jira_results,
            'confluence': confluence_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-tests', methods=['POST'])
def generate_tests():
    try:
        data = request.json
        query = data['query']
        results = data['results']
        
        # Build context from results
        context = f"Search Query: '{query}'\n\n"
        
        if results['jira']:
            context += "JIRA TICKETS:\n"
            for issue in results['jira'][:5]:
                context += f"\n- {issue['key']}: {issue['fields']['summary']}\n"
                context += f"  Description: {issue['fields'].get('description', 'No description')}\n"
                context += f"  Status: {issue['fields']['status']['name']}\n"
        
        if results['confluence']:
            context += "\n\nCONFLUENCE PAGES:\n"
            for page in results['confluence'][:5]:
                context += f"\n- {page['title']}\n"
        
        # Call Claude API
        claude_response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'Content-Type': 'application/json',
                'x-api-key': 'YOUR_CLAUDE_API_KEY_HERE'  # User needs to add their key
            },
            json={
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': 4000,
                'messages': [{
                    'role': 'user',
                    'content': f"""Based on the following information from Jira and Confluence, generate comprehensive test cases for the "{query}" feature.

{context}

Please provide test cases with:
1. Test Case ID and Title
2. Preconditions
3. Test Steps (numbered)
4. Expected Results
5. Priority (High/Medium/Low)

Format them clearly and professionally."""
                }]
            },
            timeout=60
        )
        
        claude_data = claude_response.json()
        test_cases = ''.join([
            item['text'] for item in claude_data.get('content', [])
            if item.get('type') == 'text'
        ])
        
        return jsonify({'testCases': test_cases})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Atlassian Search & Test Case Generator")
    print("="*60)
    print("\n📝 Setup Instructions:")
    print("1. Install dependencies: pip install flask flask-cors requests")
    print("2. Get your Atlassian API token from:")
    print("   https://id.atlassian.com/manage-profile/security/api-tokens")
    print("3. Add your Claude API key in the code (line 297)")
    print("4. Open http://localhost:5000 in your browser")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, port=5000)
