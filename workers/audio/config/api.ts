import axios from "axios";
import "dotenv/config"

export const serApi = axios.create({
    baseURL: process.env.NODE_ENV === "development" ? process.env.DEV_SER_API_URL : process.env.PROD_SER_API_URL,
    timeout: 20000,
    headers: {
        "Access-Control-Allow-Methods": "GET,PUT,POST,DELETE,PATCH,OPTIONS",
        "x-api-key": process.env.SER_FER_API_KEY,
    },
    validateStatus: () => true,
    withCredentials: true,
})


export const ferApi = axios.create({
    baseURL: process.env.NODE_ENV === "development" ? process.env.DEV_FER_API_URL : process.env.PROD_FER_API_URL,
    timeout: 20000,
    headers: {
        "Access-Control-Allow-Methods": "GET,PUT,POST,DELETE,PATCH,OPTIONS",
        "x-api-key": process.env.SER_FER_API_KEY,
    },
    validateStatus: () => true,
    withCredentials: true,
})