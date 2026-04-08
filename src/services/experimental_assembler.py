from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum


class NodeCategory(Enum):
    LOADER = "loader"
    SAMPLING = "sampling"
    LATENT = "latent"
    IO = "io"
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    CONDITIONING = "conditioning"


@dataclass
class ModuleDefinition:
    module_id: str
    name: str
    category: NodeCategory
    node_type: str
    inputs: Dict[str, Any]
    outputs: List[str]
    position: int
    dependencies: List[str]


@dataclass
class AssemblyResult:
    success: bool
    workflow: Optional[Dict[str, Any]]
    warnings: List[str]
    errors: List[str]
    node_count: int
    total_inputs: int


class ModuleRegistry:
    """Registry of available optional modules."""
    
    MODULES: Dict[str, ModuleDefinition] = {
        "upscale_2x": ModuleDefinition(
            module_id="upscale_2x",
            name="Upscale 2x",
            category=NodeCategory.IMAGE,
            node_type="ImageUpscaleWithModel",
            inputs={"model_name": "real-esrgan-2x.pth"},
            outputs=["IMAGE"],
            position=999,
            dependencies=["image_output"]
        ),
        "face_detail": ModuleDefinition(
            module_id="face_detail",
            name="Face Detail Restoration",
            category=NodeCategory.IMAGE,
            node_type="FaceDetailer",
            inputs={"strength": 0.8},
            outputs=["IMAGE"],
            position=998,
            dependencies=["image_output"]
        ),
        "color_correct": ModuleDefinition(
            module_id="color_correct",
            name="Color Correction",
            category=NodeCategory.IMAGE,
            node_type="ColorCorrect",
            inputs={"brightness": 1.0, "contrast": 1.0},
            outputs=["IMAGE"],
            position=997,
            dependencies=["image_output"]
        ),
        "style_transfer": ModuleDefinition(
            module_id="style_transfer",
            name="Style Transfer",
            category=NodeCategory.IMAGE,
            node_type="StyleTransfer",
            inputs={"style": "cinematic"},
            outputs=["IMAGE"],
            position=996,
            dependencies=["image_output"]
        ),
        "video_interpolation": ModuleDefinition(
            module_id="video_interpolation",
            name="Video Interpolation",
            category=NodeCategory.VIDEO,
            node_type="RIFE",
            inputs={"fps_multiply": 2},
            outputs=["VIDEO"],
            position=995,
            dependencies=["video_output"]
        ),
        "video_stabilize": ModuleDefinition(
            module_id="video_stabilize",
            name="Video Stabilization",
            category=NodeCategory.VIDEO,
            node_type="VideoStabilize",
            inputs={},
            outputs=["VIDEO"],
            position=994,
            dependencies=["video_output"]
        ),
        "audio_enhance": ModuleDefinition(
            module_id="audio_enhance",
            name="Audio Enhancement",
            category=NodeCategory.AUDIO,
            node_type="AudioEnhance",
            inputs={"denoise": 0.3},
            outputs=["AUDIO"],
            position=993,
            dependencies=["audio_output"]
        ),
        "bg_remove": ModuleDefinition(
            module_id="bg_remove",
            name="Background Removal",
            category=NodeCategory.IMAGE,
            node_type="RemBg",
            inputs={"model": "u2net"},
            outputs=["IMAGE"],
            position=995,
            dependencies=["image_output"]
        ),
    }

    @classmethod
    def get_module(cls, module_id: str) -> Optional[ModuleDefinition]:
        return cls.MODULES.get(module_id)

    @classmethod
    def get_modules_by_category(cls, category: NodeCategory) -> List[ModuleDefinition]:
        return [m for m in cls.MODULES.values() if m.category == category]

    @classmethod
    def list_modules(cls) -> List[Dict[str, Any]]:
        return [
            {
                "module_id": m.module_id,
                "name": m.name,
                "category": m.category.value,
                "dependencies": m.dependencies
            }
            for m in cls.MODULES.values()
        ]


