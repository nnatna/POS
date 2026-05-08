const COLORS = ['#ffc107','#000000','#16a34a','#7c3aed','#ec4899','#eab308','#06b6d4','#ef4444'];

const lineCanvas = document.getElementById('lineChart');
const donutCanvas = document.getElementById('donutChart');
let lineChart = null;
let donutChart = null;

// ── Init Charts ───────────────────────────────────────────────────────────────
if (lineCanvas && donutCanvas && typeof Chart !== 'undefined') {
  const lineCtx  = lineCanvas.getContext('2d');
  const grad = lineCtx.createLinearGradient(0,0,0,230);
  grad.addColorStop(0,'rgba(249,115,22,.18)');
  grad.addColorStop(1,'rgba(249,115,22,0)');

  lineChart = new Chart(lineCtx, {
    type: 'line',
    data: { labels:[], datasets:[{
      data:[], borderColor:'#ffc107', backgroundColor:grad,
      borderWidth:2.5, pointRadius:3, pointHoverRadius:6,
      pointBackgroundColor:'#ffc107', fill:true, tension:.42
    }]},
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ display:false } },
      scales:{
        x:{ grid:{ display:false }, ticks:{ font:{ size:10 }, color:'#9ca3af', maxTicksLimit:12 } },
        y:{ grid:{ color:'#f3f4f6' }, ticks:{
          font:{ size:10 }, color:'#9ca3af',
          callback: v => v>=1000 ? '$'+(v/1000).toFixed(1)+'k' : '$'+v
        }}
      },
      animation:{ duration:600 }
    }
  });

  donutChart = new Chart(donutCanvas.getContext('2d'), {
    type:'doughnut',
    data:{ labels:[], datasets:[{ data:[], backgroundColor:COLORS, borderWidth:0, hoverOffset:6 }] },
    options:{
      cutout:'68%',
      plugins:{
        legend:{ display:false },
        tooltip:{ callbacks:{ label: c=>' $'+Number(c.parsed).toLocaleString('en',{minimumFractionDigits:2}) } }
      },
      animation:{ duration:700 }
    }
  });
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const fmt  = n => '$'+Number(n).toLocaleString('en',{minimumFractionDigits:2,maximumFractionDigits:2});
const fmtK = n => n>=1000 ? '$'+(n/1000).toFixed(1)+'k' : fmt(n);
const setText = (id, value) => {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
};

function badge(state){
  const b = document.getElementById('dbBadge');
  if (!b) return;
  const map = { ok:'Django + SQLite', err:'API Error', loading:'Loading...' };
  b.textContent = map[state];
  b.className = 'badge db-badge' + (state==='ok' ? '' : state==='err' ? ' err' : ' loading');
}

function setActivePeriod(period, btn) {
  document.querySelectorAll('[data-dashboard-period]').forEach(b => {
    b.classList.remove('btn-warning', 'text-dark');
    b.classList.add('btn-outline-warning');
  });

  btn = btn || document.querySelector(`[data-dashboard-period="${period}"]`);
  if (btn) {
    btn.classList.remove('btn-outline-warning');
    btn.classList.add('btn-warning', 'text-dark');
  }
}

const TREND_LBL = { today:'Today by hour', week:'This week', month:'This month', year:'This year', all:'All time' };

