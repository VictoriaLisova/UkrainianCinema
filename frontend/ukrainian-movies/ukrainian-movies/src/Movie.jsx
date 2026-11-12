import { useNavigate } from "react-router-dom"

/** Відображає картку фільму з переходом до детальної інформації */
export default function Movie({id, poster, title, year, genres}){
  const navigate = useNavigate();

    return (
        <div className='movie' onClick={() => navigate(`/movies/${id.split("/").pop()}`)}>
            <div className='img-block'>
                <img src={poster === null ? 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR8PgItrmj9SWhclDBAmjlyFsC4w9tEKTcvDTbc2puQtQ&s' : poster} alt={title}/></div>
            <div className='movie-info'>
              <p className='movie-name'>{title}</p>
              <div className='inline-block'>
                <p>{year}</p>
                <p>{Array.isArray(genres) ? genres.join(", ") : genres}</p>
              </div>
            </div>
          </div>
    )
}