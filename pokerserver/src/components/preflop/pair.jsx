import React, { useState } from "react";
import "./pair.css";

function Pair({ card1, card2, type, info, onMouseDown, onMouseEnter, onMouseUp, hoverColor, hoverPercent, colorsByAction }) {
    const [isHovered, setIsHovered] = useState(false);
    const segments = Array.isArray(info)
        ? info.filter(s => (s?.percent || 0) > 0)
        : (info && (info.percent || 0) > 0) ? [info] : [];
    const totalPercent = segments.reduce((a, s) => a + (s.percent || 0), 0);
    const textColor = totalPercent > 50 || isHovered ? "#fff" : "#222";

    const getHoverBg = () => {
        if (!hoverColor) return "#fff";
        if (hoverColor.startsWith("#")) {
            const hex = hoverColor.replace("#", "");
            const bigint = parseInt(hex, 16);
            const r = (bigint >> 16) & 255;
            const g = (bigint >> 8) & 255;
            const b = bigint & 255;
            return `rgba(${r},${g},${b},0.6)`;
        }
        return hoverColor;
    };

    return (
        <button
            className="pair-button"
            style={{
                background: "#fff",
                color: textColor,
                position: "relative",
                overflow: "hidden"
            }}
            onMouseDown={onMouseDown}
            onMouseEnter={() => { setIsHovered(true); onMouseEnter && onMouseEnter(); }}
            onMouseLeave={() => setIsHovered(false)}
            onMouseUp={onMouseUp}
        >
            {segments.length > 0 && (
                <div className="pair-segments" aria-hidden>
                    {(() => {
                        let offset = 0;
                        return segments.map((s, idx) => {
                            const segColor = (colorsByAction && colorsByAction[s.action]) || s.color;
                            const el = (
                                <div
                                    key={idx}
                                    className="pair-segment"
                                    style={{ left: `${offset}%`, width: `${s.percent}%`, background: segColor }}
                                />
                            );
                            offset += s.percent || 0;
                            return el;
                        })
                    })()}
                </div>
            )}
            {isHovered && hoverColor && (hoverPercent ?? 0) > 0 && (
                <div
                    style={{
                        position: "absolute",
                        left: 0,
                        top: 0,
                        height: "100%",
                        width: `${hoverPercent}%`,
                        background: getHoverBg(),
                        borderRadius: 8,
                        opacity: 0.7,
                        pointerEvents: "none",
                        zIndex: 1
                    }}
                />
            )}
            <span style={{ position: "relative", zIndex: 1 }}>
                {card1}{card2}{type[0] || ""}
            </span>
        </button>
    );
}

export default Pair;
