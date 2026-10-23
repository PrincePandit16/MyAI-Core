import { useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Chat from "./page/Chat";
import Login from "./pages/Login";
import Register from "./pages/Register";
import { clearToken, getToken, saveToken } from "./services/auth";

export default function App() {
  const [token, setToken] = useState(getToken);
  const isAuthenticated = Boolean(token);

  function handleAuthenticated(accessToken: string) {
    saveToken(accessToken);
    setToken(accessToken);
  }

  function handleLogout() {
    clearToken();
    setToken(null);
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
