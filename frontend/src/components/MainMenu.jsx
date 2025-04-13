import React from "react";
import "../index.css";

const MainMenu = () => {
    const handleLogout = () => {
        localStorage.removeItem("userToken");
        window.location.href = "/auth";
    };

    const startGame = () => {
        // Здесь можешь добавить переход на игру
        window.location.href = "/game";
    };

    return (
        <div className="main-menu">
            <div className="menu-card">
                <h1>Добро пожаловать в игру</h1>
                <p className="subtitle">Готова ли ты к следующей партии?</p>

                <div className="menu-buttons">
                    <button className="start-btn" onClick={startGame}>
                        ▶ Начать игру
                    </button>
                    <button className="logout-btn" onClick={handleLogout}>
                        Выйти
                    </button>
                </div>
            </div>
        </div>
    );
};

export default MainMenu;