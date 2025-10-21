import React from "react";
import "./rangeMenu.css";

function RangeMenu({ menuState, setMenuState, colorHistory = [], setColorHistory, colorsByAction, onSetActionColor }) {
    const { action, percent } = menuState;
    const defaultColors = { raise: '#007bff', call: '#28a745', '3bet': '#ffc107', allin: '#dc3545' };
    const colorsMap = { ...defaultColors, ...(colorsByAction || {}) };
    const pushHistory = (hex) => {
        if (!setColorHistory) return;
        const c = typeof hex === 'string' ? hex.toLowerCase() : hex;
        setColorHistory(prev => {
            const arr = [c, ...prev.filter(x => x.toLowerCase() !== c)];
            return arr.slice(0, 12);
        });
    };
    const setActionColor = (act, color) => {
        if (onSetActionColor) onSetActionColor(act, color);
        pushHistory(color);
    };

    return (
        <div className="range-menu">
            <h3>Action</h3>
            <div className="action-list">
                {['raise','call','3bet','allin','fold'].map(a => (
                    <div key={a} className={`action-row ${a === action ? 'active' : ''}`}>
                        {a !== 'fold' ? (
                            <input
                                type="color"
                                className="action-color"
                                value={colorsMap[a]}
                                onChange={e => setActionColor(a, e.target.value)}
                                aria-label={`${a} color`}
                            />
                        ) : (
                            <div className="action-color disabled" />
                        )}
                        <button
                            type="button"
                            className="action-name"
                            onClick={() => setMenuState(ms => ({ ...ms, action: a }))}
                        >
                            {a === '3bet' ? '3Bet' : a.charAt(0).toUpperCase() + a.slice(1)}
                        </button>
                    </div>
                ))}
            </div>

            <h3>Percent</h3>
            <div className="percent-row">
                <input
                    type="range"
                    min={0}
                    max={100}
                    step={1}
                    value={Number.isFinite(percent) ? percent : 0}
                    onChange={e => setMenuState(ms => ({ ...ms, percent: Number(e.target.value) }))}
                    onDoubleClick={() => setMenuState(ms => ({ ...ms, percent: 100 }))}
                    aria-label="Percent slider"
                />
                <input
                    type="number"
                    min={0}
                    max={100}
                    step={1}
                    value={Number.isFinite(percent) ? percent : 0}
                    onChange={e => {
                        const raw = e.target.value
                        const num = Number(raw)
                        const safe = Number.isFinite(num) ? Math.min(100, Math.max(0, num)) : 0
                        setMenuState(ms => ({ ...ms, percent: safe }))
                    }}
                    onBlur={e => {
                        const num = Number(e.target.value)
                        const safe = Number.isFinite(num) ? Math.min(100, Math.max(0, num)) : 0
                        setMenuState(ms => ({ ...ms, percent: safe }))
                    }}
                    aria-label="Percent input"
                />
            </div>
            <div className="preset-row">
                {[100, 75, 50, 25, 0].map(p => (
                    <button
                        key={p}
                        className={`preset-btn ${p === percent ? 'active' : ''}`}
                        onClick={() => setMenuState(ms => ({ ...ms, percent: p }))}
                    >{p}%</button>
                ))}
            </div>
            {setColorHistory && colorHistory && colorHistory.length > 0 && (
                <div>
                    <h3>Recent Colors</h3>
                    <div className="history-row">
                        {colorHistory.map(c => (
                            <button
                                key={c}
                                className="history-swatch"
                                style={{ background: c }}
                                title={c}
                                onClick={() => action !== 'fold' && setActionColor(action, c)}
                                aria-label={`Use color ${c}`}
                            />)
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}

export default RangeMenu;
