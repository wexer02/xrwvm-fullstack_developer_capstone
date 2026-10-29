import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Header from '../Header/Header';
import { api } from '../../api';

export default function PostReview() {
  const { id } = useParams();
  const [dealer, setDealer] = useState({});
  const [cars, setCars] = useState([]);
  const [review, setReview] = useState('');
  const [model, setModel] = useState('');
  const [year, setYear] = useState('2023');
  const [date, setDate] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  useEffect(() => {
    Promise.all([api('/djangoapp/dealer/' + id), api('/djangoapp/get_cars'), api('/djangoapp/session')])
      .then(([details, catalog, session]) => {
        if (!session.authenticated) { window.location.assign('/login'); return; }
        setDealer(details.dealer[0]);
        setCars([...new Map(catalog.CarModels.map(car => [JSON.stringify([car.CarMake, car.CarModel]), car])).values()]);
      }).catch(err => setError(err.message));
  }, [id]);
  async function submit(event) {
    event.preventDefault(); setError(''); setSaving(true);
    try {
      const [make, carModel] = JSON.parse(model);
      await api('/djangoapp/add_review', { method: 'POST', body: JSON.stringify({
        dealership: Number(id), review, purchase: true, purchase_date: date,
        car_make: make, car_model: carModel, car_year: Number(year),
      }) });
      window.location.assign('/dealer/' + id);
    } catch (err) { setError(err.message); setSaving(false); }
  }
  return <><Header /><main className="form-page"><h1>Review {dealer.full_name}</h1>
    <form onSubmit={submit}>{error && <p role="alert">{error}</p>}
      <label htmlFor="review">Your review</label><textarea id="review" rows="4" required maxLength="5000" value={review} onChange={e => setReview(e.target.value)} />
      <label htmlFor="purchase-date">Purchase Date</label><input id="purchase-date" type="date" required max={new Date().toISOString().slice(0, 10)} value={date} onChange={e => setDate(e.target.value)} />
      <label htmlFor="cars">Car Make and Model</label><select id="cars" required value={model} onChange={e => setModel(e.target.value)}>
        <option value="">Choose Car Make and Model</option>{cars.map(car => <option key={car.CarMake + car.CarModel} value={JSON.stringify([car.CarMake, car.CarModel])}>{car.CarMake} {car.CarModel}</option>)}
      </select>
      <label htmlFor="car-year">Car Year</label><input id="car-year" type="number" required min="2015" max={new Date().getFullYear()} value={year} onChange={e => setYear(e.target.value)} />
      <button type="submit" disabled={saving}>{saving ? 'Saving…' : 'Post Review'}</button>
    </form></main></>;
}
