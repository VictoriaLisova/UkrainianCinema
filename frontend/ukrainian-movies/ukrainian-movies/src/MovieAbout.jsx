import "./movie-about.css";
import { useNavigate, useParams } from "react-router-dom";
import { getMovieInfo } from "./requests";
import { useEffect, useRef, useState } from "react";
import CastMember from "./CastMember";
import PeaopleList from "./PeopleList";

export default function MovieAbout(){
    const {id} = useParams();
    const navigate = useNavigate();
    const [movie, setMovie] = useState({});
    const [genresAmount, setGenresAmount] = useState(0);
    const [hours, sethours] = useState(0);
    const [minutes, setMinutes] = useState(0);
    const [colorNumbers, setColorNumbers] = useState([]);
    const [isReady, setIsReady] = useState(false);

    const castRef = useRef(null);

    function getDuration(duration){
        const minInHour = 60;
        var hours = 0;
        var rest = duration;
        do{
            rest -= minInHour;
            hours++;
        }while(rest >= minInHour);

        sethours(hours);
        setMinutes(rest);

        console.log("hours: " + hours);
        console.log("minutes: " + rest);
    }

    useEffect(() => {
        async function getMovie(){
            var responce = await getMovieInfo(id);
            if(responce){
                setMovie(responce);
                console.log("response: ", responce);
                setGenresAmount(responce.genres.length);
                getDuration(responce.durationMin);
            }
        }
        console.log(id)
        getMovie();
    }, [id])

    const colors = ["#4F63D8", "#A16207", "#BE185D", "#6D5A3C", "#0F766E", "#C2410C", 
        "#52627A", "#B91C1C", "#7E22CE", "#4D7C0F", "#0369A1", "#52525B"]
    
    useEffect(() => {
        function genreColors(){
            const max = colors.length - 1;
            const min = 0;
            var numbers = []
            var i = 0;
            while(i < genresAmount){
                var number = Math.floor(Math.random() * (max - min + 1)) + min;
                if(!numbers.includes(number)){
                    i++;
                    numbers.push(number);
                }
            }
            console.log(numbers);
            setColorNumbers(numbers);
        }

        if(genresAmount > 0){
            genreColors();
        }
        setIsReady(true);
    }, [genresAmount])

    function displayNames(data, isCountry) {
        if(Array.isArray(data)){
            return data.join(", ");
        }
       return data !== null && data !== "" ? data : isCountry ? "Україна" : "Не відомий";
    }

    function checkAvalibility(name) {
        return name !== "" && name !== null;
        // return Array.isArray(name) && name.length > 0;
    }

    function scrollCast(direction){
        if(castRef.current){
            castRef.current.scrollBy({
                left: direction * 150,
                behavior: "smooth"
            });
        }
    }

    function managePageLink(data, person_id){
        if (checkAvalibility(data)){
            useNavigate(`/{person_id}/movies`);
        }

    }

    if(isReady){
        return (
        <>
            <section className="top-block">
                <div id="back-btn" onClick={() => navigate("/")}>
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" stroke="#ffffff"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M6 12H18M6 12L11 7M6 12L11 17" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg>
                    <p>Назад</p>
                </div>
            </section>
            <section className="main-content">
                <div className="img-block">
                    <img src={movie.posterFile !== "None" ? movie.posterFile : 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR8PgItrmj9SWhclDBAmjlyFsC4w9tEKTcvDTbc2puQtQ&s'} alt={movie.title}/>
                </div>
                <div className="general-info">
                    <div>
                        <h2 className="title">{movie.title}</h2>
                        <div className="year-time-info">
                            <p className="year">{movie.releaseDate}</p>
                            <p className="duration">{hours}год {minutes}хв</p>
                        </div>
                    </div>
                    <div className="genres">
                        {(movie.genres ?? []).map((item, index) => {
                            return <button style={{ backgroundColor: colors[colorNumbers[index]] }} key={index}>{item}</button>
                        })}
                    </div>
                    <div className="country">
                        <p className="l-type">Країна походження</p>
                        <p>{displayNames(movie.countries, true)}</p>
                    </div>
                    <div className="language">
                        <p className="l-type">Мова озвучки</p>
                        <p>{displayNames(movie.languages, false)}</p>
                    </div>
                    <div className="director">
                        <p className="l-type">Режисер</p>
                        <PeaopleList people={movie.directors} isCountry={false}/>
                        {/* <p className={checkAvalibility(movie.director) ? "ref-itm" : ""}>{displayNames(movie.director, false)}</p> */}
                    </div>
                    <div className="writer">
                        <p className="l-type">Сценарист</p>
                        <PeaopleList people={movie.screenWriters} isCountry={false}/>
                        {/* <p className={checkAvalibility(movie.screenWriter) ? "ref-itm" : ""}>{displayNames(movie.screenWriter, false)}</p> */}
                    </div>
                    <div className="dop">
                        <p className="l-type">Оператор-постановник</p>
                        <PeaopleList people={movie.photographyDirectors} isCountry={false}/>
                        {/* <p className={checkAvalibility(movie.photographyDirector) ? "ref-itm" : ""}>{displayNames(movie.photographyDirector, false)}</p> */}
                    </div>
                    <div className="editor">
                        <p className="l-type">Монтажер</p>
                        <PeaopleList people={movie.editors} isCountry={false}/>
                        {/* <p className={checkAvalibility(movie.editor) ? "ref-itm" : ""}>{displayNames(movie.editor)}</p> */}
                    </div>
                    <div className="composite">
                        <p className="l-type">Композитор</p>
                        <PeaopleList people={movie.composers} isCountry={false}/>
                        {/* <p className={checkAvalibility(movie.composer) ? "ref-itm" : ""}>{displayNames(movie.composer)}</p> */}
                    </div>
                    <div className="company">
                        <p className="l-type">Виробнича компанія</p>
                        <PeaopleList people={movie.companies} isCountry={false}/>
                        {/* <p className={checkAvalibility(movie.company) ? "ref-itm" : ""}>{displayNames(movie.company)}</p> */}
                    </div>
                    <div className="distributor">
                        <p className="l-type">Дистриб'ютор</p>
                        <PeaopleList people={movie.distributor} isCountry={false}/>
                        {/* <p className={checkAvalibility(movie.distributor) ? "ref-itm" : ""}>{displayNames(movie.distributor)}</p> */}
                    </div>
                </div>
                <div className="inf">
                    <div className="overview">
                        <h2>Опис</h2>
                        <p>{movie.description ?? "Опис не надано."}</p>
                    </div>
                    <div className="cast-block">
                        <h2>Каст</h2>
                        {Array.isArray(movie.cast) && movie.cast.length > 0 ? (
                            <div className="members">
                                <button id="b-c-arr"
                                onClick={() => scrollCast(-1)}
                                ><svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M6 12H18M6 12L11 7M6 12L11 17" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg></button>
                                <div className="cast-track" ref={castRef}>
                                    {movie.cast?.map((member, index) => (
                                        <CastMember key={index} person_id={member.id} name={member.name} role={member.characters[0]} img={member.photo}/>
                                    ))}
                                </div>
                                <button id="n-c-arr"
                                onClick={() => scrollCast(1)}
                                ><svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" transform="matrix(-1, 0, 0, 1, 0, 0)"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M6 12H18M6 12L11 7M6 12L11 17" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg></button>
                            </div>
                        ) :<p className="cast-no-info">Даних не має.</p>}
                    </div>
                </div>
            </section>
        </>
    )
    }
}
