"""Phase 99: purely decorative retro-fantasy skin for existing Slime Wizard widgets.

No behaviors, shortcuts, signals, model methods, or new actions live here.  The
QSS applies to already-existing Qt controls; uiRole properties merely give
visual importance to existing buttons.
"""

PIXEL_PALETTE = {
    "navy": "#0c1028",
    "panel": "#121d3b",
    "panel_light": "#1c3052",
    "purple": "#9b53fa",
    "cyan": "#62e6ff",
    "green": "#7fff7f",
    "gold": "#ffdb79",
}

PIXEL_THEME_QSS = r'''
/* The shell is deliberately a skin, never a second editor. */
QMainWindow, QWidget {
    background-color: #0c1028;
    color: #e8eeff;
    font-size: 12px;
    font-family: "Segoe UI", "Consolas";
}
QWidget#pixelAppHeader {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                                stop:0 #201042,stop:0.5 #151334,stop:1 #111f3e);
    border: 2px solid #663aa6;
    border-bottom: 2px solid #7c58de;
    border-radius: 5px;
}
QLabel#pixelAppTitle {
    background: transparent;
    color: #ffdf78;
    font-family: "Consolas", "Segoe UI";
    font-weight: 900;
    font-size: 23px;
}
QLabel#pixelAppSubtitle {
    background: transparent;
    color: #b9b3e9;
    font-weight: bold;
    font-size: 12px;
}
QLabel#pixelAppPortrait { background: transparent; }
QWidget#pixelToolRegion, QWidget#pixelCanvasRegion, QWidget#pixelRightRegion {
    background: #111b35;
    border: 1px solid #40518c;
    border-radius: 5px;
}
QLabel { background: transparent; }
QLabel[uiRole="sectionTitle"] {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                                stop:0 #34205f,stop:1 #18274b);
    color: #a4f4ff;
    border: 1px solid #6e4db9;
    border-bottom: 2px solid #955ef3;
    border-radius: 3px;
    padding: 6px 8px;
    font-size: 12px;
    font-weight: bold;
}
QLabel#pixelStatusBar {
    background: #151f3b;
    color: #c5e6ff;
    border-left: 3px solid #52d6ef;
    padding: 5px 8px;
}
/* The new paint is for all EXISTING buttons, not only the toolbar. */
QPushButton, QToolButton {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                                stop:0 #33547b,stop:0.45 #243f68,stop:1 #182b4e);
    color: #f0f5ff;
    border: 2px solid #5379bd;
    border-bottom: 3px solid #24365f;
    border-radius: 5px;
    padding: 6px 9px;
    min-height: 18px;
    font-weight: 600;
}
QPushButton:hover, QToolButton:hover {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                                stop:0 #4a6ba3,stop:1 #284c80);
    border-color: #6ce8fb;
    border-bottom-color: #428dc7;
}
QPushButton:pressed, QToolButton:pressed {
    background: #17264b;
    border: 2px solid #b5a3ff;
    padding-top: 7px;
}
QPushButton:checked, QToolButton:checked {
    background: #4b2387;
    border: 2px solid #c384ff;
    color: white;
}
QPushButton:disabled, QToolButton:disabled {
    color: #8993b1;
    border-color: #404b6a;
    background: #1d2842;
}
QPushButton[uiRole="primary"], QToolButton[uiRole="primary"] {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                                stop:0 #7441d2,stop:1 #442171);
    border: 2px solid #b17cff;
    border-bottom: 3px solid #39215b;
    color: #ffffff;
    font-weight: bold;
}
QPushButton[uiRole="primary"]:hover, QToolButton[uiRole="primary"]:hover {
    background: #8350e0;
    border-color: #e4b7ff;
}
QPushButton[uiRole="success"] {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                                stop:0 #246c75,stop:1 #15515a);
    border: 2px solid #5be8dc;
    border-bottom: 3px solid #17454e;
    font-weight: bold;
}
QPushButton[uiRole="success"]:hover { background: #267e80; border-color: #a0ffde; }
QPushButton[uiRole="danger"], QToolButton[uiRole="danger"] {
    background: #493049;
    border: 2px solid #996190;
    color: #f8d6ee;
}
QPushButton[uiRole="danger"]:hover { background: #733c65; border-color: #ef91c5; }
QPushButton[uiRole="tool"]:checked {
    background: #5832a0;
    border: 2px solid #dfb6ff;
    color: #ffffff;
}
QPushButton[uiRole="preview"] {
    border: 2px solid #7cdafe;
    background: #263c68;
}
QPushButton#animationPreviewCollapseButton {
    background: #4b237f;
    border: 2px solid #b77dff;
    font-weight: bold;
}
QCheckBox { color: #dce8ff; spacing: 6px; }
QCheckBox::indicator {
    width: 15px; height: 15px;
    background: #182849;
    border: 2px solid #6c8ecb;
    border-radius: 3px;
}
QCheckBox::indicator:checked {
    background: #2da889;
    border: 2px solid #84f7d4;
}
QCheckBox#topSlimeBuddyToggle { color: #9bff9c; font-weight: bold; }
QComboBox, QSpinBox {
    background: #162b4e;
    color: #f0f2ff;
    border: 2px solid #527eb8;
    border-radius: 3px;
    padding: 4px 6px;
    min-height: 20px;
    selection-background-color: #7244c5;
}
QComboBox:hover, QSpinBox:hover, QComboBox:focus, QSpinBox:focus {
    border-color: #b387f4;
}
QComboBox QAbstractItemView {
    background: #17274b;
    color: #e8eeff;
    selection-background-color: #6337a5;
    border: 1px solid #7d65cb;
}
QListWidget {
    background: #0f1a34;
    color: #f0f4ff;
    border: 2px solid #405ca1;
    border-radius: 3px;
    padding: 3px;
    outline: none;
}
QListWidget::item { padding: 4px; border: 1px solid transparent; }
QListWidget::item:selected {
    background: #4f2789;
    border: 1px solid #c18bff;
    color: white;
    border-radius: 3px;
}
QListWidget::item:hover { background: #293b68; }
QListWidget#pixelPoseTimeline {
    background: #141b3d;
    border: 2px solid #7651b7;
    border-radius: 5px;
    padding: 5px;
}
QTabBar::tab {
    background: #21375e;
    color: #dae6ff;
    border: 1px solid #627bd2;
    border-bottom: 3px solid #2a3465;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    margin-right: 4px;
    padding: 8px 13px;
    font-weight: bold;
}
QTabBar::tab:selected {
    background: #58299d;
    color: white;
    border: 2px solid #c28bff;
    border-bottom: 3px solid #b476ff;
}
QTabBar::tab:hover { border-color: #c6a7ff; }
QFrame#slimeBuddyProductionWorkspace {
    background: #171435;
    border: 2px solid #955be3;
    border-radius: 7px;
}
QFrame#collapsibleAnimationPreview {
    background: #141d3d;
    border: 2px solid #7650bd;
    border-radius: 7px;
}
QScrollArea { border: 0; background: transparent; }
QSplitter::handle { background: #4f3a8b; }
QSplitter::handle:hover { background: #7e57cc; }
QMenu {
    color: #edf2ff;
    background: #1a274d;
    border: 2px solid #795dc2;
}
QMenu::item:selected { background: #5e38a4; }
QToolTip {
    background: #fff7de;
    color: #1a1640;
    border: 2px solid #9574d5;
    padding: 5px;
}
'''

