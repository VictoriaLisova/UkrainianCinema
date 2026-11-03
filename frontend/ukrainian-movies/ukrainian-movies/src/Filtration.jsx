import { useState } from "react";
import { getFilterData } from "./requests";
import "./search.css";

export default function Filtration(){
    const [fromYear, setFromYear] = useState(0);
    const [toYear, setToYear] = useState(0);
    const [genre, setGenre] = useState("");
    const [company, setCompany] = useState("");
    const [distributor, setDistributor] = useState("");
    const [director, setDirector] = useState("");
    const [writer, setWriter] = useState("");
    const [dop, setDop] = useState("");
    const [editor, setEditor] = useState("");
    const [composer, setComposer] = useState("");
    const [actor, setActor] = useState("");
    const [status, setStatus] = useState(false);
    const [filterRequestData, setFilterRequestData] = useState({});

    async function handleBtnClick(){
        var response = await getFilterData(filterRequestData);

    }

    return (
        <section className="filtration-b">
            <div className="f-year">
                <div className="range-bar">
                    <label htmlFor="year">Рік виробництва</label>
                    <input type="range" id="year" name="year"/>
                </div>
                <div className="range-bar-text">
                    <div className="from">
                        <label htmlFor="r-from">з</label>
                        <input readOnly type="number" id="r-from" name="r-from" value={fromYear}/>
                    </div>
                    <div className="to">
                        <label htmlFor="r-to">до</label>
                        <input readOnly type="number" id="r-to" name="r-to" value={toYear}/>
                    </div>
                </div>
            </div>
            <div className="genre-block">
                <label htmlFor="f-genre" onChange={(e) => setGenre(e.target.value)} value={genre}>Жанр</label>
                <select id="f-genre">
                    <option>Option 1</option>
                    <option>Option 2</option>
                    <option>Option 3</option>
                </select>
            </div>
            <div className="company-block">
                <label htmlFor="f-company" onChange={(e) => setCompany(e.target.value)} value={company}>Компанія-виробник</label>
                <select id="f-company">
                    <option>Option 1</option>
                    <option>Option 2</option>
                    <option>Option 3</option>
                </select>
            </div>
            <div className="distributor-block">
                <label htmlFor="f-distributor" onChange={(e) => setDistributor(e.target.value)} value={distributor}>Дистриб'ютор</label>
                <select id="f-distributor">
                    <option>Option 1</option>
                    <option>Option 2</option>
                    <option>Option 3</option>
                </select>
            </div>
            <div className="director-block">
                <label htmlFor="f-director">Режисер</label>
                <input type="search" id="f-director" name="f-director" value={director} onChange={(e) => setDirector(e.target.value)}/>
            </div>
            <div className="writer-block">
                <label htmlFor="f-writer">Сценарист</label>
                <input type="search" id="f-writer" name="f-writer" value={writer} onChange={(e) => setWriter(e.target.value)}/>
            </div>
            <div className="dop-block">
                <label htmlFor="f-dop">Оператор-постановник</label>
                <input type="search" id="f-dop" name="f-dop" value={dop} onChange={(e) => setDop(e.target.value)}/>
            </div>
            <div className="editor-block">
                <label htmlFor="f-editor">Монтажер</label>
                <input type="search" id="f-editor" name="f-editor" value={editor} onChange={(e) => setEditor(e.target.value)}/>
            </div>
            <div className="composer-block">
                <label htmlFor="f-composer">Композитор</label>
                <input type="search" id="f-composer" name="f-composer" value={composer} onChange={(e) => setComposer(e.target.value)}/>
            </div>
            <div className="actor-block">
                <label htmlFor="f-actor">Актор</label>
                <input type="search" id="f-actor" name="f-actor"  value={actor} onChange={(e) => setActor(e.target.value)}/>
            </div>
            <div className="status-block">
                <p>Завершений/Незавершений</p>
                <div className="status-check">
                    <div className="check-s">
                        <input type="checkbox" id="ended" name="ended" onChange={() => setStatus(true)}/>
                        <label htmlFor="ended">Завершений</label>
                    </div>
                    <div className="check-s">
                        <input type="checkbox" id="not-ended" name="not-ended" onChange={() => setStatus(false)}/>
                        <label htmlFor="not-ended">Незавершений</label>
                    </div>
                </div>
            </div>
            <div className="submit-btn-block">
                <button id="sbt-f" onClick={handleBtnClick}>Застосувати</button>
            </div>
        </section>
    )
}