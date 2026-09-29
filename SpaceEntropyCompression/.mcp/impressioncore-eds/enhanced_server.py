#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\enhanced_server.py #api #command_line #memory_management #multimodal #python #source_code #training  
**Category:** Source Code  
**Status:** Active
"""



import sys
import os
import json
import time
import hashlib
import asyncio
import aiohttp
import traceback
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from config.dataset_sources import (
        DATASET_REPOSITORIES, VERIFICATION_CONFIG, DOWNLOAD_CONFIG,
        USE_CASE_MAPPINGS, MEMORY_ESTIMATES, QUALITY_SCORES,
        ANNOTATION_REQUIREMENTS
    )
    # Optional imports that may not exist
    try:
        from config.dataset_sources import EMBEDDING_QUALITY_FILTERS
    except ImportError:
        EMBEDDING_QUALITY_FILTERS = {"label_coverage_threshold": 0.95}
    
    SOURCES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import dataset sources: {e}", file=sys.stderr)
    DATASET_REPOSITORIES = {}
    VERIFICATION_CONFIG = {"timeout": 30, "retry_attempts": 3, "health_check_interval": 24}
    DOWNLOAD_CONFIG = {"max_file_size": "10GB", "concurrent_downloads": 3}
    USE_CASE_MAPPINGS = {}
    MEMORY_ESTIMATES = {}
    QUALITY_SCORES = {}
    ANNOTATION_REQUIREMENTS = {}
    EMBEDDING_QUALITY_FILTERS = {}
    SOURCES_AVAILABLE = False

class EnhancedEDSMCPServer:
    """Enhanced External Data Sources MCP Server with comprehensive dataset management."""
    
    def __init__(self):
        self.project_root = str(project_root)
        self.debug = os.getenv('EDS_DEBUG', '0') == '1'
        self.cache_dir = Path(self.project_root) / ".cache" / "eds"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logging
        self.logger = logging.getLogger("EDS-MCP")
        self.logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        
        # Load cached verification results
        self.verification_cache = self._load_verification_cache()
        
        self._log_info(f"Enhanced EDS MCP Server initialized successfully. Sources available: {SOURCES_AVAILABLE}")
        if SOURCES_AVAILABLE:
            total_sources = sum(len(repos) for repos in DATASET_REPOSITORIES.values())
            self._log_info(f"Loaded {total_sources} dataset sources across {len(DATASET_REPOSITORIES)} categories")
    
    def _load_verification_cache(self) -> Dict[str, Any]:
        """Load cached verification results."""
        cache_file = self.cache_dir / "verification_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self._log_error("Loading verification cache", e)
        return {}
    
    def _save_verification_cache(self):
        """Save verification results to cache."""
        cache_file = self.cache_dir / "verification_cache.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.verification_cache, f, indent=2)
        except Exception as e:
            self._log_error("Saving verification cache", e)
    
    def _log_info(self, message: str):
        """Log info message."""
        if self.debug:
            timestamp = datetime.now().isoformat()
            print(f"[{timestamp}] EDS INFO: {message}", file=sys.stderr)
            sys.stderr.flush()
    
    def _log_error(self, operation: str, error: Exception):
        """Log error message."""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] EDS ERROR in {operation}: {str(error)}", file=sys.stderr)
        if self.debug:
            import traceback
            print(f"[{timestamp}] EDS TRACEBACK: {traceback.format_exc()}", file=sys.stderr)
        sys.stderr.flush()
    
    async def verify_dataset_source(self, source_name: str, source_config: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a dataset source is accessible and working."""
        verification_result = {
            "source_name": source_name,
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "response_time": None,
            "error": None,
            "metadata": {}
        }
        
        try:
            start_time = time.time()
            
            # Check cache first
            cache_key = f"{source_name}_{hashlib.md5(str(source_config).encode()).hexdigest()}"
            cached_result = self.verification_cache.get(cache_key)
            
            if cached_result:
                cache_time = datetime.fromisoformat(cached_result["timestamp"])
                if datetime.now() - cache_time < timedelta(hours=VERIFICATION_CONFIG["health_check_interval"]):
                    self._log_info(f"Using cached verification for {source_name}")
                    return cached_result
            
            # Perform verification based on method
            verification_method = source_config.get("verification_method", "url_check")
            
            timeout = aiohttp.ClientTimeout(total=VERIFICATION_CONFIG["timeout"])
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            
            async with aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={"User-Agent": VERIFICATION_CONFIG["user_agent"]}
            ) as session:
                
                if verification_method == "api_check":
                    api_url = source_config.get("api_url", source_config.get("base_url"))
                    async with session.head(api_url) as response:
                        verification_result["status"] = "online" if response.status < 400 else "offline"
                        verification_result["metadata"]["status_code"] = response.status
                        verification_result["metadata"]["headers"] = dict(response.headers)
                
                elif verification_method == "url_check":
                    base_url = source_config.get("base_url")
                    async with session.head(base_url) as response:
                        verification_result["status"] = "online" if response.status < 400 else "offline"
                        verification_result["metadata"]["status_code"] = response.status
                
                elif verification_method == "github_check":
                    # Special handling for GitHub repositories
                    repo_url = source_config.get("base_url", "")
                    if "github.com" in repo_url:
                        api_url = repo_url.replace("github.com", "api.github.com/repos")
                        async with session.get(api_url) as response:
                            verification_result["status"] = "online" if response.status < 400 else "offline"
                            verification_result["metadata"]["status_code"] = response.status
                            
                            if response.status == 200:
                                try:
                                    repo_data = await response.json()
                                    verification_result["metadata"]["stars"] = repo_data.get("stargazers_count", 0)
                                    verification_result["metadata"]["last_updated"] = repo_data.get("updated_at")
                                except:
                                    pass
            
            verification_result["response_time"] = time.time() - start_time
            
            # Cache the result
            self.verification_cache[cache_key] = verification_result
            self._save_verification_cache()
            
        except Exception as e:
            verification_result["status"] = "error"
            verification_result["error"] = str(e)
            self._log_error(f"Verifying {source_name}", e)
        
        return verification_result
    
    async def discover_datasets(self, category: Optional[str] = None, 
                              modality: Optional[str] = None,
                              annotation_required: bool = True,
                              validation_required: bool = True,
                              embedding_friendly: bool = False) -> List[Dict[str, Any]]:
        """Discover available datasets based on filters, prioritizing annotated datasets."""
        if not SOURCES_AVAILABLE:
            return []
        
        discovered_datasets = []
        
        for repo_category, repositories in DATASET_REPOSITORIES.items():
            if category and category.lower() not in repo_category.lower():
                continue
            
            for repo_name, repo_config in repositories.items():
                categories = repo_config.get("categories", [])
                if modality and modality not in categories:
                    continue
                
                # Filter based on annotation requirements
                has_annotations = repo_config.get("annotation_support", False)
                has_validation = repo_config.get("validation_sets", False)
                is_embedding_friendly = repo_config.get("embedding_friendly", False)
                
                if annotation_required and not has_annotations:
                    continue
                    
                if validation_required and not has_validation:
                    continue
                    
                if embedding_friendly and not is_embedding_friendly:
                    continue
                
                # Verify the repository
                verification_result = await self.verify_dataset_source(repo_name, repo_config)
                
                dataset_info = {
                    "name": repo_name,
                    "category": repo_category,
                    "base_url": repo_config.get("base_url"),
                    "download_url": repo_config.get("download_url"),
                    "categories": categories,
                    "formats": repo_config.get("download_format", []),
                    "verification": verification_result,
                    "auth_required": repo_config.get("auth_required", False),
                    "notable_datasets": repo_config.get("notable_datasets", []),
                    "annotation_support": has_annotations,
                    "validation_sets": has_validation,
                    "embedding_friendly": is_embedding_friendly,
                    "annotation_types": repo_config.get("annotation_types", []),
                    "quality_score": self._get_repository_quality_score(repo_name)
                }
                
                discovered_datasets.append(dataset_info)
        
        # Sort by quality score and annotation support
        discovered_datasets.sort(key=lambda x: (
            x["annotation_support"],
            x["validation_sets"], 
            x["embedding_friendly"],
            x["quality_score"]
        ), reverse=True)
        
        return discovered_datasets
    
    async def get_dataset_recommendations(self, use_case: str, 
                                        hardware_constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get dataset recommendations based on use case and hardware constraints."""
        if not SOURCES_AVAILABLE:
            return []
        
        recommendations = []
        
        # Get relevant datasets for use case
        use_case_data = USE_CASE_MAPPINGS.get(use_case.lower(), {})
        relevant_datasets = use_case_data.get("primary", []) + use_case_data.get("secondary", [])
        
        if not relevant_datasets:
            # Fallback to general recommendations
            relevant_datasets = ["squad", "imagenet", "librispeech", "conceptual_captions", "wikipedia"]
        
        # Filter datasets based on hardware constraints
        vram_limit = hardware_constraints.get("vram_gb", 4)  # Default to 4GB
        
        for dataset_name in relevant_datasets:
            # Find the dataset in our repositories
            for repo_category, repositories in DATASET_REPOSITORIES.items():
                for repo_name, repo_config in repositories.items():
                    notable_datasets = repo_config.get("notable_datasets", [])
                    if dataset_name in notable_datasets or dataset_name == repo_name:
                        # Estimate memory requirements
                        memory_estimate = MEMORY_ESTIMATES.get(dataset_name, 2.0)
                        
                        if memory_estimate <= vram_limit * 2:  # Allow 2x VRAM for processing
                            recommendation = {
                                "dataset_name": dataset_name,
                                "repository": repo_name,
                                "category": repo_category,
                                "base_url": repo_config.get("base_url"),
                                "download_url": repo_config.get("download_url"),
                                "estimated_memory_gb": memory_estimate,
                                "formats": repo_config.get("download_format", []),
                                "auth_required": repo_config.get("auth_required", False),
                                "suitability_score": self._calculate_suitability_score(
                                    dataset_name, use_case, hardware_constraints
                                )
                            }
                            recommendations.append(recommendation)
                        break
        
        # Sort by suitability score
        recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
        
        return recommendations
    
    def _calculate_suitability_score(self, dataset_name: str, use_case: str, 
                                   hardware_constraints: Dict[str, Any]) -> float:
        """Calculate suitability score for a dataset."""
        score = 0.0
        
        # Base quality score
        score += QUALITY_SCORES.get(dataset_name, 0.7)
        
        # Adjust for hardware constraints
        memory_requirement = MEMORY_ESTIMATES.get(dataset_name, 2.0)
        vram_limit = hardware_constraints.get("vram_gb", 4)
        
        if memory_requirement <= vram_limit * 0.5:  # 50% of VRAM
            score += 0.3
        elif memory_requirement <= vram_limit:
            score += 0.1
        else:
            score -= 0.2
        
        # Adjust for use case specificity
        use_case_data = USE_CASE_MAPPINGS.get(use_case.lower(), {})
        if dataset_name in use_case_data.get("primary", []):
            score += 0.2
        elif dataset_name in use_case_data.get("secondary", []):
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get list of available EDS tools."""
        return [
            {
                "name": "eds_discover_datasets",
                "description": "Discover available datasets from 40+ verified repositories with annotation and validation support",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Filter by dataset category",
                            "enum": ["academic", "government", "computer_vision", "nlp", "audio", "multimodal", "ai_training", "specialized", "all"]
                        },
                        "modality": {
                            "type": "string",
                            "description": "Filter by data modality",
                            "enum": ["text", "image", "audio", "video", "multimodal", "all"]
                        },
                        "annotation_required": {
                            "type": "boolean",
                            "description": "Only include datasets with annotation support",
                            "default": True
                        },
                        "validation_required": {
                            "type": "boolean",
                            "description": "Only include datasets with validation sets",
                            "default": True
                        },
                        "embedding_friendly": {
                            "type": "boolean",
                            "description": "Prioritize datasets suitable for embedding training",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "eds_verify_sources",
                "description": "Verify accessibility and health of dataset sources with caching",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of source names to verify (empty for all)"
                        },
                        "force_refresh": {
                            "type": "boolean",
                            "description": "Force refresh of cached verification results",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "eds_get_recommendations",
                "description": "Get AI-powered dataset recommendations based on use case and hardware constraints",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "use_case": {
                            "type": "string",
                            "description": "Intended use case for the dataset",
                            "enum": ["conversation", "image_classification", "speech_recognition", "multimodal", "text_generation", "embedding", "scientific"]
                        },
                        "hardware_constraints": {
                            "type": "object",
                            "properties": {
                                "vram_gb": {"type": "number", "description": "Available VRAM in GB"},
                                "ram_gb": {"type": "number", "description": "Available RAM in GB"},
                                "storage_gb": {"type": "number", "description": "Available storage in GB"}
                            },
                            "description": "Hardware constraints for dataset processing"
                        }
                    },
                    "required": ["use_case"]
                }
            },
            {
                "name": "eds_get_dataset_info",
                "description": "Get detailed information about a specific dataset with verification status",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to get information about"
                        },
                        "include_verification": {
                            "type": "boolean",
                            "description": "Include verification status in response",
                            "default": True
                        }
                    },
                    "required": ["dataset_name"]
                }
            },
            {
                "name": "eds_health_check",
                "description": "Perform comprehensive health check of all dataset sources with parallel verification",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "parallel_checks": {
                            "type": "number",
                            "description": "Number of parallel verification checks",
                            "default": 5,
                            "minimum": 1,
                            "maximum": 10
                        }
                    }
                }
            },
            {
                "name": "eds_get_statistics",
                "description": "Get comprehensive statistics about available dataset sources",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "eds_discover_embedding_datasets",
                "description": "Discover datasets specifically suitable for embedding training with annotation and validation support",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "modality": {
                            "type": "string",
                            "description": "Filter by data modality",
                            "enum": ["text", "image", "audio", "video", "multimodal", "all"]
                        },
                        "use_case": {
                            "type": "string",
                            "description": "Specific embedding use case",
                            "enum": ["sentence_similarity", "image_similarity", "cross_modal", "classification", "retrieval", "all"]
                        },
                        "min_annotation_coverage": {
                            "type": "number",
                            "description": "Minimum percentage of data with annotations (0.0-1.0)",
                            "default": 0.8,
                            "minimum": 0.0,
                            "maximum": 1.0
                        },
                        "require_validation_split": {
                            "type": "boolean",
                            "description": "Require datasets with validation splits",
                            "default": True
                        },
                        "hardware_constraints": {
                            "type": "object",
                            "properties": {
                                "vram_gb": {"type": "number", "description": "Available VRAM in GB"},
                                "max_dataset_size_gb": {"type": "number", "description": "Maximum dataset size in GB"}
                            }
                        }
                    }
                }
            }
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls for EDS operations."""
        try:
            if not SOURCES_AVAILABLE and tool_name != "eds_get_statistics":
                return {
                    "success": False,
                    "error": "Dataset sources configuration not available. Check config/dataset_sources.py",
                    "help": "Make sure the dataset_sources.py file is properly configured in the config directory."
                }
            
            if tool_name == "eds_discover_datasets":
                category = arguments.get("category")
                modality = arguments.get("modality")
                annotation_required = arguments.get("annotation_required", True)
                validation_required = arguments.get("validation_required", True)
                embedding_friendly = arguments.get("embedding_friendly", False)
                
                datasets = await self.discover_datasets(
                    category, modality, annotation_required, validation_required, embedding_friendly
                )
                
                return {
                    "success": True,
                    "data": {
                        "datasets": datasets,
                        "total_found": len(datasets),
                        "filters_applied": {
                            "category": category,
                            "modality": modality
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                }
            
            elif tool_name == "eds_verify_sources":
                source_names = arguments.get("source_names", [])
                force_refresh = arguments.get("force_refresh", False)
                
                if force_refresh:
                    self.verification_cache.clear()
                
                verification_results = []
                
                # If no specific sources, verify all
                if not source_names:
                    tasks = []
                    for repo_category, repositories in DATASET_REPOSITORIES.items():
                        for repo_name, repo_config in repositories.items():
                            tasks.append(self.verify_dataset_source(repo_name, repo_config))
                    
                    verification_results = await asyncio.gather(*tasks, return_exceptions=True)
                    verification_results = [r for r in verification_results if not isinstance(r, Exception)]
                else:
                    # Verify specific sources
                    for source_name in source_names:
                        found = False
                        for repo_category, repositories in DATASET_REPOSITORIES.items():
                            if source_name in repositories:
                                result = await self.verify_dataset_source(source_name, repositories[source_name])
                                verification_results.append(result)
                                found = True
                                break
                        
                        if not found:
                            verification_results.append({
                                "source_name": source_name,
                                "status": "not_found",
                                "error": "Source not found in repository configuration",
                                "timestamp": datetime.now().isoformat()
                            })
                
                online_count = sum(1 for r in verification_results if r.get("status") == "online")
                offline_count = sum(1 for r in verification_results if r.get("status") == "offline")
                error_count = sum(1 for r in verification_results if r.get("status") == "error")
                
                return {
                    "success": True,
                    "data": {
                        "verification_results": verification_results,
                        "total_verified": len(verification_results),
                        "online_count": online_count,
                        "offline_count": offline_count,
                        "error_count": error_count,
                        "health_percentage": (online_count / len(verification_results) * 100) if verification_results else 0,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            
            elif tool_name == "eds_get_recommendations":
                use_case = arguments.get("use_case")
                hardware_constraints = arguments.get("hardware_constraints", {"vram_gb": 4})
                
                recommendations = await self.get_dataset_recommendations(use_case, hardware_constraints)
                
                return {
                    "success": True,
                    "data": {
                        "recommendations": recommendations,
                        "total_found": len(recommendations),
                        "use_case": use_case,
                        "hardware_constraints": hardware_constraints,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            
            elif tool_name == "eds_get_dataset_info":
                dataset_name = arguments.get("dataset_name")
                include_verification = arguments.get("include_verification", True)
                
                dataset_info = None
                
                # Search for the dataset
                for repo_category, repositories in DATASET_REPOSITORIES.items():
                    for repo_name, repo_config in repositories.items():
                        notable_datasets = repo_config.get("notable_datasets", [])
                        if dataset_name in notable_datasets or dataset_name == repo_name:
                            dataset_info = {
                                "name": dataset_name,
                                "repository": repo_name,
                                "category": repo_category,
                                "base_url": repo_config.get("base_url"),
                                "download_url": repo_config.get("download_url"),
                                "categories": repo_config.get("categories", []),
                                "formats": repo_config.get("download_format", []),
                                "auth_required": repo_config.get("auth_required", False),
                                "notable_datasets": notable_datasets,
                                "estimated_memory_gb": MEMORY_ESTIMATES.get(dataset_name, "unknown"),
                                "quality_score": QUALITY_SCORES.get(dataset_name, "unknown")
                            }
                            
                            if include_verification:
                                verification_result = await self.verify_dataset_source(repo_name, repo_config)
                                dataset_info["verification"] = verification_result
                            
                            break
                    
                    if dataset_info:
                        break
                
                if not dataset_info:
                    return {
                        "success": False,
                        "error": f"Dataset '{dataset_name}' not found in repository configuration"
                    }
                
                return {
                    "success": True,
                    "data": dataset_info
                }
            
            elif tool_name == "eds_health_check":
                parallel_checks = min(arguments.get("parallel_checks", 5), 10)  # Cap at 10
                
                # Perform comprehensive health check
                all_sources = []
                for repo_category, repositories in DATASET_REPOSITORIES.items():
                    for repo_name, repo_config in repositories.items():
                        all_sources.append((repo_name, repo_config))
                
                # Process in batches for parallel checking
                verification_results = []
                for i in range(0, len(all_sources), parallel_checks):
                    batch = all_sources[i:i + parallel_checks]
                    batch_tasks = [
                        self.verify_dataset_source(repo_name, repo_config)
                        for repo_name, repo_config in batch
                    ]
                    batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                    verification_results.extend([r for r in batch_results if not isinstance(r, Exception)])
                
                # Generate health report
                online_count = sum(1 for r in verification_results if r.get("status") == "online")
                offline_count = sum(1 for r in verification_results if r.get("status") == "offline")
                error_count = sum(1 for r in verification_results if r.get("status") == "error")
                
                health_score = (online_count / len(verification_results)) * 100 if verification_results else 0
                
                return {
                    "success": True,
                    "data": {
                        "health_score": health_score,
                        "total_sources": len(verification_results),
                        "online_count": online_count,
                        "offline_count": offline_count,
                        "error_count": error_count,
                        "verification_results": verification_results,
                        "timestamp": datetime.now().isoformat(),
                        "recommendations": self._get_health_recommendations(health_score, offline_count, error_count)
                    }
                }
            
            elif tool_name == "eds_get_statistics":
                if not SOURCES_AVAILABLE:
                    return {
                        "success": True,
                        "data": {
                            "sources_available": False,
                            "message": "Dataset sources configuration not loaded",
                            "total_categories": 0,
                            "total_sources": 0,
                            "total_datasets": 0
                        }
                    }
                
                # Calculate statistics
                total_sources = sum(len(repos) for repos in DATASET_REPOSITORIES.values())
                total_datasets = sum(
                    len(repo_config.get("notable_datasets", []))
                    for repos in DATASET_REPOSITORIES.values()
                    for repo_config in repos.values()
                )
                
                category_stats = {}
                for category, repos in DATASET_REPOSITORIES.items():
                    category_stats[category] = {
                        "source_count": len(repos),
                        "dataset_count": sum(len(repo.get("notable_datasets", [])) for repo in repos.values())
                    }
                
                return {
                    "success": True,
                    "data": {
                        "sources_available": True,
                        "total_categories": len(DATASET_REPOSITORIES),
                        "total_sources": total_sources,
                        "total_datasets": total_datasets,
                        "category_breakdown": category_stats,
                        "use_cases_supported": list(USE_CASE_MAPPINGS.keys()),
                        "memory_estimates_available": len(MEMORY_ESTIMATES),
                        "quality_scores_available": len(QUALITY_SCORES),
                        "timestamp": datetime.now().isoformat()
                    }
                }
            
            elif tool_name == "eds_discover_embedding_datasets":
                modality = arguments.get("modality", "all")
                use_case = arguments.get("use_case", "all")
                min_annotation_coverage = arguments.get("min_annotation_coverage", 0.8)
                require_validation_split = arguments.get("require_validation_split", True)
                hardware_constraints = arguments.get("hardware_constraints", {"vram_gb": 4})
                
                # Filter for embedding-friendly datasets only
                embedding_datasets = await self.discover_embedding_datasets(
                    modality, use_case, min_annotation_coverage, require_validation_split, hardware_constraints
                )
                
                return {
                    "success": True,
                    "data": {
                        "embedding_datasets": embedding_datasets,
                        "total_found": len(embedding_datasets),
                        "filters_applied": {
                            "modality": modality,
                            "use_case": use_case,
                            "min_annotation_coverage": min_annotation_coverage,
                            "require_validation_split": require_validation_split,
                            "hardware_constraints": hardware_constraints
                        },
                        "annotation_summary": self._get_annotation_summary(embedding_datasets),
                        "timestamp": datetime.now().isoformat()
                    }
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                    "available_tools": [tool["name"] for tool in self.get_tools()]
                }
        
        except Exception as e:
            self._log_error(f"Tool {tool_name}", e)
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
                "tool": tool_name,
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_health_recommendations(self, health_score: float, offline_count: int, error_count: int) -> List[str]:
        """Generate health recommendations based on verification results."""
        recommendations = []
        
        if health_score < 50:
            recommendations.append("Health score is critically low. Check network connectivity and service status.")
        elif health_score < 80:
            recommendations.append("Health score is below optimal. Some sources may be experiencing issues.")
        else:
            recommendations.append("Overall health is good. Most sources are accessible.")
        
        if offline_count > 0:
            recommendations.append(f"{offline_count} sources are offline. Consider using alternative sources.")
        
        if error_count > 0:
            recommendations.append(f"{error_count} sources have errors. Check logs for details.")
        
        return recommendations

    async def discover_embedding_datasets(self, modality: str = "all", 
                                        use_case: str = "all",
                                        min_annotation_coverage: float = 0.8,
                                        require_validation_split: bool = True,
                                        hardware_constraints: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Discover datasets specifically suitable for embedding training with annotation support."""
        if not SOURCES_AVAILABLE:
            return []
        
        if hardware_constraints is None:
            hardware_constraints = {"vram_gb": 4}
        
        embedding_datasets = []
        
        # Use enhanced use case mappings if available
        use_case_datasets = []
        if use_case != "all":
            use_case_data = USE_CASE_MAPPINGS.get(use_case, {})
            use_case_datasets = use_case_data.get("primary", []) + use_case_data.get("secondary", [])
        
        for repo_category, repositories in DATASET_REPOSITORIES.items():
            for repo_name, repo_config in repositories.items():
                # Filter by modality
                categories = repo_config.get("categories", [])
                if modality != "all" and modality not in categories:
                    continue
                
                # Must be embedding-friendly
                if not repo_config.get("embedding_friendly", False):
                    continue
                
                # Must have annotations
                if not repo_config.get("annotation_support", False):
                    continue
                
                # Check validation split requirement
                if require_validation_split and not repo_config.get("validation_sets", False):
                    continue
                
                # Check annotation coverage using quality filters
                annotation_coverage = self._calculate_annotation_coverage(repo_name, repo_config)
                if annotation_coverage < min_annotation_coverage:
                    continue
                
                # Check hardware constraints
                if not self._meets_hardware_constraints(repo_name, repo_config, hardware_constraints):
                    continue
                
                # Check if dataset matches use case
                notable_datasets = repo_config.get("notable_datasets", [])
                if use_case != "all" and use_case_datasets:
                    if not any(dataset in use_case_datasets for dataset in notable_datasets):
                        continue
                
                # Verify the repository
                verification_result = await self.verify_dataset_source(repo_name, repo_config)
                
                # Calculate embedding suitability score
                embedding_score = self._calculate_embedding_suitability(repo_name, repo_config, use_case)
                
                dataset_info = {
                    "name": repo_name,
                    "category": repo_category,
                    "base_url": repo_config.get("base_url"),
                    "download_url": repo_config.get("download_url"),
                    "categories": categories,
                    "formats": repo_config.get("download_format", []),
                    "verification": verification_result,
                    "auth_required": repo_config.get("auth_required", False),
                    "notable_datasets": notable_datasets,
                    "annotation_support": True,  # Already filtered
                    "validation_sets": True,    # Already filtered
                    "embedding_friendly": True, # Already filtered
                    "annotation_types": repo_config.get("annotation_types", []),
                    "annotation_coverage": annotation_coverage,
                    "embedding_suitability_score": embedding_score,
                    "quality_score": self._get_repository_quality_score(repo_name),
                    "estimated_memory_gb": MEMORY_ESTIMATES.get(repo_name, 2.0),
                    "annotation_details": self._get_annotation_details(repo_name, repo_config)
                }
                
                embedding_datasets.append(dataset_info)
        
        # Sort by embedding suitability score, then by quality score
        embedding_datasets.sort(key=lambda x: (
            x["embedding_suitability_score"],
            x["quality_score"],
            x["annotation_coverage"]
        ), reverse=True)
        
        return embedding_datasets
    
    def _calculate_annotation_coverage(self, repo_name: str, repo_config: Dict[str, Any]) -> float:
        """Calculate annotation coverage for a repository."""
        # Use embedding quality filters if available
        coverage_threshold = EMBEDDING_QUALITY_FILTERS.get("label_coverage_threshold", 0.95)
        # For repositories with explicit annotation support, assume high coverage
        if repo_config.get("annotation_support", False):
            return coverage_threshold
        
        # Default coverage based on repository type
        if "academic" in repo_name.lower() or "research" in repo_name.lower():
            return 0.9
        elif "government" in repo_name.lower():
            return 0.85
        elif "community" in repo_name.lower():
            return 0.75
        else:
            return 0.8
    
    def _meets_hardware_constraints(self, repo_name: str, repo_config: Dict[str, Any], 
                                   hardware_constraints: Dict[str, Any]) -> bool:
        """Check if dataset meets hardware constraints."""
        vram_limit = hardware_constraints.get("vram_gb", 4)
        max_dataset_size = hardware_constraints.get("max_dataset_size_gb", 20)
        
        # Check memory requirements
        memory_estimate = MEMORY_ESTIMATES.get(repo_name, 2.0)
        
        # Allow dataset if it uses less than 2x VRAM limit
        if memory_estimate > vram_limit * 2:
            return False
        
        # Check dataset size constraint
        if memory_estimate > max_dataset_size:
            return False
        
        return True
    
    def _calculate_embedding_suitability(self, repo_name: str, repo_config: Dict[str, Any], 
                                        use_case: str) -> float:
        """Calculate embedding suitability score."""
        score = 0.0
        
        # Base score from quality scores
        score += QUALITY_SCORES.get(repo_name, 0.7)
        
        # Bonus for embedding-friendly annotation types
        annotation_types = repo_config.get("annotation_types", [])
        embedding_friendly_types = ["embeddings", "similarity_scores", "pairs", "labels"]
        
        overlap = len(set(annotation_types) & set(embedding_friendly_types))
        score += overlap * 0.1  # 0.1 bonus per relevant annotation type
        
        # Bonus for specific use case alignment
        if use_case != "all":
            notable_datasets = repo_config.get("notable_datasets", [])
            use_case_data = USE_CASE_MAPPINGS.get(use_case, {})
            use_case_datasets = use_case_data.get("primary", []) + use_case_data.get("secondary", [])
            
            if any(dataset in use_case_datasets for dataset in notable_datasets):
                score += 0.2
        
        # Bonus for validation sets
        if repo_config.get("validation_sets", False):
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _get_annotation_details(self, repo_name: str, repo_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed annotation information for a repository."""
        return {
            "annotation_types": repo_config.get("annotation_types", []),
            "validation_sets": repo_config.get("validation_sets", False),
            "annotation_coverage": self._calculate_annotation_coverage(repo_name, repo_config),
            "formats": repo_config.get("download_format", []),
            "quality_assurance": repo_config.get("quality_assurance", {}),
            "embedding_ready": repo_config.get("embedding_friendly", False)
        }
    
    def _get_annotation_summary(self, datasets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics about annotations in discovered datasets."""
        if not datasets:
            return {}
        
        total_datasets = len(datasets)
        annotation_types = set()
        avg_coverage = 0.0
        validation_count = 0
        
        for dataset in datasets:
            annotation_types.update(dataset.get("annotation_types", []))
            avg_coverage += dataset.get("annotation_coverage", 0.0)
            if dataset.get("validation_sets", False):
                validation_count += 1
        
        avg_coverage /= total_datasets
        
        return {
            "total_datasets": total_datasets,
            "datasets_with_validation": validation_count,
            "validation_percentage": (validation_count / total_datasets) * 100,
            "average_annotation_coverage": avg_coverage,
            "annotation_types_available": list(annotation_types),
            "annotation_types_count": len(annotation_types)
        }
    
    def _get_repository_quality_score(self, repo_name: str) -> float:
        """Get quality score for a repository."""
        return QUALITY_SCORES.get(repo_name, 0.7)
    

def main():
    """Main entry point for the EDS MCP server."""
    server = EnhancedEDSMCPServer()
    server._log_info("Enhanced EDS MCP Server starting up...")
    
    try:
        while True:
            try:
                line = input()
                if not line.strip():
                    continue
                
                request = json.loads(line)
                server._log_info(f"Received request: {request.get('method', 'unknown')}")
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id")
                }
                
                if request.get("method") == "initialize":
                    response["result"] = {
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "impressioncore-eds-enhanced",
                            "version": "2.0.0"
                        }
                    }
                
                elif request.get("method") == "tools/list":
                    response["result"] = {
                        "tools": server.get_tools()
                    }
                
                elif request.get("method") == "tools/call":
                    params = request.get("params", {})
                    tool_name = params.get("name")
                    arguments = params.get("arguments", {})
                    
                    if tool_name:
                        result = asyncio.run(server.handle_tool_call(tool_name, arguments))
                        response["result"] = result
                    else:
                        response["error"] = {
                            "code": -32602,
                            "message": "Invalid params: missing tool name"
                        }
                
                else:
                    response["error"] = {
                        "code": -32601,
                        "message": f"Method not found: {request.get('method')}"
                    }
                
                print(json.dumps(response))
                sys.stdout.flush()
                
            except EOFError:
                server._log_info("EOF received, shutting down...")
                break
            except json.JSONDecodeError as e:
                server._log_error("JSON decode", e)
                continue
            except Exception as e:
                server._log_error("Main loop", e)
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
    
    except KeyboardInterrupt:
        server._log_info("Server interrupted by user")
    except Exception as e:
        server._log_error("Server startup", e)


if __name__ == "__main__":
    main()
