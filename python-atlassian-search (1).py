"""
Atlassian Search Tool (Free Version)
Searches Jira and Confluence - paste results to Claude chat for test case generation
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
    <title>Atlassian Search Tool</title>
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
        .info-box {
            background: #d1ecf1;
            border: 2px solid #17a2b8;
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
        .summary-box {
            background: #e7f3ff;
            border: 2px solid #2196F3;
            border-radius: 8px;
            padding: 20px;
            margin-top: 30px;
        }
        .summary-box textarea {
            width: 100%;
            min-height: 300px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
            resize: vertical;
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
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Atlassian Search Tool</h1>
        <p class="subtitle">Search Jira & Confluence, then use Claude chat for free test case generation</p>

        <div class="info-box">
            <h3 style="margin-bottom: 10px;">💡 How This Works (Free Version)</h3>
            <ol style="margin-left: 20px; line-height: 1.8;">
                <li>Enter your Atlassian credentials below</li>
                <li>Search for your feature (e.g., "shopping list")</li>
                <li>Review the results from Jira and Confluence</li>
                <li>Click "Copy Summary for Claude" button</li>
                <li>Paste the summary in your Claude chat</li>
                <li>Claude will generate test cases for FREE! 🎉</li>
            </ol>
        </div>

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

            <div class="summary-box">
                <h3 style="margin-bottom: 15px;">📝 Summary for Claude</h3>
                <p style="margin-bottom: 10px; color: #666;">Copy this text and paste it in your Claude chat to generate test cases:</p>
                <textarea id="summaryText" readonly></textarea>
                <div class="button-group">
                    <button onclick="copySummary()" style="background: #28a745;">
                        📋 Copy Summary for Claude
                    </button>
                    <button onclick="window.open('https://claude.ai', '_blank')" style="background: #6c757d;">
                        🔗 Open Claude Chat
                    </button>
                </div>
            </div>
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
                generateSummary(query, data);
                showSuccess(`Found ${data.jira.length} Jira tickets and ${data.confluence.length} Confluence pages! Now copy the summary and paste it to Claude.`);

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
        }

        function generateSummary(query, data) {
            let summary = `I searched my Atlassian instance for "${query}" and found the following information. Please generate comprehensive test cases based on this:\n\n`;
            
            summary += `=== JIRA TICKETS (${data.jira.length} found) ===\n\n`;
            
            data.jira.forEach(issue => {
                summary += `Ticket: ${issue.key}\n`;
                summary += `Summary: ${issue.fields.summary}\n`;
                summary += `Description: ${issue.fields.description || 'No description'}\n`;
                summary += `Status: ${issue.fields.status.name}\n`;
                summary += `Type: ${issue.fields.issuetype.name}\n`;
                summary += `Priority: ${issue.fields.priority ? issue.fields.priority.name : 'Not set'}\n`;
                summary += `\n---\n\n`;
            });

            summary += `\n=== CONFLUENCE PAGES (${data.confluence.length} found) ===\n\n`;
            
            data.confluence.forEach(page => {
                summary += `Page: ${page.title}\n`;
                summary += `Type: ${page.type}\n`;
                summary += `\n---\n\n`;
            });

            summary += `\nPlease generate comprehensive test cases including:\n`;
            summary += `1. Test case ID and title\n`;
            summary += `2. Preconditions\n`;
            summary += `3. Test steps (numbered)\n`;
            summary += `4. Expected results\n`;
            summary += `5. Priority level\n`;
            summary += `6. Both positive and negative test scenarios\n`;
            summary += `7. Edge cases\n`;

            document.getElementById('summaryText').value = summary;
        }

        function copySummary() {
            const text = document.getElementById('summaryText').value;
            navigator.clipboard.writeText(text).then(() => {
                showSuccess('✅ Summary copied! Now paste it in your Claude chat to generate test cases.');
            }).catch(() => {
                showError('Failed to copy. Please select and copy manually.');
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
            jira_params = {
                'jql': f'text ~ "{query}"',
                'maxResults': 20,
                'fields': 'summary,description,status,issuetype,priority'
            }
            jira_response = requests.get(jira_url, auth=auth, params=jira_params, timeout=15)
            
            if jira_response.status_code == 200:
                jira_data = jira_response.json()
                jira_results = jira_data.get('issues', [])
            elif jira_response.status_code == 401:
                return jsonify({'error': 'Authentication failed. Check your email and API token.'}), 401
            elif jira_response.status_code == 403:
                return jsonify({'error': 'Access denied. Check your permissions.'}), 403
        except requests.exceptions.Timeout:
            return jsonify({'error': 'Jira search timed out. Try again.'}), 500
        except Exception as e:
            print(f"Jira search error: {e}")
        
        # Search Confluence
        confluence_results = []
        try:
            confluence_url = f"{base_url}/wiki/rest/api/content/search"
            confluence_params = {
                'cql': f'text ~ "{query}"',
                'limit': 20
            }
            confluence_response = requests.get(confluence_url, auth=auth, params=confluence_params, timeout=15)
            
            if confluence_response.status_code == 200:
                confluence_data = confluence_response.json()
                confluence_results = confluence_data.get('results', [])
        except requests.exceptions.Timeout:
            print("Confluence search timed out")
        except Exception as e:
            print(f"Confluence search error: {e}")
        
        return jsonify({
            'jira': jira_results,
            'confluence': confluence_results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Atlassian Search Tool (Free Version)")
    print("="*70)
    print("\n📝 Setup Instructions:")
    print("1. Make sure you installed: pip install flask flask-cors requests")
    print("   (Or use: py -m pip install flask flask-cors requests)")
    print("2. Get your Atlassian API token from:")
    print("   https://id.atlassian.com/manage-profile/security/api-tokens")
    print("3. Open http://localhost:5000 in your browser")
    print("4. Search for features, copy results, paste to Claude chat")
    print("5. Claude generates test cases for FREE!")
    print("\n💡 NO API KEY NEEDED - Use Claude chat for test generation!")
    print("="*70 + "\n")
    
    app.run(debug=True, port=5000)