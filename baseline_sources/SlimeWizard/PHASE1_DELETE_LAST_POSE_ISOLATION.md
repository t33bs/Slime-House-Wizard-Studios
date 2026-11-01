# Phase 1: final-pose deletion isolation

The Remove Pose GUI path previously refreshed the timeline after deleting its final pose, but left the deleted pose's live canvas and Slimer overlay visible. This could make an empty timeline look as though the deleted pose was still present.

Now the final-pose path hides the transient Slimer overlay, resets Slimer selection/caches, clears the pose draft, and refreshes canvas and timeline. When poses remain, the selected surviving snapshot is loaded explicitly.

Two source-level regression tests added. Full test suite: 199 passed and 433 subtests passed. Windows GUI interaction remains unverified. Previously deferred Windows tests remain deferred.
