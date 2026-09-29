# EDS Embedding-Specific Dataset Discovery Guide

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\docs\embedding_discovery_guide.md #command_line #documentation #memory_management #multimodal #training  
**Category:** Documentation  
**Status:** Active

## Overview

The `eds_discover_embedding_datasets` tool is a specialized discovery system designed specifically for finding datasets suitable for embedding training. Unlike general dataset discovery, this tool focuses on datasets that are optimized for creating high-quality embeddings with proper annotation and validation support.

## What Makes This Tool Special

### 1. **Embedding-Focused Filtering**

- Only returns datasets marked as `embedding_friendly: true`
- Prioritizes datasets with semantic similarity annotations
- Filters for datasets with proper embedding training structures

### 2. **Annotation Quality Assurance**

- Requires datasets with annotation support by default
- Calculates annotation coverage percentages
- Validates annotation types for embedding suitability

### 3. **Validation Set Requirements**

- Ensures datasets have proper validation splits
- Critical for embedding model evaluation
- Prevents overfitting during training

### 4. **Hardware-Aware Recommendations**

- Considers VRAM constraints (GTX 1050 Ti optimization)
- Estimates memory requirements for embedding training
- Filters out datasets too large for target hardware

## Tool Parameters

### Required Parameters

- None - the tool works with defaults

### Optional Parameters

#### `modality` (string)

- **Options**: "text", "image", "audio", "video", "multimodal", "all"
- **Default**: "all"
- **Purpose**: Filter datasets by data type
- **Example**: "text" for text embedding datasets only

#### `use_case` (string)

- **Options**: "sentence_similarity", "image_similarity", "cross_modal", "classification", "retrieval", "all"
- **Default**: "all"
- **Purpose**: Target specific embedding applications
- **Example**: "sentence_similarity" for BERT-style embeddings

#### `min_annotation_coverage` (number)

- **Range**: 0.0 to 1.0
- **Default**: 0.8 (80% coverage)
- **Purpose**: Minimum percentage of data with annotations
- **Example**: 0.95 for highest quality datasets only

#### `require_validation_split` (boolean)

- **Default**: true
- **Purpose**: Require datasets with validation sets
- **Example**: false to include datasets without validation

#### `hardware_constraints` (object)

- **Properties**:
  - `vram_gb`: Available VRAM (default: 4 for GTX 1050 Ti)
  - `max_dataset_size_gb`: Maximum dataset size
- **Purpose**: Filter by hardware capabilities

## Example Usage Scenarios

### 1. Basic Embedding Dataset Discovery

```json
{
  "tool": "eds_discover_embedding_datasets",
  "arguments": {}
}
```

Returns all embedding-friendly datasets with 80%+ annotation coverage.

### 2. Text Similarity Embeddings

```json
{
  "tool": "eds_discover_embedding_datasets",
  "arguments": {
    "modality": "text",
    "use_case": "sentence_similarity",
    "min_annotation_coverage": 0.9
  }
}
```

Perfect for training BERT-style sentence embedding models.

### 3. Multimodal Embeddings with Hardware Constraints

```json
{
  "tool": "eds_discover_embedding_datasets",
  "arguments": {
    "modality": "multimodal",
    "use_case": "cross_modal",
    "hardware_constraints": {
      "vram_gb": 4,
      "max_dataset_size_gb": 10
    }
  }
}
```

Finds datasets for CLIP-style multimodal embeddings on GTX 1050 Ti.

### 4. Research-Grade High-Quality Datasets

```json
{
  "tool": "eds_discover_embedding_datasets",
  "arguments": {
    "min_annotation_coverage": 0.95,
    "require_validation_split": true
  }
}
```

Returns only the highest quality datasets for research applications.

## Response Structure

### Success Response

