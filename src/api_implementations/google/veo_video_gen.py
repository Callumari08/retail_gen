import json
import os
import time
from pathlib import Path
from typing import Any

import google.auth
from google import genai


def _load_client_options(api_key_path: Path) -> dict[str, Any]:
  raw_value = api_key_path.read_text(encoding="utf-8").strip()

  if not raw_value:
    raise ValueError(f"Google API key file is empty: {api_key_path}")

  try:
    parsed_value = json.loads(raw_value)
  except json.JSONDecodeError:
    return {"api_key": raw_value}

  if isinstance(parsed_value, str):
    api_key = parsed_value.strip()
    if api_key:
      return {"api_key": api_key}
  elif isinstance(parsed_value, dict):
    api_key = parsed_value.get("api_key") or parsed_value.get("key")
    if isinstance(api_key, str) and api_key.strip():
      return {"api_key": api_key.strip()}

    if {
      "type",
      "private_key",
      "client_email",
    }.issubset(parsed_value):
      credentials, project_id = google.auth.load_credentials_from_file(
        str(api_key_path),
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
      )

      resolved_project = (
        project_id
        or parsed_value.get("project_id")
        or os.environ.get("GOOGLE_CLOUD_PROJECT")
      )
      if not resolved_project:
        raise ValueError(
          "Service account JSON is missing a project id. Add project_id to "
          "the credential file or set GOOGLE_CLOUD_PROJECT."
        )

      resolved_location = (
        parsed_value.get("location")
        or os.environ.get("GOOGLE_CLOUD_LOCATION")
        or "us-central1"
      )

      return {
        "vertexai": True,
        "credentials": credentials,
        "project": resolved_project,
        "location": resolved_location,
      }

  raise ValueError(
    f"Google API key file has an unsupported format: {api_key_path}"
  )


class VeoVideoGen:
  def __init__(self, api_key_path: str):
    api_key_path = Path(api_key_path)
    client_options = _load_client_options(api_key_path)
    self.client = genai.Client(**client_options)

  def prompt_video_gen(self, prompt: str, title: str):
    operation = self.client.models.generate_videos(
      model="veo-3.1-generate-001",
      prompt=prompt,
    )

    print("Waiting for video to generate (1-2 mins)", end="")
    while not operation.done:
      print(".", end="")
      time.sleep(5)
      operation = self.client.operations.get(operation)

    generated_video = operation.response.generated_videos[0]
    if generated_video.video is None:
      raise ValueError("\nVideo generation completed without returning a video.")
    if generated_video.video.video_bytes is None:
      raise ValueError(
        "\nGenerated video did not include downloadable bytes."
      )

    generated_video.video.save(f"{title}.mp4")
    print(f" Complete!\nGenerated Video Saved As: {title}.mp4")    
  
