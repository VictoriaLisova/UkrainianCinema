import { useEffect, useState } from 'react';
import './App.css';
import { getAllMovies } from './requests';
import Movie from './Movie';
import Movies from './Movies';
import Pagination from './Pagination';
import Header from './Header';
import Filtration from './Filtration';

export default function Catalog() {
  const [movies, setMovies] = useState([]);
  const valuesToShow = 20;
  const [currentPage, setCurrentPage] = useState(1);
  const [allMovies, setAllMovies] = useState([]);
  const [isShow, setIsShow] = useState(false);

  useEffect(() => {
    async function getMovies(){
      var data = await getAllMovies();
      if(data){
        setAllMovies(data);
        console.log(data);
      }
    }
    getMovies();

  }, [])

  function handleFilterResult(filtered){
    setAllMovies(filtered);
    setCurrentPage(1);
  }

  function scrollToUp(){
    window.scrollTo({top: 0, behavior: "smooth"});
  }

  const maxPages = Math.ceil(allMovies.length / valuesToShow);
  const startIndex = (currentPage - 1) * valuesToShow;
  const dataToShow = allMovies.slice(startIndex, startIndex + valuesToShow);

  return (
    <>
      <Header isShow={isShow} setIsShow={setIsShow}/>
      <section className='body-block'>
        <h1>Каталог фільмів</h1>
        <div style={{ display: isShow ? "block" : "none" }}>
          <Filtration onResult={handleFilterResult} />
        </div>
        <Movies dataToShow={dataToShow}/>
      </section>
      <Pagination currentPage={currentPage} setCurrentPage={setCurrentPage} scrollToUp={scrollToUp} maxPages={maxPages}/>
    </>
  )
}
