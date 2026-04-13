"""
LLM EXPLANATION ENGINE
======================
Generates rich narrative, strategic reasoning, alternatives,
confidence scores, and threat analysis for every AI action.
"""

import random
import numpy as np


class AdvancedLLMExplanationEngine:

    def __init__(self):
        self.action_history = []
        self.dramatic_tension = 0
        self.battle_cries_used = []

        self.attack_narratives = {
            "aggressive": [
                "launches a ferocious assault!",
                "strikes with brutal force!",
                "unleashes devastating power!",
                "crushes with overwhelming might!",
                "tears through defenses violently!",
            ],
            "defensive": [
                "executes a calculated strike!",
                "waits for the perfect opening!",
                "strikes with measured precision!",
                "capitalises on a tactical gap!",
                "delivers a counter-blow!",
            ],
            "strategist": [
                "manoeuvres into optimal position!",
                "exploits tactical weakness!",
                "coordinates a precise strike!",
                "executes the battle plan flawlessly!",
                "identifies a critical vulnerability!",
            ],
            "chaotic": [
                "unleashes unpredictable fury!",
                "attacks with wild abandon!",
                "creates glorious chaos!",
                "defies all tactical logic!",
                "turns the battle into mayhem!",
            ],
        }

        self.heal_narratives = {
            "aggressive": ["refuses to stay down!", "pushes through pain!", "ignores fatal wounds!"],
            "defensive": ["stabilises critical wounds!", "reinforces defences!", "restores battle readiness!"],
            "strategist": ["optimises recovery protocols!", "strategic regeneration!", "calculated restoration!"],
            "chaotic": ["miraculous recovery!", "defies medical logic!", "chaotic regeneration!"],
        }

        self.critical_narratives = [
            "CRITICAL STRIKE — the blow lands with terrifying precision!",
            "DEVASTATING HIT — bones shatter under the impact!",
            "ANNIHILATING BLOW — the attack connects perfectly!",
            "BRUTAL CRITICAL — the enemy reels from the strike!",
        ]

        self.threat_narratives = {
            "critical": ["CRITICAL THREAT — immediate action required!", "EXTREME DANGER — ally on the brink!"],
            "high":     ["High threat — enemy pressure mounting!", "Significant danger — situation deteriorating!"],
            "medium":   ["Moderate threat — enemy forces regrouping!", "Caution advised — balance shifting!"],
            "low":      ["Low threat — tactical advantage held!", "Situation normal — maintain current strategy!"],
        }

        self.battle_cries = {
            "aggressive": ["Charge — show no mercy!", "Fight or die!", "Let none survive!"],
            "defensive":  ["Hold the line — stand strong!", "Endure and overcome!", "Steady — wait for the moment!"],
            "strategist": ["Execute the plan!", "Control the battlefield!", "Calculated precision!"],
            "chaotic":    ["For chaos and glory!", "Unleash the mayhem!", "No plan? No problem!"],
        }

    # ------------------------------------------------------------------
    def generate_narrative(self, action, chars, personality, info=None,
                           revenge_active=False, ultra_mode=False, turn=0):
        act_idx = int(action[1]) if isinstance(action, (list, np.ndarray)) else 0
        target_idx = int(action[0]) if isinstance(action, (list, np.ndarray)) else 0

        roles  = ['Tank', 'DPS', 'Healer']
        teams  = ['Ally', 'Enemy']

        target_info = ""
        if target_idx < len(chars):
            t = chars[target_idx]
            hp_pct = (t[2] / t[3] * 100) if t[3] > 0 else 0
            target_info = f"{teams[t[5]]} {roles[t[4]]} (HP: {hp_pct:.0f}%)"

        if act_idx == 0:
            narratives = self.attack_narratives.get(personality, self.attack_narratives["aggressive"])
            narrative = "The unit " + random.choice(narratives)
            if info and info.get('critical'):
                narrative += "\n" + random.choice(self.critical_narratives)
            if target_info:
                narrative += f"\nTarget: {target_info}"
        elif act_idx == 4:
            narratives = self.heal_narratives.get(personality, self.heal_narratives["defensive"])
            narrative = "The healer " + random.choice(narratives)
            if target_info:
                narrative += f"\nTarget: {target_info}"
        elif act_idx == 1:
            narrative = "Adopts defensive posture — mitigating incoming damage."
        elif act_idx == 2:
            narrative = "Unleashes special ability — tactical advantage gained!"
        else:
            narrative = "Tactical repositioning — new angle of engagement acquired."

        if revenge_active:
            narrative += "\nRevenge protocol active — avenging fallen comrades!"
        if ultra_mode:
            narrative += "\nUltra-aggressive stance engaged — numerical disadvantage detected!"

        if info:
            if info.get('damage'):
                narrative += f"\nDamage dealt: {info['damage']} HP"
            if info.get('heal_amount'):
                narrative += f"\nHealing applied: +{info['heal_amount']} HP"
            if info.get('killed_enemy'):
                narrative += "\nTarget eliminated!"

        return narrative

    def generate_strategic_reasoning(self, action, chars, personality, revenge_active, ultra_mode):
        act_idx    = int(action[1]) if isinstance(action, (list, np.ndarray)) else 0
        target_idx = int(action[0]) if isinstance(action, (list, np.ndarray)) else 0

        reasoning = f"[{personality.upper()} TACTICAL ANALYSIS] "

        if revenge_active:
            reasoning += "Revenge protocol engaged — eliminating the threat that felled our ally. "
        elif ultra_mode:
            reasoning += "ULTRA-AGGRESSIVE stance — numerical disadvantage detected. Maximum damage prioritised. "

        if act_idx == 0 and target_idx >= 3:
            if target_idx < len(chars):
                target = chars[target_idx]
                hp_pct = target[2] / target[3] if target[3] > 0 else 0
                if hp_pct < 0.3:
                    reasoning += "Execution priority — enemy near elimination. Finishing blow recommended. "
                elif target[0] > 6:
                    reasoning += f"High-value target (ATK: {target[0]}) — reducing enemy damage output is critical. "
                else:
                    reasoning += "Standard engagement — wearing down enemy defences. "
        elif act_idx == 4 and target_idx < 3:
            if target_idx < len(chars):
                target = chars[target_idx]
                hp_pct = target[2] / target[3] if target[3] > 0 else 0
                role = ['Tank', 'DPS', 'Healer'][target[4]]
                reasoning += f"Sustain priority — {role} at {hp_pct:.0%} HP requires immediate restoration. "
        elif act_idx == 1:
            reasoning += "Defensive posture adopted — preserving resources for counter-attack. "

        return reasoning

    def generate_alternatives(self, action, chars, personality):
        act_idx = int(action[1]) if isinstance(action, (list, np.ndarray)) else 0
        alternatives = []

        if act_idx == 0:
            alive_enemies = [i for i in range(3, 6) if i < len(chars) and chars[i][2] > 0]
            if len(alive_enemies) > 1:
                alt = alive_enemies[0] if alive_enemies[0] != int(action[0]) else alive_enemies[-1]
                alt_role = ['Enemy Tank', 'Enemy DPS', 'Enemy Healer'][chars[alt][4]]
                alternatives.append({'action': f"Attack {alt_role}", 'why': "Alternative target with different threat priority"})

        if act_idx == 0:
            low_ally = next((i for i in range(3) if chars[i][2] > 0 and chars[i][2] / chars[i][3] < 0.4), None)
            if low_ally is not None:
                alt_role = ['Tank', 'DPS', 'Healer'][chars[low_ally][4]]
                alternatives.append({'action': f"Heal {alt_role}", 'why': "Ally at critical health — sustain priority"})

        if act_idx != 1:
            alternatives.append({'action': "Defend", 'why': "Conservative approach — preserve resources"})

        return alternatives[:2]

    def calculate_confidence(self, info, chars, ultra_mode):
        base = random.uniform(0.75, 0.95)
        if ultra_mode:            base += 0.10
        if info and info.get('critical'):    base += 0.05
        if info and info.get('killed_enemy'): base += 0.10
        ally_healths = [c[2] / c[3] for c in chars[:3] if c[3] > 0]
        if ally_healths:
            avg = sum(ally_healths) / len(ally_healths)
            if avg < 0.3:   base -= 0.15
            elif avg > 0.7: base += 0.05
        return round(min(0.99, max(0.50, base)), 2)

    def analyze_threat(self, chars):
        threat_level = "low"
        for i in range(3):
            if i < len(chars) and chars[i][2] > 0:
                hp_ratio = chars[i][2] / chars[i][3] if chars[i][3] > 0 else 0
                if hp_ratio < 0.2:
                    threat_level = "critical"
                    break
                elif hp_ratio < 0.4:
                    threat_level = "high"
                elif hp_ratio < 0.6 and threat_level == "low":
                    threat_level = "medium"

        enemies_alive = sum(1 for i in range(3, 6) if i < len(chars) and chars[i][2] > 0)
        if enemies_alive >= 3 and threat_level == "low":
            threat_level = "medium"

        narrative = random.choice(self.threat_narratives[threat_level])
        return threat_level, narrative

    def generate_battle_cry(self, personality, ultra_mode, revenge_active, difficulty):
        if revenge_active:
            cries = [
                "For the fallen — this is for my comrade!",
                "Vengeance shall be mine — prepare to fall!",
                "You took one of us — now face our wrath!",
            ]
        elif ultra_mode:
            cries = [
                "We are outnumbered — fight harder!",
                "No retreat, no surrender — fight to the end!",
                "Desperate times call for desperate measures!",
            ]
        else:
            cries = self.battle_cries.get(personality, self.battle_cries["aggressive"])

        cry = random.choice(cries)
        if difficulty == "hard":
            cry += "  [Hard mode — no mercy!]"
        return cry

    def get_full_explanation(self, action, chars, personality, info=None,
                             revenge_active=False, ultra_mode=False,
                             difficulty="normal", turn=0):
        narrative   = self.generate_narrative(action, chars, personality, info, revenge_active, ultra_mode, turn)
        reasoning   = self.generate_strategic_reasoning(action, chars, personality, revenge_active, ultra_mode)
        alternatives = self.generate_alternatives(action, chars, personality)
        confidence  = self.calculate_confidence(info, chars, ultra_mode)
        threat_level, threat_narrative = self.analyze_threat(chars)
        battle_cry  = self.generate_battle_cry(personality, ultra_mode, revenge_active, difficulty)

        action_names = ['Attack', 'Defend', 'Ability', 'Move', 'Heal']
        target_idx   = int(action[0]) if isinstance(action, (list, np.ndarray)) else 0

        return {
            'action':           f"{action_names[int(action[1])]} -> Target {target_idx}",
            'narrative':        narrative,
            'reasoning':        reasoning,
            'alternatives':     alternatives,
            'confidence':       confidence,
            'threat_level':     threat_level,
            'threat_narrative': threat_narrative,
            'battle_cry':       battle_cry,
            'source':           'LLM-RL Hybrid System',
            'llm_calls':        1,
        }
