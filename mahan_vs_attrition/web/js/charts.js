/**
 * Canvas-based chart rendering for war dynamics visualization
 */

class TimelineChart {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) throw new Error(`Canvas #${canvasId} not found`);
        this.ctx = this.canvas.getContext('2d');
        this.options = Object.assign({
            xLabel: 'Months',
            yLabel: 'Strength',
            yMin: 0,
            yMax: 100,
            xMax: null,
            gridColor: '#E0E0E0',
            textColor: '#666666',
            thresholdLines: [],
            thresholdColor: '#BDBDBD'
        }, options);
        this.series = [];
        this.xData = [];
        this.thresholdLines = this.options.thresholdLines;
        this.eventMarkers = [];
        this.selectedEventMonth = null;

        this._resize = this._handleResize.bind(this);
        window.addEventListener('resize', this._resize);
        this._handleResize();
    }

    _handleResize() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = rect.width * dpr;
        this.canvas.height = 280 * dpr;
        this.canvas.style.width = rect.width + 'px';
        this.canvas.style.height = '280px';
        this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        this.width = rect.width;
        this.height = 280;
        if (this.series.length > 0) {
            this._draw();
        }
    }

    _getPlotArea() {
        return {
            left: 55,
            top: 15,
            right: this.width - 15,
            bottom: this.height - 35,
            width: this.width - 70,
            height: this.height - 50
        };
    }

    _clear() {
        this.ctx.clearRect(0, 0, this.width, this.height);
    }

    _drawGrid() {
        const ctx = this.ctx;
        const plot = this._getPlotArea();
        const ySteps = 5;

        ctx.strokeStyle = this.options.gridColor;
        ctx.lineWidth = 0.5;

        for (let i = 0; i <= ySteps; i++) {
            const y = plot.top + (plot.height / ySteps) * i;
            ctx.beginPath();
            ctx.moveTo(plot.left, y);
            ctx.lineTo(plot.right, y);
            ctx.stroke();

            const val = this.options.yMax - (this.options.yMax / ySteps) * i;
            ctx.fillStyle = this.options.textColor;
            ctx.font = '11px sans-serif';
            ctx.textAlign = 'right';
            ctx.fillText(Math.round(val), plot.left - 8, y + 4);
        }

        const maxX = this.options.xMax || Math.max(...this.xData, 1);
        const xStep = Math.ceil(maxX / 10);
        for (let i = 0; i <= maxX; i += xStep) {
            const x = plot.left + (i / maxX) * plot.width;
            ctx.beginPath();
            ctx.moveTo(x, plot.top);
            ctx.lineTo(x, plot.bottom);
            ctx.stroke();

            ctx.fillStyle = this.options.textColor;
            ctx.font = '11px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(i, x, plot.bottom + 18);
        }

        ctx.fillStyle = this.options.textColor;
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(this.options.xLabel, plot.left + plot.width / 2, this.height - 4);

        ctx.save();
        ctx.translate(12, plot.top + plot.height / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.fillText(this.options.yLabel, 0, 0);
        ctx.restore();
    }

    _drawThresholds() {
        const ctx = this.ctx;
        const plot = this._getPlotArea();
        const maxX = this.options.xMax || Math.max(...this.xData, 1);

        for (const line of this.thresholdLines) {
            const y = plot.top + plot.height - (line.value / this.options.yMax) * plot.height;
            ctx.strokeStyle = line.color || this.options.thresholdColor;
            ctx.lineWidth = 1;
            ctx.setLineDash([6, 4]);
            ctx.beginPath();
            ctx.moveTo(plot.left, y);
            ctx.lineTo(plot.right, y);
            ctx.stroke();
            ctx.setLineDash([]);

            if (line.label) {
                ctx.fillStyle = line.color || this.options.thresholdColor;
                ctx.font = '10px sans-serif';
                ctx.textAlign = 'left';
                ctx.fillText(line.label, plot.right - 50, y - 4);
            }
        }
    }

    _drawEventMarkers() {
        if (!this.eventMarkers || this.eventMarkers.length === 0) return;
        const ctx = this.ctx;
        const plot = this._getPlotArea();
        const maxX = this.options.xMax || Math.max(...this.xData, 1);

        const TYPE_COLORS = {
            trigger:   '#F44336',
            military:  '#2196F3',
            shock:     '#FF9800',
            political: '#9C27B0',
            outcome:   '#4CAF50'
        };

        for (const ev of this.eventMarkers) {
            if (ev.month > maxX) continue;
            const x = plot.left + (ev.month / maxX) * plot.width;
            const color = TYPE_COLORS[ev.type] || '#999';

            ctx.strokeStyle = color;
            ctx.lineWidth = 1.5;
            ctx.setLineDash([4, 3]);
            ctx.beginPath();
            ctx.moveTo(x, plot.top);
            ctx.lineTo(x, plot.bottom);
            ctx.stroke();
            ctx.setLineDash([]);

            const markerY = plot.top + 10;
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(x, markerY, 4, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = '#fff';
            ctx.beginPath();
            ctx.arc(x, markerY, 1.5, 0, Math.PI * 2);
            ctx.fill();

            if (ev.month === this.selectedEventMonth) {
                ctx.strokeStyle = color;
                ctx.lineWidth = 3;
                ctx.setLineDash([]);
                ctx.beginPath();
                ctx.moveTo(x, plot.top);
                ctx.lineTo(x, plot.bottom);
                ctx.stroke();
            }
        }
    }

    _draw() {
        this._clear();
        this._drawGrid();
        this._drawThresholds();
        if (typeof this._drawSeries === 'function') {
            this._drawSeries();
        }
        this._drawEventMarkers();
    }

    _drawSeries() {
        if (!this.series || this.series.length === 0 || !this.xData || this.xData.length === 0) {
            return;
        }

        const ctx = this.ctx;
        const plot = this._getPlotArea();
        const maxX = this.options.xMax || Math.max(...this.xData, 1);
        const yMin = this.options.yMin;
        const yMax = this.options.yMax;
        const yRange = Math.max(1, yMax - yMin);

        function toX(x) {
            return plot.left + (x / maxX) * plot.width;
        }

        function toY(y) {
            const clamped = Math.max(yMin, Math.min(yMax, y));
            return plot.bottom - ((clamped - yMin) / yRange) * plot.height;
        }

        for (const s of this.series) {
            if (!s.data || s.data.length === 0) continue;

            ctx.beginPath();
            ctx.strokeStyle = s.color || '#333';
            ctx.lineWidth = s.width || 2;
            ctx.setLineDash(s.dash || []);

            let started = false;

            for (let i = 0; i < s.data.length; i++) {
                const xVal = this.xData[i];
                const yVal = s.data[i];

                if (!Number.isFinite(xVal) || !Number.isFinite(yVal)) {
                    continue;
                }

                const x = toX(xVal);
                const y = toY(yVal);

                if (!started) {
                    ctx.moveTo(x, y);
                    started = true;
                } else {
                    ctx.lineTo(x, y);
                }
            }

            if (started) {
                ctx.stroke();
            }

            ctx.setLineDash([]);
        }
    }

    setEventMarkers(markers) {
        this.eventMarkers = markers || [];
        this._draw();
    }

    setSelectedEventMonth(month) {
        this.selectedEventMonth = month;
        this._draw();
    }

    setData(xData, seriesData) {
        this.xData = xData;
        this.series = seriesData;
        this._draw();
    }

    setXMax(max) {
        this.options.xMax = max || null;
        this._draw();
    }

    addThreshold(value, label, color) {
        this.thresholdLines.push({ value, label, color });
    }

    setThresholds(lines) {
        this.thresholdLines = lines;
    }

    destroy() {
        window.removeEventListener('resize', this._resize);
    }
}

/**
 * Build legend HTML for a chart
 */
function buildLegend(containerId, items) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';
    for (const item of items) {
        const div = document.createElement('div');
        div.className = 'legend-item';
        const swatch = document.createElement('span');
        swatch.className = 'legend-swatch';
        swatch.style.backgroundColor = item.color;
        const label = document.createElement('span');
        label.textContent = item.name;
        div.appendChild(swatch);
        div.appendChild(label);
        container.appendChild(div);
    }
}
