# LLM Setup Guide - Qwen1.5-1.8B Integration

This guide explains how to set up and use the Qwen1.5-1.8B model for document summarization and correction in MarkItDown API.

## Overview

The LLM integration adds the following capabilities after markdown conversion:
- **Spelling and grammar correction** (optimized for Bahasa Indonesia and English)
- **Markdown reformatting** for better readability
- **Content summarization** into concise paragraphs
- All processing happens **locally** with no external API calls

## Prerequisites

- Python 3.8 or higher
- At least 4GB of free RAM
- ~1.5GB of disk space for the model file
- CPU-based inference (GPU optional but not required)

## Installation

### 1. Install Python Dependencies

The required dependencies are already in `requirements.txt`:

```bash
pip install -r requirements.txt
```

This will install `llama-cpp-python`, which provides efficient CPU-based inference for GGUF quantized models.

### 2. Download the Qwen1.5-1.8B Model

You need to download a quantized GGUF version of Qwen1.5-1.8B. We recommend the Q4_K_M quantization for a good balance of quality and performance.

#### Option A: Manual Download (Recommended)

1. Create a models directory:
```bash
mkdir -p models
```

2. Download the model from Hugging Face:

```bash
# Using wget
wget https://huggingface.co/Qwen/Qwen1.5-1.8B-Chat-GGUF/resolve/main/qwen1_5-1_8b-chat-q4_k_m.gguf -O models/qwen1.5-1.8b-q4_k_m.gguf

# Or using curl
curl -L https://huggingface.co/Qwen/Qwen1.5-1.8B-Chat-GGUF/resolve/main/qwen1_5-1_8b-chat-q4_k_m.gguf -o models/qwen1.5-1.8b-q4_k_m.gguf
```

3. Verify the download:
```bash
ls -lh models/qwen1.5-1.8b-q4_k_m.gguf
```

The file should be approximately 1.1-1.2 GB.

#### Option B: Using Hugging Face CLI

```bash
# Install huggingface-hub
pip install huggingface-hub

# Download the model
huggingface-cli download Qwen/Qwen1.5-1.8B-Chat-GGUF qwen1_5-1_8b-chat-q4_k_m.gguf --local-dir models --local-dir-use-symlinks False
```

#### Option C: Custom Model Path

If you prefer to store the model elsewhere, you can set the `QWEN_MODEL_PATH` environment variable:

```bash
export QWEN_MODEL_PATH=/path/to/your/model.gguf
```

## Configuration

### Enable LLM Processing

1. Start the application:
```bash
python app.py
```

