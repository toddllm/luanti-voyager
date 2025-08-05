# AI Integration Learnings & Best Practices

This document captures key learnings from integrating AI Makerspace concepts into Luanti Voyager, including practical tips for working with LLMs, transcription, and synthesis pipelines.

## Quick Reference Commands

### Monitoring Commands
```bash
# Watch your batch processing
asitop                                    # NPU/GPU usage
tail -f logs/enhanced_batch_*.log         # Batch progress
tail -f logs/ollama_monitor_debug.log     # Ollama activity

# Check what's running
ps aux | grep -E "(enhanced_batch|ollama|whisper)"
```

### Emergency Commands
```bash
# Stop everything
pkill -f enhanced_batch_processor
pkill -f monitor_ollama
ollama stop qwen2.5-coder:32b

# Clean up
rm -rf logs/ollama_traffic/capture_*.txt  # Remove old captures
```

## Pipeline Architecture

### What We Built
```
YouTube Videos → Audio Extraction → Whisper Transcription
                                         ↓
                            Ollama Synthesis ← Context + Preprocessing
                                         ↓
                            Implementation Guides → GitHub Issues
```

### Key Components

1. **Enhanced Batch Processor** (`enhanced_batch_processor.py`)
   - Context-aware processing for each AI topic
   - LLM preprocessing for insight extraction
   - Enriched notebook content generation
   - Production-ready guide creation

2. **Traffic Monitor** (`monitor_ollama_traffic.sh`)
   - Captures API calls without code modification
   - Provides visibility into model behavior
   - Helps debug prompt/response issues

3. **Resource Organization**
   ```
   docs/ai-makerspace-resources/
   ├── audio/            # Downloaded YouTube audio
   ├── transcripts/      # Whisper transcriptions
   ├── notebooks/        # Jupyter notebooks (or mock)
   ├── synthesis/        # Ollama-generated content
   └── implementation-guides/  # Final deliverables
   ```

## Ollama Optimization Tips

### Model Selection
- **qwen2.5-coder:32b** - Best for code generation, slower but high quality
- **llama3.1:8b** - Good for preprocessing/analysis, faster
- **mixtral** - Alternative for complex reasoning

### Prompt Engineering
```python
# Structure that worked well
prompt = f"""You are an expert developer creating a production-ready implementation guide...

CONTEXT AND OVERVIEW:
{specific_context}

KEY CONCEPTS TO COVER:
{concepts_list}

GAME-SPECIFIC APPLICATIONS:
{applications}

Create a COMPREHENSIVE guide that includes:
1. Executive Summary
2. Core Architecture
3. Detailed Implementation
4. Game-Specific Optimizations
5. Testing Strategy
[... specific sections ...]

Make it immediately actionable with production-quality code..."""
```

### Performance Tips
- Set timeout to 600 seconds for large syntheses
- Use smaller models for preprocessing
- Cache frequently used context
- Implement fallback models

## Whisper Best Practices

### Model Selection
- **large-v3**: Best quality, ~25 min/hour of audio
- **medium**: Faster, good enough for most content
- **small**: Quick tests and iterations

### Memory Management
```python
# Create dedicated environment
uv venv .venv-whisper
source .venv-whisper/bin/activate

# Load model once, reuse
model = whisper.load_model("large-v3")
for audio in audio_files:
    result = model.transcribe(audio)
```

### Error Handling
- Check audio file validity before processing
- Implement progress callbacks
- Save transcripts immediately after generation

## Batch Processing Wisdom

### State Management
```python
# Always implement resume capability
processed = load_progress()
for item in items:
    if item['id'] in processed:
        continue
    process(item)
    save_progress(item['id'])
```

### Logging Strategy
- Use structured logging with clear sections
- Include timestamps and progress indicators
- Log to both console and file
- Separate error logs

### Resource Coordination
```python
# Process expensive operations sequentially
for resource in resources:
    # Download (network bound)
    audio = download_video(resource['youtube_url'])
    
    # Transcribe (GPU/CPU bound)
    transcript = transcribe(audio)
    
    # Synthesize (API bound)
    synthesis = synthesize_with_ollama(transcript)
    
    # Brief pause to avoid overwhelming
    time.sleep(10)
```

## GitHub Integration Tips

### Issue Creation
- Reference AI Makerspace content
- Include implementation guides
- Add "good first issue" label
- Link to synthesized documentation

### Branch Protection
```json
{
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

## Common Pitfalls & Solutions

### 1. Notebook Download Failures
**Problem**: Google Colab notebooks often restricted
**Solution**: Implement mock notebook content for core concepts

### 2. Sudoers Configuration
**Problem**: tcpdump requires sudo
**Solution**: Add specific commands to sudoers with full paths

### 3. Memory Exhaustion
**Problem**: Multiple large models in memory
**Solution**: Unload models between operations, use virtual environments

### 4. API Timeouts
**Problem**: Ollama synthesis taking too long
**Solution**: Increase timeout, implement retry logic, use faster models for drafts

### 5. Process Management
**Problem**: Orphaned background processes
**Solution**: Save PIDs, implement proper cleanup, use process groups

## Debugging Workflows

### When Synthesis Quality is Poor
1. Check the transcript quality
2. Verify context is being passed correctly
3. Review preprocessing results
4. Try different models
5. Adjust prompt structure

### When Processes Hang
1. Check `asitop` for resource usage
2. Look for blocking I/O operations
3. Verify API endpoints are responding
4. Check for deadlocks in concurrent code

### When Files are Missing
1. Verify directory creation
2. Check file permissions
3. Look for path resolution issues
4. Ensure proper error handling

## Future Improvements Roadmap

### Short Term
- [ ] Add progress bars to CLI output
- [ ] Implement cost tracking for API calls
- [ ] Create validation scripts for outputs
- [ ] Add automatic quality checks

### Medium Term
- [ ] Build web dashboard for monitoring
- [ ] Implement distributed processing
- [ ] Add automatic PR creation
- [ ] Create testing framework

### Long Term
- [ ] ML pipeline for quality assessment
- [ ] Automatic prompt optimization
- [ ] Multi-model ensemble synthesis
- [ ] Integration with CI/CD

## Tools We Wish We Had

1. **Ollama Request Inspector**
   - Browser-like dev tools for API calls
   - Request/response diffing
   - Performance profiling

2. **Whisper Progress UI**
   - Real-time transcription preview
   - Quality indicators
   - Resource usage graphs

3. **Synthesis Validator**
   - Automated quality checks
   - Completeness verification
   - Code extraction and testing

4. **Pipeline Orchestrator**
   - Visual pipeline builder
   - Dependency management
   - Automatic retries and fallbacks

## Key Takeaways

1. **Visibility is Everything**: Better to have hacky monitoring than none
2. **Plan for Scale**: What works for 1 resource might fail at 10
3. **Embrace Incremental Progress**: Test with one, then scale
4. **Document Everything**: Today's hack is tomorrow's critical tool
5. **Monitor Actively**: Don't wait for completion to check progress

## Contributing

Found a better way? Document it here:
1. Explain the problem it solves
2. Show code examples
3. Include performance impact
4. Add to relevant section

Remember: We're building tools for developers who need to integrate AI into games. Make it practical, make it work, make it debuggable.