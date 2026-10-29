import React, { useState } from 'react';
import Header from '../Header/Header';
import { api } from '../../api';

export default function Register() {
  const [fields, setFields] = useState({ username: '', first_name: '', last_name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const update = event => setFields({ ...fields, [event.target.name]: event.target.value });
  async function submit(event) {
    event.preventDefault();
    try { await api('/djangoapp/register', { method: 'POST', body: JSON.stringify(fields) }); window.location.assign('/'); }
    catch (err) { setError(err.message); }
  }
  return <><Header /><main className="form-page"><h1>Sign Up</h1><form onSubmit={submit}>
    {error && <p role="alert">{error}</p>}
    <label htmlFor="username">Username</label><input id="username" name="username" autoComplete="username" required value={fields.username} onChange={update} />
    <label htmlFor="first-name">First Name</label><input id="first-name" name="first_name" autoComplete="given-name" required value={fields.first_name} onChange={update} />
    <label htmlFor="last-name">Last Name</label><input id="last-name" name="last_name" autoComplete="family-name" required value={fields.last_name} onChange={update} />
    <label htmlFor="email">Email</label><input id="email" name="email" type="email" autoComplete="email" required value={fields.email} onChange={update} />
    <label htmlFor="password">Password</label><input id="password" name="password" type="password" autoComplete="new-password" minLength="10" required value={fields.password} onChange={update} />
    <button type="submit">Register</button>
  </form></main></>;
}
