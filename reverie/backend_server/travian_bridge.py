"""TravianBridge — reads Travian Bot state and drives generative agent behavior.

Polls bot_state.json from the Travian Bot repo and translates bot phases/events
into persona actions, movements, and memories for the generative agents simulation.
"""
import json
import os
import time
from typing import Dict, List, Optional, Tuple

# Path to the Travian Bot repo's state file
TRAVIAN_BOT_ROOT = "/Users/tomyimkc/Documents/GitHub/Travian_Bot"
BOT_STATE_FILE = os.path.join(TRAVIAN_BOT_ROOT, "bot_state.json")


class TravianBridge:
    """Reads Travian Bot state files and translates them into
    generative agent simulation events and persona overrides."""

    # Maps bot phases → (persona_name, target_arena_suffix)
    # target_arena_suffix is the arena name that the active persona should walk to
    PHASE_MAP: Dict[str, Tuple[str, str]] = {
        # Phase 1: Village profiles
        "Village Profiles — Loop":      ("Commander Marcus",  "Strategy Hall"),
        "Village Profiles":             ("Commander Marcus",  "Strategy Hall"),
        # Phase 2: Preflight
        "Preflight":                    ("Scout Varro",       "Scout Tower"),
        "Preflight — Scanning":         ("Scout Varro",       "Scout Tower"),
        # Phase 3: Main crop check
        "Main Crop Check":              ("Centurion Titus",   "Training Grounds"),
        "Main Crop Emergency":          ("Centurion Titus",   "Training Grounds"),
        # Phase 4-5: Grey zone
        "Developed → Grey Zone (support)": ("Treasurer Lucius", "Treasury"),
        "Grey Zone Upgrades (plan-driven)": ("Builder Gaius",  "Construction Yard"),
        # Phase 6: Overflow
        "Developed → Main (overflow)":  ("Treasurer Lucius",  "Treasury"),
        # Phase 7-8: Developing
        "Developed → Developing (support)": ("Treasurer Lucius", "Treasury"),
        "Developing Upgrades (plan-driven)": ("Builder Gaius", "Construction Yard"),
        # Phase 9: Excess back
        "Developing → Main (excess)":   ("Treasurer Lucius",  "Treasury"),
        # Phase 10: Focus
        "Focus":                        ("Strategist Livia",  "Focus Chamber"),
        # Phase 11: Crop redistribution
        "Developed Crop → Developing":  ("Treasurer Lucius",  "Treasury"),
        # Phase 12: Training
        "Training":                     ("Centurion Titus",   "Training Grounds"),
        # Phase 13: Main fields
        "Main Fields":                  ("Builder Gaius",     "Construction Yard"),
        # Phase 14: Developed training
        "Developed Training":           ("Centurion Titus",   "Training Grounds"),
        # Idle / between cycles
        "init":                         ("Commander Marcus",  "Strategy Hall"),
        "Cycle Complete":               ("Commander Marcus",  "Briefing Room"),
    }

    # Maps event types to which persona should "think" about them
    EVENT_TYPE_TO_PERSONA: Dict[str, str] = {
        "resource_send":    "Treasurer Lucius",
        "resource_receive": "Treasurer Lucius",
        "build_start":      "Builder Gaius",
        "build_complete":   "Builder Gaius",
        "train_start":      "Centurion Titus",
        "train_complete":   "Centurion Titus",
        "dodge_triggered":  "Sentinel Felix",
        "attack_detected":  "Sentinel Felix",
        "focus_action":     "Strategist Livia",
        "profile_update":   "Archivist Petra",
        "preflight_scan":   "Scout Varro",
        "validation_error": "Validator Quintus",
        "phase_change":     "Commander Marcus",
    }

    def __init__(self):
        self._last_mtime: float = 0.0
        self._cached_state: Dict = {}
        self._last_event_ts: float = 0.0
        self._last_phase: str = ""

    def poll(self) -> Optional[Dict]:
        """Read bot_state.json if it has been modified since last check.

        Returns the state dict if updated, None if unchanged or unavailable.
        """
        if not os.path.exists(BOT_STATE_FILE):
            return None

        try:
            mtime = os.path.getmtime(BOT_STATE_FILE)
            if mtime <= self._last_mtime:
                return None  # No change

            with open(BOT_STATE_FILE, "r") as f:
                state = json.load(f)

            self._last_mtime = mtime
            self._cached_state = state
            return state

        except (json.JSONDecodeError, OSError, IOError):
            return None

    @property
    def state(self) -> Dict:
        """Return the last cached state (whether or not poll found changes)."""
        return self._cached_state

    def get_active_persona(self) -> Tuple[str, str]:
        """Return (persona_name, target_arena) based on current bot phase.

        Returns:
            Tuple of (persona_name, arena_name) for the currently active manager.
        """
        meta = self._cached_state.get("meta", {})
        phase = meta.get("phase", "init")
        return self.PHASE_MAP.get(phase, ("Commander Marcus", "Strategy Hall"))

    def get_phase(self) -> str:
        """Return the current bot phase string."""
        return self._cached_state.get("meta", {}).get("phase", "init")

    def is_running(self) -> bool:
        """Return True if the bot is currently running."""
        return self._cached_state.get("meta", {}).get("running", False)

    def get_loop_iteration(self) -> int:
        """Return the current loop iteration number."""
        return self._cached_state.get("meta", {}).get("loop_iteration", 0)

    def get_events_since(self, since_ts: float = 0) -> List[Dict]:
        """Return bot events newer than the given timestamp.

        Args:
            since_ts: Unix timestamp. Events after this time are returned.

        Returns:
            List of event dicts from bot_state.json.
        """
        events = self._cached_state.get("events", [])
        new_events = [e for e in events if e.get("timestamp", 0) > since_ts]
        return new_events

    def consume_new_events(self) -> List[Dict]:
        """Return new events since last call, updating the internal timestamp."""
        events = self.get_events_since(self._last_event_ts)
        if events:
            self._last_event_ts = max(e.get("timestamp", 0) for e in events)
        return events

    def has_phase_changed(self) -> bool:
        """Check if the phase has changed since last check."""
        current = self.get_phase()
        if current != self._last_phase:
            self._last_phase = current
            return True
        return False

    def event_to_thought(self, event: Dict) -> Tuple[str, str]:
        """Convert a bot event into a (persona_name, thought_string) pair.

        Args:
            event: An event dict from bot_state.json

        Returns:
            Tuple of (persona_name, thought_text) suitable for whisper injection.
        """
        event_type = event.get("type", "")
        message = event.get("message", "")
        source = event.get("source", "")
        target = event.get("target", "")
        phase = event.get("phase", "")

        # Determine which persona should think about this
        persona = self.EVENT_TYPE_TO_PERSONA.get(
            event_type, "Commander Marcus"
        )

        # Build natural-language thought
        if event_type == "resource_send":
            thought = (
                f"I just sent resources from {source} to {target}. "
                f"{message}"
            )
        elif event_type == "build_start":
            thought = (
                f"I started a new building upgrade: {message}. "
                f"Village: {source or target or 'unknown'}."
            )
        elif event_type == "build_complete":
            thought = (
                f"A building upgrade completed: {message}. "
                f"Village: {source or target or 'unknown'}."
            )
        elif event_type == "train_start":
            thought = (
                f"I began training troops: {message}. "
                f"At: {source or target or 'the barracks'}."
            )
        elif event_type in ("dodge_triggered", "attack_detected"):
            thought = (
                f"ALERT! {message}. "
                f"Village under threat: {target or source or 'unknown'}. "
                f"I must take immediate defensive action!"
            )
        elif event_type == "focus_action":
            thought = (
                f"Focus plan action: {message}. "
                f"Target village: {target or source or 'unknown'}."
            )
        elif event_type == "phase_change":
            thought = (
                f"The operational phase has changed to: {phase}. "
                f"{message}"
            )
        else:
            # Generic fallback
            thought = f"{message}"
            if source:
                thought += f" (from {source})"
            if target:
                thought += f" (to {target})"

        return persona, thought

    def get_phase_description(self) -> str:
        """Return a human-readable description of the current phase."""
        phase = self.get_phase()
        loop = self.get_loop_iteration()
        running = self.is_running()

        if not running:
            return "The Travian Bot is currently offline. All managers are on standby."

        descriptions = {
            "Village Profiles — Loop": "Commander Marcus is reviewing village classifications and tier assignments.",
            "Preflight": "Scout Varro is running reconnaissance scans across all villages.",
            "Main Crop Check": "Centurion Titus is checking if the main village has a crop emergency.",
            "Developed → Grey Zone (support)": "Treasurer Lucius is sending support resources to grey zone villages.",
            "Grey Zone Upgrades (plan-driven)": "Builder Gaius is upgrading buildings in grey zone villages.",
            "Developed → Main (overflow)": "Treasurer Lucius is transferring overflow resources to the main village.",
            "Developed → Developing (support)": "Treasurer Lucius is sending support to developing villages.",
            "Developing Upgrades (plan-driven)": "Builder Gaius is upgrading buildings in developing villages.",
            "Developing → Main (excess)": "Treasurer Lucius is transferring excess resources back to main.",
            "Focus": "Strategist Livia is executing special focus plan actions.",
            "Developed Crop → Developing": "Treasurer Lucius is redistributing crop to developing villages.",
            "Training": "Centurion Titus is training troops across the empire.",
            "Main Fields": "Builder Gaius is upgrading resource fields in the main village.",
            "Developed Training": "Centurion Titus is training defense troops in developed villages.",
            "Cycle Complete": "The operational cycle is complete. All managers are resting.",
        }

        desc = descriptions.get(phase, f"Current phase: {phase}")
        return f"[Loop {loop}] {desc}"

    def get_village_summary(self) -> str:
        """Return a brief summary of village status for persona context."""
        villages = self._cached_state.get("villages", {})
        if not villages:
            return "No village data available."

        lines = []
        for vid, v in villages.items():
            name = v.get("name", vid)
            vtype = v.get("type", "unknown")
            res = v.get("resources", {})
            lumber = res.get("lumber", "?")
            clay = res.get("clay", "?")
            iron = res.get("iron", "?")
            crop = res.get("crop", "?")
            lines.append(
                f"  {name} ({vtype}): L={lumber} C={clay} I={iron} Cr={crop}"
            )

        return "Village Status:\n" + "\n".join(lines[:10])  # Cap at 10
