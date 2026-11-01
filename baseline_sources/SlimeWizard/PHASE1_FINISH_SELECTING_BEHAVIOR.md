# Finish Selecting behavior and pending GUI verification

Finish Selecting now validates an active Slimer selection and explicitly switches into movable transform mode, with an actionable status message. It does not commit a persistent Asset Library layer. That is intentionally the job of Place as Layer; Place Frame creates a timeline pose.

User report remains open for GUI testing: clicking Finish Selecting must show the isolated selected pixels as a clearly visible floating 'slimed' selection with transform handles. If the user expects a persistent asset immediately, review the button design rather than silently committing an asset.

Windows test pending: highlight -> Finish Selecting -> drag -> Place as Layer, confirm independent numbered layer and no overwriting; repeat Place Frame and verify timeline isolation.
