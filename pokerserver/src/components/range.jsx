import React, { useState, useEffect, useRef } from "react";
import Pair from "./pair";
import RangeMenu from "./rangeMenu";
import "./range.css";

const cards = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"];
const TOTAL_COMBOS = 1326;

function Range({ initialRange = {}, onRangeChange, menuState: controlledMenuState, setMenuState: setControlledMenuState, menuCollapsed: collapsedProp, setMenuCollapsed: setCollapsedProp, colorHistory, setColorHistory, colorsByAction: externalColorsByAction, setActionColor }) {
    const [pairActions, setPairActions] = useState(initialRange || {});
    const isControlledMenu = controlledMenuState && typeof setControlledMenuState === 'function';
    const [internalMenuState, setInternalMenuState] = useState({ color: "#007bff", action: "raise", percent: 100 });
    const menuState = isControlledMenu ? controlledMenuState : internalMenuState;
    const setMenuState = isControlledMenu ? setControlledMenuState : setInternalMenuState;
    const [dragging, setDragging] = useState(false);
    const [internalCollapsed, setInternalCollapsed] = useState(false);
    const collapsed = typeof setCollapsedProp === 'function' ? !!collapsedProp : internalCollapsed;
    const setCollapsed = typeof setCollapsedProp === 'function' ? setCollapsedProp : setInternalCollapsed;

    // Historial robusto con useRef para evitar problemas de asincronía
    const historyRef = useRef([]);
    const [_, forceRerender] = useState(0); // Para forzar render tras deshacer

    // Initialize from props on mount (component remounts when selection changes)
    useEffect(() => {
        setPairActions(initialRange || {});
        historyRef.current = [];
    }, []);

    // Keyboard shortcuts for quick actions/percents
    useEffect(() => {
        const handler = (e) => {
            const tag = document.activeElement && document.activeElement.tagName
            if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || e.isComposing) return
            const k = e.key.toLowerCase()
            if (k === 'r') setMenuState(ms => ({ ...ms, action: 'raise' }))
            else if (k === 'c') setMenuState(ms => ({ ...ms, action: 'call' }))
            else if (k === 'f') setMenuState(ms => ({ ...ms, action: 'fold' }))
            else if (k === 'b' || k === '3') setMenuState(ms => ({ ...ms, action: '3bet' }))
            else if (k === 'a') setMenuState(ms => ({ ...ms, action: 'allin' }))
            else if (k === '1') setMenuState(ms => ({ ...ms, percent: 100 }))
            else if (k === '7') setMenuState(ms => ({ ...ms, percent: 75 }))
            else if (k === '5') setMenuState(ms => ({ ...ms, percent: 50 }))
            else if (k === '2') setMenuState(ms => ({ ...ms, percent: 25 }))
            else if (k === '0') setMenuState(ms => ({ ...ms, percent: 0 }))
        }
        window.addEventListener('keydown', handler)
        return () => window.removeEventListener('keydown', handler)
    }, [])
    
    useEffect(() => {
        if (onRangeChange) onRangeChange(pairActions);
    }, [pairActions]);

    const assignToPair = (key) => {
        setPairActions(prev => {
            const applying = {
                action: menuState.action,
                color: (externalColorsByAction && externalColorsByAction[menuState.action]) || menuState.color || '#007bff',
                percent: Number(menuState.percent) || 0
            };
            const curr = prev[key];
            const prevSegments = Array.isArray(curr)
                ? curr
                : curr && curr.percent > 0
                    ? [curr]
                    : [];

            // If applying 0%, remove that action segment
            let segments = prevSegments.filter(s => s.action !== applying.action);

            if (applying.percent > 0) {
                // Insert/replace target segment with desired percent and color
                segments.push({ action: applying.action, color: applying.color, percent: applying.percent });

                // Normalize to max 100% by scaling non-target segments if needed
                const target = { action: applying.action };
                const totalOthers = segments
                    .filter(s => s.action !== target.action)
                    .reduce((a, b) => a + (b.percent || 0), 0);
                const available = Math.max(0, 100 - applying.percent);
                if (totalOthers > available) {
                    const scale = available / totalOthers;
                    segments = segments.map(s => s.action === target.action ? s : { ...s, percent: Math.max(0, Math.round(s.percent * scale)) });
                }
            }

            // Clean zero/negative and cap rounding drift
            let total = segments.reduce((a, b) => a + (b.percent || 0), 0);
            if (total > 100) {
                // Reduce others proportionally
                const scale = 100 / total;
                segments = segments.map(s => ({ ...s, percent: Math.max(0, Math.round(s.percent * scale)) }));
                total = 100;
            }

            // Early exit if no change
            const same = JSON.stringify(prevSegments) === JSON.stringify(segments);
            if (same) return prev;

            // Save history and update
            historyRef.current = [...historyRef.current, JSON.parse(JSON.stringify(prev))];
            return { ...prev, [key]: segments };
        });
    };

    const clearRange = () => {
        setPairActions(prev => {
            historyRef.current = [...historyRef.current, JSON.parse(JSON.stringify(prev))];
            return {};
        });
    };

    const undoLast = () => {
        if (historyRef.current.length > 0) {
            const last = historyRef.current[historyRef.current.length - 1];
            setPairActions(last);
            historyRef.current = historyRef.current.slice(0, -1);
            forceRerender(n => n + 1); // Forzar render para actualizar el botón
        }
    };

    const handleMouseDown = (key) => {
        setDragging(true);
        assignToPair(key);
    };
    const handleMouseEnter = (key) => {
        if (dragging) assignToPair(key);
    };
    const handleMouseUp = () => setDragging(false);

    // Calcular % de manos seleccionadas (Raise + Call)
    const getCombos = (type) => {
        if (type === "") return 6; // Pareja
        if (type === "s") return 4; // Suited
        if (type === "o") return 12; // Offsuit
        return 0;
    };

    let selectedCombos = 0;
    const ACTION_KEYS = ["raise", "call", "3bet", "allin"];
    const defaultColors = { raise: "#007bff", call: "#28a745", "3bet": "#ffc107", allin: "#dc3545" };
    const ACTION_COLORS = { ...defaultColors, ...(externalColorsByAction || {}) };
    const combosByAction = { raise: 0, call: 0, "3bet": 0, allin: 0 };
    cards.forEach((card1, i) => {
        cards.forEach((card2, j) => {
            let type = "";
            let key = "";
            if (i === j) {
                type = "";
                key = `${card1}${card2}`;
            } else if (i < j) {
                type = "s";
                key = `${card1}${card2}${type}`;
            } else {
                type = "o";
                key = `${card2}${card1}${type}`;
            }
            const info = pairActions[key];
            const combos = getCombos(type);
            if (Array.isArray(info)) {
                info.forEach(seg => {
                    if (!seg || !seg.action || seg.action === 'fold') return;
                    const frac = (seg.percent || 0) / 100;
                    if (frac > 0) {
                        selectedCombos += combos * frac;
                        if (combosByAction[seg.action] !== undefined) combosByAction[seg.action] += combos * frac;
                    }
                })
            } else if (info && info.action && info.action !== 'fold') {
                const frac = (info.percent || 0) / 100;
                if (frac > 0) {
                    selectedCombos += combos * frac;
                    if (combosByAction[info.action] !== undefined) combosByAction[info.action] += combos * frac;
                }
            }
        });
    });
    const selectedPercent = ((selectedCombos / TOTAL_COMBOS) * 100).toFixed(1);
    const legendItems = ACTION_KEYS.map(a => ({ action: a, color: ACTION_COLORS[a], percent: ((combosByAction[a] / TOTAL_COMBOS) * 100).toFixed(1) }));

    return (
        <div className="range-layout">
            <div className="range-toolbar" style={{ display: "flex", gap: "10px", marginBottom: "10px" }}>
                <button className="undo-btn" onClick={undoLast} disabled={historyRef.current.length === 0}>Undo</button>
                <button className="clear-btn" onClick={clearRange}>Clear</button>
            </div>
            <div className="range-grid">
                {cards.map((card1, i) => (
                    <div className="range-row" key={card1}>
                        {cards.map((card2, j) => {
                            let type = "";
                            let key = "";
                            if (i === j) {
                                type = "";
                                key = `${card1}${card2}`;
                            } else if (i < j) {
                                type = "s";
                                key = `${card1}${card2}${type}`;
                            } else {
                                type = "o";
                                key = `${card2}${card1}${type}`;
                            }
                            const info = pairActions[key] || [];
                            return (
                                <Pair
                                    key={key}
                                    card1={i < j ? card1 : card2}
                                    card2={i < j ? card2 : card1}
                                    type={type}
                                    info={info}
                                    onMouseDown={() => handleMouseDown(key)}
                                    onMouseEnter={() => handleMouseEnter(key)}
                                    onMouseUp={handleMouseUp}
                                    hoverColor={ACTION_COLORS[menuState.action] || '#007bff'}
                                    hoverPercent={menuState.percent}
                                    colorsByAction={ACTION_COLORS}
                                />
                            );
                        })}
                    </div>
                ))}
            </div>
            <div className="range-legend" style={{ marginTop: 16 }}>
                {legendItems.map(({ action, color, percent }) => (
                    <div key={action} className="legend-item">
                        <span className="legend-swatch" style={{ background: color }} />
                        <span className="legend-text" style={{ fontWeight: 600 }}>
                            {action.charAt(0).toUpperCase() + action.slice(1)}: {percent}%
                        </span>
                    </div>
                ))}
            </div>
            <div className={`range-menu-wrapper ${collapsed ? "collapsed" : ""}`}>
                <button
                    className="toggle-handle"
                    aria-label={collapsed ? "Open menu" : "Close menu"}
                    onClick={() => setCollapsed(c => !c)}
                >
                    {collapsed ? "⟨" : "⟩"}
                </button>
                <RangeMenu
                    menuState={menuState}
                    setMenuState={setMenuState}
                    colorHistory={colorHistory}
                    setColorHistory={setColorHistory}
                    colorsByAction={ACTION_COLORS}
                    onSetActionColor={setActionColor}
                />
            </div>
        </div>
    );
}

export default Range;
