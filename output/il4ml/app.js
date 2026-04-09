/* filename: app.js */
document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/pivot')
        .then(response => response.json())
        .then(data => {
            renderChart(data);
            renderTable(data);
        })
        .catch(error => console.error('Error fetching data:', error));
});

function renderChart(data) {
    const ctx = document.getElementById('pivotChart').getContext('2d');
    
    // Extract x_values for the X axis
    const labels = data.map(row => row.x_value.toFixed(2));
    
    // Extract derivative order alphas dynamically (filtering out the 'x_value' column)
    const alphas = Object.keys(data[0])
                         .filter(k => k !== 'x_value')
                         .sort((a, b) => parseFloat(a) - parseFloat(b));
    
    const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f1c40f', '#9b59b6'];
    
    const datasets = alphas.map((alpha, index) => {
        return {
            label: `Order α = ${alpha}`,
            data: data.map(row => row[alpha]),
            borderColor: colors[index % colors.length],
            backgroundColor: colors[index % colors.length],
            borderWidth: 3,
            fill: false,
            tension: 0.3,
            pointRadius: 4,
            pointHoverRadius: 6
        };
    });

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Fractional Derivative Results Over X',
                    font: { size: 16 }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    title: { display: true, text: 'x (Input Value)' },
                    grid: { display: false }
                },
                y: {
                    title: { display: true, text: 'Mean Derivative Value D^α(x^n)' },
                    grid: { color: '#eaeded' }
                }
            }
        }
    });
}

function renderTable(data) {
    if (data.length === 0) return;

    const headerRow = document.getElementById('tableHeader');
    const tbody = document.getElementById('tableBody');
    
    // Dynamically fetch and sort columns representing order (alpha)
    const alphas = Object.keys(data[0])
                         .filter(k => k !== 'x_value')
                         .sort((a, b) => parseFloat(a) - parseFloat(b));
    
    // Build Headers
    const thX = document.createElement('th');
    thX.textContent = 'X Value';
    headerRow.appendChild(thX);
    
    alphas.forEach(alpha => {
        const th = document.createElement('th');
        th.textContent = `Order α = ${alpha}`;
        headerRow.appendChild(th);
    });
    
    // Build Body Rows
    data.forEach(row => {
        const tr = document.createElement('tr');
        
        const tdX = document.createElement('td');
        tdX.innerHTML = `<strong>${row.x_value.toFixed(2)}</strong>`;
        tr.appendChild(tdX);
        
        alphas.forEach(alpha => {
            const td = document.createElement('td');
            const val = row[alpha];
            td.textContent = (val !== null && val !== undefined) ? val.toFixed(4) : '-';
            tr.appendChild(td);
        });
        
        tbody.appendChild(tr);
    });
}
