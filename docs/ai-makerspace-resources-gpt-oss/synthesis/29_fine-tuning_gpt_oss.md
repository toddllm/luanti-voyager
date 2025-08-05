# Fine-tuning - Implementation Guide (GPT-OSS)

Generated: 2025-08-05T18:21:21.442054
Model: gpt-oss:20b

---

**Fine‑tuning in Luanti Voyager**

1. **What is Fine‑tuning?**  
Fine‑tuning is the process of taking a pre‑trained model (e.g., a language or RL policy) and training it on a smaller, domain‑specific dataset so it learns the nuances of that domain. In Luanti Voyager, you fine‑tune the AI agent’s policy or dialogue model on logs from the game world so it behaves and speaks like a true in‑world NPC.

2. **How to implement it for game AI agents**  

- **Collect domain data**  
  - Log player–agent interactions, item‑crafting traces, combat logs, or chat transcripts.  
  - Format each example as `(state, action)` for policy training or `(prompt, response)` for language training.

- **Pre‑process & split**  
  - Tokenize text with the same tokenizer used for the base model.  
  - Split into train/validation/test sets (e.g., 80/10/10).  

- **Choose a base model**  
  - For dialogue: `gpt‑neo‑125M` or `llama‑7B`.  
  - For policy: a reinforcement‑learning policy network already loaded with a pre‑trained backbone (e.g., `DQN` with a BERT encoder).

- **Set up a training script**  
  - Use HuggingFace `Trainer` or a custom PyTorch loop.  
  - Freeze lower layers if memory is limited; fine‑tune only top layers or the head.  
  - Set a low learning rate (e.g., `2e‑5`) and a small batch size.  

- **Integrate with the game loop**  
  - After fine‑tuning, load the checkpoint into the Voyager AI manager.  
  - Use the `predict()` API to generate actions or dialogue in real time.  
  - Monitor perplexity or policy loss and retrain periodically with new data.

- **Deploy & monitor**  
  - Package the checkpoint with the game server.  
  - Log AI decisions for future fine‑tuning iterations.  

3. **Simple code example** (Python, HuggingFace)

```python
from transformers import GPTNeoForCausalLM, GPTNeoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset

# 1. Load domain data (CSV with columns: "prompt","response")
dataset = load_dataset("csv", data_files={"train":"voyager_train.csv",
                                          "validation":"voyager_val.csv"})

tokenizer = GPTNeoTokenizer.from_pretrained("EleutherAI/gpt-neo-125M")

def tokenize(example):
    return tokenizer(example["prompt"] + tokenizer.eos_token + example["response"],
                     truncation=True, padding="max_length", max_length=128)

tokenized = dataset.map(tokenize, batched=True, remove_columns=["prompt","response"])

# 2. Training args
args = TrainingArguments(
    output_dir="./voyager_finetuned",
    overwrite_output_dir=True,
    per_device_train_batch_size=4,
    num_train_epochs=3,
    learning_rate=2e-5,
    logging_steps=100,
)

model = GPTNeoForCausalLM.from_pretrained("EleutherAI/gpt-neo-125M")

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["validation"],
)

trainer.train()
trainer.save_model()
```

4. **Game‑specific use case**

*NPC Crafting Guide* – Fine‑tune a GPT‑Neo model on logs of successful crafting recipes.  
- **Goal:** When a player asks “How do I make a Netherite sword?”, the NPC answers with the exact step‑by‑step recipe.  
- **Process:**  
  1. Log every crafting interaction.  
  2. Fine‑tune the language model on `(player_request, npc_response)` pairs.  
  3. Deploy the checkpoint so the in‑world “Crafting Master” NPC can provide instant, accurate advice, improving player onboarding and reducing frustration.  

This concise workflow lets you turn generic AI into a game‑aware, context‑sensitive assistant in Luanti Voyager with minimal code and data.