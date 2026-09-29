#!/usr/bin/env python3
"""
!/usr/bin/env python3

**Created:** October-15-2024  
**Updated:** August-04-2025  
**Author:** ImpressionCore Team  
**Tags:** #.mcp\impressioncore_eds\config\dataset_sources.py #api #attention_mechanism #command_line #documentation #inference #memory_management #multimodal #performance #python #pytorch #source_code #testing #training #transformer #web_interface  
**Category:** Source Code  
**Status:** Active
"""



# Academic and Research Repositories
DATASET_REPOSITORIES = {
    "academic_sources": {
        "huggingface_datasets": {
            "base_url": "https://huggingface.co/datasets",
            "api_url": "https://huggingface.co/api/datasets",
            "categories": ["text", "image", "audio", "multimodal"],
            "verification_method": "api_check",
            "download_format": ["parquet", "json", "csv", "arrow"],
            "annotation_support": True,
            "validation_sets": True,
            "notable_datasets": [
                "squad", "squad_v2", "coco", "imagenet", "librispeech", "common_voice",
                "openwebtext", "wikipedia", "bookcorpus", "conceptual_captions",
                "vqa", "clevr", "audiocaps", "clotho", "flickr30k", "wmt19",
                "glue", "super_glue", "xnli", "opus100", "cc100", "ms_marco",
                "natural_questions", "trivia_qa", "quac", "coqa", "hotpot_qa"
            ],
            "annotation_types": ["labels", "captions", "bboxes", "masks", "qa_pairs", "embeddings"],
            "embedding_friendly": True
        },
        "papers_with_code": {
            "base_url": "https://paperswithcode.com/datasets",
            "api_url": "https://paperswithcode.com/api/v1/datasets",
            "categories": ["cv", "nlp", "audio", "multimodal"],
            "verification_method": "api_check",
            "download_format": ["direct_links", "github_repos"],
            "annotation_support": True,
            "validation_sets": True,
            "notable_datasets": [
                "imagenet", "coco", "cityscapes", "pascal_voc", "ade20k",
                "kinetics", "activitynet", "something_something", "epic_kitchens"
            ],
            "annotation_types": ["benchmarks", "ground_truth", "metrics"],
            "embedding_friendly": True
        },
        "kaggle_datasets": {
            "base_url": "https://www.kaggle.com/datasets",
            "api_url": "https://www.kaggle.com/api/v1/datasets",
            "categories": ["text", "image", "audio", "tabular"],
            "verification_method": "api_check",
            "download_format": ["zip", "csv", "json"],
            "auth_required": True,
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["labels", "ground_truth", "competitions"],
            "embedding_friendly": True,
            "notable_datasets": [
                "titanic", "house_prices", "digit_recognizer", "nlp_with_disaster_tweets",
                "plant_pathology", "dogs_vs_cats", "facial_keypoints", "bike_sharing"
            ]
        },
        "zenodo": {
            "base_url": "https://zenodo.org",
            "api_url": "https://zenodo.org/api/records",
            "categories": ["scientific_data", "research"],
            "verification_method": "api_check",
            "download_format": ["various"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["metadata", "research_data", "publications"],
            "embedding_friendly": True,
            "notable_datasets": [
                "scientific_papers", "research_data", "software_archives"
            ]
        }
    },
    
    "government_sources": {
        "us_government_data": {
            "base_url": "https://data.gov",
            "api_url": "https://catalog.data.gov/api/3/action/package_search",
            "categories": ["text", "tabular", "geospatial"],
            "verification_method": "api_check",
            "download_format": ["csv", "json", "xml", "pdf"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["metadata", "classifications", "geographic_labels"],
            "embedding_friendly": False,  # Government data often not embedding-ready
            "notable_datasets": [
                "census_data", "weather_data", "economic_indicators", "health_statistics",
                "education_data", "transportation_data", "energy_data"
            ]
        },
        "european_data_portal": {
            "base_url": "https://data.europa.eu",
            "api_url": "https://data.europa.eu/api/hub/search/search",
            "categories": ["text", "tabular", "geospatial"],
            "verification_method": "api_check",
            "download_format": ["csv", "json", "xml", "rdf"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["metadata", "classifications", "geographic_labels"],
            "embedding_friendly": False,  # Government data often not embedding-ready
            "notable_datasets": [
                "eurostat", "eu_legislation", "environmental_data", "transport_data"
            ]
        },
        "world_bank_data": {
            "base_url": "https://data.worldbank.org",
            "api_url": "https://api.worldbank.org/v2/sources",
            "categories": ["economic", "social", "environmental"],
            "verification_method": "api_check",
            "download_format": ["csv", "json", "xml"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["metadata", "economic_indicators", "country_labels"],
            "embedding_friendly": False,  # Economic data often not embedding-ready
            "notable_datasets": [
                "world_development_indicators", "poverty_data", "climate_data",
                "health_data", "education_statistics", "gender_data"
            ]
        }
    },
    
    "computer_vision": {
        "visual_genome": {
            "base_url": "https://visualgenome.org",
            "download_url": "https://visualgenome.org/api/v0/api_home.html",
            "categories": ["image", "annotation", "scene_graph"],
            "verification_method": "url_check",
            "download_format": ["json", "images"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["scene_graphs", "objects", "attributes", "relationships"],
            "embedding_friendly": True,
            "notable_datasets": ["visual_genome_v1.2", "scene_graphs", "qa_pairs"]
        },
        "open_images": {
            "base_url": "https://storage.googleapis.com/openimages/web/index.html",
            "download_url": "https://storage.googleapis.com/openimages/web/download.html",
            "categories": ["image", "annotation", "detection"],
            "verification_method": "url_check",
            "download_format": ["csv", "images"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["bboxes", "labels", "masks", "relationships"],
            "embedding_friendly": True,
            "notable_datasets": ["open_images_v6", "open_images_v7", "localized_narratives"]
        },
        "imagenet": {
            "base_url": "https://image-net.org",
            "download_url": "https://image-net.org/download.php",
            "categories": ["image", "classification"],
            "verification_method": "url_check",
            "download_format": ["tar", "images"],
            "auth_required": True,
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["labels", "hierarchical_labels", "synsets"],
            "embedding_friendly": True,
            "notable_datasets": ["imagenet_1k", "imagenet_21k", "imagenet_fall11"]
        },
        "coco_dataset": {
            "base_url": "https://cocodataset.org",
            "download_url": "https://cocodataset.org/#download",
            "categories": ["image", "detection", "segmentation", "captions"],
            "verification_method": "url_check",
            "download_format": ["zip", "json", "images"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["bboxes", "masks", "captions", "keypoints"],
            "embedding_friendly": True,
            "notable_datasets": ["coco_2017", "coco_2014", "coco_stuff"]
        },
        "cifar": {
            "base_url": "https://www.cs.toronto.edu/~kriz/cifar.html",
            "download_url": "https://www.cs.toronto.edu/~kriz/cifar.html",
            "categories": ["image", "classification"],
            "verification_method": "url_check",
            "download_format": ["tar", "binary"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["labels", "fine_labels", "coarse_labels"],
            "embedding_friendly": True,
            "notable_datasets": ["cifar10", "cifar100"]
        }
    },
    
    "nlp_datasets": {
        "common_crawl": {
            "base_url": "https://commoncrawl.org",
            "download_url": "https://commoncrawl.org/get-started",
            "categories": ["text", "web_crawl"],
            "verification_method": "url_check",
            "download_format": ["warc", "wat", "wet"],
            "annotation_support": False,  # Raw web crawl data, no annotations
            "validation_sets": False,
            "annotation_types": [],
            "embedding_friendly": False,  # Requires heavy preprocessing
            "notable_datasets": ["cc_2023", "cc_2022", "cc_news"]
        },
        "project_gutenberg": {
            "base_url": "https://www.gutenberg.org",
            "download_url": "https://www.gutenberg.org/ebooks/search/?sort_order=downloads",
            "categories": ["text", "literature"],
            "verification_method": "url_check",
            "download_format": ["txt", "epub", "pdf"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["metadata", "genres", "authors"],
            "embedding_friendly": True,
            "notable_datasets": ["gutenberg_english", "gutenberg_multilingual"]
        },
        "reddit_datasets": {
            "base_url": "https://files.pushshift.io/reddit",
            "download_url": "https://files.pushshift.io/reddit/",
            "categories": ["text", "social_media"],
            "verification_method": "url_check",
            "download_format": ["zst", "json"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["upvotes", "metadata", "subreddit_labels"],
            "embedding_friendly": True,
            "notable_datasets": ["reddit_submissions", "reddit_comments"]
        },
        "wikipedia_dumps": {
            "base_url": "https://dumps.wikimedia.org",
            "download_url": "https://dumps.wikimedia.org/backup-index.html",
            "categories": ["text", "encyclopedia"],
            "verification_method": "url_check",
            "download_format": ["xml", "sql"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["categories", "links", "metadata"],
            "embedding_friendly": True,
            "notable_datasets": ["enwiki", "simplewiki", "multilingual_wiki"]
        },
        "openwebtext": {
            "base_url": "https://github.com/jcpeterson/openwebtext",
            "download_url": "https://github.com/jcpeterson/openwebtext",
            "categories": ["text", "web_text"],
            "verification_method": "github_check",
            "download_format": ["tar", "txt"],
            "annotation_support": False,  # Raw web text, no annotations
            "validation_sets": False,
            "annotation_types": [],
            "embedding_friendly": False,  # Requires preprocessing
            "notable_datasets": ["openwebtext_original", "openwebtext2"]
        }
    },
    
    "audio_datasets": {
        "mozilla_common_voice": {
            "base_url": "https://commonvoice.mozilla.org",
            "download_url": "https://commonvoice.mozilla.org/en/datasets",
            "categories": ["audio", "speech", "multilingual"],
            "verification_method": "url_check",
            "download_format": ["tar", "mp3", "wav"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["transcriptions", "speaker_demographics", "quality_votes"],
            "embedding_friendly": True,
            "notable_datasets": ["common_voice_11", "common_voice_10", "common_voice_delta"]
        },
        "librispeech": {
            "base_url": "https://www.openslr.org/12",
            "download_url": "https://www.openslr.org/12/",
            "categories": ["audio", "speech", "english"],
            "verification_method": "url_check",
            "download_format": ["tar", "flac"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["transcriptions", "alignments", "speaker_labels"],
            "embedding_friendly": True,
            "notable_datasets": ["librispeech_clean", "librispeech_other", "librispeech_dev"]
        },
        "voxceleb": {
            "base_url": "https://www.robots.ox.ac.uk/~vgg/data/voxceleb/",
            "download_url": "https://www.robots.ox.ac.uk/~vgg/data/voxceleb/",
            "categories": ["audio", "speaker_recognition"],
            "verification_method": "url_check",
            "download_format": ["zip", "wav"],
            "auth_required": True,
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["speaker_labels", "utterance_labels", "verification_pairs"],
            "embedding_friendly": True,
            "notable_datasets": ["voxceleb1", "voxceleb2"]
        },
        "freesound": {
            "base_url": "https://freesound.org",
            "api_url": "https://freesound.org/apiv2/",
            "categories": ["audio", "sound_effects"],
            "verification_method": "api_check",
            "download_format": ["wav", "mp3"],
            "auth_required": True,
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["tags", "descriptions", "categories"],
            "embedding_friendly": True,
            "notable_datasets": ["freesound_general", "freesound_tagged"]
        },
        "musicnet": {
            "base_url": "https://homes.cs.washington.edu/~thickstn/musicnet.html",
            "download_url": "https://homes.cs.washington.edu/~thickstn/musicnet.html",
            "categories": ["audio", "music"],
            "verification_method": "url_check",
            "download_format": ["npz", "csv"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["note_labels", "instrument_labels", "timing"],
            "embedding_friendly": True,
            "notable_datasets": ["musicnet_full", "musicnet_subset"]
        }
    },
    
    "multimodal_datasets": {
        "conceptual_captions": {
            "base_url": "https://ai.google.com/research/ConceptualCaptions",
            "download_url": "https://ai.google.com/research/ConceptualCaptions/download",
            "categories": ["image", "text", "captions"],
            "verification_method": "url_check",
            "download_format": ["tsv", "images"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["captions", "image_urls", "metadata"],
            "embedding_friendly": True,
            "notable_datasets": ["conceptual_captions_3m", "conceptual_captions_12m"]
        },
        "flickr30k": {
            "base_url": "https://shannon.cs.illinois.edu/DenotationGraph/",
            "download_url": "https://shannon.cs.illinois.edu/DenotationGraph/",
            "categories": ["image", "text", "captions"],
            "verification_method": "url_check",
            "download_format": ["tar", "images", "txt"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["captions", "entities", "phrases"],
            "embedding_friendly": True,
            "notable_datasets": ["flickr30k_captions", "flickr30k_entities"]
        },
        "howto100m": {
            "base_url": "https://www.di.ens.fr/~miech/howto100m/",
            "download_url": "https://www.di.ens.fr/~miech/howto100m/",
            "categories": ["video", "text", "instructional"],
            "verification_method": "url_check",
            "download_format": ["csv", "video"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["captions", "video_metadata", "timestamps"],
            "embedding_friendly": True,
            "notable_datasets": ["howto100m_full", "howto100m_subset"]
        },
        "mscoco_captions": {
            "base_url": "https://cocodataset.org/#captions-2015",
            "download_url": "https://cocodataset.org/#download",
            "categories": ["image", "text", "captions"],
            "verification_method": "url_check",
            "download_format": ["json", "images"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["captions", "image_metadata", "annotations"],
            "embedding_friendly": True,
            "notable_datasets": ["mscoco_train2017", "mscoco_val2017"]
        },
        "laion": {
            "base_url": "https://laion.ai/blog/laion-5b/",
            "download_url": "https://laion.ai/blog/laion-5b/",
            "categories": ["image", "text", "web_scale"],
            "verification_method": "url_check",
            "download_format": ["parquet", "metadata"],
            "annotation_support": True,
            "validation_sets": False,  # Web-scale data, no official validation splits
            "annotation_types": ["alt_text", "captions", "metadata"],
            "embedding_friendly": True,
            "notable_datasets": ["laion_400m", "laion_2b", "laion_5b"]
        }
    },
    
    "ai_training_datasets": {
        "pile": {
            "base_url": "https://pile.eleuther.ai",
            "download_url": "https://mystic.the-eye.eu/public/AI/pile/",
            "categories": ["text", "large_scale"],
            "verification_method": "url_check",
            "download_format": ["jsonl", "zst"],
            "annotation_support": False,  # Raw text, minimal annotations
            "validation_sets": False,
            "annotation_types": ["source_metadata"],
            "embedding_friendly": False,  # Requires significant preprocessing
            "notable_datasets": ["pile_800gb", "pile_deduplicated"]
        },
        "redpajama": {
            "base_url": "https://github.com/togethercomputer/RedPajama-Data",
            "download_url": "https://huggingface.co/datasets/togethercomputer/RedPajama-Data-1T",
            "categories": ["text", "large_scale"],
            "verification_method": "github_check",
            "download_format": ["jsonl", "parquet"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["source_metadata", "quality_scores"],
            "embedding_friendly": True,
            "notable_datasets": ["redpajama_1t", "redpajama_v2"]
        },
        "refinedweb": {
            "base_url": "https://huggingface.co/datasets/tiiuae/falcon-refinedweb",
            "download_url": "https://huggingface.co/datasets/tiiuae/falcon-refinedweb",
            "categories": ["text", "web_crawl", "filtered"],
            "verification_method": "api_check",
            "download_format": ["parquet", "jsonl"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["quality_scores", "deduplication_metadata"],
            "embedding_friendly": True,
            "notable_datasets": ["refinedweb_1t", "refinedweb_filtered"]
        },
        "c4": {
            "base_url": "https://github.com/google-research/text-to-text-transfer-transformer",
            "download_url": "https://huggingface.co/datasets/c4",
            "categories": ["text", "common_crawl_filtered"],
            "verification_method": "api_check",
            "download_format": ["json", "tfrecord"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["quality_filters", "language_metadata"],
            "embedding_friendly": True,
            "notable_datasets": ["c4_en", "c4_multilingual"]
        },
        "dolma": {
            "base_url": "https://github.com/allenai/dolma",
            "download_url": "https://huggingface.co/datasets/allenai/dolma",
            "categories": ["text", "research_corpus"],
            "verification_method": "github_check",
            "download_format": ["jsonl", "parquet"],
            "annotation_support": True,
            "validation_sets": True,
            "annotation_types": ["source_metadata", "quality_scores"],
            "embedding_friendly": True,
            "notable_datasets": ["dolma_v1_6", "dolma_books", "dolma_cc"]
        }
    },
    
    "specialized_sources": {
        "medical_datasets": {
            "base_url": "https://physionet.org",
            "api_url": "https://physionet.org/about/",
            "categories": ["medical", "time_series", "text"],
            "verification_method": "url_check",
            "download_format": ["csv", "wfdb", "edf"],
            "auth_required": True,
            "notable_datasets": ["mimic_iii", "mimic_iv", "eicu", "ptb_xl"]
        },
        "scientific_papers": {
            "base_url": "https://www.semanticscholar.org",
            "api_url": "https://api.semanticscholar.org",
            "categories": ["text", "scientific", "citations"],
            "verification_method": "api_check",
            "download_format": ["json", "jsonl"],
            "notable_datasets": ["semantic_scholar_corpus", "arxiv_papers", "pubmed_abstracts"]
        },
        "financial_data": {
            "base_url": "https://www.alphavantage.co",
            "api_url": "https://www.alphavantage.co/documentation/",
            "categories": ["time_series", "financial"],
            "verification_method": "api_check",
            "download_format": ["json", "csv"],
            "auth_required": True,
            "notable_datasets": ["stock_prices", "forex_rates", "crypto_prices"]
        },
        "legal_datasets": {
            "base_url": "https://case.law",
            "api_url": "https://api.case.law",
            "categories": ["text", "legal"],
            "verification_method": "api_check",
            "download_format": ["json", "xml"],
            "notable_datasets": ["caselaw_access_project", "legal_opinions"]
        }
    },
    
    "repository_aggregators": {
        "figshare": {
            "base_url": "https://figshare.com",
            "api_url": "https://api.figshare.com/v2/articles",
            "categories": ["research_data", "academic"],
            "verification_method": "api_check",
            "download_format": ["various"],
            "notable_datasets": ["research_outputs", "datasets", "figures"]
        },
        "dryad": {
            "base_url": "https://datadryad.org",
            "api_url": "https://datadryad.org/api/v2/datasets",
            "categories": ["scientific_data", "research"],
            "verification_method": "api_check",
            "download_format": ["various"],
            "notable_datasets": ["ecological_data", "evolutionary_data", "behavioral_data"]
        },
        "ieee_dataport": {
            "base_url": "https://ieee-dataport.org",
            "api_url": "https://ieee-dataport.org/api",
            "categories": ["engineering", "technical"],
            "verification_method": "url_check",
            "download_format": ["various"],
            "auth_required": True,
            "notable_datasets": ["signal_processing", "communications", "power_systems"]
        }
    },
    
    "additional_discovered_sources": {
        "uci_ml_repository": {
            "base_url": "https://archive.ics.uci.edu",
            "api_url": "https://archive.ics.uci.edu/api",
            "categories": ["classification", "regression", "clustering"],
            "verification_method": "url_check",
            "download_format": ["csv", "arff", "data"],
            "notable_datasets": [
                "iris", "heart_disease", "wine_quality", "breast_cancer_wisconsin",
                "adult", "bank_marketing", "car_evaluation", "mushroom",
                "glass", "ecoli", "yeast", "dermatology", "zoo"
            ]
        },
        "google_research_datasets": {
            "base_url": "https://github.com/google-research/",
            "download_url": "https://github.com/google-research/meta-dataset",
            "categories": ["meta_learning", "few_shot", "research"],
            "verification_method": "github_check",
            "download_format": ["tensorflow_datasets", "json"],
            "notable_datasets": ["meta_dataset", "omniglot", "aircraft", "cu_birds", "dtd"]
        },
        "openml": {
            "base_url": "https://www.openml.org",
            "api_url": "https://www.openml.org/api/v1",
            "categories": ["ml_research", "benchmarks", "competition"],
            "verification_method": "api_check",
            "download_format": ["arff", "csv", "json"],
            "notable_datasets": [
                "openml_cc18", "automl_benchmark", "amlb_datasets",
                "classification_suite", "regression_suite"
            ]
        },
        "awesome_public_datasets": {
            "base_url": "https://github.com/awesomedata/awesome-public-datasets",
            "download_url": "https://github.com/awesomedata/awesome-public-datasets",
            "categories": ["aggregated", "curated", "public"],
            "verification_method": "github_check",
            "download_format": ["various"],
            "notable_datasets": ["government_data", "biology", "climate", "economics", "education"]
        },
        "tonia_ai_datasets": {
            "base_url": "https://tonia.ai/datasets.html",
            "download_url": "https://tonia.ai/datasets.html",
            "categories": ["ai_research", "deep_learning"],
            "verification_method": "url_check",
            "download_format": ["various"],
            "notable_datasets": ["deep_learning_datasets", "computer_vision", "nlp_datasets"]
        },
        "simons_foundation": {
            "base_url": "https://www.simonsfoundation.org",
            "download_url": "https://www.simonsfoundation.org/datasets",
            "categories": ["scientific", "research", "biology", "mathematics"],
            "verification_method": "url_check",
            "download_format": ["various"],
            "notable_datasets": ["scientific_datasets", "mathematical_research", "biological_data"]
        },
        "big_data_analytics_news": {
            "base_url": "https://bigdataanalyticsnews.com/datasets/",
            "download_url": "https://bigdataanalyticsnews.com/datasets/",
            "categories": ["big_data", "analytics", "business"],
            "verification_method": "url_check",
            "download_format": ["csv", "json", "sql"],
            "notable_datasets": ["business_datasets", "financial_data", "marketing_data"]
        },
        "reddit_datasets_community": {
            "base_url": "https://www.reddit.com/r/datasets/",
            "api_url": "https://www.reddit.com/r/datasets.json",
            "categories": ["community", "user_generated", "diverse"],
            "verification_method": "api_check",
            "download_format": ["various"],
            "notable_datasets": ["community_datasets", "user_contributions", "niche_datasets"]
        },
        "aws_open_data": {
            "base_url": "https://registry.opendata.aws",
            "api_url": "https://registry.opendata.aws/api",
            "categories": ["cloud", "large_scale", "enterprise"],
            "verification_method": "api_check",
            "download_format": ["s3", "parquet", "csv", "json"],
            "notable_datasets": [
                "common_crawl_aws", "sentinel_2", "noaa_weather", "nasa_open_data",
                "allen_brain_atlas", "covid_19_data", "landsat_8", "modis"
            ]
        },
        "microsoft_research": {
            "base_url": "https://msropendata.com",
            "api_url": "https://msropendata.com/api",
            "categories": ["research", "ai", "computer_science"],
            "verification_method": "api_check",
            "download_format": ["various"],
            "notable_datasets": [
                "msra_research_datasets", "kinect_datasets", "speech_datasets",
                "computer_vision_datasets", "nlp_datasets"
            ]
        },
        "stanford_datasets": {
            "base_url": "https://snap.stanford.edu/data/",
            "download_url": "https://snap.stanford.edu/data/",
            "categories": ["network_analysis", "social_networks", "graph_data"],
            "verification_method": "url_check",
            "download_format": ["txt", "gz", "json"],
            "notable_datasets": [
                "facebook_networks", "twitter_networks", "amazon_networks",
                "collaboration_networks", "web_graphs", "road_networks"
            ]
        },
        "facebook_research": {
            "base_url": "https://research.fb.com/datasets/",
            "download_url": "https://github.com/facebookresearch/",
            "categories": ["ai_research", "deep_learning", "social"],
            "verification_method": "url_check",
            "download_format": ["various"],
            "notable_datasets": [
                "pytorch_datasets", "fairseq_datasets", "detectron2_datasets",
                "social_network_data", "language_models"
            ]
        },
        "google_dataset_search": {
            "base_url": "https://datasetsearch.research.google.com",
            "api_url": "https://developers.google.com/search/docs/data-types/dataset",
            "categories": ["aggregator", "search_engine", "metadata"],
            "verification_method": "url_check",
            "download_format": ["metadata_only"],
            "notable_datasets": ["indexed_datasets", "structured_data", "research_datasets"]
        },
        "ieee_datasets": {
            "base_url": "https://ieee-dataport.org/datasets",
            "api_url": "https://ieee-dataport.org/api",
            "categories": ["engineering", "technical", "ieee_research"],
            "verification_method": "api_check",
            "download_format": ["various"],
            "auth_required": True,
            "notable_datasets": [
                "signal_processing_datasets", "communication_datasets",
                "power_systems", "biomedical_engineering", "robotics_datasets"
            ]
        },
        "nature_datasets": {
            "base_url": "https://www.nature.com/sdata/",
            "api_url": "https://www.nature.com/sdata/api",
            "categories": ["scientific", "peer_reviewed", "research"],
            "verification_method": "api_check",
            "download_format": ["various"],
            "notable_datasets": [
                "scientific_data_papers", "nature_research", "peer_reviewed_datasets",
                "biological_datasets", "environmental_data"
            ]
        },
        "plos_one_datasets": {
            "base_url": "https://journals.plos.org/plosone/",
            "api_url": "https://journals.plos.org/plosone/api",
            "categories": ["scientific", "open_access", "research"],
            "verification_method": "api_check",
            "download_format": ["various"],
            "notable_datasets": [
                "plos_research_data", "open_access_datasets", "multidisciplinary_data"
            ]
        }
    },
    
    # Embedding-Specific Datasets (With Rich Annotations and Validation Sets)
    "embedding_datasets": {
        "sentence_transformers_datasets": {
            "base_url": "https://huggingface.co/sentence-transformers",
            "download_url": "https://huggingface.co/datasets/sentence-transformers",
            "categories": ["text", "embeddings", "similarity"],
            "verification_method": "api_check",
            "download_format": ["parquet", "json", "csv"],
            "annotation_support": True,
            "validation_sets": True,
            "embedding_friendly": True,
            "annotation_types": ["similarity_scores", "labels", "pairs"],
            "notable_datasets": [
                "all-nli", "stsb_multi_mt", "quora-question-pairs", 
                "ms-marco-passage", "natural-questions", "trivia-qa"
            ]
        },
        "semantic_textual_similarity": {
            "base_url": "https://ixa2.si.ehu.eus/stswiki/index.php/STSbenchmark",
            "download_url": "https://huggingface.co/datasets/stsb_multi_mt",
            "categories": ["text", "similarity", "embeddings"],
            "verification_method": "url_check",
            "download_format": ["tsv", "csv"],
            "annotation_support": True,
            "validation_sets": True,
            "embedding_friendly": True,
            "annotation_types": ["similarity_scores", "sentence_pairs"],
            "notable_datasets": ["stsb", "sick", "sts12", "sts13", "sts14", "sts15", "sts16"]
        },
        "natural_language_inference": {
            "base_url": "https://huggingface.co/datasets/sentence-transformers/all-nli",
            "download_url": "https://huggingface.co/datasets/sentence-transformers/all-nli",
            "categories": ["text", "inference", "embeddings"],
            "verification_method": "api_check",
            "download_format": ["parquet", "json"],
            "annotation_support": True,
            "validation_sets": True,
            "embedding_friendly": True,
            "annotation_types": ["premise", "hypothesis", "labels"],
            "notable_datasets": ["snli", "multinli", "xnli", "anli"]
        },
        "question_answering_embeddings": {
            "base_url": "https://huggingface.co/datasets/ms_marco",
            "download_url": "https://microsoft.github.io/msmarco/",
            "categories": ["text", "retrieval", "qa", "embeddings"],
            "verification_method": "url_check",
            "download_format": ["tsv", "json"],
            "annotation_support": True,
            "validation_sets": True,
            "embedding_friendly": True,
            "annotation_types": ["queries", "passages", "relevance_scores"],
            "notable_datasets": ["ms_marco_passage", "ms_marco_document", "natural_questions_open"]
        },
        "paraphrase_detection": {
            "base_url": "https://quoradata.quora.com/First-Quora-Dataset-Release-Question-Pairs",
            "download_url": "https://huggingface.co/datasets/quora",
            "categories": ["text", "similarity", "duplicate_detection"],
            "verification_method": "url_check",
            "download_format": ["tsv", "csv"],
            "annotation_support": True,
            "validation_sets": True,
            "embedding_friendly": True,
            "annotation_types": ["duplicate_labels", "question_pairs"],
            "notable_datasets": ["quora_question_pairs", "paws", "mrpc"]
        },
        "cross_lingual_embeddings": {
            "base_url": "https://huggingface.co/datasets/xnli",
            "download_url": "https://www.nyu.edu/projects/bowman/xnli/",
            "categories": ["text", "multilingual", "embeddings"],
            "verification_method": "url_check",
            "download_format": ["jsonl", "tsv"],
            "annotation_support": True,
            "validation_sets": True,
            "embedding_friendly": True,
            "annotation_types": ["premise", "hypothesis", "labels", "language_codes"],
            "notable_datasets": ["xnli", "paws-x", "tatoeba", "bucc"]
        }
    },
    
    # Multimodal Embedding Datasets (Cross-modal Annotations)
    "multimodal_embedding_datasets": {
        "image_text_embeddings": {
            "base_url": "https://huggingface.co/datasets/conceptual_captions",
            "download_url": "https://ai.google.com/research/ConceptualCaptions/download",
            "categories": ["image", "text", "embeddings"],
            "verification_method": "api_check",
            "download_format": ["parquet", "images"],
            "annotation_support": True,
            "validation_sets": True,
            "embedding_friendly": True,
            "annotation_types": ["captions", "image_urls", "alt_text"],
            "notable_datasets": ["conceptual_captions_3m", "conceptual_captions_12m"]
        },
        "visual_question_answering_embeddings": {
            "base_url": "https://visualqa.org",
            "download_url": "https://visualqa.org/download.html",
            "categories": ["image", "text", "qa", "embeddings"],
            "verification_method": "url_check",
            "download_format": ["json", "images"],
            "annotation_support": True,
            "validation_sets": True,
            "embedding_friendly": True,
            "annotation_types": ["questions", "answers", "rationales", "image_features"],
            "notable_datasets": ["vqa_v2", "gqa", "clevr", "visual7w"]
        },
        "image_captioning_embeddings": {
            "base_url": "https://cocodataset.org/#captions-2015",
            "download_url": "https://cocodataset.org/#download",
            "categories": ["image", "text", "captions", "embeddings"],
            "verification_method": "url_check",
            "download_format": ["json", "images"],
            "annotation_support": True,
            "validation_sets": True,
            "embedding_friendly": True,
            "annotation_types": ["captions", "image_ids", "caption_ids"],
            "notable_datasets": ["mscoco_captions", "flickr30k", "flickr8k"]
        },
        "audio_text_embeddings": {
            "base_url": "https://audiocaps.github.io",
            "download_url": "https://github.com/cdjkim/audiocaps",
            "categories": ["audio", "text", "embeddings"],
            "verification_method": "github_check",
            "download_format": ["csv", "audio"],
            "annotation_support": True,
            "validation_sets": True,
            "embedding_friendly": True,
            "annotation_types": ["audio_captions", "timestamps", "youtube_ids"],
            "notable_datasets": ["audiocaps", "clotho", "fsd50k"]
        }
    }
}

# Verification and Health Check Configuration
VERIFICATION_CONFIG = {
    "timeout": 30,
    "retry_attempts": 3,
    "health_check_interval": 24,  # hours
    "parallel_checks": 5,
    "user_agent": "ImpressionCore-EDS/2.0 (Research/Educational Use)",
    "cache_duration": 86400,  # 24 hours in seconds
    "max_response_size": "10MB"
}

# Download Configuration
DOWNLOAD_CONFIG = {
    "max_file_size": "10GB",
    "concurrent_downloads": 3,
    "verify_checksums": True,
    "create_metadata": True,
    "compression_formats": ["gzip", "bz2", "xz", "zip", "tar", "7z"],
    "supported_formats": ["csv", "json", "jsonl", "parquet", "arrow", "txt", "xml", "yaml", "tsv"],
    "chunk_size": "8MB",
    "resume_downloads": True
}

# Enhanced Annotation and Validation Configuration for Embedding Training
ANNOTATION_REQUIREMENTS = {
    "min_annotation_coverage": 0.8,  # 80% of data must have annotations
    "require_validation_split": True,
    "min_validation_size": 0.1,      # 10% validation set minimum
    "max_validation_size": 0.3,      # 30% validation set maximum
    "require_test_split": False,      # Optional test split
    "annotation_quality_threshold": 0.7,  # Minimum annotation quality score
    
    # Annotation types required for different use cases
    "annotation_types_required": {
        "embedding": {
            "mandatory": ["labels", "pairs", "similarity_scores"],
            "recommended": ["validation_sets", "metadata"],
            "optional": ["quality_scores", "confidence_scores"]
        },
        "classification": {
            "mandatory": ["labels", "validation_sets"],
            "recommended": ["class_weights", "metadata"],
            "optional": ["confidence_scores", "human_verification"]
        },
        "qa": {
            "mandatory": ["questions", "answers", "context"],
            "recommended": ["validation_sets", "answer_spans"],
            "optional": ["rationales", "difficulty_scores"]
        },
        "multimodal": {
            "mandatory": ["cross_modal_pairs", "validation_sets"],
            "recommended": ["captions", "metadata"],
            "optional": ["grounding", "attention_maps"]
        },
        "speech": {
            "mandatory": ["transcriptions", "validation_sets"],
            "recommended": ["alignments", "speaker_metadata"],
            "optional": ["phoneme_labels", "quality_scores"]
        },
        "vision": {
            "mandatory": ["labels", "validation_sets"],
            "recommended": ["bboxes", "metadata"],
            "optional": ["masks", "keypoints", "attributes"]
        }
    }
}

# Use Case Mappings with Enhanced Annotation Requirements
USE_CASE_MAPPINGS = {
    "embedding": {
        "primary": [
            "stsb_benchmark", "all_nli", "quora_question_pairs", 
            "ms_marco_passages", "natural_questions"
        ],
        "secondary": [
            "sentence_transformers_datasets", "conceptual_captions",
            "cross_lingual_embeddings"
        ],
        "evaluation": ["mteb", "glue", "super_glue"],
        "annotation_priority": ["similarity_scores", "pairs", "labels"],
        "validation_required": True,
        "min_data_size": 10000,  # Minimum samples for embedding training
        "recommended_data_size": 100000
    },
    "conversation": {
        "primary": ["squad", "squad_v2", "quac", "coqa", "all_nli"],
        "secondary": ["natural_questions", "ms_marco", "trivia_qa"],
        "evaluation": ["daily_dialog", "multi_woz"],
        "annotation_priority": ["qa_pairs", "context", "labels"],
        "validation_required": True,
        "min_data_size": 5000,
        "recommended_data_size": 50000
    },
    "image_classification": {
        "primary": ["imagenet", "coco_dataset", "open_images"],
        "secondary": ["cityscapes", "visual_genome"],
        "evaluation": ["imagenet_val", "coco_test"],
        "annotation_priority": ["class_labels", "bboxes", "validation_sets"],
        "validation_required": True,
        "min_data_size": 1000,
        "recommended_data_size": 10000
    },
    "multimodal": {
        "primary": ["visual_qa", "conceptual_captions", "flickr30k"],
        "secondary": ["mscoco_captions", "visual_genome"],
        "evaluation": ["vqa_v2", "nocaps"],
        "annotation_priority": ["cross_modal_pairs", "captions", "grounding"],
        "validation_required": True,
        "min_data_size": 5000,
        "recommended_data_size": 25000
    }
}

# Memory Requirements Estimation (in GB)
MEMORY_ESTIMATES = {
    # Small datasets (< 1GB)
    "cifar10": 0.2,
    "cifar100": 0.2,
    "squad": 0.1,
    "glue": 0.3,
    "iris": 0.001,  # Very small
    "heart_disease": 0.001,
    "wine_quality": 0.001,
    "breast_cancer_wisconsin": 0.001,
    "adult": 0.1,
    "bank_marketing": 0.1,
    
    # Medium datasets (1-5GB)
    "librispeech": 2.0,
    "common_voice": 3.0,
    "flickr30k": 1.5,
    "conceptual_captions": 4.0,
    "wikipedia": 3.5,
    "openml_cc18": 2.0,
    "meta_dataset": 3.0,
    "stanford_networks": 2.5,
    
    # Large datasets (5-20GB)
    "imagenet": 15.0,
    "coco_dataset": 8.0,
    "openwebtext": 12.0,
    "laion_400m": 18.0,
    "aws_open_data": 10.0,  # Variable
    "common_crawl_aws": 15.0,
    
    # Very large datasets (20GB+)
    "pile": 80.0,
    "redpajama": 120.0,
    "refinedweb": 150.0,
    "laion_2b": 200.0,
    "laion_5b": 500.0,
    "common_crawl": 1000.0,
    
    # Repository estimates (average dataset size)
    "zenodo": 2.0,
    "us_government_data": 1.5,
    "european_data_portal": 1.0,
    "world_bank_data": 0.5,
    "visual_genome": 3.0,
    "open_images": 12.0,
    "mozilla_common_voice": 4.0,
    "voxceleb": 6.0,
    "freesound": 2.0,
    "musicnet": 1.0,
    "mscoco_captions": 4.0,
    "howto100m": 25.0,
    "c4": 40.0,
    "dolma": 60.0
}

# Quality Scores for Embedding Training
QUALITY_SCORES = {
    # High quality, well-maintained datasets optimized for embeddings
    "huggingface_datasets": 0.95,  # Curated, standardized
    "squad": 0.95,
    "squad_v2": 0.95,
    "natural_questions": 0.90,
    "ms_marco_passages": 0.92,
    "conceptual_captions": 0.88,
    "flickr30k": 0.90,
    "imagenet": 0.95,
    "coco_dataset": 0.95,
    "librispeech": 0.90,
    "common_voice": 0.85,
    
    # Good quality datasets with annotations
    "papers_with_code": 0.90,  # Research-backed
    "kaggle_datasets": 0.82,   # Competition-validated
    "zenodo": 0.85,            # Academic quality
    "visual_genome": 0.88,     # Rich annotations
    "open_images": 0.85,       # Large scale, good labels
    "cifar10": 0.90,           # Classic benchmark
    "cifar100": 0.88,          # Classic benchmark
    "voxceleb": 0.85,          # Speaker recognition standard
    "musicnet": 0.80,          # Music annotation quality
    
    # Community and web-scale sources
    "mscoco_captions": 0.88,
    "howto100m": 0.75,         # Large but noisy
    "laion": 0.70,             # Web-scale, variable quality
    "redpajama": 0.85,         # Curated training data
    "refinedweb": 0.80,        # Filtered web data
    "c4": 0.85,                # Cleaned common crawl
    "dolma": 0.82,             # Research corpus
    
    # Government and institutional sources
    "us_government_data": 0.85,
    "european_data_portal": 0.83,
    "world_bank_data": 0.88,
    
    # Raw or unfiltered sources
    "pile": 0.75,              # Large but unfiltered
    "common_crawl": 0.60,      # Raw web data
    "openwebtext": 0.70,       # Reddit-filtered but still noisy
    "project_gutenberg": 0.85, # High quality text
    "wikipedia_dumps": 0.90,   # High quality, structured
    "reddit_datasets": 0.65,   # Social media, variable quality
    
    # Specialized medical/scientific
    "medical_datasets": 0.90,  # High quality, peer-reviewed
    "freesound": 0.75          # Community audio, variable quality
}

# Basic Quality Scores for Compatibility
QUALITY_SCORES = {
    # High quality, well-maintained datasets
    "imagenet": 0.95,
    "coco_dataset": 0.95,
    "squad": 0.90,
    "librispeech": 0.90,
    "common_voice": 0.85,
    "iris": 0.90,  # Classic, well-validated
    
    # Good quality datasets
    "conceptual_captions": 0.80,
    "flickr30k": 0.85,
    "openwebtext": 0.80,
    "wikipedia": 0.85,
    "pile": 0.90,
    "cifar10": 0.90,
    "cifar100": 0.85,
    
    # Experimental or newer datasets
    "redpajama": 0.85,
    "refinedweb": 0.80,
    "laion": 0.75,
    "dolma": 0.80,
    
    # Community and aggregated sources
    "huggingface_datasets": 0.90,
    "kaggle_datasets": 0.80,
    "papers_with_code": 0.85,
    "zenodo": 0.85,
    
    # Government sources
    "us_government_data": 0.80,
    "european_data_portal": 0.75,
    "world_bank_data": 0.85,
    
    # Default for unknown datasets
    "default": 0.70
}
