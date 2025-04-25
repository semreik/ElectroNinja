#!/usr/bin/env python3
"""
Ingest examples from metadata.json into the FAISS vector store
"""

import os
import json
import sys
import logging
from dotenv import load_dotenv

# Setup path to allow imports from the main project
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the vector store
from electroninja.config.settings import Config
from electroninja.llm.vector_store import VectorStore
from electroninja.config import logger

# Load environment variables (needed for OpenAI API key)
load_dotenv()

def extract_clean_asc_code(asc_code):
    """
    Extract only the pure ASC code starting from 'Version 4'
    This ensures we don't include descriptions in the ASC code examples
    """
    if "Version 4" in asc_code:
        idx = asc_code.find("Version 4")
        return asc_code[idx:].strip()
    return asc_code.strip()

def ingest_examples():
    """
    Ingest examples from metadata.json into the vector database
    """
    # Initialize the vector store with config
    config = Config()
    vector_store = VectorStore(config)
    
    # Path to metadata.json
    metadata_path = os.path.join(config.EXAMPLES_DIR, "metadata.json")
    
    # Check if metadata file exists
    if not os.path.exists(metadata_path):
        logger.error(f"Metadata file not found: {metadata_path}")
        return False
    
    # Read metadata.json
    logger.info(f"Reading examples from {metadata_path}")
    with open(metadata_path, "r", encoding="utf-8") as f:
        examples = json.load(f)
    
    logger.info(f"Found {len(examples)} examples in metadata.json")
    
    # Process each example
    successful = 0
    for i, example in enumerate(examples, 1):
        asc_path = example.get("asc_path")
        description = example.get("description", "No description")
        
        # Validate path
        if not asc_path:
            logger.warning(f"Example {i}: Missing asc_path")
            continue
            
        # Convert relative path if needed
        if not os.path.isabs(asc_path):
            asc_path = os.path.join(config.BASE_DIR, asc_path)
        
        # Check if file exists
        if not os.path.exists(asc_path):
            logger.warning(f"Example {i}: File not found: {asc_path}")
            continue
        
        # Read ASC file
        try:
            with open(asc_path, "r", encoding="utf-8") as asc_file:
                full_asc_code = asc_file.read().strip()
            
            # Extract only the pure ASC code starting from "Version 4"
            clean_asc_code = extract_clean_asc_code(full_asc_code)
            
            # Store the embeddings for the combined text, but keep ASC code separate from description
            # in the storage to avoid duplication in prompts
            combined_text = f"{description}\n\n{clean_asc_code}"
            
            # Add to vector store with properly separated fields
            if vector_store.add_document(combined_text, metadata={
                "asc_path": asc_path, 
                "description": description, 
                "pure_asc_code": clean_asc_code
            }):
                successful += 1
                logger.info(f"Example {i}: Added {os.path.basename(asc_path)}")
            else:
                logger.warning(f"Example {i}: Failed to add {os.path.basename(asc_path)}")
        
        except Exception as e:
            logger.error(f"Example {i}: Error processing {os.path.basename(asc_path)}: {str(e)}")
    
    # Save the index
    if successful > 0:
        if vector_store.save():
            logger.info(f"Successfully ingested {successful} examples out of {len(examples)}")
            logger.info(f"Index saved to {config.VECTOR_DB_INDEX}")
            logger.info(f"Metadata saved to {config.VECTOR_DB_METADATA}")
            return True
        else:
            logger.error("Failed to save index")
            return False
    else:
        logger.error("No examples were successfully ingested")
        return False

if __name__ == "__main__":
    # Configure logging for command-line usage
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run ingestion
    print("Starting ingestion of examples...")
    result = ingest_examples()
    
    if result:
        print("\nIngestion completed successfully!")
        print(f"Check the logs for details.")
    else:
        print("\nIngestion failed or completed with errors.")
        print("Check the logs for details.")