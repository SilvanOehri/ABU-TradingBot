// Trading Bot Dashboard JavaScript

class TradingBotDashboard {
    constructor() {
        this.initializeEventListeners();
        // Load configuration and then attempt to restore cached results (if any)
        this.loadDefaultConfig().then(() => this.loadCachedResults());
    }

    initializeEventListeners() {
        const configForm = document.getElementById('configForm');
        configForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.runBacktest();
        });
    }

    async loadDefaultConfig() {
        try {
            const response = await fetch('/api/config');
            const data = await response.json();
            
            if (data.success) {
                this.populateForm(data.data);
            }
        } catch (error) {
            console.error('Error loading config:', error);
        }
    }

    populateForm(config) {
        document.getElementById('symbol').value = config.symbol;
        document.getElementById('initial_capital').value = config.initial_capital;
        document.getElementById('backtest_days').value = config.backtest_days;
    }

    async runBacktest() {
        const formData = new FormData(document.getElementById('configForm'));
        const config = Object.fromEntries(formData.entries());
        
        // Convert numeric values
        config.initial_capital = parseFloat(config.initial_capital);
        config.backtest_days = parseInt(config.backtest_days);

        this.showLoading();
        this.updateStatus('info', 'Führe Backtest durch...');

        try {
            const response = await fetch('/api/backtest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            const result = await response.json();

            if (result.success) {
                this.displayResults(result.data);
                // Persist last successful backtest so it survives reloads/navigation
                this.saveCachedResults(result.data);
                this.updateStatus('success', 'Backtest erfolgreich abgeschlossen!');
            } else {
                this.showError(result.error);
                this.updateStatus('danger', `Fehler: ${result.error}`);
            }
        } catch (error) {
            this.showError(`Netzwerkfehler: ${error.message}`);
            this.updateStatus('danger', `Netzwerkfehler: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    showLoading() {
        document.getElementById('loadingContainer').style.display = 'block';
        document.getElementById('resultsContainer').style.display = 'none';
        document.getElementById('errorContainer').style.display = 'none';
    }

    hideLoading() {
        document.getElementById('loadingContainer').style.display = 'none';
    }

    // --- Local cache for last backtest (persists across reloads/navigation) ---
    saveCachedResults(data) {
        try {
            const payload = {
                saved_at: new Date().toISOString(),
                data: data
            };
            localStorage.setItem('lastBacktest', JSON.stringify(payload));
        } catch (e) {
            console.warn('Unable to save cached results:', e);
        }
    }

    loadCachedResults() {
        try {
            const raw = localStorage.getItem('lastBacktest');
            if (!raw) return;
            const payload = JSON.parse(raw);
            if (!payload || !payload.data) return;

            // Restore form values (if present) and show cached results
            if (payload.data.config) {
                this.populateForm(payload.data.config);
            }
            this.displayResults(payload.data);
            this.updateStatus('info', `Geladene Ergebnisse vom ${new Date(payload.saved_at).toLocaleString()}`);
        } catch (e) {
            console.warn('Unable to load cached results:', e);
            localStorage.removeItem('lastBacktest');
        }
    }

    clearCachedResults() {
        localStorage.removeItem('lastBacktest');
    }

    displayResults(data) {
        // Market Info anzeigen
        this.displayMarketInfo(data.market_data, data.config);
        
        // Strategie Ergebnisse anzeigen
        this.displayStrategyResults(data.results);
        
        // Beste Strategie hervorheben
        this.displayBestStrategy(data.results[0]);
        
        // Vergleichs-Button anzeigen
        document.getElementById('compareButton').style.display = 'block';
        
        document.getElementById('resultsContainer').style.display = 'block';
        document.getElementById('resultsContainer').classList.add('fade-in-up');
    }

    displayMarketInfo(marketData, config) {
        document.getElementById('marketSymbol').textContent = marketData.symbol;
        document.getElementById('marketStartPrice').textContent = this.formatCurrency(marketData.start_price);
        document.getElementById('marketEndPrice').textContent = this.formatCurrency(marketData.end_price);
        document.getElementById('marketDays').textContent = `${marketData.total_days} Tage`;
    }

    displayStrategyResults(results) {
        const tbody = document.getElementById('resultsTableBody');
        tbody.innerHTML = '';

        results.forEach((result, index) => {
            const row = this.createResultRow(result, index + 1);
            tbody.appendChild(row);
        });
    }

    createResultRow(result, rank) {
        const row = document.createElement('tr');
        
        // Rank Badge
        const rankBadge = this.createRankBadge(rank);
        
        // Performance Klasse
        const performanceClass = result.return_percentage > 0 ? 'performance-positive' : 
                               result.return_percentage < 0 ? 'performance-negative' : 'performance-neutral';

        // Klickbar machen - CHART VERSION
        row.style.cursor = 'pointer';
        row.setAttribute('onclick', `window.location.href='/strategy/${result.id || rank - 1}/chart'`);
        row.setAttribute('title', '📈 Klicken für Portfolio-Chart');

        row.innerHTML = `
            <td>${rankBadge}</td>
            <td><strong>${result.strategy_name}</strong> <i class="fas fa-external-link-alt text-muted"></i></td>
            <td>${this.formatCurrency(result.final_value)}</td>
            <td class="${performanceClass}">${result.return_percentage.toFixed(2)}%</td>
            <td class="${performanceClass}">${this.formatCurrency(result.profit_loss)}</td>
            <td><span class="badge bg-secondary">${result.total_trades}</span></td>
        `;

        // Hover-Effekt
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });

        return row;
    }

    createRankBadge(rank) {
        let badgeClass = 'bg-secondary';
        let icon = '';
        
        if (rank === 1) {
            badgeClass = 'rank-1';
            icon = '<i class="fas fa-trophy"></i> ';
        } else if (rank === 2) {
            badgeClass = 'rank-2';
            icon = '<i class="fas fa-medal"></i> ';
        } else if (rank === 3) {
            badgeClass = 'rank-3';
            icon = '<i class="fas fa-award"></i> ';
        }

        return `<span class="badge ${badgeClass}">${icon}#${rank}</span>`;
    }

    displayBestStrategy(bestStrategy) {
        const alertContainer = document.getElementById('bestStrategyAlert');
        const alertText = document.getElementById('bestStrategyText');
        
        alertText.innerHTML = `
            <strong>${bestStrategy.strategy_name}</strong> ist die beste Strategie mit 
            <strong>${bestStrategy.return_percentage.toFixed(2)}%</strong> Rendite!
            <br>
            Endkapital: <strong>${this.formatCurrency(bestStrategy.final_value)}</strong> 
            (Gewinn: <strong>${this.formatCurrency(bestStrategy.profit_loss)}</strong>)
        `;
        
        alertContainer.style.display = 'block';
    }

    showError(error) {
        document.getElementById('errorText').textContent = error;
        document.getElementById('errorContainer').style.display = 'block';
        document.getElementById('resultsContainer').style.display = 'none';
    }

    updateStatus(type, message) {
        const statusContainer = document.getElementById('statusContainer');
        const alertClass = `alert-${type}`;
        
        let icon = '';
        switch(type) {
            case 'success':
                icon = '<i class="fas fa-check-circle"></i>';
                break;
            case 'danger':
                icon = '<i class="fas fa-exclamation-triangle"></i>';
                break;
            case 'info':
                icon = '<i class="fas fa-info-circle"></i>';
                break;
            default:
                icon = '<i class="fas fa-info-circle"></i>';
        }
        
        statusContainer.innerHTML = `
            <div class="alert ${alertClass}">
                ${icon} ${message}
            </div>
        `;
    }

    formatCurrency(value) {
        return new Intl.NumberFormat('de-DE', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    }
}

// Dashboard initialisieren wenn Seite geladen ist
document.addEventListener('DOMContentLoaded', () => {
    new TradingBotDashboard();
});
