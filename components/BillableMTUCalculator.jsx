const BillableMTUCalculator = () => {
  const [inputs, setInputs] = useState({
    totalMtu: 80000,
    eventBasis: 'total',
    events: 12000000,
    fup: 100
  });

  const [result, setResult] = useState({ eventsOverFup: 0, billableMtu: 0, driver: 'mtu' });

  useEffect(() => {
    const { totalMtu, events, fup } = inputs;
    const safeFup = fup > 0 ? fup : 1;
    const eventsOverFup = Math.round(events / safeFup);
    const billableMtu = Math.max(totalMtu, eventsOverFup);
    const driver = eventsOverFup > totalMtu ? 'events' : 'mtu';

    setResult({ eventsOverFup, billableMtu, driver });
  }, [inputs]);

  const reset = () => setInputs({ totalMtu: 80000, eventBasis: 'total', events: 12000000, fup: 100 });

  const basisLabel = inputs.eventBasis === 'custom' ? 'Custom User Actions' : 'Total Tracked Events';

  return (
    <div style={{ fontFamily: 'Inter, sans-serif', border: '1px solid #e1e8ed', borderRadius: '12px', background: '#fff', maxWidth: '950px', margin: '20px auto', overflow: 'hidden' }}>
      <div style={{ background: '#023047', color: 'white', padding: '12px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '13px', fontWeight: 'bold', textTransform: 'uppercase' }}>Billable MTU Calculator</span>
        <button onClick={reset} style={{ background: 'rgba(255,255,255,0.2)', border: '1px solid rgba(255,255,255,0.3)', color: 'white', fontSize: '10px', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer' }}>RESET</button>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', background: '#e1e8ed', gap: '1px' }}>
        <div style={{ flex: '1.5', minWidth: '350px', background: '#fff', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: '800', color: '#6a7c92', textTransform: 'uppercase', marginBottom: '6px' }}>
              Total MTU (Mobile + Web + TV)
            </label>
            <input
              type="number"
              min="0"
              value={inputs.totalMtu}
              onChange={(e) => setInputs((p) => ({ ...p, totalMtu: parseInt(e.target.value, 10) || 0 }))}
              style={{ width: '100%', padding: '10px', border: '1px solid #e1e8ed', borderRadius: '6px', fontSize: '15px', fontWeight: 'bold', fontFamily: 'monospace' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: '800', color: '#6a7c92', textTransform: 'uppercase', marginBottom: '6px' }}>
              Event basis (per your contract)
            </label>
            <select
              value={inputs.eventBasis}
              onChange={(e) => setInputs((p) => ({ ...p, eventBasis: e.target.value }))}
              style={{ width: '100%', padding: '10px', border: '1px solid #e1e8ed', borderRadius: '6px', fontSize: '13px' }}
            >
              <option value="custom">Custom User Actions</option>
              <option value="total">Total Tracked Events</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: '800', color: '#6a7c92', textTransform: 'uppercase', marginBottom: '6px' }}>
              Events this month (selected basis)
            </label>
            <input
              type="number"
              min="0"
              value={inputs.events}
              onChange={(e) => setInputs((p) => ({ ...p, events: parseInt(e.target.value, 10) || 0 }))}
              style={{ width: '100%', padding: '10px', border: '1px solid #e1e8ed', borderRadius: '6px', fontSize: '15px', fontWeight: 'bold', fontFamily: 'monospace' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: '800', color: '#6a7c92', textTransform: 'uppercase', marginBottom: '6px' }}>
              Contracted FUP (events per user)
            </label>
            <input
              type="number"
              min="1"
              value={inputs.fup}
              onChange={(e) => setInputs((p) => ({ ...p, fup: parseInt(e.target.value, 10) || 1 }))}
              style={{ width: '100%', padding: '10px', border: '1px solid #e1e8ed', borderRadius: '6px', fontSize: '15px', fontWeight: 'bold', fontFamily: 'monospace' }}
            />
          </div>
        </div>

        <div style={{ flex: '1', minWidth: '280px', background: '#f8fafc', padding: '30px', display: 'flex', flexDirection: 'column', justifyContent: 'center', borderLeft: '1px solid #e1e8ed' }}>
          <div style={{ display: 'flex', gap: '10px', marginBottom: '16px' }}>
            <div style={{ flex: 1, background: result.driver === 'mtu' ? '#e6f7f4' : '#fff', border: `1px solid ${result.driver === 'mtu' ? '#2a9d8f' : '#e1e8ed'}`, borderRadius: '8px', padding: '12px' }}>
              <div style={{ fontSize: '10px', color: '#6a7c92', textTransform: 'uppercase', marginBottom: '4px' }}>Total MTU</div>
              <div style={{ fontSize: '18px', fontWeight: '800', fontFamily: 'monospace', color: '#023047' }}>{inputs.totalMtu.toLocaleString()}</div>
            </div>
            <div style={{ flex: 1, background: result.driver === 'events' ? '#e6f7f4' : '#fff', border: `1px solid ${result.driver === 'events' ? '#2a9d8f' : '#e1e8ed'}`, borderRadius: '8px', padding: '12px' }}>
              <div style={{ fontSize: '10px', color: '#6a7c92', textTransform: 'uppercase', marginBottom: '4px' }}>Events ÷ FUP</div>
              <div style={{ fontSize: '18px', fontWeight: '800', fontFamily: 'monospace', color: '#023047' }}>{result.eventsOverFup.toLocaleString()}</div>
            </div>
          </div>

          <div style={{ background: '#fff', border: '1px solid #e1e8ed', borderRadius: '8px', padding: '16px', borderLeft: '4px solid #023047' }}>
            <div style={{ fontSize: '11px', fontWeight: 'bold', color: '#6a7c92', textTransform: 'uppercase', marginBottom: '6px' }}>Billable MTU</div>
            <div style={{ fontSize: '26px', fontWeight: '800', fontFamily: 'monospace', color: '#023047', marginBottom: '10px' }}>{result.billableMtu.toLocaleString()}</div>
            <div style={{ fontSize: '12px', color: '#475569', lineHeight: '1.5' }}>
              {result.driver === 'events'
                ? `Driven by ${basisLabel} ÷ FUP. Your event volume is above your FUP allowance.`
                : 'Driven by Total MTU. Your event volume is within your FUP allowance.'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BillableMTUCalculator;
