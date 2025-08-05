# Vector Memory - Implementation Guide (GPT-OSS)

Generated: 2025-08-05T18:16:23.857271
Model: gpt-oss:20b

---

**Vector Memory in Luanti Voyager – Quick‑Start Guide**  
*Word count: ~420*

---

### 1. What is Vector Memory?  
Vector Memory is a lightweight, fixed‑size embedding that captures an AI agent’s recent perceptual and action history. Rather than storing raw state logs, the vector compresses observations (e.g., block types, coordinates, nearby entities) and outputs of a small neural network into a single high‑dimensional float array. The agent can query this vector to decide its next move, enabling continual learning and contextual decision‑making without large replay buffers.

---

### 2. How to implement it for game AI agents

- **Choose an embedding dimension**  
  `const int VECTOR_SIZE = 128;`  (tune for trade‑off between fidelity and memory)

- **Create a perception encoder**  
  ```csharp
  float[] EncodePerception(WorldState ws)
  {
      // Flatten block types, positions, entity IDs into a feature vector
      // Example: 10 features per block * 8 nearby blocks = 80 features
      // Normalise all values to [-1,1]
  }
  ```

- **Design a simple recurrent module**  
  Use a lightweight GRU or simple feed‑forward network that accepts the previous vector and the new perception encoding, producing an updated vector.  
  ```csharp
  float[] UpdateVector(float[] prevVec, float[] enc)
  {
      // e.g., GRU step
      return GRU(prevVec, enc);
  }
  ```

- **Persist the vector in the agent’s state**  
  ```csharp
  public class AIAgent : MonoBehaviour
  {
      private float[] memoryVector = new float[VECTOR_SIZE];
      void Start() { Array.Clear(memoryVector, 0, VECTOR_SIZE); }
  }
  ```

- **Use the vector for policy inference**  
  Feed `memoryVector` into a policy network that outputs action probabilities (move, place block, attack, etc.).

- **Optional: Periodic offline training**  
  Store tuples `(memoryVector, action, reward)` during play for later fine‑tuning of the encoder/GRU.

---

### 3. One simple code example (Unity‑C#)

```csharp
using UnityEngine;
using MLAgents;   // Optional ML‑Agents integration

public class PathfinderAgent : AIAgent
{
    // Encoder – simple feature extraction
    float[] Encode()
    {
        var enc = new float[64];
        // Example: gather nearest 4 blocks
        for (int i = 0; i < 4; i++)
        {
            var block = GetNearestBlock(i);
            enc[i * 16 + 0] = block.typeId / 255f;          // normalized block type
            enc[i * 16 + 1] = block.position.x / 100f;      // world X
            enc[i * 16 + 2] = block.position.y / 100f;      // world Y
            enc[i * 16 + 3] = block.position.z / 100f;      // world Z
            // fill remaining 12 slots with zeros or other features
        }
        return enc;
    }

    // GRU‑style update (placeholder)
    float[] GRU(float[] h, float[] x)
    {
        // Simple tanh‑based recurrence for demo
        var outVec = new float[h.Length];
        for (int i = 0; i < h.Length; i++)
            outVec[i] = Mathf.Tanh(h[i] * 0.8f + x[i % x.Length] * 0.2f);
        return outVec;
    }

    // Called each frame or on relevant event
    void Update()
    {
        var enc = Encode();
        memoryVector = GRU(memoryVector, enc);

        // Policy inference (stub)
        var action = DecideAction(memoryVector);
        Perform(action);
    }

    int DecideAction(float[] vec)
    {
        // Simple rule‑based demo: if high value in index 0 → move forward
        return vec[0] > 0.5f ? 1 : 0;
    }
}
```

---

### 4. Game‑specific use case

**Dynamic Pathfinding with Memory of Block Destruction**

In Luanti Voyager, players can destroy blocks that open new pathways. An AI ally that uses Vector Memory can *remember* the last few block types it broke and the resulting terrain changes, allowing it to:
1. **Predict tunnel openings** – the vector will contain a signature pattern when a certain block type is destroyed.
2. **Avoid pitfalls** – if the memory shows recent falls, the agent will seek higher ground in subsequent steps.
3. **Co‑operate with the player** – by sharing its memory vector over a network, the player can see which areas the AI has already cleared, enabling better team strategy.

This lightweight, continual‑learning memory eliminates the need for large replay buffers while giving agents contextual awareness of dynamic world changes typical in Minecraft‑style worlds.