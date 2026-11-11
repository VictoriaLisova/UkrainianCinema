import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { getSuggestions } from "./requests";
import Filtration from "./Filtration";

export default function Header({ isShow, setIsShow }){
    const navigate = useNavigate();
    const [text, setText] = useState("");
    const [suggestions, setSuggestions] = useState([]);
    // const [isShow, setIsShow] = useState(false);

    useEffect(() => {
        const query = text.trim();
        if(query.length < 2){
            setSuggestions([]);
            return;
        }

        const timer = setTimeout(async () => {
            var response = await getSuggestions(query);
            if(response){
                setSuggestions(response);
                console.log(response);
            }
        }, 10)

        return () => clearTimeout(timer);
    }, [text])

    return (
         <section className='header-bar'>
            <div className='logo-block' onClick={() => navigate("/")}>
                <h1>Ukrainian movies</h1>
            </div>
            <div className='filtration-block'>
                <div className='search-block'>
                    {suggestions.length > 0 && (
                        <div className="suggestions-list">
                            {suggestions.map((movie) => (
                                <div key={movie.id} className="suggestion-item" onClick={() => navigate(`/movies/${movie.id}`)}>
                                    <span>{movie.title}</span>
                                    {movie.year && <span>{movie.year}</span>}
                                </div>
                            ))}
                        </div>
                    )}
                    <input type="search" placeholder='Назва фільму...' value={text} onChange={(e) => setText(e.target.value)}/>
                </div>
                <div className='filtration' onClick={() => setIsShow(!isShow)}>
                    <div className='filter-icon'><svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M12 7L20 7" stroke="#ffffff" stroke-linecap="round"></path> <path d="M4 7L8 7" stroke="#ffffff" stroke-linecap="round"></path> <path d="M17 17L20 17" stroke="#ffffff" stroke-linecap="round"></path> <path d="M4 17L12 17" stroke="#ffffff" stroke-linecap="round"></path> <circle cx="10" cy="7" r="2" transform="rotate(90 10 7)" stroke="#ffffff" stroke-linecap="round"></circle> <circle cx="15" cy="17" r="2" transform="rotate(90 15 17)" stroke="#ffffff" stroke-linecap="round"></circle> </g></svg>
                        <p>Фільтри</p>
                    </div>
                </div>
            </div>
            {/* {isShow && (<Filtration/>)} */}
      </section>
    )
}