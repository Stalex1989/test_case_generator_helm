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

def extract_text_from_adf(adf_doc):
    """Extract plain text from Atlassian Document Format"""
    if not adf_doc or not isinstance(adf_doc, dict):
        return ""
    
    text_parts = []
    
    def traverse(node):
        if isinstance(node, dict):
            # Extract text content
            if node.get('type') == 'text':
                text_parts.append(node.get('text', ''))
            
            # Traverse content array
            if 'content' in node and isinstance(node['content'], list):
                for child in node['content']:
                    traverse(child)
        elif isinstance(node, list):
            for item in node:
                traverse(item)
    
    traverse(adf_doc)
    return ' '.join(text_parts)

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
        .badge {
            background: #28a745;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-left: 8px;
        }
        .badge-high {
            background: #007bff;
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
                <input type="text" id="searchQuery" placeholder="e.g., shopping list OR CD-27453" onkeypress="if(event.key==='Enter') searchAtlassian()">
                <button onclick="searchAtlassian()" id="searchBtn">Search</button>
            </div>
            <p style="font-size: 12px; color: #666; margin-top: 5px;">
                💡 Tip: You can search by keywords or by ticket ID (e.g., "CD-27453")
            </p>
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

            // Display Jira results
            let jiraHtml = '';
            if (data.jira && data.jira.length > 0) {
                data.jira.forEach(issue => {
                    // Use extracted description text if available
                    let descText = issue.fields.description_text || 'No description';
                    
                    if (descText && descText.length > 200) {
                        descText = descText.substring(0, 200) + '...';
                    }
                    
                    jiraHtml += `
                        <div class="result-item">
                            <div class="result-title">${issue.key}: ${issue.fields.summary || 'No summary'}</div>
                            <div class="result-description">${descText}</div>
                            <div class="result-meta">
                                Status: ${issue.fields.status ? issue.fields.status.name : 'Unknown'} | 
                                Type: ${issue.fields.issuetype ? issue.fields.issuetype.name : 'Unknown'}
                            </div>
                        </div>
                    `;
                });
            } else {
                jiraHtml = '<p>No Jira tickets found</p>';
            }

            document.getElementById('jiraResults').innerHTML = jiraHtml;

            // Display Confluence results
            const query = document.getElementById('searchQuery').value.toLowerCase();
            let confluenceHtml = '';
            
            if (data.confluence && data.confluence.length > 0) {
                data.confluence.forEach(page => {
                    const title = page.title.toLowerCase();
                    let badge = '';
                    
                    if (title === query) {
                        badge = '<span class="badge">EXACT MATCH</span>';
                    } else if (title.includes(query)) {
                        badge = '<span class="badge badge-high">HIGH RELEVANCE</span>';
                    }
                    
                    confluenceHtml += `
                        <div class="result-item">
                            <div class="result-title">${page.title}${badge}</div>
                            <div class="result-meta">Type: ${page.type}</div>
                        </div>
                    `;
                });
            } else {
                confluenceHtml = '<p>No Confluence pages found</p>';
            }

            document.getElementById('confluenceResults').innerHTML = confluenceHtml;
            document.getElementById('results').style.display = 'block';
        }

        function generateSummary(query, data) {
            let summary = `I searched my Atlassian instance for "${query}" and found the following information. Please generate comprehensive test cases based on this:\n\n`;
            
            summary += `=== JIRA TICKETS (${data.jira.length} found) ===\n\n`;
            
            if (data.jira && data.jira.length > 0) {
                data.jira.forEach(issue => {
                    // Use extracted description text if available
                    const descText = issue.fields.description_text || 'No description';
                    
                    summary += `Ticket: ${issue.key}\n`;
                    summary += `Summary: ${issue.fields.summary || 'No summary'}\n`;
                    summary += `Description: ${descText}\n`;
                    summary += `Status: ${issue.fields.status ? issue.fields.status.name : 'Unknown'}\n`;
                    summary += `Type: ${issue.fields.issuetype ? issue.fields.issuetype.name : 'Unknown'}\n`;
                    summary += `Priority: ${issue.fields.priority ? issue.fields.priority.name : 'Not set'}\n`;
                    summary += `\n---\n\n`;
                });
            }

            summary += `\n=== CONFLUENCE PAGES (${data.confluence.length} found) ===\n\n`;
            
            if (data.confluence && data.confluence.length > 0) {
                data.confluence.forEach(page => {
                    summary += `Page: ${page.title}\n`;
                    summary += `Type: ${page.type}\n`;
                    summary += `\n---\n\n`;
                });
            }

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
            
            # Check if query looks like a ticket ID
            is_ticket_id = '-' in query and any(char.isdigit() for char in query)
            
            if is_ticket_id:
                jql_query = f'key = {query} OR key ~ {query}'
            else:
                words = query.split()
                if len(words) > 1:
                    word_queries = [f'text ~ "{word}"' for word in words]
                    jql_query = ' AND '.join(word_queries)
                else:
                    jql_query = f'text ~ "{query}"'
            
            print(f"JQL Query: {jql_query}")
            
            jira_payload = {
                'jql': jql_query,
                'maxResults': 50,
                'fields': ['summary', 'description', 'status', 'issuetype', 'priority', 'key']
            }
            
            jira_response = requests.post(
                jira_url,
                auth=auth,
                json=jira_payload,
                headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                timeout=15
            )
            
            # Fallback to /search/jql if standard endpoint is deprecated
            if jira_response.status_code == 410:
                print("Standard search deprecated, trying /search/jql endpoint...")
                jira_url = f"{base_url}/rest/api/3/search/jql"
                jira_response = requests.post(
                    jira_url,
                    auth=auth,
                    json=jira_payload,
                    headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                    timeout=15
                )
            
            if jira_response.status_code == 200:
                jira_data = jira_response.json()
                all_jira = jira_data.get('issues', [])
                
                # Rank results by relevance for non-ticket searches
                if not is_ticket_id and all_jira:
                    query_lower = query.lower()
                    ranked_jira = []
                    
                    for issue in all_jira:
                        summary = (issue['fields'].get('summary') or '').lower()
                        
                        # Handle description - extract text from ADF or use string
                        desc_field = issue['fields'].get('description')
                        if isinstance(desc_field, dict):
                            description = extract_text_from_adf(desc_field).lower()
                            # Store extracted text back for display
                            issue['fields']['description_text'] = extract_text_from_adf(desc_field)
                        elif isinstance(desc_field, str):
                            description = desc_field.lower()
                            issue['fields']['description_text'] = desc_field
                        else:
                            description = ''
                            issue['fields']['description_text'] = ''
                        
                        score = 0
                        if query_lower == summary:
                            score = 100
                        elif query_lower in summary:
                            score = 90
                        elif description and query_lower in description:
                            score = 70
                        elif all(word in summary or word in description for word in query_lower.split()):
                            score = 50
                        else:
                            score = 30
                        
                        ranked_jira.append((score, issue))
                    
                    ranked_jira.sort(key=lambda x: x[0], reverse=True)
                    jira_results = [r[1] for r in ranked_jira[:25]]
                else:
                    jira_results = all_jira
                    
            elif jira_response.status_code == 401:
                return jsonify({'error': 'Authentication failed. Check your email and API token.'}), 401
            elif jira_response.status_code == 403:
                return jsonify({'error': 'Access denied. Check your permissions.'}), 403
            else:
                print(f"Jira error: {jira_response.status_code} - {jira_response.text}")
                
        except requests.exceptions.Timeout:
            print("Jira search timed out")
        except Exception as e:
            print(f"Jira search error: {e}")
        
        # Search Confluence - use the search endpoint (same as UI)
        confluence_results = []
        try:
            # Use the search endpoint that powers the UI search
            confluence_url = f"{base_url}/wiki/rest/api/search"
            
            print(f"Confluence Search Query: {query}")
            
            confluence_params = {
                'cql': f'type=page AND text ~ "{query}"',
                'limit': 50
            }
            confluence_response = requests.get(confluence_url, auth=auth, params=confluence_params, timeout=15)
            
            if confluence_response.status_code == 200:
                confluence_data = confluence_response.json()
                search_results = confluence_data.get('results', [])
                
                # Extract content items from search results
                all_results = []
                for item in search_results:
                    if 'content' in item:
                        all_results.append(item['content'])
                
                # Simple ranking by title relevance
                query_lower = query.lower()
                ranked_results = []
                
                for result in all_results:
                    title = result.get('title', '').lower()
                    result_type = result.get('type', '')
                    
                    score = 0
                    
                    # Score based on title
                    if query_lower in title:
                        score = 100
                    elif any(word in title for word in query_lower.split()):
                        score = 70
                    else:
                        score = 50
                    
                    # Prefer pages
                    if result_type == 'page':
                        score += 10
                    
                    ranked_results.append((score, result))
                
                # Sort and return
                ranked_results.sort(key=lambda x: x[0], reverse=True)
                confluence_results = [r[1] for r in ranked_results[:50]]
                
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