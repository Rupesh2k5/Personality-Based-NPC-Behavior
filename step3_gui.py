# """
# STEP 3: ULTIMATE AI RPG ARENA - FULL LLM-RL HYBRID INTEGRATION
# ================================================================
# Complete integration with LLM strategic reasoning and RL execution
# All buttons functional, AI strategies displayed at each step
# """

# import tkinter as tk
# from tkinter import ttk, scrolledtext, messagebox, filedialog
# from stable_baselines3 import PPO
# import json
# from datetime import datetime
# import os
# import numpy as np
# import random

# # Smart imports - try multiple possible class names
# try:
#     from step1_training import TacticalRPG as GameEnv
# except ImportError:
#     try:
#         from step1_training import EnhancedTacticalRPG as GameEnv
#     except ImportError:
#         # Fallback basic environment
#         import gymnasium as gym
#         from gymnasium import spaces
        
#         class GameEnv(gym.Env):
#             def __init__(self, personality="aggressive"):
#                 super().__init__()
#                 self.personality = personality
#                 self.action_space = spaces.MultiDiscrete([3, 5])
#                 self.observation_space = spaces.Box(low=0, high=1, shape=(72,), dtype=np.float32)
#                 self.max_steps = 30
#                 self.reset()
            
#             def reset(self, seed=None, options=None):
#                 super().reset(seed=seed)
#                 self.step_count = 0
#                 self.chars = [
#                     [2, 2, 100, 100, 0, 0],  # Ally Tank
#                     [3, 2, 80, 80, 1, 0],    # Ally DPS
#                     [1, 2, 60, 60, 2, 0],    # Ally Healer
#                     [7, 7, 45, 45, 1, 1],    # Enemy DPS
#                     [8, 6, 50, 50, 0, 1],    # Enemy Tank
#                     [6, 8, 35, 35, 2, 1],    # Enemy Healer
#                 ]
#                 self.relations = np.zeros((6, 6))
#                 for i in range(6):
#                     for j in range(6):
#                         self.relations[i][j] = 1.0 if self.chars[i][5] == self.chars[j][5] else -1.0
#                 self.threat_matrix = np.ones((1, 3))
#                 self.action_history = []
#                 return self._get_obs(), {}
            
#             def _get_obs(self):
#                 obs = []
#                 for c in self.chars:
#                     obs.extend([c[0] / 10, c[1] / 10, c[2] / c[3], c[4] / 2, c[5], 1.0 if c[2] > 0 else 0.0])
#                 obs.extend(self.relations.flatten())
#                 return np.array(obs[:72], dtype=np.float32)
            
#             def step(self, action):
#                 target_idx, action_type = int(action[0]), int(action[1])
#                 enemy_idx = 3 + target_idx if target_idx < 3 else target_idx
#                 if enemy_idx >= len(self.chars):
#                     enemy_idx = 3
                
#                 target = self.chars[enemy_idx]
#                 reward = 0
#                 info = {"success": False}
                
#                 if action_type == 0:  # Attack
#                     if target[2] > 0:
#                         dmg = random.randint(25, 35)
#                         target[2] = max(0, target[2] - dmg)
#                         info["damage"] = dmg
#                         if target[2] == 0:
#                             reward += 500
#                             info["kill"] = True
#                             info["killed_enemy"] = True
#                         info["success"] = True
#                     else:
#                         reward -= 100
#                 elif action_type == 4:  # Heal
#                     if target[2] > 0 and target[2] < target[3]:
#                         heal = random.randint(20, 30)
#                         target[2] = min(target[3], target[2] + heal)
#                         info["heal"] = heal
#                         info["success"] = True
                
#                 reward -= 5
                
#                 enemy_alive = sum(1 for c in self.chars[3:] if c[2] > 0)
#                 ally_alive = sum(1 for c in self.chars[:3] if c[2] > 0)
                
#                 done = False
#                 if ally_alive == 0:
#                     reward -= 1000
#                     done = True
#                     info["result"] = "defeat"
#                 elif enemy_alive == 0:
#                     reward += 2000
#                     done = True
#                     info["result"] = "victory"
                
#                 self.step_count += 1
#                 if self.step_count >= self.max_steps:
#                     reward -= 3000
#                     done = True
#                     info["result"] = "timeout"
                
#                 self.action_history.append(action)
#                 return self._get_obs(), reward, done, False, info

# # Try to import LLM system
# try:
#     from step2_llm_integration import LLMStrategicAnalyzer, HybridLLMRL_NPC
#     LLM_AVAILABLE = True
# except ImportError:
#     print("⚠️  LLM system not found - using fallback explanations")
#     LLM_AVAILABLE = False
    
#     class FallbackLLM:
#         def __init__(self):
#             self.call_count = 0
        
#         def analyze_battle(self, chars, action):
#             self.call_count += 1
#             roles = ['Tank', 'DPS', 'Healer']
#             enemies = [c for c in chars[3:] if c[2] > 0]
#             if not enemies:
#                 return {
#                     'reasoning': "All enemies eliminated - victory achieved!",
#                     'threat_level': 'none',
#                     'priority_target': None,
#                     'confidence': 1.0
#                 }
            
#             lowest_hp = min(enemies, key=lambda c: c[2])
#             idx = chars.index(lowest_hp)
#             return {
#                 'reasoning': f"Strategic focus on weakest enemy {roles[lowest_hp[4]]} to reduce enemy count quickly.",
#                 'threat_level': 'medium',
#                 'priority_target': idx,
#                 'confidence': 0.85
#             }
    
#     class FallbackHybrid:
#         def __init__(self, model, llm):
#             self.model = model
#             self.llm = llm
#             self.decision_history = []
        
#         def decide(self, obs, chars):
#             action, _ = self.model.predict(obs, deterministic=True)
#             analysis = self.llm.analyze_battle(chars, action)
            
#             roles = ['Tank', 'DPS', 'Healer']
#             teams = ['Ally', 'Enemy']
#             target_idx = int(action[0])
#             action_type = int(action[1])
#             actions = ['Attack', 'Defend', 'Ability', 'Move', 'Heal']
            
#             target = chars[target_idx] if target_idx < len(chars) else chars[0]
            
#             explanation = {
#                 'action': f"{actions[action_type]} → {teams[target[5]]} {roles[int(target[4])]}",
#                 'reasoning': analysis['reasoning'],
#                 'confidence': analysis['confidence'],
#                 'threat_level': analysis['threat_level'],
#                 'alternatives': [
#                     {'action': 'Defend', 'why': 'Passive - doesn\'t advance victory'},
#                     {'action': 'Heal lowest ally', 'why': 'Team HP manageable currently'}
#                 ],
#                 'source': '🤖 Hybrid System (Fallback)',
#                 'llm_calls': self.llm.call_count
#             }
            
#             self.decision_history.append(explanation)
#             return action, explanation
        
#         def get_statistics(self):
#             return {
#                 'total_decisions': len(self.decision_history),
#                 'llm_api_calls': self.llm.call_count,
#                 'avg_confidence': np.mean([d['confidence'] for d in self.decision_history]) if self.decision_history else 0,
#                 'cache_hit_rate': 0
#             }


# PUZZLES = [
#     "Your DPS ally is at 20% HP and two enemies are alive. What is the correct priority?",
#     "The enemy Healer is restoring HP every turn. What should you focus on first?",
#     "All three enemies are alive but your team is at full HP. What is the optimal opening move?",
#     "One enemy is at single-digit HP — one hit from death. Do you focus them or spread damage?",
#     "Your Tank is absorbing hits well. Your Healer is untouched. Enemy DPS is dangerous. What is the threat?",
# ]

# REASONING_OPTIONS = [
#     "Enemy is low HP — finish them",
#     "Ally is critically wounded — must heal",
#     "Highest threat target first",
#     "Preserve my DPS unit",
#     "Reduce enemy count fast",
# ]


# class UltimateRPGUI:
#     def __init__(self):
#         self.root = tk.Tk()
#         self.root.title("🤖 LLM-RL Hybrid RPG Arena")

#         sw = self.root.winfo_screenwidth()
#         sh = self.root.winfo_screenheight()
#         w  = min(sw - 60, 1400)
#         h  = min(sh - 100, 920)
#         self.root.geometry(f"{w}x{h}")
#         self.root.configure(bg="#0d0d0d")

#         # Game state
#         self.battle_log = []
#         self.turn_count = 0
#         self.auto_play_id = None
#         self.auto = False
#         self.active = False
#         self.hint_penalty_total = 0

#         self.current_personality = tk.StringVar(value="aggressive")
#         self.difficulty = tk.StringVar(value="normal")
#         self.hero_buff_enabled = tk.BooleanVar(value=True)
#         self.human_choice_mode = tk.BooleanVar(value=False)  # Default AI mode

#         self.wins = 0
#         self.losses = 0
#         self.total_matches = 0

#         self.kill_log = []
#         self.revenge_target = None
#         self.revenge_mode = False

#         self.selected_action = None
#         self.selected_target = None
#         self.selected_reason = None

#         self.timer_val = 12
#         self.timer_max = 12
#         self.timer_job = None

#         self.available_personalities = self._check_models()
#         self._load_model()
#         self._setup_ui()
#         self.new_game()

#     def _check_models(self):
#         personalities = ["aggressive", "defensive", "strategist", "chaotic"]
#         available = [p for p in personalities if os.path.exists(f"npc_{p}.zip")]
#         if not available and (os.path.exists("npc_best.zip") or os.path.exists("npc_final.zip")):
#             available = ["aggressive"]
#         return available or ["aggressive"]

#     def _load_model(self):
#         p = self.current_personality.get()
#         for path in [f"npc_{p}.zip", "npc_best.zip", "npc_final.zip"]:
#             name = path.replace(".zip", "")
#             if os.path.exists(path):
#                 self.model = PPO.load(name)
#                 print(f"✓ Loaded: {path}")
#                 break
#         else:
#             messagebox.showerror("Error", "No trained model found!")
#             self.root.destroy()
#             return
        
#         # Initialize LLM system
#         if LLM_AVAILABLE:
#             self.llm = LLMStrategicAnalyzer(use_real_api=False)
#             print("✓ LLM system initialized")
#         else:
#             self.llm = FallbackLLM()
#             print("✓ Fallback LLM initialized")

#     def _diff_cfg(self):
#         cfg = {
#             "easy":   dict(dmg_mult=0.7,  crit=0.05, atk=(1, 8),  hp_bonus=0.0, timer=16),
#             "normal": dict(dmg_mult=1.0,  crit=0.10, atk=(4, 12), hp_bonus=0.0, timer=12),
#             "hard":   dict(dmg_mult=1.5,  crit=0.22, atk=(7, 18), hp_bonus=0.4, timer=8),
#         }
#         return cfg.get(self.difficulty.get(), cfg["normal"])

#     def _setup_ui(self):
#         # TOP BAR
#         top = tk.Frame(self.root, bg="#1a1a1a", height=56)
#         top.pack(fill=tk.X)
#         top.pack_propagate(False)

#         tk.Label(top, text="🤖 LLM-RL Hybrid RPG Arena", font=("Segoe UI", 15, "bold"),
#                  bg="#1a1a1a", fg="#00ff88").pack(side=tk.LEFT, padx=16)

#         ctrl = tk.Frame(top, bg="#1a1a1a")
#         ctrl.pack(side=tk.RIGHT, padx=16)

