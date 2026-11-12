import Movie from "./Movie";

/** Формує список карток фільмів */
export default function Movies({dataToShow}){
    return (
        <div className='movies'>
            {dataToShow.map((movie, _) => (
                <Movie key={movie.id} id={movie.id} poster={movie.poster} title={movie.title} year={movie.date} genres={movie.genres}/>
            ))}
        </div>
    )
}