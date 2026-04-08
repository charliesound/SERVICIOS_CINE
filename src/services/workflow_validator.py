from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from .workflow_registry import workflow_registry


@dataclass
class ValidationError:
    field: str
    message: str
    severity: str


@dataclass
class ValidationResult:
    valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    workflow_key: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": [{"field": e.field, "message": e.message} for e in self.errors],
            "warnings": [{"field": w.field, "message": w.message} for w in self.warnings],
            "workflow_key": self.workflow_key
        }


class WorkflowValidator:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def validate(self, workflow: Dict[str, Any], strict: bool = True) -> ValidationResult:
        errors = []
        warnings = []

        if "workflow_key" not in workflow and "nodes" not in workflow:
            errors.append(ValidationError("root", "Workflow must have 'workflow_key' or 'nodes'", "error"))
            return ValidationResult(False, errors, warnings, None)

        workflow_key = workflow.get("workflow_key")

        if workflow_key:
            template = workflow_registry.get_workflow(workflow_key)
            if not template:
                errors.append(ValidationError("workflow_key", f"Unknown workflow: {workflow_key}", "error"))
                return ValidationResult(False, errors, warnings, workflow_key)

            nodes_errors, nodes_warnings = self._validate_nodes(workflow.get("nodes", []), template)
            errors.extend(nodes_errors)
            warnings.extend(nodes_warnings)

            missing_links = self._check_required_links(workflow, template)
            if missing_links:
                for link in missing_links:
                    errors.append(ValidationError(f"link:{link}", f"Missing required link: {link}", "error"))

        if not strict:
            critical_errors = [e for e in errors if e.severity == "error"]
            errors = critical_errors

        return ValidationResult(
            valid=len([e for e in errors if e.severity == "error"]) == 0,
            errors=errors,
            warnings=warnings,
            workflow_key=workflow_key
        )

    def _validate_nodes(self, nodes: List[Dict], template) -> Tuple[List[ValidationError], List[ValidationError]]:
        errors = []
        warnings = []

        if not nodes:
            errors.append(ValidationError("nodes", "Workflow must have at least one node", "error"))
            return errors, warnings

        output_found = False
        for node in nodes:
            if not node.get("type"):
                errors.append(ValidationError(f"node:{node.get('id')}", "Node missing 'type' field", "error"))
                continue

            if node.get("type") == "SaveImage" or node.get("type") == "SaveAnimatedWEBP" or node.get("type") == "SaveAudio":
                output_found = True

            required_missing = self._check_required_inputs(node, template)
            for missing in required_missing:
                warnings.append(ValidationError(f"node:{node.get('id')}", f"Recommended input '{missing}' not provided", "warning"))

        if not output_found:
            warnings.append(ValidationError("nodes", "No output node found (SaveImage/SaveAudio)", "warning"))

        return errors, warnings

    def _check_required_inputs(self, node: Dict, template) -> List[str]:
        missing = []
        template_nodes = {n.class_type: n for n in template.nodes}
        
        if node["type"] in template_nodes:
            required = template_nodes[node["type"]].required_inputs
            inputs = node.get("inputs", {})
            
            for req in required:
                if req not in inputs or inputs[req] is None:
                    if req not in ["model", "clip", "vae", "positive", "negative"]:
                        missing.append(req)

        return missing

    def _check_required_links(self, workflow: Dict, template) -> List[str]:
        missing = []
        
        return missing

    def validate_inputs(self, workflow_key: str, inputs: Dict[str, Any]) -> ValidationResult:
        template = workflow_registry.get_workflow(workflow_key)
        if not template:
            return ValidationResult(False, [
                ValidationError("workflow_key", f"Unknown workflow: {workflow_key}", "error")
            ], [], workflow_key)

        errors = []
        warnings = []

        for required in template.required_inputs:
            if required not in inputs or inputs[required] is None:
                errors.append(ValidationError(
                    f"input:{required}",
                    f"Required input '{required}' is missing",
                    "error"
                ))

        for optional in template.optional_inputs:
            if optional in inputs:
                value = inputs[optional]
                validation_error = self._validate_input_value(optional, value)
                if validation_error:
                    warnings.append(ValidationError(f"input:{optional}", validation_error, "warning"))

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            workflow_key=workflow_key
        )

    def _validate_input_value(self, input_name: str, value: Any) -> Optional[str]:
        if input_name == "seed" and value < 0:
            return "Seed must be >= 0"
        
        if input_name in ["width", "height"]:
            if value not in [256, 512, 768, 1024, 1536, 2048]:
                return f"{input_name} should be a standard resolution (256, 512, 768, 1024, 1536, 2048)"
        
        if input_name == "steps":
            if value < 1 or value > 100:
                return "Steps should be between 1 and 100"
        
        if input_name == "cfg":
            if value < 0 or value > 20:
                return "CFG should be between 0 and 20"
        
        return None

    def validate_backend_match(self, workflow: Dict[str, Any], backend: str) -> bool:
        workflow_backend = workflow.get("backend")
        if not workflow_backend:
            return True
        return workflow_backend == backend


validator = WorkflowValidator()
