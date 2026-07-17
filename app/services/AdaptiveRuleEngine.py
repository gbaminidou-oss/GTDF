"""
AdaptiveRuleEngine.py
=====================
Implements the Adaptive Rule Engine described in the GTDF dissertation (§4.6, Fig 4.21).

Decision logic:
  Domain score < 40%   → Beginner   (High Priority Path)
  Domain score 40–74%  → Intermediate (Medium Priority Path)
  Domain score ≥ 75%   → Advanced   (Low Priority Path)
  Unclear case         → defaults to Intermediate

Dynamic difficulty adjustment during learning:
  3 consecutive correct → upgrade difficulty
  2 consecutive wrong   → downgrade + enable hints

This service is stateless — all inputs come in as parameters, all outputs are
returned as plain dicts so routes/models stay fully decoupled.
"""

from config import Config


# ── Threshold constants (dissertation §4.6) ───────────────────────────────────
BEGINNER_MAX = Config.BEGINNER_MAX          # < 40
INTERMEDIATE_MAX = Config.INTERMEDIATE_MAX  # 40 – 74
ADVANCED_MIN = Config.ADVANCED_MIN          # ≥ 75

CORRECT_STREAK_UPGRADE = Config.CORRECT_STREAK_UPGRADE   # 3
WRONG_STREAK_DOWNGRADE = Config.WRONG_STREAK_DOWNGRADE   # 2

DIFFICULTY_ORDER = ["beginner", "intermediate", "advanced"]

# Module ordering per domain (aligns to GTDF modules 1-7)
DOMAIN_MODULE_MAP = {
    "phishing":           1,
    "social_engineering": 2,
    "password_security":  3,
    "safe_browsing":      4,
    "pretexting":         5,
    "data_handling":      6,
    "incident_reporting": 7,
}


