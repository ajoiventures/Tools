import pickle, base64, io, os
from PIL import Image

BASE = r'C:\Projects\Tools\Form Tool\Tree Service Form'
photos_dir = os.path.join(BASE, 'photos')

def b64(n, width=720, quality=65):
    path = os.path.join(photos_dir, f'card_{str(n).zfill(2)}.jpg')
    if not os.path.exists(path): return None
    img = Image.open(path).convert('RGB')
    w, h = img.size
    if w > width:
        img = img.resize((width, int(h*width/w)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=quality, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()

imgs = {n: b64(n) for n in range(1, 12)}

# card_12 lives as palm_by_pool.jpeg in the base dir
pool_path = os.path.join(BASE, 'palm_by_pool.jpeg')
if os.path.exists(pool_path):
    img = Image.open(pool_path).convert('RGB')
    w, h = img.size
    if w > 720:
        img = img.resize((720, int(h*720/w)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=65, optimize=True)
    imgs[12] = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
    print(f'card_12 encoded from palm_by_pool.jpeg')
else:
    imgs[12] = None
    print('palm_by_pool.jpeg not found')

print('Images encoded')

def photo_div(n, alt=''):
    src = imgs.get(n)
    if not src:
        return '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#888;font-size:13px">No photo</div>'
    return f'<img src="{src}" alt="{alt}" style="width:100%;height:100%;object-fit:cover;object-position:top;display:block">'

NAV_WOM = '''<div class="nav-bar">
  <a href="tree_service_approval.html">&#8592; Review Form</a>
  <span>|</span>
  <a href="quote_evaluation.html">Quote Evaluation</a>
</div>'''

NAV_EVAL = '''<div class="nav-bar">
  <a href="tree_service_approval.html">&#8592; Review Form</a>
  <span>|</span>
  <a href="wom_work_authorization.html">WOM Authorization</a>
</div>'''

SHARED_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#F5F3EF;color:#1a1a1a;font-size:15px}
.page{max-width:820px;margin:32px auto;padding:0 16px 64px}
.nav-bar{background:#5C4033;border-radius:12px;padding:12px 18px;margin-bottom:20px;display:flex;gap:12px;flex-wrap:wrap;align-items:center}
.nav-bar a{color:#fff;text-decoration:none;font-size:12px;font-weight:600;padding:6px 14px;border-radius:100px;background:rgba(255,255,255,.15)}
.nav-bar a:hover{background:rgba(255,255,255,.3)}
.nav-bar span{color:rgba(255,255,255,.5);font-size:12px;margin:0 2px}
.sec-head{font-size:11px;font-weight:700;letter-spacing:1px;color:#8D6E63;text-transform:uppercase;margin:24px 0 12px}
.item-card{background:#fff;border:1px solid #ddd8d0;border-radius:12px;overflow:hidden;margin-bottom:16px;box-shadow:0 1px 6px rgba(0,0,0,.05)}
.item-header{background:linear-gradient(to right,#F8F4EF,#fff);border-bottom:1px solid #e5e0d6;padding:11px 16px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.item-num{width:28px;height:28px;border-radius:50%;background:#5C4033;color:#fff;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0}
.item-title{font-size:14px;font-weight:700;flex:1;min-width:120px}
.item-loc{font-size:11px;color:#6b7280;width:100%;margin-top:-4px;padding-left:38px}
.item-body{display:grid;grid-template-columns:280px 1fr}
.item-photo{overflow:hidden;height:320px;background:#111;border-right:1px solid #ddd8d0}
.item-info{padding:14px 16px;display:flex;flex-direction:column;gap:10px}
.info-lbl{font-size:9px;font-weight:700;letter-spacing:1px;color:#8D6E63;text-transform:uppercase;margin-bottom:3px}
.info-txt{font-size:12px;line-height:1.6;color:#374151}
.work-list{list-style:none;display:flex;flex-direction:column;gap:5px}
.work-list li{font-size:13px;font-weight:400;color:#1a1a1a;background:#F8F4EF;border-left:3px solid #5C4033;border-radius:0 6px 6px 0;padding:6px 10px 6px 12px;line-height:1.5}
@media(max-width:580px){.item-body{grid-template-columns:1fr}.item-photo{border-right:none;border-bottom:1px solid #ddd8d0;height:240px}}
"""

# ─── WOM AUTHORIZATION ────────────────────────────────────────────────────────
# status: 'quoted' = already in #2509/#2510, 'addon' = being added in $3,200 offer, 'tbd' = needs pricing

wom_items = [
    (1,  'Fallen Palm — Front Driveway',          '📍 Front driveway',              'quoted', '#2509',
     'Fallen/downed palm in the front driveway. Roots exposed, tree fully toppled.',
     ['Remove downed palm from front yard', 'Full debris cleanup']),
    (2,  'Camphor Tree — Front Yard',             '📍 Front yard',                  'quoted', '#2509',
     'Large Camphor tree with marked branches and circled sucker growth throughout the canopy.',
     ['Prune back marked Camphor limbs', 'Remove interior sucker growth and dead limbs']),
    (3,  'Norfolk Pine Removal + Stump Grinding', '📍 Backyard, left fence line',   'quoted', '#2510',
     'Norfolk Pine heavily browned along the left fence line. Full removal plus stump grinding.',
     ['Complete removal of Norfolk Pine', 'Stump grinding to ground level', 'Full debris cleanup']),
    (4,  'Small Dead Tree',                       '📍 Backyard, in front of Norfolk Pine', 'addon', 'Add-on',
     'Small fully dead tree with no foliage directly in front of the Norfolk Pines. Circled for full removal.',
     ['Full removal of small dead tree', 'Stump removal or grinding to ground level', 'Full debris cleanup']),
    (5,  'Dead Yucca Palm',                       '📍 Front left corner of fence',  'addon', 'Add-on',
     'Dead Yucca Palm in the front left fence corner. Circled for full removal including root and base.',
     ['Full removal of dead Yucca Palm', 'Remove base and root to ground level']),
    (6,  'Driveway Oak Overhang (Neighbor\'s)',   '📍 Front driveway edge',         'addon', 'Add-on',
     "Limbs from neighbor's oak hang over the driveway. Trim to restore vehicle clearance.",
     ["Trim overhanging oak limbs from neighbor's tree at driveway edge", 'Raise clearance to safe vehicle height']),
    (7,  'Roadside Palm Debris Hauling',          '📍 Roadside / front of property','tbd',   'Price TBD',
     'Pile of palm debris at the roadside left by a third party. Hauling only — no cutting involved.',
     ['Haul and dispose of existing roadside palm debris pile']),
    (8,  'Cedar Tree — Right Side of House',      '📍 Right side yard',             'quoted', '#2509',
     'Cedar along the right side yard. Circled dead lower limbs for removal.',
     ['Remove dead lower limb on Cedar tree at the right side']),
    (9,  'Front Right Oak Tree',                  '📍 Front right side of house',   'quoted', '#2509',
     'Laurel Oak at the front of the home. Canopy to be raised; lower limbs and sucker growth circled.',
     ['Raise canopy on Laurel oak at the front of the home', 'Remove lower hanging branches']),
    (10, 'Backyard Laurel Oak',                   '📍 Back left corner of house',   'quoted', '#2509',
     'Large Laurel Oak at the back left corner. Lower hanging limbs and interior sucker growth circled.',
     ['Weight reduction pruning on Laurel oak', 'Remove lower hanging limbs around perimeter',
      'Remove interior sucker growth for wind mitigation']),
    (11, 'Smaller Front-Left Fence Tree',         '📍 Front left side, behind fence', 'addon', 'Add-on',
     'Smaller tree at the front left fence. Branches growing into fence; sucker growth creeping over panels.',
     ['Trim branches growing into fence line', 'Remove sucker growth from fence perimeter']),
    (12, 'Palm by the Pool',                      '📍 Backyard pool and patio',     'tbd',   'Price TBD',
     'Palm tree beside the backyard pool and patio. Site visit needed to assess condition and scope.',
     ['Assess palm condition and provide scope at site visit', 'Trim, remove, or prune per assessment']),
]

STATUS_BADGE = {
    'quoted': ('background:#DCFCE7;color:#166534;border:1px solid #BBF7D0', '&#10003; In Estimate'),
    'addon':  ('background:#FEF3C7;color:#92400e;border:1px solid #FDE68A', '+ Add to Scope'),
    'tbd':    ('background:#DBEAFE;color:#1d4ed8;border:1px solid #BFDBFE', '&#128203; Price Needed'),
}

def wom_card(num, title, loc, status, ref, desc, scope):
    items_html = ''.join(f'<li>{s}</li>' for s in scope)
    badge_style, badge_label = STATUS_BADGE[status]
    ref_style = 'background:#F0FDF4;color:#166534;border:1px solid #BBF7D0' if status == 'quoted' else \
                'background:#FEF9C3;color:#78350f;border:1px solid #FDE68A' if status == 'addon' else \
                'background:#EFF6FF;color:#1d4ed8;border:1px solid #BFDBFE'
    checkbox = '<input type="checkbox" checked style="width:16px;height:16px;accent-color:#166534;margin-right:8px;vertical-align:middle">Authorized' \
        if status == 'quoted' else \
        '<input type="checkbox" style="width:16px;height:16px;accent-color:#92400e;margin-right:8px;vertical-align:middle"><span style="color:#92400e">Confirm add-on with WOM</span>' \
        if status == 'addon' else \
        '<input type="checkbox" style="width:16px;height:16px;accent-color:#1d4ed8;margin-right:8px;vertical-align:middle"><span style="color:#1d4ed8">Pending price from WOM</span>'
    return f'''<div class="item-card">
  <div class="item-header">
    <div class="item-num">{str(num).zfill(2)}</div>
    <div class="item-title">{title}</div>
    <span style="font-size:10px;font-weight:700;padding:3px 9px;border-radius:100px;{ref_style}">{ref}</span>
    <span style="font-size:10px;font-weight:700;padding:3px 9px;border-radius:100px;{badge_style}">{badge_label}</span>
    <div class="item-loc">{loc}</div>
  </div>
  <div class="item-body">
    <div class="item-photo">{photo_div(num, title)}</div>
    <div class="item-info">
      <div><div class="info-lbl">Description</div><p class="info-txt">{desc}</p></div>
      <div><div class="info-lbl">Work scope</div><ul class="work-list">{items_html}</ul></div>
      <div style="margin-top:auto;padding-top:10px;border-top:1px solid #f0ece5;font-size:13px;font-weight:600;color:#374151">{checkbox}</div>
    </div>
  </div>
</div>'''

wom_cards_html = ''.join(wom_card(*item) for item in wom_items)

wom_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Quote Update Request — Word of Mouth Tree Service</title>
<style>
{SHARED_CSS}
.hero{{background:#fff;border:1px solid #ddd8d0;border-radius:14px;padding:24px 28px;margin-bottom:20px;box-shadow:0 2px 10px rgba(0,0,0,.06)}}
.hero-top{{display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;margin-bottom:18px}}
.hero h1{{font-size:20px;font-weight:700}}
.hero-sub{{font-size:13px;color:#6b7280;margin-top:2px}}
.parties{{display:grid;grid-template-columns:1fr 1fr;gap:20px;border-top:1px solid #e5e0d6;padding-top:16px}}
@media(max-width:500px){{.parties{{grid-template-columns:1fr}}}}
.p-lbl{{font-size:10px;font-weight:700;letter-spacing:1px;color:#8D6E63;text-transform:uppercase;margin-bottom:5px}}
.p-name{{font-size:14px;font-weight:600;margin-bottom:2px}}
.p-det{{font-size:12px;color:#6b7280;line-height:1.7}}
.sum-row{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:20px}}
@media(max-width:540px){{.sum-row{{grid-template-columns:repeat(2,1fr)}}}}
.sum-box{{background:#fff;border:1px solid #ddd8d0;border-radius:10px;padding:12px 14px;text-align:center}}
.sum-box.highlight{{border:2px solid #166534;background:#F0FDF4}}
.sum-lbl{{font-size:10px;font-weight:700;letter-spacing:.8px;color:#8D6E63;text-transform:uppercase;margin-bottom:3px}}
.sum-val{{font-size:18px;font-weight:700}}
.sum-sub{{font-size:11px;color:#6b7280;margin-top:2px}}
.offer-banner{{background:linear-gradient(135deg,#1a3a2a,#166534);color:#fff;border-radius:12px;padding:18px 22px;margin-bottom:20px}}
.offer-banner h2{{font-size:16px;font-weight:700;margin-bottom:6px}}
.offer-banner p{{font-size:13px;line-height:1.6;opacity:.9}}
.offer-script{{background:rgba(255,255,255,.1);border-left:3px solid rgba(255,255,255,.4);border-radius:0 8px 8px 0;padding:11px 14px;margin-top:10px;font-size:13px;font-style:italic;line-height:1.6}}
.legend{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}}
.leg{{font-size:11px;font-weight:600;padding:4px 10px;border-radius:100px}}
.totals{{background:#fff;border:1px solid #ddd8d0;border-radius:12px;padding:18px 22px;margin:20px 0}}
.tot-row{{display:flex;justify-content:space-between;font-size:13px;color:#374151;padding:6px 0;border-bottom:1px solid #f0ece5}}
.tot-row.grand{{border-bottom:none;font-size:17px;font-weight:700;color:#1a1a1a;padding-top:14px}}
.tot-row.addon{{color:#92400e}}
.sig-card{{background:#fff;border:1px solid #ddd8d0;border-radius:12px;padding:22px;margin-bottom:20px}}
.sig-title{{font-size:15px;font-weight:700;margin-bottom:5px}}
.sig-txt{{font-size:13px;color:#6b7280;line-height:1.6;margin-bottom:18px}}
.sig-grid{{display:grid;grid-template-columns:2fr 1fr;gap:16px}}
@media(max-width:460px){{.sig-grid{{grid-template-columns:1fr}}}}
.sig-lbl{{font-size:10px;font-weight:700;letter-spacing:.8px;color:#8D6E63;text-transform:uppercase;display:block;margin-bottom:6px}}
.sig-line{{border:none;border-bottom:1.5px solid #5C4033;width:100%;padding:7px 4px;font-size:14px;background:transparent;outline:none;color:#1a1a1a}}
.print-btn{{display:block;width:100%;padding:15px;background:#166534;color:#fff;font-size:15px;font-weight:700;border:none;border-radius:10px;cursor:pointer;text-align:center}}
.print-btn:hover{{background:#14532D}}
@media print{{.nav-bar,.print-btn,.offer-banner{{display:none}}body{{background:#fff}}.page{{margin:0;padding:0}}}}
</style>
</head>
<body>
<div class="page">
{NAV_WOM}
<div class="hero">
  <div class="hero-top">
    <div><h1>Quote Update Request — All 12 Items</h1><div class="hero-sub">Word of Mouth Tree Service &middot; Please review and provide updated pricing</div></div>
    <div style="background:#92400e;color:#fff;font-size:11px;font-weight:700;letter-spacing:.8px;padding:6px 14px;border-radius:100px">ACTION NEEDED</div>
  </div>
  <div class="parties">
    <div>
      <div class="p-lbl">Property Owner</div>
      <div class="p-name">Paul Irumudomon</div>
      <div class="p-det">2509 Ives Avenue, Orlando FL 32806<br>(407) 717-0861</div>
    </div>
    <div>
      <div class="p-lbl">Contractor</div>
      <div class="p-name">Word of Mouth Tree Service</div>
      <div class="p-det">441 Baker Ave, Altamonte Springs FL 32714<br>(407) 862-9779 &middot; atollman.womtree@gmail.com</div>
    </div>
  </div>
</div>

<div class="offer-banner">
  <h2>&#128203; Request: Updated Quote for All 12 Items</h2>
  <p>Your current estimates (#2509 + #2510) cover 6 of the 12 items on this property for $3,000. I would like to give you the full job. Please review the 6 add-on items below, price items #07 and #12 on your next visit, and send me an updated all-in quote. My proposed budget for all 12 items is <strong>$3,200</strong>.</p>
  <div class="offer-script">Please reply with a revised quote covering all 12 items listed below. I am ready to move forward as soon as I receive your updated pricing.</div>
</div>

<div class="sum-row">
  <div class="sum-box"><div class="sum-lbl">Current Quote</div><div class="sum-val">$3,000</div><div class="sum-sub">6 items — #2509+#2510</div></div>
  <div class="sum-box highlight"><div class="sum-lbl">Proposed Budget</div><div class="sum-val" style="color:#166534">$3,200</div><div class="sum-sub">All 12 items</div></div>
  <div class="sum-box"><div class="sum-lbl">Total Items</div><div class="sum-val">12</div><div class="sum-sub">Full property scope</div></div>
  <div class="sum-box"><div class="sum-lbl">Add-Ons to Price</div><div class="sum-val">6</div><div class="sum-sub">Items 04 05 06 07 11 12</div></div>
</div>

<div class="legend">
  <span class="leg" style="background:#DCFCE7;color:#166534">&#10003; In Estimate — already quoted</span>
  <span class="leg" style="background:#FEF3C7;color:#92400e">+ Add-on — include in $3,200 offer</span>
  <span class="leg" style="background:#DBEAFE;color:#1d4ed8">&#128203; Price Needed — WOM to confirm</span>
</div>

<div class="sec-head">Complete 12-item work scope</div>
{wom_cards_html}

<div class="totals">
  <div class="tot-row"><span>Estimate #2509 — Pruning &amp; fallen palm (Items 01, 02, 08, 09, 10)</span><span>$1,500.00</span></div>
  <div class="tot-row"><span>Estimate #2510 — Norfolk Pine removal + stump (Item 03)</span><span>$1,500.00</span></div>
  <div class="tot-row addon"><span>Add-ons — Items 04, 05, 06, 11</span><span>Your price: $________</span></div>
  <div class="tot-row addon"><span>Items 07 &amp; 12 — price at site visit</span><span>Your price: $________</span></div>
  <div class="tot-row grand"><span>Updated All-In Total (please provide)</span><span>$____________</span></div>
</div>

<div class="sig-card">
  <div class="sig-title">&#9993; Please Reply With Your Updated Quote</div>
  <div class="sig-txt">Review the 12 items and photos above. Reply to this email with:<br><br>
  1. Confirmation of which add-on items (04, 05, 06, 11) you can include<br>
  2. Pricing for items #07 (roadside debris hauling) and #12 (pool palm) after site review<br>
  3. Your updated all-in total for all items you can cover<br><br>
  My proposed budget for the full scope is <strong>$3,200</strong>. I am ready to move forward immediately upon receiving your revised quote. Payment by check on completion.</div>
  <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:8px;padding:12px 16px;margin-top:12px;font-size:13px;color:#14532D">
    <strong>Reply to:</strong> Paul Irumudomon &nbsp;&middot;&nbsp; (407) 717-0861 &nbsp;&middot;&nbsp; ajoiventures@gmail.com
  </div>
</div>
<button class="print-btn" onclick="window.print()">Save as PDF / Print to attach to email</button>
</div>
</body>
</html>'''

wom_out = os.path.join(BASE, 'wom_work_authorization.html')
with open(wom_out, 'w', encoding='utf-8') as f:
    f.write(wom_html)
print(f'WOM: {os.path.getsize(wom_out)//1024}KB')

# ─── QUOTE EVALUATION ─────────────────────────────────────────────────────────

def co_row(name, cls, detail):
    colors = {'covered':'background:#F0FDF4;color:#166534', 'missing':'background:#FFF1F2;color:#9f1239',
              'unclear':'background:#FFFBEB;color:#92400e', 'none':'background:#F9FAFB;color:#9ca3af'}
    st = colors.get(cls, colors['none'])
    return f'<div style="display:flex;justify-content:space-between;font-size:12px;padding:5px 9px;border-radius:6px;margin-bottom:4px;{st}"><strong style="font-size:11px">{name}</strong><span style="font-size:11px">{detail}</span></div>'

def pill(txt, color):
    colors = {'r':'background:#FEE2E2;color:#991b1b', 'g':'background:#DCFCE7;color:#166534',
              'b':'background:#DBEAFE;color:#1d4ed8', 'a':'background:#FEF3C7;color:#92400e'}
    return f'<span style="font-size:10px;font-weight:600;padding:2px 8px;border-radius:100px;{colors[color]}">{txt}</span>'

def eval_card(num, title, loc, pills_html, desc, co_rows_html, unquoted=False):
    photo_html = photo_div(num, title) if imgs.get(num) else '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#888;font-size:13px">No photo yet</div>'
    warning = '<div style="background:#FEF3C7;border:1px solid #FDE68A;border-radius:8px;padding:8px 12px;font-size:12px;color:#92400e;font-weight:500">&#9888; Ask all 3 companies to price this before signing</div>' if unquoted else ''
    return f'''<div class="item-card">
  <div class="item-header">
    <div class="item-num">{str(num).zfill(2)}</div>
    <div class="item-title">{title}</div>
    <div style="display:flex;gap:5px;flex-wrap:wrap">{pills_html}</div>
    <div class="item-loc">{loc}</div>
  </div>
  <div class="item-body">
    <div class="item-photo">{photo_html}</div>
    <div class="item-info">
      <div><div class="info-lbl">Situation</div><p class="info-txt">{desc}</p></div>
      <div><div class="info-lbl">Coverage</div>{co_rows_html}</div>
      {warning}
    </div>
  </div>
</div>'''

eval_items = [
    eval_card(1, 'Fallen Palm — Front Driveway', '📍 Front driveway — HIGH PRIORITY',
        pill('ABT missed','r')+pill('WOM ✓','g')+pill('J&J ✓ $200','g'),
        'Palm fully toppled in the front driveway. Roots exposed. Safety hazard blocking driveway access.',
        co_row('ABT','missing','✗ Not quoted — confirm if included') +
        co_row('WOM #2509','covered','✓ Included in $1,500 bundle') +
        co_row('J&J','covered','✓ $200 for 2 fallen palms')),
    eval_card(2, 'Camphor Tree — Front Yard', '📍 Front yard — MEDIUM PRIORITY',
        pill('ABT ✓ $1,500','g')+pill('WOM ✓','g')+pill('J&J unclear','a'),
        'Large Camphor tree with marked branches and circled sucker growth throughout the canopy.',
        co_row('ABT','covered','✓ $1,500 — branches + sucker growth') +
        co_row('WOM #2509','covered','✓ Included in $1,500 bundle') +
        co_row('J&J','unclear','? Confirm if in $1,000 trimming bundle')),
    eval_card(3, 'Norfolk Pine Removal + Stump Grinding', '📍 Backyard, left fence — HIGH PRIORITY',
        pill('ABT $1,550','g')+pill('WOM $1,500','g')+pill('J&J $2,150 — high','a'),
        'Norfolk Pine heavily browned along the left fence. All 3 quote this — but J&J charges $600 more.',
        co_row('ABT','covered','✓ $1,400 removal + $150 stump = $1,550') +
        co_row('WOM #2510','covered','✓ $1,500 removal + stump combined') +
        co_row('J&J','unclear','✓ $2,000 + $150 stump = $2,150 — negotiate down')),
    eval_card(4, 'Small Dead Tree (Near Norfolk Pine)', '📍 Backyard, in front of Norfolk Pine — MEDIUM PRIORITY',
        pill('ABT ✓ FREE','g')+pill('WOM missing','r')+pill('J&J ✓ incl.','g'),
        'Small fully dead tree with no foliage, directly in front of the Norfolk Pines. Circled for full removal.',
        co_row('ABT','covered','✓ FREE — bundled with Yucca/dead tree line item') +
        co_row('WOM','missing','✗ Not quoted — ask to add') +
        co_row('J&J','covered','✓ Included in "2 small dead trees" $200')),
    eval_card(5, 'Dead Yucca Palm — Front Left Fence Corner', '📍 Front left corner of fence — MEDIUM PRIORITY',
        pill('ABT ✓ FREE','g')+pill('WOM missing','r')+pill('J&J ✓ incl.','g'),
        'Dead Yucca Palm in the front left fence corner. Circled for full removal including root and base.',
        co_row('ABT','covered','✓ FREE — bundled with small dead tree') +
        co_row('WOM','missing','✗ Not quoted — ask to add') +
        co_row('J&J','covered','✓ Included in "2 small dead trees" $200')),
    eval_card(6, 'Driveway Oak Overhang (Neighbor\'s Tree)', '📍 Front driveway edge — HIGH PRIORITY',
        pill('ABT ✓ $100','g')+pill('WOM missing','r')+pill('J&J missing','r'),
        'Limbs from neighbor\'s oak hang over the driveway. Circled for trimming to raise vehicle clearance.',
        co_row('ABT','covered','✓ $100 — only company that quoted this') +
        co_row('WOM','missing','✗ Not quoted — ask to add (~$100)') +
        co_row('J&J','missing','✗ Not quoted — ask to add')),
    eval_card(7, 'Roadside Palm Debris Hauling', '📍 Roadside / front of property — MEDIUM PRIORITY',
        pill('No one quoted','a'),
        'Pile of palm debris at the roadside left by a third party. Homeowner wants hauling only — no cutting.',
        co_row('ABT','none','✗ Not quoted — ask to price') +
        co_row('WOM','none','✗ Not quoted — ask to price') +
        co_row('J&J','none','✗ Not quoted — ask to price'), unquoted=True),
    eval_card(8, 'Cedar Tree — Right Side of House', '📍 Right side yard — LOWER PRIORITY',
        pill('ABT ✓ $400','g')+pill('WOM ✓','g')+pill('J&J unclear','a'),
        'Cedar along the right side yard. Circled area shows dead lower limbs to be removed.',
        co_row('ABT','covered','✓ $400 — remove dead lower limbs') +
        co_row('WOM #2509','covered','✓ Included in $1,500 bundle') +
        co_row('J&J','unclear','? Confirm if in $1,000 trimming bundle')),
    eval_card(9, 'Front Right Oak Tree', '📍 Front right side of house — MEDIUM PRIORITY',
        pill('ABT ✓ $800','g')+pill('WOM ✓','g')+pill('J&J ✓','g'),
        'Oak on the front right. Two lower hanging branches circled plus sucker growth in the canopy.',
        co_row('ABT','covered','✓ $800 — lower branches + sucker growth + dead limbs') +
        co_row('WOM #2509','covered','✓ Raise canopy on Laurel oak at front of home') +
        co_row('J&J','covered','✓ Included in $1,000 trimming bundle')),
    eval_card(10, 'Backyard Laurel Oak Tree', '📍 Back left corner of house — LOWER PRIORITY',
        pill('ABT ✓ $750','g')+pill('WOM ✓','g')+pill('J&J ✓','g'),
        'Laurel Oak at the back left corner. Lower hanging limbs and interior sucker growth circled.',
        co_row('ABT','covered','✓ $750 — lower limbs + sucker growth') +
        co_row('WOM #2509','covered','✓ Weight reduction pruning on back left Laurel oak') +
        co_row('J&J','covered','✓ Included in $1,000 trimming bundle')),
    eval_card(11, 'Smaller Front-Left Fence Tree', '📍 Front left side, behind fence — LOWER PRIORITY',
        pill('ABT ✓ $150','g')+pill('WOM missing','r')+pill('J&J missing','r'),
        'Smaller tree at the front left fence. Branches growing into fence; sucker growth creeping over panels.',
        co_row('ABT','covered','✓ $150 — trim branches + remove sucker growth') +
        co_row('WOM','missing','✗ Not quoted — ask to add (~$150)') +
        co_row('J&J','missing','✗ Not quoted — ask to add')),
    eval_card(12, 'Palm by the Pool', '📍 Backyard pool and patio — LOWER PRIORITY',
        pill('No one quoted','a')+pill('New item','b'),
        'Palm tree beside the backyard pool and patio. New item — no contractor has assessed or quoted it yet.',
        co_row('ABT','none','✗ Not quoted — needs site visit') +
        co_row('WOM','none','✗ Not quoted — needs site visit') +
        co_row('J&J','none','✗ Not quoted — needs site visit'), unquoted=True),
]

eval_cards_html = ''.join(eval_items)

def pb_card(name, contact, base, target, target_cls, ask, steps):
    steps_html = ''.join(f'<li style="font-size:12px;color:#6b7280;line-height:1.7;margin-bottom:2px">{s}</li>' for s in steps)
    target_colors = {'g':'background:#DCFCE7;color:#166534','a':'background:#FEF3C7;color:#92400e','b':'background:#DBEAFE;color:#1d4ed8'}
    tc = target_colors[target_cls]
    return f'''<div style="background:#fff;border:1px solid #ddd8d0;border-radius:12px;padding:18px 20px;margin-bottom:14px">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:8px">
    <div><div style="font-size:14px;font-weight:700">{name}</div><div style="font-size:11px;color:#6b7280">{contact} &middot; Base: {base}</div></div>
    <span style="font-size:12px;font-weight:700;padding:4px 12px;border-radius:100px;{tc}">Target: {target}</span>
  </div>
  <div style="background:#F8F4EF;border-left:3px solid #5C4033;border-radius:0 8px 8px 0;padding:10px 14px;font-size:13px;font-style:italic;color:#374151;margin-bottom:10px;line-height:1.6">"{ask}"</div>
  <ul style="padding-left:1.1rem;list-style:disc">{steps_html}</ul>
</div>'''

playbook_html = pb_card(
    '1. Word of Mouth Tree Service',
    '(407) 862-9779 &middot; atollman.womtree@gmail.com', '$3,000 / 6 items',
    '$3,200 all-in', 'g',
    'I want to give you the job. Can you add the missing items (#04, #05, #06, #07, #11, #12) to your existing scope for a flat $3,200 all-in?',
    ['Items #04, #05, #06, #11 cost only <strong style="color:#1a1a1a">$650 at ABT</strong> — WOM can likely absorb them to win the full job.',
     'Ask them to price <strong style="color:#1a1a1a">#07 roadside hauling</strong> and <strong style="color:#1a1a1a">#12 pool palm</strong> at the same call.',
     'Request a <strong style="color:#1a1a1a">single combined invoice</strong> for estimates #2509 + #2510 — bundling often gets a small discount.',
     'Pay by <strong style="color:#1a1a1a">check or ACH</strong> — avoids their 2.9% credit card surcharge (~$90 savings).',
     'Offer to <strong style="color:#1a1a1a">sign today</strong> if they hit $3,200 — companies prioritize quick closes.']
) + pb_card(
    '2. ABT Tree Care',
    '(386) 331-5110 &middot; treecareabt@gmail.com', '$4,500 / 9 items',
    '$3,500 all-in', 'a',
    'Word of Mouth quoted me $3,200 for all 12 items. You cover the most work — match $3,500 and we sign today.',
    ['They moved $5,250 → $4,500 already — <strong style="color:#1a1a1a">another $500–$1,000 drop is realistic</strong>.',
     'They missed <strong style="color:#1a1a1a">#01 fallen palm</strong> entirely — ask if it\'s included or add it free.',
     'They already give <strong style="color:#1a1a1a">#04 and #05 free</strong> — proof they\'re flexible on price.',
     'Ask for a <strong style="color:#1a1a1a">cash/check price</strong> — often unlocks an extra 5–10% off.',
     'Get them to price <strong style="color:#1a1a1a">#07 and #12</strong> for a true all-in number.']
) + pb_card(
    '3. J&J Lawn &amp; Tree Service',
    '(407) 774-2076 &middot; OfficeJJtree@gmail.com &middot; ISA Certified FL-5734A', '$3,550 / 8 items',
    '$3,100 all-in', 'b',
    'Your Norfolk Pine is $600 above my other quotes. Match $1,500 for the Norfolk Pine, confirm Camphor and Cedar are in scope, and add the missing items — let\'s do $3,100 all-in.',
    ['<strong style="color:#1a1a1a">Norfolk Pine at $2,150</strong> is the biggest overcharge — ABT: $1,550, WOM: $1,500. Dropping to $1,500 saves $650.',
     'Confirm <strong style="color:#1a1a1a">Camphor (#02) and Cedar (#08)</strong> are in the $1,000 trimming bundle — if not, add $1,500–$1,900.',
     'Ask to add <strong style="color:#1a1a1a">#06 driveway oak, #07 debris, #11 fence tree, #12 pool palm</strong>.',
     '<strong style="color:#1a1a1a">ISA certification</strong> is real value — worth a small premium if the price gap closes.',
     'Pay by <strong style="color:#1a1a1a">Zelle</strong> (their preferred) — avoids the 3% card fee.']
)

eval_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tree Service Quote Evaluation — All 12 Items</title>
<style>
{SHARED_CSS}
.hero{{background:#fff;border:1px solid #ddd8d0;border-radius:14px;padding:24px 28px;margin-bottom:20px;box-shadow:0 2px 10px rgba(0,0,0,.06)}}
.hero h1{{font-size:20px;font-weight:700;margin-bottom:4px}}
.hero p{{font-size:13px;color:#6b7280;line-height:1.6}}
.co-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:24px}}
@media(max-width:580px){{.co-grid{{grid-template-columns:1fr}}}}
.co-card{{background:#fff;border:1px solid #ddd8d0;border-radius:12px;padding:16px}}
.co-card.best{{border:2px solid #166534}}
.tbl-wrap{{overflow-x:auto;background:#fff;border:1px solid #ddd8d0;border-radius:12px;margin-bottom:24px}}
table{{width:100%;border-collapse:collapse;font-size:12px;min-width:520px}}
th{{padding:9px 10px;font-size:10px;font-weight:700;color:#6b7280;border-bottom:1.5px solid #e5e0d6;text-align:left;background:#F8F4EF;white-space:nowrap}}
th.c{{text-align:center}}
td{{padding:7px 10px;border-bottom:0.5px solid #f0ece5;vertical-align:middle;color:#1a1a1a}}
td.c{{text-align:center}}
tr:last-child td{{border-bottom:none}}
.ts td{{background:#F8F4EF;font-size:10px;font-weight:700;color:#8D6E63;letter-spacing:.6px;text-transform:uppercase;padding:5px 10px}}
.tf td{{background:#F8F4EF;font-weight:700;font-size:12px}}
.y{{color:#166534;font-weight:600}}.n{{color:#b91c1c}}.q{{color:#b45309}}
.nt{{font-size:10px;color:#6b7280}}
.verdict{{background:#1a3a2a;color:#d1fae5;border-radius:12px;padding:20px 22px;margin-top:8px}}
</style>
</head>
<body>
<div class="page">
{NAV_EVAL}
<div class="hero">
  <h1>Tree Service Quote Evaluation — All 12 Items</h1>
  <p>Owner approved all 12 items. No single company covers everything. Compare all three quotes item by item, see the true all-in price, and use the negotiation scripts below.</p>
</div>

<div class="sec-head">Company quotes at a glance</div>
<div class="co-grid">
  <div class="co-card">
    <div style="font-size:13px;font-weight:700;margin-bottom:2px">ABT Tree Care</div>
    <div style="font-size:22px;font-weight:700">$4,500</div>
    <div style="font-size:12px;color:#6b7280;margin-bottom:6px">9 of 12 items &middot; after $750 discount</div>
    <div style="font-size:12px;font-weight:500;background:#FEE2E2;color:#991b1b;padding:5px 8px;border-radius:6px">True all-in: ~$5,100–5,500</div>
    <div style="font-size:11px;color:#6b7280;margin-top:8px;border-top:1px solid #f0ece5;padding-top:8px">(386) 331-5110<br>treecareabt@gmail.com</div>
  </div>
  <div class="co-card best">
    <div style="font-size:13px;font-weight:700;margin-bottom:2px">Word of Mouth <span style="font-size:10px;font-weight:700;background:#DCFCE7;color:#166534;padding:2px 8px;border-radius:100px;margin-left:4px">Lowest base</span></div>
    <div style="font-size:22px;font-weight:700">$3,000</div>
    <div style="font-size:12px;color:#6b7280;margin-bottom:6px">6 of 12 items &middot; #2509 + #2510</div>
    <div style="font-size:12px;font-weight:500;background:#FEF3C7;color:#92400e;padding:5px 8px;border-radius:6px">True all-in: ~$3,600–4,000</div>
    <div style="font-size:11px;color:#6b7280;margin-top:8px;border-top:1px solid #f0ece5;padding-top:8px">(407) 862-9779<br>atollman.womtree@gmail.com</div>
  </div>
  <div class="co-card">
    <div style="font-size:13px;font-weight:700;margin-bottom:2px">J&amp;J Lawn &amp; Tree <span style="font-size:10px;font-weight:700;background:#DBEAFE;color:#1d4ed8;padding:2px 8px;border-radius:100px;margin-left:4px">ISA Certified</span></div>
    <div style="font-size:22px;font-weight:700">$3,550</div>
    <div style="font-size:12px;color:#6b7280;margin-bottom:6px">8 of 12 items &middot; Proposal #68072</div>
    <div style="font-size:12px;font-weight:500;background:#FEF3C7;color:#92400e;padding:5px 8px;border-radius:6px">True all-in: ~$4,100–4,600</div>
    <div style="font-size:11px;color:#6b7280;margin-top:8px;border-top:1px solid #f0ece5;padding-top:8px">(407) 774-2076<br>OfficeJJtree@gmail.com</div>
  </div>
</div>

<div class="sec-head">Coverage by item — all 12</div>
<div class="tbl-wrap">
<table>
<thead><tr><th>#</th><th>Item</th><th class="c">ABT</th><th class="c">WOM</th><th class="c">J&amp;J</th><th>Note</th></tr></thead>
<tbody>
<tr class="ts"><td colspan="6">Removals</td></tr>
<tr><td>01</td><td>Fallen palm — front driveway</td><td class="c n">✗</td><td class="c y">✓</td><td class="c y">✓ $200</td><td class="nt" style="color:#b91c1c">ABT missed this</td></tr>
<tr><td>03</td><td>Norfolk Pine removal + stump</td><td class="c y">✓ $1,550</td><td class="c y">✓ $1,500</td><td class="c q">✓ $2,150</td><td class="nt">J&amp;J $600 over market</td></tr>
<tr><td>04</td><td>Small dead tree (near Norfolk Pine)</td><td class="c y">✓ FREE</td><td class="c n">✗</td><td class="c y">✓ incl.</td><td class="nt" style="color:#b91c1c">WOM missing</td></tr>
<tr><td>05</td><td>Dead Yucca Palm</td><td class="c y">✓ FREE</td><td class="c n">✗</td><td class="c y">✓ incl.</td><td class="nt" style="color:#b91c1c">WOM missing</td></tr>
<tr class="ts"><td colspan="6">Trimming / Pruning</td></tr>
<tr><td>02</td><td>Camphor tree — front yard</td><td class="c y">✓ $1,500</td><td class="c y">✓ incl.</td><td class="c q">?</td><td class="nt">Confirm J&amp;J scope</td></tr>
<tr><td>06</td><td>Driveway oak overhang (neighbor's)</td><td class="c y">✓ $100</td><td class="c n">✗</td><td class="c n">✗</td><td class="nt" style="color:#b91c1c">Only ABT quoted</td></tr>
<tr><td>08</td><td>Cedar tree — right side</td><td class="c y">✓ $400</td><td class="c y">✓ incl.</td><td class="c q">?</td><td class="nt">Confirm J&amp;J scope</td></tr>
<tr><td>09</td><td>Front right oak tree</td><td class="c y">✓ $800</td><td class="c y">✓ incl.</td><td class="c y">✓ incl.</td><td class="nt" style="color:#166534">All 3 cover</td></tr>
<tr><td>10</td><td>Backyard Laurel Oak</td><td class="c y">✓ $750</td><td class="c y">✓ incl.</td><td class="c y">✓ incl.</td><td class="nt" style="color:#166534">All 3 cover</td></tr>
<tr><td>11</td><td>Smaller front-left fence tree</td><td class="c y">✓ $150</td><td class="c n">✗</td><td class="c n">✗</td><td class="nt" style="color:#b91c1c">Only ABT quoted</td></tr>
<tr class="ts"><td colspan="6">Unquoted by all — must add</td></tr>
<tr><td>07</td><td>Roadside palm debris hauling</td><td class="c n">✗</td><td class="c n">✗</td><td class="c n">✗</td><td class="nt" style="color:#92400e">Ask all 3 to price</td></tr>
<tr><td>12</td><td>Palm by the pool</td><td class="c n">✗</td><td class="c n">✗</td><td class="c n">✗</td><td class="nt" style="color:#1d4ed8">New — no one seen it</td></tr>
<tr class="tf"><td colspan="2">Items covered</td><td class="c">9/12</td><td class="c">6/12</td><td class="c">8/12</td><td></td></tr>
</tbody>
</table>
</div>

<div class="sec-head">All 12 items — photos &amp; company coverage</div>
{eval_cards_html}

<div class="sec-head">Negotiation playbook — actions per company</div>
{playbook_html}

<div class="verdict">
  <div style="font-size:13px;font-weight:700;letter-spacing:.5px;text-transform:uppercase;color:#6ee7b7;margin-bottom:10px">Best move — in order</div>
  <ol style="padding-left:1.1rem;list-style:decimal">
    <li style="font-size:13px;line-height:1.8;margin-bottom:2px;color:#d1fae5"><strong style="color:#fff">Call Word of Mouth first</strong> — ask for all 12 items at $3,200. If yes, you save $1,300 vs ABT.</li>
    <li style="font-size:13px;line-height:1.8;margin-bottom:2px;color:#d1fae5">If WOM won't add the missing items, <strong style="color:#fff">call ABT</strong> and show them the WOM number. Push for $3,500 all-in.</li>
    <li style="font-size:13px;line-height:1.8;margin-bottom:2px;color:#d1fae5">Use <strong style="color:#fff">J&J as backup</strong> — if they confirm Camphor + Cedar and drop Norfolk Pine to $1,500, they hit ~$3,050 with ISA credentials.</li>
    <li style="font-size:13px;line-height:1.8;color:#d1fae5">Before signing anyone, <strong style="color:#fff">send a photo of the pool palm (#12)</strong> and ask all three to price it.</li>
  </ol>
</div>
</div>
</body>
</html>'''

eval_out = os.path.join(BASE, 'quote_evaluation.html')
with open(eval_out, 'w', encoding='utf-8') as f:
    f.write(eval_html)
print(f'Eval: {os.path.getsize(eval_out)//1024}KB')
print('Done')
