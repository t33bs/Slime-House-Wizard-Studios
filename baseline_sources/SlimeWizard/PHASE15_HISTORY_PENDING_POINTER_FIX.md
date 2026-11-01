# Phase 15: history restore pending-pointer cleanup

Undo/Redo replaces model part dictionaries. The staged Slimer layer's object-identity pointer previously survived history restoration, leaving Apply Move tied to an obsolete object. The history restoration path now clears the pending transaction and re-enables Move Original Pixels. This is a safety fix; redo of a provisional creation is treated as a normal asset and must not be mistaken for an active transaction. Windows GUI validation is still needed.
