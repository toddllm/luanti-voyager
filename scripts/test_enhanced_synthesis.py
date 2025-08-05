#!/Users/tdeshane/luanti-voyager/.venv-whisper/bin/python3
"""
Test enhanced synthesis using existing transcript
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

def create_mock_notebook_content():
    """Create comprehensive mock notebook content for Vector Memory"""
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["# Vector Memory Implementation for Game Agents\n", 
                          "Using LlamaIndex and ChromaDB for persistent agent memory"]
            },
            {
                "cell_type": "code",
                "source": [
                    "# Setup and imports\n",
                    "from llama_index import VectorStoreIndex, SimpleDirectoryReader, Document\n",
                    "from llama_index.vector_stores import ChromaVectorStore\n",
                    "from llama_index.storage.storage_context import StorageContext\n",
                    "import chromadb\n",
                    "from datetime import datetime\n",
                    "import json\n",
                    "\n",
                    "# Initialize ChromaDB client\n",
                    "db = chromadb.PersistentClient(path=\"./agent_memory_db\")\n"
                ]
            },
            {
                "cell_type": "code",
                "source": [
                    "class GameAgentMemory:\n",
                    "    \"\"\"Long-term memory system for game agents\"\"\"\n",
                    "    \n",
                    "    def __init__(self, agent_id: str, memory_collection=\"agent_memories\"):\n",
                    "        self.agent_id = agent_id\n",
                    "        self.client = chromadb.PersistentClient(path=\"./agent_memory_db\")\n",
                    "        self.collection = self.client.get_or_create_collection(memory_collection)\n",
                    "        \n",
                    "        # Create LlamaIndex vector store\n",
                    "        self.vector_store = ChromaVectorStore(chroma_collection=self.collection)\n",
                    "        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)\n",
                    "        \n",
                    "    def store_memory(self, memory_text: str, memory_type: str, metadata: dict = None):\n",
                    "        \"\"\"Store a memory with metadata\"\"\"\n",
                    "        doc_metadata = {\n",
                    "            \"agent_id\": self.agent_id,\n",
                    "            \"timestamp\": datetime.now().isoformat(),\n",
                    "            \"memory_type\": memory_type,\n",
                    "            **(metadata or {})\n",
                    "        }\n",
                    "        \n",
                    "        doc = Document(\n",
                    "            text=memory_text,\n",
                    "            metadata=doc_metadata\n",
                    "        )\n",
                    "        \n",
                    "        # Add to index\n",
                    "        if hasattr(self, 'index'):\n",
                    "            self.index.insert(doc)\n",
                    "        else:\n",
                    "            self.index = VectorStoreIndex.from_documents(\n",
                    "                [doc], storage_context=self.storage_context\n",
                    "            )\n",
                    "    \n",
                    "    def recall_memories(self, query: str, top_k: int = 5, memory_type: str = None):\n",
                    "        \"\"\"Retrieve relevant memories based on query\"\"\"\n",
                    "        if not hasattr(self, 'index'):\n",
                    "            return []\n",
                    "            \n",
                    "        # Create query engine\n",
                    "        query_engine = self.index.as_query_engine(\n",
                    "            similarity_top_k=top_k,\n",
                    "            node_postprocessors=[\n",
                    "                # Filter by agent_id and optionally by memory_type\n",
                    "            ]\n",
                    "        )\n",
                    "        \n",
                    "        response = query_engine.query(query)\n",
                    "        return response\n"
                ]
            },
            {
                "cell_type": "code",
                "source": [
                    "# Practical example: Agent exploring game world\n",
                    "agent_memory = GameAgentMemory(\"agent_001\")\n",
                    "\n",
                    "# Store exploration memories\n",
                    "agent_memory.store_memory(\n",
                    "    \"Found a village at coordinates (100, 64, -200). The village has a blacksmith and 5 houses.\",\n",
                    "    memory_type=\"exploration\",\n",
                    "    metadata={\"location\": {\"x\": 100, \"y\": 64, \"z\": -200}, \"poi_type\": \"village\"}\n",
                    ")\n",
                    "\n",
                    "agent_memory.store_memory(\n",
                    "    \"Traded 10 emeralds for diamond sword with villager blacksmith.\",\n",
                    "    memory_type=\"interaction\",\n",
                    "    metadata={\"trade_value\": 10, \"item_received\": \"diamond_sword\"}\n",
                    ")\n",
                    "\n",
                    "# Later, query memories\n",
                    "memories = agent_memory.recall_memories(\"Where can I find a blacksmith?\")\n",
                    "print(memories)\n"
                ]
            },
            {
                "cell_type": "code",
                "source": [
                    "# Advanced: Episodic memory with temporal awareness\n",
                    "class EpisodicMemory(GameAgentMemory):\n",
                    "    \"\"\"Enhanced memory with episode tracking\"\"\"\n",
                    "    \n",
                    "    def start_episode(self, goal: str):\n",
                    "        \"\"\"Begin a new episode with a specific goal\"\"\"\n",
                    "        self.current_episode = {\n",
                    "            \"id\": f\"episode_{datetime.now().timestamp()}\",\n",
                    "            \"goal\": goal,\n",
                    "            \"start_time\": datetime.now().isoformat(),\n",
                    "            \"memories\": []\n",
                    "        }\n",
                    "        \n",
                    "    def add_to_episode(self, memory_text: str, success: bool = None):\n",
                    "        \"\"\"Add memory to current episode\"\"\"\n",
                    "        if hasattr(self, 'current_episode'):\n",
                    "            self.store_memory(\n",
                    "                memory_text,\n",
                    "                memory_type=\"episodic\",\n",
                    "                metadata={\n",
                    "                    \"episode_id\": self.current_episode[\"id\"],\n",
                    "                    \"episode_goal\": self.current_episode[\"goal\"],\n",
                    "                    \"success\": success\n",
                    "                }\n",
                    "            )\n",
                    "    \n",
                    "    def recall_successful_episodes(self, similar_goal: str):\n",
                    "        \"\"\"Find episodes where similar goals were achieved\"\"\"\n",
                    "        # Query for successful episodes with similar goals\n",
                    "        return self.recall_memories(\n",
                    "            f\"successful episode achieving goal similar to: {similar_goal}\",\n",
                    "            memory_type=\"episodic\"\n",
                    "        )\n"
                ]
            }
        ]
    }

def test_enhanced_synthesis():
    """Test creating enhanced synthesis with existing transcript"""
    print("Testing Enhanced Synthesis for Vector Memory")
    print("="*60)
    
    # Load existing transcript
    transcript_path = Path("docs/ai-makerspace-resources/transcripts/21_vector_memory.json")
    
    if not transcript_path.exists():
        print(f"❌ Transcript not found: {transcript_path}")
        return False
        
    print(f"✅ Found transcript: {transcript_path}")
    
    with open(transcript_path, 'r') as f:
        transcript = json.load(f)
    
    print(f"   Transcript length: {len(transcript.get('text', ''))} chars")
    
    # Get mock notebook content
    notebook_content = create_mock_notebook_content()
    print(f"✅ Created mock notebook with {len(notebook_content['cells'])} cells")
    
    # Extract code from notebook
    code_examples = []
    for cell in notebook_content.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = ''.join(cell.get('source', []))
            if source.strip():
                code_examples.append(source)
    
    print(f"   Extracted {len(code_examples)} code examples")
    
    # Create comprehensive prompt
    prompt = f"""You are an expert developer creating a comprehensive implementation guide for integrating "Vector Memory" into Luanti Voyager, a Minecraft-like game with AI agents.

