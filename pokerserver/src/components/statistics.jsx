import React from "react";
import {
  ChartCanvas,
  Chart,
  discontinuousTimeScaleProvider,
  LineSeries,
  AreaSeries,
  XAxis,
  YAxis,
  withDeviceRatio,
  MouseCoordinateX,
  MouseCoordinateY,
  CrossHairCursor,
  HoverTooltip, 
} from "react-financial-charts";

/*
  Profit / Loss over time demo.

  Input mock structure:
  { hands: [ { id: 123456, earned: 12, lost: 0 }, ... ] }

  We compute per-hand net = earned - lost and cumulative P/L over time,
  then render a single chart with:
    - Positive area (green) above zero
    - Negative area (red) below zero
    - Line for cumulative P/L
  Visual strength (opacity) is scaled by the maximum absolute value in the series.
*/

function genMockHands(n = 120) {
  const hands = [];
  let baseDate = new Date();
  baseDate.setHours(0, 0, 0, 0);
  for (let i = 0; i < n; i++) {
    // make some realistic-ish P/L swings
    const won = Math.random() < 0.6 ? Math.round(Math.random() * 6) : 0;
    const lost = Math.random() < 0.4 ? Math.round(Math.random() * 6) : 0;
    hands.push({
      id: 100000 + i,
      earned: won,
      lost: lost,
      date: new Date(baseDate.getTime() + i * 60 * 60 * 1000), // hourly steps
    });
  }
  return { hands };
}

function prepareSeries(input) {
  const rows = [];
  let cum = 0;
  for (const h of input.hands) {
    const net = (h.earned || 0) - (h.lost || 0);
    cum += net;
    rows.push({
      date: h.date instanceof Date ? h.date : new Date(h.date),
      id: h.id,
      net,
      cumulative: cum,
    });
  }
  return rows;
}

function Statistics({ width = 1000, ratio = window.devicePixelRatio || 1 }) {
  const mock = React.useMemo(() => genMockHands(240), []);
  const dataRaw = React.useMemo(() => prepareSeries(mock), [mock]);

  // guard: need at least 2 points
  if (!dataRaw || dataRaw.length < 2) {
    return <div>No data</div>;
  }

  const maxAbs = Math.max(...dataRaw.map((d) => Math.abs(d.cumulative)), 1);
  const maxPositive = Math.max(...dataRaw.map((d) => (d.cumulative > 0 ? d.cumulative : 0)), 0);
  const maxNegative = Math.max(...dataRaw.map((d) => (d.cumulative < 0 ? Math.abs(d.cumulative) : 0)), 0);

  // scale opacities so that stronger swings get stronger color
  const posOpacity = Math.min(0.9, maxPositive / maxAbs * 0.9 + 0.1);
  const negOpacity = Math.min(0.9, maxNegative / maxAbs * 0.9 + 0.1);

  // colors
  const green = `rgba(16,185,129,${posOpacity.toFixed(2)})`; // emerald
  const red = `rgba(239,68,68,${negOpacity.toFixed(2)})`; // rose

  // scale provider
  const xScaleProvider = discontinuousTimeScaleProvider.inputDateAccessor((d) => d.date);
  const { data, xScale, xAccessor, displayXAccessor } = xScaleProvider(dataRaw);

  const start = xAccessor(data[Math.max(0, data.length - 120)]);
  const end = xAccessor(data[data.length - 1]);
  const xExtents = [start, end];

  return (
    <div>
      <h2 style={{ margin: "8px 0 16px", fontFamily: "Inter, Roboto, Arial", color: "#0f172a" }}>
        Profit / Loss over time
      </h2>

      <div style={{
        background: "#0b1220",
        borderRadius: 12,
        padding: 12,
        color: "white",
      }}>

        <ChartCanvas
          height={500}
          width={width}
          ratio={ratio}
          margin={{ left: 70, right: 30, top: 12, bottom: 30 }}
          seriesName="PL"
          data={data}
          xAccessor={xAccessor}
          displayXAccessor={displayXAccessor}
          xScale={xScale}
          xExtents={xExtents}
        >
          <Chart id={1} yExtents={(d) => [d.cumulative]}>
            {/* axis styling: make ticks/labels visible against dark background */}
            <XAxis
              showGridLines
              stroke="#0f172a"
              tickStroke="#94a3b8"
              tickLabelFill="#94a3b8"
              showTicks={true}
              opacity={0.9}
              tickFormat={(d) => {
                try {
                  // show only day number for tight spacing; change as needed
                  return d instanceof Date ? d.getDate() : d.toString();
                } catch {
                  return String(d);
                }
              }}
            />
            <YAxis
              showGridLines
              stroke="#0f172a"
              tickStroke="#94a3b8"
              tickLabelFill="#94a3b8"
              showTicks={true}
              opacity={0.9}
            />
             {/* positive area */}
             <AreaSeries
               yAccessor={(d) => (d.cumulative > 0 ? d.cumulative : 0)}
               stroke={() => green}
               fillStyle={() => green}
             />
             {/* negative area */}
             <AreaSeries
               yAccessor={(d) => (d.cumulative < 0 ? d.cumulative : 0)}
               stroke={() => red}
               fillStyle={() => red}
             />
             {/* cumulative line */}
            <LineSeries yAccessor={(d) => d.cumulative} fillStyle="#60a5fa" strokeWidth={2} />

            <MouseCoordinateX displayFormat={(d) => {
              try { return d instanceof Date ? d.toLocaleString() : String(d); }
              catch { return String(d); }
            }} />
            <MouseCoordinateY displayFormat={(y) => `${Number(y).toFixed(2)}€`} />

          <HoverTooltip
            origin={[10, -40]}
            tooltipContent={({ currentItem, xAccessor }) => {
              if (!currentItem) return null;
              return {
                x: xAccessor(currentItem) instanceof Date ? xAccessor(currentItem).toLocaleString() : String(xAccessor(currentItem)),
                y: `${Number(currentItem.cumulative).toFixed(2)}€`,
                items: [
                  { label: "Cumulative", value: `${Number(currentItem.cumulative).toFixed(2)}€`, stroke: "#60a5fa" },
                  { label: "Net", value: `${Number(currentItem.net).toFixed(2)}€` },
                ],
              };
            }}
          />
             <CrossHairCursor />
           </Chart>
         </ChartCanvas>
       </div>
     </div>
   );
 }
 
 export default Statistics;