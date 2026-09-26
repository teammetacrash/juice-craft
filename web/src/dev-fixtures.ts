// Isolated synthetic UI fixtures. Imported only by Vite's development build.
export function installFixtures(){
 const date=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Kolkata',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
 const masters=[{id:'b1',kind:'brand',name:'Arun',active:1},{id:'b2',kind:'brand',name:'Dairy Day',active:1},{id:'c1',kind:'category',name:'Popsicles',active:1},{id:'c2',kind:'category',name:'Family packs',active:1},{id:'m1',kind:'prepared',name:'Mojito',active:1},{id:'m2',kind:'prepared',name:'Milkshake',active:1}];
 const products:any[]=[{id:'p1',name:'Chocolate Cone',brand:'b1',brand_name:'Arun',category:'c1',category_name:'Popsicles',price:4500,cost:3000,qty:24,low:5,variant:'100 ml',active:1,kind:'packaged'},{id:'p2',name:'Mango Popsicle',brand:'b2',brand_name:'Dairy Day',category:'c1',category_name:'Popsicles',price:2500,cost:1700,qty:4,low:5,variant:'60 ml',active:1,kind:'packaged'},{id:'p3',name:'Vanilla Family Pack',brand:'b1',brand_name:'Arun',category:'c2',category_name:'Family packs',price:16000,cost:11000,qty:12,low:3,variant:'500 ml',active:1,kind:'packaged'},{id:'p4',name:'Classic Mojito',category:'m1',category_name:'Mojito',price:8000,cost:0,qty:0,low:0,active:1,kind:'prepared',brand_name:''},{id:'p5',name:'Oreo Milkshake',category:'m2',category_name:'Milkshake',price:12000,cost:0,qty:0,low:0,active:1,kind:'prepared',brand_name:''}];
 const totals={revenue:184500,net:46200,margin:55200,bills:28,units:53,waste:2000,expenses:7000,prepared:48000};
 const sales=[{id:'s1',number:1042,date,time:'15:30',payment:'UPI',status:'completed',total:21000,units:3},{id:'s2',number:1041,date,time:'15:12',payment:'Cash',status:'completed',total:8000,units:1},{id:'s3',number:1040,date,time:'14:50',payment:'UPI',status:'completed',total:16000,units:2}];
 const shop={name:'JUICE CRAFT',address:'',phone:'',footer:'Thank you! Come back for something refreshing.'};
 const native=window.fetch.bind(window);
 window.fetch=async(input,init)=>{if(!String(input).includes('/juicecraft-shop'))return native(input,init);const body=init?.body?JSON.parse(String(init.body)):{};const action=body.action||new URL(String(input),location.origin).searchParams.get('action');let result:any={ok:true};
 if(action==='bootstrap')result={products,masters,settings:shop,mustChange:false};
 else if(action==='dashboard')result={todayReport:totals,totals:{...totals,revenue:1234500,net:362100,bills:182},days:Array.from({length:7},(_,i)=>{const d=new Date(date+'T12:00:00Z');d.setUTCDate(d.getUTCDate()-6+i);return{date:d.toISOString().slice(0,10),revenue:[110000,175000,150000,220000,187000,208000,184500][i],margin:46000,bills:28}}),dailyLoss:[],dailyExpense:[],from:date,to:date,bucket:'day',series:Array.from({length:new URL(String(input),location.origin).searchParams.get('range')==='30'?30:7},(_,i)=>({name:String(i+1),revenue:1200+i*80,profit:300+i*12,bills:18+i})),stock:{value:210800},sales,items:products.slice(0,4).map((p,i)=>({...p,brand:p.brand_name,qty:32-i*5}))};
 else if(action==='product'){const i=products.findIndex(p=>p.id===body.id);const p={...body,price:Math.round(Number(body.price)*100),cost:Math.round(Number(body.cost)*100),brand_name:masters.find(m=>m.id===body.brand)?.name,category_name:masters.find(m=>m.id===body.category)?.name};if(i>=0)products[i]={...products[i],...p};else products.push({...p,id:'new'+products.length});}
 else if(action==='report')result={totals,count:sales.length,sales,payments:[{payment:'UPI',total:37000},{payment:'Cash',total:8000}],items:[]};
 else if(action==='bill')result={...sales[0],shop,lines:[{id:'l1',name:'Chocolate Cone',brand:'Arun',price:4500,qty:2},{id:'l2',name:'Oreo Milkshake',brand:'Prepared',price:12000,qty:1}]};
 else if(action==='movements'||action==='expenses'||action==='history')result=[];
 else if(action==='storage')result={sales:182,lines:342,movements:28};
 else if(action==='sale')result={id:'s1'};
 return new Response(JSON.stringify(result),{headers:{'Content-Type':'application/json'}});
 };
}