# Phase 100: styling only for existing controls in the left Tools / Asset Library.
# Scoped selectors avoid changing pose timeline, canvas geometry or editor behavior.
PHASE100_LEFT_PANEL_QSS = r'''
QWidget#pixelToolRegion {
    background: #101b37;
    border: 2px solid #5a65b7;
    border-radius: 6px;
}
QLabel#pixelLeftToolsHeading, QLabel#pixelAssetsHeading,
QLabel#pixelSlimerHeading, QLabel#pixelCleanerHeading {
    color: #f3e8ff;
    border-left: 4px solid #a45bf6;
    border-bottom: 2px solid #57d3ef;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #3b2768,stop:0.55 #263265,stop:1 #152748);
    padding: 7px 8px;
    font-size: 12px;
    font-weight: 800;
}
QLabel#pixelAssetsHeading { border-left-color: #ffdb79; }
QLabel#pixelSlimerHeading { border-left-color: #a4f2a7; }
QLabel#pixelCleanerHeading { border-left-color: #62e6ff; }
QListWidget#pixelAssetLibraryList {
    background: #0e1734;
    border: 2px solid #6589c7;
    border-radius: 5px;
    padding: 5px;
    outline: none;
    alternate-background-color: #18254a;
}
QListWidget#pixelAssetLibraryList::item {
    color: #e9efff;
    border: 1px solid transparent;
    border-bottom: 1px solid #293a67;
    padding: 7px 6px;
    min-height: 22px;
}
QListWidget#pixelAssetLibraryList::item:selected {
    color: #ffffff;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #7133af,stop:1 #422e81);
    border: 2px solid #c68bff;
    border-radius: 3px;
}
QListWidget#pixelAssetLibraryList::item:hover:!selected {
    background: #263b65;
    border-left: 2px solid #6ee4f3;
}
QLabel#pixelActiveAssetLabel {
    background: #162f49;
    color: #a7ffcb;
    border: 1px solid #438c9e;
    border-left: 4px solid #79e4ca;
    border-radius: 3px;
    padding: 6px;
    font-weight: bold;
}
QLabel#pixelAssetVisibilityHint {
    color: #c6c9ef;
    background: #172342;
    border-left: 2px solid #8163c5;
    padding: 5px;
}
QCheckBox#pixelInactiveAssetToggle,
QCheckBox#pixelLockAspectToggle { color: #c1e8ff; font-weight: 600; }
'''
PIXEL_THEME_QSS += PHASE100_LEFT_PANEL_QSS