class ExperimentalWorkflowAssembler:
    """
    Prototype for semi-automatic workflow assembly.
    ALPHA - Not for production use.
    """
    
    MAX_NODES = 50
    MAX_MODULES = 5
    
    def __init__(self):
        self.module_registry = ModuleRegistry()
    
    def assemble(
        self,
        base_workflow_key: str,
        modules: List[str],
        options: Optional[Dict[str, Any]] = None
    ) -> AssemblyResult:
        """
        Assemble a workflow with optional modules.
        
        Args:
            base_workflow_key: Base workflow to extend
            modules: List of module IDs to add
            options: Optional configuration
            
        Returns:
            AssemblyResult with workflow or errors
        """
        warnings = []
        errors = []
        
        if len(modules) > self.MAX_MODULES:
            errors.append(f"Too many modules. Max: {self.MAX_MODULES}")
            return AssemblyResult(False, None, warnings, errors, 0, 0)
        
        if not modules:
            errors.append("No modules specified")
            return AssemblyResult(False, None, warnings, errors, 0, 0)
        
        selected_modules = []
        for module_id in modules:
            module = self.module_registry.get_module(module_id)
            if not module:
                errors.append(f"Unknown module: {module_id}")
                continue
            selected_modules.append(module)
        
        if errors:
            return AssemblyResult(False, None, warnings, errors, 0, 0)
        
        if not self._validate_dependencies(selected_modules):
            errors.append("Module dependencies not satisfied")
            return AssemblyResult(False, None, warnings, errors, 0, 0)
        
        workflow = self._build_workflow(base_workflow_key, selected_modules, options or {})
        
        validation_errors = self._validate_graph(workflow)
        if validation_errors:
            errors.extend(validation_errors)
        
        warnings.append("EXPERIMENTAL: This feature is in alpha testing")
        warnings.append("Do not use in production environments")
        
        return AssemblyResult(
            success=len(errors) == 0,
            workflow=workflow if len(errors) == 0 else None,
            warnings=warnings,
            errors=errors,
            node_count=len(workflow.get("nodes", [])),
            total_inputs=len(workflow.get("inputs", {}))
        )
    
    def _validate_dependencies(self, modules: List[ModuleDefinition]) -> bool:
        required_outputs = set()
        provided_outputs = {"image_output", "video_output", "audio_output"}
        
        for module in modules:
            required_outputs.update(module.dependencies)
        
        return required_outputs.issubset(provided_outputs)
    
    def _build_workflow(
        self,
        base_key: str,
        modules: List[ModuleDefinition],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        modules_sorted = sorted(modules, key=lambda m: m.position)
        
        workflow = {
            "version": "0.1.0-alpha",
            "experimental": True,
            "base_workflow": base_key,
            "modules": [m.module_id for m in modules_sorted],
            "nodes": [],
            "links": [],
            "metadata": {
                "assembler_version": "0.1.0",
                "nodes_count": len(modules_sorted) + 3,
                "created_at": "auto"
            }
        }
        
        workflow["nodes"].append({
            "id": "base_loader",
            "type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "sdxl_base.safetensors"}
        })
        
        for module in modules_sorted:
            node = {
                "id": f"module_{module.module_id}",
                "type": module.node_type,
                "inputs": {**module.inputs, **options.get(module.module_id, {})},
                "category": module.category.value,
                "module": True
            }
            workflow["nodes"].append(node)
        
        workflow["nodes"].append({
            "id": "output",
            "type": "SaveImage",
            "inputs": {"filename_prefix": "experimental"}
        })
        
        return workflow
    
    def _validate_graph(self, workflow: Dict[str, Any]) -> List[str]:
        errors = []
        
        if len(workflow.get("nodes", [])) > self.MAX_NODES:
            errors.append(f"Too many nodes. Max: {self.MAX_NODES}")
        
        node_types = [n.get("type") for n in workflow.get("nodes", [])]
        if node_types.count("SaveImage") > 3:
            errors.append("Too many output nodes")
        
        return errors
    
    def get_available_modules(self) -> List[Dict[str, Any]]:
        return self.module_registry.list_modules()
    
    def get_module_info(self, module_id: str) -> Optional[Dict[str, Any]]:
        module = self.module_registry.get_module(module_id)
        if not module:
            return None
        
        return {
            "module_id": module.module_id,
            "name": module.name,
            "category": module.category.value,
            "node_type": module.node_type,
            "inputs": module.inputs,
            "outputs": module.outputs,
            "dependencies": module.dependencies
        }


assembler = ExperimentalWorkflowAssembler()
