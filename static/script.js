async function fetchData() {
    try {
        const response = await fetch('/filter');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
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
    } catch (error) {
        console.error('Error fetching stock data:', error);
    }
}

// تحميل البيانات أول مرة عند فتح الصفحة
window.onload = fetchData;