# Phase 101 — center-editor chrome only. These selectors style existing widgets.
# The underlying canvas rendering, zoom math, tabs, layer data and event handlers
# remain unchanged; no zoom buttons or editing actions are introduced.
PHASE101_CENTER_CHROME_QSS = r'''
QWidget#pixelCanvasRegion {
    background: #101a35;
    border: 2px solid #5974b5;
    border-radius: 6px;
}
QLabel#pixelCanvasHeading {
    color: #f2e5ff;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #42216d,stop:0.56 #253361,stop:1 #17264c);
    border: 1px solid #9463eb;
    border-left: 4px solid #d09aff;
    border-bottom: 2px solid #65dcfa;
    border-radius: 3px;
    padding: 7px 9px;
    font-weight: bold;
}
QLabel#pixelCanvasNavLabel {
    color: #9cefff;
    font-weight: bold;
}
QLabel#pixelZoomReadout {
    background: #20395c;
    color: #f8e6ff;
    border: 2px solid #73d9f1;
    border-radius: 4px;
    padding: 5px 9px;
    min-width: 45px;
    font-weight: 900;
}
QLabel#pixelCanvasNavTip { color: #b6c9ef; font-size: 11px; }
QPushButton#pixelCanvasFitButton {
    color: #f5faff;
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #39638e,stop:1 #203659);
    border: 2px solid #66cff4;
    border-bottom: 3px solid #32578b;
    font-weight: bold;
}
QPushButton#pixelCanvasFitButton:hover {
    border-color: #a9f3ff; background: #3b5e91;
}
QTabBar#pixelWorkspaceTabs {
    background: #111a39;
    border-bottom: 2px solid #634a9d;
}
QTabBar#pixelWorkspaceTabs::tab {
    background: #1d3760;
    color: #d9eeff;
    border: 1px solid #6389c1;
    border-bottom: 3px solid #243c6e;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    padding: 8px 13px;
    margin-right: 4px;
    font-weight: bold;
}
QTabBar#pixelWorkspaceTabs::tab:selected {
    background: #632aa8;
    color: #ffffff;
    border: 2px solid #d199ff;
    border-bottom: 3px solid #e2b7ff;
}
QTabBar#pixelWorkspaceTabs::tab:hover:!selected {
    background: #304d7e; border-color: #9bc9ff;
}
QPushButton#pixelWorkspaceAddButton {
    background: #263f6c; color: #c3f8ff;
    border: 2px solid #7baeea;
    border-bottom: 3px solid #3b538e;
    font-weight: bold;
}
QPushButton#pixelWorkspaceAddButton:hover {
    background: #3a5987; border-color: #b8eaff;
}
'''
PIXEL_THEME_QSS += PHASE101_CENTER_CHROME_QSS

