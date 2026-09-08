---
name: modelark-mcp
description: Guide for using the ModelArk Seed Multimodal MCP server to generate or edit images, audio, video, and 3D models (including Seedance 2.5, Hyper3D, Hitem3d, BytePlus VOD AI MediaKit enhancement, video transcoding, and voice/background audio separation), understand images and videos through Seed 2.1, transcribe speech to text, manage Seedance and 3D tasks, upload reference media, and fetch persisted artifacts.
---

# ModelArk multimodal tools

Use the available MCP tools for durable image, audio, video, 3D, understanding,
transcription and VOD processing. Discover tool names and input schemas at
runtime. Resolve the selected model/operation and supported reference roles
before submitting; examples below are dated guidance, not capability evidence.

## Shared execution contract

- Freeze exact prompt bytes and a prepared operation before submission. Record
  returned provider IDs immediately in the single project task registry.
- Unknown acceptance after timeout means submission_unknown. Reconcile before
  any retry or transport fallback; known task IDs resume polling.
- Preserve provider completion separately from user review/approval.
- Download every generated modality to its project-local path and record the
  hash, bytes, artifact ID, actual streams and usage. Durable URIs supplement
  the local asset. Download failure retries artifact retrieval, not generation.
- Use environment-resolved credentials. Keep secrets and signed URLs out of
  durable request identity. Reference-cache identity is content hash plus
  storage scope; expired URLs need presigning, missing objects may need upload.
- Cleanup/cancel/delete requires explicit user scope. Provider success or age
  alone never authorizes cleanup.
- Confirm model limits, prices and tool aliases against live evidence before
  generation. Do not pass unsupported flags or change models silently.
- Keep estimated cost, confirmed billing and provider usage separate.

## Load the relevant mode

Read only the reference for the requested tool family. For a submission or
recovery, also read generation workflows and errors/recovery; setup material is
needed only for configuration or missing capabilities.

| Need | Reference |
| --- | --- |
| Artifact Access | [artifact-access.md](references/artifact-access.md) |
| VOD AI MediaKit | [vod-ai-mediakit.md](references/vod-ai-mediakit.md) |
| VOD AI MediaKit audio separation | [vod-ai-mediakit-audio-separation.md](references/vod-ai-mediakit-audio-separation.md) |
| Seed Audio Tools | [seed-audio-tools.md](references/seed-audio-tools.md) |
| Reusing uploaded references across shots (presign pattern) | [reusing-uploaded-references-across-shots-presign-pattern.md](references/reusing-uploaded-references-across-shots-presign-pattern.md) |
| Seedream (Image) Tools | [seedream-image-tools.md](references/seedream-image-tools.md) |
| Seedance (Video) Tools | [seedance-video-tools.md](references/seedance-video-tools.md) |
| Seedance 2.5 (Video) Tools | [seedance-2-5-video-tools.md](references/seedance-2-5-video-tools.md) |
| Seed 3D (Hyper3D + Hitem3d) Tools | [seed-3d-hyper3d-hitem3d-tools.md](references/seed-3d-hyper3d-hitem3d-tools.md) |
| Seed 2.1 Multimodal Understanding | [seed-2-1-multimodal-understanding.md](references/seed-2-1-multimodal-understanding.md) |
| Speech-to-Text | [speech-to-text.md](references/speech-to-text.md) |
| Object Storage Upload | [object-storage-upload.md](references/object-storage-upload.md) |
| Resources | [resources.md](references/resources.md) |
| Architecture | [runtime-architecture.md](references/runtime-architecture.md) |
| Usage Patterns | [generation-workflows.md](references/generation-workflows.md) |
| Error Handling | [errors-and-recovery.md](references/errors-and-recovery.md) |
| Best Practices | [operating-practices.md](references/operating-practices.md) |
| Environment Essentials | [environment.md](references/environment.md) |
| Registration and setup | [setup.md](references/setup.md) |
