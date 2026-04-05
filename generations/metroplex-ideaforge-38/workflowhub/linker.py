"""Link management logic for WorkflowHub (Feature 3)."""

import sys
from workflowhub.storage import item_exists, add_link, link_exists


def parse_artifact_ref(ref: str) -> tuple[str, str]:
    """
    Parse an artifact reference in TYPE:ID format.

    Args:
        ref: String in format TYPE:ID (e.g., 'slack:s1')

    Returns:
        Tuple of (type, id)

    Raises:
        ValueError if format is invalid
    """
    if ':' not in ref:
        raise ValueError(f"Invalid artifact reference format: '{ref}'. Expected TYPE:ID")

    parts = ref.split(':', 1)
    artifact_type = parts[0].strip()
    artifact_id = parts[1].strip()

    if not artifact_type or not artifact_id:
        raise ValueError(f"Invalid artifact reference format: '{ref}'. Expected TYPE:ID")

    return artifact_type, artifact_id


def create_link(source_ref: str, target_ref: str) -> str:
    """
    Create a bidirectional link between two artifacts.

    Args:
        source_ref: Source artifact in TYPE:ID format
        target_ref: Target artifact in TYPE:ID format

    Returns:
        Success message

    Raises:
        SystemExit on validation failures
    """
    # Parse references
    try:
        source_type, source_id = parse_artifact_ref(source_ref)
        target_type, target_id = parse_artifact_ref(target_ref)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Check for self-linking
    if source_type == target_type and source_id == target_id:
        print(f"Error: Cannot link an artifact to itself ({source_ref})")
        sys.exit(1)

    # Validate both artifacts exist
    if not item_exists(source_id, source_type):
        print(f"Error: Source artifact not found: {source_ref}")
        sys.exit(1)

    if not item_exists(target_id, target_type):
        print(f"Error: Target artifact not found: {target_ref}")
        sys.exit(1)

    # Check if link already exists
    if link_exists(source_type, source_id, target_type, target_id):
        print(f"Link already exists between {source_ref} and {target_ref}")
        return f"Link already exists between {source_ref} ←→ {target_ref}"

    # Create the bidirectional link
    add_link(source_type, source_id, target_type, target_id)

    return f"Linked {source_ref} ←→ {target_ref}"
