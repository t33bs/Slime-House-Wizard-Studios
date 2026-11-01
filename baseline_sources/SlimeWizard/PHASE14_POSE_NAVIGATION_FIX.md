# Pose timeline navigation correction

The Previous frame and Next frame buttons previously operated on the hidden legacy recipe-step list (`self.steps`) rather than the saved pose timeline. They now use `select_timeline_pose()` and the current animation's saved pose count, clamped at both ends. The existing pose draft preservation/selection behavior remains centralized in the timeline selection path.

## Deferred Windows GUI checks
- In an animation with 3 or more poses, Previous and Next select and render the correct saved pose.
- First and last poses do not navigate beyond timeline bounds.
- Navigation works when the legacy recipe controls are hidden.
- Switching animation names then navigating uses that animation's own poses.
- Unsaved pose edits and Slimer draft state follow the existing pose-switch safeguards.
