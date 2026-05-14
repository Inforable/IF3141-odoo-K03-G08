/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, useState, onMounted } = owl;

export class ProcurementDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            data: {},
            filteredMaterials: [],
            loading: true,
            filterPeriod: 'Bulanan',
            searchQuery: '',
            selectedStatus: 'All'
        });
        
        this.chartInstances = {};

        onWillStart(async () => {
            await this.loadData();
        });

        onMounted(() => {
            setTimeout(() => {
                this.renderCharts();
            }, 100);
        });
    }

    async loadData(domain = []) {
        this.state.loading = true;
        const result = await this.rpc("/web/dataset/call_kw/procurement.dashboard/get_dashboard_data", {
            model: 'procurement.dashboard',
            method: 'get_dashboard_data',
            args: [domain],
            kwargs: {},
        });
        this.state.data = result;
        this.state.filteredMaterials = result.materials || [];
        this.state.loading = false;
    }

    onSearchChange(ev) {
        this.state.searchQuery = ev.target.value.toLowerCase();
        this.applyFilters();
    }

    onStatusFilterChange(status) {
        this.state.selectedStatus = status;
        this.applyFilters();
    }

    applyFilters() {
        // Apply search dan status filter 

        let filtered = this.state.data.materials || [];

        // Search query
        if (this.state.searchQuery) {
            filtered = filtered.filter(item =>
                item.name.toLowerCase().includes(this.state.searchQuery) ||
                item.kategori.toLowerCase().includes(this.state.searchQuery)
            );
        }

        // Filter status
        if (this.state.selectedStatus !== 'All') {
            filtered = filtered.filter(item => item.status === this.state.selectedStatus);
        }

        this.state.filteredMaterials = filtered;
    }

    renderCharts() {
        if (!this.state.data.charts) return;
        
        // Destroy existing charts jika ada
        Object.values(this.chartInstances).forEach(chart => {
            if (chart) chart.destroy();
        });
        
        // Load Chart.js library if not available
        if (typeof Chart === 'undefined') {
            this.loadChartLib();
        } else {
            this.renderCategoryChart();
        }
    }

    loadChartLib() {
        console.log('Loading Chart.js library...');
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js';
        script.onload = () => {
            console.log('Chart.js loaded successfully');
            this.renderCategoryChart();
        };
        script.onerror = () => {
            console.error('Failed to load Chart.js');
        };
        document.head.appendChild(script);
    }

    renderCategoryChart() {
        const ctx = document.getElementById('categoryChart');
        if (!ctx || typeof Chart === 'undefined') return;

        const chartData = this.state.data.charts || {};
        
        console.log('Rendering Category Bar Chart with data:', chartData);
        
        this.chartInstances.categoryChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartData.labels || ['Bahan Utama', 'Bahan Tambahan', 'Packaging'],
                datasets: [
                    {
                        label: 'Jumlah Bahan',
                        data: chartData.category_counts || [0, 0, 0],
                        backgroundColor: ['#4f46e5', '#06b6d4', '#1B2939', '#22c55e', '#ef4444'],
                        borderColor: '#4f46e5',
                        borderWidth: 1,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        precision: 0,
                    }
                }
            }
        });
    }
}

ProcurementDashboard.template = "procurement_dashboard.MainDashboard";
registry.category("actions").add("procurement_dashboard.main", ProcurementDashboard);