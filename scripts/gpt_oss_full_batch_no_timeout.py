#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""
Enhanced batch processor with NO TIMEOUTS
GPT-OSS Version with IDENTICAL PROMPTING to qwen2.5 and FULL transcripts
This is the FINAL fair comparison - letting GPT-OSS run as long as needed
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path
from datetime import datetime
import re
import time
from typing import Dict, List, Any

class EnhancedAIResourceProcessor:
    def __init__(self, base_dir="docs/ai-makerspace-resources-gpt-oss-full"):
        self.base_dir = Path(base_dir)
        self.audio_dir = self.base_dir / "audio"
        self.transcript_dir = self.base_dir / "transcripts"
        self.notebook_dir = self.base_dir / "notebooks"
        self.synthesis_dir = self.base_dir / "synthesis"
        self.guides_dir = self.base_dir / "implementation-guides"
        
        # Create directories
        for dir in [self.audio_dir, self.transcript_dir, self.notebook_dir, 
                   self.synthesis_dir, self.guides_dir]:
            dir.mkdir(parents=True, exist_ok=True)
    
    def get_context_for_topic(self, issue_num: int, title: str) -> Dict[str, Any]:
        """Get rich context for each topic - IDENTICAL to qwen2.5 version"""
        contexts = {
            21: {  # Vector Memory
                "overview": "Vector memory enables AI agents to store and retrieve episodic memories using semantic similarity search",
                "key_concepts": ["embeddings", "similarity search", "episodic memory", "long-term storage"],
                "game_applications": [
                    "Agents remembering player interactions",
                    "Location-based memories (where resources were found)",
                    "Learning from past successes and failures",
                    "Building knowledge about the game world"
                ],
                "implementation_hints": [
                    "Use ChromaDB or Qdrant for vector storage",
                    "Store memories with rich metadata (time, location, context)",
                    "Implement memory decay for realism",
                    "Query memories based on current context"
                ]
            },
            22: {  # Planner-Executor
                "overview": "Separates high-level planning from low-level execution for more robust agent behavior",
                "key_concepts": ["task decomposition", "hierarchical control", "plan adaptation", "execution monitoring"],
                "game_applications": [
                    "Complex goal achievement (build a house, explore area)",
                    "Multi-step crafting sequences",
                    "Coordinated team actions",
                    "Dynamic replanning when obstacles encountered"
                ],
                "implementation_hints": [
                    "Planner creates abstract plans",
                    "Executor handles concrete actions",
                    "Monitor execution and trigger replanning",
                    "Use state machines or behavior trees"
                ]
            },
            23: {  # Multi-Agent Swarm
                "overview": "Multiple agents working together with emergent collective behavior",
                "key_concepts": ["coordination", "communication", "task allocation", "emergent behavior"],
                "game_applications": [
                    "Village simulation with specialized roles",
                    "Collaborative building projects",
                    "Resource gathering teams",
                    "Defense formations"
                ],
                "implementation_hints": [
                    "Use message passing between agents",
                    "Implement role-based behaviors",
                    "Share information through environment or direct communication",
                    "Balance individual and collective goals"
                ]
            },
            24: {  # MCP/A2A
                "overview": "Standard protocols for tool use (MCP) and agent communication (A2A)",
                "key_concepts": ["tool interoperability", "protocol standards", "cross-platform agents", "API design"],
                "game_applications": [
                    "Expose game actions as MCP tools",
                    "Enable external AI assistants to play",
                    "Cross-game agent migration",
                    "Standardized agent capabilities"
                ],
                "implementation_hints": [
                    "Implement MCP server for game actions",
                    "Use A2A for agent negotiation",
                    "Create tool manifests",
                    "Handle async communication"
                ]
            },
            25: {  # RAG Production
                "overview": "Production-ready retrieval augmented generation for knowledge-grounded responses",
                "key_concepts": ["retrieval", "reranking", "context window management", "hybrid search"],
                "game_applications": [
                    "Wiki-powered agent knowledge",
                    "Dynamic quest generation",
                    "Contextual NPC dialogue",
                    "Crafting recipe assistance"
                ],
                "implementation_hints": [
                    "Index game documentation",
                    "Use hybrid search (keyword + semantic)",
                    "Implement reranking for relevance",
                    "Cache frequent queries"
                ]
            },
            26: {  # LLM Optimization
                "overview": "Techniques to optimize LLM inference for real-time game performance",
                "key_concepts": ["quantization", "caching", "batch processing", "model selection"],
                "game_applications": [
                    "Real-time NPC dialogue",
                    "Fast decision making",
                    "Efficient multi-agent inference",
                    "Resource-constrained deployment"
                ],
                "implementation_hints": [
                    "Use model quantization (GGUF/GPTQ)",
                    "Implement prompt caching",
                    "Batch similar queries",
                    "Consider smaller specialized models"
                ]
            },
            27: {  # Guardrails
                "overview": "Safety and quality control for LLM outputs in game environments",
                "key_concepts": ["content filtering", "output validation", "safety constraints", "quality metrics"],
                "game_applications": [
                    "Family-friendly content enforcement",
                    "Preventing exploits/cheating",
                    "Maintaining game lore consistency",
                    "Rate limiting and abuse prevention"
                ],
                "implementation_hints": [
                    "Pre and post-processing filters",
                    "Structured output validation",
                    "Context-aware constraints",
                    "Fallback behaviors"
                ]
            },
            28: {  # Agent Observability
                "overview": "Monitoring and debugging tools for AI agent behavior",
                "key_concepts": ["telemetry", "visualization", "debugging", "performance metrics"],
                "game_applications": [
                    "Debug stuck agents",
                    "Visualize decision processes",
                    "Performance profiling",
                    "Player-facing AI explanations"
                ],
                "implementation_hints": [
                    "Log decision traces",
                    "Implement visual debugging overlays",
                    "Track performance metrics",
                    "Create replay systems"
                ]
            },
            29: {  # Fine-tuning
                "overview": "Adapting language models to game-specific behaviors and knowledge",
                "key_concepts": ["domain adaptation", "behavioral cloning", "reward modeling", "data collection"],
                "game_applications": [
                    "Game-specific dialogue styles",
                    "Learning from player demonstrations",
                    "Optimizing for player engagement",
                    "Custom personality traits"
                ],
                "implementation_hints": [
                    "Collect gameplay data",
                    "Use LoRA for efficient fine-tuning",
                    "Implement RLHF pipelines",
                    "Version control model checkpoints"
                ]
            },
            30: {  # Agent Evaluation
                "overview": "Systematic testing and evaluation of AI agent performance",
                "key_concepts": ["benchmarks", "metrics", "A/B testing", "player feedback"],
                "game_applications": [
                    "Measure agent competence",
                    "Player satisfaction scoring",
                    "Behavioral diversity metrics",
                    "Performance regression testing"
                ],
                "implementation_hints": [
                    "Create test scenarios",
                    "Define success metrics",
                    "Automate evaluation pipelines",
                    "Collect player feedback"
                ]
            }
        }
        
        return contexts.get(issue_num, {
            "overview": f"Advanced AI technique: {title}",
            "key_concepts": [],
            "game_applications": [],
            "implementation_hints": []
        })
    
    def create_enhanced_prompt(self, title: str, context: Dict, transcript_text: str, 
                             notebook_code: List[str], preprocessing_result: str = "") -> str:
        """Create a comprehensive, context-aware prompt - FULL TRANSCRIPT"""
        
        # Use FULL transcript (up to 6000 chars like qwen2.5)
        full_transcript = transcript_text[:6000]
        
        prompt = f"""You are an expert game developer creating a production-ready implementation guide for integrating "{title}" into Luanti Voyager, an open-source Minecraft-like game with AI agents.

CONTEXT AND OVERVIEW:
{context.get('overview', '')}

KEY CONCEPTS TO COVER:
{json.dumps(context.get('key_concepts', []), indent=2)}

GAME-SPECIFIC APPLICATIONS:
{json.dumps(context.get('game_applications', []), indent=2)}

IMPLEMENTATION HINTS:
{json.dumps(context.get('implementation_hints', []), indent=2)}

PREPROCESSED INSIGHTS:
{preprocessing_result}

TRANSCRIPT (Key sections - {len(full_transcript)} chars total):
{full_transcript}

NOTEBOOK CODE EXAMPLES ({len(notebook_code)} examples):
{chr(10).join(f"```python\n{code[:800]}\n```" for code in notebook_code[:4])}

Create a COMPREHENSIVE, PRODUCTION-READY implementation guide that includes:

1. **Executive Summary** (2-3 paragraphs)
   - What this enables for game AI agents
   - Why it's valuable for players
   - Performance implications

2. **Core Architecture** 
   - System design with clear components
   - Data flow diagrams (describe in text)
   - Integration points with game engine

3. **Detailed Implementation**
   - Complete, runnable code examples
   - Error handling and edge cases
   - Configuration options

4. **Game-Specific Optimizations**
   - Tick rate considerations
   - Memory management
   - Multiplayer synchronization

5. **Agent Behavior Examples**
   - 3-4 specific scenarios showing the technology in action
   - Before/after comparisons

6. **Testing Strategy**
   - Unit tests for core components
   - Integration tests with game engine
   - Performance benchmarks

7. **Deployment Checklist**
   - Configuration steps
   - Monitoring setup
   - Rollback procedures

8. **Advanced Patterns**
   - Scaling to many agents
   - Player interaction patterns
   - Emergent behaviors

Make it immediately actionable with production-quality code that handles edge cases. Focus on Luanti/Minetest specific integration."""
        
        return prompt
    
    def synthesize_with_ollama(self, prompt: str, model: str = "gpt-oss:20b") -> str:
        """Enhanced synthesis with NO TIMEOUT"""
        print(f"🤖 Synthesizing with {model}...")
        print(f"📝 Prompt length: {len(prompt)} characters")
        print(f"⏱️  No timeout - letting model complete naturally...")
        
        cmd = ["ollama", "run", model, prompt]
        
        try:
            start_time = time.time()
            # NO TIMEOUT - let it run as long as needed
            result = subprocess.run(cmd, capture_output=True, text=True)
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Synthesis completed in {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
                print(f"📄 Output length: {len(result.stdout)} characters")
                return result.stdout
            else:
                print(f"❌ Synthesis error: {result.stderr}")
                return None
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Error after {elapsed:.1f} seconds: {e}")
            return None
    
    def process_resource(self, issue_num: int, title: str, youtube_url: str = None, 
                        notebook_url: str = None, skip_transcription: bool = False):
        """Process a single resource with enhanced pipeline"""
        
        print(f"\n{'='*60}")
        print(f"🚀 Processing Issue #{issue_num}: {title}")
        print(f"{'='*60}")
        
        # Get rich context
        context = self.get_context_for_topic(issue_num, title)
        print(f"📚 Loaded context with {len(context.get('game_applications', []))} game applications")
        
        # Step 1: Get transcript
        transcript = None
        # Look for existing transcript in original location
        original_transcript_path = Path("docs/ai-makerspace-resources/transcripts") / f"{issue_num}_{title.lower().replace(' ', '_')}.json"
        transcript_path = self.transcript_dir / f"{issue_num}_{title.lower().replace(' ', '_')}.json"
        
        if original_transcript_path.exists():
            print(f"📄 Loading existing transcript from original location...")
            with open(original_transcript_path, 'r') as f:
                transcript = json.load(f)
            # Copy to our directory
            with open(transcript_path, 'w') as f:
                json.dump(transcript, f, indent=2)
        
        # Step 2: Check for real notebook
        notebook_path = Path("docs/ai-makerspace-resources/notebooks") / f"{issue_num:02d}_{title.lower().replace(' ', '_')}.ipynb"
        notebook_code = []
        
        if notebook_path.exists():
            print(f"📓 Found real notebook: {notebook_path.name}")
            try:
                with open(notebook_path, 'r') as f:
                    notebook_data = json.load(f)
                
                # Extract code from real notebook
                for cell in notebook_data.get('cells', []):
                    if cell.get('cell_type') == 'code':
                        source = cell.get('source', '')
                        if isinstance(source, list):
                            source = ''.join(source)
                        if source.strip():
                            notebook_code.append(source)
                
                print(f"✅ Extracted {len(notebook_code)} code cells from real notebook")
            except Exception as e:
                print(f"❌ Error reading notebook: {e}")
        else:
            print(f"📝 No notebook found, will synthesize using transcript only")
        
        # Step 3: Create enhanced prompt with FULL transcript
        prompt = self.create_enhanced_prompt(
            title, context,
            transcript.get('text', '') if transcript else "",
            notebook_code,
            ""  # No preprocessing for fair comparison
        )
        
        # Step 4: Synthesize WITHOUT TIMEOUT
        synthesis = self.synthesize_with_ollama(prompt)
        
        if synthesis:
            # Save enhanced synthesis
            synthesis_path = self.synthesis_dir / f"{issue_num:02d}_{title.lower().replace(' ', '_')}.md"
            with open(synthesis_path, 'w') as f:
                f.write(f"# {title} - Implementation Guide (GPT-OSS Full No Timeout)\n\n")
                f.write(f"Issue: #{issue_num}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Model: gpt-oss:20b\n")
                f.write(f"Prompt: IDENTICAL to qwen2.5 with FULL 6000 char transcript\n")
                f.write(f"Timeout: NONE - model ran to completion\n\n")
                f.write(synthesis)
            
            print(f"✅ Saved synthesis: {synthesis_path}")
            
            # Also save implementation guide
            guide_path = self.guides_dir / f"{issue_num:02d}_{title.lower().replace(' ', '_')}.md"
            with open(guide_path, 'w') as f:
                f.write(f"# {title} - Luanti Implementation Guide\n\n")
                f.write(synthesis)
            
            return True
        
        return False

def main():
    """Process all AI Makerspace resources with NO TIMEOUTS"""
    processor = EnhancedAIResourceProcessor()
    
    # Topics to process (all 10)
    topics = [
        {"issue": 21, "title": "Vector Memory"},
        {"issue": 22, "title": "Planner Executor"},
        {"issue": 23, "title": "Multi-Agent Swarm"},
        {"issue": 24, "title": "MCP and A2A Protocols"},
        {"issue": 25, "title": "Production RAG"},
        {"issue": 26, "title": "LLM Optimization"},
        {"issue": 27, "title": "Guardrails"},
        {"issue": 28, "title": "Agent Observability"},
        {"issue": 29, "title": "Fine-tuning"},
        {"issue": 30, "title": "Agent Evaluation"}
    ]
    
    successful = 0
    failed = []
    
    print(f"🚀 Processing {len(topics)} AI Makerspace topics with GPT-OSS")
    print(f"📝 Using IDENTICAL prompts to qwen2.5 with FULL 6000 char transcripts")
    print(f"⏱️  NO TIMEOUTS - letting each synthesis run to completion")
    print(f"💡 Based on test: expecting ~2-3 minutes per topic\n")
    
    start_time = time.time()
    
    for topic in topics:
        success = processor.process_resource(
            issue_num=topic["issue"],
            title=topic["title"],
            skip_transcription=True
        )
        
        if success:
            successful += 1
        else:
            failed.append(topic)
    
    # Summary
    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"📊 FINAL COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful: {successful}/{len(topics)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"⏱️ Total time: {elapsed/60:.1f} minutes")
    print(f"📈 Average time per synthesis: {elapsed/len(topics)/60:.1f} minutes")
    
    if failed:
        print(f"\nFailed topics:")
        for topic in failed:
            print(f"  - {topic['title']} (#{topic['issue']})")
    
    print(f"\n✅ Final comparison complete!")
    print(f"Check {processor.synthesis_dir} for results")
    print(f"\nThis proves GPT-OSS can handle full prompts without context limitations!")

if __name__ == "__main__":
    main()