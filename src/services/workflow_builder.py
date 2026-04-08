from typing import Dict, List, Optional, Any
from copy import deepcopy

from .workflow_registry import workflow_registry, WorkflowTemplate, TaskCategory


class WorkflowBuilder:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def build_workflow(self, workflow_key: str, inputs: Dict[str, Any], 
                       overrides: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        template = workflow_registry.get_workflow(workflow_key)
        if not template:
            return None

        workflow = {
            "nodes": [],
            "links": [],
            "version": "1.0",
            "workflow_key": workflow_key,
            "category": template.category.value,
            "backend": template.backend
        }

        nodes_map = {}

        for node in template.nodes:
            node_dict = self._build_node(node, inputs, nodes_map)
            if node_dict:
                workflow["nodes"].append(node_dict)
                nodes_map[node.node_id] = node_dict

        self._finalize_links(workflow, nodes_map)

        if overrides:
            self._apply_overrides(workflow, overrides)

        return workflow

    def _build_node(self, node, inputs: Dict[str, Any], nodes_map: Dict) -> Optional[Dict[str, Any]]:
        node_dict = {
            "id": node.node_id,
            "type": node.class_type,
            "pos": [0, 0],
            "size": [320, 240],
            "flags": {},
            "order": 0,
            "mode": 0,
            "inputs": {},
            "outputs": {},
            "properties": {},
            "widgets_values": []
        }

        for input_name in node.required_inputs:
            value = inputs.get(input_name)
            if value is not None:
                node_dict["inputs"][input_name] = self._resolve_input(value, input_name, nodes_map)
            elif input_name in ["prompt", "text"]:
                node_dict["inputs"][input_name] = inputs.get("prompt", "") or inputs.get("text", "")

        for input_name in node.optional_inputs:
            value = inputs.get(input_name)
            if value is not None:
                node_dict["inputs"][input_name] = self._resolve_input(value, input_name, nodes_map)

        return node_dict

    def _resolve_input(self, value: Any, input_name: str, nodes_map: Dict) -> Any:
        if input_name == "clip" and isinstance(value, list):
            node_id, output_idx = value
            if node_id in nodes_map:
                return {"name": "clip", "slot_index": output_idx, "link": None}
        
        if input_name == "model" and isinstance(value, list):
            node_id, output_idx = value
            if node_id in nodes_map:
                return {"name": "model", "slot_index": output_idx, "link": None}
        
        if input_name == "vae" and isinstance(value, list):
            node_id, output_idx = value
            if node_id in nodes_map:
                return {"name": "vae", "slot_index": output_idx, "link": None}
        
        return value

    def _finalize_links(self, workflow: Dict, nodes_map: Dict):
        links = []
        link_id = 1

        for node in workflow["nodes"]:
            for input_name, input_val in node.get("inputs", {}).items():
                if isinstance(input_val, dict) and "link" in input_val:
                    for target_node in workflow["nodes"]:
                        if target_node["id"] == node["id"]:
                            continue
                        for out_name in ["model", "clip", "vae", "samples", "images", "audio", "text"]:
                            if out_name in target_node.get("outputs", {}):
                                pass

        workflow["links"] = links

    def _apply_overrides(self, workflow: Dict, overrides: Dict[str, Any]):
        for node in workflow["nodes"]:
            for key, value in overrides.items():
                if key in node.get("inputs", {}):
                    node["inputs"][key] = value
                if key in node.get("widgets_values", []):
                    idx = node["widgets_values"].index(key)
                    if idx + 1 < len(node["widgets_values"]):
                        node["widgets_values"][idx + 1] = value

    def build_from_intent(self, intent: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        from .workflow_planner import planner
        
        analysis = planner.analyze_intent(intent, context)
        
        if not analysis.detected_workflow:
            return None
        
        if analysis.missing_inputs:
            return {
                "error": "missing_inputs",
                "missing": analysis.missing_inputs,
                "analysis": {
                    "task_type": analysis.task_type,
                    "backend": analysis.backend,
                    "confidence": analysis.confidence,
                    "reasoning": analysis.reasoning
                }
            }
        
        merged_inputs = {**context, **analysis.suggested_params}
        
        return self.build_workflow(analysis.detected_workflow, merged_inputs)

    def clone_workflow(self, workflow_key: str, new_name: str) -> Optional[Dict[str, Any]]:
        template = workflow_registry.get_workflow(workflow_key)
        if not template:
            return None
        
        return {
            "nodes": deepcopy(template.nodes),
            "version": "1.0",
            "workflow_key": f"{workflow_key}_custom",
            "name": new_name,
            "category": template.category.value,
            "backend": template.backend,
            "custom": True
        }

    def get_workflow_preview(self, workflow_key: str) -> Optional[Dict[str, Any]]:
        template = workflow_registry.get_workflow(workflow_key)
        if not template:
            return None
        
        return {
            "key": template.key,
            "name": template.name,
            "description": template.description,
            "required_inputs": template.required_inputs,
            "optional_inputs": template.optional_inputs,
            "nodes_count": len(template.nodes),
            "node_types": [n.class_type for n in template.nodes],
            "tags": template.tags
        }


builder = WorkflowBuilder()
