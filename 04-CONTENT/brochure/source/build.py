# Builds the brochure: brochure-src.html + assets/ -> sterling-brochure.html (self-contained) + PDF.
# Run from this folder: python3 build.py   (needs: pip install pillow playwright pypdf)
import base64, io, os
from PIL import Image
D = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(D, 'assets')
def font(n): return 'data:font/ttf;base64,' + base64.b64encode(open(os.path.join(A, 'fonts', n), 'rb').read()).decode()
def jpg(im, q=90):
    b = io.BytesIO(); im.convert('RGB').save(b, 'JPEG', quality=q); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
def b64(n, mime): return f'data:{mime};base64,' + base64.b64encode(open(os.path.join(A, n), 'rb').read()).decode()
s = open(os.path.join(D, 'brochure-src.html')).read()
rep = {'__F_IS_R__': font('InstrumentSans-Regular.ttf'), '__F_IS_B__': font('InstrumentSans-Bold.ttf'),
       '__F_SER_I__': font('InstrumentSerif-Italic.ttf'), '__F_SER_R__': font('InstrumentSerif-Regular.ttf'),
       '__F_GM__': font('GeistMono-Regular.ttf'),
       '__HERO__': jpg(Image.open(os.path.join(A, 'hero.png')), 94),
       '__LIFE__': jpg(Image.open(os.path.join(A, 'life.png')), 92),
       '__FLAT__': jpg(Image.open(os.path.join(A, 'flat.png')), 92)}
h = Image.open(os.path.join(A, 'headshot-source.jpeg'))
W, H = h.size; ch = int(.45 * H); w = int(ch * .8); x0 = int(.44 * W) - w // 2; y0 = int(.315 * H)
rep['__HEAD__'] = jpg(h.crop((x0, y0, x0 + w, y0 + ch)).resize((720, 900), Image.LANCZOS), 88)
rep['__IITB__'] = b64('iitb.svg', 'image/svg+xml')
sw = Image.open(os.path.join(A, 'swaayatt.png')).convert('RGBA'); sw.thumbnail((360, 360), Image.LANCZOS)
bb = io.BytesIO(); sw.save(bb, 'PNG', optimize=True); rep['__SWAY__'] = 'data:image/png;base64,' + base64.b64encode(bb.getvalue()).decode()
rep['__LPLOGO__'] = f'<img src="{b64("launchpilot.png", "image/png")}" alt="LaunchPilot logo">' if os.path.exists(os.path.join(A, 'launchpilot.png')) else ''
rep['__LPFULL__'] = b64('launchpilot_full.png', 'image/png')
rep['__QR__'] = b64('qr_wa.svg', 'image/svg+xml')
rep['__KIT__'] = jpg(Image.open(os.path.join(A, 'kit_annotated.png')), 92)
for k, v in rep.items(): s = s.replace(k, v)
out = os.path.join(D, 'sterling-brochure.html'); open(out, 'w').write(s)
from playwright.sync_api import sync_playwright
pdf = os.path.join(D, 'Sterling-Robotics-Academy-Brochure.pdf')
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.goto('file://' + out); pg.wait_for_timeout(1500)
    pg.pdf(path=pdf, prefer_css_page_size=True, print_background=True); b.close()
from pypdf import PdfReader, PdfWriter
wr = PdfWriter(clone_from=PdfReader(pdf))
wr.add_metadata({'/Title': 'Sterling Robotics Academy, 2026–27 Cohorts', '/Author': 'Swarit Bhardwaj', '/Subject': '12-week live robotics course, grades 6 to 12'})
wr.write(pdf); print('built', out, pdf)
