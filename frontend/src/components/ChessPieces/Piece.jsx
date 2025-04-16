// Piece.jsx
import React from "react";
import './ChessPieces.css';

export const Piece = ({ classPiece, colorPiece, position, onDragStart, onClick }) => {
    return (
        <div
            className={`piece ${classPiece} ${colorPiece}`}
            draggable
            onDragStart={(e) => onDragStart(e, position)} // передаем данные о позиции
            onClick={() => onClick(position)} // передаем позицию при клике
        >
        </div>
    );
};