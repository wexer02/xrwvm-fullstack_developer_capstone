import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Dealers from './components/Dealers/Dealers';
import Dealer from './components/Dealers/Dealer';
import PostReview from './components/Dealers/PostReview';
import Login from './components/Login/Login';
import Register from './components/Register/Register';

export default function App() {
  return <Routes>
    <Route path="/" element={<Dealers />} />
    <Route path="/login" element={<Login />} />
    <Route path="/register" element={<Register />} />
    <Route path="/dealer/:id" element={<Dealer />} />
    <Route path="/postreview/:id" element={<PostReview />} />
  </Routes>;
}
