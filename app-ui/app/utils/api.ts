import axios from "axios";

const url = new URL("", import.meta.env.VITE_API_URL).toString();
export default axios.create({
  baseURL: url,
  headers: {
    "Content-Type": "application/json, text/plain, */*",
  },
  withCredentials: true,
  xsrfCookieName: "X-Xsrf-Token",
  xsrfHeaderName: "X-Xsrf-Token",
  withXSRFToken: true,
});
