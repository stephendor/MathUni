"""Render lesson canvases in headless Chrome and reject blank/clipped output."""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlparse


CHROME_CANDIDATES = (
    os.environ.get("CHROME_PATH"),
    shutil.which("google-chrome"), shutil.which("chrome"),
    shutil.which("chromium"), shutil.which("chromium-browser"),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
)
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCEPTIONS = os.path.join(REPO, "curriculum", "canvas-render-exceptions.json")


def chrome_path():
    return next((path for path in CHROME_CANDIDATES
                 if path and os.path.isfile(path)), None)


def harness(paths):
    urls = [Path(path).resolve().as_uri() for path in paths]
    return r"""<!doctype html><meta charset=utf-8><body><pre id=result>pending</pre>
<script>
const urls=%s;
function pixels(c){
  const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
  const counts=new Map();
  for(let i=0;i<d.length;i+=4){
    const key=d[i]+','+d[i+1]+','+d[i+2]+','+d[i+3];
    counts.set(key,(counts.get(key)||0)+1);
  }
  let background=null,bgCount=-1;
  for(const [key,count] of counts)if(count>bgCount){background=key;bgCount=count;}
  let n=0,minX=c.width,minY=c.height,maxX=-1,maxY=-1;
  const rows=new Uint8Array(c.height), cols=new Uint8Array(c.width);
  for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++){
    const i=(y*c.width+x)*4,key=d[i]+','+d[i+1]+','+d[i+2]+','+d[i+3];
    if(key!==background){
      n++; rows[y]=1; cols[x]=1; minX=Math.min(minX,x);maxX=Math.max(maxX,x);
      minY=Math.min(minY,y);maxY=Math.max(maxY,y);
    }
  }
  const edge=minX<=1||minY<=1||maxX>=c.width-2||maxY>=c.height-2;
  const interiorGap=[...rows.slice(2,-2)].includes(0)||[...cols.slice(2,-2)].includes(0);
  return {painted:n,bbox:[minX,minY,maxX,maxY],clipped:!!(n&&edge&&interiorGap),
          ink:ink(c,background,n)};
}
// Read-back fixture. Gate 7's canvas read-back is a human opening the figure
// and checking that the bars end where the numbers say; it found every
// positional claim in lab-09 correct to within a pixel, and had no way to
// leave behind evidence that it ran. This is that evidence: per INK COLOUR,
// how much of it there is and where it extends. Bar ends, threshold-line
// positions and annotation-colour counts all fall out of it, so a figure
// whose numbers move without its drawing fails loudly instead of waiting for
// the next reader.
//
// Channels are quantised to 32 levels, and a colour is kept only if it covers
// at least a fiftieth of the figure's ink. Both thresholds are there to keep
// ANTI-ALIASING out of the fixture: every stroke in this figure generates a
// dozen blend colours at a few hundred pixels each, spanning nearly the whole
// canvas, and they are precisely the rows that would differ on the next
// Chrome release. What survives is the figure's structural ink — the bar
// colours, the axis and label colour, the annotation colour — which is what
// the read-back is about.
function ink(c,background,painted){
  const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
  const q=v=>Math.round(v/32)*32;
  const seen=new Map();
  for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++){
    const i=(y*c.width+x)*4;
    if(d[i+3]===0)continue;
    const key=d[i]+','+d[i+1]+','+d[i+2]+','+d[i+3];
    if(key===background)continue;
    const k=q(d[i])+','+q(d[i+1])+','+q(d[i+2]);
    let e=seen.get(k);
    if(!e){e={colour:k,n:0,minX:c.width,minY:c.height,maxX:-1,maxY:-1};seen.set(k,e);}
    e.n++;
    if(x<e.minX)e.minX=x; if(x>e.maxX)e.maxX=x;
    if(y<e.minY)e.minY=y; if(y>e.maxY)e.maxY=y;
  }
  const floor=Math.max(24,Math.round(painted*0.02));
  return [...seen.values()].filter(e=>e.n>=floor)
    .sort((a,b)=>b.n-a.n||(a.colour<b.colour?-1:1))
    .map(e=>({colour:e.colour,n:e.n,bbox:[e.minX,e.minY,e.maxX,e.maxY]}));
}
function visible(c){
  for(let e=c;e;e=e.parentElement){
    const s=getComputedStyle(e);
    if(s.display==='none'||s.visibility==='hidden'||s.visibility==='collapse'||Number(s.opacity)===0)return false;
  }
  const r=c.getBoundingClientRect();
  return r.width>0&&r.height>0;
}
async function run(){
  const out=[];
  for(const url of urls){
    const f=document.createElement('iframe');
    document.body.appendChild(f);
    const source=await (await fetch(url)).text();
    const bootstrap=`<script>
window.__canvasRuntimeErrors=[];
const __recordCanvasError=e=>window.__canvasRuntimeErrors.push(
  String(e.reason||e.error||e.message||e));
window.addEventListener('error',__recordCanvasError);
window.addEventListener('unhandledrejection',__recordCanvasError);
<\/script><base href="${url.replaceAll('&','&amp;').replaceAll('"','&quot;')}">`;
    await new Promise((ok,bad)=>{f.onload=ok;f.onerror=bad;f.srcdoc=bootstrap+source});
    await new Promise(ok=>setTimeout(ok,80));
    const doc=f.contentDocument;
    const runtimeErrors=f.contentWindow.__canvasRuntimeErrors;
    const canvases=[...doc.querySelectorAll('canvas')].filter(c=>
      c.getAttribute('aria-hidden')!=='true');
    function snapshot(state){
      for(const c of canvases) out.push({url,id:c.id,state,...pixels(c),visible:visible(c)});
      while(runtimeErrors.length)out.push({url,id:'',state,runtimeError:runtimeErrors.shift()});
    }
    snapshot(undefined);
    let interaction=0;
    for(const b of doc.querySelectorAll('button[onclick]')){
      if(/^check\s*\(/.test(b.getAttribute('onclick'))) continue;
      try{b.click()}catch(e){runtimeErrors.push(String(e))}
      interaction++;
      await new Promise(ok=>setTimeout(ok,40));
      snapshot('after-click-'+interaction);
    }
    for(const control of doc.querySelectorAll('input[type=range]')){
      for(const value of [control.min,control.max]){
        if(value==='')continue;
        control.value=value;
        control.dispatchEvent(new Event('input',{bubbles:true}));
        control.dispatchEvent(new Event('change',{bubbles:true}));
        interaction++;
        await new Promise(ok=>setTimeout(ok,40));
        snapshot('after-range-'+interaction);
      }
    }
    for(const target of canvases){
      const r=target.getBoundingClientRect();
      for(const point of [[.08,.5,'left'],[.5,.5,'centre'],[.92,.5,'right']]){
        try{target.dispatchEvent(new MouseEvent('click',{bubbles:true,
          clientX:r.left+r.width*point[0],clientY:r.top+r.height*point[1]}))}
        catch(e){runtimeErrors.push(String(e))}
        interaction++;
        const settle=point[2]==='left'?Number(target.dataset.renderSettleMs||80):80;
        await new Promise(ok=>setTimeout(ok,settle));
        snapshot('after-canvas-'+point[2]);
      }
    }
    f.remove();
  }
  document.getElementById('result').textContent=JSON.stringify(out);
}
run().catch(e=>document.getElementById('result').textContent=JSON.stringify({error:String(e)}));
</script>""" % json.dumps(urls)


