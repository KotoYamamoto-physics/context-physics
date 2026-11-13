#!/usr/bin/env python3
"""生徒用 index.html から教師用 teacher/index.html を作る。
問題データ（D, FIG, SG）は生徒用ページのものをそのまま使うので、
生徒用ページを直したら、このスクリプトを実行し直すだけで教師用ページも新しくなる。
使い方: python3 tools/build_teacher.py
"""
import re, pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent
s = (root / 'index.html').read_text(encoding='utf-8')

def rep(a, b, count=1):
    global s
    n = s.count(a)
    if n != count:
        sys.exit(f'置換できません（{n}件）: {a[:60]}')
    s = s.replace(a, b)

rep('<title>身のまわりから考える物理</title>',
    '<title>身のまわりから考える物理 教師用</title>\n<meta name="robots" content="noindex,nofollow">')
rep('<h1><span class="nb">身のまわりから考える物理</span>　<span class="nb">物理基礎・物理</span></h1>', '<h1><span class="nb">身のまわりから考える物理</span>　<span class="nb">教師用</span></h1>')
s, k = re.subn(r'<div class="lead">.*?</div>',
    '''<div class="lead">
      <p>授業の準備に使う画面です。</p>
      <ul>
        <li>問題の「選ぶ」にチェックを入れると、<b>提示モード</b>（プロジェクターで1問ずつ映す）や、<b>ワークシートの印刷</b>（A4横・右側の解説を切り取って配る）に使えます。</li>
        <li>各問題の「提示」を押すと、その問題をすぐに映せます。</li>
        <li>「絞り込み ▼」から、科目・分野・難易度などで問題を絞り込めます。</li>
      </ul>
      <p>生徒用のページ：<a href="../">身のまわりから考える物理</a>（このページのリンクは、生徒には伝えないでください）</p>
    </div>''',
    s, count=1, flags=re.S)
if k != 1: sys.exit('lead が見つかりません')
# 教師用：選択肢ははじめから表示、解答は確認なしで開く
rep("let subj='all',dom='all',kw='',ord='subj',showCol=true,chAll=false,lv='0';",
    "let subj='all',dom='all',kw='',ord='subj',showCol=true,chAll=true,lv='0';")
rep('<button class="unused-toggle" id="ch-tg" aria-pressed="false">', '<button class="unused-toggle" id="ch-tg" aria-pressed="true">')
rep('if(thought.has(i)){open(i);return}', '{open(i);return}')
# 表示中の問題を記録
rep("let html='',lastB='',lastM='',n=0,nc=0;", "let html='',lastB='',lastM='',n=0,nc=0;vis=[];")
rep("    n++;\n    const chHtml", "    n++;vis.push(i);\n    const chHtml")
# 各問題に「選ぶ」「提示」
rep("""<td class="no">${String(r[13]).padStart(3,'0')}<br>${badge}</td>""",
    """<td class="no">${String(r[13]).padStart(3,'0')}<br>${badge}<label class="pick"><input type="checkbox" data-pick="${i}"${picked.has(i)?' checked':''}>選ぶ</label><button class="pbtn" data-act="present" data-i="${i}">提示</button></td>""")
rep("  }else if(act==='toggle'){", "  }else if(act==='present'){\n    startPresent(i);\n  }else if(act==='toggle'){")

# 絞り込み（並び順・科目・分野・難易度など）は、固定した帯の中の開閉パネルに移す
rep('    <input type="search" id="q" placeholder="キーワードで絞り込み" aria-label="キーワードで絞り込み">\n    <span class="count" id="count"></span>\n', '')
m = re.search(r'  <div class="controls">\n    <span class="ctl-label">並び順.*?\n(?=  <div class="tablebox" id="box">)', s, flags=re.S)
if not m: sys.exit('絞り込みの部分が見つかりません')
FILTERS = m.group(0)
s = s[:m.start()] + s[m.end():]
TOOLBAR = '''  <div class="tbar" id="tbar">
    <div class="tb-row">
      <button class="tb-btn tb-f" id="f-tg" aria-expanded="false" aria-controls="fpanel">絞り込み ▼</button>
      <span class="tb-sum" id="f-sum"></span>
      <input type="search" id="q" placeholder="キーワードで絞り込み" aria-label="キーワードで絞り込み">
      <span class="count" id="count"></span>
    </div>
    <div class="tb-row">
      <span class="tb-count" id="pk-count">選んだ問題：0題</span>
      <button class="tb-btn" id="pk-all">表示中の問題をすべて選ぶ</button>
      <button class="tb-btn" id="pk-clear">選択を解除</button>
      <span class="tb-sep"></span>
      <button class="tb-btn tb-main" id="pv-start">提示モード</button>
      <button class="tb-btn tb-main" id="ws-print">ワークシートを印刷</button>
      <label class="tb-opt"><input type="checkbox" id="ws-ch" checked>ワークシートに選択肢をのせる</label>
      <span class="tb-msg" id="tb-msg" role="status"></span>
    </div>
    <div class="fpanel" id="fpanel" hidden>
''' + FILTERS + '''    </div>
  </div>
'''
rep('  <div class="tablebox" id="box">', TOOLBAR + '  <div class="tablebox" id="box">')
rep("  count.textContent=n+'題'+(nc?`・コラム${nc}`:'');", "  count.textContent=n+'題'+(nc?`・コラム${nc}`:'');\n  if(typeof updSum==='function')updSum();")

