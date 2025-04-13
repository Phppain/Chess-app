import React from "react";
import { Navigate } from "react-router-dom";

// Здесь можно использовать auth-хранилище или localStorage/token
const isAuthenticated = () => {
    return localStorage.getItem("userToken") !== null;
};

const PrivateRoute = ({ children }) => {
    return isAuthenticated() ? children : <Navigate to="/auth" />;
};

export default PrivateRoute;