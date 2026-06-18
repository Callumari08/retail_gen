import json
import mimetypes
import os
import time
from urllib.parse import urlparse
from urllib.request import urlopen
from pathlib import Path
from typing import Any

import google.auth
from google import genai
from google.genai import types


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


def _load_reference_image(image_link: str) -> types.Image:
  if not image_link.strip():
    raise ValueError("Product image_link is empty.")

  with urlopen(image_link) as response:
    image_bytes = response.read()
    mime_type = response.headers.get_content_type()

  if not image_bytes:
    raise ValueError(f"Product image_link returned no data: {image_link}")

  if not mime_type or mime_type == "application/octet-stream":
    guessed_mime_type, _ = mimetypes.guess_type(urlparse(image_link).path)
    mime_type = guessed_mime_type

  if not mime_type or not mime_type.startswith("image/"):
    raise ValueError(
      f"Could not determine an image MIME type for product image_link: {image_link}"
    )

  return types.Image(image_bytes=image_bytes, mime_type=mime_type)


class VeoVideoGen:
  def __init__(self, api_key_path: str):
    api_key_path = Path(api_key_path)
    client_options = _load_client_options(api_key_path)
    self.client = genai.Client(**client_options)

  def prompt_video_gen(self, prompt: str, title: str, image_link: str):
    reference_image = _load_reference_image(image_link)
    operation = self.client.models.generate_videos(
      model="veo-3.1-generate-001",
      source=types.GenerateVideosSource(prompt=prompt),
      config=types.GenerateVideosConfig(
        reference_images=[
          types.VideoGenerationReferenceImage(
            image=reference_image,
            reference_type=types.VideoGenerationReferenceType.ASSET,
          )
        ]
      ),
    )

    print("Waiting for video to generate (1-2 mins)", end="")
    while not operation.done:
      print(".", end="", flush=True)
      time.sleep(5)
      operation = self.client.operations.get(operation)

    result = operation.result or operation.response
    if result is None:
      raise ValueError("\nVideo generation completed without a result payload.")

    generated_videos = result.generated_videos
    if not generated_videos:
      filtered_count = result.rai_media_filtered_count or 0
      filtered_reasons = result.rai_media_filtered_reasons or []
      if filtered_count:
        raise ValueError(
          "\nVideo generation completed, but all outputs were filtered by "
          f"Google safety checks. Reasons: {', '.join(filtered_reasons) or 'unknown'}"
        )

      raise ValueError(
        "\nVideo generation completed without any generated videos."
      )

    generated_video = generated_videos[0]
    if generated_video.video is None:
      raise ValueError("\nVideo generation completed without returning a video.")
    if generated_video.video.video_bytes is None:
      raise ValueError(
        "\nGenerated video did not include downloadable bytes."
      )

    generated_video.video.save(f"{title}.mp4")
    print(f" Complete!\nGenerated Video Saved As: {title}.mp4")    
  
