import { useEffect, useState } from "react";
import { getFilterData, getGenres } from "./requests";
import "./search.css";

export default function Filtration({ onResult }) {
    const [genres, setGenres] = useState([]);
    const [genre, setGenre] = useState("");
    const [order, setOrder] = useState("");
    const [fromYear, setFromYear] = useState("");
    const [toYear, setToYear] = useState("");

    useEffect(() => {
        getGenres().then(setGenres);
    }, []);

    async function apply(filters){
        try{
            const movies = await getFilterData(filters);
            onResult?.(movies);
        }catch{
            onResult?.([]);
        }
    }

    async function handleBtnClick() {
        await apply({genre, order, fromYear, toYear});
    }


    async function handleReset() {
        setGenre("");
        setOrder("");
        setFromYear("");
        setToYear("");
        await apply({});
    }

    return (
        <section className="filtration-b">
            <div className="f-year">
                <label>Рік виробництва</label>
                <div className="range-bar-text">
                    <div className="from">
                        <label htmlFor="r-from">з</label>
                        <input type="number" id="r-from" min="1890" max="2100"
                               value={fromYear}
                               onChange={(e) => setFromYear(e.target.value)} />
                    </div>
                    <div className="to">
                        <label htmlFor="r-to">до</label>
                        <input type="number" id="r-to" min="1890" max="2100"
                               value={toYear}
                               onChange={(e) => setToYear(e.target.value)} />
                    </div>
                </div>
            </div>

            <div className="genre-block">
                <label htmlFor="f-genre">Жанр</label>
                <select id="f-genre" value={genre}
                        onChange={(e) => setGenre(e.target.value)}>
                    <option value="">Усі жанри</option>
                    {genres.map((g) => (
                        <option key={g} value={g}>{g}</option>
                    ))}
                </select>
            </div>

            <div className="order-block">
                <label htmlFor="f-order">Сортування за роком</label>
                <select id="f-order" value={order}
                        onChange={(e) => setOrder(e.target.value)}>
                    <option value="">Без сортування</option>
                    <option value="asc">За зростанням</option>
                    <option value="desc">За спаданням</option>
                </select>
            </div>

            <div className="submit-btn-block">
                <button id="sbt-f" onClick={handleBtnClick}>Застосувати</button>
                <button  id="rst-f" type="button" onClick={handleReset}>Скинути</button>
            </div>
        </section>
    );
}
