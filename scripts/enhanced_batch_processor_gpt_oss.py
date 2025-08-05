#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""
Enhanced batch processor with LLM preprocessing for better context and synthesis
GPT-OSS Version: Uses gpt-oss:20b model for all LLM operations
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
    def __init__(self, base_dir="docs/ai-makerspace-resources-gpt-oss"):
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
        """Get rich context for each topic"""
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
            }
        }
        
        return contexts.get(issue_num, {
            "overview": f"Advanced AI technique: {title}",
            "key_concepts": [],
            "game_applications": [],
            "implementation_hints": []
        })
    
    def create_enriched_notebook_content(self, issue_num: int, title: str, context: Dict[str, Any]) -> Dict[str, List]:
        """Create enriched notebook content based on context"""
        base_imports = """import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio
import json
from datetime import datetime
"""
        
        notebooks = {
            21: {  # Vector Memory - Rich implementation
                "cells": [
                    {
                        "cell_type": "code",
                        "source": base_imports + """
# Vector Memory System for Luanti Agents
import chromadb
from llama_index import VectorStoreIndex, Document
from llama_index.vector_stores import ChromaVectorStore
from llama_index.storage.storage_context import StorageContext

class LuantiAgentMemory:
    \"\"\"Production-ready memory system for game agents\"\"\"
    
    def __init__(self, agent_id: str, world_name: str):
        self.agent_id = agent_id
        self.world_name = world_name
        
        # Initialize persistent storage
        self.client = chromadb.PersistentClient(
            path=f"./memories/{world_name}"
        )
        
        # Create collections for different memory types
        self.episodic = self.client.get_or_create_collection(
            f"{agent_id}_episodic",
            metadata={"type": "episodic", "agent": agent_id}
        )
        
        self.semantic = self.client.get_or_create_collection(
            f"{agent_id}_semantic",
            metadata={"type": "semantic", "agent": agent_id}
        )
        
        self.spatial = self.client.get_or_create_collection(
            f"{agent_id}_spatial",
            metadata={"type": "spatial", "agent": agent_id}
        )
"""
                    },
                    {
                        "cell_type": "code",
                        "source": """
    def store_episodic_memory(self, event: str, context: Dict[str, Any]):
        \"\"\"Store an episodic memory with full context\"\"\"
        memory_id = f"ep_{datetime.now().timestamp()}"
        
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "location": context.get("location", {}),
            "entities_present": context.get("entities", []),
            "emotion": context.get("emotion", "neutral"),
            "importance": context.get("importance", 5),
            "agent_id": self.agent_id
        }
        
        self.episodic.add(
            documents=[event],
            metadatas=[metadata],
            ids=[memory_id]
        )
        
        # Trigger memory consolidation if needed
        if metadata["importance"] > 8:
            self._consolidate_important_memory(memory_id, event, metadata)
    
    def recall_similar_experiences(self, query: str, location: Dict = None, n_results: int = 5):
        \"\"\"Recall memories similar to current situation\"\"\"
        where_clause = {"agent_id": self.agent_id}
        
        if location:
            # Add spatial filtering
            where_clause["$and"] = [
                {"location.x": {"$gte": location["x"] - 50, "$lte": location["x"] + 50}},
                {"location.z": {"$gte": location["z"] - 50, "$lte": location["z"] + 50}}
            ]
        
        results = self.episodic.query(
            query_texts=[query],
            where=where_clause,
            n_results=n_results
        )
        
        return self._process_memories(results)
"""
                    },
                    {
                        "cell_type": "code",
                        "source": """
    def store_spatial_memory(self, location: Dict, description: str, poi_type: str):
        \"\"\"Store location-based memories\"\"\"
        memory_id = f"sp_{location['x']}_{location['z']}"
        
        metadata = {
            "x": location["x"],
            "y": location["y"],
            "z": location["z"],
            "poi_type": poi_type,  # village, dungeon, resource, etc
            "discovered": datetime.now().isoformat(),
            "last_visited": datetime.now().isoformat(),
            "visit_count": 1
        }
        
        # Update if exists
        existing = self.spatial.get(ids=[memory_id])
        if existing["ids"]:
            metadata["visit_count"] = existing["metadatas"][0]["visit_count"] + 1
            metadata["discovered"] = existing["metadatas"][0]["discovered"]
        
        self.spatial.upsert(
            documents=[description],
            metadatas=[metadata],
            ids=[memory_id]
        )
    
    def find_nearest_poi(self, current_location: Dict, poi_type: str = None, max_distance: int = 1000):
        \"\"\"Find nearest point of interest\"\"\"
        where_clause = {}
        if poi_type:
            where_clause["poi_type"] = poi_type
        
        # Get all POIs
        all_pois = self.spatial.get(where=where_clause)
        
        # Calculate distances and sort
        pois_with_distance = []
        for i, poi_meta in enumerate(all_pois["metadatas"]):
            distance = np.sqrt(
                (poi_meta["x"] - current_location["x"])**2 +
                (poi_meta["z"] - current_location["z"])**2
            )
            if distance <= max_distance:
                pois_with_distance.append({
                    "description": all_pois["documents"][i],
                    "metadata": poi_meta,
                    "distance": distance
                })
        
        return sorted(pois_with_distance, key=lambda x: x["distance"])
"""
                    }
                ]
            },
            22: {  # Planner-Executor - Game-focused implementation
                "cells": [
                    {
                        "cell_type": "code",
                        "source": base_imports + """
# Planner-Executor Architecture for Luanti Agents

@dataclass
class GameTask:
    \"\"\"Represents a task in the game world\"\"\"
    task_id: str
    description: str
    task_type: str  # gather, build, explore, combat, social
    priority: int
    prerequisites: List[str] = None
    required_items: List[str] = None
    target_location: Dict = None
    estimated_duration: int = 0
    
@dataclass 
class TaskResult:
    task_id: str
    success: bool
    result_data: Any
    error: str = None
    items_used: List[str] = None
    items_gained: List[str] = None

class LuantiPlanner:
    \"\"\"High-level planning for game agents\"\"\"
    
    def __init__(self, agent_state, world_state, llm=None):
        self.agent_state = agent_state
        self.world_state = world_state
        self.llm = llm
        self.active_plan = []
        
    def create_plan(self, goal: str) -> List[GameTask]:
        \"\"\"Decompose high-level goal into executable tasks\"\"\"
        
        # Use LLM or rule-based planning
        if self.llm:
            return self._llm_planning(goal)
        else:
            return self._rule_based_planning(goal)
    
    def _rule_based_planning(self, goal: str) -> List[GameTask]:
        \"\"\"Rule-based task decomposition\"\"\"
        plans = {
            "build_house": [
                GameTask("gather_wood", "Gather 20 wood", "gather", 1, 
                        required_items=["axe"], estimated_duration=300),
                GameTask("gather_stone", "Gather 30 stone", "gather", 1,
                        required_items=["pickaxe"], estimated_duration=400),
                GameTask("craft_materials", "Craft building materials", "craft", 2,
                        prerequisites=["gather_wood", "gather_stone"]),
                GameTask("clear_area", "Clear 10x10 area", "build", 3),
                GameTask("build_foundation", "Place foundation", "build", 4,
                        prerequisites=["clear_area", "craft_materials"]),
                GameTask("build_walls", "Build walls", "build", 5,
                        prerequisites=["build_foundation"]),
                GameTask("build_roof", "Add roof", "build", 6,
                        prerequisites=["build_walls"])
            ],
            "explore_cave": [
                GameTask("prepare_equipment", "Gather torches and food", "gather", 1),
                GameTask("find_cave", "Locate nearby cave", "explore", 2),
                GameTask("light_path", "Place torches for return", "explore", 3),
                GameTask("mine_ores", "Extract valuable ores", "gather", 4,
                        required_items=["pickaxe", "torch"]),
                GameTask("return_safe", "Return to surface", "explore", 5)
            ]
        }
        
        # Match goal to plan template
        for plan_name, tasks in plans.items():
            if plan_name in goal.lower():
                return tasks
        
        # Default exploration plan
        return [GameTask("explore", f"Explore to achieve: {goal}", "explore", 1)]
"""
                    },
                    {
                        "cell_type": "code", 
                        "source": """
class LuantiExecutor:
    \"\"\"Low-level task execution for game agents\"\"\"
    
    def __init__(self, agent_controller, world_interface):
        self.agent = agent_controller
        self.world = world_interface
        self.current_task = None
        self.execution_history = []
        
    async def execute_task(self, task: GameTask) -> TaskResult:
        \"\"\"Execute a single task with monitoring\"\"\"
        self.current_task = task
        start_time = datetime.now()
        
        try:
            # Check prerequisites
            if not self._check_prerequisites(task):
                return TaskResult(task.task_id, False, None, 
                                "Prerequisites not met")
            
            # Route to appropriate executor
            if task.task_type == "gather":
                result = await self._execute_gather(task)
            elif task.task_type == "build":
                result = await self._execute_build(task)
            elif task.task_type == "explore":
                result = await self._execute_explore(task)
            elif task.task_type == "craft":
                result = await self._execute_craft(task)
            else:
                result = await self._execute_generic(task)
            
            # Record execution
            self.execution_history.append({
                "task": task,
                "result": result,
                "duration": (datetime.now() - start_time).seconds
            })
            
            return result
            
        except Exception as e:
            return TaskResult(task.task_id, False, None, str(e))
    
    async def _execute_gather(self, task: GameTask) -> TaskResult:
        \"\"\"Execute resource gathering task\"\"\"
        target_resource = task.description.split()[-1]  # Extract resource type
        required_amount = int(task.description.split()[-2])
        
        gathered = 0
        items_gained = []
        
        while gathered < required_amount:
            # Find nearest resource
            resource_pos = await self.world.find_nearest_block(target_resource)
            if not resource_pos:
                break
                
            # Navigate to resource
            await self.agent.navigate_to(resource_pos)
            
            # Gather resource
            result = await self.agent.mine_block(resource_pos)
            if result.success:
                gathered += result.items_gained
                items_gained.extend(result.items)
            
            # Check inventory space
            if self.agent.inventory_full():
                await self._store_items()
        
        return TaskResult(
            task.task_id, 
            gathered >= required_amount,
            {"gathered": gathered, "target": required_amount},
            items_gained=items_gained
        )
"""
                    }
                ]
            }
        }
        
        # Return enriched notebook or create basic one
        if issue_num in notebooks:
            return notebooks[issue_num]
        
        # Generic notebook structure
        return {
            "cells": [
                {
                    "cell_type": "code",
                    "source": f"""# {title} Implementation for Luanti
{base_imports}

# Core implementation based on AI Makerspace concepts
class {title.replace(' ', '')}System:
    def __init__(self):
        # Initialize based on context
        self.config = {json.dumps(context, indent=4)}
        
    def process(self, input_data):
        # Main processing logic
        pass
"""
                }
            ]
        }
    
    def preprocess_with_llm(self, transcript_text: str, title: str, context: Dict) -> str:
        """Use LLM to extract key insights and create better prompts"""
        
        analysis_prompt = f"""Analyze this AI Makerspace transcript excerpt about "{title}" and extract:

1. The 3-5 most important technical concepts discussed
2. Specific implementation patterns or code approaches mentioned
3. Common pitfalls or challenges discussed
4. Performance or optimization tips
5. Integration points with other systems

Context for this technology:
{json.dumps(context, indent=2)}

Transcript excerpt:
{transcript_text[:3000]}

Provide a structured analysis focusing on practical implementation details for a game environment."""

        try:
            # Use a faster model for preprocessing
            cmd = ["ollama", "run", "gpt-oss:20b", analysis_prompt]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return ""
        except:
            return ""
    
    def create_enhanced_prompt(self, title: str, context: Dict, transcript_text: str, 
                             notebook_code: List[str], preprocessing_result: str) -> str:
        """Create a comprehensive, context-aware prompt"""
        
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