def render_results(paths, browser=None):
    browser = browser or chrome_path()
    if not browser:
        raise RuntimeError("Chrome/Chromium not found; set CHROME_PATH")
    with tempfile.TemporaryDirectory(prefix="mathuni-canvas-") as tmp:
        page = os.path.join(tmp, "harness.html")
        with open(page, "w", encoding="utf-8") as handle:
            handle.write(harness(paths))
        # Each lesson may now exercise button, range, and three canvas-click
        # states. Scale the virtual-time allowance with that expanded surface.
        budget = max(8000, len(paths) * 650)
        command = [browser, "--headless=new", "--disable-gpu", "--no-sandbox",
                   "--allow-file-access-from-files", "--disable-web-security",
                   "--virtual-time-budget=%d" % budget, "--dump-dom",
                   Path(page).as_uri()]
        result = subprocess.run(command, capture_output=True, text=True,
                                encoding="utf-8", errors="replace",
                                timeout=max(60, len(paths)))
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "headless browser failed")
    marker = '<pre id="result">'
    if marker not in result.stdout:
        raise RuntimeError("render harness produced no result")
    payload = result.stdout.split(marker, 1)[1].split("</pre>", 1)[0]
    if payload == "pending":
        raise RuntimeError("render harness did not finish before its time budget")
    decoded = json.loads(html.unescape(payload))
    if isinstance(decoded, dict) and decoded.get("error"):
        raise RuntimeError(decoded["error"])
    return decoded