class AdaptiveRuleEngine:
    """
    Stateless engine that reads assessment scores and produces a personalised
    learning path.  All public methods accept plain dicts and return plain dicts.
    """

    # ── 1. Initial level assignment ───────────────────────────────────────────
    @staticmethod
    def assign_level(score: float) -> str:
        """
        Map a percentage score (0–100) to a difficulty level string.

        Args:
            score: percentage score for a domain (0.0 – 100.0)

        Returns:
            'beginner' | 'intermediate' | 'advanced'
        """
        if score < BEGINNER_MAX + 1:       # < 40 → Beginner
            return "beginner"
        elif score <= INTERMEDIATE_MAX:    # 40–74 → Intermediate
            return "intermediate"
        else:                              # ≥ 75 → Advanced
            return "advanced"

    @staticmethod
    def assign_risk(overall_score: float) -> str:
        """
        Map overall score to PMT-aligned risk level.

        High risk   → score < 40  (weak threat coping)
        Medium risk → score 40–74
        Low risk    → score ≥ 75
        """
        if overall_score < 40:
            return "high"
        elif overall_score < 75:
            return "medium"
        else:
            return "low"

    # ── 2. Full learning path from assessment results ─────────────────────────
    @classmethod
    def build_learning_path(cls, domain_scores: dict) -> dict:
        """
        Process per-domain scores and produce a structured learning path.

        Args:
            domain_scores: {domain_name: score_pct, ...}

        Returns:
            {
              'domain_levels':   {domain: level},
              'priority_order':  [domain, ...],   # weakest first
              'weakest_domain':  str,
              'overall_score':   float,
              'risk_level':      str,
              'module_order':    [module_id, ...],
              'recommendations': [str, ...],
            }
        """
        if not domain_scores:
            return cls._empty_path()

        domain_levels = {
            domain: cls.assign_level(score)
            for domain, score in domain_scores.items()
        }

        # Sort weakest first (ascending score)
        priority_order = sorted(domain_scores, key=lambda d: domain_scores[d])
        weakest_domain = priority_order[0]
        overall_score = sum(domain_scores.values()) / len(domain_scores)

        module_order = [
            DOMAIN_MODULE_MAP[d]
            for d in priority_order
            if d in DOMAIN_MODULE_MAP
        ]

        recommendations = cls._generate_recommendations(domain_scores, domain_levels)

        return {
            "domain_levels":  domain_levels,
            "priority_order": priority_order,
            "weakest_domain": weakest_domain,
            "overall_score":  round(overall_score, 1),
            "risk_level":     cls.assign_risk(overall_score),
            "module_order":   module_order,
            "recommendations": recommendations,
        }

    # ── 3. Dynamic difficulty adjustment (in-session) ─────────────────────────
    @staticmethod
    def adjust_difficulty(
        current_difficulty: str,
        correct_streak: int,
        wrong_streak: int,
    ) -> dict:
        """
        Apply in-session difficulty adjustment rules (Fig 4.21).

        Args:
            current_difficulty: current level string
            correct_streak:     consecutive correct answers so far
            wrong_streak:       consecutive wrong answers so far

        Returns:
            {
              'new_difficulty': str,
              'hints_enabled':  bool,
              'event':          str,  # 'upgrade' | 'downgrade' | 'no_change'
            }
        """
        idx = DIFFICULTY_ORDER.index(current_difficulty) if current_difficulty in DIFFICULTY_ORDER else 0
        hints_enabled = False
        event = "no_change"

        if correct_streak >= CORRECT_STREAK_UPGRADE:
            # Upgrade if not already at max
            if idx < len(DIFFICULTY_ORDER) - 1:
                idx += 1
                event = "upgrade"
        elif wrong_streak >= WRONG_STREAK_DOWNGRADE:
            # Downgrade if not at min
            if idx > 0:
                idx -= 1
            hints_enabled = True   # enable hints regardless
            event = "downgrade"

        return {
            "new_difficulty": DIFFICULTY_ORDER[idx],
            "hints_enabled":  hints_enabled,
            "event":          event,
        }

    # ── 4. Record an attempt and return streak updates ───────────────────────
    @staticmethod
    def update_streaks(is_correct: bool, correct_streak: int, wrong_streak: int) -> dict:
        """
        Update streak counters after an answer.

        Returns:
            {'correct_streak': int, 'wrong_streak': int}
        """
        if is_correct:
            return {"correct_streak": correct_streak + 1, "wrong_streak": 0}
        else:
            return {"correct_streak": 0, "wrong_streak": wrong_streak + 1}

    # ── 5. Module unlock decision ─────────────────────────────────────────────
    @staticmethod
    def can_unlock_module(module_order: int, completed_module_ids: list) -> bool:
        """
        A module is unlocked if either it is module 1, or the previous module
        in the ordered sequence has been completed.

        Args:
            module_order: the .order field of the module to check (1-based)
            completed_module_ids: list of module .order values completed by user

        Returns:
            bool
        """
        if module_order == 1:
            return True
        return (module_order - 1) in completed_module_ids

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _generate_recommendations(domain_scores: dict, domain_levels: dict) -> list:
        tips = {
            "phishing":           "Practice identifying suspicious email headers and links.",
            "social_engineering": "Learn about authority and urgency manipulation tactics.",
            "password_security":  "Focus on creating and managing strong, unique passwords.",
            "safe_browsing":      "Study how to verify website authenticity before entering data.",
            "pretexting":         "Understand how attackers fabricate scenarios to extract information.",
            "data_handling":      "Review data classification and secure disposal practices.",
            "incident_reporting": "Learn the correct steps to escalate a suspected security incident.",
        }
        recs = []
        for domain in sorted(domain_scores, key=lambda d: domain_scores[d]):
            if domain_scores[domain] < 75:
                recs.append(f"[{domain_levels[domain].upper()}] {tips.get(domain, domain)}")
        return recs[:5]  # top 5 recommendations

    @staticmethod
    def _empty_path() -> dict:
        return {
            "domain_levels":   {},
            "priority_order":  [],
            "weakest_domain":  "",
            "overall_score":   0.0,
            "risk_level":      "unknown",
            "module_order":    [1, 2, 3, 4, 5, 6, 7],
            "recommendations": [],
        }
