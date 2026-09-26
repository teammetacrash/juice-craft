import React from 'react';
import {createRoot} from 'react-dom/client';
import Shop from './shop';
import './primitives.css';
import './design.css';
async function start(){
 if(import.meta.env.DEV && location.pathname==='/__responsive'){createRoot(document.getElementById('root')!).render(<div style={{padding:24,background:'#e8eaf0',minHeight:'100vh'}}><p style={{marginBottom:12}}>Mobile layout check · synthetic sample data · 390 × 844</p><iframe title="Mobile preview" src="/__design" style={{width:390,height:844,border:'1px solid #ccc',background:'white'}}/></div>);return;}
 if(import.meta.env.DEV && location.pathname==='/__design'){const {installFixtures}=await import('./dev-fixtures');installFixtures();}
 createRoot(document.getElementById('root')!).render(<Shop/>);
}
start();