def render_errors(paths, browser=None, exceptions_path=EXCEPTIONS):
    errors = []
    with open(exceptions_path, encoding="utf-8") as handle:
        exceptions = json.load(handle)
    requested = {
        os.path.relpath(os.path.abspath(path), REPO).replace("\\", "/")
        for path in paths
    }
    exercised = set()
    for item in render_results(paths, browser=browser):
        parsed = unquote(urlparse(item["url"]).path).lstrip("/")
        if os.name == "nt" and re.match(r"^[A-Za-z]:/", parsed):
            source = parsed
        else:
            source = "/" + parsed
        rel = os.path.relpath(source, REPO).replace("\\", "/")
        exception_key = rel + "#" + item.get("id", "")
        state_exception_key = (exception_key + "@" + item["state"]
                               if item.get("state") else exception_key)
        label = "%s#%s%s" % (item["url"], item.get("id", ""),
                              " " + item["state"] if item.get("state") else "")
        if item.get("runtimeError"):
            errors.append(label + " raised runtime error: " + item["runtimeError"])
        elif not item["visible"]:
            errors.append(label + " is not visible")
        elif not item["painted"]:
            errors.append(label + " is blank")
        elif item["clipped"]:
            if state_exception_key in exceptions:
                exercised.add(state_exception_key)
            elif exception_key in exceptions:
                exercised.add(exception_key)
            else:
                errors.append(label + " paints against an edge with an interior gap")
    stale = sorted(key for key in exceptions
                   if key.rsplit("#", 1)[0] in requested and key not in exercised)
    errors.extend("stale canvas-render exception was not exercised: " + key
                  for key in stale)
    return errors


FIXTURES = os.path.join(REPO, "curriculum", "canvas-fixtures")
# Anti-aliasing and Chrome's own rasteriser move a boundary by a pixel and a
# colour's coverage by a fraction of a percent between versions. These are the
# loosest tolerances that still fail the thing the fixture exists to catch — a
# bar that ends somewhere else, a threshold line that moved, an annotation
# that was recoloured or deleted. A bar in this figure is 13 px tall and the
# two threshold lines sit 7 px apart, so 2 px cannot hide a moved line.
BBOX_TOLERANCE = 2
COUNT_TOLERANCE = 0.08


def fixture_path(path):
    unit = os.path.splitext(os.path.basename(path))[0]
    return os.path.join(FIXTURES, unit + ".json")


def fixture_for(paths, browser=None):
    """{canvas key: read-back} for the given lessons, from a real render."""
    out = {}
    for item in render_results(paths, browser=browser):
        if item.get("runtimeError") or not item.get("visible"):
            continue
        key = "%s@%s" % (item.get("id", ""), item.get("state") or "initial")
        out[key] = {"painted": item["painted"], "bbox": item["bbox"],
                    "ink": item.get("ink", [])}
    return out


