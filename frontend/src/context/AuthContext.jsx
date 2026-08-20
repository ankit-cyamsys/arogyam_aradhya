import { createContext, useContext, useEffect, useState } from "react";
import api from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => {
    const raw = localStorage.getItem("aa_auth");
    return raw ? JSON.parse(raw) : null;
  });
  const [ready, setReady] = useState(true);

  const persist = (data) => {
    if (data) {
      localStorage.setItem("aa_token", data.access_token);
      localStorage.setItem("aa_auth", JSON.stringify(data));
    } else {
      localStorage.removeItem("aa_token");
      localStorage.removeItem("aa_auth");
    }
    setAuth(data);
  };

  const login = async (username, password, segment) => {
    const { data } = await api.post("/auth/login", { username, password, segment });
    persist(data);
    return data;
  };

  const signup = async (payload) => {
    const { data } = await api.post("/auth/signup", payload);
    persist(data);
    return data;
  };

  const directSignup = async (payload) => {
    const { data } = await api.post("/auth/direct/signup", payload);
    persist(data);
    return data;
  };

  const adminLogin = async (username, password) => {
    const { data } = await api.post("/auth/admin/login", { username, password });
    persist(data);
    return data;
  };

  const logout = () => persist(null);

  return (
    <AuthContext.Provider value={{ auth, ready, login, signup, directSignup, adminLogin, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
