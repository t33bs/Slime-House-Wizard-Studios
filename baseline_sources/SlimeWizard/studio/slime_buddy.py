"""Optional, non-prescriptive workflow guidance for independent creature artwork."""
STATIONS = {
 "Import": ("Bring in one PNG or many separate parts.", "Use Import PNG assets. Transparent images work best for layered editing.", "Your art can have any anatomy, silhouette, colors, or number of pieces."),
 "Assembly": ("Arrange the pieces however you imagine them.", "Click a piece to select it; drag to move; use the corner handle to resize. Undo is always available.", "You decide where every piece belongs."),
 "Rigging": ("Connect pieces only when you want them to move together.", "Select a piece, optionally choose a parent, and place its pivot where you want it to turn.", "Floating parts, disconnected pieces, and unusual joints are welcome."),
 "Poses": ("Create a different arrangement for each moment of motion.", "Choose an animation and pose; move or turn pieces; save the pose; use Copy Pose to build on it.", "Every pose is your choice; the tool does not enforce a movement style."),
 "Timeline": ("Choose the order and speed of your poses.", "Add, copy, remove, or shift poses. Smaller duration values play faster. Preview as often as you like.", "There is no required frame count or correct rhythm."),
 "Preview": ("Preview the poses you created.", "Use Play and playback speed to check the timing of your own animation. Hide the preview panel when you want more canvas space.", "Preview guides never change or export artwork."),
 "Save": ("Keep an editable copy of your work.", "Use Save creature to store the project, including its layers and animation data.", "Saving never changes the appearance you chose."),
 "Export": ("Turn your poses into shareable files.", "Choose GIF, transparent APNG, or sprite sheet. Preview timing and confirm the output before sharing.", "Technical warnings concern missing data or export limitations, never your art style."),
}
def station_guide(station):
    if station not in STATIONS: raise KeyError(station)
    intro,how,freedom=STATIONS[station]
    return f"{intro}\nHow: {how}\nCreative freedom: {freedom}"

