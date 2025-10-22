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
  CrossHairCursor,
  Cursor,
  MouseCoordinateX,
  MouseCoordinateY,
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
    const lost = Math.random() < 0.6 ? Math.round(Math.random() * 6) : 0;
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
  const posOpacity = Math.min(0.9, (maxPositive / maxAbs) * 0.9 + 0.1);
  const negOpacity = Math.min(0.9, (maxNegative / maxAbs) * 0.9 + 0.1);

  // colors (use toFixed(2) to produce valid rgba alpha)
  const green = `rgba(16,185,129,${posOpacity.toFixed(2)})`; // emerald
  const red = `rgba(239,68,68,${negOpacity.toFixed(2)})`; // rose

  // scale provider
  const xScaleProvider = discontinuousTimeScaleProvider.inputDateAccessor((d) => d.date);
  const { data, xScale, xAccessor, displayXAccessor } = xScaleProvider(dataRaw);

  const start = xAccessor(data[Math.max(0, data.length - 120)]);
  const end = xAccessor(data[data.length - 1]);
  const xExtents = [start, end];

  return (
    <div style={{ alignContent: "center", display: "flex", flexDirection: "column", marginTop: 16, marginBottom: 32, alignItems: "center" }}>
      <h2 style={{ margin: "8px 0 16px", fontFamily: "Inter, Roboto, Arial", color: "#0f172a" }}>
        Profit & Loss over time
      </h2>

      <div style={{
        background: " #f5f6fa",
        borderRadius: 12,
        padding: 12,
        color: "white",
        border: "1px solid #e2e8f0",
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
          <Chart id={1} yExtents={(d) => [d.cumulative, 0]}>
            <XAxis
              showGridLines
              stroke="#0f172a"
              tickStroke="#94a3b8"
              tickLabelFill="#283f5fff"
              showTicks={true}
              opacity={0.9}
              tickFormat={(d) => {
                try {
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
              tickLabelFill="#283f5fff"
              showTicks={true}
              opacity={0.9}
            />

            <LineSeries yAccessor={(d) => 0} strokeStyle = "#000000ff" strokeWidth={1} />
            <LineSeries yAccessor={(d) => d.cumulative} strokeStyle = "#888888ff" strokeWidth={2} />
            <Cursor />

          </Chart>
        <CrossHairCursor />
        </ChartCanvas>
      </div>
    </div>
  );
}

export default Statistics;