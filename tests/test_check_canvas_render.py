import json
import os
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


@pytest.mark.parametrize("wrapper", [
    "<style>canvas{visibility:hidden}</style>",
    "<style>body{opacity:0}</style>",
    "<style>body{display:none}</style>",
])
def test_painted_but_invisible_canvas_fails(tmp_path, wrapper):
    path = lesson(tmp_path, wrapper + """<script>const x=c.getContext('2d');
x.fillRect(10,10,20,20);</script>""")
    assert any("not visible" in error for error in render_errors([path]))


def test_unused_exception_for_a_requested_lesson_fails(tmp_path):
    path = lesson(tmp_path, """<script>const x=c.getContext('2d');
x.fillRect(10,10,20,20);</script>""")
    rel = os.path.relpath(path, os.path.dirname(os.path.dirname(__file__))).replace("\\", "/")
    exceptions = tmp_path / "exceptions.json"
    exceptions.write_text(json.dumps({rel + "#c": "temporary"}), encoding="utf-8")
    assert any("stale canvas-render exception" in error
               for error in render_errors([path], exceptions_path=str(exceptions)))
