import unittest
from unittest.mock import MagicMock, patch
from src.services.render_context_preparer import RenderContextPreparer
from src.settings import settings

class TestRenderContextPreparer(unittest.TestCase):
    def setUp(self):
        self.mock_storage = MagicMock()
        self.preparer = RenderContextPreparer(self.mock_storage)
        # Aseguramos un estado conocido para los tests
        self.original_flag = settings.enable_render_context_flags
        settings.enable_render_context_flags = True

    def tearDown(self):
        settings.enable_render_context_flags = self.original_flag

    def test_prepare_payload_no_flag(self):
        settings.enable_render_context_flags = False
        payload = {"1": {"class_type": "KSampler", "inputs": {"model": "model_link"}}}
        result = self.preparer.prepare_payload(payload, {"character_id": "test"})
        self.assertEqual(result, payload)

    def test_prepare_payload_with_character(self):
        # Mock de personaje con imagen de referencia
        self.mock_storage.get_active_storage_character.return_value = {
            "character_id": "char_1",
            "reference_images": ["char_1_ref.jpg"]
        }
        
        payload = {
            "10": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["4", 0],
                    "positive": ["5", 0],
                    "negative": ["6", 0],
                    "latent_image": ["7", 0]
                }
            },
            "4": {"class_type": "CheckpointLoaderSimple"},
        }
        
        context = {"character_id": "char_1", "use_ipadapter": True}
        result = self.preparer.prepare_payload(payload, context)
        
        # Verificar que se inyectaron los nuevos nodos
        # El ID inicial debería ser 11 (max(10, 4) + 1)
        self.assertIn("11", result) # LoadImage
        self.assertIn("12", result) # CLIPVision
        self.assertIn("13", result) # IPAdapterModel
        self.assertIn("14", result) # Apply IPAdapter
        
        # Verificar conexiones
        self.assertEqual(result["14"]["inputs"]["model"], ["4", 0])
        self.assertEqual(result["10"]["inputs"]["model"], ["14", 0])
        self.assertEqual(result["11"]["inputs"]["image"], "char_1_ref.jpg")

    def test_prepare_payload_fallback_on_error(self):
        # Provocar un error en el preparador (ej. payload inválido)
        payload = "not a dict"
        result = self.preparer.prepare_payload(payload, {"character_id": "test"})
        # Debe devolver el original sin explotar
        self.assertEqual(result, payload)

if __name__ == "__main__":
    unittest.main()
