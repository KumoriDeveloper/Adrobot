import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import { api } from './api';

type CatalogItem = {
  id: number;
  name: string;
  state?: string;
  country?: string[];
};

type Catalogs = {
  offers: CatalogItem[];
  domains: CatalogItem[];
  groups: CatalogItem[];
  traffic_sources: CatalogItem[];
};

type CampaignListItem = {
  id: number;
  name: string;
  state?: string;
};

type CampaignDetails = {
  campaign: {
    id: number;
    name: string;
    state?: string;
  };
  streams: {
    id: number;
    name: string;
    type: string;
    schema: string;
    filters?: {
      name: string;
      mode: string;
      payload: string[];
    }[];
    offers?: {
      offer_id: number;
      share: number;
      state: string;
    }[];
  }[];
};

function getErrorMessage(error: any): string {
  return error.response?.data?.detail || error.message || 'Неизвестная ошибка';
}

function activeFirst(items: CatalogItem[]): CatalogItem[] {
  return [...items].sort((a, b) => {
    if (a.state === 'active' && b.state !== 'active') return -1;
    if (a.state !== 'active' && b.state === 'active') return 1;
    return a.name.localeCompare(b.name);
  });
}

export default function App() {
  const [tab, setTab] = useState<'create' | 'edit'>('create');

  const [catalogs, setCatalogs] = useState<Catalogs>({
    offers: [],
    domains: [],
    groups: [],
    traffic_sources: [],
  });
  const [catalogsLoading, setCatalogsLoading] = useState(true);
  const [catalogsError, setCatalogsError] = useState('');

  const [name, setName] = useState('');
  const [geo, setGeo] = useState('');
  const [offerId, setOfferId] = useState('');
  const [domainId, setDomainId] = useState('');
  const [groupId, setGroupId] = useState('');
  const [trafficSourceId, setTrafficSourceId] = useState('');

  const [campaignId, setCampaignId] = useState('');
  const [offerToChange, setOfferToChange] = useState('');

  const [campaigns, setCampaigns] = useState<CampaignListItem[]>([]);
  const [campaignDetails, setCampaignDetails] =
    useState<CampaignDetails | null>(null);
  const [campaignsLoading, setCampaignsLoading] = useState(false);
  const [campaignLoading, setCampaignLoading] = useState(false);
  const [campaignError, setCampaignError] = useState('');

  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  const offers = activeFirst(catalogs.offers);
  const domains = activeFirst(catalogs.domains);
  const groups = activeFirst(catalogs.groups);
  const trafficSources = activeFirst(catalogs.traffic_sources);

  useEffect(() => {
    async function loadCatalogs() {
      setCatalogsLoading(true);
      setCatalogsError('');

      try {
        const response = await api.get<Catalogs>('/catalogs');
        const data = response.data;

        setCatalogs({
          offers: data.offers || [],
          domains: data.domains || [],
          groups: data.groups || [],
          traffic_sources: data.traffic_sources || [],
        });

        const firstOffer = activeFirst(data.offers || [])[0];
        const firstDomain = activeFirst(data.domains || [])[0];
        const firstGroup = activeFirst(data.groups || [])[0];
        const firstTrafficSource = activeFirst(data.traffic_sources || [])[0];

        setOfferId('');
        setGeo('');
        if (firstDomain) setDomainId(String(firstDomain.id));
        if (firstGroup) setGroupId(String(firstGroup.id));
        if (firstTrafficSource) {
          setTrafficSourceId(String(firstTrafficSource.id));
        }
      } catch (error) {
        setCatalogsError(getErrorMessage(error));
      } finally {
        setCatalogsLoading(false);
      }
    }

    loadCatalogs();
  }, []);

  useEffect(() => {
    if (tab !== 'edit') return;

    let cancelled = false;

    async function loadCampaigns() {
      setCampaignsLoading(true);
      setCampaignError('');

      try {
        const response = await api.get<CampaignListItem[]>('/campaigns/');
        if (!cancelled) setCampaigns(response.data);
      } catch (error) {
        if (!cancelled) setCampaignError(getErrorMessage(error));
      } finally {
        if (!cancelled) setCampaignsLoading(false);
      }
    }

    loadCampaigns();

    return () => {
      cancelled = true;
    };
  }, [tab]);

  useEffect(() => {
    if (!campaignId) {
      setCampaignDetails(null);
      setCampaignError('');
      return;
    }

    let cancelled = false;

    async function loadCampaignDetails() {
      setCampaignLoading(true);
      setCampaignError('');

      try {
        const response = await api.get<CampaignDetails>(
          `/campaigns/${Number(campaignId)}`
        );
        if (!cancelled) setCampaignDetails(response.data);
      } catch (error) {
        if (!cancelled) {
          setCampaignDetails(null);
          setCampaignError(getErrorMessage(error));
        }
      } finally {
        if (!cancelled) setCampaignLoading(false);
      }
    }

    loadCampaignDetails();

    return () => {
      cancelled = true;
    };
  }, [campaignId]);

  function handleOfferChange(value: string) {
    setOfferId(value);

    const selectedOffer = catalogs.offers.find(
      (item) => String(item.id) === value,
    );

    if (selectedOffer?.country?.[0]) {
      setGeo(selectedOffer.country[0]);
    }
  }

  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage('');

    try {
      const response = await api.post('/campaigns/create', {
        name: name.trim(),
        geo: geo.trim().toUpperCase(),
        offer_id: Number(offerId),
        domain_id: Number(domainId),
        group_id: Number(groupId),
        traffic_source_id: Number(trafficSourceId),
      });

      setMessage(
        `Кампания создана\n\n` +
        `Задача: ${response.data.id}\n` +
        `Keitaro ID: ${response.data.keitaro_campaign_id ?? 'не указан'}\n` +
        `Название: ${response.data.campaign_name ?? name}\n` +
        `GEO: ${response.data.geo ?? geo}\n` +
        `Статус: ${response.data.status}`,
      );
    } catch (error) {
      setMessage(`Ошибка создания кампании:\n${getErrorMessage(error)}`);
    } finally {
      setBusy(false);
    }
  }

  async function mutate(action: 'add' | 'remove') {
    if (!campaignId || !offerToChange) return;

    setBusy(true);
    setMessage('');
    setCampaignError('');

    try {
      const url = `/campaigns/${Number(campaignId)}/offers/${Number(offerToChange)}`;
      const response =
        action === 'add'
          ? await api.post(url)
          : await api.delete(url);

      setMessage(response.data.message || 'Операция выполнена');

      try {
        const details = await api.get<CampaignDetails>(
          `/campaigns/${Number(campaignId)}`
        );
        setCampaignDetails(details.data);
      } catch (error) {
        setCampaignError(
          `Операция выполнена, но не удалось обновить данные кампании: ${getErrorMessage(error)}`
        );
      }
    } catch (error) {
      setMessage(`Ошибка операции:\n${getErrorMessage(error)}`);
    } finally {
      setBusy(false);
    }
  }

  function renderOptions(items: CatalogItem[]) {
    return items.map((item) => (
      <option key={item.id} value={item.id}>
        {item.id} — {item.name}
        {item.state && item.state !== 'active' ? ` (${item.state})` : ''}
      </option>
    ));
  }

  return (
    <main className="shell">
      <header>
        <div className="brand">
          <span className="logo">A</span>
          <div>
            <b>ADROBOT</b>
            <small>Keitaro campaign workspace</small>
          </div>
        </div>
        <span className="status">CONTROL PANEL</span>
      </header>

      <section className="intro">
        <p className="eyebrow">ADVERTISING OPERATIONS</p>
        <h1>
          Campaign
          <br />
          <em>management.</em>
        </h1>
        <p className="sub">
          Создание и редактирование кампаний Keitaro в одном рабочем пространстве.
        </p>
      </section>

      <nav>
        <button
          className={tab === 'create' ? 'active' : ''}
          onClick={() => setTab('create')}
        >
          01 / Создать кампанию
        </button>
        <button
          className={tab === 'edit' ? 'active' : ''}
          onClick={() => setTab('edit')}
        >
          02 / Редактор кампании
        </button>
      </nav>

      <section className="panel">
        {tab === 'create' ? (
          <>
            <div className="panelhead">
              <div>
                <p className="eyebrow">NEW WORKFLOW</p>
                <h2>Новая кампания</h2>
              </div>
              <span className="number">01</span>
            </div>

            {catalogsLoading && (
              <p className="catalog-hint">Загружаем данные из Keitaro…</p>
            )}

            {catalogsError && (
              <div className="catalog-error">
                Не удалось загрузить каталоги: {catalogsError}
                <button
                  type="button"
                  className="retry"
                  onClick={() => window.location.reload()}
                >
                  Обновить страницу
                </button>
              </div>
            )}

            <form onSubmit={create}>
              <label>
                Название кампании
                <input
                  required
                  minLength={1}
                  maxLength={255}
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  placeholder="Например, PL — Cardiolux"
                />
              </label>

              <label>
                Оффер Keitaro
                <select
                  required
                  value={offerId}
                  onChange={(event) => handleOfferChange(event.target.value)}
                  disabled={catalogsLoading || offers.length === 0}
                >
                  <option value="">Выберите оффер</option>
                  {renderOptions(offers)}
                </select>
              </label>

              <div className="two">
                <label>
                  GEO-код страны
                  <input
                  required
                  readOnly
                  value={geo}
                  placeholder="Сначала выберите оффер"
                />
                </label>

                <label>
                  Домен
                  <select
                    required
                    value={domainId}
                    onChange={(event) => setDomainId(event.target.value)}
                    disabled={catalogsLoading || domains.length === 0}
                  >
                    <option value="">Выберите домен</option>
                    {renderOptions(domains)}
                  </select>
                </label>
              </div>

              <label>
                Группа кампаний
                <select
                  required
                  value={groupId}
                  onChange={(event) => setGroupId(event.target.value)}
                  disabled={catalogsLoading || groups.length === 0}
                >
                  <option value="">Выберите группу</option>
                  {renderOptions(groups)}
                </select>
              </label>

              <label>
                Источник трафика
                <select
                  required
                  value={trafficSourceId}
                  onChange={(event) => setTrafficSourceId(event.target.value)}
                  disabled={catalogsLoading || trafficSources.length === 0}
                >
                  <option value="">Выберите источник трафика</option>
                  {renderOptions(trafficSources)}
                </select>
              </label>

              <button
                className="primary"
                disabled={
                  busy ||
                  catalogsLoading ||
                  !!catalogsError ||
                  !name.trim() ||
                  !geo.trim() ||
                  !offerId ||
                  !domainId ||
                  !groupId ||
                  !trafficSourceId
                }
              >
                {busy ? 'Создание…' : 'Создать кампанию ↗'}
              </button>
            </form>
          </>
        ) : (
          <>
            <div className="panelhead">
              <div>
                <p className="eyebrow">EXISTING WORKFLOW</p>
                <h2>Редактор офферов</h2>
              </div>
              <span className="number">02</span>
            </div>

            <label>
              Кампания Keitaro
              <select
                value={campaignId}
                onChange={(event) => {
                  setCampaignId(event.target.value);
                  setOfferToChange('');
                  setMessage('');
                }}
                disabled={campaignsLoading || campaigns.length === 0}
              >
                <option value="">
                  {campaignsLoading ? 'Загрузка кампаний…' : 'Выберите кампанию'}
                </option>
                {campaigns.map((campaign) => (
                  <option key={campaign.id} value={campaign.id}>
                    {campaign.id} — {campaign.name}
                    {campaign.state ? ` (${campaign.state})` : ''}
                  </option>
                ))}
              </select>
            </label>

            {campaignError && (
              <p className="catalog-error">{campaignError}</p>
            )}

            {campaignLoading && <p className="catalog-hint">Загрузка кампании…</p>}

            {campaignDetails && (
              <div className="campaign-details">
                <h3>{campaignDetails.campaign.name}</h3>
                <p>
                  ID: {campaignDetails.campaign.id}
                  {campaignDetails.campaign.state
                    ? ` · Статус: ${campaignDetails.campaign.state}`
                    : ''}
                </p>

                <h3>Потоки кампании</h3>
                {campaignDetails.streams.map((stream) => (
                  <div className="stream" key={stream.id}>
                    <b>{stream.name}</b>
                    <p>
                      ID: {stream.id} · Тип: {stream.type} · Схема: {stream.schema}
                    </p>

                    {stream.filters?.map((filter, index) => (
                      <p key={`${stream.id}-filter-${index}`}>
                        Фильтр: {filter.name} · {filter.mode}
                        {filter.payload?.length
                          ? ` · ${filter.payload.join(', ')}`
                          : ''}
                      </p>
                    ))}

                    {stream.offers && stream.offers.length > 0 && (
                      <div className="offer-list">
                        {stream.offers.map((offer) => {
                          const catalogOffer = catalogs.offers.find(
                            (item) => item.id === offer.offer_id
                          );

                          return (
                            <p key={offer.offer_id}>
                              Оффер {offer.offer_id}
                              {catalogOffer ? ` — ${catalogOffer.name}` : ''}
                              {' · '}
                              {offer.share}%
                              {' · '}
                              {offer.state}
                            </p>
                          );
                        })}
                      </div>
                    )}

                    {stream.type === 'default' &&
                      (!stream.offers || stream.offers.length === 0) && (
                        <p>Офферы отсутствуют</p>
                      )}
                  </div>
                ))}
              </div>
            )}

            <label>
              Оффер Keitaro
              <select
                value={offerToChange}
                onChange={(event) => setOfferToChange(event.target.value)}
                disabled={!campaignId || catalogsLoading || offers.length === 0}
              >
                <option value="">Выберите оффер</option>
                {renderOptions(offers)}
              </select>
            </label>

            <div className="actions">
              <button
                className="primary"
                disabled={busy || campaignLoading || !campaignId || !offerToChange}
                onClick={() => mutate('add')}
              >
                Добавить оффер +
              </button>
              <button
                className="danger"
                disabled={busy || campaignLoading || !campaignId || !offerToChange}
                onClick={() => mutate('remove')}
              >
                Удалить оффер −
              </button>
            </div>
          </>
        )}

        {message && <pre className="message">{message}</pre>}
      </section>

      <footer>
        <span>ADROBOT / TEST ASSIGNMENT</span>
        <span>FASTAPI · REACT · KEITARO API</span>
      </footer>
    </main>
  );
}
