# GPT-OSS vs Qwen2.5-Coder Comparison Report

## Executive Summary

This report provides a first look at GPT-OSS:20b performance compared to the older Qwen2.5-Coder:32b model for generating AI Makerspace implementation guides. As expected from a newer model, GPT-OSS demonstrates substantial improvements in output quality and completeness.

## Test Methodology

### Three Experiments Conducted

1. **Initial Test**: Different prompting strategies (unfair comparison)
2. **Reduced Transcript Test**: Identical prompts with 2000-char transcripts
3. **No Timeout Test**: Full prompts without artificial timeouts

### Critical Discovery
**Only 1 out of 10 topics (Vector Memory) had an actual transcript**. The other 9 topics were synthesized using only context and notebook code, making broad performance comparisons invalid.

## Performance Analysis

### With Actual Transcript (Vector Memory Only)
- **Qwen2.5-Coder**: ~5-10 minutes (estimated from previous runs)
- **GPT-OSS**: 3.8 minutes for 8,215 char prompt
- **Output**: 27.5 KB from GPT-OSS

### Without Transcripts (9 other topics)
- **GPT-OSS**: 1.9-2.9 minutes
- **Prompt sizes**: 2,010-5,240 characters
- **Output sizes**: 16-23 KB

## Key Findings

### 1. Timeout Constraints Matter
- Initial tests with 300-600s timeouts made GPT-OSS appear limited
- Without timeouts, GPT-OSS handled all prompts successfully
- **Lesson**: Never impose artificial timeouts on LLM inference

### 2. Data Availability Affects Results
- Only Vector Memory had transcript content for true comparison
- Other topics used structured prompts but no transcript data
- Both models can generate quality content from context alone

### 3. Model Capabilities
- **GPT-OSS**: Successfully handled 8,215 character prompt
- **Both models**: 100% success rate on their respective tests
- **Output quality**: Both produce comprehensive, usable guides

## Corrected Conclusions

1. **Timeout removal is essential** for GPT-OSS to function properly
2. **Limited comparable data** - only 1 topic had transcripts for both models
3. **Both models are viable** for synthesis tasks
4. **Context-only synthesis** works well for both models

## Recommendations

### For Current Use
1. **Remove all timeouts** when using GPT-OSS
2. **Both models work well** - choice depends on your constraints
3. **GPT-OSS advantages**: Potentially faster when timeouts removed
4. **Qwen2.5 advantages**: Proven track record with full transcripts

### For Future Testing
1. Obtain transcripts for all 10 topics
2. Run both models with identical inputs
3. Compare timing and quality with complete data
4. Test with various prompt sizes

## Technical Notes

- **GPT-OSS:20b**: 13 GB model, runs via Ollama
- **Qwen2.5-Coder:32b**: 32b parameter model, runs via Ollama
- **Testing platform**: MacBook with Apple Silicon
- **Critical setting**: No timeout constraints for GPT-OSS

## Quality Analysis Results

A detailed analysis of synthesis outputs reveals significant quality differences:

### For Vector Memory (with transcript):
- **Content Volume**: GPT-OSS produced 2.8x more content (27,779 vs 9,795 chars)
- **Code Quantity**: GPT-OSS included 7.2x more code (506 vs 70 lines)
- **Code Quality**: GPT-OSS provided production-ready implementations with gRPC, metrics, error handling
- **Information Design**: GPT-OSS used 53 tables vs 0 in qwen2.5

### For All Topics:
- **Average content**: GPT-OSS ~21,000 chars vs qwen2.5 ~8,700 chars (2.4x)
- **Code blocks**: GPT-OSS averaged 9 vs qwen2.5's 1.5 (6x)
- **Completeness**: GPT-OSS provided deployable solutions vs conceptual frameworks

See [SYNTHESIS_QUALITY_ANALYSIS.md](SYNTHESIS_QUALITY_ANALYSIS.md) for detailed comparison.

## Summary

This first look at GPT-OSS confirms it delivers the expected improvements over the older qwen2.5 model. While only 1 topic had transcript data for timing comparison, the quality analysis quantifies GPT-OSS's advantages: 2.8x more content, 7.2x more code, and production-ready implementations. 

The key operational finding is that GPT-OSS requires no timeout constraints - artificial timeouts will cause apparent failures.