# notion-to-llms-txt

🤖 Convert your Notion workspace exports into AI-friendly LLMS.txt format

## The Problem

When working with AI agents like Claude, ChatGPT, or coding assistants, you often need to explain "where things are" in your Notion workspace. Without context about your documentation structure, AI agents:

- ❌ Can't efficiently navigate your knowledge base
- ❌ Don't know which pages contain relevant information  
- ❌ Waste time with ineffective searches
- ❌ Miss important documentation that could solve problems faster

## The Solution

**notion-to-llms-txt** creates a structured map of your entire Notion workspace that AI agents can instantly understand. Think of it as a "table of contents" optimized for AI consumption.

## What You Get

✅ **Instant workspace overview** - AI agents know exactly what documentation exists  
✅ **Proper page prioritization** - Important pages (larger content) appear first  
✅ **Direct Notion links** - AI can guide you to specific pages when needed  
✅ **Hierarchical structure** - Preserves your workspace organization  

## Installation

```bash
uv tool install notion-to-llms-txt
```

## Usage

### Step 1: Export from Notion

1. Go to your Notion workspace
2. Click **Settings & members** → **Settings** → **Export content**
3. Choose **Export format: Markdown & CSV**
4. Click **Export** and download the ZIP file
5. Extract the ZIP to a folder (e.g., `/Users/you/notion-export/`)

### Step 2: Generate LLMS.txt

```bash
notion-to-llms-txt /path/to/extracted/notion-export --workspace your-workspace-name
```

For more options:
```bash
notion-to-llms-txt --help
```

### Step 3: What You Get

The tool generates a `notion-llms.txt` file like this:

```markdown
# Notion Workspace

> Notion page structure and links overview

## Projects
- [AI Development Guidelines](https://notion.so/your-workspace/abc123...): Complete guide for AI project workflows
- [Product Roadmap 2025](https://notion.so/your-workspace/def456...): Strategic planning and feature priorities
- [Engineering Standards](https://notion.so/your-workspace/ghi789...): Code review and deployment processes

## Team Documentation  
- [Onboarding Checklist](https://notion.so/your-workspace/jkl012...): New team member setup guide
- [Meeting Notes Archive](https://notion.so/your-workspace/mno345...): Historical meeting records and decisions
```

## Recommended Usage

### 🎯 Share with AI Agents

1. **Upload to your favorite AI agent** (Claude, ChatGPT, etc.)
2. **Include in your prompts**: "Here's my workspace structure: [attach notion-llms.txt]"
3. **Place in Notion**: Create a "AI Agent Resources" page and paste the content

### 💡 Example Conversations

**Before notion-to-llms-txt:**
> "Can you help me find our deployment process documentation?"
> 
> *AI: "I don't have access to your Notion workspace. Could you search for deployment-related pages?"*

**After notion-to-llms-txt:**
> "Can you help me find our deployment process documentation?" [includes LLMS.txt]
> 
> *AI: "Based on your workspace structure, check the 'Engineering Standards' page at https://notion.so/your-workspace/ghi789... - it likely contains your deployment processes."*

### 🔄 Keep It Updated

Re-run the tool whenever you:
- Add major new pages or sections
- Reorganize your workspace structure  
- Want to refresh AI agent knowledge

## What is LLMS.txt?

[LLMS.txt](https://llmstxt.org/) is a proposed standard for providing structured information to Large Language Models. It's like a `robots.txt` for AI - a simple way to help AI agents understand your content structure.

## Requirements

- Python 3.11+
- UV package manager  
- Notion workspace with export access

## Development

See [CLAUDE.md](CLAUDE.md) for development context and contributing guidelines.

## License

Apache 2.0 - see [LICENSE](LICENSE) for details.