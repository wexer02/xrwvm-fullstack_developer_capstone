import React, { useEffect, useState } from 'react';
import Header from '../Header/Header';
import { api } from '../../api';

export default function Dealers() {
  const [dealers, setDealers] = useState([]);
  const [states, setStates] = useState([]);
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [state, setState] = useState(new URLSearchParams(window.location.search).get('state') || 'All');
  useEffect(() => {
    api('/djangoapp/get_dealers').then(data => {
      setStates([...new Set(data.dealers.map(dealer => dealer.state))].sort());
    }).catch(err => setError(err.message));
    api('/djangoapp/session').then(data => setUsername(data.userName)).catch(err => setError(err.message));
  }, []);
  useEffect(() => {
    setError('');
    api('/djangoapp/get_dealers' + (state === 'All' ? '' : '/' + encodeURIComponent(state)))
      .then(data => setDealers(data.dealers)).catch(err => setError(err.message));
    window.history.replaceState(null, '', state === 'All' ? '/' : '/?state=' + encodeURIComponent(state));
  }, [state]);
  return <><Header /><main>
    <h1>Find a dealership</h1><p>Browse our branches and read what customers have to say.</p>
    <label htmlFor="state">Filter by state</label> <select id="state" value={state} onChange={e => setState(e.target.value)}>
      <option value="All">All States</option>{states.map(item => <option key={item}>{item}</option>)}
    </select>
    {error && <p role="alert">{error}</p>}
    <p>{dealers.length} dealerships {state !== 'All' && 'in ' + state}</p>
    <div className="table-wrap"><table className="table table-striped"><thead><tr>
      <th>ID</th><th>Dealer Name</th><th>City</th><th>Address</th><th>Zip</th><th>State</th>{username && <th>Review Dealer</th>}
    </tr></thead><tbody>{dealers.map(dealer => <tr key={dealer.id}>
      <td>{dealer.id}</td><td><a href={'/dealer/' + dealer.id}>{dealer.full_name}</a></td>
      <td>{dealer.city}</td><td>{dealer.address}</td><td>{dealer.zip}</td><td>{dealer.state}</td>
      {username && <td><a href={'/postreview/' + dealer.id}>Review Dealer</a></td>}
    </tr>)}</tbody></table></div>
  </main></>;
}
