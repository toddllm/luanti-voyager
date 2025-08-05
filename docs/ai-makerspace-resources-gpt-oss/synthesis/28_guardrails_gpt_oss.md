# Guardrails - Implementation Guide (GPT-OSS)

Generated: 2025-08-05T18:20:46.204148
Model: gpt-oss:20b

---

**Guardrails in Luanti Voyager – Quick Implementation Guide**  
*< 500 words – practical, code‑focused*

---

### 1. What is Guardrails?  
Guardrails are high‑level constraints that keep AI agents’ behavior within safe, predictable boundaries. They act like a virtual “no‑go” zone, automatically overriding low‑level decisions that would break game rules, damage the world, or create undesirable interactions. Think of them as invisible fences that shape NPC logic without hard‑coding every rule.

---

### 2. How to implement Guardrails for AI agents  

- **Define the scope**  
  * Choose which agents need guardrails (e.g., villagers, mobs, player‑controlled bots).  
  * Decide the type of constraints: positional, interaction, resource, or combat.

- **Create a Guardrail class**  
  ```java
  public abstract class Guardrail {
      public abstract boolean isViolated(Agent agent, World world);
      public abstract void enforce(Agent agent, World world);
  }
  ```

- **Implement specific guardrails**  
  * *BoundaryGuard* – keeps agents inside a defined radius.  
  * *InteractionGuard* – blocks access to protected blocks (e.g., chests in admin area).  
  * *CombatGuard* – limits aggression to non‑hostile mobs.

- **Attach guardrails to the AI scheduler**  
  ```java
  agent.addGuardrail(new BoundaryGuard(30));   // 30‑block radius
  agent.addGuardrail(new InteractionGuard(protectedChest));
  ```

- **Hook guardrails into the tick/update loop**  
  ```java
  @Override
  public void tick() {
      for (Guardrail g : guardrails) {
          if (g.isViolated(this, world)) {
              g.enforce(this, world);
          }
      }
      // proceed with normal AI logic
  }
  ```

- **Prioritize guardrails**  
  Guardrails should run **before** the agent’s normal decision tree so that any violation is corrected instantly.

- **Test in sandbox mode**  
  Enable a debug flag to log guardrail triggers for quick iteration.

---

### 3. One simple code example  

Below is a minimal **BoundaryGuard** that forces an agent to stay within a 20‑block radius of a spawn point.

```java
public class BoundaryGuard extends Guardrail {
    private final BlockPos center;
    private final int radius;

    public BoundaryGuard(BlockPos center, int radius) {
        this.center = center;
        this.radius = radius;
    }

    @Override
    public boolean isViolated(Agent agent, World world) {
        return center.distanceSq(agent.getPosition()) > radius * radius;
    }

    @Override
    public void enforce(Agent agent, World world) {
        // Move the agent back toward the center
        Vec3d toCenter = center.subtract(agent.getPosition()).normalize();
        agent.setVelocity(toCenter.multiply(0.3)); // gentle push
        System.out.println("Guardrail: Agent " + agent.getId() +
                           " was outside boundary, moved back.");
    }
}
```

*Usage*

```java
Agent villager = new Agent(...);
villager.addGuardrail(new BoundaryGuard(villager.getSpawnPos(), 20));
```

---

### 4. Game‑specific use case  

**Scenario:** In Luanti Voyager, an AI‑controlled mining bot must not dig below the “stone‑layer” (y = 12) to preserve the world’s bedrock and prevent players from exploiting underground resources.

**Guardrail implementation**

```java
public class MiningDepthGuard extends Guardrail {
    private final int minY;

    public MiningDepthGuard(int minY) { this.minY = minY; }

    @Override
    public boolean isViolated(Agent agent, World world) {
        return agent.getPosition().y < minY;
    }

    @Override
    public void enforce(Agent agent, World world) {
        // Stop mining action and send agent to safe zone
        agent.stopMining();
        agent.moveTo(agent.getSpawnPos().add(5, 0, 5)); // nearby safe spot
        System.out.println("Guardrail: Mining bot prevented from going below y=" + minY);
    }
}
```

Attach to all mining bots:

```java
miningBot.addGuardrail(new MiningDepthGuard(12));
```

With this guardrail, bots automatically retreat when they reach the forbidden depth, preventing resource leaks and maintaining world integrity.

---

**Summary**  
Guardrails give you a modular, reusable way to enforce high‑level rules on AI agents. Define a base class, implement specific constraints, hook them into the update cycle, and test thoroughly. In Luanti Voyager, guardrails protect core game mechanics—be it keeping NPCs within bounds, preventing resource abuse, or maintaining safe interactions—while still letting your AI agents enjoy rich, autonomous behavior.