// static/script.js
async function fetchData() {
    const response = await fetch("/filter");
    const data = await response.json();

    const tableBody = document.querySelector("#stocksTable tbody");
    tableBody.innerHTML = ""; // حذف البيانات السابقة

    data.forEach(stock => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${stock.ticker}</td>
            <td>${stock.price} ريال</td>
            <td>${stock.rsi}</td>
            <td>${stock.volume.toLocaleString()}</td>
            <td>${stock.change_pct}%</td>
        `;

        tableBody.appendChild(row);
    });
}
