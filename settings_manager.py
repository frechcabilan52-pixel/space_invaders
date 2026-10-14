import json
import os

SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "game_settings.json"
)

DEFAULT_SETTINGS = {
    # AUDIO
    "sound_volume": 0.8,
    "music_volume": 0.5,

    # CONTROLS
    "mobile_controls": False,
    "left_button": False,
    "right_button": False,
    "fire_button": False,

    # DISPLAY
    "fullscreen": False,
    "show_fps": True,

    # GAMEPLAY
    "difficulty": "normal",
    "player_speed": 10,
    "enemy_difficulty": "normal",
    "screen_shake": True,
    "damage_effects": True,
}


class SettingsManager:

    def __init__(self, path: str = SETTINGS_PATH):
        self.path = path
        self.settings = self._load()

    def _load(self) -> dict:

        if not os.path.exists(self.path):
            self.settings = DEFAULT_SETTINGS.copy()
            self.save()
            return self.settings

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                loaded = json.load(file)

            if not isinstance(loaded, dict):
                raise ValueError(
                    "Settings file must contain a JSON object."
                )

            merged = DEFAULT_SETTINGS.copy()
            merged.update(loaded)

            valid_difficulties = (
                "easy", "normal", "hard"
            )

            if merged.get("difficulty") not in valid_difficulties:
                merged["difficulty"] = "normal"

            if merged.get("enemy_difficulty") not in valid_difficulties:
                merged["enemy_difficulty"] = "normal"

            try:
                merged["player_speed"] = max(
                    1, min(20, int(merged["player_speed"]))
                )
            except (TypeError, ValueError):
                merged["player_speed"] = 10

            legacy_controls = loaded.get(
                "mobile_controls", False
            )

            for key in (
                "left_button",
                "right_button",
                "fire_button",
            ):
                if key not in loaded:
                    merged[key] = legacy_controls

            self.settings = merged
            self.save()

            return self.settings

        except (json.JSONDecodeError, OSError, ValueError) as error:
            print(
                "[SettingsManager] Failed to load settings:",
                error
            )
            self.settings = DEFAULT_SETTINGS.copy()
            return self.settings

    def save(self):

        try:
            folder = os.path.dirname(self.path)

            if folder:
                os.makedirs(folder, exist_ok=True)

            with open(self.path, "w", encoding="utf-8") as file:
                json.dump(
                    self.settings,
                    file,
                    indent=4
                )

        except OSError as error:
            print(
                "[SettingsManager] Failed to save settings:",
                error
            )

    def get(self, key: str, default=None):
        return self.settings.get(key, default)

    def set(self, key: str, value):

        if key not in DEFAULT_SETTINGS:
            print(
                f"[SettingsManager] Unknown setting: {key}"
            )
            return

        valid_difficulties = (
            "easy", "normal", "hard"
        )

        if key in ("difficulty", "enemy_difficulty"):
            if value not in valid_difficulties:
                print(
                    "Difficulty must be easy, normal, or hard."
                )
                return

        if key == "player_speed":
            try:
                value = max(1, min(20, int(value)))
            except (TypeError, ValueError):
                return

        if key in (
            "screen_shake",
            "damage_effects",
            "show_fps",
            "fullscreen",
            "mobile_controls",
            "left_button",
            "right_button",
            "fire_button",
        ):
            value = bool(value)

        if key in ("sound_volume", "music_volume"):
            try:
                value = max(
                    0.0, min(1.0, float(value))
                )
            except (TypeError, ValueError):
                return

        self.settings[key] = value
        self.save()

    def reset_to_default(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.save()

    def get_all(self) -> dict:
        return self.settings.copy()


settings = SettingsManager()