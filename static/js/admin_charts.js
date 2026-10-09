/**
 * CrimeConnect - Admin Dashboard Charts using Chart.js
 */

document.addEventListener('DOMContentLoaded', () => {
  const categoryCanvas = document.getElementById('categoryChart');
  const statusCanvas = document.getElementById('statusChart');

  if (categoryCanvas && statusCanvas) {
    fetch('/admin/api/stats')
      .then(response => response.json())
      .then(data => {
        renderCategoryChart(categoryCanvas, data.categories);
        renderStatusChart(statusCanvas, data.statuses);
      })
      .catch(error => {
        console.error('Error fetching dashboard statistics:', error);
      });
  }
});

function renderCategoryChart(canvas, categoryData) {
  const labels = Object.keys(categoryData);
  const counts = Object.values(categoryData);

  new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: counts,
        backgroundColor: [
          '#2563eb', // Blue
          '#7c3aed', // Purple
          '#d97706', // Amber
          '#dc2626', // Red
          '#059669', // Emerald
          '#0891b2', // Cyan
          '#475569'  // Slate
        ],
        borderWidth: 2,
        borderColor: 'transparent'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 12,
            font: { size: 12 }
          }
        }
      }
    }
  });
}

function renderStatusChart(canvas, statusData) {
  const labels = Object.keys(statusData);
  const counts = Object.values(statusData);

  new Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Complaints',
        data: counts,
        backgroundColor: [
          '#38bdf8', // Submitted (Sky)
          '#fbbf24', // Under Review (Amber)
          '#c084fc', // Info Requested (Purple)
          '#34d399', // Resolved (Green)
          '#94a3b8'  // Closed (Slate)
        ],
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      }
    }
  });
}
