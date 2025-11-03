"""Extract puzzle data from screenshots using GPT-4o-mini vision."""

import base64
import json
import io
import sys
from PIL import Image
from jsonschema import validate, ValidationError
from openai import OpenAI

# --- 1) JSON Schema ---
NYT_PIPS_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "NYT Pips Extraction",
    "type": "object",
    "additionalProperties": False,
    "required": ["valid_positions", "dominoes", "regions"],
    "properties": {
        "valid_positions": {
            "type": "array",
            "items": {"$ref": "#/$defs/Position"}
        },
        "dominoes": {
            "type": "array",
            "items": {
                "type": "array",
                "minItems": 2,
                "maxItems": 2,
                "items": {"type": "integer", "minimum": 0, "maximum": 6},
                "additionalItems": False
            }
        },
        "regions": {
            "type": "array",
            "items": {"$ref": "#/$defs/Region"}
        }
    },
    "$defs": {
        "Position": {
            "type": "object",
            "additionalProperties": False,
            "required": ["row", "col"],
            "properties": {
                "row": {"type": "integer", "minimum": 0},
                "col": {"type": "integer", "minimum": 0}
            }
        },
        "Constraint": {
            "type": "object",
            "additionalProperties": False,
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["none", "equal", "notequal", "greater_than", "less_than", "number"]
                }
            },
            "patternProperties": {
                "^value$": {"type": "integer", "minimum": 0}
            }
        },
        "Region": {
            "type": "object",
            "additionalProperties": False,
            "required": ["positions", "constraint"],
            "properties": {
                "positions": {
                    "type": "array",
                    "minItems": 1,
                    "items": {"$ref": "#/$defs/Position"}
                },
                "constraint": {"$ref": "#/$defs/Constraint"}
            }
        }
    }
}

SYSTEM_PROMPT = """You convert a single NYT Pips screenshot into structured JSON.
Rules:
- Output must be VALID JSON that matches the provided JSON schema.
- Use zero-based row/col indices.
- Extract all valid board cells, the domino tray tiles, and regions with constraints:
    - type "equal" when all pips in the cage are identical (no value field)
    - type "notequal" when all pips in the cage differ (no value field)
    - type "greater_than" (value is an integer threshold the cage sum must exceed)
    - type "less_than" (value is an integer threshold the cage sum must stay below)
    - type "number" (value is an integer that the cage sum must equal)
    - type "none" when no badge is present.
- If uncertain, pick the most likely interpretation and remain schema-valid."""


def load_image_as_data_url(path: str) -> str:
    """
    Load an image file and convert it to a base64 data URL.
    
    Args:
        path: Path to the image file
        
    Returns:
        Base64-encoded data URL string
    """
    # Optional: crop to board/tray beforehand to save tokens.
    with Image.open(path) as im:
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def call_model(image_data_url: str, prior_errors: str | None = None) -> dict:
    """
    Call GPT-4o-mini with JSON-schema enforcement.
    
    Args:
        image_data_url: Base64-encoded image data URL
        prior_errors: Optional error message from previous attempt to help model correct
        
    Returns:
        Extracted puzzle data as dictionary
        
    Raises:
        Exception: If API call fails or response cannot be parsed
    """
    client = OpenAI()  # uses OPENAI_API_KEY env var
    
    user_instructions = (
        "Extract the JSON for this puzzle." if not prior_errors
        else f"Your previous JSON failed these checks:\n{prior_errors}\n"
             "Return corrected JSON that satisfies the schema."
    )

    resp = client.chat.completions.create(
        model="gpt-4o-mini",  # vision-capable, inexpensive
        temperature=0,
        max_tokens=2000,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "nyt_pips_extraction",
                "strict": True,
                "schema": NYT_PIPS_SCHEMA
            },
        },
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_instructions},
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            },
        ],
    )

    # Parse the response. The SDK may expose either a parsed payload or raw text parts.
    message = resp.choices[0].message
    parsed = getattr(message, "parsed", None)
    if parsed is not None:
        return parsed

    content = message.content
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if not isinstance(part, dict):
                continue
            if part.get("type") in {"output_text", "text"} and "text" in part:
                text_parts.append(part["text"])
        content_text = "".join(text_parts)
    else:
        content_text = content or ""

    try:
        return json.loads(content_text)
    except json.JSONDecodeError as exc:  # pragma: no cover - depends on remote model output
        snippet = content_text[:1000]
        raise ValidationError(
            f"Model returned invalid JSON (pos {exc.pos}): {exc.msg}. Partial response: {snippet}"
        ) from exc


def semantic_validate(payload: dict):
    """
    Perform domain-specific validation beyond JSON Schema.
    
    Args:
        payload: Extracted puzzle data
        
    Raises:
        ValidationError: If semantic validation fails
    """
    # Ensure constraints have correct shape and semantics
    for r in payload.get("regions", []):
        c = r["constraint"]
        t = c.get("type")
        positions = r.get("positions", [])

        if t == "equal":
            if len(positions) < 2:
                raise ValidationError('Constraint "equal" must apply to at least two cells.')
            if "value" in c:
                raise ValidationError('Constraint "equal" must not include a value.')
        elif t == "notequal":
            if len(positions) < 2:
                raise ValidationError('Constraint "notequal" must apply to at least two cells.')
            if "value" in c:
                raise ValidationError('Constraint "notequal" must not include a value.')
        elif t in {"greater_than", "less_than", "number"}:
            if "value" not in c:
                raise ValidationError(f'Constraint "{t}" must include a value.')
            value = c["value"]
            if not isinstance(value, int) or value < 0:
                raise ValidationError(f'Constraint "{t}" value must be a non-negative integer.')
            if len(positions) < 1:
                raise ValidationError(f'Constraint "{t}" must apply to at least one cell.')
        elif t == "none":
            continue
        else:
            raise ValidationError(f'Unknown constraint type: {t}')


def extract_puzzle(path: str, retry: int = 1) -> dict:
    """
    Extract puzzle data from a screenshot.
    
    Args:
        path: Path to the screenshot image file
        retry: Number of retry attempts if validation fails
        
    Returns:
        Extracted puzzle data as dictionary
        
    Raises:
        ValidationError: If extraction fails after all retry attempts
    """
    img = load_image_as_data_url(path)
    last_err = None
    for attempt in range(retry + 1):
        try:
            data = call_model(img, prior_errors=str(last_err) if last_err else None)
        except ValidationError as e:
            last_err = e
            if attempt == retry:
                raise
            continue
        try:
            validate(instance=data, schema=NYT_PIPS_SCHEMA)  # structural
            semantic_validate(data)  # domain-specific
            return data
        except ValidationError as e:
            last_err = e
            if attempt == retry:
                raise


def main():
    """Command-line interface for puzzle extraction."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract NYT Pips puzzle data from screenshots using GPT-4o-mini",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pips-extract screenshot.png
  pips-extract puzzle.jpg > puzzle.json
  
Environment:
  OPENAI_API_KEY must be set to use this feature
        """
    )
    
    parser.add_argument(
        "screenshot",
        help="Path to screenshot image file (PNG, JPG, etc.)"
    )
    
    parser.add_argument(
        "-r", "--retry",
        type=int,
        default=1,
        help="Number of retry attempts if validation fails (default: 1)"
    )
    
    args = parser.parse_args()
    
    try:
        result = extract_puzzle(args.screenshot, retry=args.retry)
        print(json.dumps(result, indent=2, sort_keys=True))
    except FileNotFoundError:
        print(f"Error: File '{args.screenshot}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error extracting puzzle: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