// ── Load Dashboard ────────────────────────────────────────────────────────────
async function loadDash(period, btn){
  setActivePeriod(period, btn);
  badge('loading');

  try {
   const res = await fetch(`/dashboard/api/dashboard/?period=${period}`);
    if(!res.ok) throw new Error('HTTP '+res.status);
    const d = await res.json();

    // KPI
    setText('kpiRev', fmtK(d.kpi.total_revenue));
    setText('kpiSales', d.kpi.total_sales.toLocaleString());
    setText('kpiExp', fmtK(d.kpi.total_expense));
    setText('kpiProfit', fmtK(d.kpi.net_profit));

    const avg = d.kpi.total_sales > 0 ? fmt(d.kpi.total_revenue / d.kpi.total_sales) : '$0.00';
    setText('kpiRevSub', `avg ${avg} / sale`);
    setText('kpiSalesSub', `${d.kpi.order_count} orders`);
    setText('trendLbl', TREND_LBL[period] || '');
    setText('dashSub', `Showing data for: ${TREND_LBL[period]}`);

    // Line
    if (lineChart) {
      lineChart.data.labels           = d.trend.map(t=>t.label);
      lineChart.data.datasets[0].data = d.trend.map(t=>t.amount);
      lineChart.update();
    }

    // Donut
    const total = d.donut.reduce((s,c)=>s+c.value, 0);
    setText('donutTotal', fmtK(total));
    if (donutChart) {
      donutChart.data.labels                      = d.donut.map(c=>c.name);
      donutChart.data.datasets[0].data            = d.donut.map(c=>c.value);
      donutChart.data.datasets[0].backgroundColor = COLORS.slice(0, d.donut.length);
      donutChart.update();
    }

    const donutLegend = document.getElementById('donutLegend');
    if (donutLegend) {
      donutLegend.innerHTML = d.donut.map((c,i)=>{
      const pct = total > 0 ? ((c.value/total)*100).toFixed(1) : 0;
      return `<div class="legend-row-item">
        <span class="lname"><span class="ldot" style="background:${COLORS[i]}"></span>${c.name}</span>
        <span style="display:flex;align-items:center;">
          <span class="lval">${fmtK(c.value)}</span>
          <span class="lpct">${pct}%</span>
        </span>
      </div>`;
      }).join('');
    }

    // Top Products
    const topProducts = document.getElementById('topProducts');
    if (topProducts) {
      topProducts.innerHTML = d.top_products.length
        ? d.top_products.map((p,i)=>{
          const rankClass = i === 0 ? 'text-bg-warning' : i === 1 ? 'text-bg-secondary' : i === 2 ? 'text-bg-info' : 'text-bg-light';
          return `<tr>
            <td class="ps-3"><span class="badge rounded-pill ${rankClass}">${i+1}</span></td>
            <td class="fw-semibold">${p.name}</td>
            <td class="text-muted">${p.brand || '-'}</td>
            <td class="text-muted">${p.category}</td>
            <td class="text-end">${p.qty}</td>
            <td class="text-end pe-3 text-danger fw-semibold">${fmt(p.revenue)}</td>
          </tr>`;
          }).join('')
        : `<tr><td colspan="6" class="text-center text-muted py-4">No sales in this period.</td></tr>`;
    }

    // Low Stock
    const lowStock = document.getElementById('lowStock');
    if (lowStock) {
      lowStock.innerHTML = d.low_stock.length
        ? d.low_stock.map(p=>{
          const pct = Math.min(100, (p.stock_quantity / 50) * 100);
          const progressClass = p.stock_quantity <= 10 ? 'bg-danger' : p.stock_quantity <= 25 ? 'bg-warning' : 'bg-success';
          return `<div class="pb-3 mb-3 border-bottom">
            <div class="d-flex align-items-start justify-content-between gap-3">
              <div class="flex-grow-1 overflow-hidden">
                <div class="fw-semibold text-truncate">${p.name}</div>
                <div class="small text-muted">${p.cat_name || '-'}</div>
              </div>
              <span class="badge text-bg-light border">${p.stock_quantity}</span>
            </div>
            <div class="progress mt-2" role="progressbar" aria-label="${p.name} stock" aria-valuenow="${p.stock_quantity}" aria-valuemin="0" aria-valuemax="50" style="height: 5px;">
              <div class="progress-bar ${progressClass}" style="width:${pct}%;"></div>
            </div>
          </div>`;
          }).join('')
        : '<div class="text-success small py-2">All products well stocked</div>';
    }

    badge('ok');

  } catch(e) {
    badge('err');
    console.error('Dashboard error:', e);
  }
}

// ── Auto load ─────────────────────────────────────────────────────────────────
window.loadDash = loadDash;
loadDash('month', null);