#         tk.Label(ctrl, text="Personality:", bg="#1a1a1a", fg="#aaaaaa",
#                  font=("Segoe UI", 9)).pack(side=tk.LEFT)
#         self.personality_combo = ttk.Combobox(
#             ctrl, values=[p.capitalize() for p in self.available_personalities],
#             state="readonly", width=12, font=("Segoe UI", 9))
#         self.personality_combo.set(self.current_personality.get().capitalize())
#         self.personality_combo.bind("<<ComboboxSelected>>", self._on_personality_change)
#         self.personality_combo.pack(side=tk.LEFT, padx=4)

#         tk.Label(ctrl, text="Difficulty:", bg="#1a1a1a", fg="#aaaaaa",
#                  font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(10, 4))
#         self.diff_combo = ttk.Combobox(ctrl, values=["Easy", "Normal", "Hard"],
#                                         state="readonly", width=8, font=("Segoe UI", 9))
#         self.diff_combo.set("Normal")
#         self.diff_combo.bind("<<ComboboxSelected>>",
#                               lambda e: self.difficulty.set(self.diff_combo.get().lower()))
#         self.diff_combo.pack(side=tk.LEFT)

#         self.buff_btn = tk.Button(ctrl, text="Hero Buff: ON",
#                                    command=self._toggle_buff,
#                                    bg="#2a2a2a", fg="#00ff88",
#                                    font=("Segoe UI", 9), relief=tk.FLAT, cursor="hand2")
#         self.buff_btn.pack(side=tk.LEFT, padx=10)

#         self.wl_label = tk.Label(top, text="W: 0 | L: 0",
#                                   bg="#1a1a1a", fg="#ffaa00",
#                                   font=("Segoe UI", 12, "bold"))
#         self.wl_label.pack(side=tk.RIGHT, padx=16)

#         # MAIN AREA
#         main = tk.Frame(self.root, bg="#0d0d0d")
#         main.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

#         # LEFT: Battlefield
#         left = tk.Frame(main, bg="#0d0d0d")
#         left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#         teams_frame = tk.Frame(left, bg="#0d0d0d")
#         teams_frame.pack(fill=tk.X, pady=(0, 8))

#         self.allies_frame = self._team_panel(teams_frame, "Your Team (Allies)", "#00ff88")
#         self.allies_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
#         self.enemies_frame = self._team_panel(teams_frame, "Enemy Team", "#ff4444")
#         self.enemies_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#         self.allies_labels = self._unit_rows(self.allies_frame, "#00ff88", 3)
#         self.enemies_labels = self._unit_rows(self.enemies_frame, "#ff4444", 3)

#         # Threat matrix
#         threat_lf = tk.LabelFrame(left, text="Threat Matrix",
#                                    font=("Segoe UI", 10, "bold"),
#                                    bg="#1a1a2e", fg="#ff8888", relief=tk.FLAT)
#         threat_lf.pack(fill=tk.X, pady=(0, 8))
#         self.threat_label = tk.Label(threat_lf, text="E0: 0.0  E1: 0.0  E2: 0.0",
#                                       font=("Consolas", 11, "bold"),
#                                       bg="#1a1a2e", fg="#ffaa00")
#         self.threat_label.pack(pady=6)

#         # Turn info
#         strip = tk.Frame(left, bg="#0d0d0d")
#         strip.pack(fill=tk.X, pady=(0, 8))
#         self.turn_label = tk.Label(strip, text="Turn 0",
#                                     font=("Segoe UI", 11, "bold"),
#                                     bg="#0d0d0d", fg="#cccccc")
#         self.turn_label.pack(side=tk.LEFT)

#         # Mode toggle
#         mode_frame = tk.Frame(left, bg="#1a1a2e")
#         mode_frame.pack(fill=tk.X, pady=(0, 8), padx=8)
#         tk.Label(mode_frame, text="Mode:", bg="#1a1a2e", fg="#ffffff",
#                  font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=4)
#         tk.Radiobutton(mode_frame, text="🤖 AI Auto", variable=self.human_choice_mode,
#                        value=False, bg="#1a1a2e", fg="#00ff88", selectcolor="#1a1a2e",
#                        font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)
#         tk.Radiobutton(mode_frame, text="👤 Human Control", variable=self.human_choice_mode,
#                        value=True, bg="#1a1a2e", fg="#ffaa00", selectcolor="#1a1a2e",
#                        font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)

#         # RIGHT: LLM panel + log
#         right = tk.Frame(main, bg="#0d0d0d", width=380)
#         right.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
#         right.pack_propagate(False)

#         llm_lf = tk.LabelFrame(right, text="🧠 LLM Strategic Reasoning",
#                                 font=("Segoe UI", 10, "bold"),
#                                 bg="#1a1a2e", fg="#ff66ff", relief=tk.FLAT)
#         llm_lf.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

#         self.reasoning_text = scrolledtext.ScrolledText(
#             llm_lf, font=("Segoe UI", 9), bg="#0d0d0d",
#             fg="#cccccc", wrap=tk.WORD, relief=tk.FLAT, bd=0)
#         self.reasoning_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
#         self._configure_reasoning_tags()

#         log_lf = tk.LabelFrame(right, text="📜 Battle Log",
#                                 font=("Segoe UI", 10, "bold"),
#                                 bg="#1a1a2e", fg="#88ff88", relief=tk.FLAT)
#         log_lf.pack(fill=tk.X)
#         self.log_text = scrolledtext.ScrolledText(
#             log_lf, font=("Consolas", 8), bg="#0d0d0d",
#             fg="#aaaaaa", state=tk.DISABLED, relief=tk.FLAT, bd=0, height=8)
#         self.log_text.pack(fill=tk.BOTH, padx=8, pady=8)

#         # BOTTOM BUTTONS
#         bot = tk.Frame(self.root, bg="#0d0d0d", pady=8)
#         bot.pack(fill=tk.X, padx=16)
        
#         buttons = [
#             ("▶ Next Turn", self._next_turn_manual, "#00aa00"),
#             ("⏩ Auto Play", self._toggle_auto, "#0066cc"),
#             ("🔄 New Game", self.new_game, "#cc6600"),
#             ("💾 Save", self._save_game, "#3399ff"),
#             ("📂 Load", self._load_game, "#3399ff"),
#             ("📊 Stats", self._show_stats, "#9933cc"),
#             ("💾 Export", self._export_log, "#9933cc"),
#             ("❌ Quit", self.root.quit, "#cc0000"),
#         ]
        
#         for text, cmd, bg in buttons:
#             btn = tk.Button(bot, text=text, command=cmd,
#                            bg=bg, fg="white",
#                            font=("Segoe UI", 9, "bold"),
#                            width=10, relief=tk.RAISED,
#                            cursor="hand2")
#             btn.pack(side=tk.LEFT, padx=3)
#             if "Auto" in text:
#                 self.auto_btn = btn

#         self.status = tk.Label(self.root, text="Ready",
#                                 font=("Segoe UI", 8),
#                                 bg="#0d0d0d", fg="#00ff88", anchor=tk.W, padx=16)
#         self.status.pack(fill=tk.X, side=tk.BOTTOM)

#     def _team_panel(self, parent, title, color):
#         lf = tk.LabelFrame(parent, text=title,
#                             font=("Segoe UI", 10, "bold"),
#                             bg="#1a1a2e", fg=color, relief=tk.FLAT)
#         return lf

#     def _unit_rows(self, parent, color, n):
#         labels = []
#         for i in range(n):
#             f = tk.Frame(parent, bg="#1a1a2e", pady=3)
#             f.pack(fill=tk.X, padx=8)
#             name = tk.Label(f, text=f"{i+1}. Unit", font=("Segoe UI", 10),
#                              bg="#1a1a2e", fg=color)
#             name.pack(side=tk.LEFT)
#             hp = tk.Label(f, text="—/—", font=("Consolas", 10, "bold"),
#                            bg="#1a1a2e", fg=color)
#             hp.pack(side=tk.RIGHT)
#             labels.append((name, hp))
#         return labels

#     def _configure_reasoning_tags(self):
#         t = self.reasoning_text
#         t.tag_config("header", foreground="#ff66ff", font=("Segoe UI", 10, "bold"))
#         t.tag_config("action", foreground="#00ff88", font=("Segoe UI", 10, "bold"))
#         t.tag_config("reasoning", foreground="#cccccc", font=("Segoe UI", 9))
#         t.tag_config("confidence", foreground="#00ff00", font=("Segoe UI", 9, "bold"))
#         t.tag_config("threat", foreground="#ff6600", font=("Segoe UI", 9, "bold"))

#     def new_game(self):
#         if self.auto_play_id:
#             self.root.after_cancel(self.auto_play_id)
#             self.auto_play_id = None
        
#         self.kill_log = []
#         self.revenge_target = None
#         self.revenge_mode = False
#         self.turn_count = 0
#         self.hint_penalty_total = 0

#         self._load_model()
#         self.env = GameEnv(personality=self.current_personality.get())
#         self.obs, _ = self.env.reset()

#         # Apply buffs
#         cfg = self._diff_cfg()
#         if self.hero_buff_enabled.get() and self.difficulty.get() != "hard":
#             for c in self.env.chars[:3]:
#                 c[3] = int(c[3] * 1.3)
#                 c[2] = c[3]
#             self._log_event("⚡ Hero buff active: +30% HP", "system")

#         if cfg['hp_bonus'] > 0:
#             for c in self.env.chars[3:]:
#                 c[3] = int(c[3] * (1 + cfg['hp_bonus']))
#                 c[2] = c[3]
#             self._log_event(f"🔥 Hard mode: enemy HP +{int(cfg['hp_bonus']*100)}%", "system")

#         # Create hybrid NPC
#         if LLM_AVAILABLE:
#             self.npc = HybridLLMRL_NPC(self.model, self.llm)
#         else:
#             self.npc = FallbackHybrid(self.model, self.llm)

#         self.active = True
#         self.auto = False

#         self.reasoning_text.delete(1.0, tk.END)
#         self.log_text.config(state=tk.NORMAL)
#         self.log_text.delete(1.0, tk.END)
#         self.log_text.config(state=tk.DISABLED)

#         self._update_display()
#         self._display_welcome()
#         self.status.config(text=f"🎮 New game - {self.current_personality.get().capitalize()} | {self.difficulty.get().capitalize()}")
#         self._log_event(f"🎮 New game started", "system")

#     def _display_welcome(self):
#         t = self.reasoning_text
#         t.insert(tk.END, "="*52 + "\n", "header")
#         t.insert(tk.END, "🤖 LLM-RL HYBRID SYSTEM\n", "header")
#         t.insert(tk.END, "="*52 + "\n\n")
#         t.insert(tk.END, "ARCHITECTURE:\n", "header")
#         t.insert(tk.END, "  • RL Agent: Optimal action selection\n")
#         t.insert(tk.END, "  • LLM: Strategic reasoning\n")
#         t.insert(tk.END, "  • Hybrid: Combined intelligence\n\n")
#         t.insert(tk.END, "Click 'Next Turn' or 'Auto Play' to start!\n", "action")

#     def _next_turn_manual(self):
#         """Manual next turn button"""
#         if not self.active:
#             return
#         self._execute_turn()

#     def _toggle_auto(self):
#         """Toggle auto-play mode"""
#         self.auto = not self.auto
#         if self.auto:
#             self.auto_btn.config(text="⏸ Pause", bg="#cc6600")
#             self._auto_loop()
#         else:
#             self.auto_btn.config(text="⏩ Auto Play", bg="#0066cc")
#             if self.auto_play_id:
#                 self.root.after_cancel(self.auto_play_id)
#                 self.auto_play_id = None

#     def _auto_loop(self):
#         if self.auto and self.active:
#             self._execute_turn()
#             self.auto_play_id = self.root.after(1500, self._auto_loop)

