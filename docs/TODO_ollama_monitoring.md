# TODO: Ollama Monitoring and Debug Setup

## Network Traffic Capture (for immediate debugging)

For capturing Ollama API traffic without debug logs, use `mitmproxy`:

```bash
# Install mitmproxy
brew install mitmproxy

# Start mitmproxy on port 8888
mitmproxy -p 8888

# In another terminal, run Ollama requests through the proxy
export HTTP_PROXY=http://localhost:8888
export HTTPS_PROXY=http://localhost:8888

# Run your Ollama commands
ollama run qwen2.5-coder:32b "test prompt"
```

Alternative with `tcpdump` for raw traffic:
```bash
# Capture localhost traffic on Ollama's default port (11434)
sudo tcpdump -i lo0 -A 'tcp port 11434' -w ollama_traffic.pcap

# View captured traffic
tcpdump -r ollama_traffic.pcap -A | grep -E "(POST|prompt|response)"
```

## Future Improvements for Tomorrow

### 1. Enable Debug Logging
```python
# In enhanced_batch_processor.py
os.environ['OLLAMA_DEBUG'] = '1'
os.environ['OLLAMA_LOGS'] = './logs/ollama_debug.log'
```

### 2. Capture Prompts and Responses
```python
# Add to synthesis method
def synthesize_with_ollama(self, prompt: str, model: str = "qwen2.5-coder:32b") -> str:
    # Save prompt
    prompt_file = self.logs_dir / f"prompt_{datetime.now().timestamp()}.txt"
    with open(prompt_file, 'w') as f:
        f.write(prompt)
    
    # ... existing code ...
    
    # Save response
    if result.returncode == 0:
        response_file = self.logs_dir / f"response_{datetime.now().timestamp()}.txt"
        with open(response_file, 'w') as f:
            f.write(result.stdout)
```

### 3. Add Request/Response Logging Wrapper
```python
class OllamaLogger:
    def __init__(self, log_dir):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
    def log_interaction(self, prompt, response, model, duration):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "duration_seconds": duration,
            "prompt": prompt[:500],  # First 500 chars
            "response": response[:500]
        }
        
        log_file = self.log_dir / f"ollama_log_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
```

### 4. Monitor Resource Usage During Synthesis
- Track NPU/GPU usage per synthesis
- Log memory consumption
- Record model loading times

### 5. Create Ollama Dashboard Script
```bash
#!/bin/bash
# ollama_monitor.sh
# Split terminal to show:
# - asitop (NPU usage)
# - tail -f ollama logs
# - tail -f batch processor logs
# - ollama list (active models)
```

## Implementation Priority
1. Add debug environment variables
2. Implement prompt/response logging
3. Create monitoring dashboard
4. Add performance metrics collection
5. Build analysis tools for collected data

---
**Note**: Network capture approach is useful for debugging when logs aren't available, but proper logging is preferred for production use.