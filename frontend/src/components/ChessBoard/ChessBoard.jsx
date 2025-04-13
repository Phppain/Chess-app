import React, { useEffect, useState, useCallback, useRef } from "react";
import { Piece } from "../ChessPieces/Piece";

export const ChessBoard = () => {
    const [pieces, setPieces] = useState({});
    const [gameData, setGameData] = useState(null);
    const [possibleMoves, setPossibleMoves] = useState([]);
    const [selectedPiece, setSelectedPiece] = useState(null);
    const [timer, setTimer] = useState(600); // 10 минут
    const socketRef = useRef(null);
    const initializedRef = useRef(false);

    // Таймер
    useEffect(() => {
        const interval = setInterval(() => {
            setTimer((prev) => (prev > 0 ? prev - 1 : 0));
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    const formatTime = (seconds) => {
        const min = Math.floor(seconds / 60)
            .toString()
            .padStart(2, "0");
        const sec = (seconds % 60).toString().padStart(2, "0");
        return `${min}:${sec}`;
    };

    useEffect(() => {
        if (initializedRef.current) return;
        initializedRef.current = true;

        fetch("http://localhost:8000/api/Game/start_new/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                player_white: 1,
                player_black: 2,
                result: "in_progress",
            }),
        })
            .then((res) => res.json())
            .then((data) => {
                console.log("Game initialized:", data);
                setGameData(data.game);
                setPieces(data.pieces || {});
            })
            .catch((err) => console.error("Error initializing game:", err));

        socketRef.current = new WebSocket("ws://localhost:8000/ws/chess/");

        socketRef.current.onopen = () => {
            console.log("WebSocket connected!");
        };

        socketRef.current.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.pieces) setPieces(data.pieces);
                if (data.possible_moves) setPossibleMoves(data.possible_moves);
            } catch (err) {
                console.error("WebSocket message error:", err);
            }
        };

        socketRef.current.onerror = (err) => {
            console.error("WebSocket error:", err);
        };

        socketRef.current.onclose = (event) => {
            console.log("WebSocket closed:", event);
        };

        return () => socketRef.current?.close();
    }, []);

    const handleDragStart = (e, position) => {
        e.dataTransfer.setData("position", position);
    };

    const handleDrop = (e, row, col) => {
        e.preventDefault();
        const fromPosition = e.dataTransfer.getData("position");
        const movingPiece = pieces[fromPosition];
        if (!movingPiece) return;

        const newPosition = `(${row}, ${col})`;
        const newPieces = { ...pieces };
        delete newPieces[fromPosition];
        newPieces[newPosition] = { ...movingPiece, position: [row, col] };
        setPieces(newPieces);
        setPossibleMoves([]);
        setSelectedPiece(null);

        if (socketRef.current) {
            socketRef.current.send(
                JSON.stringify({
                    type: "move_piece",
                    from: fromPosition,
                    to: newPosition,
                })
            );
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    const handlePieceClick = (pos) => {
        setSelectedPiece(pos);
        if (socketRef.current) {
            socketRef.current.send(
                JSON.stringify({
                    type: "get_possible_moves",
                    from: pos,
                })
            );
        }
    };

    const renderSquare = useCallback(
        (row, col) => {
            const isBlack = (row + col) % 2 === 1;
            const positionKey = `(${row}, ${col})`;
            const piece = pieces[positionKey];
            const isMoveTarget = possibleMoves.includes(positionKey);

            return (
                <div
                    key={`${row}-${col}`}
                    style={{
                        width: 64,
                        height: 64,
                        backgroundColor: isMoveTarget
                            ? "#baca44"
                            : isBlack
                            ? "#769656"
                            : "#eeeed2",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        border:
                            positionKey === selectedPiece
                                ? "2px solid gold"
                                : "1px solid transparent",
                    }}
                    onDrop={(e) => handleDrop(e, row, col)}
                    onDragOver={handleDragOver}
                >
                    {piece && (
                        <Piece
                            classPiece={piece.type.toLowerCase()}
                            colorPiece={piece.color}
                            position={piece.position}
                            onDragStart={(e) => handleDragStart(e, positionKey)}
                            onClick={() => handlePieceClick(positionKey)}
                        />
                    )}
                </div>
            );
        },
        [pieces, possibleMoves, selectedPiece]
    );

    if (!gameData) return <div>Loading...</div>;

    return (
        <div style={{ display: "flex", gap: "40px", padding: "30px" }}>
            <div>
                <h3 style={{ marginBottom: 10 }}>Game ID: {gameData.id}</h3>
                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(8, 64px)",
                        gridTemplateRows: "repeat(8, 64px)",
                        border: "2px solid #444",
                    }}
                    id="ChessBoard"
                >
                    {Array.from({ length: 8 }, (_, row) =>
                        Array.from({ length: 8 }, (_, col) =>
                            renderSquare(7 - row, col) // переворачиваем доску
                        )
                    )}
                </div>
            </div>

            <div style={{ minWidth: 200 }}>
                <h3>Игроки</h3>
                <div style={{ marginBottom: 20 }}>
                    <strong>Белые:</strong> {gameData.player_white_name || "Игрок 1"}
                    <br />
                    <small>Ранг: {gameData.white_rank || 1200}</small>
                </div>
                <div>
                    <strong>Чёрные:</strong> {gameData.player_black_name || "Игрок 2"}
                    <br />
                    <small>Ранг: {gameData.black_rank || 1200}</small>
                </div>

                <h3 style={{ marginTop: 30 }}>Таймер</h3>
                <div
                    style={{
                        fontSize: "24px",
                        fontWeight: "bold",
                        marginTop: 10,
                        color: timer < 30 ? "#e74c3c" : "#2ecc71",
                    }}
                >
                    {formatTime(timer)}
                </div>
            </div>
        </div>
    );
};