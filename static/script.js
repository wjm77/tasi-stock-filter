async function fetchData() {
    const response = await fetch('/filter');
    const stocks = await response.json();

    const tbody = document.querySelector('#stocksTable tbody');
    tbody.innerHTML = '';

    stocks.forEach(stock => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${stock.ticker}</td>
            <td>${stock.price}</td>
            <td>${stock.rsi}</td>
            <td>${stock.volume}</td>
            <td>${stock.change_pct}%</td>
        `;
        tbody.appendChild(tr);
    });
}

// تحميل البيانات أول مرة عند فتح الصفحة
window.onload = fetchData;
