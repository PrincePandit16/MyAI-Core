import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Chat from "./page/Chat";
import Login from "./pages/Login";
import Register from "./pages/Register";
import api from "./api/client";

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    api.get("/auth/me").then(() => setIsAuthenticated(true)).catch(() => setIsAuthenticated(false));
  }, []);

  function handleAuthenticated() {
    setIsAuthenticated(true);
  }

  function handleLogout() {
    api.post("/auth/logout").finally(() => setIsAuthenticated(false));
  }

  return (
    <Routes>
      <Route
        path="/"
        element={<Navigate to={isAuthenticated ? "/chat" : "/login"} replace />}
      />
      <Route
        path="/login"
        element={
          isAuthenticated ? (
            <Navigate to="/chat" replace />
          ) : (
            <Login onAuthenticated={handleAuthenticated} />
          )
        }
      />
      <Route
        path="/register"
        element={
          isAuthenticated ? (
            <Navigate to="/chat" replace />
          ) : (
            <Register onAuthenticated={handleAuthenticated} />
          )
        }
      />
      <Route
        path="/chat"
        element={
          isAuthenticated ? (
            <Chat onLogout={handleLogout} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path="*"
        element={<Navigate to={isAuthenticated ? "/chat" : "/login"} replace />}
      />
    </Routes>
  );
}