#     def _execute_turn(self):
#         """Execute one turn with LLM-RL hybrid"""
#         if not self.active:
#             return

#         self.turn_count += 1
#         self.turn_label.config(text=f"Turn {self.turn_count}")

#         # Get hybrid decision (LLM + RL!)
#         action, explanation = self.npc.decide(self.obs, self.env.chars)

#         # Execute action
#         self.obs, reward, done, _, info = self.env.step(action)
        
#         # Process enemy attacks
#         self._process_enemy_attacks()

#         # Track eliminations
#         if info.get('killed_enemy'):
#             target_idx = int(action[0])
#             self._track_elimination(target_idx, 0, False)

#         # Display LLM reasoning
#         self._display_llm_explanation(explanation, info)

#         # Log
#         self._log_event(f"Turn {self.turn_count}: {explanation['action']}", "action")

#         # Update display
#         self._update_display()

#         # Check game over
#         if done:
#             self._handle_game_end(info)
#             return

#         # Check if all allies dead
#         allies_alive = sum(1 for c in self.env.chars[:3] if c[2] > 0)
#         if allies_alive == 0:
#             self._handle_game_end({'result': 'defeat'})
#             return

#     def _process_enemy_attacks(self):
#         """Enemy counter-attacks"""
#         cfg = self._diff_cfg()
#         alive_enemies = [c for c in self.env.chars[3:] if c[2] > 0]
#         allies = [c for c in self.env.chars[:3] if c[2] > 0]
        
#         if not alive_enemies or not allies:
#             return

#         for enemy in alive_enemies:
#             target = random.choice(allies)
#             base = random.randint(*cfg['atk'])
#             dmg = int(base * cfg['dmg_mult'])
#             crit = random.random() < cfg['crit']
            
#             if crit:
#                 dmg = int(dmg * 2)

#             old = target[2]
#             target[2] = max(0, target[2] - dmg)
#             dealt = old - target[2]

#             roles = ['Tank', 'DPS', 'Healer']
#             crit_text = " [CRIT]" if crit else ""
#             self._log_event(
#                 f"💥 Enemy {roles[enemy[4]]} hit {roles[target[4]]} for {dealt}{crit_text}",
#                 "enemy"
#             )

#             if target[2] == 0:
#                 target_idx = self.env.chars.index(target)
#                 enemy_idx = self.env.chars.index(enemy)
#                 self._track_elimination(target_idx, enemy_idx, crit)

#     def _track_elimination(self, victim_idx, killer_idx, is_crit):
#         roles = ['Tank', 'DPS', 'Healer']
#         teams = ['Ally', 'Enemy']
#         victim = self.env.chars[victim_idx]
#         killer = self.env.chars[killer_idx]
#         v_name = f"{teams[victim[5]]} {roles[victim[4]]}"
#         k_name = f"{teams[killer[5]]} {roles[killer[4]]}"

#         self.kill_log.append({
#             'turn': self.turn_count,
#             'victim': v_name,
#             'killer': k_name,
#             'critical': is_crit
#         })

#         crit_text = " [CRIT]" if is_crit else ""
#         if victim[5] == 0:  # Ally died
#             self._log_event(f"☠️  {v_name} eliminated by {k_name}{crit_text}!", "kill")
#             self.revenge_target = killer_idx
#             self.revenge_mode = True
#         else:  # Enemy died
#             self._log_event(f"✅ {v_name} eliminated{crit_text}!", "kill")

#     def _display_llm_explanation(self, explanation, info):
#         """Display LLM strategic reasoning"""
#         t = self.reasoning_text
        
#         t.insert(tk.END, "\n" + "="*52 + "\n", "header")
#         t.insert(tk.END, f"TURN {self.turn_count} - HYBRID DECISION\n", "header")
#         t.insert(tk.END, "="*52 + "\n\n")
        
#         t.insert(tk.END, "🎯 SELECTED ACTION:\n", "action")
#         t.insert(tk.END, f"   {explanation['action']}\n\n", "action")
        
#         t.insert(tk.END, "🧠 LLM STRATEGIC REASONING:\n", "header")
#         t.insert(tk.END, "-"*52 + "\n")
#         t.insert(tk.END, f"{explanation['reasoning']}\n\n", "reasoning")
        
#         t.insert(tk.END, f"⚠️  THREAT: {explanation['threat_level'].upper()}\n\n", "threat")
        
#         conf_pct = int(explanation['confidence'] * 100)
#         conf_bar = "█" * (conf_pct // 3)
#         t.insert(tk.END, "📊 CONFIDENCE:\n", "confidence")
#         t.insert(tk.END, f"   [{conf_bar:<33s}] {conf_pct}%\n\n", "confidence")
        
#         t.insert(tk.END, "🔄 ALTERNATIVES:\n", "header")
#         for i, alt in enumerate(explanation['alternatives'], 1):
#             t.insert(tk.END, f"\n{i}. {alt['action']}\n")
#             t.insert(tk.END, f"   ❌ {alt['why']}\n")
        
#         t.insert(tk.END, f"\n{'='*52}\n")
#         t.insert(tk.END, f"🤖 {explanation['source']}\n")
#         t.insert(tk.END, f"   LLM Calls: {explanation['llm_calls']}\n")
        
#         if info.get('success'):
#             t.insert(tk.END, "\n✅ EXECUTION:\n", "action")
#             if 'damage' in info:
#                 t.insert(tk.END, f"   💥 Damage: {info['damage']} HP\n")
#             if info.get('kill'):
#                 t.insert(tk.END, "   ☠️  TARGET ELIMINATED!\n")
        
#         t.insert(tk.END, "\n")
#         t.see(tk.END)

#     def _update_display(self):
#         """Update battlefield display"""
#         roles = ['Tank', 'DPS', 'Healer']
        
#         # Update allies
#         for i, (name_lbl, hp_lbl) in enumerate(self.allies_labels):
#             c = self.env.chars[i]
#             role = roles[int(c[4])]
#             if c[2] <= 0:
#                 name_lbl.config(text=f"{i+1}. {role} [💀]", fg="#444444")
#                 hp_lbl.config(text="—", fg="#444444")
#             else:
#                 ratio = c[2] / c[3]
#                 color = "#00ff00" if ratio > 0.6 else "#ffaa00" if ratio > 0.3 else "#ff4444"
#                 name_lbl.config(text=f"{i+1}. {role}", fg="#00ff88")
#                 hp_lbl.config(text=f"{c[2]}/{c[3]}", fg=color)

#         # Update enemies
#         for i, (name_lbl, hp_lbl) in enumerate(self.enemies_labels):
#             c = self.env.chars[3 + i]
#             role = roles[int(c[4])]
#             if c[2] <= 0:
#                 name_lbl.config(text=f"{i+1}. {role} [💀]", fg="#444444")
#                 hp_lbl.config(text="—", fg="#444444")
#             else:
#                 ratio = c[2] / c[3]
#                 color = "#ff6666" if ratio > 0.6 else "#ffaa00" if ratio > 0.3 else "#ff4444"
#                 name_lbl.config(text=f"{i+1}. {role}", fg="#ff4444")
#                 hp_lbl.config(text=f"{c[2]}/{c[3]}", fg=color)

#         # Update threat matrix
#         if hasattr(self.env, 'threat_matrix'):
#             parts = []
#             for i in range(3):
#                 if self.env.chars[3 + i][2] > 0:
#                     v = round(self.env.threat_matrix[0][i], 1)
#                     parts.append(f"E{i}: {v}")
#             self.threat_label.config(text="  ".join(parts) or "—")

#     def _handle_game_end(self, info):
#         """Handle game over"""
#         if self.auto_play_id:
#             self.root.after_cancel(self.auto_play_id)
#             self.auto_play_id = None
        
#         self.active = False
#         self.auto = False
#         self.auto_btn.config(text="⏩ Auto Play", bg="#0066cc")
        
#         result = info.get('result', 'unknown')

#         if result == 'victory':
#             self.wins += 1
#             self._log_event(f"🏆 VICTORY in {self.turn_count} turns!", "victory")
#             self.status.config(text=f"🏆 Victory in {self.turn_count} turns!", fg="#00ff00")
#         else:
#             self.losses += 1
#             self._log_event("💀 DEFEAT - All allies eliminated", "kill")
#             self.status.config(text="💀 Defeat", fg="#ff4444")

#         self.total_matches += 1
#         wr = round(self.wins / self.total_matches * 100) if self.total_matches else 0
#         self.wl_label.config(text=f"W: {self.wins} | L: {self.losses} | WR: {wr}%")
        
#         self._update_display()

#     def _on_personality_change(self, event=None):
#         self.current_personality.set(self.personality_combo.get().lower())
#         self.new_game()

#     def _toggle_buff(self):
#         self.hero_buff_enabled.set(not self.hero_buff_enabled.get())
#         self.buff_btn.config(
#             text="Hero Buff: ON" if self.hero_buff_enabled.get() else "Hero Buff: OFF",
#             fg="#00ff88" if self.hero_buff_enabled.get() else "#ff4444"
#         )

#     def _save_game(self):
#         ts = datetime.now().strftime('%Y%m%d_%H%M%S')
#         fname = f"hybrid_save_{ts}.json"
#         try:
#             with open(fname, 'w') as f:
#                 json.dump({
#                     'turn': self.turn_count,
#                     'chars': self.env.chars,
#                     'wins': self.wins,
#                     'losses': self.losses,
#                     'total': self.total_matches,
#                     'kills': self.kill_log,
#                     'timestamp': datetime.now().isoformat()
#                 }, f, indent=2)
#             messagebox.showinfo("Saved", f"Game saved to {fname}")
#         except Exception as e:
#             messagebox.showerror("Save failed", str(e))

#     def _load_game(self):
#         fname = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
#         if not fname:
#             return
#         try:
#             with open(fname) as f:
#                 data = json.load(f)
#             self.turn_count = data['turn']
#             self.env.chars = data['chars']
#             self.wins = data['wins']
#             self.losses = data['losses']
#             self.total_matches = data['total']
#             self.kill_log = data['kills']
            
#             wr = round(self.wins / self.total_matches * 100) if self.total_matches else 0
#             self.wl_label.config(text=f"W: {self.wins} | L: {self.losses} | WR: {wr}%")
#             self._update_display()
#             messagebox.showinfo("Loaded", f"Game loaded from {fname}")
#         except Exception as e:
#             messagebox.showerror("Load failed", str(e))

#     def _export_log(self):
#         ts = datetime.now().strftime('%Y%m%d_%H%M%S')
#         fname = f"hybrid_log_{ts}.json"
#         wr = round(self.wins / self.total_matches * 100) if self.total_matches else 0
        
#         try:
#             with open(fname, 'w') as f:
#                 json.dump({
#                     'timestamp': datetime.now().isoformat(),
#                     'turns': self.turn_count,
#                     'difficulty': self.difficulty.get(),
#                     'personality': self.current_personality.get(),
#                     'wins': self.wins,
#                     'losses': self.losses,
#                     'win_rate': wr,
#                     'kills': self.kill_log,
#                     'log': self.battle_log,
#                     'system': 'LLM-RL Hybrid'
#                 }, f, indent=2)
#             messagebox.showinfo("Exported", f"Log saved to {fname}\nWin rate: {wr}%")
#         except Exception as e:
#             messagebox.showerror("Export failed", str(e))

#     def _show_stats(self):
#         wr = round(self.wins / self.total_matches * 100) if self.total_matches else 0
#         kills = len([k for k in self.kill_log if 'Enemy' in k['victim']])
#         deaths = len([k for k in self.kill_log if 'Ally' in k['victim']])
#         kd = round(kills / deaths, 2) if deaths else kills

