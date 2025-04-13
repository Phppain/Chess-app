import React, { useState } from "react";
import Login from "./Login/Login";
import Register from "./Reg/Reg";

const AuthWrapper = () => {
    const [isLogin, setIsLogin] = useState(true);

    return (
        <div>
            {isLogin ? <Login /> : <Register />}

            <div style={{ textAlign: "center", marginTop: "20px" }}>
                {isLogin ? (
                    <>
                        <span>Нет аккаунта? </span>
                        <button
                            onClick={() => setIsLogin(false)}
                            style={linkStyle}
                        >
                            Зарегистрироваться
                        </button>
                    </>
                ) : (
                    <>
                        <span>Уже есть аккаунт? </span>
                        <button
                            onClick={() => setIsLogin(true)}
                            style={linkStyle}
                        >
                            Войти
                        </button>
                    </>
                )}
            </div>
        </div>
    );
};

const linkStyle = {
    background: "none",
    border: "none",
    color: "#00aaff",
    cursor: "pointer",
    textDecoration: "underline",
    fontSize: "14px",
    padding: "0"
};

export default AuthWrapper;