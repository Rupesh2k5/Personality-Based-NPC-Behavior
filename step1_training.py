"""
STEP 1 ENHANCED: TACTICAL RPG WITH INTELLIGENCE FEATURES
=========================================================
Features:
  Threat-Based Targeting System
  Smart Healing Logic
  Anti-Spam Memory
  Action Diversity Tracking
  Personality Modes (4 types)
  Critical Hit System
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces
import random
from collections import deque
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import time
import os


class EnhancedTacticalRPG(gym.Env):
    def __init__(self, difficulty="medium", personality="aggressive", verbose=False):
        super().__init__()
        self.difficulty = difficulty
        self.personality = personality  # aggressive, defensive, strategist, chaotic
        self.verbose = verbose
        self.max_steps = 35
        self.action_space = spaces.MultiDiscrete([6, 5])
        self.observation_space = spaces.Box(0, 1, shape=(78,), dtype=np.float32)

        # Intelligence Features
        self.action_history = deque(maxlen=10)
        self.threat_matrix = np.zeros((3, 3))
        self.critical_hits = 0
        self.last_heal_target = None

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.step_count = 0
        self.kills = 0
        self.action_history.clear()
        self.episode_rewards = []
        self.enemy_focus_history = {}

        tank_bonus = random.randint(-5, 15)
        dps_bonus = random.randint(10, 25)
        healer_bonus = random.randint(-10, 5)
        enemy_var = [random.randint(-10, 10) for _ in range(3)]

        # [atk, def, hp, max_hp, role, team, power_level]
        self.chars = [
            [3, 4, 120 + tank_bonus, 120 + tank_bonus, 0, 0, 1],
            [5, 2, 100 + dps_bonus, 100 + dps_bonus, 1, 0, 2],
            [2, 2, 70 + healer_bonus, 70 + healer_bonus, 2, 0, 0],
            [random.randint(4, 7), 5, 80 + enemy_var[0], 80 + enemy_var[0], 1, 1, 0],
            [random.randint(5, 8), 6, 90 + enemy_var[1], 90 + enemy_var[1], 0, 1, 0],
            [random.randint(3, 6), 4, 65 + enemy_var[2], 65 + enemy_var[2], 2, 1, 0],
        ]

        for i in range(3, 6):
            self.enemy_focus_history[i] = []

        self._update_threat_matrix()

        self.relations = np.zeros((6, 6))
        for i in range(6):
            for j in range(6):
                self.relations[i][j] = 1 if self.chars[i][5] == self.chars[j][5] else -1

        return self._get_obs(), {}

    def _get_obs(self):
        obs = []
        for c in self.chars:
            obs.extend([
                c[0] / 10,
                c[1] / 10,
                c[2] / c[3] if c[3] > 0 else 0,
                c[4] / 2,
                c[5],
                1.0 if c[2] > 0 else 0.0
            ])
        relations_flat = self.relations.flatten()
        obs.extend(relations_flat[:33])
        obs.extend(self.threat_matrix.flatten())
        return np.array(obs, dtype=np.float32)

    def _update_threat_matrix(self):
        threat_values = {0: 0.5, 1: 1.5, 2: 1.0}
        for ally_idx in range(3):
            for enemy_idx in range(3):
                enemy = self.chars[3 + enemy_idx]
                if enemy[2] > 0:
                    base_threat = threat_values.get(enemy[4], 1.0)
                    hp_factor = 1.0 - (enemy[2] / enemy[3])
                    self.threat_matrix[ally_idx][enemy_idx] = base_threat * (1 + hp_factor)
                else:
                    self.threat_matrix[ally_idx][enemy_idx] = 0

    def _check_critical_hit(self, attacker, target):
        base_crit = 0.15
        if target[2] < target[3] * 0.3:
            base_crit += 0.25
        if attacker[6] >= 1:
            base_crit += 0.1
        return random.random() < base_crit

    def _get_smart_heal_target(self):
        allies = [(i, self.chars[i]) for i in range(3) if self.chars[i][2] > 0]
        if not allies:
            return None
        return min(allies, key=lambda x: x[1][2] / x[1][3])[0]

    def _check_spam(self, action_type):
        if len(self.action_history) >= 3:
            recent = list(self.action_history)[-3:]
            if all(a == action_type for a in recent):
                return True
        return False

    def _apply_personality(self, action_type, target_idx):
        if self.personality == "aggressive":
            if action_type != 0 and random.random() < 0.3:
                return 0, self._get_highest_threat_target()
        elif self.personality == "defensive":
            if action_type == 0 and random.random() < 0.3:
                heal_target = self._get_smart_heal_target()
                if heal_target is not None:
                    return 4, heal_target
        elif self.personality == "strategist":
            allies_low = any(c[2] / c[3] < 0.3 for c in self.chars[:3])
            if allies_low and action_type != 4:
                heal_target = self._get_smart_heal_target()
                if heal_target is not None:
                    return 4, heal_target
        elif self.personality == "chaotic":
            if random.random() < 0.2:
                return random.randint(0, 4), random.randint(0, 2)
        return action_type, target_idx

    def _get_highest_threat_target(self):
        threats = [(i, self.threat_matrix[0][i]) for i in range(3)
                   if self.chars[3 + i][2] > 0]
        if threats:
            return max(threats, key=lambda x: x[1])[0]
        return 0

    def _enemy_turn(self):
        damage_report = []
        total_ally_damage = 0

        enemy_indices = [i for i in range(3, 6) if self.chars[i][2] > 0]
        if not enemy_indices:
            return [], 0

        random.shuffle(enemy_indices)
        num_attackers = random.randint(1, min(2, len(enemy_indices)))
        attacking_enemies = enemy_indices[:num_attackers]

        for e_idx in attacking_enemies:
            enemy = self.chars[e_idx]
            alive_allies = [(i, self.chars[i]) for i in range(3) if self.chars[i][2] > 10]
            if not alive_allies:
                alive_allies = [(i, self.chars[i]) for i in range(3) if self.chars[i][2] > 1]
            if not alive_allies:
                continue

            target_weights = []
            for idx, ally in alive_allies:
                weight = 1.0
                if ally[6] >= 1:
                    weight *= 3.0
                weight *= (ally[2] / ally[3])
                target_weights.append(weight)

            if random.random() < 0.75:
                target_idx = random.choices([idx for idx, _ in alive_allies],
                                            weights=target_weights)[0]
            else:
                target_idx = random.choice([idx for idx, _ in alive_allies])

            target = self.chars[target_idx]
            self.enemy_focus_history[e_idx].append(target_idx)

            base_dmg = enemy[0] * random.randint(2, 4)
            if self._check_critical_hit(enemy, target):
                base_dmg = int(base_dmg * 1.5)

            dmg = random.randint(int(base_dmg * 0.8), int(base_dmg * 1.2))
            old_hp = target[2]
            min_hp = random.randint(1, 3)
            target[2] = max(min_hp, target[2] - dmg)
            actual_damage = old_hp - target[2]
            total_ally_damage += actual_damage

            role_names = ['Tank', 'DPS', 'Healer']
            target_role = role_names[int(target[4])]
            enemy_role = role_names[int(enemy[4])]

            damage_report.append(
                f"Enemy {e_idx - 3} ({enemy_role}) -> Ally {target_idx} ({target_role}): {actual_damage} dmg"
            )

        return damage_report, total_ally_damage

    def step(self, action):
        target_idx, act = int(action[0]), int(action[1])

        if target_idx >= len(self.chars):
            target_idx = 0

        target = self.chars[target_idx]
        reward = 0
        reward_breakdown = {}
        info = {"log": [], "success": False, "outcome_details": []}

        self.action_history.append(act)
        act, target_idx = self._apply_personality(act, target_idx)

        if self._check_spam(act):
            reward -= 20
            reward_breakdown['Spam Penalty'] = -20

        role_names = ['Tank', 'DPS', 'Healer']

        if act == 0:
            if target[5] == 1 and target[2] > 0:
                base_dmg = random.randint(20, 35)
                is_crit = self._check_critical_hit(self.chars[0], target)
                if is_crit:
                    base_dmg = int(base_dmg * 2.0)
                    self.critical_hits += 1
                    info['critical'] = True

                old_hp = target[2]
                target[2] = max(0, target[2] - base_dmg)
                actual_dmg = old_hp - target[2]

                enemy_threat_idx = target_idx - 3 if target_idx >= 3 else 0
                threat_bonus = self.threat_matrix[0][enemy_threat_idx] * 10

                dmg_reward = actual_dmg * 2.0 + threat_bonus
                reward += dmg_reward
                reward_breakdown['Damage Dealt'] = dmg_reward
                if threat_bonus > 0:
                    reward_breakdown['Threat Bonus'] = threat_bonus

                info['damage'] = actual_dmg
                info['success'] = True

                crit_text = "CRITICAL HIT! " if is_crit else ""
                outcome_msg = f"{crit_text}Dealt {actual_dmg} damage to Enemy {target_idx - 3} ({role_names[int(target[4])]})"
                info['outcome_details'].append(outcome_msg)
                info['log'].append(outcome_msg)

                if target[2] == 0:
                    self.kills += 1
                    kill_bonus = 150
                    reward += kill_bonus
                    reward_breakdown['Kill Bonus'] = kill_bonus
                    info['killed_enemy'] = True
                    kill_msg = f"Enemy {target_idx - 3} ({role_names[int(target[4])]}) ELIMINATED!"
                    info['outcome_details'].append(kill_msg)
                    info['log'].append(kill_msg)
            else:
                penalty = -35
                reward += penalty
                reward_breakdown['Invalid Attack'] = penalty
                info['outcome_details'].append("Invalid attack target!")

        elif act == 1:
            recent_defends = sum(1 for a in self.action_history if a == 1)
            if recent_defends >= 2:
                reward += -25
                reward_breakdown['Defend Spam'] = -25
            else:
                reward += -4
                reward_breakdown['Defend Cost'] = -4
            info['success'] = True
            info['outcome_details'].append("Defensive stance - damage reduction active")

        elif act == 2:
            if target[5] == 1 and target[2] > 0:
                base_dmg = random.randint(25, 40)
                enemy_threat_idx = target_idx - 3 if target_idx >= 3 else 0
                if self.threat_matrix[0][enemy_threat_idx] > 1.2:
                    base_dmg = int(base_dmg * 1.5)
                target[2] = max(0, target[2] - base_dmg)
                reward += base_dmg * 2.5
                reward_breakdown['Ability Damage'] = base_dmg * 2.5
                info['outcome_details'].append(f"Used special ability on Enemy {target_idx - 3}")
            else:
                reward += -18
                reward_breakdown['Ability Cost'] = -18
            info['success'] = True

        elif act == 3:
            reward += -3
            reward_breakdown['Move Cost'] = -3
            info['success'] = True
            info['outcome_details'].append("Tactical reposition completed")

        elif act == 4:
            heal_target = target_idx if target[5] == 0 else self._get_smart_heal_target()
            if heal_target is not None and self.chars[heal_target][5] == 0:
                target = self.chars[heal_target]
                heal = random.randint(25, 40)
                old_hp = target[2]
                target[2] = min(target[3], target[2] + heal)
                actual_heal = target[2] - old_hp
                heal_reward = actual_heal * 1.5
                reward += heal_reward
                reward_breakdown['Healing'] = heal_reward
                if old_hp < target[3] * 0.3:
                    reward += 30
                    reward_breakdown['Critical Heal Bonus'] = 30
                info['heal_amount'] = actual_heal
                info['success'] = True
                heal_msg = f"Healed Ally {heal_target} ({role_names[int(target[4])]}) for {actual_heal} HP"
                info['outcome_details'].append(heal_msg)
                info['log'].append(heal_msg)
            else:
                reward += -18
                reward_breakdown['Invalid Heal'] = -18
                info['outcome_details'].append("Cannot heal enemy!")

        enemy_logs, ally_damage = self._enemy_turn()
        info['log'].extend(enemy_logs)
        for log in enemy_logs:
            info['outcome_details'].append(log)
        if ally_damage > 0:
            damage_penalty = -ally_damage * 0.25
            reward += damage_penalty
            reward_breakdown['Ally Damage Taken'] = damage_penalty

        enemies_alive = sum(1 for c in self.chars[3:] if c[2] > 0)
        recent_attacks = sum(1 for a in list(self.action_history)[-6:] if a == 0)
        if enemies_alive > 0 and recent_attacks == 0:
            reward += -30
            reward_breakdown['No Attack Penalty'] = -30

        done = False
        if enemies_alive == 0:
            victory_bonus = 700
            if self.step_count < 20:
                speed_bonus = 200
                victory_bonus += speed_bonus
                reward_breakdown['Speed Bonus'] = speed_bonus
            reward += victory_bonus
            reward_breakdown['VICTORY BONUS'] = victory_bonus
            done = True
            info['result'] = 'victory'
            info['outcome_details'].append("VICTORY! All enemies defeated!")
            info['log'].append("ALL ENEMIES DEFEATED!")

        self.step_count += 1
        if self.step_count >= self.max_steps:
            timeout_penalty = -450
            reward += timeout_penalty
            reward_breakdown['Timeout Penalty'] = timeout_penalty
            done = True
            info['result'] = 'timeout'
            info['outcome_details'].append("Battle timeout - mission incomplete")

        self._update_threat_matrix()

        self.episode_rewards.append(reward)
        info['reward_breakdown'] = reward_breakdown
        info['total_reward'] = reward
        info['cumulative_reward'] = sum(self.episode_rewards)
        info['threat_matrix'] = self.threat_matrix.tolist()
        info['critical_hits'] = self.critical_hits

        return self._get_obs(), reward, done, False, info


def train(personality="aggressive", timesteps=250000):
    print(f"\nTraining {personality.upper()} personality for {timesteps} timesteps...")
    start_time = time.time()

    env = DummyVecEnv([lambda: EnhancedTacticalRPG(personality=personality)])
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=4e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        verbose=1
    )

    model.learn(total_timesteps=timesteps)
    model.save(f"npc_{personality}")

    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)

    print(f"{personality.upper()} model saved as 'npc_{personality}.zip'")
    print(f"Training time: {minutes} minutes {seconds} seconds")

    return model


if __name__ == "__main__":
    print("=" * 70)
    print("ENHANCED TACTICAL RPG - TRAINING")
    print("=" * 70)
    print("\n1. Train ALL 4 personalities (~90 minutes)")
    print("2. Train only AGGRESSIVE (~20 minutes)")
    print("3. Train specific personality")

    choice = input("\nSelect option (1/2/3): ").strip()

    if choice == '1':
        personalities = ["aggressive", "defensive", "strategist", "chaotic"]
        total_start = time.time()
        for i, personality in enumerate(personalities, 1):
            print(f"\nTraining {i}/4: {personality.upper()}")
            train(personality, timesteps=250000)
        total_time = time.time() - total_start
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        print(f"\nAll 4 personalities trained! Total time: {hours}h {minutes}m")
        for p in personalities:
            size = os.path.getsize(f"npc_{p}.zip") / 1024 if os.path.exists(f"npc_{p}.zip") else 0
            print(f"  npc_{p}.zip ({size:.1f} KB)")

    elif choice == '2':
        train("aggressive", timesteps=250000)

    elif choice == '3':
        print("\n1. Aggressive  2. Defensive  3. Strategist  4. Chaotic")
        p_choice = input("Select (1-4): ").strip()
        personalities = ["aggressive", "defensive", "strategist", "chaotic"]
        if p_choice.isdigit() and 1 <= int(p_choice) <= 4:
            train(personalities[int(p_choice) - 1], timesteps=250000)
        else:
            train("aggressive", timesteps=250000)
    else:
        train("aggressive", timesteps=250000)