OVERLAY = '''
<div id="pv" hidden role="dialog" aria-label="提示モード">
  <div class="pv-top"><span class="pv-no" id="pv-no"></span><span class="pv-th" id="pv-th"></span><span class="pv-el" id="pv-el"></span><span class="pv-pos" id="pv-pos"></span><button class="pv-x" id="pv-full">全画面</button><button class="pv-x" id="pv-close">閉じる（Esc）</button></div>
  <div class="pv-body" id="pv-body"></div>
  <div class="pv-nav">
    <button class="pv-b" id="pv-prev">◀ 前の問題</button>
    <button class="pv-b pv-s" id="pv-ch">選択肢を見る</button>
    <button class="pv-b pv-s" id="pv-ans">答えを見る</button>
    <button class="pv-b pv-s" id="pv-ex">解説を見る</button>
    <button class="pv-b" id="pv-next">次の問題 ▶</button>
  </div>
  <p class="pv-help">キー操作：スペース … 次の段階（選択肢 → 答え → 解説）　← → … 前・次の問題　Esc … 閉じる</p>
</div>
<div id="print" aria-hidden="true"></div>
'''
rep('\n<script>\n', OVERLAY + '\n<script>\n')

CSS = '''
/* ===== 教師用 ===== */
.lead a{color:var(--accent);font-weight:700}
.tbar{position:sticky;top:0;z-index:5;display:grid;gap:8px;padding:10px 12px;border:1px solid var(--accent);border-radius:10px;background:var(--accent-soft);box-shadow:0 2px 6px rgba(0,0,0,.06)}
.tb-row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.tb-f{font-weight:700;border-color:var(--accent);color:var(--accent)}
.tb-f[aria-expanded="true"]{background:var(--accent);color:var(--surface)}
.tb-sum{font-size:.85rem;color:var(--fg);font-weight:500}
.tbar input[type=search]{margin-left:auto}
.fpanel{display:grid;gap:10px;padding-top:10px;border-top:1px solid var(--accent);max-height:55vh;overflow:auto}
.fpanel[hidden]{display:none}
@media (max-width:760px){.tbar{position:static}.tbar input[type=search]{margin-left:0}}
.tb-count{font-weight:700;color:var(--accent);font-variant-numeric:tabular-nums;margin-right:4px}
.tb-btn{font:inherit;font-size:.9rem;border:1px solid var(--line);background:var(--surface);color:var(--fg);border-radius:8px;padding:5px 12px;cursor:pointer}
.tb-main{border-color:var(--accent);background:var(--accent);color:var(--surface);font-weight:700}
.tb-sep{flex:0 0 1px;height:24px;background:var(--line)}
.tb-opt{font-size:.85rem;display:inline-flex;gap:4px;align-items:center;cursor:pointer}
.tb-msg{font-size:.85rem;color:var(--answer);font-weight:700}
.pick{display:flex;gap:4px;align-items:center;margin-top:6px;font-size:.8rem;cursor:pointer;white-space:nowrap}
.pick input{width:16px;height:16px;accent-color:var(--accent)}
.pbtn{margin-top:4px;font:inherit;font-size:.78rem;font-weight:700;border:1px solid var(--accent);color:var(--accent);background:var(--surface);border-radius:6px;padding:1px 8px;cursor:pointer}
tr.card:has(.pick input:checked) td{background:var(--accent-soft)}
@media (max-width:760px){tr.card .no{flex-direction:row;flex-wrap:wrap;align-items:center;gap:6px}tr.card .pick,tr.card .pbtn{margin-top:0}}
/* 提示モード */
#pv{position:fixed;inset:0;z-index:50;background:var(--surface);color:var(--fg);display:grid;grid-template-rows:auto 1fr auto auto}
#pv[hidden]{display:none}
.pv-top{display:flex;flex-wrap:wrap;gap:6px 16px;align-items:baseline;padding:12px 24px;border-bottom:2px solid var(--accent);background:var(--accent-soft)}
.pv-no{font-family:var(--f-mono);color:var(--muted)}
.pv-th{font-family:var(--f-display);font-weight:800;font-size:clamp(20px,2.2vw,32px);color:var(--accent)}
.pv-el{color:var(--muted);font-size:.95rem}
.pv-pos{margin-left:auto;color:var(--muted);font-variant-numeric:tabular-nums}
.pv-x{font:inherit;border:1px solid var(--line);background:var(--surface);color:var(--fg);border-radius:8px;padding:4px 12px;cursor:pointer}
.pv-body{overflow:auto;padding:24px clamp(16px,4vw,64px);display:grid;gap:20px;align-content:start;font-size:clamp(19px,2vw,30px);line-height:1.7}
.pv-main{display:grid;gap:24px;align-items:start}
.pv-main.has-fig{grid-template-columns:minmax(0,1.15fr) minmax(0,1fr)}
@media (max-width:900px){.pv-main.has-fig{grid-template-columns:1fr}}
.pv-q{margin:0;white-space:pre-line}
.pv-body .fig{margin:0}
.pv-body .fig svg{max-width:100%;max-height:52vh;width:100%}
.pv-ch{margin:0;padding-left:2.4em;list-style:none;display:grid;gap:6px}
.pv-ch li{position:relative}.pv-ch li::before{content:attr(data-l);position:absolute;left:-1.6em;color:var(--accent);font-weight:800}
.pv-ans{border:2px solid var(--answer);border-radius:10px;padding:12px 18px;background:var(--answer-soft);color:var(--answer);font-weight:700}
.pv-ex{font-size:.72em;line-height:1.8;white-space:pre-line;border-left:4px solid var(--answer);padding-left:16px}
.pv-ex .fig{max-width:520px;margin-top:10px}
.pv-nav{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;padding:12px;border-top:1px solid var(--line)}
.pv-b{font:inherit;font-size:1.05rem;border:1.5px solid var(--line);background:var(--surface);color:var(--fg);border-radius:10px;padding:8px 18px;cursor:pointer}
.pv-s{border-color:var(--answer);color:var(--answer);font-weight:700}
.pv-s[aria-pressed="true"]{background:var(--answer-soft)}
.pv-b:disabled{opacity:.35;cursor:default}
.pv-help{margin:0;padding:0 12px 10px;text-align:center;color:var(--muted);font-size:.8rem}
/* ワークシート（印刷） */
#print{display:none}
@page{size:A4 landscape;margin:8mm}
@media print{
  html,body{background:#fff!important;margin:0!important;padding:0!important}
  .wrap,#pv{display:none!important}
  #print{display:block;--fg:#000;--muted:#444;--surface:#fff;--soft:#e6e6e6;--water:#d2e4f2;--accent:#1f6b5c;--line:#999;--carrot:#e8925a;color:#000;font-family:var(--f-body)}
  .sheet{height:190mm;display:grid;grid-template-columns:62fr 38fr;grid-template-rows:100%;overflow:hidden;break-after:page;page-break-after:always}
  .sheet:last-child{break-after:auto;page-break-after:auto}
  .ws-l{display:flex;flex-direction:column;gap:2.2mm;padding-right:5mm;font-size:10.5pt;line-height:1.6;min-height:0}
  .ws-h{display:flex;gap:3mm;align-items:baseline;border-bottom:1.2pt solid #000;padding-bottom:1mm}
  .ws-no{font-family:var(--f-mono);font-size:9pt}
  .ws-h b{font-size:13pt}
  .ws-el{margin-left:auto;font-size:8.5pt;color:#444}
  .ws-name{font-size:9.5pt;text-align:right}
  .ws-q{margin:0;white-space:pre-line}
  .ws-l .fig{margin:0;padding:1.5mm;border:0.6pt solid #999;align-self:center}
  .ws-l .fig svg{max-width:100%;max-height:58mm;width:auto;height:58mm}
  .ws-ch{margin:0;padding-left:7mm;list-style:none}
  .ws-ch li{position:relative}.ws-ch li::before{content:attr(data-l);position:absolute;left:-5mm;font-weight:700}
  .ws-lab{font-size:9pt;font-weight:700;margin-top:1mm}
  .ws-a1{height:14mm;border:0.8pt solid #000;border-radius:2mm}
  .ws-lines{flex:1 1 auto;min-height:22mm;border:0.8pt solid #000;border-radius:2mm}
  .ws-r{border-left:1pt dashed #000;padding-left:5mm;font-size:8.6pt;line-height:1.55;position:relative;overflow:hidden}
  .ws-cut{position:absolute;top:0;left:-3.2mm;font-size:9pt;background:#fff;line-height:1}
  .ws-r h4{margin:2mm 0 .5mm;font-size:8.6pt}
  .ws-r .ws-a{margin:0;font-weight:700}
  .ws-r p{margin:0;white-space:pre-line}
  .ws-r .fig{margin:2mm 0 0;padding:1mm;border:0.6pt solid #999}
  .ws-r .fig svg{max-width:100%;max-height:45mm;width:auto}
  .fig svg text.sm{fill:#444}
}
'''
rep('</style>', CSS + '</style>')