```json
{
  "success": true,
  "data": {
    "embedding_datasets": [
      {
        "name": "dataset_name",
        "category": "academic",
        "base_url": "https://...",
        "download_url": "https://...",
        "categories": ["text", "embeddings"],
        "formats": ["json", "csv"],
        "verification": {
          "status": "online",
          "response_time": 0.5,
          "timestamp": "2025-01-17T..."
        },
        "auth_required": false,
        "notable_datasets": ["squad", "glue"],
        "annotation_support": true,
        "validation_sets": true,
        "embedding_friendly": true,
        "annotation_types": ["similarity_scores", "labels"],
        "annotation_coverage": 0.92,
        "embedding_suitability_score": 0.85,
        "quality_score": 0.9,
        "estimated_memory_gb": 2.1,
        "annotation_details": {
          "annotation_types": ["similarity_scores", "labels"],
          "validation_sets": true,
          "annotation_coverage": 0.92,
          "formats": ["json", "csv"],
          "quality_assurance": {},
          "embedding_ready": true
        }
      }
    ],
    "total_found": 15,
    "filters_applied": {
      "modality": "text",
      "use_case": "sentence_similarity",
      "min_annotation_coverage": 0.9,
      "require_validation_split": true,
      "hardware_constraints": {"vram_gb": 4}
    },
    "annotation_summary": {
      "total_datasets": 15,
      "datasets_with_validation": 15,
      "validation_percentage": 100.0,
      "average_annotation_coverage": 0.91,
      "annotation_types_available": ["similarity_scores", "labels", "embeddings"],
      "annotation_types_count": 3
    },
    "timestamp": "2025-01-17T..."
  }
}
```

## Key Features Explained

### 1. **Embedding Suitability Scoring**

Each dataset receives a score based on:

- Base quality score from repository reputation
- Annotation type relevance for embeddings
- Use case alignment
- Validation set availability

### 2. **Annotation Coverage Calculation**

- Academic repositories: 90% coverage assumed
- Government datasets: 85% coverage
- Community datasets: 75% coverage
- Explicit annotation support: 95% coverage

### 3. **Hardware Constraint Filtering**

- Memory requirement ≤ 2x VRAM limit
- Dataset size ≤ specified maximum
- Optimized for GTX 1050 Ti (4GB VRAM)

### 4. **Verification Integration**

- Real-time repository health checks
- Cached verification results
- Online/offline status reporting

## Best Practices

### 1. **Start Broad, Then Narrow**

```json
// First, discover all embedding datasets
{"tool": "eds_discover_embedding_datasets", "arguments": {}}

// Then filter for specific needs
{"tool": "eds_discover_embedding_datasets", "arguments": {
  "modality": "text",
  "use_case": "sentence_similarity",
  "min_annotation_coverage": 0.9
}}
```

### 2. **Consider Hardware Constraints**

Always specify your hardware limitations:

```json
{
  "hardware_constraints": {
    "vram_gb": 4,
    "max_dataset_size_gb": 20
  }
}
```

### 3. **Use Annotation Summary**

The response includes an annotation summary to help understand:

- Overall dataset quality
- Validation set availability
- Annotation type diversity

## Integration with ImpressionCore

This tool is specifically designed for ImpressionCore's embedding training pipeline:

1. **Phase 1**: Discover suitable datasets
2. **Phase 2**: Verify dataset accessibility
3. **Phase 3**: Download and prepare datasets
4. **Phase 4**: Train embedding models

The tool ensures that discovered datasets are compatible with ImpressionCore's brain-inspired architecture and memory constraints.

## Advanced Usage

### Custom Quality Thresholds

```json
{
  "min_annotation_coverage": 0.99,
  "require_validation_split": true,
  "hardware_constraints": {
    "vram_gb": 8,
    "max_dataset_size_gb": 50
  }
}
```

### Cross-Modal Discovery

```json
{
  "modality": "multimodal",
  "use_case": "cross_modal",
  "min_annotation_coverage": 0.85
}
```

### Retrieval-Optimized Datasets

```json
{
  "use_case": "retrieval",
  "min_annotation_coverage": 0.9,
  "require_validation_split": true
}
```

## Troubleshooting

### No Datasets Found

- Lower `min_annotation_coverage` threshold
- Set `require_validation_split` to false
- Increase `max_dataset_size_gb` limit
- Use "all" for modality and use_case

### Hardware Constraints Too Restrictive

- Increase VRAM limit if possible
- Increase dataset size limit
- Consider datasets with lower memory requirements

### Verification Failures

- Check network connectivity
- Verify repository URLs are accessible
- Use force_refresh in verification tools

## Related Tools

- `eds_discover_datasets`: General dataset discovery
- `eds_verify_sources`: Repository health checking
- `eds_get_recommendations`: AI-powered recommendations
- `eds_health_check`: Comprehensive system health

This embedding-specific discovery tool represents a significant advancement in dataset curation for AI training, specifically optimized for ImpressionCore's requirements and hardware constraints.
