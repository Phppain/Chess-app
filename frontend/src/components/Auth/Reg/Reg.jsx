import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Reg.css";

const Register = () => {
    const [nickname, setNickName] = useState("");
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setSuccess("");
    
        if (!nickname || !email || !password || !firstName || !lastName) {
            setError("Пожалуйста, заполните все поля");
            return;
        }
    
        try {
            const res = await fetch("http://localhost:8000/api/User/register/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ nickname, firstName, lastName, email, password })
            });
    
            const data = await res.json();
    
            if (!res.ok) {
                setError(data.detail || "Ошибка регистрации");
            } else {
                setSuccess("Успешно зарегистрирован!");
                setNickName("");
                setFirstName("");
                setLastName("");
                setEmail("");
                setPassword("");
                localStorage.setItem("userToken", JSON.stringify(data.user));
    
                setTimeout(() => {
                    navigate("/");
                }, 1500);
            }
        } catch (err) {
            setError("Ошибка сервера");
        }
    };

    return (
        <div className="register-container">
            <form className="register-form" onSubmit={handleSubmit}>
                <h2>Регистрация</h2>

                {error && <div className="error">{error}</div>}
                {success && <div className="success">{success}</div>}

                <label>Имя пользователя</label>
                <input
                    type="text"
                    value={nickname}
                    onChange={(e) => setNickName(e.target.value)}
                />
                <label>Имя</label>
                <input
                    type="text"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                />
                <label>Фамилия</label>
                <input
                    type="text"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                />

                <label>Email</label>
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />

                <label>Пароль</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />

                <button type="submit">Зарегистрироваться</button>
            </form>
        </div>
    );
};

export default Register;