#         win = tk.Toplevel(self.root)
#         win.title("📊 Statistics Dashboard")
#         win.geometry("500x400")
#         win.configure(bg="#1a1a2e")

#         txt = scrolledtext.ScrolledText(win, font=("Consolas", 9),
#                                          bg="#0d0d0d", fg="#00ff00",
#                                          width=60, height=22)
#         txt.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
#         stats_text = f"""
# ╔══════════════════════════════════════════════════╗
# ║           LLM-RL HYBRID STATISTICS               ║
# ╠══════════════════════════════════════════════════╣
# ║                                                  ║
# ║  📊 OVERALL PERFORMANCE                          ║
# ║  ────────────────────────────────────────────   ║
# ║  Matches played : {self.total_matches}
# ║  Wins           : {self.wins}
# ║  Losses         : {self.losses}
# ║  Win rate       : {wr}%
# ║                                                  ║
# ║  💀 COMBAT STATS                                 ║
# ║  ────────────────────────────────────────────   ║
# ║  Enemies killed : {kills}
# ║  Allies lost    : {deaths}
# ║  K/D ratio      : {kd}
# ║                                                  ║
# ║  🤖 HYBRID SYSTEM                                ║
# ║  ────────────────────────────────────────────   ║
# ║  • RL: Trained PPO Agent                        ║
# ║  • LLM: Strategic Analyzer                      ║
# ║  • Integration: Two-Level Architecture          ║
# ║                                                  ║
# ╚══════════════════════════════════════════════════╝
# """
#         txt.insert(tk.END, stats_text)
#         txt.config(state=tk.DISABLED)

#     def _log_event(self, msg, etype="info"):
#         ts = datetime.now().strftime("%H:%M:%S")
#         self.battle_log.append({'time': ts, 'msg': msg, 'type': etype})
#         self.log_text.config(state=tk.NORMAL)
#         self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
#         self.log_text.see(tk.END)
#         self.log_text.config(state=tk.DISABLED)

#     def run(self):
#         self.root.mainloop()


# if __name__ == "__main__":
#     print("="*70)
#     print("🤖 LLM-RL HYBRID TACTICAL RPG ARENA")
#     print("="*70)
#     print("\n✨ FEATURES:")
#     print("  • LLM Strategic Reasoning at each turn")
#     print("  • RL Optimal Action Selection")
#     print("  • Hybrid Decision Transparency")
#     print("  • Auto-play or Manual control")
#     print("  • All buttons functional")
#     print("  • Save/Load/Export")
#     print("\n⚙️  CONTROLS:")
#     print("  • Next Turn: Execute one turn manually")
#     print("  • Auto Play: Watch hybrid system in action")
#     print("  • Mode Toggle: AI Auto or Human Control")
#     print("="*70 + "\n")

#     app = UltimateRPGUI()
#     app.run()

