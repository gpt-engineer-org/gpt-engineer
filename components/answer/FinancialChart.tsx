// FinancialChart.jsx
import React, { useEffect, useRef, memo } from 'react';

const styles = {
  container: {
    height: "400px",
    width: "100%",
    maxHeight: "400px",
    minHeight: "400px",
    "@media (maxWidth: 768px)": {
      height: "150px",
      maxHeight: "150px",
      minHeight: "150px",
    },
  },
};

function FinancialChart({ ticker }: { ticker: string }) {
  const container = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.type = "text/javascript";
    script.async = true;
    script.innerHTML = `
      {
        "autosize": true,
        "symbol": "${ticker}",
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": "light",
        "style": "2",
        "locale": "en",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "calendar": false,
        "support_host": "https://www.tradingview.com",
        "container_id": "${container.current?.id}"
      }
    `;

    if (container.current) {
      container.current.appendChild(script);
    }

    return () => {
      if (container.current) {
        container.current.innerHTML = "";
      }
    };
  }, []);

  return (
    <div className="my-5 tradingview-widget-container" ref={container} style={styles.container}>
      <div className="tradingview-widget-copyright">
        <a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank">
          <span className="blue-text">Track all markets on TradingView</span>
        </a>
      </div>
    </div>
  );
}

export default memo(FinancialChart);