/** @odoo-module **/

import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { onMounted, onPatched } from "@odoo/owl";

// Append ' EGP' to totals row cells for EGP amount columns
patch(ListRenderer.prototype, 'SGL_list_footer_egp_suffix', {
    setup() {
        const res = this._super(...arguments);
        const appendSuffix = () => {
            try {
                const root = this.el;
                if (!root) return;
                const tfoot = root.querySelector('tfoot');
                if (!tfoot) return;
                const footerCells = Array.from(tfoot.querySelectorAll('td'));
                const names = ['estimate_profit_egp','actual_profit_egp','estimate_cost_egp','actual_cost_egp','estimate_revenue_egp','actual_revenue_egp'];
                footerCells.forEach((cell) => {
                    const name = cell.getAttribute('data-name') || cell.getAttribute('data-field');
                    if (name && names.includes(name) && !cell.dataset.egpAppended) {
                        const txt = (cell.textContent || '').trim();
                        if (txt && !/\bEGP\b/.test(txt)) {
                            cell.textContent = `${txt} EGP`;
                            cell.dataset.egpAppended = '1';
                        }
                    }
                });
            } catch (_) {
                // no-op
            }
        };
        onMounted(appendSuffix);
        onPatched(appendSuffix);
        return res;
    },
});


