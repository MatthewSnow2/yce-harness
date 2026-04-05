"""JSON file import logic for WorkflowHub."""

import json
from pathlib import Path
from datetime import datetime
from typing import Tuple
from workflowhub.storage import init_db, insert_item


def validate_timestamp(timestamp_str: str) -> str:
    """
    Validate and normalize timestamp string.

    Handles 'Z' suffix by replacing with '+00:00' for ISO format compatibility.
    Returns normalized timestamp string.
    Raises ValueError if invalid.
    """
    # Replace 'Z' with '+00:00' for ISO format compatibility
    normalized = timestamp_str.replace('Z', '+00:00')

    # Validate by parsing
    try:
        datetime.fromisoformat(normalized)
        return normalized
    except ValueError as e:
        raise ValueError(f"Invalid timestamp format: {timestamp_str}") from e


def import_artifacts(directory: str) -> Tuple[int, int, int]:
    """
    Import artifacts from JSON files in the specified directory.

    Returns tuple: (imported_count, skipped_count, failed_count)
    """
    # Initialize database if needed
    init_db()

    imported = 0
    skipped = 0
    failed = 0

    # Find all JSON files in directory
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"Error: Directory '{directory}' does not exist")
        return (0, 0, 0)

    json_files = list(dir_path.glob("*.json"))
    if not json_files:
        print(f"Warning: No JSON files found in '{directory}'")
        return (0, 0, 0)

    # Process each JSON file
    for json_file in json_files:
        try:
            # Read and parse JSON file
            with open(json_file, 'r', encoding='utf-8') as f:
                artifacts = json.load(f)

            # Ensure it's a list
            if not isinstance(artifacts, list):
                print(f"Warning: {json_file.name} does not contain a JSON array, skipping")
                continue

            # Process each artifact
            for artifact in artifacts:
                try:
                    # Validate required fields
                    if not isinstance(artifact, dict):
                        failed += 1
                        continue

                    artifact_id = artifact.get('id')
                    artifact_type = artifact.get('type')
                    timestamp = artifact.get('timestamp')

                    if not artifact_id or not artifact_type or not timestamp:
                        failed += 1
                        continue

                    # Validate and normalize timestamp
                    try:
                        normalized_timestamp = validate_timestamp(timestamp)
                    except ValueError:
                        failed += 1
                        continue

                    # Get optional content field
                    content = artifact.get('content', '')

                    # Try to insert
                    if insert_item(artifact_id, artifact_type, content, normalized_timestamp):
                        imported += 1
                    else:
                        skipped += 1

                except Exception as e:
                    # Individual artifact processing error
                    failed += 1

        except UnicodeDecodeError:
            print(f"Error: {json_file.name} has encoding issues (must be UTF-8)")
            failed += 1
        except json.JSONDecodeError:
            print(f"Error: {json_file.name} is not valid JSON")
            failed += 1
        except Exception as e:
            print(f"Error processing {json_file.name}: {e}")
            failed += 1

    return (imported, skipped, failed)
