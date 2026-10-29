import React, { useEffect, useState } from 'react';
import { api } from '../../api';

export default function Header() {
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  useEffect(() => { api('/djangoapp/session').then(data => setUsername(data.userName)).catch(() => {}); }, []);
  async function logout() {
    try { await api('/djangoapp/logout', { method: 'POST' }); window.location.assign('/'); }
    catch (err) { setError(err.message); }
  }
  return <><nav className="site-nav" aria-label="Main navigation">
    <a className="brand" href="/">Cars Dealership</a>
    <a href="/">Home</a><a href="/about">About Us</a><a href="/contact">Contact Us</a>
    <div className="account">{username ? <><strong>{username}</strong><button onClick={logout}>Logout</button></> : <><a href="/login">Login</a><a href="/register">Sign Up</a></>}</div>
  </nav>{error && <p role="alert">{error}</p>}</>;
}
