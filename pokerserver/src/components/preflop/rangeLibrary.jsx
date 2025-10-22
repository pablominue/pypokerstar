import React, { useEffect, useState } from "react";
import { listRanges, loadRange, saveRange, deleteRange } from "../../api/apiRange";
import CardRange from "./range";
import "./rangeLibrary.css";

export default function RangeLibraryMenu({ onLoadRange, currentRange }) {
    const [index, setIndex] = useState({});
    const [player, setPlayer] = useState("default");
    const [category, setCategory] = useState("Ranges");
    const [position, setPosition] = useState("UTG");
    const [name, setName] = useState("");

    useEffect(() => setIndex(listRanges()), []);

    const handleSave = () => {
        const cr = currentRange instanceof CardRange ? currentRange : CardRange.fromObject(currentRange);
        if (!cr) return;
        const n = name || `range-${new Date().toISOString().replace(/[:.]/g,'-')}`;
        saveRange({ cardRange: cr, player, category, name: n });
        setIndex(listRanges());
        setName("");
    };

    const handleLoad = (n) => {
        const cr = loadRange({ player, category, position, name: n });
        if (cr && typeof onLoadRange === "function") onLoadRange(cr);
    };

    const playerCategories = index[player] || {};
    const positions = playerCategories[category] || {};
    const names = positions[position] || [];

    return (
        <div className="range-library-menu">
            <div style={{ marginBottom: 8 }}>
                <input value={player} onChange={e => setPlayer(e.target.value)} placeholder="Player" />
                <input value={category} onChange={e => setCategory(e.target.value)} placeholder="Folder" />
                <input value={position} onChange={e => setPosition(e.target.value)} placeholder="Position" />
            </div>
            <div style={{ marginBottom: 8 }}>
                <input value={name} onChange={e => setName(e.target.value)} placeholder="Save as (name)" />
                <button onClick={handleSave}>Save current</button>
            </div>
            <div>
                <strong>Saved ranges for {player} / {category} / {position}</strong>
                <ul>
                    {names.map(n => (
                        <li key={n}>
                            {n}
                            <button onClick={() => handleLoad(n)} style={{ marginLeft: 8 }}>Load</button>
                            <button onClick={() => { deleteRange({ player, category, position, name: n }); setIndex(listRanges()); }} style={{ marginLeft: 6 }}>Delete</button>
                        </li>
                    ))}
                    {names.length === 0 && <li><em>No ranges</em></li>}
                </ul>
            </div>
        </div>
    );
}