# Phase 102 — pose timeline visual treatment ONLY. Scoped names refer to
# existing timeline, spinbox and buttons; none of the signals/operations change.
PHASE102_TIMELINE_CHROME_QSS = r'''
QLabel#pixelTimelineHeading {
    color: #f9e8ff;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #49246e,stop:0.53 #2a346a,stop:1 #17284b);
    border: 1px solid #a069ee;
    border-left: 4px solid #ecc184;
    border-bottom: 2px solid #66e4f7;
    border-radius: 4px;
    padding: 7px 10px;
    font-weight: 900;
}
QListWidget#pixelPoseTimeline {
    background: #0c1634;
    color: #e9f0ff;
    border: 2px solid #7b65c6;
    border-bottom: 3px solid #40356e;
    border-radius: 6px;
    padding: 7px;
    outline: none;
}
QListWidget#pixelPoseTimeline::item {
    color: #dceaff;
    background: #1c2d52;
    border: 2px solid #536ca8;
    border-bottom: 3px solid #30416f;
    border-radius: 5px;
    padding: 7px;
    margin: 2px;
    min-width: 83px;
}
QListWidget#pixelPoseTimeline::item:selected {
    color: #ffffff;
    background: #593099;
    border: 2px solid #dbadff;
    border-bottom: 3px solid #a779ea;
    border-radius: 5px;
}
QListWidget#pixelPoseTimeline::item:hover:!selected {
    background: #2b4676;
    border-color: #75d9fb;
}
QLabel#pixelTimelineTimingCaption {
    color: #b8e9ff;
    font-weight: 700;
}
QSpinBox#pixelTimelineDuration {
    background: #192c54;
    color: #f8e9ff;
    border: 2px solid #7bd7ed;
    border-bottom: 3px solid #376d9e;
    border-radius: 4px;
    padding: 5px 7px;
    font-weight: bold;
}
QSpinBox#pixelTimelineDuration:hover,
QSpinBox#pixelTimelineDuration:focus {
    border-color: #dab3ff;
}
QPushButton#pixelTimelineSavePose {
    background: #386a62;
    color: #f2fff8;
    border: 2px solid #76eab5;
    border-bottom: 3px solid #2a655a;
}
QPushButton#pixelTimelineSavePose:hover {
    background: #427e72;
    border-color: #b0ffda;
}
QPushButton#pixelTimelineRestorePose,
QPushButton#pixelTimelineDuplicatePose,
QPushButton#pixelTimelineCopyPose {
    background: #3a326b;
    color: #f5eaff;
    border: 2px solid #ab83e8;
    border-bottom: 3px solid #373365;
}
QPushButton#pixelTimelineRestorePose:hover,
QPushButton#pixelTimelineDuplicatePose:hover,
QPushButton#pixelTimelineCopyPose:hover {
    background: #5a4392;
    border-color: #e2adff;
}
QPushButton#pixelTimelineInsertPose,
QToolButton#pixelTimelineImportPose {
    background: #26516b;
    color: #ecfaff;
    border: 2px solid #69def3;
    border-bottom: 3px solid #264f77;
}
QPushButton#pixelTimelineInsertPose:hover,
QToolButton#pixelTimelineImportPose:hover {
    background: #376b88;
    border-color: #a3f5ff;
}
QPushButton#pixelTimelinePreviousPose,
QPushButton#pixelTimelineNextPose,
QPushButton#pixelTimelineShiftLeft,
QPushButton#pixelTimelineShiftRight {
    background: #263d68;
    color: #eaf5ff;
    border: 2px solid #81a5e3;
    border-bottom: 3px solid #344673;
}
QPushButton#pixelTimelinePreviousPose:hover,
QPushButton#pixelTimelineNextPose:hover,
QPushButton#pixelTimelineShiftLeft:hover,
QPushButton#pixelTimelineShiftRight:hover {
    background: #365687;
    border-color: #a9d8ff;
}
QPushButton#pixelTimelineRemovePose {
    background: #5c2e55;
    color: #ffe5f4;
    border: 2px solid #d27cba;
    border-bottom: 3px solid #493052;
}
QPushButton#pixelTimelineRemovePose:hover {
    background: #793d69;
    border-color: #ffb6d9;
}
'''
PIXEL_THEME_QSS += PHASE102_TIMELINE_CHROME_QSS


