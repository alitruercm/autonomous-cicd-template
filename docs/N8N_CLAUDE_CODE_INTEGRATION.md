# n8n + Claude Code Integration Guide

A comprehensive guide to enable Claude Code to access, analyze, debug, and modify n8n workflows programmatically across multiple environments.

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [Multi-Environment Configuration](#multi-environment-configuration)
3. [CLI Commands Reference](#cli-commands-reference)
4. [Usage Examples](#usage-examples)
5. [Workflow Modification Patterns](#workflow-modification-patterns)
6. [Debugging Workflows](#debugging-workflows)
7. [Troubleshooting](#troubleshooting)

---

## Initial Setup

### Step 1: Enable n8n API

1. Open your n8n instance (e.g., `http://localhost:5678`)
2. Go to **Settings** → **API**
3. Enable API access
4. Click **Create API Key**
5. Copy the generated API key (save it securely - it won't be shown again)

### Step 2: Configure Environment Variables

Copy `.env.example` to `.env` and add your n8n credentials:

```bash
# Default n8n environment
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your_api_key_here
```

### Step 3: Install Dependencies

The n8n CLI helper requires `axios` and `dotenv`:

```bash
npm install axios dotenv
```

---

## Multi-Environment Configuration

To work with multiple n8n instances (local, staging, production), configure named environments in your `.env` file:

```bash
# Default environment (used when no -e flag specified)
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your_default_key

# Local development
N8N_LOCAL_URL=http://localhost:5678
N8N_LOCAL_API_KEY=your_local_key

# Production
N8N_PROD_URL=https://n8n.yourcompany.com
N8N_PROD_API_KEY=your_prod_key

# Staging
N8N_STAGING_URL=https://staging-n8n.yourcompany.com
N8N_STAGING_API_KEY=your_staging_key

# Client-specific (any name works)
N8N_CLIENT1_URL=https://client1-n8n.example.com
N8N_CLIENT1_API_KEY=your_client1_key
```

### Naming Convention

The `-e <name>` flag looks for these environment variables:
- `N8N_<NAME>_URL` - The n8n instance URL
- `N8N_<NAME>_API_KEY` - The API key for that instance

| Flag | URL Variable | API Key Variable |
|------|--------------|------------------|
| `-e local` | `N8N_LOCAL_URL` | `N8N_LOCAL_API_KEY` |
| `-e prod` | `N8N_PROD_URL` | `N8N_PROD_API_KEY` |
| `-e staging` | `N8N_STAGING_URL` | `N8N_STAGING_API_KEY` |
| `-e myserver` | `N8N_MYSERVER_URL` | `N8N_MYSERVER_API_KEY` |

---

## CLI Commands Reference

```bash
Usage: node scripts/n8n-cli.js [-e <env>] <command> [arguments]
```

### Environment Commands

| Command | Description |
|---------|-------------|
| `envs` | List all configured environments |

### Workflow Commands

| Command | Description |
|---------|-------------|
| `workflows` | List all workflows |
| `workflow <id>` | Get workflow details and nodes |
| `active` | List only active workflows |
| `search <term>` | Search workflows by name |

### Execution Commands

| Command | Description |
|---------|-------------|
| `executions [workflowId]` | List recent executions |
| `execution <id>` | Get execution summary with nodes |
| `nodes <executionId>` | Get all node outputs (detailed) |
| `node <execId> <nodeName>` | Get specific node output |
| `errors <executionId>` | Show only errors from execution |

### Action Commands

| Command | Description |
|---------|-------------|
| `trigger <workflowId> [json]` | Trigger workflow webhook |
| `credentials` | List configured credentials |

---

## Usage Examples

### Basic Usage (Default Environment)

```bash
# List all workflows
node scripts/n8n-cli.js workflows

# Get workflow details
node scripts/n8n-cli.js workflow Y6eWdKJoHaeWZgMX

# List recent executions
node scripts/n8n-cli.js executions

# Debug an execution
node scripts/n8n-cli.js execution 920
```

### Multi-Environment Usage

```bash
# List workflows in production
node scripts/n8n-cli.js -e prod workflows

# Check errors in staging
node scripts/n8n-cli.js -e staging errors 123

# Trigger workflow in local environment
node scripts/n8n-cli.js -e local trigger abc123 '{"test": true}'

# List all configured environments
node scripts/n8n-cli.js envs
```

### Debugging Workflow Executions

```bash
# Step 1: Get execution overview
node scripts/n8n-cli.js execution 920

# Step 2: Find failing nodes
node scripts/n8n-cli.js errors 920

# Step 3: Examine all node outputs
node scripts/n8n-cli.js nodes 920

# Step 4: Check specific node
node scripts/n8n-cli.js node 920 "OpenAI"
```

---

## Workflow Modification Patterns

### Basic Pattern: Update a Code Node

Create a script to modify workflow nodes programmatically:

```javascript
#!/usr/bin/env node
require('dotenv').config();
const axios = require('axios');

// Select environment
const envName = process.env.N8N_ENV || '';
const prefix = envName ? envName.toUpperCase() + '_' : '';
const N8N_BASE_URL = process.env[`N8N_${prefix}URL`] || process.env.N8N_BASE_URL;
const N8N_API_KEY = process.env[`N8N_${prefix}API_KEY`] || process.env.N8N_API_KEY;
const WORKFLOW_ID = 'YOUR_WORKFLOW_ID';

const api = axios.create({
  baseURL: N8N_BASE_URL + '/api/v1',
  headers: {
    'X-N8N-API-KEY': N8N_API_KEY,
    'Content-Type': 'application/json'
  }
});

const NEW_CODE = `// Your new code here
const input = $input.first().json;
return [{ json: { result: 'success' } }];
`;

async function updateWorkflow() {
  // Get workflow
  const { data: workflow } = await api.get(`/workflows/${WORKFLOW_ID}`);

  // Modify nodes
  workflow.nodes = workflow.nodes.map(node => {
    if (node.name === 'Your Node Name') {
      node.parameters.jsCode = NEW_CODE;
    }
    return node;
  });

  // Save workflow
  await api.put(`/workflows/${WORKFLOW_ID}`, {
    name: workflow.name,
    nodes: workflow.nodes,
    connections: workflow.connections,
    settings: workflow.settings,
    staticData: workflow.staticData
  });

  console.log('Workflow updated successfully!');
}

updateWorkflow().catch(console.error);
```

---

## Debugging Workflows

### Common Debugging Steps

1. **Check execution status**
   ```bash
   node scripts/n8n-cli.js execution <id>
   ```

2. **Find failing nodes**
   ```bash
   node scripts/n8n-cli.js errors <id>
   ```

3. **Examine node outputs**
   ```bash
   node scripts/n8n-cli.js nodes <id>
   ```

4. **Check specific node**
   ```bash
   node scripts/n8n-cli.js node <id> "Node Name"
   ```

### Debug Code in Nodes

Add console.log statements to workflow code nodes:

```javascript
// In your n8n Code node
console.log('=== DEBUG INFO ===');
console.log('Input data:', JSON.stringify($input.first().json, null, 2));

const result = processData($input.first().json);

console.log('Output:', JSON.stringify(result, null, 2));
return [{ json: result }];
```

---

## Troubleshooting

### "N8N_API_KEY not set"

Generate an API key:
1. Go to n8n Settings → API
2. Enable API access
3. Create new API key
4. Add to `.env` file

### "Request failed with status code 401"

API key is invalid or expired. Generate a new one.

### "Request failed with status code 404"

- Check N8N_BASE_URL is correct
- Verify workflow/execution ID exists
- Ensure n8n is running

### "ECONNREFUSED"

n8n is not running. Start it with:
```bash
n8n start
```

### Environment Not Found

Ensure your `.env` has the correct format:
```bash
N8N_<NAME>_URL=https://your-n8n-url.com
N8N_<NAME>_API_KEY=your_api_key
```

---

## Quick Reference Card

| Command | Description |
|---------|-------------|
| `envs` | List configured environments |
| `workflows` | List all workflows |
| `workflow <id>` | Get workflow details |
| `executions [wfId]` | List recent executions |
| `execution <id>` | Get execution details |
| `nodes <id>` | All node outputs |
| `node <id> <name>` | Specific node output |
| `errors <id>` | Only failed nodes |
| `trigger <id> [json]` | Trigger webhook |
| `active` | List active workflows |
| `search <term>` | Search workflows |
| `credentials` | List credentials |

**Environment flag:** `-e <name>` (e.g., `-e prod`, `-e staging`)
