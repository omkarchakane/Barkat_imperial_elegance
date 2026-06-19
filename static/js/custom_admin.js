(function () {
    function getChartData() {
        const chartDataNode = document.getElementById('barkat-admin-chart-data');
        if (!chartDataNode) {
            return null;
        }

        try {
            return JSON.parse(chartDataNode.textContent);
        } catch (error) {
            return null;
        }
    }

    function luxuryGridColor() {
        return 'rgba(31, 41, 55, 0.08)';
    }

    function createGradient(ctx, colorStart, colorEnd) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 320);
        gradient.addColorStop(0, colorStart);
        gradient.addColorStop(1, colorEnd);
        return gradient;
    }

    function initCharts() {
        if (!window.Chart) {
            return;
        }

        const data = getChartData();
        if (!data) {
            return;
        }

        const monthlyCanvas = document.getElementById('monthlySalesChart');
        if (monthlyCanvas) {
            try {
                const ctx = monthlyCanvas.getContext('2d');
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: data.salesLabels,
                        datasets: [{
                            label: 'Monthly Sales',
                            data: data.monthlySales,
                            borderColor: '#8B0000',
                            backgroundColor: createGradient(ctx, 'rgba(139, 0, 0, 0.22)', 'rgba(139, 0, 0, 0.02)'),
                            borderWidth: 3,
                            pointBackgroundColor: '#C9A227',
                            pointBorderColor: '#ffffff',
                            pointBorderWidth: 2,
                            pointRadius: 4,
                            tension: 0.42,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                backgroundColor: '#111827',
                                titleColor: '#C9A227',
                                bodyColor: '#ffffff',
                                padding: 12,
                                cornerRadius: 12
                            }
                        },
                        scales: {
                            x: { grid: { display: false }, ticks: { color: '#6B7280' } },
                            y: { grid: { color: luxuryGridColor() }, ticks: { color: '#6B7280' }, beginAtZero: true }
                        }
                    }
                });
                monthlyCanvas.dataset.ready = 'chart';
            } catch (error) {
                monthlyCanvas.dataset.ready = '';
            }
        }

        const categoryCanvas = document.getElementById('categoryDoughnutChart');
        if (categoryCanvas) {
            try {
                new Chart(categoryCanvas.getContext('2d'), {
                    type: 'doughnut',
                    data: {
                        labels: data.categoryLabels,
                        datasets: [{
                            data: data.categoryValues,
                            backgroundColor: data.categoryColors,
                            borderColor: '#ffffff',
                            borderWidth: 4,
                            hoverOffset: 8
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '64%',
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    boxWidth: 12,
                                    color: '#1F2937',
                                    font: { weight: '700' }
                                }
                            }
                        }
                    }
                });
                categoryCanvas.dataset.ready = 'chart';
            } catch (error) {
                categoryCanvas.dataset.ready = '';
            }
        }

        const revenueCanvas = document.getElementById('revenueTrendChart');
        if (revenueCanvas) {
            try {
                const ctx = revenueCanvas.getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.salesLabels,
                        datasets: [{
                            type: 'bar',
                            label: 'Revenue',
                            data: data.monthlySales,
                            backgroundColor: 'rgba(201, 162, 39, 0.72)',
                            borderRadius: 12,
                            maxBarThickness: 28
                        }, {
                            type: 'line',
                            label: 'Trend',
                            data: data.revenueTrends,
                            borderColor: '#8B0000',
                            borderWidth: 3,
                            pointRadius: 0,
                            tension: 0.4,
                            yAxisID: 'trend'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                labels: {
                                    color: '#1F2937',
                                    font: { weight: '700' }
                                }
                            }
                        },
                        scales: {
                            x: { grid: { display: false }, ticks: { color: '#6B7280' } },
                            y: { grid: { color: luxuryGridColor() }, ticks: { color: '#6B7280' }, beginAtZero: true },
                            trend: { display: false, position: 'right', beginAtZero: true }
                        }
                    }
                });
                revenueCanvas.dataset.ready = 'chart';
            } catch (error) {
                revenueCanvas.dataset.ready = '';
            }
        }
    }

    function initSidebar() {
        const toggle = document.querySelector('.lux-sidebar-toggle');
        if (!toggle) {
            return;
        }

        toggle.addEventListener('click', function () {
            document.body.classList.toggle('sidebar-open');
        });
    }

    function setupCanvas(canvas) {
        const parent = canvas.parentElement;
        const width = parent ? parent.clientWidth : 640;
        const height = parent ? parent.clientHeight : 300;
        const ratio = window.devicePixelRatio || 1;
        canvas.width = width * ratio;
        canvas.height = height * ratio;
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;
        const context = canvas.getContext('2d');
        context.setTransform(ratio, 0, 0, ratio, 0, 0);
        context.clearRect(0, 0, width, height);
        return { context, width, height };
    }

    function drawFallbackLineChart(canvas, labels, values) {
        if (!canvas) return;
        canvas.dataset.ready = 'fallback';
        const { context, width, height } = setupCanvas(canvas);
        const padding = { top: 24, right: 24, bottom: 38, left: 48 };
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;
        const maxValue = Math.max(...values, 1);
        const points = values.map((value, index) => ({
            x: padding.left + (chartWidth * index / Math.max(values.length - 1, 1)),
            y: padding.top + chartHeight - ((value / maxValue) * chartHeight),
        }));

        context.strokeStyle = 'rgba(31, 41, 55, 0.08)';
        context.lineWidth = 1;
        context.font = '700 11px Inter, Arial';
        context.fillStyle = '#6B7280';
        for (let index = 0; index <= 4; index += 1) {
            const y = padding.top + chartHeight * index / 4;
            context.beginPath();
            context.moveTo(padding.left, y);
            context.lineTo(width - padding.right, y);
            context.stroke();
        }

        const gradient = context.createLinearGradient(0, padding.top, 0, height - padding.bottom);
        gradient.addColorStop(0, 'rgba(139, 0, 0, 0.24)');
        gradient.addColorStop(1, 'rgba(139, 0, 0, 0.02)');
        context.beginPath();
        points.forEach((point, index) => index ? context.lineTo(point.x, point.y) : context.moveTo(point.x, point.y));
        context.lineTo(points[points.length - 1].x, height - padding.bottom);
        context.lineTo(points[0].x, height - padding.bottom);
        context.closePath();
        context.fillStyle = gradient;
        context.fill();

        context.beginPath();
        points.forEach((point, index) => index ? context.lineTo(point.x, point.y) : context.moveTo(point.x, point.y));
        context.strokeStyle = '#8B0000';
        context.lineWidth = 3;
        context.lineJoin = 'round';
        context.lineCap = 'round';
        context.stroke();

        points.forEach((point, index) => {
            context.beginPath();
            context.arc(point.x, point.y, 4, 0, Math.PI * 2);
            context.fillStyle = '#C9A227';
            context.fill();
            context.strokeStyle = '#ffffff';
            context.lineWidth = 2;
            context.stroke();
            if (index % 2 === 0 || width > 620) {
                context.fillStyle = '#6B7280';
                context.textAlign = 'center';
                context.fillText(labels[index], point.x, height - 14);
            }
        });
    }

    function drawFallbackDoughnut(canvas, labels, values, colors) {
        if (!canvas) return;
        canvas.dataset.ready = 'fallback';
        const { context, width, height } = setupCanvas(canvas);
        const total = values.reduce((sum, value) => sum + value, 0) || 1;
        const radius = Math.min(width, height) * 0.28;
        const centerX = width / 2;
        const centerY = height * 0.43;
        let start = -Math.PI / 2;

        values.forEach((value, index) => {
            const slice = (value / total) * Math.PI * 2;
            context.beginPath();
            context.arc(centerX, centerY, radius, start, start + slice);
            context.arc(centerX, centerY, radius * 0.58, start + slice, start, true);
            context.closePath();
            context.fillStyle = colors[index] || '#C9A227';
            context.fill();
            start += slice;
        });

        context.fillStyle = '#1F2937';
        context.font = '900 24px Inter, Arial';
        context.textAlign = 'center';
        context.fillText(String(total), centerX, centerY + 6);
        context.font = '700 12px Inter, Arial';
        context.fillStyle = '#6B7280';
        context.fillText('Products', centerX, centerY + 26);

        const legendY = height - 70;
        labels.slice(0, 4).forEach((label, index) => {
            const x = index % 2 === 0 ? width * 0.17 : width * 0.56;
            const y = legendY + Math.floor(index / 2) * 24;
            context.fillStyle = colors[index] || '#C9A227';
            context.fillRect(x, y - 9, 10, 10);
            context.fillStyle = '#1F2937';
            context.font = '700 12px Inter, Arial';
            context.textAlign = 'left';
            context.fillText(label, x + 16, y);
        });
    }

    function drawFallbackRevenueChart(canvas, labels, monthlySales, trendValues) {
        if (!canvas) return;
        canvas.dataset.ready = 'fallback';
        const { context, width, height } = setupCanvas(canvas);
        const padding = { top: 24, right: 24, bottom: 38, left: 44 };
        const chartWidth = width - padding.left - padding.right;
        const chartHeight = height - padding.top - padding.bottom;
        const maxBar = Math.max(...monthlySales, 1);
        const maxTrend = Math.max(...trendValues, 1);
        const barGap = 8;
        const barWidth = Math.max(12, (chartWidth / monthlySales.length) - barGap);

        context.strokeStyle = 'rgba(31, 41, 55, 0.08)';
        for (let index = 0; index <= 4; index += 1) {
            const y = padding.top + chartHeight * index / 4;
            context.beginPath();
            context.moveTo(padding.left, y);
            context.lineTo(width - padding.right, y);
            context.stroke();
        }

        monthlySales.forEach((value, index) => {
            const x = padding.left + (chartWidth / monthlySales.length) * index + barGap / 2;
            const barHeight = (value / maxBar) * chartHeight;
            const y = padding.top + chartHeight - barHeight;
            context.fillStyle = 'rgba(201, 162, 39, 0.76)';
            context.beginPath();
            if (context.roundRect) {
                context.roundRect(x, y, barWidth, barHeight, 10);
            } else {
                context.rect(x, y, barWidth, barHeight);
            }
            context.fill();
        });

        context.beginPath();
        trendValues.forEach((value, index) => {
            const x = padding.left + (chartWidth / Math.max(trendValues.length - 1, 1)) * index;
            const y = padding.top + chartHeight - ((value / maxTrend) * chartHeight);
            index ? context.lineTo(x, y) : context.moveTo(x, y);
        });
        context.strokeStyle = '#8B0000';
        context.lineWidth = 3;
        context.lineCap = 'round';
        context.lineJoin = 'round';
        context.stroke();

        context.fillStyle = '#6B7280';
        context.font = '700 11px Inter, Arial';
        context.textAlign = 'center';
        labels.forEach((label, index) => {
            if (index % 2 === 0 || width > 620) {
                const x = padding.left + (chartWidth / Math.max(labels.length - 1, 1)) * index;
                context.fillText(label, x, height - 14);
            }
        });
    }

    function initFallbackCharts() {
        const data = getChartData();
        if (!data) return;
        drawFallbackLineChart(document.getElementById('monthlySalesChart'), data.salesLabels, data.monthlySales);
        drawFallbackDoughnut(
            document.getElementById('categoryDoughnutChart'),
            data.categoryLabels,
            data.categoryValues,
            data.categoryColors
        );
        drawFallbackRevenueChart(
            document.getElementById('revenueTrendChart'),
            data.salesLabels,
            data.monthlySales,
            data.revenueTrends
        );
    }

    document.addEventListener('DOMContentLoaded', function () {
        initCharts();
        initSidebar();
        initFallbackCharts();
        window.setTimeout(initFallbackCharts, 800);
        window.setTimeout(initFallbackCharts, 1800);
        window.addEventListener('resize', function () {
            window.setTimeout(initFallbackCharts, 150);
        });
    });
})();
