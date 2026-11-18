import json

data = json.load(open("dashboard/data.json"))

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>SaaS Revenue Intelligence (SYNTHETIC DATA)</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
body{font-family:Segoe UI,Arial,sans-serif;margin:0;background:#f4f6f8;color:#1f2933}
header{background:#14213d;color:#fff;padding:14px 24px}
header small{display:block;color:#fca311;margin-top:4px}
nav{background:#fff;border-bottom:1px solid #d9dee3;padding:0 24px}
nav button{border:0;background:none;padding:14px 18px;font-size:15px;cursor:pointer;border-bottom:3px solid transparent}
nav button.on{border-bottom-color:#fca311;font-weight:600}
main{padding:20px 24px;max-width:1100px;margin:auto}
.page{display:none}.page.on{display:block}
.cards{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:16px}
.card{background:#fff;border-radius:8px;padding:14px 18px;flex:1;min-width:170px;box-shadow:0 1px 3px #0001}
.card b{display:block;font-size:24px;margin-top:4px}
.box{background:#fff;border-radius:8px;padding:16px;margin-bottom:16px;box-shadow:0 1px 3px #0001}
table{border-collapse:collapse;width:100%}td,th{padding:6px 10px;border-bottom:1px solid #e5e9ed;text-align:right}
td:first-child,th:first-child{text-align:left}
.note{font-size:13px;color:#52606d;margin-top:8px}
</style></head><body>
<header><b>SaaS Revenue Intelligence</b>
<small>ALL DATA IS SYNTHETIC. Randomly generated, not a real company.</small></header>
<nav><button class="on" onclick="show(0,this)">1. Executive revenue</button>
<button onclick="show(1,this)">2. Retention</button>
<button onclick="show(2,this)">3. Customer health</button></nav>
<main>
<section class="page on">
<div class="cards" id="kpi1"></div>
<div class="box"><h3>Monthly recurring revenue (MRR)</h3><canvas id="c1"></canvas></div>
<div class="box"><h3>MRR bridge, last 12 months</h3><canvas id="c2"></canvas>
<div class="note">Closing MRR = Opening + New + Expansion + Reactivation - Contraction - Churn. The bridge reconciles in every month (dbt test).</div></div>
<div class="box"><h3>Latest month bridge</h3><table id="t1"></table></div>
</section>
<section class="page">
<div class="cards" id="kpi2"></div>
<div class="box"><h3>Trailing 12-month NRR and GRR</h3><canvas id="c3"></canvas>
<div class="note">NRR counts only accounts paying 12 months earlier. New customers and reactivations are excluded (metric contract).</div></div>
<div class="box"><h3>Trailing 12-month customer churn</h3><canvas id="c4"></canvas></div>
</section>
<section class="page">
<div class="cards" id="kpi3"></div>
<div class="box"><h3>Paying accounts by risk flag</h3><canvas id="c5"></canvas></div>
<div class="box"><h3>Revenue by segment</h3><table id="t2"></table>
<div class="note">Largest single account is under 1% of MRR, so risk is spread broadly, not concentrated.</div></div>
<div class="box"><h3>What the simulation shows (from the SQL investigation)</h3>
<ul>
<li>Usage falls step by step before churn: about 59% of plan norm one month before cancelling, versus about 102% otherwise.</li>
<li>About half of accounts with an escalated ticket cancelled the next month (51.7%) versus 3.0% baseline, but 60% of churners had no escalation.</li>
<li>Enterprise accounts for the largest share of contraction MRR.</li>
</ul>
<div class="note">These patterns were planted in the generator. They show the pipeline detects them. They are correlations, not proof that raising usage or fixing tickets prevents churn. The risk flag is a proposed rule, not a validated prediction.</div></div>
</section>
</main>
<script>
const D = __DATA__;
const $ = id => document.getElementById(id);
const money = v => "$" + Math.round(v).toLocaleString();
const pct = v => (v*100).toFixed(1) + "%";
function show(i,b){document.querySelectorAll(".page").forEach((p,j)=>p.classList.toggle("on",i===j));
document.querySelectorAll("nav button").forEach(x=>x.classList.remove("on"));b.classList.add("on");}
function card(id,items){$(id).innerHTML=items.map(x=>`<div class="card">${x[0]}<b>${x[1]}</b></div>`).join("");}
const B=D.bridge, L=B[B.length-1], P=B[B.length-2];
const lab=B.map(r=>r.m.slice(0,7));
card("kpi1",[["Latest MRR",money(L.closing_mrr)],["ARR",money(L.arr)],
["MoM growth",pct(L.closing_mrr/P.closing_mrr-1)],["Net new MRR (latest month)",money(L.closing_mrr-L.opening_mrr)]]);
new Chart($("c1"),{type:"line",data:{labels:lab,datasets:[{label:"MRR",data:B.map(r=>r.closing_mrr),borderColor:"#14213d",tension:.2}]}});
const last=B.slice(-12), ll=last.map(r=>r.m.slice(0,7));
const ds=(n,k,c)=>({label:n,data:last.map(r=>r[k]),backgroundColor:c});
new Chart($("c2"),{type:"bar",data:{labels:ll,datasets:[ds("New","new_mrr","#2a9d8f"),ds("Expansion","expansion_mrr","#8ab17d"),
ds("Reactivation","reactivation_mrr","#e9c46a"),ds("Contraction","contraction_mrr","#f4a261"),ds("Churn","churn_mrr","#e76f51")]},
options:{scales:{x:{stacked:true},y:{stacked:true}}}});
$("t1").innerHTML="<tr><th>Component</th><th>MRR</th></tr>"+[["Opening",L.opening_mrr],["+ New",L.new_mrr],["+ Expansion",L.expansion_mrr],
["+ Reactivation",L.reactivation_mrr],["- Contraction",L.contraction_mrr],["- Churn",L.churn_mrr],["= Closing",L.closing_mrr]]
.map(r=>`<tr><td>${r[0]}</td><td>${money(r[1])}</td></tr>`).join("");
const R=D.retention, RL=R[R.length-1], rl=R.map(r=>r.m.slice(0,7));
card("kpi2",[["NRR (TTM)",pct(RL.nrr_ttm)],["GRR (TTM)",pct(RL.grr_ttm)],["Customer churn (TTM)",pct(RL.customer_churn_ttm)]]);
new Chart($("c3"),{type:"line",data:{labels:rl,datasets:[{label:"NRR",data:R.map(r=>r.nrr_ttm),borderColor:"#2a9d8f"},
{label:"GRR",data:R.map(r=>r.grr_ttm),borderColor:"#e76f51"}]}});
new Chart($("c4"),{type:"line",data:{labels:rl,datasets:[{label:"Customer churn",data:R.map(r=>r.customer_churn_ttm),borderColor:"#14213d"}]}});
const H=D.health_flags, tot=H.reduce((a,r)=>a+r.accounts,0), hi=H.find(r=>r.risk_flag==="high")||{accounts:0,mrr:0};
card("kpi3",[["Paying accounts",tot],["High risk accounts",hi.accounts],["MRR in high risk",money(hi.mrr)]]);
new Chart($("c5"),{type:"bar",data:{labels:H.map(r=>r.risk_flag),datasets:[{label:"Accounts",data:H.map(r=>r.accounts),backgroundColor:["#e76f51","#2a9d8f","#e9c46a"]}]}});
$("t2").innerHTML="<tr><th>Segment</th><th>Accounts</th><th>MRR</th></tr>"+D.segments.map(r=>`<tr><td>${r.segment}</td><td>${r.accounts}</td><td>${money(r.mrr)}</td></tr>`).join("");
</script></body></html>"""

html = TEMPLATE.replace("__DATA__", json.dumps(data))
open("dashboard/index.html", "w", encoding="utf-8").write(html)
print("Saved dashboard/index.html")