TRANSCRIPT (Key sections - {len(transcript_text)} chars total):
{transcript_text[:6000]}

IMPLEMENTATION CODE EXAMPLES ({len(notebook_code)} examples):
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
        """Enhanced synthesis with better error handling"""
        print(f"🤖 Synthesizing with {model}...")
        print(f"⏳ This may take up to 30 minutes with gpt-oss:20b...")
        
        cmd = ["ollama", "run", model, "--verbose", prompt]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"❌ Synthesis error: {result.stderr}")
                # Fallback to smaller model
                print("🔄 Trying fallback model...")
                cmd[2] = "gpt-oss:20b"
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
                return result.stdout if result.returncode == 0 else None
        except subprocess.TimeoutExpired:
            print("⏱️ Synthesis timed out")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
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
        
        # Step 1: Get transcript (download + transcribe or load existing)
        transcript = None
        transcript_path = self.transcript_dir / f"{issue_num}_{title.lower().replace(' ', '_')}.json"
        
        if skip_transcription and transcript_path.exists():
            print(f"📄 Loading existing transcript...")
            with open(transcript_path, 'r') as f:
                transcript = json.load(f)
        elif youtube_url and not skip_transcription:
            # Download and transcribe (existing logic)
            pass
        
        # Step 2: Check for real notebook first
        notebook_path = self.notebook_dir / f"{issue_num:02d}_{title.lower().replace(' ', '_')}.ipynb"
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
                print(f"⚠️ Skipping this resource - no valid notebook")
                return False
        else:
            print(f"⚠️ No notebook found for {title}")
            print(f"   Expected: {notebook_path}")
            print(f"📝 Will synthesize using transcript only")
        
        # Step 3: Preprocess with LLM for better insights
        preprocessing_result = ""
        if transcript:
            print(f"🔍 Preprocessing transcript for insights...")
            preprocessing_result = self.preprocess_with_llm(
                transcript.get('text', ''), title, context
            )
            if preprocessing_result:
                print(f"✅ Extracted key insights")
        
        # Step 4: Create enhanced prompt
        prompt = self.create_enhanced_prompt(
            title, context,
            transcript.get('text', '') if transcript else "",
            notebook_code,
            preprocessing_result
        )
        
        # Step 5: Synthesize
        synthesis = self.synthesize_with_ollama(prompt)
        
        if synthesis:
            # Save enhanced synthesis
            synthesis_path = self.synthesis_dir / f"{issue_num:02d}_{title.lower().replace(' ', '_')}.md"
            with open(synthesis_path, 'w') as f:
                f.write(f"# {title} - Enhanced Implementation Guide\n\n")
                f.write(f"Issue: #{issue_num}\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Type: Enhanced (Context-Aware + Preprocessed)\n\n")
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
    """Process resource from environment variables or test with Vector Memory"""
    processor = EnhancedAIResourceProcessor()
    
    # Check for environment variables
    issue_num = os.environ.get('RESOURCE_ISSUE')
    title = os.environ.get('RESOURCE_TITLE')
    youtube_url = os.environ.get('RESOURCE_YOUTUBE')
    notebook_url = os.environ.get('RESOURCE_NOTEBOOK')
    
    if issue_num and title:
        # Process from environment variables
        success = processor.process_resource(
            issue_num=int(issue_num),
            title=title,
            youtube_url=youtube_url if youtube_url else None,
            notebook_url=notebook_url if notebook_url else None,
            skip_transcription=True  # Skip for now, we already have transcripts
        )
    else:
        # Default test with Vector Memory
        success = processor.process_resource(
            issue_num=21,
            title="Vector Memory",
            skip_transcription=True  # Use existing transcript
        )
    
    if success:
        print("\n✅ Enhanced processing complete!")
        print("Check the synthesis directory for the improved output")

if __name__ == "__main__":
    main()