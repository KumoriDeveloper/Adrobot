import { useState } from 'react'; import { api } from './api';

export default function App() {
  const [tab, setTab] = useState<'create'|'edit'>('create');
  const [name, setName] = useState(''); const [geo, setGeo] = useState(''); const [offer, setOffer] = useState('');
  const [campaignId, setCampaignId] = useState(''); const [offerToChange, setOfferToChange] = useState('');
  const [message, setMessage] = useState(''); const [busy, setBusy] = useState(false);
  async function create(e: React.FormEvent) { e.preventDefault(); setBusy(true); setMessage('');
    try { const r = await api.post('/campaigns/create', {name, geo, offer_id: Number(offer)}); setMessage(`Задача ${r.data.id}: ${r.data.status}`); }
    catch (e: any) { setMessage(e.response?.data?.detail || e.message); } finally { setBusy(false); }
  }
  async function mutate(action: 'add'|'remove') { setBusy(true); setMessage('');
    try { const url = `/campaigns/${Number(campaignId)}/offers/${Number(offerToChange)}`;
      const r = action === 'add' ? await api.post(url) : await api.delete(url);
      setMessage(JSON.stringify(r.data));
    } catch (e: any) { setMessage(e.response?.data?.detail || e.message); } finally { setBusy(false); }
  }
  return <main className="shell"><header><div className="brand"><span className="logo">A</span><div><b>ADROBOT</b><small>Keitaro campaign workspace</small></div></div><span className="status">CONTROL PANEL</span></header>
    <section className="intro"><p className="eyebrow">ADVERTISING OPERATIONS</p><h1>Campaign<br/><em>management.</em></h1><p className="sub">Создание и редактирование кампаний Keitaro в одном рабочем пространстве.</p></section>
    <nav><button className={tab==='create'?'active':''} onClick={()=>setTab('create')}>01 / Создать кампанию</button><button className={tab==='edit'?'active':''} onClick={()=>setTab('edit')}>02 / Редактор кампании</button></nav>
    <section className="panel">{tab==='create' ? <><div className="panelhead"><div><p className="eyebrow">NEW WORKFLOW</p><h2>Новая кампания</h2></div><span className="number">01</span></div><form onSubmit={create}>
      <label>Название кампании<input required value={name} onChange={e=>setName(e.target.value)} placeholder="Например, MX — Summer offer"/></label>
      <div className="two"><label>GEO-код страны<input required minLength={2} maxLength={2} value={geo} onChange={e=>setGeo(e.target.value.toUpperCase())} placeholder="MX"/></label><label>ID оффера Keitaro<input required type="number" min="1" value={offer} onChange={e=>setOffer(e.target.value)} placeholder="123"/></label></div>
      <button className="primary" disabled={busy}>{busy?'Создание…':'Создать кампанию ↗'}</button></form></> : <><div className="panelhead"><div><p className="eyebrow">EXISTING WORKFLOW</p><h2>Редактор офферов</h2></div><span className="number">02</span></div><label>ID кампании<input type="number" value={campaignId} onChange={e=>setCampaignId(e.target.value)} placeholder="ID кампании Keitaro"/></label><label>ID оффера<input type="number" value={offerToChange} onChange={e=>setOfferToChange(e.target.value)} placeholder="ID оффера"/></label><div className="actions"><button className="primary" disabled={busy||!campaignId||!offerToChange} onClick={()=>mutate('add')}>Добавить оффер +</button><button className="danger" disabled={busy||!campaignId||!offerToChange} onClick={()=>mutate('remove')}>Удалить оффер −</button></div></>}
      {message && <pre className="message">{message}</pre>}</section><footer><span>ADROBOT / TEST ASSIGNMENT</span><span>FASTAPI · REACT · KEITARO API</span></footer></main>
}
