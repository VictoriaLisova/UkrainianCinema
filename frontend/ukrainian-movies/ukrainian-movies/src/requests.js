import axios from "axios";
const API_URL = "http://127.0.0.1:5000";

/** Отримує повний каталог фільмів із Flask API */
export async function getAllMovies(){
    try{
        const response = await axios.get(API_URL);
        return response.data;
    }catch(error){
        console.error("Error while getting movies", error);
        throw error;
    }
}

/** Отримує детальну інформацію про фільм із сервера.
 * @param {string} id - Ідентифікатор фільму Wikidata.
 * @returns {Promise<Object|null>} Дані фільму або null.
*/
export async function getMovieInfo(id){
    try{
        const responce = await axios.get(`${API_URL}/movie/${id}`);
        return responce.data;
    }catch(error){
        console.error(error);
        throw error;
    }
}

/**
 * Отримує інформацію про людину та її фільмографію
 * @param {string} person_id - Ідентифікатор людини TMDb.
 * @returns {Promise<Object>} Інформація про людину та список фільмів.
*/
export async function searchByPerson(person_id){
    try{
        var response = await axios.get(`${API_URL}/${person_id}/movies`);
        return response.data;
    }catch(error){
        console.error(error);
        throw error;
    }
}

/**
 * Отримує підказки для пошуку за назвою фільму
 * @param {string} text - Пошуковий текст
 * @returns {Promise<Object[]>} Список підказок
*/
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

/**
 * Отримує фільми, які відповідають заданим параметрам фільтрації
 * @param {Object} filters - Параметри фільтрації
 * @param {string} [filters.genre] - Жанр
 * @param {string} [filters.order] - Напрямок сортування asc або desc
 * @param {string|number} [filters.fromYear] - Початковий рік
 * @param {string|number} [filters.toYear] - Кінцевий рік
 * @returns {Promise<Object[]>} Відфільтровані фільми
*/
export async function getFilterData({ genre, order, fromYear, toYear }) {
    try {
        const params = {};
        if (genre) params.genre = genre;
        if (order) params.order = order;
        if (fromYear) params.from_year = fromYear;
        if (toYear) params.to_year = toYear;

        const response = await axios.get(`${API_URL}/filter`, { params });
        return response.data;
    } catch (error) {
        console.error(error);
        throw error;
    }
}

/**
 * Отримує список доступних жанрів із сервера
 * @returns {Promise<string[]>} Список жанрів
*/
export async function getGenres() {
    try {
        const response = await axios.get(`${API_URL}/genres`);
        return response.data;
    } catch (error) {
        console.error(error);
        throw error;
    }
}