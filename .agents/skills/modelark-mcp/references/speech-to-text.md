# Speech-to-Text

Requires `BYTEPLUS_SEED_SPEECH_API_KEY`. Auth scope: `seed:asr:transcribe`.

#### `speech_to_text`

Transcribe audio to text via Seed Speech ASR (synchronous HTTP). The tool
internally submits the audio to the provider, polls until complete, and
returns the full result in a single call — no task ID, no object-storage
upload, no second tool required.

The call is capped by `SEED_SPEECH_ASR_POLL_MAX_SECONDS` (default 600s).

| Parameter | Type | Required | Description |
|---|---|---|---|
| `audio` | `AsrAudioInput` | Yes | Audio source (see below) |
| `options` | `AsrRequestOptions` | No | Transcription feature toggles |

**`AsrAudioInput`** (provide exactly one source):

| Field | Type | Required | Description |
|---|---|---|---|
| `audio_url` | `str` | No* | HTTPS URL of the audio file |
| `audio_data` | `str` | No* | Base64-encoded audio bytes. Mutually exclusive with other inputs. |
| `audio_file_path` | `str` | No* | Absolute local file path. stdio transport only. Mutually exclusive with other inputs. |
| `audio_format` | `"wav"` \| `"mp3"` \| `"ogg"` \| `"raw"` \| `"flac"` | Yes | Audio format |

**`AsrRequestOptions`:**

| Field | Type | Required | Description |
|---|---|---|---|
| `language` | `str` | No (default `en-US`) | BCP-47 language code |
| `enable_punc` | `bool` | No | Enable punctuation |
| `enable_itn` | `bool` | No | Enable ITN |

Returns `SpeechToTextOutput` with `result: TranscriptionResult` and optional
`log_id`. `TranscriptionResult` includes `text` (full transcript),
`utterances` (with word-level timestamps and speaker labels), and
`duration_ms`.

Transcription output is text — no artifact persistence needed.

**ASR error code `20000003` (silent audio).** Seed Speech ASR reports task
state in the `X-Api-Status-Code` header: `20000000` = success, `20000001` /
`20000002` = still processing, and `20000003` = terminal failure meaning
**silent audio — no human speech was detected**. The tool surfaces this as
`Seed Speech ASR query failed with status code 20000003` with
`retryable=false`. It is not transient — retrying the same task will not help.
Verify the audio actually contains speech and matches the declared
`audio_format`: for `wav`/`raw` the gateway assumes 16 kHz, 16-bit, mono PCM,
and a mismatch decodes to silence or garbage. Re-submit with corrected audio.

---
