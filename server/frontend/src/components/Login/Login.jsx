import React, { useState } from 'react';
import Header from '../Header/Header';
import { api } from '../../api';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  async function submit(event) {
    event.preventDefault();
    try { await api('/djangoapp/login', { method: 'POST', body: JSON.stringify({ userName: username, password }) }); window.location.assign('/'); }
    catch (err) { setError(err.message); }
  }
  return <><Header /><main className="form-page"><h1>Login</h1><form onSubmit={submit}>
    {error && <p role="alert">{error}</p>}
    <label htmlFor="username">Username</label><input id="username" autoComplete="username" required value={username} onChange={e => setUsername(e.target.value)} />
    <label htmlFor="password">Password</label><input id="password" type="password" autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)} />
    <button type="submit">Login</button><a href="/register">Create an account</a>
  </form></main></>;
}
