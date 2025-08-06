# GPT-OSS Timing Data (No Timeouts)

## Complete Timing Results

From the full batch run without timeouts:

| Topic | Prompt Size | Time (seconds) | Time (minutes) | Output Size |
|-------|-------------|----------------|----------------|-------------|
| Vector Memory | 8,215 chars | 230.1 | 3.8 | 27,544 chars |
| Planner Executor | 2,158 chars | 172.9 | 2.9 | 22,832 chars |
| Multi-Agent Swarm | 3,143 chars | 139.9 | 2.3 | 18,398 chars |
| MCP/A2A Protocols | 5,240 chars | 173.1 | 2.9 | 23,049 chars |
| Production RAG | 2,489 chars | 162.8 | 2.7 | 19,636 chars |
| LLM Optimization | 2,330 chars | 153.3 | 2.6 | 20,190 chars |
| Guardrails | 2,065 chars | 130.9 | 2.2 | 20,532 chars |
| Agent Observability | 2,010 chars | 146.4 | 2.4 | 20,245 chars |
| Fine-tuning | 2,067 chars | 171.6 | 2.9 | 22,888 chars |
| Agent Evaluation | 2,013 chars | 114.7 | 1.9 | 16,474 chars |

## Summary Statistics

- **Total time**: 26.6 minutes for all 10 topics
- **Average time**: 2.7 minutes (159.6 seconds)
- **Fastest**: Agent Evaluation - 1.9 minutes
- **Slowest**: Vector Memory - 3.8 minutes (only one with transcript)
- **Success rate**: 100% (10/10)

## Key Observations

1. **Vector Memory took longest** (3.8 min) - the only topic with actual transcript data
2. **Topics without transcripts** averaged 2.4 minutes
3. **No correlation between prompt size and time** for small prompts
4. **All completed successfully** when timeouts removed

## Comparison Context

- **Qwen2.5 timing**: Estimated 5-10 minutes per topic (from previous runs)
- **GPT-OSS advantage**: Approximately 2-3x faster even for Vector Memory
- **Critical finding**: Must remove timeouts for GPT-OSS to function