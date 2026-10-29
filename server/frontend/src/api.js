export async function api(url, options = {}) {
  const headers = { ...options.headers };
  if (options.method && options.method !== 'GET') {
    const tokenResponse = await fetch('/djangoapp/csrf');
    const token = await tokenResponse.json();
    headers['X-CSRFToken'] = token.csrfToken;
    headers['Content-Type'] = 'application/json';
  }
  const response = await fetch(url, { ...options, headers });
  const data = await response.json();
  if (!response.ok) throw new Error(data.message || 'Unable to complete request.');
  return data;
}