# Phase 103 — final visual pass for EXISTING Buddy and preview widgets.
# No additional controls, independent generation actions, or editor behavior.
PHASE103_RIGHT_DOCK_QSS = r'''
QWidget#pixelRightRegion {
    background: #101933;
    border: 2px solid #7355ad;
    border-radius: 6px;
}
QSplitter#buddyPreviewVerticalSplitter::handle {
    background: #574383;
    border-top: 1px solid #9e73e2;
    border-bottom: 1px solid #2d225d;
}
QSplitter#buddyPreviewVerticalSplitter::handle:hover {
    background: #8b5dc4;
}
QFrame#slimeBuddyProductionWorkspace {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #211949,stop:0.36 #191a42,stop:1 #121b36);
    border: 2px solid #a06add;
    border-bottom: 3px solid #523e91;
    border-radius: 6px;
}
QLabel#pixelBuddyWorkspaceHeading {
    color: #f3dcff;
    background: #33245f;
    border: 1px solid #b37af1;
    border-left: 4px solid #8ee8f9;
    border-bottom: 2px solid #6c4ca5;
    border-radius: 3px;
    padding: 7px 8px;
    font-family: "Consolas", "Segoe UI";
    font-size: 13px;
    font-weight: 900;
}
QLabel#pixelBuddyMascot { background: transparent; }
QLabel#pixelBuddySpeechBubble {
    color: #282347;
    background: #fff3dd;
    border: 2px solid #ae84e9;
    border-bottom: 4px solid #7866bd;
    border-radius: 6px;
    padding: 10px;
    font-family: "Consolas", "Segoe UI";
    font-size: 12px;
    font-weight: bold;
}
QLabel#pixelBuddyProductionHeading {
    color: #b2f0ff;
    background: #24345c;
    border-left: 4px solid #a971ed;
    border-bottom: 1px solid #4d6fa8;
    padding: 7px 8px;
    font-weight: 900;
}
QLabel#pixelBuddyProductionExplainer {
    color: #d0e4fb;
    background: #172b4c;
    border: 1px solid #3e5984;
    border-radius: 4px;
    padding: 9px;
}
QLabel#buddyProductionStatus {
    color: #ffe2a4;
    background: #302d4e;
    border: 1px solid #a487d0;
    border-left: 4px solid #efc77b;
    border-radius: 4px;
    padding: 9px;
    font-weight: bold;
}
QLabel#pixelBuddyHandoffLabel {
    color: #c7dafa;
    background: #182540;
    border: 1px solid #3d4e83;
    border-radius: 4px;
    padding: 8px;
}
QFrame#collapsibleAnimationPreview {
    background: #151e3e;
    border: 2px solid #8060c1;
    border-bottom: 3px solid #47417e;
    border-radius: 6px;
}
QLabel#pixelAnimationPreviewHeading {
    color: #f4e8ff;
    background: #35225d;
    border: 1px solid #9b69e5;
    border-left: 4px solid #7bdff5;
    border-bottom: 2px solid #6a4cb0;
    border-radius: 3px;
    padding: 7px 8px;
    font-size: 13px;
    font-weight: 900;
}
QPushButton#animationPreviewCollapseButton {
    color: #f8eaff;
    background: #493071;
    border: 2px solid #b18af0;
    border-bottom: 3px solid #4b367b;
    padding: 5px 9px;
}
QPushButton#animationPreviewCollapseButton:hover {
    background: #65459e;
    border-color: #ddbeff;
}
QLabel#pixelSlimerPreviewHeading, QLabel#pixelCreaturePreviewHeading {
    color: #bcefff;
    background: #1b3052;
    border-left: 3px solid #71d7ef;
    border-bottom: 1px solid #405e8d;
    padding: 6px 8px;
    font-weight: bold;
}
QLabel#pixelSlimerCleanPreview, QLabel#pixelFramePreviewImage {
    background: #101b39;
    border: 2px solid #5d72ad;
    border-radius: 3px;
}
QScrollArea#pixelFramePreviewScroll {
    background: #0d1630;
    border: 1px solid #455e99;
    border-radius: 4px;
}
QPushButton#pixelPreviewZoomOut, QPushButton#pixelPreviewZoomIn,
QPushButton#pixelPreviewZoomFit {
    color: #e9f7ff;
    background: #284367;
    border: 2px solid #69addb;
    border-bottom: 3px solid #325784;
    font-weight: bold;
}
QPushButton#pixelPreviewZoomOut:hover, QPushButton#pixelPreviewZoomIn:hover,
QPushButton#pixelPreviewZoomFit:hover {
    background: #3c6289;
    border-color: #9ff0ff;
}
QPushButton#pixelPreviewPlayButton {
    color: #f2fff4;
    background: #2b655c;
    border: 2px solid #77ddb6;
    border-bottom: 3px solid #245b54;
    font-weight: 900;
}
QPushButton#pixelPreviewPlayButton:hover {
    background: #357d71;
    border-color: #a5ffdc;
}
QPushButton#pixelPreviewPlayButton:checked {
    color: #fff4d5;
    background: #755334;
    border-color: #f3cd91;
}
QLabel#pixelPreviewSpeedHeading, QCheckBox#pixelPreviewLoopCheck {
    color: #c4eaf7;
    font-weight: bold;
}
QComboBox#pixelPreviewSpeedSelect {
    background: #1b3255;
    color: #eff7ff;
    border: 2px solid #6c92ce;
    border-radius: 3px;
    padding: 5px;
}
QComboBox#pixelPreviewSpeedSelect:hover { border-color: #c199ff; }
'''
PIXEL_THEME_QSS += PHASE103_RIGHT_DOCK_QSS