Based on the AI Makerspace session transcript and notebook code examples, create a COMPREHENSIVE implementation guide.

TRANSCRIPT EXCERPT (first 5000 chars):
{transcript.get('text', '')[:5000]}

NOTEBOOK CODE EXAMPLES ({len(code_examples)} cells):
{chr(10).join(f"```python\n{code}\n```" for code in code_examples)}

Create a COMPREHENSIVE implementation guide that includes:

1. **Executive Summary** - What vector memory enables for game agents (2-3 paragraphs)
2. **Core Concepts** - Key ideas adapted for game context
3. **Architecture Design** - How to structure this in Luanti
4. **Detailed Implementation** - Step-by-step code with explanations
5. **Integration with Luanti** - Specific integration points with game engine
6. **Memory Types** - Different types of memories agents should store
7. **Query Patterns** - How agents retrieve and use memories
8. **Performance Optimization** - Game-specific performance considerations
9. **Testing Strategy** - How to validate memory system works correctly
10. **Example Scenarios** - Practical game scenarios using vector memory

Make it practical, detailed, and immediately actionable for developers. Include specific code that can be copied and adapted. Focus on game-specific applications."""
    
    print("\nCalling Ollama for synthesis...")
    print("(This may take a few minutes)")
    
    # Call Ollama
    cmd = [
        "ollama", "run", "qwen2.5-coder:32b",
        "--verbose",
        prompt
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            synthesis = result.stdout
            print(f"✅ Synthesis generated ({len(synthesis)} chars)")
            
            # Save enhanced synthesis
            output_path = Path("docs/ai-makerspace-resources/synthesis/21_vector_memory_enhanced_test.md")
            with open(output_path, 'w') as f:
                f.write(f"# Vector Memory - Enhanced Synthesis Test\n\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Type: Enhanced (Transcript + Mock Notebook)\n\n")
                f.write(synthesis)
            
            print(f"✅ Saved to: {output_path}")
            
            # Show preview
            print("\n" + "="*60)
            print("PREVIEW (first 1000 chars):")
            print("="*60)
            print(synthesis[:1000])
            print("...")
            
            return True
        else:
            print(f"❌ Ollama error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️ Ollama timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_enhanced_synthesis()
    if success:
        print("\n✅ Test successful! Check the enhanced synthesis file.")
    else:
        print("\n❌ Test failed!")