"""LLM utilities for document summarization and correction using Qwen1.5-1.8B."""
import os
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Global model instance (lazy loaded)
_llm_model = None


def get_model_path():
    """Get the path to the LLM model file."""
    # Check environment variable first
    model_path = os.environ.get('QWEN_MODEL_PATH')
    if model_path and os.path.exists(model_path):
        return model_path
    
    # Default path in models directory
    default_path = os.path.join(os.path.dirname(__file__), 'models', 'qwen1.5-1.8b-q4_k_m.gguf')
    if os.path.exists(default_path):
        return default_path
    
    return None


def initialize_llm(model_path: Optional[str] = None, n_ctx: int = 4096, n_gpu_layers: int = 0) -> bool:
    """
    Initialize the LLM model for inference.
    
    Args:
        model_path: Path to the GGUF model file. If None, uses default path.
        n_ctx: Context window size (default: 4096)
        n_gpu_layers: Number of layers to offload to GPU (default: 0 for CPU-only)
        
    Returns:
        bool: True if initialization successful, False otherwise
    """
    global _llm_model
    
    try:
        from llama_cpp import Llama
        
        if model_path is None:
            model_path = get_model_path()
        
        if model_path is None or not os.path.exists(model_path):
            logger.error(f"Model file not found at {model_path}")
            return False
        
        logger.info(f"Loading LLM model from {model_path}")
        _llm_model = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            verbose=False
        )
        logger.info("LLM model loaded successfully")
        return True
        
    except ImportError:
        logger.error("llama-cpp-python not installed. Install with: pip install llama-cpp-python")
        return False
    except Exception as e:
        logger.error(f"Failed to initialize LLM model: {str(e)}")
        return False


def is_model_loaded() -> bool:
    """Check if the LLM model is loaded."""
    return _llm_model is not None


def create_prompt(markdown_content: str, task: str = "summarize_and_correct") -> str:
    """
    Create a prompt for the LLM based on the task.
    
    Args:
        markdown_content: The markdown content to process
        task: Type of task ("summarize_and_correct" or "correct_only")
        
    Returns:
        str: Formatted prompt for the LLM
    """
    if task == "summarize_and_correct":
        prompt = f"""<|im_start|>system
You are a helpful assistant that processes documents. Your tasks are:
1. Correct any spelling and grammar errors (especially for Bahasa Indonesia and English)
2. Reformat the markdown if needed for better readability
3. Summarize the content into concise, well-structured paragraphs
4. Maintain the original meaning and important details

Output only the corrected and summarized content in markdown format.<|im_end|>
<|im_start|>user
Process this document:

{markdown_content}<|im_end|>
<|im_start|>assistant
"""
    else:  # correct_only
        prompt = f"""<|im_start|>system
You are a helpful assistant that corrects documents. Your tasks are:
1. Correct any spelling and grammar errors (especially for Bahasa Indonesia and English)
2. Reformat the markdown if needed for better readability
3. Maintain all original content without summarizing

Output only the corrected content in markdown format.<|im_end|>
<|im_start|>user
Correct this document:

{markdown_content}<|im_end|>
<|im_start|>assistant
"""
    
    return prompt


def process_document(
    markdown_content: str,
    task: str = "summarize_and_correct",
    max_tokens: int = 2048,
    temperature: float = 0.7
) -> Optional[str]:
    """
    Process document content using the LLM.
    
    Args:
        markdown_content: The markdown content to process
        task: Type of task ("summarize_and_correct" or "correct_only")
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.0 to 1.0)
        
    Returns:
        Optional[str]: Processed content, or None if processing failed
    """
    global _llm_model
    
    if not is_model_loaded():
        logger.warning("LLM model not loaded, attempting to initialize")
        if not initialize_llm():
            logger.error("Failed to initialize LLM model")
            return None
    
    try:
        # Create prompt
        prompt = create_prompt(markdown_content, task)
        
        # Truncate input if too long (leave room for output)
        max_input_chars = 8000  # Approximate limit for context
        if len(markdown_content) > max_input_chars:
            logger.warning(f"Document too long ({len(markdown_content)} chars), truncating to {max_input_chars}")
            markdown_content = markdown_content[:max_input_chars] + "\n\n[Content truncated...]"
            prompt = create_prompt(markdown_content, task)
        
        # Generate response
        logger.info(f"Processing document with task: {task}")
        response = _llm_model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["<|im_end|>", "<|endoftext|>"],
            echo=False
        )
        
        # Extract generated text
        if response and 'choices' in response and len(response['choices']) > 0:
            generated_text = response['choices'][0]['text'].strip()
            logger.info(f"Successfully processed document ({len(generated_text)} chars)")
            return generated_text
        else:
            logger.error("No response generated from LLM")
            return None
            
    except Exception as e:
        logger.error(f"Error processing document with LLM: {str(e)}")
        return None


def generate_title(
    markdown_content: str,
    max_tokens: int = 50,
    temperature: float = 0.5
) -> Optional[str]:
    """
    Generate a predicted title for the document content using the LLM.
    
    Args:
        markdown_content: The markdown content to analyze
        max_tokens: Maximum tokens for title generation (default: 50)
        temperature: Sampling temperature (default: 0.5 for more focused output)
        
    Returns:
        Optional[str]: Predicted title, or None if generation failed
    """
    global _llm_model
    
    if not is_model_loaded():
        logger.warning("LLM model not loaded, attempting to initialize")
        if not initialize_llm():
            logger.error("Failed to initialize LLM model")
            return None
    
    try:
        # Create a specialized prompt for title generation
        prompt = f"""<|im_start|>system
You are a helpful assistant that generates concise document titles. Your task is to:
1. Read the document content carefully
2. Identify the main topic and purpose
3. Generate a clear, descriptive title (max 10-15 words)
4. Output ONLY the title without any additional text or formatting

For documents in Bahasa Indonesia, provide the title in Bahasa Indonesia.
For documents in English, provide the title in English.<|im_end|>
<|im_start|>user
Generate a title for this document:

{markdown_content[:2000]}<|im_end|>
<|im_start|>assistant
"""
        
        # Generate title
        logger.info("Generating document title with LLM")
        response = _llm_model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["<|im_end|>", "<|endoftext|>", "\n\n"],
            echo=False
        )
        
        # Extract generated text
        if response and 'choices' in response and len(response['choices']) > 0:
            title = response['choices'][0]['text'].strip()
            # Clean up the title - remove quotes, extra whitespace, etc.
            title = title.strip('"\'').strip()
            logger.info(f"Successfully generated title: {title}")
            return title
        else:
            logger.error("No title generated from LLM")
            return None
            
    except Exception as e:
        logger.error(f"Error generating title with LLM: {str(e)}")
        return None


def get_model_info() -> Dict[str, any]:
    """
    Get information about the current LLM model.
    
    Returns:
        Dict with model information (loaded status, path, etc.)
    """
    model_path = get_model_path()
    return {
        'loaded': is_model_loaded(),
        'model_path': model_path,
        'model_exists': model_path is not None and os.path.exists(model_path) if model_path else False
    }


def unload_model():
    """Unload the LLM model from memory."""
    global _llm_model
    if _llm_model is not None:
        _llm_model = None
        logger.info("LLM model unloaded")