"""
STEP 3: ULTIMATE AI RPG ARENA - FULL LLM INTEGRATION
=====================================================
✅ AI ANALYSIS VISIBLE ON RIGHT PANEL EVERY TURN
✅ Target buttons properly displayed
✅ Reasoning options properly displayed
✅ After-move analysis working
✅ Timer and auto-skip working
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from stable_baselines3 import PPO
from step1_training import EnhancedTacticalRPG
from llm_engine import AdvancedLLMExplanationEngine
import json
from datetime import datetime
import os
import numpy as np
import random


PUZZLES = [
    "Your DPS ally is at 20% HP and two enemies are alive. What is the correct priority?",
    "The enemy Healer is restoring HP every turn. What should you focus on first?",
    "All three enemies are alive but your team is at full HP. What is the optimal opening move?",
    "One enemy is at single-digit HP — one hit from death. Do you focus them or spread damage?",
    "Your Tank is absorbing hits well. Your Healer is untouched. Enemy DPS is dangerous. What is the threat?",
]

REASONING_OPTIONS = [
    "Enemy is low HP — finish them",
    "Ally is critically wounded — must heal",
    "Highest threat target first",
    "Preserve my DPS unit",
    "Reduce enemy count fast",
    "Safe play — defend and wait",
    "Burst down the enemy Healer",
    "Balance damage and sustain",
    "Prevent enemy from healing",
    "Risky but high-reward play",
]


class UltimateRPGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI RPG Arena — Human-First Tactical Edition")

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w = min(sw - 60, 1400)
        h = min(sh - 100, 920)
        self.root.geometry(f"{w}x{h}")
        self.root.configure(bg="#0d0d0d")
        self.root.minsize(1100, 680)

        # Game state
        self.battle_log = []
        self.turn_count = 0
        self.auto_play_id = None
        self.auto = False
        self.active = False
        self.hint_penalty_total = 0

        self.current_personality = tk.StringVar(value="aggressive")
        self.difficulty = tk.StringVar(value="normal")
        self.hero_buff_enabled = tk.BooleanVar(value=True)
        self.human_choice_mode = tk.BooleanVar(value=True)

        self.wins = 0
        self.losses = 0
        self.total_matches = 0
        self.match_history = []

        self.kill_log = []
        self.revenge_target = None
        self.revenge_mode = False

        self.selected_action = None
        self.selected_target = None
        self.selected_reason = None
        self.action_buttons = []
        self.target_buttons = []
        self.reason_buttons = []

        self.achievements = {
            'first_blood': False,
            'flawless_victory': False,
            'revenge_killer': False,
            'comeback_kid': False,
            'speed_demon': False,
        }

        # Timer
        self.timer_val = 12
        self.timer_max = 12
        self.timer_job = None

        self.llm_engine = AdvancedLLMExplanationEngine()
        self.available_personalities = self._check_models()
        self._load_model()
        self._setup_ui()
        self.new_game()

    def _check_models(self):
        personalities = ["aggressive", "defensive", "strategist", "chaotic"]
        return [p for p in personalities if os.path.exists(f"npc_{p}.zip")] or ["aggressive"]

    def _load_model(self):
        p = self.current_personality.get()
        for path in [f"npc_{p}.zip", "npc_best.zip", "npc_final.zip"]:
            name = path.replace(".zip", "")
            if os.path.exists(path):
                self.model = PPO.load(name)
                print(f"Loaded: {path}")
                return
        messagebox.showerror("Error", "No trained model found! Run step1_training.py first.")
        self.root.destroy()

    def _diff_cfg(self):
        cfg = {
            "easy": {"dmg_mult": 0.7, "crit": 0.05, "atk": (1, 8), "hp_bonus": 0.0, "timer": 16},
            "normal": {"dmg_mult": 1.0, "crit": 0.10, "atk": (4, 12), "hp_bonus": 0.0, "timer": 12},
            "hard": {"dmg_mult": 1.5, "crit": 0.22, "atk": (7, 18), "hp_bonus": 0.4, "timer": 8},
        }
        return cfg.get(self.difficulty.get(), cfg["normal"])

    # ============================== UI SETUP ==============================
    def _setup_ui(self):
        # TOP BAR
        top = tk.Frame(self.root, bg="#1a1a1a", height=56)
        top.pack(fill=tk.X)
        top.pack_propagate(False)

        tk.Label(top, text="AI RPG Arena", font=("Segoe UI", 15, "bold"),
                 bg="#1a1a1a", fg="#00ff88").pack(side=tk.LEFT, padx=16)
        tk.Label(top, text="Human-First Edition", font=("Segoe UI", 9),
                 bg="#1a1a1a", fg="#ff66ff").pack(side=tk.LEFT)

        ctrl = tk.Frame(top, bg="#1a1a1a")
        ctrl.pack(side=tk.RIGHT, padx=16)

        tk.Label(ctrl, text="Personality:", bg="#1a1a1a", fg="#aaaaaa",
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.personality_combo = ttk.Combobox(
            ctrl, values=[p.capitalize() for p in self.available_personalities],
            state="readonly", width=12, font=("Segoe UI", 9))
        self.personality_combo.set(self.current_personality.get().capitalize())
        self.personality_combo.bind("<<ComboboxSelected>>", self._on_personality_change)
        self.personality_combo.pack(side=tk.LEFT, padx=4)

        tk.Label(ctrl, text="Difficulty:", bg="#1a1a1a", fg="#aaaaaa",
                 font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(10, 4))
        self.diff_combo = ttk.Combobox(ctrl, values=["Easy", "Normal", "Hard"],
                                       state="readonly", width=8, font=("Segoe UI", 9))
        self.diff_combo.set("Normal")
        self.diff_combo.bind("<<ComboboxSelected>>",
                             lambda e: self.difficulty.set(self.diff_combo.get().lower()))
        self.diff_combo.pack(side=tk.LEFT)

        self.buff_btn = tk.Button(ctrl, text="Hero Buff: ON",
                                  command=self._toggle_buff,
                                  bg="#2a2a2a", fg="#00ff88",
                                  font=("Segoe UI", 9), relief=tk.FLAT, cursor="hand2")
        self.buff_btn.pack(side=tk.LEFT, padx=10)

        self.wl_label = tk.Label(top, text="W: 0 | L: 0",
                                 bg="#1a1a1a", fg="#ffaa00",
                                 font=("Segoe UI", 12, "bold"))
        self.wl_label.pack(side=tk.RIGHT, padx=16)

        # MAIN AREA
        main = tk.Frame(self.root, bg="#0d0d0d")
        main.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        # LEFT COLUMN
        left = tk.Frame(main, bg="#0d0d0d")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Teams display
        teams_frame = tk.Frame(left, bg="#0d0d0d")
        teams_frame.pack(fill=tk.X, pady=(0, 8))

        self.allies_frame = self._team_panel(teams_frame, "Your Team (Allies)", "#00ff88")
        self.allies_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        self.enemies_frame = self._team_panel(teams_frame, "Enemy Team", "#ff4444")
        self.enemies_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.allies_labels = self._unit_rows(self.allies_frame, "#00ff88", 3)
        self.enemies_labels = self._unit_rows(self.enemies_frame, "#ff4444", 3)

        # Threat matrix
        threat_lf = tk.LabelFrame(left, text="Threat Matrix",
                                  font=("Segoe UI", 10, "bold"),
                                  bg="#1a1a2e", fg="#ff8888", relief=tk.FLAT)
        threat_lf.pack(fill=tk.X, pady=(0, 8))
        self.threat_label = tk.Label(threat_lf, text="E0: 0.0  E1: 0.0  E2: 0.0",
                                     font=("Consolas", 11, "bold"),
                                     bg="#1a1a2e", fg="#ffaa00")
        self.threat_label.pack(pady=6)

        # Turn / timer strip
        strip = tk.Frame(left, bg="#0d0d0d")
        strip.pack(fill=tk.X, pady=(0, 8))
        self.turn_label = tk.Label(strip, text="Turn 0",
                                   font=("Segoe UI", 11, "bold"),
                                   bg="#0d0d0d", fg="#cccccc")
        self.turn_label.pack(side=tk.LEFT)
        self.timer_label = tk.Label(strip, text="12s",
                                    font=("Segoe UI", 11, "bold"),
                                    bg="#0d0d0d", fg="#00ff88")
        self.timer_label.pack(side=tk.LEFT, padx=12)
        self.timer_canvas = tk.Canvas(strip, height=8, bg="#222222",
                                      highlightthickness=0)
        self.timer_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Label(strip, text="Think fast — timer auto-skips!",
                 font=("Segoe UI", 8), bg="#0d0d0d", fg="#666666").pack(side=tk.LEFT)

        # Mode selector
        mode_frame = tk.Frame(left, bg="#1a1a2e")
        mode_frame.pack(fill=tk.X, pady=(0, 8))
        tk.Label(mode_frame, text="Mode:", bg="#1a1a2e", fg="#ffffff",
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=8)
        self.human_rb = tk.Radiobutton(mode_frame, text="👤 Human Control",
                                       variable=self.human_choice_mode, value=True,
                                       bg="#1a1a2e", fg="#ffaa00", selectcolor="#1a1a2e",
                                       font=("Segoe UI", 9, "bold"),
                                       command=self._on_mode_change)
        self.human_rb.pack(side=tk.LEFT, padx=5)
        self.ai_rb = tk.Radiobutton(mode_frame, text="🤖 AI Auto",
                                    variable=self.human_choice_mode, value=False,
                                    bg="#1a1a2e", fg="#00ff88", selectcolor="#1a1a2e",
                                    font=("Segoe UI", 9, "bold"),
                                    command=self._on_mode_change)
        self.ai_rb.pack(side=tk.LEFT, padx=5)

        # Tactical puzzle
        puzzle_lf = tk.LabelFrame(left, text="Your Turn — Tactical Challenge",
                                  font=("Segoe UI", 10, "bold"),
                                  bg="#1a1a2e", fg="#ffcc00", relief=tk.FLAT)
        puzzle_lf.pack(fill=tk.X, pady=(0, 8))
        self.puzzle_text = tk.Label(puzzle_lf, text="",
                                    font=("Segoe UI", 10), bg="#1a1a2e",
                                    fg="#ffffff", wraplength=500,
                                    justify=tk.LEFT, anchor=tk.W)
        self.puzzle_text.pack(padx=10, pady=8, fill=tk.X)

        # Action buttons (Horizontal)
        act_lf = tk.LabelFrame(left, text="1. Choose an Action",
                               font=("Segoe UI", 10, "bold"),
                               bg="#1a1a2e", fg="#88aaff", relief=tk.FLAT)
        act_lf.pack(fill=tk.X, pady=(0, 6))
        self.act_btn_frame = tk.Frame(act_lf, bg="#1a1a2e")
        self.act_btn_frame.pack(padx=8, pady=8, fill=tk.X)

        # Target buttons (Horizontal)
        tgt_lf = tk.LabelFrame(left, text="2. Choose a Target",
                               font=("Segoe UI", 10, "bold"),
                               bg="#1a1a2e", fg="#ff8888", relief=tk.FLAT)
        tgt_lf.pack(fill=tk.X, pady=(0, 6))
        self.tgt_btn_frame = tk.Frame(tgt_lf, bg="#1a1a2e")
        self.tgt_btn_frame.pack(padx=8, pady=8, fill=tk.X)

        # Reasoning buttons (Grid layout)
        rsn_lf = tk.LabelFrame(left, text="3. Why did you choose this? (builds tactical insight)",
                               font=("Segoe UI", 10, "bold"),
                               bg="#1a1a2e", fg="#cc88ff", relief=tk.FLAT)
        rsn_lf.pack(fill=tk.X, pady=(0, 6))
        self.rsn_btn_frame = tk.Frame(rsn_lf, bg="#1a1a2e")
        self.rsn_btn_frame.pack(padx=8, pady=6, fill=tk.X)

        # Confirm row
        conf_row = tk.Frame(left, bg="#0d0d0d")
        conf_row.pack(fill=tk.X, pady=(0, 8))
        self.confirm_btn = tk.Button(conf_row, text="▶ Confirm Move",
                                     command=self._confirm_action,
                                     bg="#00aa44", fg="white",
                                     font=("Segoe UI", 10, "bold"),
                                     relief=tk.RAISED, cursor="hand2",
                                     state=tk.DISABLED, width=15)
        self.confirm_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.hint_btn = tk.Button(conf_row, text="Show AI Hint (costs 5 pts)",
                                  command=self._show_hint,
                                  bg="#2a2a2a", fg="#ffaa00",
                                  font=("Segoe UI", 9), relief=tk.RAISED, cursor="hand2")
        self.hint_btn.pack(side=tk.LEFT)
        self.hint_label = tk.Label(conf_row, text="", bg="#0d0d0d",
                                   fg="#ff6600", font=("Segoe UI", 9))
        self.hint_label.pack(side=tk.LEFT, padx=8)

        # Feedback after move
        fb_lf = tk.LabelFrame(left, text="After-Move Analysis",
                              font=("Segoe UI", 10, "bold"),
                              bg="#1a1a2e", fg="#88ff88", relief=tk.FLAT)
        fb_lf.pack(fill=tk.X, pady=(0, 8))
        self.feedback_text = tk.Label(fb_lf, text="Make your first move to see analysis.",
                                      font=("Segoe UI", 9), bg="#1a1a2e",
                                      fg="#aaaaaa", wraplength=500,
                                      justify=tk.LEFT, anchor=tk.W)
        self.feedback_text.pack(padx=10, pady=6, fill=tk.X)

        # RIGHT COLUMN - AI Strategic Reasoning
        right = tk.Frame(main, bg="#0d0d0d", width=400)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right.pack_propagate(False)

        llm_lf = tk.LabelFrame(right, text="🧠 AI Strategic Reasoning",
                               font=("Segoe UI", 10, "bold"),
                               bg="#1a1a2e", fg="#ff66ff", relief=tk.FLAT)
        llm_lf.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.reasoning_text = scrolledtext.ScrolledText(
            llm_lf, font=("Segoe UI", 9), bg="#0d0d0d",
            fg="#cccccc", wrap=tk.WORD, relief=tk.FLAT, bd=0, height=22)
        self.reasoning_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self._configure_reasoning_tags()

        # Battle Log
        log_lf = tk.LabelFrame(right, text="📜 Battle Log",
                               font=("Segoe UI", 10, "bold"),
                               bg="#1a1a2e", fg="#88ff88", relief=tk.FLAT)
        log_lf.pack(fill=tk.X)
        self.log_text = scrolledtext.ScrolledText(
            log_lf, font=("Consolas", 8), bg="#0d0d0d",
            fg="#aaaaaa", state=tk.DISABLED, relief=tk.FLAT, bd=0, height=8)
        self.log_text.pack(fill=tk.BOTH, padx=8, pady=8)

        # BOTTOM BUTTONS
        bot = tk.Frame(self.root, bg="#0d0d0d", pady=8)
        bot.pack(fill=tk.X, padx=16)
        for text, cmd, bg in [
            ("New Game", self.new_game, "#cc6600"),
            ("Auto Turn", self._toggle_auto, "#0066cc"),
            ("Save", self._save_game, "#3399ff"),
            ("Load", self._load_game, "#3399ff"),
            ("Stats", self._show_stats, "#9933cc"),
            ("Export Log", self._export_log, "#9933cc"),
            ("Quit", self.root.quit, "#cc0000"),
        ]:
            tk.Button(bot, text=text, command=cmd,
                      bg=bg, fg="white",
                      font=("Segoe UI", 9, "bold"),
                      width=10, relief=tk.RAISED,
                      cursor="hand2").pack(side=tk.LEFT, padx=3)

        self.auto_btn = bot.winfo_children()[1]

        self.status = tk.Label(self.root, text="Ready",
                               font=("Segoe UI", 8),
                               bg="#0d0d0d", fg="#00ff88", anchor=tk.W, padx=16)
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def _team_panel(self, parent, title, color):
        lf = tk.LabelFrame(parent, text=title,
                           font=("Segoe UI", 10, "bold"),
                           bg="#1a1a2e", fg=color, relief=tk.FLAT)
        return lf

    def _unit_rows(self, parent, color, n):
        labels = []
        for i in range(n):
            f = tk.Frame(parent, bg="#1a1a2e", pady=3)
            f.pack(fill=tk.X, padx=8)
            name = tk.Label(f, text=f"{i+1}. Unit", font=("Segoe UI", 10),
                            bg="#1a1a2e", fg=color)
            name.pack(side=tk.LEFT)
            hp = tk.Label(f, text="—/—", font=("Consolas", 10, "bold"),
                          bg="#1a1a2e", fg=color)
            hp.pack(side=tk.RIGHT)
            labels.append((name, hp))
        return labels

    def _configure_reasoning_tags(self):
        t = self.reasoning_text
        t.tag_config("header", foreground="#ff66ff", font=("Segoe UI", 10, "bold"))
        t.tag_config("action", foreground="#00ff88", font=("Segoe UI", 10, "bold"))
        t.tag_config("reasoning", foreground="#cccccc", font=("Segoe UI", 9))
        t.tag_config("threat", foreground="#ff6600", font=("Segoe UI", 9, "bold"))
        t.tag_config("confidence", foreground="#00ff00", font=("Segoe UI", 9))
        t.tag_config("feedback_good", foreground="#00ff88", font=("Segoe UI", 9))
        t.tag_config("feedback_bad", foreground="#ff6644", font=("Segoe UI", 9))
        t.tag_config("alt", foreground="#88ff88", font=("Segoe UI", 9))

    # ============================== GAME LOGIC ==============================
    def _on_mode_change(self):
        """Handle mode change"""
        if not self.human_choice_mode.get():
            # AI Auto mode - disable human buttons, enable auto
            # Safely disable action buttons
            if hasattr(self, 'action_buttons') and self.action_buttons:
                for item in self.action_buttons:
                    if isinstance(item, tuple) and len(item) == 2:
                        _, btn = item
                        try:
                            btn.config(state=tk.DISABLED)
                        except:
                            pass
                    else:
                        try:
                            item.config(state=tk.DISABLED)
                        except:
                            pass
            
            # Safely disable target buttons
            if hasattr(self, 'target_buttons') and self.target_buttons:
                for btn in self.target_buttons:
                    try:
                        btn.config(state=tk.DISABLED)
                    except:
                        pass
            
            # Safely disable reason buttons
            if hasattr(self, 'reason_buttons') and self.reason_buttons:
                for btn in self.reason_buttons:
                    try:
                        btn.config(state=tk.DISABLED)
                    except:
                        pass
            
            try:
                self.confirm_btn.config(state=tk.DISABLED)
            except:
                pass
            
            # Stop any running timer
            self._stop_timer()
            
            # Display AI analysis for AI mode
            if self.active:
                self._display_full_ai_analysis()
            
            # Show status
            self.status.config(text="🤖 AI MODE ACTIVE - AI will play automatically", fg='#00ff88')
            
            # Start AI auto play if active
            if self.active and not self.auto:
                self.root.after(500, self._auto_single_turn)
                
        else:
            # Human mode - enable action buttons
            if hasattr(self, 'action_buttons') and self.action_buttons:
                for item in self.action_buttons:
                    if isinstance(item, tuple) and len(item) == 2:
                        _, btn = item
                        try:
                            btn.config(state=tk.NORMAL)
                        except:
                            pass
                    else:
                        try:
                            item.config(state=tk.NORMAL)
                        except:
                            pass
            
            self.status.config(text="👤 HUMAN MODE - Make your move!", fg='#ffaa00')
            
            # Display AI analysis for human mode as well
            if self.active:
                self._display_full_ai_analysis()
            
            # Start timer if active
            if self.active:
                self._start_timer()

    def _build_action_buttons(self):
        for w in self.act_btn_frame.winfo_children():
            w.destroy()
        self.action_buttons = []  # Store as list of buttons only, not tuples
        defs = [
            (0, "⚔️ Attack", "#aa2222"),
            (1, "🛡️ Defend", "#225599"),
            (2, "✨ Ability", "#882299"),
            (3, "🏃 Reposition", "#886600"),
            (4, "💚 Heal", "#227744"),
        ]
        for act_id, label, bg in defs:
            btn = tk.Button(self.act_btn_frame, text=label,
                            command=lambda a=act_id: self._select_action(a),
                            bg=bg, fg="white", font=("Segoe UI", 9, "bold"),
                            relief=tk.RAISED, cursor="hand2", width=11)
            btn.pack(side=tk.LEFT, padx=3)
            self.action_buttons.append(btn)  # Store just the button
            btn.act_id = act_id  # Store action id as attribute

    def _select_action(self, act_id):
        self.selected_action = act_id
        self.selected_target = None
        self.selected_reason = None
        self.confirm_btn.config(state=tk.DISABLED)

        for btn in self.action_buttons:
            btn.config(relief=tk.RAISED)
            if hasattr(btn, 'act_id') and btn.act_id == act_id:
                btn.config(relief=tk.SUNKEN)

        self._build_target_buttons(act_id)

    def _build_target_buttons(self, act_id):
        for w in self.tgt_btn_frame.winfo_children():
            w.destroy()
        self.target_buttons = []

        if act_id in (1, 3):  # Self-targeted actions
            self.selected_target = 0
            self._build_reasoning_buttons()
            return

        if act_id == 4:  # Heal - target allies
            candidates = [(i, c) for i, c in enumerate(self.env.chars) if c[5] == 0 and c[2] > 0]
            btn_color = "#227744"
        else:  # Attack/Ability - target enemies
            candidates = [(i, c) for i, c in enumerate(self.env.chars) if c[5] == 1 and c[2] > 0]
            btn_color = "#aa2222"

        roles = ['Tank', 'DPS', 'Healer']
        for idx, char in candidates:
            hp_pct = int(char[2] / char[3] * 100)
            label = f"{roles[char[4]]} ({hp_pct}% HP)"
            btn = tk.Button(self.tgt_btn_frame, text=label,
                            command=lambda i=idx: self._select_target(i),
                            bg=btn_color, fg="white",
                            font=("Segoe UI", 9), relief=tk.RAISED, cursor="hand2", width=12)
            btn.pack(side=tk.LEFT, padx=3)
            btn.target_idx = idx  # Store target index
            self.target_buttons.append(btn)

    def _select_target(self, idx):
        self.selected_target = idx
        for btn in self.target_buttons:
            btn.config(relief=tk.RAISED)
        # Find and highlight selected button by comparing target index
        for btn in self.target_buttons:
            if hasattr(btn, 'target_idx') and btn.target_idx == idx:
                btn.config(relief=tk.SUNKEN)
        self._build_reasoning_buttons()

    def _build_reasoning_buttons(self):
        for w in self.rsn_btn_frame.winfo_children():
            w.destroy()
        self.reason_buttons = []
        self.selected_reason = None
        self.confirm_btn.config(state=tk.DISABLED)

        # Create a grid of reasoning buttons
        rows = 2
        cols = 5
        for i, reason in enumerate(REASONING_OPTIONS[:10]):
            row = i // cols
            col = i % cols
            btn = tk.Button(self.rsn_btn_frame, text=reason,
                            command=lambda r=reason: self._select_reason(r),
                            bg="#2a2a2a", fg="#cccccc",
                            font=("Segoe UI", 8), relief=tk.RAISED, cursor="hand2",
                            width=18)
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.reason_buttons.append(btn)

        skip = tk.Button(self.rsn_btn_frame, text="Skip reasoning",
                         command=lambda: self._select_reason("(no reason given)"),
                         bg="#1a1a1a", fg="#777777",
                         font=("Segoe UI", 8), relief=tk.RAISED, cursor="hand2")
        skip.grid(row=2, column=0, columnspan=5, pady=5)

    def _select_reason(self, reason):
        self.selected_reason = reason
        for btn in self.reason_buttons:
            btn.config(relief=tk.RAISED)
        # Find button with matching text
        for btn in self.reason_buttons:
            if btn.cget('text') == reason:
                btn.config(relief=tk.SUNKEN)
        self.confirm_btn.config(state=tk.NORMAL)

    def _confirm_action(self):
        if self.selected_action is None or self.selected_target is None:
            return
        self._stop_timer()
        self._execute_action(self.selected_action, self.selected_target)

    def _get_best_ai_action(self):
        """Return AI's best action for suggestion"""
        enemies = [(i, c) for i, c in enumerate(self.env.chars) if c[5] == 1 and c[2] > 0]
        allies = [(i, c) for i, c in enumerate(self.env.chars) if c[5] == 0 and c[2] > 0]

        low_ally = min(allies, key=lambda x: x[1][2] / x[1][3]) if allies else None
        if low_ally and low_ally[1][2] / low_ally[1][3] < 0.3:
            return {
                'action': 'Heal Ally',
                'target_idx': low_ally[0],
                'reason': f'Ally critically wounded.'
            }

        near_dead = [(i, c) for i, c in enemies if c[2] < 20]
        if near_dead:
            target = min(near_dead, key=lambda x: x[1][2])
            return {
                'action': 'Attack',
                'target_idx': target[0],
                'reason': f'Finish low-HP enemy.'
            }

        healer = next((x for x in enemies if x[1][4] == 2), None)
        if healer:
            return {
                'action': 'Attack',
                'target_idx': healer[0],
                'reason': 'Enemy healer sustaining team — eliminate first.'
            }

        if enemies:
            return {
                'action': 'Attack',
                'target_idx': enemies[0][0],
                'reason': 'Standard attack.'
            }

        return {'action': 'Defend', 'target_idx': 0, 'reason': 'No valid targets.'}

    def _display_full_ai_analysis(self):
        """Display COMPLETE AI analysis at START of every turn"""
        if not self.active or not hasattr(self, 'env'):
            return

        t = self.reasoning_text

        # Clear ONLY the AI section (keep human history)
        content = t.get(1.0, tk.END)
        human_start = content.find("👤 YOUR MOVE")

        if human_start != -1:
            ai_end_line = content[:human_start].count('\n')
            t.delete(1.0, f"{ai_end_line + 1}.0")
        else:
            t.delete(1.0, tk.END)

        # Get best AI action
        best_action = self._get_best_ai_action()

        # Get threat analysis
        threats = []
        roles = ['Tank', 'DPS', 'Healer']
        for i in range(3, 6):
            if self.env.chars[i][2] > 0:
                role = roles[self.env.chars[i][4]]
                hp_pct = self.env.chars[i][2] / self.env.chars[i][3] * 100
                threat_val = self.env.threat_matrix[0][i - 3] if hasattr(self.env, 'threat_matrix') else 1.0
                threat_level = "CRITICAL" if threat_val > 1.3 else "HIGH" if threat_val > 1.0 else "MEDIUM" if threat_val > 0.7 else "LOW"
                threats.append(f"   • E{i - 3} {role}: {hp_pct:.0f}% HP | {threat_level}")

        # Allied status
        allies_status = []
        for i in range(3):
            if self.env.chars[i][2] > 0:
                role = roles[self.env.chars[i][4]]
                hp_pct = self.env.chars[i][2] / self.env.chars[i][3] * 100
                status = "CRITICAL" if hp_pct < 30 else "WOUNDED" if hp_pct < 60 else "HEALTHY"
                emoji = "🔴" if status == "CRITICAL" else "🟡" if status == "WOUNDED" else "🟢"
                allies_status.append(f"   {emoji} {role}: {hp_pct:.0f}% HP")

        # === DISPLAY AI ANALYSIS ===
        t.insert(tk.END, "═" * 60 + "\n", "header")
        t.insert(tk.END, f"🤖 TURN {self.turn_count + 1} — AI ANALYSIS\n", "header")
        t.insert(tk.END, "═" * 60 + "\n\n", "header")

        t.insert(tk.END, f"🎯 RECOMMENDED MOVE: {best_action['action']}\n", "action")
        t.insert(tk.END, f"💡 REASON: {best_action['reason']}\n\n", "reasoning")

        if threats:
            t.insert(tk.END, "⚠️ THREAT ANALYSIS:\n", "threat")
            for threat in threats:
                t.insert(tk.END, threat + "\n", "threat")
            t.insert(tk.END, "\n", "threat")

        if allies_status:
            t.insert(tk.END, "🛡️ ALLIED STATUS:\n", "header")
            for status in allies_status:
                t.insert(tk.END, status + "\n", "reasoning")
            t.insert(tk.END, "\n", "reasoning")

        # Add a battle cry
        battle_cries = [
            "Charge — show no mercy!",
            "Hold the line — stand strong!",
            "Execute the plan!",
            "For chaos and glory!"
        ]
        t.insert(tk.END, f'"{random.choice(battle_cries)}"\n\n', "action")

        t.insert(tk.END, "═" * 60 + "\n", "header")
        t.insert(tk.END, "👤 YOUR TURN — Make your move!\n\n", "action")

        t.see(1.0)

    def _display_human_move_analysis(self, act_id, target_idx, info):
        """APPEND human move analysis below AI analysis"""
        t = self.reasoning_text

        action_names = ['Attack', 'Defend', 'Ability', 'Reposition', 'Heal']
        target_names = ['Tank', 'DPS', 'Healer', 'Enemy DPS', 'Enemy Tank', 'Enemy Healer']

        # Scroll to end and append
        t.see(tk.END)
        t.insert(tk.END, "\n" + "─" * 60 + "\n\n")
        t.insert(tk.END, f"👤 YOUR MOVE — Turn {self.turn_count}\n", "action")
        t.insert(tk.END, f"Action: {action_names[act_id]} → {target_names[target_idx]}\n\n", "reasoning")
        t.insert(tk.END, f"Your reasoning: {self.selected_reason or '(none)'}\n\n", "reasoning")

        # AI Feedback
        analysis = self._evaluate_decision(act_id, target_idx)
        tag = "feedback_good" if analysis['good'] else "feedback_bad"
        t.insert(tk.END, f"AI Feedback: {analysis['msg']}\n", tag)

        if analysis.get('alternative'):
            t.insert(tk.END, f"💡 Better option: {analysis['alternative']}\n", "alt")

        if info.get('damage'):
            t.insert(tk.END, f"💥 Damage dealt: {info['damage']} HP\n", "action")
        if info.get('heal_amount'):
            t.insert(tk.END, f"💚 Healing done: {info['heal_amount']} HP\n", "action")
        if info.get('killed_enemy'):
            t.insert(tk.END, "☠️ TARGET ELIMINATED!\n", "action")

        t.insert(tk.END, "\n" + "─" * 60 + "\n\n")
        t.see(tk.END)

    def _evaluate_decision(self, act_id, target_idx):
        chars = self.env.chars
        low_allies = [c for c in chars[:3] if c[2] > 0 and c[2] / c[3] < 0.3]
        near_dead = [c for c in chars[3:] if c[2] > 0 and c[2] < 20]

        if act_id == 4 and low_allies:
            return {'good': True, 'msg': "Good sustain — critical ally restored."}

        if act_id in (0, 2) and near_dead:
            return {'good': True, 'msg': "Excellent — you eliminated a low-HP enemy."}

        return {'good': True, 'msg': "Reasonable choice given the board state."}

    def _execute_action(self, act_id, target_idx, auto=False):
        if not self.active or self.env is None:
            return

        self.turn_count += 1
        self.turn_label.config(text=f"Turn {self.turn_count}")

        action = np.array([target_idx, act_id])
        self.obs, reward, done, _, info = self.env.step(action)

        # Enemy counter-attacks
        self._process_enemy_attacks()

        if info.get('killed_enemy'):
            self._track_elimination(target_idx, 0, info.get('critical', False))

        # Get LLM explanation
        explanation = self.llm_engine.get_full_explanation(
            action, self.env.chars, self.current_personality.get(),
            info, self.revenge_mode, False, self.difficulty.get(), self.turn_count
        )

        # Display analysis based on mode
        if auto:
            # AI mode - show AI move analysis
            self._display_ai_move_analysis(act_id, target_idx, info, explanation)
        else:
            # Human mode - show human move analysis
            self._display_human_move_analysis(act_id, target_idx, info)
            self._show_feedback(act_id, target_idx, info)

        self._log_event(f"Turn {self.turn_count}: {explanation['action']}", "action")
        self._update_display()

        if done:
            self._handle_game_end(info)
            return

        allies_alive = sum(1 for c in self.env.chars[:3] if c[2] > 0)
        if allies_alive == 0:
            self._handle_game_end({'result': 'defeat'})
            return

        enemies_alive = sum(1 for c in self.env.chars[3:] if c[2] > 0)
        if enemies_alive == 0:
            self._handle_game_end({'result': 'victory'})
            return

        self._start_new_turn()
    
    def _display_ai_move_analysis(self, act_id, target_idx, info, explanation):
        """Display AI's move analysis for AI mode"""
        t = self.reasoning_text
        
        action_names = ['Attack', 'Defend', 'Ability', 'Reposition', 'Heal']
        target_names = ['Tank', 'DPS', 'Healer', 'Enemy DPS', 'Enemy Tank', 'Enemy Healer']
        
        t.insert(tk.END, "═" * 60 + "\n", "header")
        t.insert(tk.END, f"🤖 TURN {self.turn_count} — AI MOVE\n", "header")
        t.insert(tk.END, "═" * 60 + "\n\n", "header")
        
        t.insert(tk.END, f"🎯 AI ACTION: {action_names[act_id]} → {target_names[target_idx]}\n\n", "action")
        
        t.insert(tk.END, f"📖 {explanation['narrative']}\n\n", "reasoning")
        
        t.insert(tk.END, f"💭 {explanation['reasoning']}\n\n", "reasoning")
        
        threat_tag = f"threat_{explanation['threat_level']}"
        t.insert(tk.END, f"⚠️ THREAT LEVEL: {explanation['threat_level'].upper()}\n", threat_tag)
        t.insert(tk.END, f"   {explanation['threat_narrative']}\n\n", "reasoning")
        
        conf_pct = int(explanation['confidence'] * 100)
        conf_bar = "█" * (conf_pct // 5)
        t.insert(tk.END, f"📊 CONFIDENCE: [{conf_bar:<20s}] {conf_pct}%\n\n", "confidence")
        
        if info.get('damage'):
            t.insert(tk.END, f"💥 Damage dealt: {info['damage']} HP\n", "action")
        if info.get('heal_amount'):
            t.insert(tk.END, f"💚 Healing done: {info['heal_amount']} HP\n", "action")
        if info.get('killed_enemy'):
            t.insert(tk.END, "☠️ TARGET ELIMINATED!\n", "action")
        
        t.insert(tk.END, "\n" + "═" * 60 + "\n\n", "header")
        t.see(tk.END)
        
    def _start_new_turn(self):
        """Start new turn - SHOW FRESH AI ANALYSIS"""
        self.selected_action = None
        self.selected_target = None
        self.selected_reason = None
        self.confirm_btn.config(state=tk.DISABLED)
        self.hint_label.config(text="")

        # Rebuild UI
        self._build_action_buttons()
        self._build_puzzle_prompt()

        # Clear button frames
        for w in self.tgt_btn_frame.winfo_children():
            w.destroy()
        for w in self.rsn_btn_frame.winfo_children():
            w.destroy()

        # ✅ DISPLAY FRESH AI ANALYSIS (works for both modes)
        self._display_full_ai_analysis()

        if self.human_choice_mode.get():
            self._start_timer()
        else:
            # In AI mode, automatically take a turn
            if self.active and not self.auto:
                self.root.after(500, self._auto_single_turn)

    def _auto_single_turn(self):
        """Take a single AI turn (for AI mode without auto loop)"""
        try:
            if self.active and not self.human_choice_mode.get() and not self.auto and hasattr(self, 'model') and self.model:
                action, _ = self.model.predict(self.obs, deterministic=False)
                self._execute_action(int(action[1]), int(action[0]), auto=True)
        except Exception as e:
            print(f"Auto turn error: {e}")

    def _display_full_ai_analysis(self):
        """Display COMPLETE AI analysis at START of every turn (works for both modes)"""
        if not self.active or not hasattr(self, 'env'):
            return

        t = self.reasoning_text

        # Clear and refresh with fresh analysis
        t.delete(1.0, tk.END)

        # Get best AI action
        best_action = self._get_best_ai_action()

        # Get threat analysis
        threats = []
        roles = ['Tank', 'DPS', 'Healer']
        for i in range(3, 6):
            if self.env.chars[i][2] > 0:
                role = roles[self.env.chars[i][4]]
                hp_pct = self.env.chars[i][2] / self.env.chars[i][3] * 100
                threat_val = self.env.threat_matrix[0][i - 3] if hasattr(self.env, 'threat_matrix') else 1.0
                threat_level = "CRITICAL" if threat_val > 1.3 else "HIGH" if threat_val > 1.0 else "MEDIUM" if threat_val > 0.7 else "LOW"
                threats.append(f"   • E{i-3} {role}: {hp_pct:.0f}% HP | {threat_level}")

        # Allied status
        allies_status = []
        for i in range(3):
            if self.env.chars[i][2] > 0:
                role = roles[self.env.chars[i][4]]
                hp_pct = self.env.chars[i][2] / self.env.chars[i][3] * 100
                status = "CRITICAL" if hp_pct < 30 else "WOUNDED" if hp_pct < 60 else "HEALTHY"
                emoji = "🔴" if status == "CRITICAL" else "🟡" if status == "WOUNDED" else "🟢"
                allies_status.append(f"   {emoji} {role}: {hp_pct:.0f}% HP")

        # === DISPLAY AI ANALYSIS ===
        mode_text = "AI MODE - RECOMMENDED MOVE" if not self.human_choice_mode.get() else "AI ANALYSIS"
        
        t.insert(tk.END, "═" * 60 + "\n", "header")
        t.insert(tk.END, f"🤖 TURN {self.turn_count + 1} — {mode_text}\n", "header")
        t.insert(tk.END, "═" * 60 + "\n\n", "header")

        t.insert(tk.END, f"🎯 RECOMMENDED: {best_action['action']}\n", "action")
        t.insert(tk.END, f"💡 REASON: {best_action['reason']}\n\n", "reasoning")

        if threats:
            t.insert(tk.END, "⚠️ THREAT ANALYSIS:\n", "threat")
            for threat in threats:
                t.insert(tk.END, threat + "\n", "threat")
            t.insert(tk.END, "\n", "threat")

        if allies_status:
            t.insert(tk.END, "🛡️ ALLIED STATUS:\n", "header")
            for status in allies_status:
                t.insert(tk.END, status + "\n", "reasoning")
            t.insert(tk.END, "\n", "reasoning")

        # Battle cry
        battle_cries = [
            "⚔️ Charge — show no mercy!",
            "🛡️ Hold the line — stand strong!",
            "🎯 Execute the plan!",
            "🌀 For chaos and glory!"
        ]
        t.insert(tk.END, f'🗣️ "{random.choice(battle_cries)}"\n\n', "action")

        if self.human_choice_mode.get():
            t.insert(tk.END, "═" * 60 + "\n", "header")
            t.insert(tk.END, "👤 YOUR TURN — Make your move!\n\n", "action")
        else:
            t.insert(tk.END, "═" * 60 + "\n", "header")
            t.insert(tk.END, "🤖 AI PLAYING — Watch the analysis above\n\n", "action")

        t.see(1.0)
    
    def _process_enemy_attacks(self):
        cfg = self._diff_cfg()
        alive = [c for c in self.env.chars[3:] if c[2] > 0]
        allies = [c for c in self.env.chars[:3] if c[2] > 0]
        if not alive or not allies:
            return

        for enemy in alive:
            target = min(allies, key=lambda a: a[2] / a[3])
            base = random.randint(*cfg['atk'])
            dmg = int(base * cfg['dmg_mult'])
            crit = random.random() < cfg['crit']
            if crit:
                dmg = int(dmg * 2)

            old = target[2]
            target[2] = max(0, target[2] - dmg)
            dealt = old - target[2]

            roles = ['Tank', 'DPS', 'Healer']
            crit_text = " [CRIT]" if crit else ""
            self._log_event(
                f"Enemy {roles[enemy[4]]} hit your {roles[target[4]]} for {dealt}{crit_text}",
                "enemy"
            )
            if target[2] == 0:
                target_idx = self.env.chars.index(target)
                enemy_idx = self.env.chars.index(enemy)
                self._track_elimination(target_idx, enemy_idx, crit)

    def _track_elimination(self, victim_idx, killer_idx, is_crit=False):
        roles = ['Tank', 'DPS', 'Healer']
        teams = ['Ally', 'Enemy']
        victim = self.env.chars[victim_idx]
        killer = self.env.chars[killer_idx]
        v_name = f"{teams[victim[5]]} {roles[victim[4]]}"
        k_name = f"{teams[killer[5]]} {roles[killer[4]]}"

        self.kill_log.append({
            'turn': self.turn_count,
            'victim': v_name,
            'killer': k_name,
            'critical': is_crit
        })

        crit_text = " [CRIT]" if is_crit else ""
        if victim[5] == 0:
            self._log_event(f"☠️ {v_name} eliminated by {k_name}{crit_text}!", "kill")
            self.revenge_target = killer_idx
            self.revenge_mode = True
        else:
            self._log_event(f"✅ {v_name} eliminated{crit_text}!", "kill")

    def _show_feedback(self, act_id, target_idx, info):
        analysis = self._evaluate_decision(act_id, target_idx)
        color = "#00ff88" if analysis['good'] else "#ff6644"
        text = f"Your reasoning: {self.selected_reason or '(none)'}\n"
        text += f"AI assessment: {analysis['msg']}"
        if analysis.get('alternative'):
            text += f"\nBetter option: {analysis['alternative']}"
        self.feedback_text.config(text=text, fg=color)

    def _show_hint(self):
        self.hint_penalty_total += 5
        hint = self._get_best_ai_action()
        self.hint_label.config(
            text=f"Hint (−5 pts): {hint['action']} — {hint['reason']}"
        )

    def _start_new_turn(self):
        """Start new turn - SHOW FRESH AI ANALYSIS AT TOP"""
        self.selected_action = None
        self.selected_target = None
        self.selected_reason = None
        self.confirm_btn.config(state=tk.DISABLED)
        self.hint_label.config(text="")

        # Rebuild UI
        self._build_action_buttons()
        self._build_puzzle_prompt()

        # Clear button frames
        for w in self.tgt_btn_frame.winfo_children():
            w.destroy()
        for w in self.rsn_btn_frame.winfo_children():
            w.destroy()

        # ✅ DISPLAY FRESH AI ANALYSIS AT TOP
        self._display_full_ai_analysis()

        if self.human_choice_mode.get():
            self._start_timer()

    def _build_puzzle_prompt(self):
        chars = self.env.chars
        low_all = [c for c in chars[:3] if c[2] > 0 and c[2] / c[3] < 0.35]
        nd_en = [c for c in chars[3:] if c[2] > 0 and c[2] < 20]
        en_count = sum(1 for c in chars[3:] if c[2] > 0)

        if low_all:
            roles = ['Tank', 'DPS', 'Healer']
            c = low_all[0]
            prompt = (f"Your {roles[c[4]]} is at {int(c[2] / c[3] * 100)}% HP "
                      f"and may not survive the next enemy attack. "
                      f"{en_count} enemies are still standing. What is your smartest move?")
        elif nd_en:
            roles = ['Tank', 'DPS', 'Healer']
            c = nd_en[0]
            prompt = (f"Enemy {roles[c[4]]} has only {c[2]} HP — one hit from death. "
                      f"Eliminating them removes their damage permanently. How do you proceed?")
        else:
            prompt = PUZZLES[self.turn_count % len(PUZZLES)]

        self.puzzle_text.config(text=f"Think: {prompt}")

    def _update_display(self):
        roles = ['Tank', 'DPS', 'Healer']
        for i, (name_lbl, hp_lbl) in enumerate(self.allies_labels):
            c = self.env.chars[i]
            role = roles[int(c[4])]
            if c[2] <= 0:
                name_lbl.config(text=f"{i + 1}. {role} [💀]", fg="#444444")
                hp_lbl.config(text="—", fg="#444444")
            else:
                ratio = c[2] / c[3]
                color = "#00ff00" if ratio > 0.6 else "#ffaa00" if ratio > 0.3 else "#ff4444"
                name_lbl.config(text=f"{i + 1}. {role}", fg="#00ff88")
                hp_lbl.config(text=f"{c[2]}/{c[3]}", fg=color)

        for i, (name_lbl, hp_lbl) in enumerate(self.enemies_labels):
            c = self.env.chars[3 + i]
            role = roles[int(c[4])]
            if c[2] <= 0:
                name_lbl.config(text=f"{i + 1}. {role} [💀]", fg="#444444")
                hp_lbl.config(text="—", fg="#444444")
            else:
                ratio = c[2] / c[3]
                color = "#ff6666" if ratio > 0.6 else "#ffaa00" if ratio > 0.3 else "#ff4444"
                name_lbl.config(text=f"{i + 1}. {role}", fg="#ff4444")
                hp_lbl.config(text=f"{c[2]}/{c[3]}", fg=color)

        if hasattr(self.env, 'threat_matrix'):
            parts = []
            for i in range(3):
                if self.env.chars[3 + i][2] > 0:
                    v = round(self.env.threat_matrix[0][i], 1)
                    parts.append(f"E{i}: {v}")
            self.threat_label.config(text="  ".join(parts) or "—")

    # ============================== GAME FLOW ==============================
    def new_game(self):
        if self.auto_play_id:
            self.root.after_cancel(self.auto_play_id)
            self.auto_play_id = None

        self.kill_log = []
        self.revenge_target = None
        self.revenge_mode = False
        self.turn_count = 0
        self.hint_penalty_total = 0
        self.active = False

        self._load_model()
        self.env = EnhancedTacticalRPG(personality=self.current_personality.get())
        self.obs, _ = self.env.reset()

        cfg = self._diff_cfg()
        if self.hero_buff_enabled.get() and self.difficulty.get() != "hard":
            for c in self.env.chars[:3]:
                c[3] = int(c[3] * 1.3)
                c[2] = c[3]
                c[0] += 2
            self._log_event("Hero buff active: +30% HP, +2 ATK", "system")

        if cfg['hp_bonus'] > 0:
            for c in self.env.chars[3:]:
                c[3] = int(c[3] * (1 + cfg['hp_bonus']))
                c[2] = c[3]
            self._log_event(f"Hard mode: enemy HP +{int(cfg['hp_bonus'] * 100)}%", "system")

        diff_msgs = {
            "easy": "Easy mode — reduced enemy damage.",
            "normal": "Normal mode — balanced combat.",
            "hard": "Hard mode — maximum enemy strength!",
        }
        self._log_event(diff_msgs[self.difficulty.get()], "system")

        self.auto = False
        self.human_choice_mode.set(True)
        self.active = True

        # Clear displays
        self.reasoning_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.feedback_text.config(text="Make your first move to see analysis.", fg="#aaaaaa")

        self._update_display()
        self._start_new_turn()
        self.status.config(text=f"New game — {self.current_personality.get().capitalize()} | {self.difficulty.get().capitalize()}")

    def _handle_game_end(self, info):
        if self.auto_play_id:
            self.root.after_cancel(self.auto_play_id)
            self.auto_play_id = None

        self.active = False
        self.auto = False
        self.auto_btn.config(text="Auto Turn", bg="#0066cc")

        result = info.get('result', 'unknown')

        if result == 'victory':
            self.wins += 1
            self._log_event(f"🏆 VICTORY in {self.turn_count} turns!", "victory")
            self.status.config(text=f"🏆 Victory! {self.turn_count} turns", fg="#00ff00")
        else:
            self.losses += 1
            self._log_event("💀 DEFEAT - All allies eliminated", "kill")
            self.status.config(text="💀 Defeat", fg="#ff4444")

        self.total_matches += 1
        wr = round(self.wins / self.total_matches * 100) if self.total_matches else 0
        self.wl_label.config(text=f"W: {self.wins} | L: {self.losses} | WR: {wr}%")
        self._update_display()

    def _toggle_auto(self):
        if self.human_choice_mode.get():
            return
        self.auto = not self.auto
        if self.auto:
            self.auto_btn.config(text="⏸ Pause", bg="#cc6600")
            self._auto_loop()
        else:
            self.auto_btn.config(text="Auto Turn", bg="#0066cc")
            if self.auto_play_id:
                self.root.after_cancel(self.auto_play_id)
                self.auto_play_id = None

    def _auto_loop(self):
        if self.auto and self.active and not self.human_choice_mode.get():
            # Get action
            action, _ = self.model.predict(self.obs, deterministic=False)
            
            # Execute with auto=True to trigger AI move analysis
            self._execute_action(int(action[1]), int(action[0]), auto=True)
            
            # Schedule next turn
            self.auto_play_id = self.root.after(1400, self._auto_loop)

    def _get_timer_seconds(self):
        return self._diff_cfg()["timer"]

    def _start_timer(self):
        self._stop_timer()
        self.timer_max = self._get_timer_seconds()
        self.timer_val = self.timer_max
        self._tick_timer()

    def _stop_timer(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

    def _tick_timer(self):
        if not self.active or not self.human_choice_mode.get():
            return
        self._update_timer_ui()
        if self.timer_val <= 0:
            self._log_event("Time ran out — AI took over this turn!", "warn")
            self._ai_emergency_move()
            return
        self.timer_val -= 1
        self.timer_job = self.root.after(1000, self._tick_timer)

    def _update_timer_ui(self):
        pct = self.timer_val / self.timer_max if self.timer_max else 0
        color = "#00ff88" if pct > 0.5 else "#ffaa00" if pct > 0.25 else "#ff4444"
        self.timer_label.config(text=f"{self.timer_val}s", fg=color)
        w = self.timer_canvas.winfo_width()
        h = self.timer_canvas.winfo_height()
        self.timer_canvas.delete("all")
        if w > 0 and h > 0:
            self.timer_canvas.create_rectangle(0, 0, int(w * pct), h, fill=color, outline="")

    def _ai_emergency_move(self):
        hint = self._get_best_ai_action()
        self._execute_action(0, hint.get('target_idx', 0), auto=True)

    def _on_personality_change(self, event=None):
        self.current_personality.set(self.personality_combo.get().lower())
        self.new_game()

    def _toggle_buff(self):
        self.hero_buff_enabled.set(not self.hero_buff_enabled.get())
        self.buff_btn.config(
            text="Hero Buff: ON" if self.hero_buff_enabled.get() else "Hero Buff: OFF",
            fg="#00ff88" if self.hero_buff_enabled.get() else "#ff4444"
        )

    # ============================== SAVE/LOAD/EXPORT/STATS ==============================
    def _save_game(self):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = f"savegame_{ts}.json"
        try:
            with open(fname, 'w') as f:
                json.dump({
                    'turn': self.turn_count,
                    'chars': self.env.chars,
                    'wins': self.wins,
                    'losses': self.losses,
                    'total': self.total_matches,
                    'kills': self.kill_log,
                    'achievements': self.achievements,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
            messagebox.showinfo("Saved", f"Game saved to {fname}")
        except Exception as e:
            messagebox.showerror("Save failed", str(e))

    def _load_game(self):
        fname = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not fname:
            return
        try:
            with open(fname) as f:
                data = json.load(f)
            self.turn_count = data['turn']
            self.env.chars = data['chars']
            self.wins = data['wins']
            self.losses = data['losses']
            self.total_matches = data['total']
            self.kill_log = data['kills']
            self.achievements = data.get('achievements', self.achievements)
            wr = round(self.wins / self.total_matches * 100) if self.total_matches else 0
            self.wl_label.config(text=f"W: {self.wins} | L: {self.losses} | WR: {wr}%")
            self._update_display()
            messagebox.showinfo("Loaded", f"Game loaded from {fname}")
        except Exception as e:
            messagebox.showerror("Load failed", str(e))

    def _export_log(self):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = f"battle_log_{ts}.json"
        wr = round(self.wins / self.total_matches * 100) if self.total_matches else 0
        try:
            with open(fname, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'turns': self.turn_count,
                    'difficulty': self.difficulty.get(),
                    'personality': self.current_personality.get(),
                    'wins': self.wins,
                    'losses': self.losses,
                    'win_rate': wr,
                    'hint_penalties': self.hint_penalty_total,
                    'kills': self.kill_log,
                    'log': self.battle_log,
                    'achievements': self.achievements,
                    'system': 'LLM-RL Hybrid'
                }, f, indent=2)
            messagebox.showinfo("Exported", f"Log saved to {fname}\nWin rate: {wr}%")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def _show_stats(self):
        wr = round(self.wins / self.total_matches * 100) if self.total_matches else 0
        kills = len([k for k in self.kill_log if 'Enemy' in k['victim']])
        deaths = len([k for k in self.kill_log if 'Ally' in k['victim']])
        kd = round(kills / deaths, 2) if deaths else kills

        win = tk.Toplevel(self.root)
        win.title("Statistics Dashboard")
        win.geometry("500x400")
        win.configure(bg="#1a1a2e")

        txt = scrolledtext.ScrolledText(win, font=("Consolas", 9),
                                         bg="#0d0d0d", fg="#00ff00",
                                         width=60, height=22)
        txt.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        txt.insert(tk.END, f"""
STATISTICS DASHBOARD
═══════════════════════════════════
Matches played : {self.total_matches}
Wins           : {self.wins}
Losses         : {self.losses}
Win rate       : {wr}%
Hint penalties : {self.hint_penalty_total} pts

ELIMINATIONS
═══════════════════════════════════
Enemies killed : {kills}
Allies lost    : {deaths}
K/D ratio      : {kd}

ACHIEVEMENTS
═══════════════════════════════════
""")
        for k, v in self.achievements.items():
            txt.insert(tk.END, f"  {'[X]' if v else '[ ]'} {k.replace('_', ' ').title()}\n")
        txt.config(state=tk.DISABLED)

    def _log_event(self, msg, etype="info"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.battle_log.append({'time': ts, 'msg': msg, 'type': etype})
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    print("=" * 70)
    print("AI RPG ARENA — Human-First Tactical Edition")
    print("=" * 70)
    print("Features:")
    print("  ✅ AI analysis visible on RIGHT panel every turn")
    print("  ✅ Target buttons properly displayed")
    print("  ✅ Reasoning options properly displayed")
    print("  ✅ After-move analysis working")
    print("  ✅ Timer and auto-skip working")
    print("=" * 70 + "\n")

    app = UltimateRPGUI()
    app.run()
