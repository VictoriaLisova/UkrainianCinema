import { useParams } from "react-router-dom"
import { searchByPerson } from "./requests"
import { useEffect, useState } from "react";
import Movies from "./Movies";
import Pagination from "./Pagination";
import "./search.css";
import Header from "./Header";

export default function Search(){
    const {person_id} = useParams();
    const [movies, setMovies] = useState([]);
    const [person, setPerson] = useState({});
    const valuesToShow = 20;
    const [currentPage, setCurrentPage] = useState(1);
    const maxPages = Math.ceil(movies.length / valuesToShow);
    const startIndex = (currentPage - 1) * valuesToShow;
    const dataToShow = movies.slice(startIndex, startIndex + valuesToShow);


    useEffect(() => {
        async function getSearchResults(){
            var response = await searchByPerson(person_id);
            if(response){
                setMovies(response.movies);
                setPerson(response.person);
                console.log(response);
            }
        }
        getSearchResults();
    }, [person_id])

    return(
        <>
            <Header/>
            <div className="search-title">
                <h2>{person.name}</h2>
            </div>
            <Movies dataToShow={movies}/>
            <Pagination currentPage={currentPage} setCurrentPage={setCurrentPage} scrollToUp={window.scrollTo({top: 0, behavior: "smooth"})} maxPages={maxPages}/>
        </>
    )
}