import { useNavigate } from "react-router-dom";

export default function PeaopleList({people, isCountry}){
    const navigate = useNavigate();

    if (!Array.isArray(people) || people.length === 0) {
        return isCountry ? <p>Україна</p> : <p>Не відомий</p>;
    }

    function checkAvalibility(name) {
        // return name !== "" && name !== null;
        return Array.isArray(name) && name.length > 0;
    }

    return (
        <p className={checkAvalibility(people) ? "ref-itm" : ""}>
            {people.map((person, index) => (
                <span key={person.id}>
                    <span
                        className="ref-itm"
                        onClick={() => navigate(`/${person.id}/movies`)}
                    >
                        {person.name}
                    </span>
                    {index < people.length - 1 && ", "}
                </span>
            ))}
        </p>
    );
}