import { useNavigate } from "react-router-dom";

/** Відображає список сутностей та переходи за їхніми ідентифікаторами
 * @param {Object} props - Властивості компонента
 * @param {Object[]} props.people - Сутності з полями id та name
 * @param {boolean} props.isCountry - Ознака підстановки назви країни за відсутності даних
*/
export default function PeaopleList({people, isCountry}){
    const navigate = useNavigate();

    if (!Array.isArray(people) || people.length === 0) {
        return isCountry ? <p>Україна</p> : <p>Не відомий</p>;
    }

    /** Перевіряє, чи передане значення є непорожнім масивом */
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