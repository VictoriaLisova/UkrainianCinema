import { useNavigate } from "react-router-dom"

export default function CastMember({person_id, name, role, img}){
    const navigate = useNavigate();

    return (
         <div className="cast-member" onClick={() => navigate(`/${person_id}/movies`)}>
            <div className="cast-img">
                <img src={img ?? 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTkvallQ5ZGN8H0RHyH6fe91ycZ2NbnLPmx9x-2_NqnBQ&s=10'} alt={name}/>
            </div>
            <p>{name}</p>
            <p className="role">{role}</p>
        </div>
    )
}