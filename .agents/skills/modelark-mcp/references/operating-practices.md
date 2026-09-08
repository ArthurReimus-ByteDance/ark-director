## Best Practices

1. **Always persist.** Set `persist=true` (the default) so generated media
   survives provider URL expiry. Reference the returned `ArtifactRef.uri` for
   durable access.

2. **Poll with backoff for Seedance.** Use the `recommended_poll_after_ms`
   from `seedance_create_task` (2.0) or `seedance_2_5_create_task` (2.5) output. Don't
   poll faster than the interval — it
   wastes quota and can hit rate limits.

3. **Make polling resumable.** Save the task ID and request metadata before the
   first poll. A process timeout must continue the existing task, not create a
   duplicate.

4. **Use variation tools for choice.** When the user needs options (e.g., "show
   me a few versions"), use a variation tool rather than calling the single
   generate tool multiple times. Variations run in parallel and handle partial
   failures gracefully.

5. **Set seeds for reproducibility.** When the user wants consistent or
   reproducible output, pass a fixed `seed` to `seedream_generate_image` or a
   `base_seed` to `seedream_generate_image_variations`.

6. **Check health first.** Call `seed-health://status` to verify which products
   are configured before attempting generation.

7. **Respect model capabilities.** Different models support different features
   (batch generation, resolutions, reference counts). Check the capability
   registry before passing unsupported parameters.

8. **Explicit task cleanup.** Cancel or delete provider tasks only within
   explicit user authorization. Completion or age alone does not grant cleanup.

9. **Validate input sizes.** Audio and image references are limited to 10 MiB
   each; video references are limited to 200 MiB. Base64 inputs are validated
   before submission.

10. **Treat cost estimates as estimates.** Record estimated cost separately
    from confirmed billing and usage. Do not infer actual cost solely from a
    preflight estimate when resolution or token usage differs.

11. **Verify the saved media.** Provider task success proves generation
    completed, not that resolution, audio, narrative continuity, or playback
    compatibility satisfy the production brief.

12. **Use `media_upload` for URL-only workflows.** Seedance video references
    are URL-only. When starting with a local or Base64 video, upload it first
    and pass the presigned URL into `seedance_create_task` (2.0) or `seedance_2_5_create_task` (2.5).

13. **Reuse references with `media_presign` — do not re-upload.** Presigned URLs
    expire after 30 minutes by default, but the underlying object persists in TOS/S3.
    Upload each reference file once, store the `object_key`, and call
    `media_presign` (single key) or `media_presign_batch` (many keys at once)
    to get a fresh URL for each new shot. This avoids re-uploading the same
    character/location/prop sheets for every scene.

14. **`speech_to_text` is synchronous.** It blocks until transcription completes
    or the poll cap is reached. Provide appropriately sized audio and plan for
    the blocking duration.

15. **Use `seed_understand` for multimodal reasoning.** It can analyze images
    (OCR, scene description), videos (content analysis, UI review), and
    reason across multiple media inputs. Enable `thinking=true` for complex
    analysis. Video Base64 is not supported — upload via `media_upload` first.

16. **Choose the right Seedance model.** Use 2.0 (`seedance_create_task`)
    for 4K or lower cost. Use 2.5 (`seedance_2_5_create_task`) for
    30-second generation, 50 references, timestamp editing, 1080p output, or
    multi-round extension. The get/list/cancel tools are shared.

17. **Treat MediaKit persistence separately from the provider result.** Keep the
    returned `source_url` whenever `vod_enhance_video` or
    `vod_get_transcode_task` reports success. Prefer `persist=true`, but inspect
    `persistence` and `persistence_issue`: the 200 MiB limit or a
    safe-download/storage failure can prevent the durable copy without
    invalidating the provider result. Do not resubmit after an ambiguous
    timeout, and do not present `estimated_cost_usd` as available.

18. **Transcode is submit-then-poll.** Call `vod_transcode_video`, capture the
    returned `task_id`, then poll with `vod_get_transcode_task` until the
    status is `succeeded` or `failed`. The default profile is portrait-to-720x720
    letterbox; set `video.codec`, `scale_*`, `bitrate_*`, `fps`, and
    `container_format` to target a specific output. Do not retry the POST after
    an ambiguous timeout — re-poll the task ID instead.

19. **Choose the right 3D model.** Use `hyper3d_create_task` for text-to-3D or
    when you need seeds, PBR materials, custom mesh modes, or HD textures. Use
    `hitem3d_create_task` for image-to-3D with multi-view inputs (front/back/
    left/right) and resolution control (1536/1536pro). The get/list/cancel tools
    are family-specific — use `hyper3d_*` for Hyper3D task IDs and `hitem3d_*`
    for Hitem3d task IDs.

20. **3D output is a zip package.** The provider returns a 24-hour file URL
    containing a zip of the 3D file. On first successful poll with
    `persist_output=true` (default), the file is copied to the artifact store.
    Use the returned `ArtifactRef.uri` for durable access after the provider
    URL expires.

---
