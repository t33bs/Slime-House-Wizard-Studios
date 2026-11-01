"""Phase 78: handles remain accessible under zoom and do not overlap the menu."""
from studio.viewport_handles import visible_handle_position


def test_small_artwork_preserves_normal_handle_position():
    point = visible_handle_position((210, 175), [(170, 160), (200, 160),
                                              (200, 185), (170, 185)], 600, 400)
    assert point == (210, 175)


def test_zoomed_artwork_handle_clamped_inside_viewport():
    # Zoom crops the right and bottom of the selected leg; original controls
    # would end up outside the widget even though the leg is still visible.
    corners = [(-700, -200), (900, -200), (900, 660), (-700, 660)]
    for desired in ((930, 150), (180, 700), (105, -250)):
        x, y = visible_handle_position(desired, corners, 500, 350)
        assert 22 <= x <= 478
        assert 22 <= y <= 328


def test_handle_at_edge_of_visible_artwork_can_be_reached():
    x, y = visible_handle_position((-8, 120), [(-100, 80), (2, 80), (2, 160), (-100, 160)],
                                   500, 350)
    assert 22 <= x <= 478
    assert 22 <= y <= 328


def test_handle_avoids_expanded_canvas_menu():
    blocked = (300, 0, 500, 260)
    pos = visible_handle_position((425, 70), [(240, 20), (480, 20),
                                              (480, 160), (240, 160)],
                                  500, 350, blocked=blocked)
    assert pos is not None
    x, y = pos
    assert 22 <= x <= 478 and 22 <= y <= 328
    assert not (288 <= x <= 512 and -12 <= y <= 272)


def test_offscreen_artwork_does_not_show_untethered_handle():
    assert visible_handle_position((420, 90), [(900, 60), (940, 60),
                                               (940, 90), (900, 90)], 500, 350) is None


def test_handle_pixel_bounds_not_affected_by_canvas_zoom():
    small = visible_handle_position((320, 200), [(290, 175), (310, 175),
                                                  (310, 225), (290, 225)], 600, 400)
    big = visible_handle_position((950, 600), [(-120, -40), (950, -40),
                                                (950, 600), (-120, 600)], 600, 400)
    assert small == (320, 200)
    assert 22 <= big[0] <= 578 and 22 <= big[1] <= 378
