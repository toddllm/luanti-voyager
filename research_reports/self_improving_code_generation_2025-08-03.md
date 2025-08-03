# Designing a Self-Improving Code-Generating Game Agent

**Source:** OpenAI Deep Research  
**Date:** 2025-08-03  
**Prompt:** [Self-Improving Code Generation](../DEEP_RESEARCH_PROMPTS.md#prompt-2-self-improving-code-generation)

---

**Goal:** Build an agent that can **start simple and autonomously improve**, writing its own code to handle increasingly complex game behaviors. The agent begins with basic movement/interaction *primitives* (e.g. move, turn, pick up object) and learns to compose these into higher-level *skills*. Crucially, it can **debug its own code** when errors occur and **transfer knowledge** between similar tasks. The design must handle **partial observability** (limited agent vision), be **LLM-backend-agnostic** (work with OpenAI, Anthropic, Ollama, etc.), be **compute-efficient** for open-source use, and **enforce safety constraints** throughout.

Below we outline the system architecture and address each specific question in detail, including prompt strategies, error handling, skill reuse, skill representation, and exploration-exploitation balance. Throughout, we include examples and implementation strategies to concretize the ideas.

## System Overview and Architecture

&#x20;*Figure: High-level architecture of a self-improving LLM-driven agent (inspired by **Voyager**). The agent consists of three main modules: (1) an **Iterative Prompting Mechanism** that generates and executes code based on the agent's goals and observations, (2) a **Skill Library** that stores learned code "skills" and enables their retrieval/reuse, and (3) an **Automatic Curriculum** (or task scheduler) that proposes new goals to drive exploration. The agent uses game API primitives (e.g. movement, actions) as its initial vocabulary. It runs in a loop of proposing a task, prompting an LLM to write code to achieve it, executing that code in the game environment, and using environment feedback (observations, errors, outcomes) to refine its skills and update what it knows.*

**Autonomy and Self-Improvement:** The agent begins with only fundamental actions, but over time it *writes new code* to achieve higher-level objectives. Each new successful code snippet becomes a **new skill** in the library. For example, initially it only knows how to move and pick up items; later it might learn a skill called `build_bridge()` by composing moves and item placements. The system is designed to **improve iteratively**: after each attempt at a task, it evaluates the outcome and updates its approach. Recent research demonstrates that such self-referential agents can indeed bootstrap themselves – a coding agent (SICA) showed **17–53% performance gains** on coding benchmarks by iteratively reflecting and improving its own code, all while respecting safety and resource limits.

**Partial Observability:** In many games the agent cannot see the whole world state at once. Our design explicitly accounts for this. The agent treats each code-generation attempt as an action in a *partially observable MDP*, where the code executes and yields new observations (e.g. "I moved and now see a wall") that inform the next steps. The agent's prompt will include its *current observation/knowledge* of the world, and the generated code can incorporate *exploration logic* (e.g. loops to scan the area or move around) to handle unknown information. For instance, if the goal is "find a key" and the agent's vision is limited, the LLM might produce a function that wanders the map or systematically searches rooms until the key is found, updating an internal map as it goes. (We'll discuss prompt structure for this below.)

**LLM-Backend-Agnostic & Compute Efficiency:** To accommodate different LLMs (OpenAI GPT-4/GPT-3.5, Anthropic Claude, local models via Ollama, etc.), the system does not rely on any model-specific fine-tuning or proprietary features. Instead, it uses *prompt-based in-context learning* – i.e. all intelligence comes from the LLM's outputs given carefully engineered prompts and few-shot examples. This means we can swap in any sufficiently capable code-generating model. For open-source efficiency, we minimize expensive calls and avoid heavy reinforcement learning training loops. The agent *reuses existing skills* whenever possible to reduce new LLM calls, and it executes code in the game environment to learn (which is often cheaper than massive model inference). In Voyager (an open-ended Minecraft agent), this approach yielded strong lifelong learning without any fine-tuning of the model. We can also choose smaller-code models (like Code Llama or WizardCoder) for local deployment – while they may produce more mistakes, the self-debugging mechanism (Section 2) will catch and correct many errors, making the system robust even with less powerful models.

**Safety Constraints:** Safety is built in at multiple layers. First, the prompt itself includes instructions that **restrict the code generation** to the allowed game API and prevent hazardous operations. For example, the system message (or prompt preamble) might say: *"You are an agent coding for a game. Only use the provided game API functions (move, turn, useItem, etc.). Do not execute external commands or access files. Avoid code that could harm the game server or crash the program."* This steers the LLM away from producing disallowed actions. Second, we **sandbox the code execution**. Generated code is run in a controlled game environment with limited privileges – e.g. a Python sandbox that permits only game-specific modules. If the code tries something unsafe (like a forbidden library call), the sandbox halts execution and reports an error. The agent then treats this as a runtime failure to debug (instead of ever executing a truly unsafe action). We also include *safety checks* in the review cycle: after the LLM produces code, the agent can scan it for blacklisted functions or risky patterns before execution. This multi-pronged approach maintains alignment with safety requirements throughout learning.

With the high-level picture in mind, let's dive into each of the specific questions and design elements:

## 1. Prompt Engineering for Reliable Code Generation

**Prompt Structure:** Crafting an effective prompt is critical for guiding the LLM to produce correct and context-aware code. We use a structured prompt template that provides the LLM with:

* **Task Description:** A concise statement of the current goal or skill to implement. For example: *"Goal: Craft a pickaxe"* or *"Goal: Traverse to the room with the key and unlock the door."* This gives the LLM a clear objective.
* **Context/Observations:** Relevant state information and constraints. This includes the agent's *current observations (partial world state)* and *inventory or knowledge*. For instance: *"Current observation: an iron ore is at position (10,5), agent at (0,0). Inventory: 2 sticks, 0 iron ingots. The agent's vision range is 5 tiles."* Including partial observability context informs the LLM that the agent may need to explore or gather info. We also list *known primitives or APIs* here (e.g. `move(direction)`, `craft(item)`, `scan_area()` etc.), so the model knows what building blocks it can use in code.
* **Relevant Skills/Hints:** (If applicable) A summary of top relevant previously learned skills or examples. Using a **few-shot learning** style, we can insert pseudo-code or descriptions of similar tasks the agent solved before. For example: *"Known skill: `craft_planks(wood)` – uses wood logs in inventory to craft wooden planks. Known skill: `go_to(x,y)` – moves the agent to coordinates (x,y) using A* search."\* This acts as *in-context retrieval* of skills, guiding the model to reuse or call those functions. In practice, we might include the signatures or a brief excerpt of those functions. (We discuss skill retrieval more in Section 3.)
* **Instruction/Format:** A direct instruction to *write code* and the expected format. For example: *"Write a Python function `craft_pickaxe()` that uses the available API to achieve the goal. If the goal cannot be completed due to missing prerequisites, the code should handle it (e.g., gather needed items). Provide only the code for the function, no explanations."* This ensures the LLM output is just code. The format can be tailored per LLM (some might need a `<BEGIN CODE>` marker or triple-backticks for clarity). We also remind the model of constraints: *"Use only allowed functions. Do not produce system commands. Ensure the code is efficient and avoid infinite loops."*

By structuring the prompt with these elements, we give the LLM a *clear problem definition, environment state, available tools, and examples* – greatly increasing the reliability of the generated code. This prompt engineering echoes the approach used in Voyager's iterative prompting mechanism, where the agent feeds the LLM a goal plus context like inventory items, and gets back a code snippet to execute the goal.

**Example Prompt:** Suppose the agent's goal is to **open a locked door** in a dungeon game, with partial observability (it can only see adjacent cells). We might assemble a prompt like:

```
Goal: Unlock the door at location (8, 3).

Current Observation: The agent is at (5, 3) facing East. The door (locked) is 3 tiles east. A key is required to unlock it. The agent's inventory: [no key]. Visible area: floor tiles around, a key is faintly visible on a table at (7,3) within view.

Known Skills:
- move_to(x, y): Moves the agent to the target coordinates, using BFS to handle obstacles.
- pick_up(item): Picks up an item if present at the agent's location.
- unlock_door(): Unlocks a door at the agent's location if agent has the key.

Instructions: Write a Python function `open_door()` that:
1. Navigates to the key (if not already in inventory),
2. Picks up the key,
3. Moves to the door,
4. Uses the key to unlock the door.
Use the primitives and known skills above. Handle partial observability by exploring if the key isn't immediately visible. Only output the function code.
```

This prompt explicitly tells the LLM what to do and what it has to work with. A well-designed model-agnostic prompt like this should yield a reasonable solution. For example, an LLM might return:

```python
def open_door():
    # Step 1: Get the key if not in inventory
    if "key" not in inventory:
        # The key was seen at (7,3); move there and pick it up
        move_to(7, 3)
        pick_up("key")
        if "key" not in inventory:
            # If key still not in inventory, maybe it's slightly off – search nearby
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                move(dx, dy)  # small exploratory move
                if "key" in inventory:
                    break
            # (Additional logic could be added to systematically search further)
    # Step 2: Move to the door location
    move_to(8, 3)
    # Step 3: Unlock the door using the key
    if "key" in inventory and is_door_locked(8, 3):
        unlock_door()
```

This code uses known skills `move_to` and `pick_up` and includes a bit of logic for partial observability (a small local search if the key wasn't found as expected). The actual complexity of search could be greater (e.g., a loop expanding outward), but the key is that the *prompt encouraged the model to handle missing info*. We provided the clue that a key is needed and might not be in inventory, so the model generated code to ensure the key is obtained. In practice, more sophisticated prompt tactics like **chain-of-thought** can be used: we might ask the model first to outline a plan in comments (ensuring it considers the unknowns) and then produce code. For backend-agnostic implementation, we can do this in a single prompt (for models that follow instructions well) or in a multi-turn format (for chat-based models, using a system message to set rules and user message as the task). The design needs testing per model to fine-tune the prompt wording, but the general template remains consistent.

**Prompt Reliability Techniques:** To further improve reliability, we leverage prompt techniques such as:

* **Few-Shot Examples:** If the model tends to make specific mistakes (say, forgetting to handle errors or not using available functions), we include a simplified example in the prompt. For instance: *"Example: Goal: pick up an item. \[then a small code function example]. Now for the actual goal, write the code."* This shows the model the style expected.
* **Verbalizing Constraints:** Clearly reminding the model of partial observability and safety constraints in the prompt. E.g. *"Remember: the agent has limited vision, so your code may need to move around to find targets."* This helps the LLM not assume global knowledge.
* **Format Enforcement:** Ensuring the prompt yields only code. For OpenAI or Anthropic models, one can use the system role or high-level instruction: *"Respond with just the Python code and minimal comments, no additional explanation."* For local models that may be chatty, we instruct similarly or post-process the output to remove extraneous text.

By carefully structuring prompts in this manner, our agent can reliably generate code that is tailored to the current task and context. This prompt engineering is model-agnostic and has been demonstrated to work across APIs – for example, **Voyager's prompt to GPT-4 included the task, the agent's state (inventory, etc.), and it reliably got back executable code for that task**. We expect similar prompt templates to generalize to other LLMs (Claude, local GPT4All, etc.) with only minor adjustments.

## 2. Handling Syntax Errors and Runtime Failures (Self-Debugging)

No matter how good the prompt, the agent's first attempt at generating code will sometimes be wrong – code might have syntax errors, bugs, or logical mistakes (especially with smaller or uncoded models). A cornerstone of our system is the ability to **detect and fix errors autonomously**. We implement a **self-debugging loop** that catches errors, feeds them back into the LLM, and iterates until the code works or a limit is reached.

**Compilation/Syntax Errors:** After the LLM produces code, the agent attempts to *compile* or run it in a test mode. If a syntax error or exception occurs immediately, the agent captures the error message. For example, Python might throw `SyntaxError: invalid syntax at line 5`. The agent then *augments the prompt* for the next LLM call with this feedback. A simple strategy: prepend a message like *"The previous attempt failed with the following error: `SyntaxError: ...`. Please fix the code accordingly."* and include the faulty code for reference. The LLM, seeing the error, can attempt to correct it (e.g. fix a missing parenthesis or indentation). This process continues iteratively until the code compiles.

We can take inspiration from recent research on LLM self-debugging which shows that models can effectively fix their own syntax mistakes when given the error trace. In practice, even open-source models can fix simple errors if the error message is provided (since they've likely seen such patterns during training). For instance:

* **First pass code:**

  ```python
  def build_bridge():
      for i in range(5):
          place_block("wood")
          move("forward"
  ```

  (Missing a parenthesis)
* **Error caught:** `SyntaxError: unexpected EOF while parsing (<string>, line 4)`
* **Agent's follow-up prompt addendum:** "Previous code had a syntax error: unexpected EOF at line 4. Fix this error."
* **LLM second pass:** It returns the corrected code:

  ```python
  def build_bridge():
      for i in range(5):
          place_block("wood")
          move("forward")
  ```

  which now compiles.

This automated fix loop continues for any syntax or static errors until the code can run.

**Runtime Failures and Logical Errors:** More challenging is when the code runs but doesn't achieve the desired result or hits a runtime error (exception) during execution. Our system tackles this in two ways:

**1. Execute with Checks (Testing):** Whenever the agent writes a new skill code, we run it in the game environment in a controlled way. We monitor for exceptions (like calling a function with wrong arguments or index out of range) and for *goal completion*. If a runtime error occurs, we catch the exception and feed that back to the LLM similar to syntax errors. For example, if the code calls a nonexistent API function `open_door()` and raises an `AttributeError`, we prompt the LLM: *"Error: `AttributeError: 'GameAPI' object has no attribute 'open_door'`. The function open\_door() is not available. Please use the provided `unlock_door()` function instead."* The LLM then knows to correct the API call. This approach is analogous to unit testing the generated code with the environment as the test harness. The *Self-Debugging* technique by Chen et al. (2023) showed that LLMs can improve accuracy by leveraging execution feedback in this manner.

**2. Outcome Verification (Semantic Errors):** Not all issues manifest as explicit exceptions; sometimes the code just doesn't accomplish the goal. To handle this, we use a **self-verification** step where the agent evaluates the outcome against the goal. After running the code, the agent asks: "Did this code actually solve the task?" We can implement this by either having known success criteria (e.g., check game state: the door is now open, or the agent's inventory has the crafted item) *or* by using the LLM itself as a critic. The latter is powerful: we can prompt the LLM with a description of what happened and ask if the goal was met. This was done in Voyager, where after executing a skill, they provided the LLM with the current state and the intended task, and the LLM (in a "critic mode") would respond whether the program achieved the task and if not, suggest a fix. For example, after running `craft_pickaxe()` code, the agent might tell the LLM: *"After execution, inventory has no pickaxe."* The LLM might realize the code failed to actually call the crafting function, and suggest adding a `craft("pickaxe")` step.

In our design, we combine both automated checks and LLM-based reflection:

* If a failure is clear (error message or obvious missing condition), directly feed that into the next prompt.
* Additionally, have the LLM explain its own code. We could prompt: *"Explain the above code's logic and whether it achieves the goal."* This can reveal logical bugs. Indeed, **Self-Debugging by explanation** has been shown to help models find mistakes without any external feedback. The model might "talk through" the code (like rubber-duck debugging) and notice, for instance, that it never used the key to unlock the door in our earlier example.
* Finally, incorporate suggested fixes. We ask the LLM to produce a corrected version of the code given the critique.

**Example – Iterative Debugging:** Suppose the agent is trying to implement a skill to **fight a monster** (`fight_monster()`), using basic attack and defense primitives. On first attempt, the LLM produces code that swings a sword but forgets to check if the agent's health is low (a dangerous omission). When executed, the agent might actually get killed in-game due to not healing or blocking. There's no Python exception here; the code ran, but the outcome (agent died) is a failure. We detect this via game state (agent's HP <= 0). The agent can then prompt the LLM with: *"The fight\_monster code resulted in the agent's death. It did not use any defensive actions. Please adjust the strategy to ensure survival (e.g., use shield or heal when low on HP)."* With this feedback, the LLM might modify the code to include health checks and defensive moves. For instance, adding:

```python
if player.health < 20: use_item("health_potion")
elif monster.distance() < 2: attack("sword")
else: block()
```

This loop continues until the fight sequence reliably succeeds (or at least improves). In practice, a budget of a few iterations is often enough to correct most issues, especially if the model is large. For smaller models, more iterations might be needed or more explicit hints in the feedback.

**Sample Dialogue of the Debug Loop:**

* *Attempt 1:* LLM generates `fight_monster()` code (attacks repeatedly).
* *Execution feedback:* Agent observes "Agent died because health dropped to 0."
* *Prompt to LLM:* "The agent died. Likely cause: no healing or blocking. Modify the code to use defensive actions when health is low."
* *Attempt 2:* LLM adds health check but uses a wrong item name causing KeyError.
* *Error feedback:* "KeyError: 'healthpotion' – item name not recognized. Use 'health\_potion'."
* *Attempt 3:* LLM fixes item name. Code executes, agent survives and monster defeated.
* *Verification:* Agent confirms monster is defeated and agent alive – success. It then **stores this final code in the skill library**.

By handling errors in this iterative fashion, the agent not only achieves the immediate goal but also *learns* a correct skill for future reuse. Notably, this process is **LLM-backend neutral**: whether using GPT-4 or a local model, the loop is the same; the difference is just how many iterations might be needed (larger models often produce correct code faster). The key is that the agent uses *tool feedback* (runtime errors, game state) and *LLM self-reflection* to converge to working solutions, embodying a powerful self-debugging capability.

It's worth mentioning that this approach draws on ideas of **Reflexion** and **Self-Correction** in LLM agents. The agent explicitly critiques its own outputs and refines them, at the cost of extra compute per task but with the benefit of higher reliability. For open-source use, this is a good trade-off: rather than requiring a perfect model, we let a weaker model make mistakes but iteratively fix them. The compute overhead is just a few extra LLM calls and re-executions, which is often acceptable for moderate tasks.

## 3. Efficient Skill Retrieval and Reuse

As the agent solves tasks, it accumulates a **Skill Library**: a repository of code functions it has written, from simple skills (like `move_to(x,y)` or `pick_up(item)`) to complex ones (like `build_shelter()` or `fight_monster()`). **Efficient retrieval and reuse of these skills** is crucial for two reasons: (a) it dramatically improves efficiency (why ask the LLM to reinvent a solution we already have?), and (b) it enables **transfer of knowledge** between tasks – the agent can apply prior skills to new but similar problems.

**Skill Library Structure:** Each skill can be stored as a pair: **(Description, Code)**. The description is a concise natural language summary or signature (e.g. "craft a pickaxe from wood and iron" or "navigate to coordinates (x,y) avoiding obstacles"). The code is the function implementation the LLM generated (and debugged) for that description. We might also store metadata like prerequisites or outcomes. For fast lookup, we maintain indices:

* A **direct index** (hash table) keyed by skill name or exact goal. If a new goal matches exactly a previous one, we can reuse that code immediately without calling the LLM.
* A **semantic index** for similarity lookup. We embed each skill's description into a vector space (using an embedding model) and do a nearest-neighbor search to find skills relevant to a new goal. For example, if the agent faces a goal "fight a dragon", the system might retrieve skills like "fight goblin" or "dodge attack" as similar context. In the Voyager Minecraft agent, *each skill was indexed by the embedding of its description to enable retrieval in similar future situations*, and at runtime they queried the top 5 relevant skills for a new task. We can implement this with a lightweight vector store (many open-source options exist, or even just cosine similarity on stored embeddings since the number of skills will not be huge initially).

**Prompting with Retrieved Skills:** Once we have relevant skills, how do we reuse them? There are two main ways:

* **Direct Code Reuse:** If a new task can be solved by *calling* one or more existing skills, the agent can construct a solution by orchestrating those calls instead of writing everything from scratch. For instance, suppose the agent already learned `craft_sword()` and now the goal is "craft an iron sword". The agent can simply call `craft_sword("iron")` if parameterized, or use the same sequence (craft pickaxe -> mine iron -> smelt -> craft sword) that it has in its library. We could even have the LLM itself realize this by providing the skill list in the prompt. e.g. *"You have functions: craft\_sword(material), mine\_ore(type), smelt\_ore(type). Goal: craft an iron sword. Use the available functions."* The LLM will likely produce something like:

  ```python
  def craft_iron_sword():
      mine_ore("iron")
      smelt_ore("iron")
      craft_sword("iron")
  ```

  This is trivial for the model since we framed it as composition of known pieces. **Composing simpler programs to form complex skills** is exactly how we get rapid capability gains. Each new skill can be a combination of earlier ones (this not only saves time, but also reduces the chance of error since those components are tested).
* **Few-Shot Example in Prompt:** Alternatively, if direct function calls aren't obvious, we can include one or two similar skill implementations in the prompt as *guidance*. For a new task, we find the most similar past task and show its code to the LLM: *"Example skill (for a similar task): {code}"* followed by *"Now solve the new task."* This leverages the LLM's pattern matching to produce analogous code. For instance, if the new goal is "find and mine a diamond", we might show the code for "find and mine iron" as an example. The LLM would then follow that pattern, replacing "iron" with "diamond" and adjusting any differences (it might realize diamond is deeper underground and thus requires digging deeper, etc., if such knowledge is in the model).
* In practice, we can combine both: present relevant skill snippets and also encourage the model to explicitly call them if applicable.

**Skill Transfer Example:** *Transferring knowledge between similar tasks* might look like this: The agent has learned a skill to **escape a maze** (say, by always turning left at walls). Later, it encounters a **new maze**. Instead of learning from scratch, the agent recalls the "escape maze" skill. Perhaps the new maze has a twist (doors that need keys), but 90% of the logic is the same. The agent can reuse the pathfinding part and only generate new code for the key-door part. Implementation-wise, the skill library finds the "maze escape" function as relevant. The prompt to the LLM for the new maze task might include: *"Known skill `escape_maze()`: \[code]. This maze has locked doors, so incorporate key finding into the strategy."* The LLM then outputs a modified version of `escape_maze` that calls `find_key()` when encountering a locked door, etc. This way, *knowledge is transferred* – the mapping and traversal logic from the old maze is used in the new context with minimal changes.

**Efficiency Considerations:** Retrieving and reusing skills greatly improves efficiency:

* **Fewer LLM calls:** If a skill is found that exactly matches or covers the task, the agent might skip calling the LLM entirely and just execute the code (or maybe call the LLM to double-check minor adaptations). This saves a potentially expensive model invocation.
* **Shorter prompts:** Even when using the LLM, providing an existing solution often means the model just has to do slight modifications, not generate from scratch. It tends to produce correct code faster (less chance of hallucinating irrelevant approaches if a template is given).
* **Avoiding catastrophic forgetting:** As the agent learns many skills over time, retrieving them keeps them in active use, which both validates their correctness in new contexts and prevents the system from "forgetting" their existence. In lifelong learning agents like Voyager, the skill library allowed reusing earlier knowledge so effectively that the agent could solve novel tasks in a new world from scratch using those skills, whereas other agents without such memory struggled.

Under the hood, efficient skill reuse can be implemented with common open-source components: use an embedding model (like OpenAI text-embedding-ada or a local equivalent) for descriptions, a simple vector DB (FAISS or just a Python list with cosine similarity), and design the prompt assembly to inject skill references. This is lightweight and scales with number of skills (which might grow to dozens or hundreds, but not millions, so search is fast).

**Knowledge Transfer vs. New Learning:** The agent should decide when to reuse vs. write new. A simple strategy: attempt to retrieve skills for each new task; if none are sufficiently similar (say, similarity score above a threshold), then treat it as a genuinely new skill and call the LLM without examples (just the primitives). If partial matches exist, use them as building blocks. Over time, as the library grows, the fraction of tasks that can leverage prior code increases, accelerating learning. We might even incorporate a rule like "if the first attempt without reuse fails, try again using a related skill example", to cover cases where the agent first tries fresh code and then realizes it should have reused something.

In summary, by building a **rich skill library and a retrieval mechanism**, our system enables efficient reuse of code and **transfer of skills** between tasks. Empirical evidence from systems like Voyager confirms that this approach leads to *rapid compounding of abilities*: skills become *temporally extended, interpretable, and compositional*, letting the agent tackle more complex tasks much faster than learning from scratch each time. This design also keeps the system **compute-efficient** – once a skill is learned, using it costs almost nothing (just running the code), whereas an LLM call is relatively expensive.

## 4. Representing Skills: Pure Functions vs. Stateful Objects

When designing the agent's skill implementations, an important architectural decision is how to represent these skills in code. Should each skill be a **pure function** (no side-effects except acting on the environment, and no internal persistent state between calls), or a **stateful object** (maintaining internal variables or memory across invocations)?

**Pure Function Approach:** Treat each skill as a standalone function that takes some inputs (if needed) and performs a sequence of actions via the game API. The function may of course affect the game world (that's the point) and may query global state, but it does not hold its own long-lived state between uses. For example:

```python
def navigate_to(x, y):
    """Moves the agent to tile (x,y) using A* search."""
    # (Implementation that maybe uses a local fringe/open_set, etc.)
    return  # when done, agent is at (x,y)
```

If the agent needs to go to two different locations successively, it just calls `navigate_to` twice with different parameters; each call computes its path anew (or uses global pathfinding utilities).

**Stateful Skill Object Approach:** Encapsulate skills in classes or objects that can carry internal state. For instance:

```python
class Navigator:
    def __init__(self):
        self.map = {}  # internal map memory of discovered terrain
    def navigate_to(self, x, y):
        # uses self.map to avoid visited areas, etc.
```

This way, the Navigator could learn or update `self.map` as it explores, and reuse that info on subsequent calls.

**Trade-offs:**

* **Reusability and Modularity:** *Pure functions* are highly modular – any skill can call any other simply by invoking the function. This makes composition straightforward (as seen with the skill reuse examples). Pure functions with clear inputs/outputs are also easier to debug and test in isolation. *Stateful objects* can still be composed, but you then have to ensure you pass the right object around or use some shared global object. It adds complexity: e.g., if one skill's state influences another, you must manage references or shared state carefully. For an LLM-generated system, simpler is better – so leaning towards pure functions or at most simple classes with static methods is wise, to keep the prompt and code understanding manageable.

* **Memory & Partial Observability:** Partial observability often implies the agent should **remember** information (e.g. what it has seen of the map). Where to store this memory? If we use pure functions, one approach is to maintain a *global memory structure* (like the agent's knowledge base) that functions can read/write. For instance, a global `world_map` dictionary that all navigation functions update with newly seen areas. Each function call explicitly updates this global if needed. This retains functional purity at the skill level (no hidden state in the function), but allows across-calls memory via the global context. Alternatively, a stateful object like `Navigator` holds the map. Both can achieve the same result. The difference is mainly organizational: global vs encapsulated.

* **Safety and Clarity:** Pure functions have the advantage of not carrying hidden state that might unpredictably change behavior. Each call's behavior is determined by its parameters and global env, nothing else hidden. This transparency is useful for an autonomous agent because it's easier to trace why something happened. Stateful skills could accumulate subtle state that's hard to debug (imagine a `SearchAgent` object that keeps an internal counter of steps – if that isn't reset correctly between tasks, it could cause weird behavior). Since our agent is itself debugging and improving its code, having simpler, stateless code makes it *easier for the LLM to reason about it*. A large language model can read a function and understand it more easily if the function doesn't depend on complex external state (beyond what's obvious like calling sensor APIs).

* **Concurrency and Multi-goal handling:** If the system ever needs to interleave tasks or handle multiple objectives, stateful skills could cause interference. Pure functions (especially if they rely only on passed-in parameters and global read-only knowledge) avoid this – they run and finish without lingering effects (besides environment changes). This is safer in multi-agent or multi-task scenarios.

**Our Design Choice:** We lean towards representing skills as **mostly pure functions** (possibly with parameters to generalize them). This aligns with how Voyager and similar systems treat skills – essentially as scripts or subroutines that can be invoked when needed. Voyager's skills were **interpretable and modular code snippets** that could be transferred between agents or runs. This suggests they were not heavily reliant on hidden object state; they operated on the environment and explicit inputs (like item names or coordinates). Their composability was a major asset – e.g., they combined skills like *crafting tools* and *mining resources* to form higher-level routines, which is easiest done when those skills are functions that can be called in sequence.

We can still allow some state *in a controlled way*:

* The agent itself can maintain a global **memory object** (like an in-memory database of the world). Skills can update this. For example, a `explore_area()` skill might populate a global map with discovered tiles. Another skill `plan_route()` can consult this global map. The key is the state is part of the agent's central knowledge, not encapsulated in a skill that might not be accessible elsewhere.
* If using classes for organizational purposes (e.g., grouping related skills), we ensure they're mostly wrappers around static logic. For instance, a `CombatSkill` class might hold some configuration (like preferred weapon) but its method `execute_combat()` just runs a sequence using current game state each time, rather than relying on an internal memory of last fight.

**Example – Pure vs Stateful:** Consider a **patrolling** skill where the agent guards an area by walking back and forth. A pure function implementation might take a path or waypoints as input and loop through them:

```python
def patrol(path_points):
    for pt in path_points:
        move_to(pt.x, pt.y)
    # loop back:
    for pt in reversed(path_points):
        move_to(pt.x, pt.y)
```

It doesn't retain anything between calls – if called again, it would do the same patrol. A stateful version might be:

```python
class Patroller:
    def __init__(self, path_points):
        self.path = path_points
        self.step = 0
        self.direction = 1  # 1 forward, -1 backward
    def patrol_step(self):
        # move one step in the patrol
        target = self.path[self.step]
        move_to(target.x, target.y)
        self.step += self.direction
        if self.step == len(self.path)-1 or self.step == 0:
            self.direction *= -1
```

Here the object remembers where it left off in the patrol. This is more complex but supports continuous patrolling without repeating the whole loop in one function call. In a single-threaded agent context, we could achieve similar behavior with a generator or by storing an index in a global variable if needed. If possible, we would prefer the simpler approach (patrol as a single function that perhaps loops indefinitely until some condition or a higher-level controller stops it). In scenarios where we truly need persistent state (like ongoing behaviors that aren't completed in one call), we might introduce a controlled stateful mechanism (e.g., a global event loop that calls skills stepwise, maintaining their state externally).

**Conclusion on Skill Representation:** For clarity, ease of learning, and safety, we recommend treating skills as pure functions or simple procedures. This makes them **easier to reuse** and **share**. In fact, one of the benefits noted in Voyager was that the learned skills were *human-readable and transferable* to other agents or runs. That implies a functional style – you can literally copy the code snippet and use it elsewhere. If each skill were an object tightly coupled with agent-specific state, transferring it would be harder. So, to meet the requirement of being usable in open-source and by any backend, simple function-based skills are best.

We will, however, ensure that the agent's *memory of the world* (for partial observability) is maintained at the agent level. So the agent might have a data structure like `agent.world_knowledge` that skills consult. This way, we achieve the effect of stateful memory (for things like mapping, remembering last known positions of targets, etc.) without complicating the skill interfaces. It's a clean separation: **skills = actions on environment**, **agent = owns knowledge/state**.

## 5. Balancing Exploration vs. Exploitation in Skill Learning

An agent that only exploits known skills may stagnate, and one that only explores new things may waste time or fail to consolidate knowledge. We need a strategy to balance **exploration** (trying novel tasks or strategies to discover new skills) versus **exploitation** (leveraging current best-known skills to achieve goals efficiently) during the agent's learning process. This is akin to the classic explore-exploit tradeoff in reinforcement learning, but in our context it's about *skill learning and usage*.

**Automatic Curriculum (Task Scheduler):** We propose to include an **Automatic Curriculum** module (as shown in the architecture) that decides what task or goal the agent should tackle next. This module can dynamically bias towards exploration or exploitation based on the agent's progress:

* The curriculum keeps track of **unexplored goals** vs. **mastered goals**. For example, in a sandbox game like Minecraft, unexplored might include "visit a new biome" or "craft a novel item" while mastered goals are ones it has done (and has a skill for).
* It assigns a notion of **novelty score** or *intrinsic reward* to potential tasks. Tasks that lead the agent to experience new states or require new skills are given higher novelty values. This encourages exploration. In Voyager, GPT-4 was used to suggest tasks under an overarching goal of "discover as many diverse things as possible" – effectively an in-context **novelty search** guiding exploration. We can replicate a simpler version: use an LLM or heuristic to propose a new goal that the agent hasn't tried yet whenever exploration is needed.
* Simultaneously, the curriculum knows which skills the agent has and their competence. If a complex objective can now be achieved by composing known skills (exploitation), the curriculum will eventually select that to test the agent's ability and also potentially reveal any gaps.

**Exploration Mode:** At times, the system should deliberately push the agent outside its comfort zone. This could be triggered when:

* The agent has plateaued (no recent new skills or improvement).
* There are obvious gaps in skillset (e.g., agent has combat skills but never tried building structures).
* Simply on a schedule (every N tasks, do something novel).
  During exploration mode, the curriculum might use randomness or LLM creativity to generate a novel goal. For instance, *"You have never tried swimming across a river, attempt that"* or *"There is a rumor of treasure in a cave, go investigate"*. These tasks might not be immediately practical or might even fail, but they force the agent to develop new skills (like swimming, or dealing with darkness in a cave, etc.). The key is to keep such exploration *safe* – ensure it doesn't violate safety constraints (e.g., don't explore by intentionally doing something catastrophic in-game) and *limited* – maybe allocate a certain budget of trials to exploration before refocusing.

**Exploitation Mode:** On the other hand, the agent should capitalize on what it has learned to achieve goals more efficiently and to combine skills in useful ways. Exploitation tasks could include:

* Solving a known challenge faster or more optimally using the refined skills.
* Achieving a large objective that is essentially a composition of mastered sub-skills. For example, if the agent has learned "gather wood", "gather stone", "craft axe", etc., an exploitative goal might be "Build a log cabin" – which uses all those known skills in concert. This solidifies the skills and also serves as a test: if any skill is lacking (maybe it didn't learn how to make a door for the cabin), that gap becomes apparent.
* Repeating earlier tasks in new contexts to ensure generalization. For instance, if it learned to solve a maze layout A, try a different maze layout B (exploitation of the strategy in a new instance, which also has a bit of exploration but within a known skill domain).

**Balancing Strategy:** We can formalize the balance with a few approaches:

* **Epsilon-greedy-like scheduling:** At each decision point, with probability ε (say 20%), pick a purely exploratory task; with probability 1-ε, pick a task that exploits or extends existing skills. The value of ε can decay over time as the agent becomes more competent (like annealing in RL), meaning early on it explores a lot, later it focuses on optimizing what it knows. However, since our environment might be open-ended, we might keep a small ε > 0 always to continue finding new things indefinitely.
* **Intrinsic reward and meta-optimization:** We can assign a *score* to each potential next task as a weighted sum of novelty and utility. Novelty could be measured by how many new state elements or new skill requirements the task entails (e.g., if it needs a skill the agent doesn't have, that's high novelty). Utility could be an extrinsic reward if available (some games have points or progress metrics). Then pick the task with the highest score. This is akin to the *upper confidence bound (UCB)* approach where you favor tasks that are either unexplored or have high value. In absence of extrinsic rewards, novelty alone drives selection (which is what Voyager did – maximizing exploration of new items and areas).
* **LLM-guided curriculum:** We can actually prompt an LLM to generate suggestions for the next goal given the agent's state and skills. For example: *"The agent has learned to chop wood, build fire, and fish. What should it try next that is new and interesting?"* The LLM might respond: "Perhaps build a shelter or explore beyond the forest." This introduces a heuristic but can yield creative exploration tasks. For exploitation, we could similarly ask: *"Given these skills, what larger project can it accomplish?"* This approach was used in **Promptbreeder/OPRO** for optimizing prompts via language and in Voyager to create an automatic curriculum focusing on novel discoveries. It's light on compute (just some text generation) and can be done with a smaller model or even rules to avoid heavy usage of a big model.

**Example of Balance:** Imagine our agent in a Minecraft-like world:

* Early on, it explores basic skills (exploration-heavy): it wanders around, learns to mine wood, craft planks, make a crafting table. These are novel, so the curriculum keeps suggesting new basic tasks (explore a cave, find coal, etc.).
* Once foundational skills are there, the curriculum might switch to a bigger goal (exploitative): "Build a basic house." This uses known skills (gather wood, craft planks) but also pushes the agent to possibly learn a new one (build\_wall structure if it hasn't).
* After building a house (exploit success), the curriculum injects a novel challenge: "There is a lake nearby; figure out how to cross it." This might require learning to build a boat – a new skill (exploration).
* If the agent now has boat-building, maybe suggest "Travel across the lake to find new lands" (exploit the boat skill in a broader way, while also leading to new terrain = exploration).
* Throughout, the agent also revisits earlier tasks with higher expectations: e.g., initially it took 10 steps to kill a monster clumsily, now with better weapons, can it do it in 3 steps without losing health? This exploitation ensures it fine-tunes usage of skills for efficiency.

By alternating in this fashion, the agent **continuously learns** (no long stagnation) while also **consolidating knowledge** (not forgetting to use what it learned). This addresses *lifelong learning*: as noted, many older LLM agents weren't lifelong learners, but by having a loop that explicitly includes exploring new tasks and accumulating skills for reuse, our agent becomes one.

One can draw an analogy to human learning: sometimes you practice what you know (exploitation) to get better or achieve a milestone, other times you try something entirely new (exploration) to expand your capabilities. The automatic curriculum emulates this balance in a structured way.

**Measuring Balance:** We might implement simple metrics to ensure the agent doesn't veer too far to either side:

* Track the ratio of new skills learned vs. old skills reused in a recent window. If the agent hasn't learned anything new in a while, increase exploration probability. If it's only learning new things but failing to integrate them, schedule some tasks that require integrating multiple skills.
* Use success rate and competency as signals: if the agent fails too many exploratory tasks in a row, maybe shift to exploitation to build confidence (or improve some base skills). Conversely, if all tasks are easily done, it's time to up the challenge.

In **open-source, compute-limited settings**, a practical strategy might be *to explicitly script the alternation*: e.g., for every 3 tasks solved, allocate 1 task purely for exploration. This is easy to implement and ensures some balance without complex computations. For a more adaptive approach, the intrinsic reward method can be used but might require tuning.

To conclude, balancing exploration and exploitation in our system is handled by the curriculum/planning component. We ensure constant progress by injecting novelty, while also frequently using and testing existing skills in larger combinations. The end result is an agent that **continuously expands its skill set** while **reinforcing and optimizing its prior knowledge**. This balance was critical in systems like Voyager, which explicitly maximized exploration (leading to 3.3× more unique discoveries than baselines) but also used its skill library to achieve goals that other agents couldn't. By following a similar approach, our agent will not only learn a wide array of behaviors but do so efficiently and safely, ready to tackle increasingly complex challenges.

## Conclusion and Implementation Summary

Bringing it all together, our self-improving code generation system for game agents operates in a loop of **prompted code generation, execution with feedback, and iterative refinement**, gradually building a repertoire of skills. We started with basic primitives and showed how the agent can engineer prompts to reliably compose those into bigger tasks (Section 1). We introduced a robust self-debugging mechanism to handle errors and ensure each skill the agent saves is correct (Section 2). We emphasized the importance of skill reuse via an efficient library and retrieval system, enabling transfer of knowledge between tasks (Section 3). We reasoned about skill representation, favoring pure functions for clarity and modularity, which fits well with LLM-based code generation and partial observability needs (Section 4). Finally, we discussed strategies to balance exploration of new skills vs. exploitation of learned skills, via an automatic curriculum that drives open-ended learning (Section 5).

**Concrete Implementation Strategies:**

* Use a *modular design*: e.g., a Python framework where the agent is an object that holds the skill library (perhaps as a dict and an embedding index) and has methods like `learn_new_skill(goal)` which encapsulates the prompt LLM → execute → debug loop. Another method `choose_next_goal()` implements the curriculum strategy.
* Integrate with any LLM via an abstraction layer: one can write a wrapper that takes our prompt components and calls either OpenAI API or a local model API. The key is to handle the differences (e.g., for chat models, format prompt as system+user messages; for text completion models, send one concatenated prompt string).
* Testing and sandboxing: Wrap the execution of generated code in try/except to catch errors, and possibly run it in an isolated thread or subprocess with limited privileges (especially if using Python execution). This ensures safety and that our agent process remains stable even if generated code has issues (like infinite loops or heavy computation – we can impose a step limit or timeout on execution).
* Logging and monitoring: For development, have the agent log each prompt, code output, and result. This will help refine prompt engineering by seeing where the model might misbehave or need more guidance. Over time, we can enrich the prompt or few-shot examples to handle common pitfalls observed in logs.
* Maintain safety by design: Only expose safe API functions to the code (the environment API can be a controlled object the code calls into). Double-check outputs with regex or static analysis for any disallowed patterns (for example, if it's supposed to just call game API, ensure no import os or similar in the code).
* Evaluate incrementally: Start in a simple gridworld or text-based game to validate the approach (since partial observability and skill learning can be demonstrated even in a grid maze or a text adventure). Then scale up to more complex environments (the architecture remains the same).

By following this design, we fulfill the requirements: the agent handles partial observability by using memory and exploratory code; it's model-agnostic by relying only on prompt-based LLM usage; it's compute-efficient by reusing skills and avoiding retraining; and it maintains safety through careful prompting, sandboxing, and internal checks. This kind of system is at the cutting edge of AI research – as evidenced by projects like Voyager and SICA – yet is implementable today with open-source tools and models. It offers a promising pathway to game agents that **learn and evolve through coding themselves**, all while under the guidance of our prompts and safety constraints.

**Sources:**

1. Vogels et al., *Voyager: An Open-Ended Embodied Agent with LLMs*, 2023 – key components of exploration curriculum, skill library, and iterative prompting.
2. My Social (Medium), *Meet Voyager, the GPT-4 Powered AI Agent...*, 2023 – explanation of Voyager's architecture and self-improvement loop.
3. Chen et al., *Teaching Large Language Models to Self-Debug*, 2023 – technique for LLMs to debug code via execution feedback and explanation.
4. Wang et al., *Voyager skill library and prompting mechanism* (Project page) – details on skill embedding retrieval and self-verification via GPT-4 feedback.
5. Medium (My Social), *Voyager Key Features*, 2023 – benefits of skill interpretability, composability, and lifelong learning in an LLM-driven agent.
6. SICA Paper (Robeyns et al., 2025), *Self-Improving Coding Agent* – demonstrated performance gains with self-editing code and safety considerations.
7. Synthesis AI Blog, 2025 – framing code generation as a partially observable MDP, enabling iterative solution refinement with feedback.
8. Voyager Project Page – highlights of exploration vs exploitation (automatic curriculum for novelty vs using skill library to generalize).