import "./ChessBoard.css"
import { Piece } from "../ChessPieces/Piece";
import React, { useEffect, useState, useCallback, useRef } from "react";

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
                // console.log('DATA:', data.pieces);
                
                socketRef.current = new WebSocket(`ws://localhost:8000/ws/chess/${data.game.id}/`);

                socketRef.current.onopen = () => {
                    console.log("WebSocket connected!");
                };

                socketRef.current.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        console.log('DATA main:', data);
                
                        if (data.pieces) {
                            let normalized = {};
                            
                            data.pieces.forEach((p) => {
                                const key = `(${p.position[0]}, ${p.position[1]})`;
                                normalized[key] = p;
                            });
                            setPieces(normalized);
                            console.log("DATA (object):", normalized);
                        }
                
                        if (data.moves) {
                            console.log("DATA:",data);
                            
                            setPossibleMoves(data.possible_moves);
                        }
                
                        if (data.type === "move_result") {
                            const { from, to } = data;
                            const newPieces = { ...pieces };
                            const movedPiece = newPieces[from];
                            delete newPieces[from];
                            newPieces[to] = movedPiece;
                            setPieces(newPieces);
                        }
                
                        if (data.type === "possible_moves") {
                            setPossibleMoves(data.moves);
                        }
                
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
            })
            .catch((err) => console.error("Error initializing game:", err));
    
            
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
                    board: pieces
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
            
            // console.log(pieces);
            

            return (
                <div
                    key={positionKey}
                    id={`square-${row}-${col}`}
                    style={{
                        backgroundColor: possibleMoves.some(
                            ([r, c]) => `(${r}, ${c})` === positionKey
                        )
                            ? "#baca44"
                            : isBlack
                            ? "#769656"
                            : "#eeeed2",
                        border:
                            positionKey === selectedPiece
                                ? "2px solid gold"
                                : "1px solid transparent",
                        display: "flex",
                    }}
                    onDrop={(e) => handleDrop(e, row, col)}
                    onDragOver={handleDragOver}
                >
                    {piece && piece['type'] != null && (
                        <Piece
                            classPiece={piece['type'].toLowerCase()}
                            colorPiece={piece['color']}
                            position={piece['position']}
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
                <div id="ChessBoard">
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