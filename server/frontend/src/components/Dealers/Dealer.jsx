import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import Header from '../Header/Header';
import { api } from '../../api';

export default function Dealer() {
  const { id } = useParams();
  const [dealer, setDealer] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  useEffect(() => {
    Promise.all([api('/djangoapp/dealer/' + id), api('/djangoapp/reviews/dealer/' + id), api('/djangoapp/session')])
      .then(([details, comments, session]) => { setDealer(details.dealer[0]); setReviews(comments.reviews); setUsername(session.userName); })
      .catch(err => setError(err.message));
  }, [id]);
  return <><Header /><main>{error && <p role="alert">{error}</p>}
    {dealer ? <><h1>{dealer.full_name}</h1><p>{dealer.address}, {dealer.city}, {dealer.state} {dealer.zip}</p>
      {username ? <a className="btn btn-primary" href={'/postreview/' + id}>Review Dealer</a> : <p><a href="/login">Login</a> to post a review.</p>}
      <h2>Customer reviews</h2><div className="reviews">{reviews.map(review => <article className="review" key={review.id}>
        <span className={'sentiment ' + review.sentiment}>{review.sentiment}</span><p>{review.review}</p>
        <p><strong>{review.name}</strong></p><p>{review.car_make} {review.car_model} · {review.car_year}</p>
      </article>)}</div>{!reviews.length && <p>No reviews yet.</p>}
    </> : !error && <p>Loading dealership…</p>}
  </main></>;
}
