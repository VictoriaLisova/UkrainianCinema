import axios from "axios";
const API_URL = "http://127.0.0.1:5000";

export async function getAllMovies(){
    try{
        const response = await axios.get(API_URL);
        return response.data;
    }catch(error){
        console.error("Error while getting movies", error);
        throw error;
    }
}

export async function getMovieInfo(id){
    try{
        const responce = await axios.get(`${API_URL}/movie/${id}`);
        return responce.data;
    }catch(error){
        console.error(error);
        throw error;
    }
}

export async function searchByPerson(person_id){
    try{
        var response = await axios.get(`${API_URL}/${person_id}/movies`);
        return response.data;
    }catch(error){
        console.error(error);
        throw error;
    }
}

export async function getSuggestions(text){
    try{
        var response = await axios.get(`${API_URL}/suggestions`, {
            params: {q: text}
        });
        return response.data;
    }catch(error){
        console.error(error);
        throw error;
    }
}

export async function getFilterData(filter_queque){
    try{
        var response = await axios.get(`${API_URL}/filter`, {params: {p: filter_queque}});
        return response.data;
    }catch(error){
        console.error(error);
        throw error;
    }
}
