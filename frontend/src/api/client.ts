import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "",
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const detail: unknown = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      const messages = detail
        .map((item: unknown) => {
          if (typeof item === "object" && item !== null && "msg" in item) {
            return String(item.msg);
          }
          return "";
        })
        .filter(Boolean);
      if (messages.length > 0) return messages.join(", ");
    }
    if (error.response) return `Request failed (HTTP ${error.response.status}).`;
    return error.message || fallback;
  }
  return error instanceof Error ? error.message : fallback;
}

export default api;
