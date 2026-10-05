# Publication copy and cover assets

Read when delivering a completed video intended for sharing, or when the user asks for 发布文稿, 封面, 截图, titles, descriptions or social posts. Work from the final script and exported cut; production plans and discarded drafts are not the publication source.

## Local deliverable

Save ready-to-use copy in `PUBLISH.md` in each requested language version’s video project or locale directory. Include the local cover and screenshot links in a clearly separated asset section. Produce other languages only when requested. If the destination is unknown, write a platform-neutral version and proceed.

Include:

- One recommended title that names the actual question or value of the video. Add alternatives only when useful or requested.
- A description that opens with the viewer's question or the video's concrete example, explains what the viewer will see, and lands the central takeaway. Summarize the final narrative rather than transcribing the voiceover.
- A small set of relevant topic tags when appropriate to the destination.
- A project or source link when one is actually available. Omit an unknown URL instead of inventing one or leaving a placeholder in ready-to-post text.

For a long video, add chapters when useful, using the final measured timeline. For a technical explainer, include a brief mechanism-illustration note if viewers could mistake diagrams or weights for measured results. Keep detailed citations in the source document and link it when practical.

## Editorial checks

Make the title, promised scope and examples match the delivered version. A selected history is not a complete survey; parallel research branches are not necessarily successor models. Use the same terminology and date conventions as the verified script.

Describe the subject's value to the audience. Mention the rendering framework or production process only when the post is about how the video was made. Claims such as breakthroughs, best performance or complete coverage need evidence from the actual content.

After a narrative revision, check the title, description, chapter times and linked filename together. Present the actual local copy file with the video. A copy-only request can be answered directly; creating an account, uploading assets or posting is outside drafting scope.

## Cover and screenshot delivery

For each completed language version, save a publication cover and a separate original video screenshot under `covers/`, for example `cover-en.png` and `video-still-en.png`. For multi-language delivery, check each version individually; finishing the English package does not close a missing Chinese package.

Select the screenshot from the actual final MP4. Compare a few relevant moments and choose a settled mechanism state with readable labels and a clear subject; avoid blank frames, transitions and incomplete reveals. Record the selected timestamp and source filename in the asset section of `PUBLISH.md`. Label this file as an original video still. If useful for a clean cover, render the same scene with the caption overlay disabled as a separate derivative, leaving the original still intact.

Design the cover for thumbnail viewing: a short localized headline, a clear mechanism or subject from the film, strong contrast and restrained secondary text. Reuse the visual language of the video; use editable Remotion/SVG assets when appropriate. AI-created illustrations can support a cover when suitable, but are not screenshots or evidence of actual video content. Keep the two asset types distinct.

Use the target platform's format when specified; otherwise match the video's aspect ratio and provide a high-resolution PNG, such as 1920×1080 for a landscape film. Inspect full size and thumbnail size for clipping, font coverage, contrast and legibility. Preserve editable cover source when available. If browser rendering is unavailable, an available native vector renderer can export code-authored covers, while a video decoder can still extract original screenshots; report the actual method used.

Before delivery, check that the video, copy, cover and screenshot files all exist for every requested language, that links resolve, and that titles and chapter times match the final cut. Add discoverable links to the project README as appropriate. Keep these requirements in the local production workflow; publishing the package externally still needs the user's instruction.
