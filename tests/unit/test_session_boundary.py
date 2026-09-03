"""Synthetic deterministic tests for the coarse session-boundary identity.

No repository media fixtures. These tests exercise only the pure relative-path
derivation in ``session_boundary`` — no filesystem, no ffmpeg.
"""

from scripts.local_media_agent.session_boundary import (
    MEANINGFUL_RETENTION_DEPTH,
    coarse_session_id,
    meaningful_lineage,
)


class TestDifferentUpperLineageSameCardName:
    def test_different_upper_lineage_same_card_name(self):
        a = coarse_session_id("A/Campo/Tarjeta 1/M4ROOT/CLIP/a.mp4")
        b = coarse_session_id("B/Campo/Tarjeta 1/M4ROOT/CLIP/b.mp4")
        assert a == "A/Campo"
        assert b == "B/Campo"
        assert a != b


class TestGenericClipCollision:
    def test_generic_clip_collision(self):
        a = coarse_session_id("A/M4ROOT/CLIP/a.mp4")
        b = coarse_session_id("B/M4ROOT/CLIP/b.mp4")
        assert a == "A"
        assert b == "B"
        assert a != b


class TestSameLogicalSessionDifferentCard:
    def test_same_logical_session_different_card(self):
        card1 = coarse_session_id("A/Campo/Tarjeta 1/M4ROOT/CLIP/a.mp4")
        card2 = coarse_session_id("A/Campo/Tarjeta 2/M4ROOT/CLIP/b.mp4")
        assert card1 == card2 == "A/Campo"


class TestCameraAndExternalAudioSharedUpperSession:
    def test_camera_and_external_audio_shared_upper_session(self):
        cam = coarse_session_id("A/Interview/M4ROOT/CLIP/cam.mp4")
        wav = coarse_session_id("A/Interview/Audio/rec.wav")
        assert cam == wav == "A/Interview"


class TestShallowPathStableFallback:
    def test_bare_file_falls_back_to_stem(self):
        assert coarse_session_id("clip.mp4") == "clip"

    def test_shallow_nonempty(self):
        sid = coarse_session_id("clip.mp4")
        assert isinstance(sid, str)
        assert sid.strip() != ""

    def test_generic_only_shallow_falls_back_to_parent_chain(self):
        sid = coarse_session_id("M4ROOT/CLIP/clip.mp4")
        assert sid == "M4ROOT/CLIP"
        assert sid.strip() != ""

    def test_card_only_shallow(self):
        assert coarse_session_id("Tarjeta 1/clip.mp4") == "Tarjeta 1"


class TestCaseVariantGenericComponents:
    def test_case_variant_generic_components(self):
        assert coarse_session_id("A/m4root/clip/a.mp4") == "A"
        assert coarse_session_id("A/M4ROOT/CLIP/a.mp4") == "A"


class TestDeterministicId:
    def test_deterministic_across_calls(self):
        paths = [
            "A/Campo/Tarjeta 1/M4ROOT/CLIP/a.mp4",
            "Mariano/Campo/Tarjeta 2/M4ROOT/CLIP/b.mp4",
            "M4ROOT/CLIP/clip.mp4",
            "solo.wav",
        ]
        for p in paths:
            first = coarse_session_id(p)
            for _ in range(5):
                assert coarse_session_id(p) == first


class TestAbsoluteRootNotPartOfId:
    def test_drive_letter_prefix_stripped(self):
        bare = coarse_session_id("A/Campo/Tarjeta 1/M4ROOT/CLIP/a.mp4")
        with_drive = coarse_session_id("F:/A/Campo/Tarjeta 1/M4ROOT/CLIP/a.mp4")
        with_drive_windows = coarse_session_id("F:\\A\\Campo\\Tarjeta 1\\M4ROOT\\CLIP\\a.mp4")
        assert with_drive == bare
        assert with_drive_windows == bare

    def test_unc_prefix_stripped(self):
        bare = coarse_session_id("A/Campo/Tarjeta 1/M4ROOT/CLIP/a.mp4")
        with_unc = coarse_session_id("//server/share/A/Campo/Tarjeta 1/M4ROOT/CLIP/a.mp4")
        assert with_unc == bare


class TestExpectedBehavior:
    def test_meaningful_lineage(self):
        assert meaningful_lineage("Pruden/Campo/Tarjeta 1/M4ROOT/CLIP/A.mp4") == [
            "Pruden",
            "Campo",
        ]
        assert meaningful_lineage("Pruden/Entrevista/Audio/REC001.wav") == [
            "Pruden",
            "Entrevista",
            "Audio",
        ]

    def test_retention_depth_constant(self):
        assert MEANINGFUL_RETENTION_DEPTH == 2

    def test_three_person_example_never_collapses(self):
        ids = {
            "Pruden": coarse_session_id("Pruden/Campo/Tarjeta 1/M4ROOT/CLIP/A.mp4"),
            "Mariano": coarse_session_id("Mariano/Campo/Tarjeta 1/M4ROOT/CLIP/B.mp4"),
            "Kiko": coarse_session_id("Kiko Traza/Campo/Tarjeta 1/M4ROOT/CLIP/C.mp4"),
        }
        assert len(set(ids.values())) == 3
