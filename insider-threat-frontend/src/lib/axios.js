import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");

    console.group("AXIOS REQUEST");
    console.log("URL:", `${config.baseURL}${config.url}`);
    console.log("TOKEN:", token);

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    console.log("HEADERS:", config.headers);
    console.groupEnd();

    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => {
    console.group("AXIOS SUCCESS");
    console.log("STATUS:", response.status);
    console.log("DATA:", response.data);
    console.groupEnd();

    return response;
  },
  (error) => {
    console.group("AXIOS ERROR");
    console.log("STATUS:", error.response?.status);
    console.log("DATA:", error.response?.data);
    console.groupEnd();

    return Promise.reject(error);
  }
);

export default api;
