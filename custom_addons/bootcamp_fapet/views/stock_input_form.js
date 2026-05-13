/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, useState, onWillStart } = owl;

export class StockInputForm extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.state = useState({
            materials: [],
            loading: false,
            showNewMaterialForm: false,
            newMaterial: {
                name: '',
                category: 'Bahan Utama',
                uom: 'kg',
                stok: 0,
                min_stok: 0
            },
            formData: {
                material_id: null,
                transaction_type: 'in',
                quantity: 0,
                notes: ''
            },
            currentStock: 0,
            stockAfter: 0,
            recentTransactions: []
        });

        onWillStart(async () => {
            await this.loadMaterials();
            await this.loadRecentTransactions();
        });
    }

    async loadMaterials() {
        try {
            const result = await this.rpc("/web/dataset/call_kw/bahan.baku/search_read", {
                model: 'bahan.baku',
                method: 'search_read',
                args: [],
                kwargs: {
                    fields: ['id', 'name', 'stok', 'uom'],
                    order: 'name',
                }
            });
            this.state.materials = result || [];
        } catch (error) {
            console.error('Error loading materials:', error);
            this.state.materials = [];
        }
    }

    async loadRecentTransactions() {
        try {
            const result = await this.rpc("/web/dataset/call_kw/procurement.dashboard/get_stock_input_transactions", {
                model: 'procurement.dashboard',
                method: 'get_stock_input_transactions',
                args: [],
                kwargs: {}
            });
            this.state.recentTransactions = result;
        } catch (error) {
            console.error('Error loading transactions:', error);
        }
    }

    onMaterialChange(ev) {
        const materialId = parseInt(ev.target.value);
        const material = this.state.materials.find(m => m.id === materialId);
        
        this.state.formData.material_id = materialId;
        if (material) {
            this.state.currentStock = material.stok || 0;
            this.updateStockAfter();
        }
    }

    onTransactionTypeChange(ev) {
        this.state.formData.transaction_type = ev.target.value;
        this.updateStockAfter();
    }

    onQuantityChange(ev) {
        this.state.formData.quantity = parseFloat(ev.target.value) || 0;
        this.updateStockAfter();
    }

    onNewMaterialNameChange(ev) {
        this.state.newMaterial.name = ev.target.value;
    }

    onNewMaterialCategoryChange(ev) {
        this.state.newMaterial.category = ev.target.value;
    }

    onNewMaterialUomChange(ev) {
        this.state.newMaterial.uom = ev.target.value;
    }

    onNewMaterialStokChange(ev) {
        this.state.newMaterial.stok = parseFloat(ev.target.value) || 0;
    }

    onNewMaterialMinStokChange(ev) {
        this.state.newMaterial.min_stok = parseFloat(ev.target.value) || 0;
    }

    toggleNewMaterialForm() {
        this.state.showNewMaterialForm = !this.state.showNewMaterialForm;
    }

    cancelNewMaterialForm() {
        this.state.showNewMaterialForm = false;
    }

    updateStockAfter() {
        if (this.state.formData.transaction_type === 'in') {
            this.state.stockAfter = this.state.currentStock + this.state.formData.quantity;
        } else {
            this.state.stockAfter = this.state.currentStock - this.state.formData.quantity;
        }
    }

    async submitForm() {
        if (this.state.stockAfter < 0) {
            this.notification.add('Stok tidak boleh negatif!', {
                type: 'danger',
                sticky: false
            });
            return;
        }

        if (!this.state.formData.material_id) {
            this.notification.add('Pilih bahan baku terlebih dahulu!', {
                type: 'warning',
                sticky: false
            });
            return;
        }

        this.state.loading = true;
        try {
            const result = await this.rpc("/web/dataset/call_kw/procurement.dashboard/update_stock_with_history", {
                model: 'procurement.dashboard',
                method: 'update_stock_with_history',
                args: [
                    this.state.formData.material_id,
                    this.state.formData.quantity,
                    this.state.formData.transaction_type,
                    this.state.formData.notes
                ],
                kwargs: {}
            });

            if (result.success) {
                this.notification.add('Stok berhasil diperbarui!', {
                    type: 'success',
                    sticky: false
                });

                // Reset form
                this.state.formData = {
                    material_id: null,
                    transaction_type: 'in',
                    quantity: 0,
                    notes: ''
                };
                this.state.currentStock = 0;
                this.state.stockAfter = 0;

                // Reload materials dan transactions
                await this.loadMaterials();
                await this.loadRecentTransactions();
            } else {
                this.notification.add(result.message || 'Gagal menyimpan data', {
                    type: 'danger',
                    sticky: false
                });
            }
        } catch (error) {
            this.notification.add('Gagal menyimpan data: ' + error.message, {
                type: 'danger',
                sticky: false
            });
        } finally {
            this.state.loading = false;
        }
    }

    async createNewMaterial() {
        if (!this.state.newMaterial.name) {
            this.notification.add('Nama bahan baku tidak boleh kosong!', {
                type: 'warning',
                sticky: false
            });
            return;
        }

        this.state.loading = true;
        try {
            const newMaterialId = await this.rpc("/web/dataset/call_kw/bahan.baku/create", {
                model: 'bahan.baku',
                method: 'create',
                args: [{
                    name: this.state.newMaterial.name,
                    category: this.state.newMaterial.category,
                    uom: this.state.newMaterial.uom,
                    stok: this.state.newMaterial.stok,
                    min_stok: this.state.newMaterial.min_stok
                }],
                kwargs: {}
            });

            this.notification.add('Bahan baku berhasil ditambahkan!', {
                type: 'success',
                sticky: false
            });

            // Reset form
            this.state.newMaterial = {
                name: '',
                category: 'Bahan Utama',
                uom: 'kg',
                stok: 0,
                min_stok: 0
            };
            this.state.showNewMaterialForm = false;

            // Reload materials
            await this.loadMaterials();

            // Auto-select material baru
            // this.state.formData.material_id = newMaterialId;
            // const material = this.state.materials.find(m => m.id === newMaterialId);
            // if (material) {
            //     this.state.currentStock = material.stok || 0;
            //     this.updateStockAfter();
            // }
        } catch (error) {
            this.notification.add('Gagal menambahkan bahan baku: ' + error.message, {
                type: 'danger',
                sticky: false
            });
        } finally {
            this.state.loading = false;
        }
    }
}

StockInputForm.template = "procurement_dashboard.StockInputForm";
registry.category("actions").add("procurement_dashboard.stock_input", StockInputForm);