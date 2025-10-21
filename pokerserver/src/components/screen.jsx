import React from "react";
import './screen.css';
export default function Screen({ children }) {
  return (
    <div className="screen">
      {children}
    </div>
  );
}