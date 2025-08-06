# GPT-OSS vs Qwen2.5-Coder Comparison Report

## Executive Summary

This report compares synthesis quality between GPT-OSS:20b and Qwen2.5-Coder:32b models for generating AI Makerspace implementation guides. Testing revealed important insights about timeout constraints and the importance of having actual transcript data for fair comparison.

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

## Summary

While GPT-OSS shows promise and handles large prompts when given sufficient time, the lack of transcript data for 9/10 topics prevents definitive performance comparisons. The key takeaway is that artificial timeout constraints can create false impressions of model limitations.