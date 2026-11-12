/** Точка входу React-застосунку та налаштування маршрутів */
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './App.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Catalog from './Catalog'
import MovieAbout from './MovieAbout'
import Search from './Search'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Catalog/>}/>
        <Route path="/movies/:id" element={<MovieAbout/>}/>
        <Route path="/:person_id/movies" element={<Search/>}/>
      </Routes>
    </BrowserRouter>
  </StrictMode>
)
