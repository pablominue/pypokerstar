import React from "react";
import './screen.css';
import Grid from '@mui/material/Grid';

export default function Screen({ children }) {
  return (
    <Grid 
      container spacing={1} className="screen-grid"
      sx={{
        justifyContent: "center",
        alignItems: "center",
      }}>
      <div className="sepparator"></div>
      <Grid item xs={12} className="screen-content"
      >
        {children}
      </Grid>
    </Grid>
  );
}