JS = r'''
/* ===== 教師用 ===== */
let vis=[];
const PK='cbp-teacher-picked';
const picked=new Set((()=>{try{return JSON.parse(localStorage.getItem(PK)||'[]')}catch(e){return []}})().filter(i=>D[i]&&D[i][5]!=='コラム'));
function savePicked(){try{localStorage.setItem(PK,JSON.stringify([...picked]))}catch(e){}}
const pkCount=document.getElementById('pk-count'),tbMsg=document.getElementById('tb-msg');
function updPk(){pkCount.textContent='選んだ問題：'+picked.size+'題';tbMsg.textContent=''}
function pickedInOrder(){return order().filter(i=>picked.has(i))}
tb.addEventListener('change',e=>{const c=e.target.closest('input[data-pick]');if(!c)return;const i=+c.dataset.pick;c.checked?picked.add(i):picked.delete(i);c.closest('tr').classList.toggle('picked',c.checked);savePicked();updPk()});
document.getElementById('pk-all').addEventListener('click',()=>{vis.forEach(i=>picked.add(i));savePicked();render();updPk()});
document.getElementById('pk-clear').addEventListener('click',()=>{picked.clear();savePicked();render();updPk()});
const DL='アイウエオ';
const chList=(ch,cls)=>`<ol class="${cls}">${ch.map((c,j)=>`<li data-l="${DL[j]}">${esc(c)}</li>`).join('')}</ol>`;
/* 提示モード */
const pv=document.getElementById('pv'),pvBody=document.getElementById('pv-body');
let pList=[],pPos=0,pStep=0,lastFocus=null;
function startPresent(i){
  const pk=pickedInOrder();
  let list=pk.length?pk:vis.slice();
  if(i!==undefined&&!list.includes(i))list=vis.slice();
  if(!list.length){tbMsg.textContent='映す問題がありません。条件を変えるか、問題を選んでください。';return}
  pList=list;pPos=i===undefined?0:Math.max(0,list.indexOf(i));pStep=0;lastFocus=document.activeElement;
  pv.hidden=false;document.body.style.overflow='hidden';drawPv();document.getElementById('pv-next').focus();
}
function closePv(){pv.hidden=true;document.body.style.overflow='';if(document.fullscreenElement)document.exitFullscreen().catch(()=>{});if(lastFocus)lastFocus.focus()}
function drawPv(){
  const r=D[pList[pPos]],ch=r[8],hasCh=ch.length>0,fig=FIG[r[6]],afig=FIG[r[6]+'#解答'];
  document.getElementById('pv-no').textContent='No.'+String(r[13]).padStart(3,'0')+'（'+r[0]+'）';
  document.getElementById('pv-th').textContent=r[6];
  document.getElementById('pv-el').textContent=r[4]+'／'+FL[r[5]];
  document.getElementById('pv-pos').textContent=(pPos+1)+' / '+pList.length;
  let h=`<div class="pv-main${fig?' has-fig':''}"><div style="display:grid;gap:18px;align-content:start"><p class="pv-q">${esc(r[7])}</p>${hasCh&&pStep>=1?chList(ch,'pv-ch'):''}</div>${fig?`<figure class="fig">${fig}</figure>`:''}</div>`;
  if(pStep>=2)h+=`<div class="pv-ans">答え：${esc(r[9])}</div>`;
  if(pStep>=3)h+=`<div class="pv-ex">${esc(r[10])}${afig?`<figure class="fig">${afig}</figure>`:''}</div>`;
  pvBody.innerHTML=h;
  const bc=document.getElementById('pv-ch'),ba=document.getElementById('pv-ans'),be=document.getElementById('pv-ex');
  bc.disabled=!hasCh;bc.textContent=hasCh?'選択肢を見る':'選択肢なし';bc.setAttribute('aria-pressed',hasCh&&pStep>=1);
  ba.setAttribute('aria-pressed',pStep>=2);be.setAttribute('aria-pressed',pStep>=3);
  document.getElementById('pv-prev').disabled=pPos===0;document.getElementById('pv-next').disabled=pPos===pList.length-1;
  if(pStep>=2){const t=pvBody.querySelector(pStep>=3?'.pv-ex':'.pv-ans');if(t)t.scrollIntoView({block:'nearest'})}else pvBody.scrollTop=0;
}
function pvGo(d){const n=pPos+d;if(n<0||n>=pList.length)return;pPos=n;pStep=0;drawPv()}
function pvStep(s){pStep=(pStep>=s?s-1:s);if(pStep===1&&!D[pList[pPos]][8].length)pStep=0;drawPv()}
document.getElementById('pv-start').addEventListener('click',()=>startPresent());
document.getElementById('pv-close').addEventListener('click',closePv);
document.getElementById('pv-prev').addEventListener('click',()=>pvGo(-1));
document.getElementById('pv-next').addEventListener('click',()=>pvGo(1));
document.getElementById('pv-ch').addEventListener('click',()=>pvStep(1));
document.getElementById('pv-ans').addEventListener('click',()=>pvStep(2));
document.getElementById('pv-ex').addEventListener('click',()=>pvStep(3));
document.getElementById('pv-full').addEventListener('click',()=>{if(document.fullscreenElement)document.exitFullscreen().catch(()=>{});else if(pv.requestFullscreen)pv.requestFullscreen().catch(()=>{})});
document.addEventListener('keydown',e=>{
  if(pv.hidden)return;
  if(e.key==='Escape'){if(!document.fullscreenElement)closePv();return}
  if(e.key==='ArrowRight'){e.preventDefault();pvGo(1)}
  else if(e.key==='ArrowLeft'){e.preventDefault();pvGo(-1)}
  else if(e.key===' '||e.key==='Enter'){if(e.target.closest&&e.target.closest('.pv-nav,.pv-top'))return;e.preventDefault();if(pStep<3){pStep++;if(pStep===1&&!D[pList[pPos]][8].length)pStep=2;drawPv()}}
});
/* ワークシート */
const prt=document.getElementById('print');
document.getElementById('ws-print').addEventListener('click',()=>{
  const list=pickedInOrder();
  if(!list.length){tbMsg.textContent='先に、印刷する問題の「選ぶ」にチェックを入れてください。';return}
  const withCh=document.getElementById('ws-ch').checked;
  prt.innerHTML=list.map(i=>{const r=D[i],fig=FIG[r[6]],afig=FIG[r[6]+'#解答'];
    return `<section class="sheet"><div class="ws-l"><div class="ws-h"><span class="ws-no">No.${String(r[13]).padStart(3,'0')}</span><b>${esc(r[6])}</b><span class="ws-el">${esc(r[0])}　${esc(r[4])}</span></div>`+
    `<div class="ws-name">　　年　　組　　番　氏名＿＿＿＿＿＿＿＿＿＿＿＿</div><p class="ws-q">${esc(r[7])}</p>${fig?`<figure class="fig">${fig}</figure>`:''}${withCh&&r[8].length?chList(r[8],'ws-ch'):''}`+
    `<div class="ws-lab">自分の答え（予想）</div><div class="ws-a1"></div><div class="ws-lab">そう考えた理由</div><div class="ws-lines"></div></div>`+
    `<div class="ws-r"><span class="ws-cut">✂</span><h4>模範解答</h4><p class="ws-a">${esc(r[9])}</p><h4>解説</h4><p>${esc(r[10])}</p>${afig?`<figure class="fig">${afig}</figure>`:''}</div></section>`}).join('');
  tbMsg.textContent='';
  setTimeout(()=>window.print(),50);
});
updPk();
const fTg=document.getElementById('f-tg'),fPanel=document.getElementById('fpanel'),fSum=document.getElementById('f-sum');
fTg.addEventListener('click',()=>{const o=fPanel.hidden;fPanel.hidden=!o;fTg.setAttribute('aria-expanded',o);fTg.textContent=o?'絞り込み ▲':'絞り込み ▼'});
function updSum(){
  const p=[];
  p.push(subj==='all'?'すべての科目':subj);
  p.push(dom==='all'?'すべての分野':dom);
  if(lv!=='0')p.push('★'.repeat(+lv));
  if(ord==='field')p.push('分野ごとの順');
  if(!showCol)p.push('コラムなし');
  fSum.textContent='条件：'+p.join('・');
}
'''
rep('\nrender();\n</script>', '\n' + JS + '\nrender();\n</script>')
out = root / 'teacher' / 'index.html'
out.write_text(s, encoding='utf-8')
print('wrote', out, len(s))