2. Log in to the web interface (default: http://localhost:5000)

3. Navigate to **Settings** page

4. Configure LLM options:
   - **Enable LLM Processing**: Check to enable
   - **LLM Task**: Choose between:
     - `summarize_and_correct`: Corrects and summarizes content
     - `correct_only`: Only corrects without summarizing
   - **Max Tokens**: Maximum length of generated output (default: 2048)
   - **Temperature**: Creativity level 0.0-1.0 (default: 0.7, lower = more focused)

5. Save the configuration

### Environment Variables

You can also configure the model path via environment variables:

```bash
# Set custom model path
export QWEN_MODEL_PATH=/path/to/qwen1.5-1.8b-q4_k_m.gguf

# Run the application
python app.py
```

## Model Variants

Different quantization levels are available with varying quality/performance tradeoffs:

| Quantization | File Size | RAM Usage | Quality | Speed |
|--------------|-----------|-----------|---------|-------|
| Q2_K         | ~700 MB   | ~2 GB     | Good    | Fast  |
| Q4_K_M (Recommended) | ~1.1 GB | ~3 GB | Very Good | Medium |
| Q5_K_M       | ~1.3 GB   | ~3.5 GB   | Excellent | Slower |
| Q8_0         | ~1.9 GB   | ~4 GB     | Best    | Slowest |

Download different variants by replacing the model filename in the download URL.

## Usage

### Via Web Interface

1. Upload a document through the web interface
2. If LLM processing is enabled, you'll see both:
   - **Original Markdown**: Raw converted content
   - **Summary**: LLM-processed and corrected content

### Via API

```bash
# Convert a document
curl -X POST http://localhost:5000/api/convert \
  -F "file=@document.pdf" \
  -H "Cookie: session=YOUR_SESSION_COOKIE"

# Response includes both markdown_content and summary_content
{
  "success": true,
  "id": 1,
  "filename": "document.pdf",
  "markdown_content": "# Original Content...",
  "summary_content": "# Corrected and Summarized Content...",
  "upload_time": "2024-01-01T12:00:00",
  "file_size": 1024
}
```

## Performance Tips

### CPU Optimization

By default, llama-cpp-python uses CPU inference. You can optimize performance:

1. **Use multiple threads**: llama-cpp-python automatically uses available CPU cores

2. **Adjust context window**: For shorter documents, you can reduce memory usage by modifying `llm_utils.py`:
```python
initialize_llm(n_ctx=2048)  # Default is 4096
```

### GPU Acceleration (Optional)

If you have a compatible GPU, you can enable GPU acceleration:

1. Install llama-cpp-python with GPU support:
```bash
# For NVIDIA GPUs with CUDA
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# For AMD GPUs with ROCm
CMAKE_ARGS="-DLLAMA_HIPBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# For Apple Silicon (Metal)
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

2. Modify `llm_utils.py` to use GPU layers:
```python
initialize_llm(n_gpu_layers=35)  # Offload layers to GPU
```

## Troubleshooting

### Model Not Found

**Error**: `Model file not found`

**Solution**: Verify the model path:
```bash
# Check default location
ls -lh models/qwen1.5-1.8b-q4_k_m.gguf

# Or set custom path
export QWEN_MODEL_PATH=/full/path/to/model.gguf
```

### Out of Memory

**Error**: Process killed or memory error

**Solutions**:
1. Use a smaller quantization (Q2_K instead of Q4_K_M)
2. Reduce context window in `llm_utils.py`
3. Close other applications
4. Process smaller documents

### Slow Processing

**Issue**: LLM processing takes too long

**Solutions**:
1. Use a smaller quantization (Q4_K_M or Q2_K)
2. Reduce `max_tokens` in settings (e.g., 1024 instead of 2048)
3. Use `correct_only` task instead of `summarize_and_correct`
4. Enable GPU acceleration if available

### Poor Quality Output

**Issue**: Corrections or summaries are not good

**Solutions**:
1. Use a higher quality quantization (Q5_K_M or Q8_0)
2. Adjust temperature (lower = more focused, higher = more creative)
3. Try different task modes
4. For very short documents, use `correct_only` instead of summarization

## Language Support

Qwen1.5-1.8B has excellent multilingual support, especially for:
- **Bahasa Indonesia** ✅ (Primary focus)
- English ✅
- Chinese ✅
- Other Asian languages ✅

The model automatically detects the document language and processes accordingly.

## Advanced Configuration

### Custom Prompts

To customize the LLM prompts, edit `llm_utils.py` and modify the `create_prompt()` function.

### Processing Limits

To prevent processing very large documents, the system automatically truncates content to ~8000 characters. You can adjust this in `llm_utils.py`:

```python
max_input_chars = 8000  # Increase or decrease as needed
```

## Security Notes

1. **Local Processing**: All LLM inference happens locally; no data is sent to external services
2. **Privacy**: Document content never leaves your server
3. **Resource Usage**: Monitor system resources when processing large documents
4. **Model Safety**: Use only official Qwen models from Hugging Face

## Model Information

- **Model**: Qwen1.5-1.8B-Chat
- **Developer**: Alibaba Cloud
- **License**: Apache 2.0 (check model card for details)
- **Context Length**: 32K tokens (configured to 4K for efficiency)
- **Languages**: Multilingual with strong support for Asian languages
- **Format**: GGUF (quantized for efficient inference)

## Additional Resources

- [Qwen1.5 GitHub](https://github.com/QwenLM/Qwen1.5)
- [Qwen1.5-1.8B Model Card](https://huggingface.co/Qwen/Qwen1.5-1.8B)
- [GGUF Models](https://huggingface.co/Qwen/Qwen1.5-1.8B-Chat-GGUF)
- [llama.cpp Documentation](https://github.com/ggerganov/llama.cpp)
- [llama-cpp-python Documentation](https://github.com/abetlen/llama-cpp-python)

## Support

If you encounter issues:
1. Check this documentation
2. Verify model file integrity (checksum)
3. Check application logs for detailed error messages
4. Review system resource usage
5. Try a smaller model quantization

For application-specific issues, check the main README.md and open an issue on the project repository.