# Build 1.3 - only viewport layout and scroll affordance; editor pixels unaffected.
BUILD13_CANVAS_TIMELINE_QSS = r'''
QSplitter#pixelCanvasTimelineSplitter::handle:vertical {
    background: #7353b7;
    border-top: 2px solid #b293ee;
    border-bottom: 2px solid #26345d;
    margin: 1px 0px;
}
QSplitter#pixelCanvasTimelineSplitter::handle:vertical:hover {
    background: #b784f4;
    border-top: 2px solid #e0c2ff;
}
QScrollArea#pixelLeftToolsScroll QScrollBar:vertical,
QListWidget#pixelAssetLibraryList QScrollBar:vertical {
    width: 19px;
    background: #121c37;
    border: 1px solid #6379bb;
    margin: 0px;
}
QScrollArea#pixelLeftToolsScroll QScrollBar::handle:vertical,
QListWidget#pixelAssetLibraryList QScrollBar::handle:vertical {
    background: #8063ca;
    border: 2px solid #c0a5ee;
    border-radius: 4px;
    min-height: 44px;
}
QScrollArea#pixelLeftToolsScroll QScrollBar::handle:vertical:hover,
QListWidget#pixelAssetLibraryList QScrollBar::handle:vertical:hover {
    background: #aa87ee;
}
QScrollArea#pixelLeftToolsScroll QScrollBar::add-line:vertical,
QScrollArea#pixelLeftToolsScroll QScrollBar::sub-line:vertical,
QListWidget#pixelAssetLibraryList QScrollBar::add-line:vertical,
QListWidget#pixelAssetLibraryList QScrollBar::sub-line:vertical {
    height: 0px;
}
'''
PIXEL_THEME_QSS += BUILD13_CANVAS_TIMELINE_QSS
