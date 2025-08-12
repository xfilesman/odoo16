/** @odoo-module **/
import { ListRenderer } from "@web/views/list/list_renderer";
import { patch } from "@web/core/utils/patch";
import { usePopover } from "@web/core/popover/popover_hook";

patch(ListRenderer.prototype, {
    setup() {
        this._super(...arguments);
        this.popover = usePopover();
    },

    toggleColumn(ev, fieldName) {
        const column = this.state.columns.find(col => col.name === fieldName);
        if (column) {
            column.invisible = !column.invisible;
            this.props.list.model.notify();
        }
    },

    onColumnHeaderClick(ev, column) {
        if (ev.target.closest('.o_column_filter')) {
            const target = ev.target.closest('.o_column_sortable');
            this.popover.add(target, this.constructor.components.ColumnFilter, {
                fieldName: column.name,
                column: column,
                toggle: this.toggleColumn.bind(this),
            });
        } else {
            this._super(...arguments);
        }
    },
});

patch(ListRenderer, {
    template: 'web.ListView',
    components: {
        ...ListRenderer.components,
        ColumnFilter: class ColumnFilter extends owl.Component {
            static template = 'SGL.ColumnFilter';
            
            toggleVisibility() {
                this.props.toggle(null, this.props.fieldName);
            }
        },
    },
});