def _compare_ink(key, expected, actual):
    errors = []
    want = {row["colour"]: row for row in expected}
    got = {row["colour"]: row for row in actual}
    for colour in sorted(set(want) | set(got)):
        if colour not in got:
            errors.append("%s: colour %s is gone (was %d px at %s)"
                          % (key, colour, want[colour]["n"],
                             want[colour]["bbox"]))
            continue
        if colour not in want:
            errors.append("%s: colour %s is new (%d px at %s)"
                          % (key, colour, got[colour]["n"], got[colour]["bbox"]))
            continue
        a, b = want[colour], got[colour]
        allowed = max(8, int(a["n"] * COUNT_TOLERANCE))
        if abs(a["n"] - b["n"]) > allowed:
            errors.append("%s: colour %s covers %d px, fixture records %d"
                          % (key, colour, b["n"], a["n"]))
        moved = [i for i in range(4)
                 if abs(a["bbox"][i] - b["bbox"][i]) > BBOX_TOLERANCE]
        if moved:
            errors.append("%s: colour %s extends to %s, fixture records %s"
                          % (key, colour, b["bbox"], a["bbox"]))
    return errors


def fixture_errors(paths, browser=None):
    """Compare a live render against the committed read-back fixtures.

    A lesson with no fixture is NOT silently skipped: it is reported, so the
    set of figures under read-back is visible rather than inferred.
    """
    errors, checked = [], 0
    for path in paths:
        stored = fixture_path(path)
        if not os.path.isfile(stored):
            errors.append("no read-back fixture for %s (expected %s)"
                          % (path, os.path.relpath(stored, REPO)))
            continue
        with open(stored, encoding="utf-8") as handle:
            expected = json.load(handle)
        actual = fixture_for([path], browser=browser)
        for key in sorted(set(expected) | set(actual)):
            if key not in actual:
                errors.append("%s: canvas state %r no longer renders"
                              % (path, key))
                continue
            if key not in expected:
                errors.append("%s: canvas state %r is new and unrecorded"
                              % (path, key))
                continue
            checked += 1
            errors += ["%s: %s" % (path, e) for e in
                       _compare_ink(key, expected[key]["ink"], actual[key]["ink"])]
    return errors, checked


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--record-fixture", action="store_true",
                        help="write the read-back fixture for these lessons")
    parser.add_argument("--check-fixture", action="store_true",
                        help="compare a live render against the fixtures")
    args = parser.parse_args(argv)
    if args.record_fixture and args.check_fixture:
        parser.error("--record-fixture and --check-fixture are exclusive")
    if args.record_fixture:
        os.makedirs(FIXTURES, exist_ok=True)
        for path in args.paths:
            data = fixture_for([path])
            with open(fixture_path(path), "w", encoding="utf-8",
                      newline="\n") as handle:
                json.dump(data, handle, indent=2, sort_keys=True)
                handle.write("\n")
            print("recorded %s (%d canvas state(s))"
                  % (os.path.relpath(fixture_path(path), REPO), len(data)))
        return 0
    if args.check_fixture:
        try:
            errors, checked = fixture_errors(args.paths)
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            print("FAIL " + str(exc))
            return 1
        for error in errors:
            print("FAIL " + error)
        print("%s canvas read-back: %d state(s) compared across %d lesson(s),"
              " %d difference(s)" % ("FAIL" if errors else "PASS", checked,
                                     len(args.paths), len(errors)))
        return 1 if errors else 0
    try:
        errors = render_errors(args.paths)
    except (RuntimeError, subprocess.TimeoutExpired) as exc:
        print("FAIL " + str(exc))
        return 1
    for error in errors:
        print("FAIL " + error)
    print("%s rendered %d lesson file(s)" % (
        "FAIL" if errors else "PASS", len(args.paths)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
