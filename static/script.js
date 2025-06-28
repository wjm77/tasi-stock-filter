async function fetchData() {
    const response = await fetch('/filter');
    const data = await response.json();
    const tbody = document.querySelector("#stocksTable tbody");
    tbody.innerHTML = "";
    data.forEach(stock => {
        const row = document.createElement("tr");
        row.innerHTML = `<td>${stock.ticker}</td><td>${stock.price}</td><td>${stock.rsi}</td><td>${stock.volume}</td><td>${stock.change_pct}</td>`;
        tbody.appendChild(row);
    });
}
