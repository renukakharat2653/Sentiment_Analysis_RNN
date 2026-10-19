
const reviewBox = document.getElementById("review");
const charCount = document.getElementById("charCount");
const historyKey = "sentimentAIHistory";

function updateCharCount() {
  if (reviewBox && charCount) {
    charCount.textContent = `${reviewBox.value.length} / 2000 characters`;
  }
}
if (reviewBox) {
  reviewBox.addEventListener("input", updateCharCount);
  updateCharCount();
}

let historyItems = [];
try {
  historyItems = JSON.parse(sessionStorage.getItem(historyKey) || "[]");
  if (!Array.isArray(historyItems)) historyItems = [];
} catch {
  historyItems = [];
}

function getSentiment(value) {
  const text = String(value || "").toLowerCase();
  if (text.includes("positive") || text.includes("pos")) return "Positive";
  if (text.includes("negative") || text.includes("neg")) return "Negative";
  if (text.includes("neutral")) return "Neutral";
  return "Unknown";
}

function renderDashboard() {
  const counts = { Positive: 0, Negative: 0, Neutral: 0 };
  historyItems.forEach(item => {
    if (Object.hasOwn(counts, item.sentiment)) counts[item.sentiment]++;
  });

  document.getElementById("positiveCount").textContent = counts.Positive;
  document.getElementById("negativeCount").textContent = counts.Negative;
  document.getElementById("neutralCount").textContent = counts.Neutral;
  document.getElementById("totalCount").textContent = historyItems.length;

  document.getElementById("positiveLegend").textContent = counts.Positive;
  document.getElementById("negativeLegend").textContent = counts.Negative;
  document.getElementById("neutralLegend").textContent = counts.Neutral;

  const percent = historyItems.length
    ? Math.round(counts.Positive * 100 / historyItems.length) : 0;
  document.getElementById("positivePercent").textContent =
    historyItems.length ? `${percent}%` : "0%";

  if (window.sentimentChart) {
    window.sentimentChart.data.datasets[0].data = [
      counts.Positive, counts.Negative, counts.Neutral
    ];
    window.sentimentChart.update();
  }

  if (window.activityChart) {
    const recent = historyItems.slice(0, 7).reverse();
    window.activityChart.data.labels = recent.map((_, i) => `Review ${i + 1}`);
    window.activityChart.data.datasets[0].data = recent.map((_, i) => i + 1);
    window.activityChart.update();
  }

  const body = document.getElementById("historyBody");
  body.replaceChildren();

  if (historyItems.length === 0) {
    const row = body.insertRow();
    const cell = row.insertCell();
    cell.colSpan = 3;
    cell.className = "empty";
    cell.textContent = "No reviews analyzed yet. Try the form above.";
    return;
  }

  historyItems.forEach(item => {
    const row = body.insertRow();
    const reviewCell = row.insertCell();
    reviewCell.className = "review-cell";
    reviewCell.textContent = item.review;

    const sentimentCell = row.insertCell();
    const badge = document.createElement("span");
    badge.className = "sentiment-badge " + item.sentiment.toLowerCase();
    badge.textContent = item.sentiment;
    sentimentCell.appendChild(badge);

    row.insertCell().textContent = item.time;
  });
}

if (window.Chart) {
  window.sentimentChart = new Chart(
    document.getElementById("sentimentChart"),
    {
      type: "doughnut",
      data: {
        labels: ["Positive", "Negative", "Neutral"],
        datasets: [{
          data: [0, 0, 0],
          backgroundColor: ["#20bd78", "#ff9b37", "#478aff"],
          borderWidth: 0,
          hoverOffset: 5
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        cutout: "72%",
        plugins: { legend: { display: false } }
      }
    }
  );

  window.activityChart = new Chart(
    document.getElementById("activityChart"),
    {
      type: "line",
      data: {
        labels: [],
        datasets: [{
          label: "Reviews analyzed",
          data: [],
          borderColor: "#7455f5",
          backgroundColor: "rgba(116,85,245,.12)",
          fill: true,
          tension: .35,
          pointRadius: 4,
          pointBackgroundColor: "#7455f5"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { precision: 0 } },
          x: { grid: { display: false } }
        }
      }
    }
  );
}

const clearButton = document.getElementById("clearHistory");
if (clearButton) {
  clearButton.addEventListener("click", () => {
    historyItems = [];
    sessionStorage.removeItem(historyKey);
    renderDashboard();
  });
}

// Flask passes the prediction as a data attribute on the result element.
const result = document.querySelector("[data-prediction]");
if (result) {
  const review = result.dataset.review || "";
  const sentiment = getSentiment(result.dataset.prediction);

  if (review && sentiment !== "Unknown") {
    const alreadySaved = historyItems.some(item =>
      item.review === review && item.sentiment === sentiment
    );

    if (!alreadySaved) {
      historyItems.unshift({
        review,
        sentiment,
        time: new Date().toLocaleTimeString([], {
          hour: "2-digit", minute: "2-digit"
        })
      });
      historyItems = historyItems.slice(0, 30);
      sessionStorage.setItem(historyKey, JSON.stringify(historyItems));
    }
  }
}

renderDashboard();