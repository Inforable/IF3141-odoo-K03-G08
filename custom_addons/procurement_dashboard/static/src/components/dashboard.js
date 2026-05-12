/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, useState } = owl;

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

        onWillStart(async () => {
            await this.loadData();
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
}

ProcurementDashboard.template = "procurement_dashboard.MainDashboard";
registry.category("actions").add("procurement_dashboard.main", ProcurementDashboard);