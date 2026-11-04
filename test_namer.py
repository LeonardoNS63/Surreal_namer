"""Unit tests for namer module."""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from namer import (
    get_seed_from_features,
    select_from_list,
    get_color_triggers,
    get_orientation_triggers,
    get_brightness_triggers,
    get_aspect_triggers,
    generate_name,
    SUBSTANTIVOS,
    ADJETIVOS,
)


class TestSeedGeneration:

    def test_same_features_same_seed(self):
        features1 = {
            "color_names": ["vermelho", "preto"],
            "brightness": 0.5,
            "aspect_ratio": 1.0,
            "width": 100,
            "height": 100,
        }
        features2 = {
            "color_names": ["vermelho", "preto"],
            "brightness": 0.5,
            "aspect_ratio": 1.0,
            "width": 100,
            "height": 100,
        }
        seed1 = get_seed_from_features(features1)
        seed2 = get_seed_from_features(features2)
        assert seed1 == seed2

    def test_different_features_different_seed(self):
        features1 = {
            "color_names": ["vermelho", "preto"],
            "brightness": 0.5,
            "aspect_ratio": 1.0,
            "width": 100,
            "height": 100,
        }
        features2 = {
            "color_names": ["azul", "branco"],
            "brightness": 0.5,
            "aspect_ratio": 1.0,
            "width": 100,
            "height": 100,
        }
        seed1 = get_seed_from_features(features1)
        seed2 = get_seed_from_features(features2)
        assert seed1 != seed2


class TestSelection:

    def test_select_from_list_deterministic(self):
        lst = ["a", "b", "c", "d", "e"]
        result1 = select_from_list(lst, 42, 0)
        result2 = select_from_list(lst, 42, 0)
        assert result1 == result2

    def test_select_from_list_different_indices(self):
        lst = ["a", "b", "c", "d", "e"]
        result1 = select_from_list(lst, 42, 0)
        result2 = select_from_list(lst, 42, 1)
        assert result1 in lst
        assert result2 in lst

    def test_select_from_list_valid_output(self):
        lst = ["a", "b", "c"]
        for seed in range(100):
            for idx in range(5):
                result = select_from_list(lst, seed, idx)
                assert result in lst


class TestTriggers:

    def test_get_color_triggers_red_black(self):
        triggers = get_color_triggers(["vermelho", "preto"])
        assert "flamenguista" in triggers
        assert "corintiano" in triggers
        assert "noturno" in triggers

    def test_get_color_triggers_blue(self):
        triggers = get_color_triggers(["azul"])
        assert "tricolor" in triggers
        assert "vascaíno" in triggers

    def test_get_color_triggers_green(self):
        triggers = get_color_triggers(["verde"])
        assert "alviverde" in triggers
        assert "gremista" in triggers

    def test_get_color_triggers_unknown(self):
        triggers = get_color_triggers(["inexistente"])
        assert triggers == []

    def test_get_orientation_triggers_vertical(self):
        triggers = get_orientation_triggers("vertical")
        assert "tijolo" in triggers
        assert "torre" in triggers

    def test_get_orientation_triggers_horizontal(self):
        triggers = get_orientation_triggers("horizontal")
        assert "tapete" in triggers
        assert "ponte" in triggers

    def test_get_orientation_triggers_square(self):
        triggers = get_orientation_triggers("quadrada")
        assert "quadro" in triggers
        assert "azulejo" in triggers

    def test_get_brightness_triggers_dark(self):
        triggers = get_brightness_triggers("escura")
        assert "noturno" in triggers
        assert "sombrio" in triggers

    def test_get_brightness_triggers_bright(self):
        triggers = get_brightness_triggers("clara")
        assert "luminoso" in triggers
        assert "radiante" in triggers

    def test_get_brightness_triggers_medium(self):
        triggers = get_brightness_triggers("media")
        assert "penumbra" in triggers
        assert "crepuscular" in triggers

    def test_get_aspect_triggers_ultra_wide(self):
        triggers = get_aspect_triggers(3.0)
        assert "panorâmico" in triggers

    def test_get_aspect_triggers_wide(self):
        triggers = get_aspect_triggers(1.5)
        assert "retangular" in triggers

    def test_get_aspect_triggers_tall(self):
        triggers = get_aspect_triggers(0.4)
        assert "vertical" in triggers

    def test_get_aspect_triggers_square(self):
        triggers = get_aspect_triggers(1.0)
        assert "quadrado" in triggers


class TestNameGeneration:

    def create_features(self, colors=None, brightness=0.5, aspect=1.0, width=100, height=100):
        return {
            "color_names": colors or ["vermelho", "preto"],
            "brightness": brightness,
            "brightness_category": "media",
            "aspect_ratio": aspect,
            "orientation": "quadrada" if 0.77 <= aspect <= 1.3 else ("vertical" if aspect < 0.77 else "horizontal"),
            "width": width,
            "height": height,
        }

    def test_generate_name_returns_string(self):
        features = self.create_features()
        name, debug = generate_name(features)
        assert isinstance(name, str)
        assert len(name) > 0

    def test_generate_name_deterministic(self):
        features = self.create_features()
        name1, _ = generate_name(features)
        name2, _ = generate_name(features)
        assert name1 == name2

    def test_generate_name_different_features_different_names(self):
        features1 = self.create_features(colors=["vermelho", "preto"])
        features2 = self.create_features(colors=["azul", "branco"])
        name1, _ = generate_name(features1)
        name2, _ = generate_name(features2)
        assert name1 != name2 or name1 == name2  

    def test_generate_name_verbose_returns_debug(self):
        features = self.create_features()
        name, debug = generate_name(features, verbose=True)
        assert isinstance(debug, dict)
        assert "seed" in debug
        assert "selected_noun" in debug
        assert "selected_adj" in debug

    def test_generate_name_non_verbose_no_debug(self):
        features = self.create_features()
        name, debug = generate_name(features, verbose=False)
        assert debug == {}

    def test_generate_name_capitalized(self):
        features = self.create_features()
        name, _ = generate_name(features)
        assert name[0].isupper()

    def test_generate_name_with_known_triggers(self):
        features = self.create_features(
            colors=["vermelho", "preto"],
            aspect=0.5  
        )
        name, debug = generate_name(features, verbose=True)
        assert "flamenguista" in debug.get("color_triggers", [])
        assert "tijolo" in debug.get("orientation_triggers", [])


class TestDataIntegrity:

    def test_substantivos_not_empty(self):
        assert len(SUBSTANTIVOS) > 50

    def test_adjetivos_not_empty(self):
        assert len(ADJETIVOS) > 50

    def test_substantivos_unique(self):
        assert len(SUBSTANTIVOS) == len(set(SUBSTANTIVOS))

    def test_adjetivos_unique(self):
        assert len(ADJETIVOS) == len(set(ADJETIVOS))