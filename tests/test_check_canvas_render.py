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


def test_uniform_opaque_background_is_observably_blank(tmp_path):
    path = lesson(tmp_path, """<script>const x=c.getContext('2d');
x.fillStyle='#123456';x.fillRect(0,0,c.width,c.height);</script>""")
    assert any("blank" in error for error in render_errors([path]))


def test_foreground_over_opaque_background_passes(tmp_path):
    path = lesson(tmp_path, """<script>const x=c.getContext('2d');
x.fillStyle='#123456';x.fillRect(0,0,c.width,c.height);
x.fillStyle='#ffffff';x.fillRect(10,10,20,20);</script>""")
    assert render_errors([path]) == []


@pytest.mark.parametrize("wrapper", [
    "<style>canvas{visibility:hidden}</style>",
    "<style>body{opacity:0}</style>",
    "<style>body{display:none}</style>",
])
def test_painted_but_invisible_canvas_fails(tmp_path, wrapper):
    path = lesson(tmp_path, wrapper + """<script>const x=c.getContext('2d');
x.fillRect(10,10,20,20);</script>""")
    assert any("not visible" in error for error in render_errors([path]))


def test_each_interactive_canvas_state_is_checked(tmp_path):
    path = lesson(tmp_path, """
<button onclick="c.getContext('2d').clearRect(0,0,c.width,c.height)">blank</button>
<button onclick="c.getContext('2d').fillRect(10,10,20,20)">restore</button>
<script>c.getContext('2d').fillRect(10,10,20,20)</script>""")
    assert any("after-click" in error and "blank" in error
               for error in render_errors([path]))


def test_range_input_states_are_checked(tmp_path):
    path = lesson(tmp_path, """
<input id="r" type="range" min="0" max="1" value="0">
<script>const x=c.getContext('2d');x.fillRect(10,10,20,20);
r.addEventListener('input',()=>{if(r.value==='1')x.clearRect(0,0,c.width,c.height)})</script>""")
    assert any("after-range" in error and "blank" in error
               for error in render_errors([path]))


def test_canvas_click_state_is_checked(tmp_path):
    path = lesson(tmp_path, """<script>const x=c.getContext('2d');
x.fillRect(10,10,20,20);c.addEventListener('click',()=>x.clearRect(0,0,c.width,c.height));</script>""")
    assert any("after-canvas" in error and "blank" in error
               for error in render_errors([path]))


def test_canvas_click_includes_left_interaction_target(tmp_path):
    path = lesson(tmp_path, """<script>const x=c.getContext('2d');
x.fillRect(10,10,20,20);c.addEventListener('click',e=>{
const r=c.getBoundingClientRect();if(e.clientX-r.left<r.width*.1)x.clearRect(0,0,c.width,c.height);});</script>""")
    assert any("after-canvas" in error and "blank" in error
               for error in render_errors([path]))


def test_unused_exception_for_a_requested_lesson_fails(tmp_path):
    path = lesson(tmp_path, """<script>const x=c.getContext('2d');
x.fillRect(10,10,20,20);</script>""")
    rel = os.path.relpath(path, os.path.dirname(os.path.dirname(__file__))).replace("\\", "/")
    exceptions = tmp_path / "exceptions.json"
    exceptions.write_text(json.dumps({rel + "#c": "temporary"}), encoding="utf-8")
    assert any("stale canvas-render exception" in error
               for error in render_errors([path], exceptions_path=str(exceptions)))
