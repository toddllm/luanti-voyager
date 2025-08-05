# Debugging and Monitoring Guide for AI Development

This document captures the debugging techniques and monitoring approaches used during the AI Makerspace integration project. While some methods are "hacky," they proved invaluable for understanding system behavior and ensuring quality outputs.

## Table of Contents
1. [Process Monitoring](#process-monitoring)
2. [Network Traffic Analysis](#network-traffic-analysis)
3. [NPU/GPU Monitoring](#npugpu-monitoring)
4. [Ollama API Debugging](#ollama-api-debugging)
5. [Batch Processing Monitoring](#batch-processing-monitoring)
6. [Memory Management](#memory-management)
7. [Future Enhancement Ideas](#future-enhancement-ideas)

## Process Monitoring

### Background Process Management
When running long batch processes (like Whisper transcription or Ollama synthesis):

```bash
# Start process in background with logging
nohup python scripts/process_batch.py > logs/batch_$(date +%Y%m%d_%H%M%S).log 2>&1 &

# Save PID for later management
echo $! > logs/batch_process.pid

# Monitor process
ps aux | grep process_batch
tail -f logs/batch_*.log

# Kill if needed
kill $(cat logs/batch_process.pid)
```

### Key Learning
- Always capture PIDs when starting background processes
- Use descriptive log filenames with timestamps
- Implement proper signal handling in Python scripts for clean shutdown

## Network Traffic Analysis

### tcpdump for API Monitoring
We used tcpdump to capture Ollama API traffic without modifying code:

```bash
# Capture Ollama traffic on localhost
sudo tcpdump -i lo0 -A -s 0 'tcp port 11434' -w ollama_capture.pcap

# Real-time monitoring with filtering
sudo tcpdump -i lo0 -A 'tcp port 11434' | grep -E "(POST|prompt|response)"
```

### Automated Traffic Monitor Script
Created `monitor_ollama_traffic.sh` that:
- Captures 30-second snapshots every 2 minutes
- Filters for relevant API calls
- Saves both raw captures and debug logs
- Runs continuously in background

### macOS sudoers Configuration
To avoid password prompts for tcpdump:

```bash
# Add to sudoers (as root)
echo "username ALL=(ALL) NOPASSWD: /usr/sbin/tcpdump, /opt/homebrew/bin/timeout" | sudo tee /etc/sudoers.d/tcpdump_monitor
```

### Key Learnings
- tcpdump on loopback interface (`lo0`) captures all localhost traffic
- Use full paths in sudoers for security
- Filter aggressively to reduce capture size
- Ollama uses plain HTTP (not HTTPS) for localhost

## NPU/GPU Monitoring

### Apple Silicon Monitoring Tools

1. **asitop** - User-friendly terminal UI
   ```bash
   brew install asitop
   asitop  # Shows CPU, GPU, ANE (Neural Engine) usage
   ```

2. **powermetrics** - Detailed system metrics
   ```bash
   # Monitor Apple Neural Engine
   sudo powermetrics --samplers ane_power -i 1000
   
   # Combined GPU and ANE monitoring
   sudo powermetrics --samplers gpu_power,ane_power -i 1000
   ```

### Key Learnings
- ANE (Apple Neural Engine) handles ML workloads on Apple Silicon
- Monitor during Whisper transcription to see NPU utilization
- asitop is easier for quick checks, powermetrics for detailed analysis

## Ollama API Debugging

### Capture Methods (in order of preference)

1. **Enable Debug Logging**
   ```bash
   OLLAMA_DEBUG=1 ollama serve
   tail -f ~/.ollama/logs/server.log
   ```

2. **HTTP Proxy Interception**
   ```bash
   # Install mitmproxy
   brew install mitmproxy
   
   # Start proxy
   mitmproxy -p 8888
   
   # Route Ollama through proxy
   export HTTP_PROXY=http://localhost:8888
   ollama run model "prompt"
   ```

3. **tcpdump Capture** (what we used)
   - Useful when you can't modify environment variables
   - Captures actual network packets
   - Can run without modifying the application

### Parsing Ollama Streaming Responses
Ollama streams JSON fragments:
```bash
# Extract and combine response fragments
grep -o '"response":"[^"]*"' capture.txt | sed 's/"response":"//g' | tr -d '\n'
```

### Key Learnings
- Ollama uses streaming JSON responses
- Each fragment contains model name, timestamp, and text chunk
- The `done` field indicates completion
- Responses can be very long - implement proper buffering

## Batch Processing Monitoring

### Virtual Environment Management
Used `uv` for fast, isolated environments:

```bash
# Create dedicated environment for Whisper
uv venv .venv-whisper
source .venv-whisper/bin/activate
uv pip install openai-whisper

# Separate environment for other tools
uv venv .venv-tools
```

### Progress Tracking
1. **Structured Logging**
   ```python
   print(f"[{current}/{total}] Processing {item}...")
   ```

2. **State Persistence**
   - Save progress to allow resuming
   - Track completed items in JSON file

3. **Time Estimates**
   - Log start time for each operation
   - Calculate and display ETA

### Key Learnings
- Whisper large-v3 takes ~25 minutes per hour of audio
- Always implement resume capability for long processes
- Log both to console and file for debugging
- Use separate virtual environments to avoid conflicts

## Memory Management

### Monitoring Python Memory Usage
```python
import psutil
import os

def log_memory():
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / 1024 / 1024  # MB
    print(f"Memory usage: {mem:.1f} MB")
```

### Handling Large Files
- Process in chunks when possible
- Clear variables explicitly: `del large_var`
- Use generators for sequential processing

### Key Learnings
- Whisper models consume significant memory (4-8GB)
- Ollama models are loaded on-demand
- Monitor memory during batch processing
- Implement graceful degradation for OOM scenarios

## Future Enhancement Ideas

Based on our debugging experience:

### 1. Integrated Monitoring Dashboard
Create a terminal dashboard that shows:
- Active processes and their status
- Real-time Ollama API calls
- NPU/GPU utilization
- Memory usage
- Progress bars for batch operations

### 2. Ollama Request/Response Logger
```python
class OllamaLogger:
    def __init__(self):
        self.log_dir = Path("logs/ollama_interactions")
        
    def log_interaction(self, prompt, response, metadata):
        # Save with timestamp, model, duration
        # Include token counts and cost estimates
```

### 3. Automatic Resume System
- Checkpoint after each successful operation
- Store state in SQLite or JSON
- Automatic retry with exponential backoff
- Skip already-processed items

### 4. Performance Profiling
- Track operation durations
- Identify bottlenecks
- Generate performance reports
- Suggest optimizations

### 5. Enhanced Error Handling
- Capture and categorize errors
- Automatic fallback strategies
- Send notifications for critical failures
- Collect diagnostic information

### 6. Testing Infrastructure
```bash
# Smoke test with single item
./scripts/test_pipeline.sh --single

# Dry run to verify setup
./scripts/batch_processor.py --dry-run

# Validate outputs
./scripts/validate_synthesis.py
```

### 7. Resource Management
- Implement queue system for GPU/NPU intensive tasks
- Automatic model unloading when idle
- Concurrent processing where beneficial
- Resource reservation system

## Debugging Checklist

When things go wrong:

1. **Check Process Status**
   ```bash
   ps aux | grep -E "(python|ollama|whisper)"
   ```

2. **Review Logs**
   ```bash
   tail -f logs/*.log
   ls -lt logs/ | head -20  # Recent files
   ```

3. **Monitor Resources**
   ```bash
   asitop  # Quick overview
   htop    # Detailed process view
   ```

4. **Verify Network**
   ```bash
   lsof -i :11434  # Check Ollama port
   ```

5. **Test Components Individually**
   ```bash
   # Test Ollama
   ollama list
   ollama run qwen2.5-coder:32b "test"
   
   # Test Whisper
   whisper --help
   ```

## Lessons Learned

1. **Always implement logging** - You'll need it when running overnight batches
2. **Use full paths** - Especially in scripts and sudoers
3. **Capture metadata** - Timestamps, durations, model versions
4. **Plan for failure** - Resume capability is essential
5. **Monitor actively** - Don't wait until morning to find out it failed
6. **Document hacks** - Today's quick fix might become tomorrow's critical debugging tool

## Contributing

If you discover new debugging techniques or monitoring approaches:
1. Document them here with examples
2. Explain when and why to use them
3. Include any caveats or limitations
4. Add to the appropriate section

Remember: A "hacky" solution that provides visibility is better than flying blind!