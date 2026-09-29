# Web Search MCP Basic Usage Example

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\web_search_mcp\examples\basic_search.md #command_line #documentation #web_interface  
**Category:** Documentation  
**Status:** Active

This example demonstrates how to use the Web Search MCP server for research with proper citations.

## Python Client Example

```python
import requests
import json

# Server configuration
MCP_SERVER_URL = "http://localhost:8765"

def search_with_citations(query, num_results=5):
    """
    Perform a web search with citations using the MCP server
    
    Args:
        query: Search query string
        num_results: Number of results to return
        
    Returns:
        JSON response with search results and citations
    """
    # Prepare the request
    endpoint = f"{MCP_SERVER_URL}/search"
    payload = {
        "query": query,
        "num_results": num_results,
        "require_citations": True
    }
    
    # Send the request
    response = requests.post(endpoint, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Example usage
if __name__ == "__main__":
    query = "impact of artificial intelligence on healthcare"
    results = search_with_citations(query)
    
    if results:
        print(f"Found {len(results['results'])} results for '{query}'")
        print("\nResults with citations:")
        
        for i, result in enumerate(results['results'], 1):
            print(f"\n--- Result {i} ---")
            print(f"Title: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Summary: {result['content'][:150]}...")
            print(f"Citation: {result['citation']}")
```

## Example Output

```
Found 5 results for 'impact of artificial intelligence on healthcare'

--- Result 1 ---
Title: 10 Common Applications of Artificial Intelligence in Healthcare
URL: https://www.techtarget.com/searchenterpriseai/feature/10-common-applications-of-artificial-intelligence-in-healthcare
Summary: AI in healthcare can help medical professionals save time treating patients through early diagnosis and with automated administrative tasks...
Citation: Nicole Laskowski. (2023). 10 Common Applications of Artificial Intelligence in Healthcare. Techtarget.com. Retrieved on September 5, 2023 from https://www.techtarget.com/searchenterpriseai/feature/10-common-applications-of-artificial-intelligence-in-healthcare

--- Result 2 ---
Title: The impact of artificial intelligence in healthcare: a systematic review
URL: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8285156/
Summary: Artificial intelligence (AI) algorithms, particularly deep learning, have demonstrated remarkable progress in image-recognition tasks...
Citation: Pacis, D. M., et al. (2018). The impact of artificial intelligence in healthcare: a systematic review. Ncbi.nlm.nih.gov. Retrieved on September 5, 2023 from https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8285156/
```

## Using with an AI Assistant

When requesting information from an AI assistant, you can ask it to use the MCP server to perform research:

```
Can you research the impact of artificial intelligence on healthcare using the MCP server for accurate and cited information?
```

The AI can then make requests to the MCP server, gather the information, and provide a well-researched response with proper citations.
