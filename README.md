# Tactical RPG — Human-First AI Arena

## File Structure

| File | Purpose |
|------|---------|
| `step1_training.py` | RL environment + PPO training for all 4 AI personalities |
| `llm_engine.py` | Narrative, reasoning, confidence & threat analysis engine |
| `step3_gui.py` | Main Tkinter GUI — human-first gameplay with full LLM integration |
| `requirements.txt` | Python dependencies |

## Setup

```bash
pip install -r requirements.txt
```

## Step 1 — Train the AI models

```bash
python step1_training.py
```

Choose option 1 to train all 4 personalities (aggressive, defensive,
strategist, chaotic). Each saves as `npc_<personality>.zip`.
Quick test: choose option 2 (aggressive only, ~20 minutes).

## Step 2 — Play the game

```bash
python step3_gui.py
```

Requires at least one trained model file in the same directory.

---

## Human-First Features (What forces your brain to work)

### Decision Timer
Every turn has a countdown: 16s Easy / 12s Normal / 8s Hard.
If you run out of time, the AI takes the turn automatically.
Hard mode is designed to make most players feel rushed.

### Contextual Tactical Puzzles
Each turn opens with a scenario question based on the ACTUAL
game state — not generic text. Example:
"Your DPS is at 20% HP and two enemies are alive. What is the priority?"

### Mandatory Reasoning Selection
After choosing an action AND a target, you must pick WHY
you made that choice from a tactical options list.
This forces strategy articulation — not button-mashing.

### After-Move Analysis
Every turn ends with whether your decision was correct and why.
If a better option existed it is shown with explicit reasoning.
Example: "Enemy Healer was active — you should have burst her first."

### AI Hints Cost Points
You can request AI suggestions, but each costs 5 points.
The hint penalty total appears in the post-game summary so
professors can see whether you played independently.

### Threat Matrix
Live display of each enemy's threat value so you can form
decisions without manually computing from raw numbers.

---

## Personalities

| Personality | Behaviour |
|-------------|-----------|
| Aggressive  | Favours attacks, focuses high-threat targets |
| Defensive   | Prefers healing and defending when allies are low |
| Strategist  | Adapts dynamically — heals if critical, attacks if safe |
| Chaotic     | 20% random actions — unpredictable pressure |

## Difficulty Scaling

| Difficulty | Enemy DMG | Crit Chance | Timer | Enemy HP |
|------------|-----------|-------------|-------|----------|
| Easy       | ×0.7      | 5%          | 16s   | Normal   |
| Normal     | ×1.0      | 10%         | 12s   | Normal   |
| Hard       | ×1.5      | 22%         | 8s    | +40%     |
