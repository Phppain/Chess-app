import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

const Login = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError("");
        setSuccess("");

        if (!username || !password) {
            setError("Заполните все поля");
            return;
        }

        try {
            const res = await fetch("http://localhost:8000/api/User/login/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email: username, password })
            });

            const data = await res.json();

            if (!res.ok) {
                setError(data.error || "Неверные данные");
            } else {
                setSuccess("Успешный вход!");
                localStorage.setItem("userToken", JSON.stringify(data.user));
                
                navigate("/");
            }
        } catch (err) {
            setError("Ошибка сервера");
        }
    };

    return (
        <div className="login-container">
            <form className="login-form" onSubmit={handleLogin}>
                <h2>Вход</h2>
                {error && <div className="error">{error}</div>}
                {success && <div className="success">{success}</div>}

                <label>Email</label>
                <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />

                <label>Пароль</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />

                <button type="submit">Войти</button>
            </form>
        </div>
    );
};

export default Login;