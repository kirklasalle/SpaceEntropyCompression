# Web Search MCP Server

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\web_search_mcp\readme.md #api #documentation #pytorch #testing #transformer #web_interface  
**Category:** Documentation  
**Status:** Active

This MCP (Model Context Protocol) server provides comprehensive web search capabilities for AI assistants, featuring Google search with advanced operators, DuckDuckGo integration, and intelligent content extraction.

## Features

### 🔍 **Comprehensive Search Engines**

- **Google Search** with full operator support (site:, filetype:, intitle:, etc.)
- **DuckDuckGo Search** for privacy-focused searching
- **Dual Search Mode** combining results from both engines

### 🛠️ **Advanced Tools**

1. **`web_search`** - Perform comprehensive web search with optional advanced operators
2. **`fetch_webpage`** - Extract and parse content from specific URLs
3. **`search_with_filters`** - Pre-configured filters for academic, technical, news content
4. **`get_search_suggestions`** - Query optimization and search suggestions
5. **`bulk_url_fetch`** - Efficiently fetch content from multiple URLs

### ⚡ **Google Search Operators Supported**

- `site:domain.com` - Search within specific sites
- `filetype:pdf` - Search for specific file types
- `intitle:"phrase"` - Search in page titles
- `inurl:keyword` - Search in URLs
- `"exact phrase"` - Exact phrase matching
- `-excluded` - Exclude terms
- `after:YYYY-MM-DD` - Results after date
- `before:YYYY-MM-DD` - Results before date
- `related:site.com` - Find related sites
- `cache:url` - View cached versions

### 🎯 **Smart Filters**

- **Academic**: Focuses on .edu, .org, and scholarly sources
- **Technical**: Targets developer documentation and forums
- **News**: Searches reputable news sources
- **Documentation**: Finds official docs and guides
- **Tutorials**: Optimizes for how-to and learning content

## Setup

1. **Install Dependencies:**

```bash
cd .mcp/web-search-mcp
pip install -r requirements.txt
```

2. **Configure VS Code MCP:**
The server is pre-configured in `.vscode/mcp.json` with proper MCP protocol integration.

3. **Test Installation:**

```bash
python server.py
```

## Tool Usage Examples

### Basic Web Search

```json
{
  "tool": "web_search",
  "query": "Python machine learning tutorial",
  "num_results": 10,
  "search_engine": "both"
}
```

### Advanced Search with Operators

```json
{
  "tool": "web_search",
  "query": "neural networks",
  "operators": {
    "site": "github.com",
    "filetype": "py",
    "after": "2023-01-01"
  }
}
```

### Filtered Search

```json
{
  "tool": "search_with_filters",
  "query": "transformer architecture",
  "filter_type": "academic",
  "num_results": 8
}
```

### Fetch Webpage Content

```json
{
  "tool": "fetch_webpage",
  "url": "https://example.com/article"
}
```

### Get Search Suggestions

```json
{
  "tool": "get_search_suggestions",
  "query": "pytorch optimization"
}
```

## Response Format

All tools return structured JSON with:

- **Search Results**: Title, URL, snippet, source, citation
- **Metadata**: Query info, timestamps, result counts
- **Citations**: Properly formatted academic-style citations
- **Error Handling**: Graceful degradation with error messages

## Rate Limiting

- **30 requests per minute** (configurable)
- **Burst protection** for rapid consecutive requests
- **Automatic backoff** for rate limit protection

## Privacy & Compliance

- **No personal data storage**
- **Respectful crawling** with proper delays
- **User-Agent headers** for transparency
- **Terms of service compliance** for all search engines

## Integration

The server automatically integrates with VS Code through the MCP protocol, providing:

- **Tool Discovery**: All tools automatically appear in VS Code
- **Type Safety**: Full JSON schema validation
- **Error Reporting**: Detailed error messages and logs
- **Performance Monitoring**: Built-in logging and metrics

## Troubleshooting

### Common Issues

1. **"MCP library not installed"** → Run: `pip install mcp`
2. **"Search failed"** → Check internet connection and rate limits
3. **"Tools not showing"** → Restart VS Code and check MCP configuration

### Debug Mode

Enable debug logging in `config.json`:

```json
{
  "mcp": {
    "debug": true
  }
}
```

Check logs in `web_search_mcp.log` for detailed information.
  ],
  "metadata": {
    "query": "original query",
    "timestamp": "search timestamp",
    "result_count": 5
  }
}

```
