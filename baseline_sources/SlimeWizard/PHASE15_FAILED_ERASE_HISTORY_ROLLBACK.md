# Phase 15: Failed source erase restores Undo/Redo history

A failed Move Original Pixels source erase now restores the project Undo and Redo stacks, plus the current pose-draft dirty marker, alongside the original source image buffers. A rejected Apply Move is not a completed edit and must not consume an Undo slot or destroy Redo history.

Regression tests inject an exception after partial image mutation and assert source buffers, history stacks, and pose draft metadata are all restored. Windows GUI testing for consecutive Apply Move remains outstanding.
