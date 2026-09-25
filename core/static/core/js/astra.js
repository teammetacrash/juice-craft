document.write('<script src="/static/core/js/app.js"><\/script>');

function astraInitNav(){
  document.addEventListener("DOMContentLoaded",()=>{
    const side=document.querySelector("#sidebar");
    const overlay=document.querySelector("#overlay");
    const menu=document.querySelector("#menuBtn");
    const close=()=>{side?.classList.remove("open");overlay?.classList.remove("show")};
    menu?.addEventListener("click",()=>overlay?.classList.toggle("show"));
    overlay?.addEventListener("click",close);
    document.querySelectorAll(".sidebar-nav a").forEach(a=>a.addEventListener("click",close));
  });
}
astraInitNav();

dashboard=async function(){
  let d=await api("dashboard"),m=d.metrics||{},s=m.summary||{},st=m.stock||{},daily=m.daily||[];
  let max=Math.max(1,...daily.map(x=>Number(x.revenue||0)));
  root.innerHTML=
  '<div class="dashboard-welcome"><div><h2>Good Morning, Admin! 👋</h2><p>Here’s how JUICE CRAFT is performing today.</p></div><select class="period-pill"><option>Today</option></select></div>'+
  '<div class="metric-grid">'+
    metric("Today’s Revenue",money(s.revenue),Number(s.revenue||0)>0?"↗ Sales recorded":"Ready for sales")+
    metric("Estimated Profit",money(s.profit),Number(s.profit||0)>0?"↗ Gross profit":"Updates automatically")+
    metric("Bills",s.bills||0,Number(s.bills||0)>0?"↗ Completed":"No bills yet")+
    metric("Items Sold",s.items||0,Number(s.items||0)>0?"↗ Units sold":"No items yet")+
  '</div>'+
  '<div class="dashboard-grid">'+
    '<div class="panel"><div class="panel-title"><div><h3>Sales Performance</h3><p>Revenue over the last 7 days</p></div><span class="badge-soft">Last 7 Days</span></div>'+
      '<div class="chart-bars">'+daily.map(x=>'<div class="chart-col"><div class="chart-bar" title="'+money(x.revenue)+'" style="height:'+Math.max(4,Math.round(Number(x.revenue||0)/max*165))+'px"></div><small>'+esc(x.label)+'</small></div>').join("")+'</div>'+
    '</div>'+
    '<div class="panel"><div class="panel-title"><div><h3>Stock Overview</h3><p>Current packaged inventory</p></div></div>'+
      '<div class="summary-strip">'+
        '<div class="summary-box"><span>Total Units</span><strong>'+Number(st.units||0)+'</strong></div>'+
        '<div class="summary-box"><span>Low Stock</span><strong>'+Number(st.low||0)+'</strong></div>'+
        '<div class="summary-box"><span>Out of Stock</span><strong>'+Number(st.out||0)+'</strong></div>'+
        '<div class="summary-box"><span>Stock Value</span><strong>'+money(st.value)+'</strong></div>'+
      '</div>'+
      '<div class="panel-title"><h3>Needs Attention</h3><a href="/inventory/">View All</a></div>'+
      '<ul class="list-clean">'+((m.needs_attention||[]).length?(m.needs_attention||[]).slice(0,4).map(x=>'<li class="list-row"><span><strong>'+esc(x.name)+'</strong><br>'+esc(x.brand||"")+'</span><span class="badge-soft">'+Number(x.stock||0)+' left</span></li>').join(""):'<li class="empty-state">Stock is looking healthy.</li>')+'</ul>'+
    '</div>'+
  '</div>'+
  '<div class="three-panel-grid">'+
    '<div class="panel"><div class="panel-title"><div><h3>Best Selling Items</h3><p>Top performers</p></div></div><ul class="list-clean">'+((m.top_items||[]).slice(0,5).map((x,i)=>'<li class="list-row"><span><strong>'+(i+1)+'. '+esc(x.name)+'</strong></span><span>'+Number(x.quantity||x.qty||0)+' sold</span></li>').join("")||'<li class="empty-state">Sales will appear here.</li>')+'</ul></div>'+
    '<div class="panel stat-focus"><span class="stat-icon">♻</span><div><span>Wastage Today</span><strong>'+money(s.wastage)+'</strong><small>Recorded stock loss</small></div></div>'+
    '<div class="panel stat-focus"><span class="stat-icon">₹</span><div><span>Expenses Today</span><strong>'+money(s.expenses)+'</strong><small>Business expenses</small></div></div>'+
  '</div>'+
  '<div class="panel recent-panel"><div class="panel-title"><div><h3>Recent Sales</h3><p>Latest completed bills</p></div><a href="/reports/">View reports</a></div>'+
    '<div class="data-table-wrap"><table><thead><tr><th>Bill</th><th>Time</th><th>Payment</th><th>Amount</th></tr></thead><tbody>'+
    (d.recent.length?d.recent.map(x=>'<tr><td><strong>'+esc(x.bill_number)+'</strong></td><td>'+new Date(x.created_at).toLocaleTimeString("en-IN",{hour:"2-digit",minute:"2-digit"})+'</td><td><span class="badge-soft">'+esc(x.payment_method||"")+'</span></td><td><strong>'+money(x.total)+'</strong></td></tr>').join(""):'<tr><td colspan="4"><div class="empty-state">No sales yet. Create your first bill.</div></td></tr>')+
    '</tbody></table></div></div>';
};
