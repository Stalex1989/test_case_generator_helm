# Atlassian Search & AI Test Case Generator

A local Python web application that searches your Atlassian (Jira & Confluence) instance and helps generate comprehensive test cases using Claude AI - completely free!


## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Atlassian account with API token

### Installation

1. **Clone or download the project**

2. **Install dependencies**
```bash
pip install flask flask-cors requests
```
or
```bash
py -m pip install flask flask-cors requests
```

3. **Get your Atlassian API Token**
   - Visit: https://id.atlassian.com/manage-profile/security/api-tokens
   - Click "Create API token"
   - Copy and save it securely

4. **Run the application**
```bash
python atlassian_search.py
```
or
```bash
py atlassian_search.py
```

5. **Open your browser**
   - Navigate to: http://localhost:5000

## 📖 How to Use

### Step 1: Configure Credentials
- Enter your Atlassian email
- Paste your API token
- Confirm your Atlassian base URL (e.g., `https://yourcompany.atlassian.net`)

### Step 2: Search
- Type your search query (e.g., "shopping list feature", "attached asset", "login bug")
- Click "Search"
- View Jira tickets and Confluence pages results

### Step 3: Generate Test Cases
- Click "Copy Summary for Claude"
- Open Claude chat (claude.ai)
- Paste the summary
- Claude generates comprehensive test cases for FREE!


## 📝 Example Searches

- `shopping list` - Find feature documentation and tickets
- `attached asset` - Search for asset-related pages
- `CD-27453` - Find specific Jira ticket by ID
- `login bug` - Search for login-related issues
- `maintenance template` - Find template documentation


## 🤝 Contributing

This was built during a hackathon. Ideas and improvements welcome!
