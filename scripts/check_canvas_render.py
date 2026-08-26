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
  let n=0,minX=c.width,minY=c.height,maxX=-1,maxY=-1;
  const rows=new Uint8Array(c.height), cols=new Uint8Array(c.width);
  for(let y=0;y<c.height;y++)for(let x=0;x<c.width;x++)if(d[(y*c.width+x)*4+3]){
    n++; rows[y]=1; cols[x]=1; minX=Math.min(minX,x);maxX=Math.max(maxX,x);
    minY=Math.min(minY,y);maxY=Math.max(maxY,y);
  }
  const edge=minX<=1||minY<=1||maxX>=c.width-2||maxY>=c.height-2;
  const interiorGap=[...rows.slice(2,-2)].includes(0)||[...cols.slice(2,-2)].includes(0);
  return {painted:n,bbox:[minX,minY,maxX,maxY],clipped:!!(n&&edge&&interiorGap)};
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
    const f=document.createElement('iframe'); f.src=url; document.body.appendChild(f);
    await new Promise((ok,bad)=>{f.onload=ok;f.onerror=bad});
    await new Promise(ok=>setTimeout(ok,80));
    const doc=f.contentDocument;
    const canvases=[...doc.querySelectorAll('canvas')].filter(c=>
      c.getAttribute('aria-hidden')!=='true');
    for(const c of canvases) out.push({url,id:c.id,visible:visible(c),...pixels(c)});
    let interaction=0;
    for(const b of doc.querySelectorAll('button[onclick]')){
      if(/^check\s*\(/.test(b.getAttribute('onclick'))) continue;
      try{b.click()}catch(e){}
      interaction++;
      await new Promise(ok=>setTimeout(ok,40));
      for(const c of canvases) out.push({url,id:c.id,state:'after-click-'+interaction,visible:visible(c),...pixels(c)});
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
        budget = max(8000, len(paths) * 250)
        command = [browser, "--headless=new", "--disable-gpu", "--no-sandbox",
                   "--allow-file-access-from-files", "--disable-web-security",
                   "--virtual-time-budget=%d" % budget, "--dump-dom",
                   Path(page).as_uri()]
        result = subprocess.run(command, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=60)
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
        label = "%s#%s%s" % (item["url"], item.get("id", ""),
                              " after click" if item.get("state") else "")
        if not item["visible"]:
            errors.append(label + " is not visible")
        elif not item["painted"]:
            errors.append(label + " is blank")
        elif item["clipped"]:
            if exception_key in exceptions:
                exercised.add(exception_key)
            else:
                errors.append(label + " paints against an edge with an interior gap")
    stale = sorted(key for key in exceptions
                   if key.rsplit("#", 1)[0] in requested and key not in exercised)
    errors.extend("stale canvas-render exception was not exercised: " + key
                  for key in stale)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args(argv)
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
