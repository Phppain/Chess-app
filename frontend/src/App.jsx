import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AuthWrapper from "./components/Auth/AuthWrapper";
import MainMenu from "./components/MainMenu";
import PrivateRoute from "./routes/PrivateRoute";
import { ChessBoard } from "./components/ChessBoard/ChessBoard";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/auth" element={<AuthWrapper />} />
                <Route
                    path="/"
                    element={
                        <PrivateRoute>
                            <MainMenu />
                        </PrivateRoute>
                    }
                />
                <Route path="/game" element={<ChessBoard />}/>
            </Routes>
        </Router>
    );
}

export default App;