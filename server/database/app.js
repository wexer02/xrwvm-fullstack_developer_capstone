const express = require('express');
const mongoose = require('mongoose');
const fs = require('node:fs');
const path = require('node:path');

const app = express();
app.use(express.json({ limit: '16kb' }));
const Reviews = require('./review');
const Dealerships = require('./dealership');
const Counter = mongoose.model('counter', new mongoose.Schema({ _id: String, seq: Number }));
const data = name => JSON.parse(fs.readFileSync(path.join(__dirname, 'data', name), 'utf8'));
const route = handler => async (req, res, next) => {
  try { await handler(req, res); } catch (error) { next(error); }
};

app.get('/', (req, res) => res.json({ service: 'Dealer and Review API', status: 'ready' }));
app.get('/fetchReviews', route(async (req, res) => res.json(await Reviews.find({}, '-_id -__v').sort({ id: -1 }))));
app.get('/fetchReviews/dealer/:id', route(async (req, res) => {
  res.json(await Reviews.find({ dealership: Number(req.params.id) }, '-_id -__v').sort({ id: -1 }));
}));
app.get('/fetchDealers', route(async (req, res) => {
  res.json(await Dealerships.find({}, '-_id -__v').sort({ id: 1 }));
}));
app.get('/fetchDealers/:state', route(async (req, res) => {
  res.json(await Dealerships.find(req.params.state === 'All' ? {} : { state: req.params.state }, '-_id -__v').sort({ id: 1 }));
}));
app.get('/fetchDealer/:id', route(async (req, res) => {
  res.json(await Dealerships.find({ id: Number(req.params.id) }, '-_id -__v'));
}));
app.post('/insert_review', route(async (req, res) => {
  if (!process.env.INTERNAL_API_KEY || req.get('X-API-Key') !== process.env.INTERNAL_API_KEY) {
    return res.status(403).json({ error: 'This endpoint is for the Django service.' });
  }
  const input = req.body;
  const dealer = Number(input.dealership);
  if (!Number.isInteger(dealer) || !await Dealerships.exists({ id: dealer })) {
    return res.status(400).json({ error: 'Unknown dealership.' });
  }
  if (typeof input.review !== 'string' || !input.review.trim() || input.review.length > 5000 ||
      typeof input.name !== 'string' || !input.name.trim() || input.name.length > 150 ||
      typeof input.car_make !== 'string' || typeof input.car_model !== 'string' ||
      !Number.isInteger(input.car_year) || input.car_year < 2015 || input.car_year > new Date().getFullYear() ||
      typeof input.purchase_date !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(input.purchase_date)) {
    return res.status(400).json({ error: 'Invalid review data.' });
  }
  const counter = await Counter.findByIdAndUpdate('reviews', { $inc: { seq: 1 } }, { new: true });
  const review = await Reviews.create({
    id: counter.seq, name: input.name.trim(), dealership: dealer, review: input.review.trim(),
    purchase: true, purchase_date: input.purchase_date, car_make: input.car_make,
    car_model: input.car_model, car_year: input.car_year,
  });
  res.status(201).json(review);
}));
app.use((error, req, res, next) => {
  console.error(error.message);
  res.status(error instanceof SyntaxError ? 400 : 500).json({ error: 'Unable to process request.' });
});

async function start() {
  await mongoose.connect(process.env.MONGO_URL || 'mongodb://127.0.0.1:27017/dealershipsDB');
  // Seed only empty collections so restarts preserve reviews.
  if (!await Dealerships.exists({})) await Dealerships.insertMany(data('dealerships.json').dealerships);
  if (!await Reviews.exists({})) await Reviews.insertMany(data('reviews.json').reviews);
  const latest = await Reviews.findOne().sort({ id: -1 });
  await Counter.findByIdAndUpdate('reviews', { $max: { seq: latest ? latest.id : 0 } }, { upsert: true });
  app.listen(Number(process.env.API_PORT || 3030), '127.0.0.1', () => console.log('Dealer API ready on port 3030'));
}
start().catch(error => { console.error(error.message); process.exit(1); });
