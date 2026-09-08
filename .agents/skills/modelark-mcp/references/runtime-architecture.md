## Architecture

### Three-Provider Design

The server normalizes three distinct BytePlus API surfaces:

| Provider | Auth | Base URL | Products |
|---|---|---|---|
| **ModelArk** | `Authorization: Bearer <key>` | `https://ark.ap-southeast.bytepluses.com/api/v3` | Seedream, Seedance, Seed 3D (Hyper3D + Hitem3d), Seed 2.1 Understanding |
| **Seed Speech** | `X-Api-Key: <key>` | `https://voice.ap-southeast-1.bytepluses.com` | Seed Audio, Speech-to-Text |
| **VOD AI MediaKit** | `Authorization: Bearer <key>` | `https://mediakit.ap-southeast-1.bytepluses.com/api/v1` | Video enhancement, video transcoding, voice + background audio separation |

One Seed Speech key covers both Seed Audio and ASR — the provider distinguishes
them by `X-Api-Resource-Id`, not by the key. ModelArk uses a separate Bearer
key that covers Seedream, Seedance, Seed 3D, and Seed 2.1 Understanding (3D
requires an additional feature flag). VOD AI MediaKit uses a third Bearer key.
Tools for a product are only registered when its provider API key is set.

### Runtime Services

Each server process maintains shared runtime services:

- **Artifact Store** — Filesystem-backed durable media persistence with
  ownership metadata and TTL-based cleanup.
- **Budget Ledger** — SQLite-backed per-principal daily spend tracking.
- **Task Ownership Store** — SQLite-backed task ID to principal mapping for
  Seedance and Seed 3D ownership enforcement.
- **Provider Limiters** — Concurrency control: a per-provider semaphore
  (default 5) for every call, plus a per-principal semaphore (default 3) that
  bounds authenticated JWT HTTP principals only. Local principals (stdio and
  HTTP-local) are bounded solely by the provider limit.
- **Safe Downloader** — SSRF-safe URL downloads with IP pinning and redirect
  validation.

### Model Capability Registry

The server validates inputs against known model capabilities before spending
quota. Eleven model families, with these default model IDs:

| Family | Default Model ID | Key Traits |
|---|---|---|
| **Seedream Pro** | `dola-seedream-5-0-pro-260628` | 10 refs, no batch, PNG/JPEG |
| **Seedream Lite** | *(configured via `SEEDREAM_MODEL_BINDINGS`)* | 14 refs, batch, streaming, PNG/JPEG |
| **Seedream 4.x** | *(configured via `SEEDREAM_MODEL_BINDINGS`)* | 14 refs, batch, streaming, JPEG only |
| **Seedance 2.5** | `dreamina-seedance-2-5-260628` | 30 imgs / 10 vids / 10 audios, 480p / 720p / 1080p, up to 30s, structured editing + extension |
| **Seedance 2 Standard** | `dreamina-seedance-2-0-260128` | 9 imgs / 3 vids / 3 audios, 480p–4K, 0–15s |
| **Seedance 2 Fast** | *(configured via `SEEDANCE_MODEL_BINDINGS`)* | 480p, 720p only |
| **Seedance 2 Mini** | *(configured via `SEEDANCE_MODEL_BINDINGS`)* | 480p, 720p only |
| **Seed 2.1 Turbo** | `dola-seed-2-1-turbo-260628` (default) | 256K context, images + videos, deep-thinking |
| **Seed 2.1 Pro** | `dola-seed-evolving` (recognized built-in; opt-in via `SEED_UNDERSTANDING_DEFAULT_MODEL`) | 256K context, images + videos, deep-thinking |
| **Hyper3D** | `hyper3d-gen2-260112` | Text-to-3D + image-to-3D (5 imgs), GLB/OBJ/USDZ/FBX/STL, seeds, PBR materials |
| **Hitem3d** | `hitem3d-2-0-251223` | Image-to-3D only (1–4 imgs), OBJ/GLB/STL/FBX/USDZ, resolution + face control |

Custom model IDs must be explicitly bound via `SEEDREAM_MODEL_BINDINGS`,
`SEEDANCE_MODEL_BINDINGS`, `SEED_UNDERSTANDING_MODEL_BINDINGS`, or
`SEED3D_MODEL_BINDINGS` JSON. When a client omits the `model` parameter, the
default model for that product is used.

---
