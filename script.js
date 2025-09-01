console.log("NewsPulse UI Loaded");

document.addEventListener("DOMContentLoaded", function () {

    // ----- Auto-dismiss Bootstrap alerts -----
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 4000); // 4 seconds
    });

    // ----- Smooth scroll for anchor links -----
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e){
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // ----- Initialize Chart.js for Trending -----
    ['sentimentChart','entityChart','sourceChart'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            new Chart(el.getContext('2d'), el.dataset.chart ? JSON.parse(el.dataset.chart) : {});
        }
    });
});
