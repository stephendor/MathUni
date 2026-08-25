import pytest

from scripts.check_canvas_render import chrome_path, render_errors


pytestmark = pytest.mark.skipif(not chrome_path(), reason="headless Chrome unavailable")


def lesson(tmp_path, body):
    path = tmp_path / "lesson.html"
    path.write_text("<canvas id='c' width='80' height='60'></canvas>" + body,
                    encoding="utf-8")
    return str(path)


def test_visible_interior_drawing_passes(tmp_path):
    path = lesson(tmp_path, """<script>const x=c.getContext('2d');
x.fillRect(10,10,20,20);</script>""")
    assert render_errors([path]) == []


def test_off_canvas_drawing_is_observably_blank(tmp_path):
    path = lesson(tmp_path, """<script>const x=c.getContext('2d');
x.fillRect(10,c.height+10,20,20);</script>""")
    assert any("blank" in error for error in render_errors([path]))
