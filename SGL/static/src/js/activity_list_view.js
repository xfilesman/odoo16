/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";
import { registry } from "@web/core/registry";

export class ActivityListController extends ListController {
    setup() {
        super.setup();
    }

    async onOpenColumnWizard() {
        try {
            const viewId = await this.env.services.orm.call('ir.model.data', 'xmlid_to_res_id', ['SGL.view_sgl_file_cover_activity_column_wizard_form']);
            await this.env.services.action.doAction({
                type: 'ir.actions.act_window',
                res_model: 'sgl.file.cover.activity.column.wizard',
                view_mode: 'form',
                target: 'new',
                views: [[viewId, 'form']],
                view_id: viewId,
            });
        } catch (e) {
            await this.env.services.action.doAction({
                type: 'ir.actions.act_window',
                res_model: 'sgl.file.cover.activity.column.wizard',
                view_mode: 'form',
                target: 'new',
            });
        }
    }

    filterByCurrency(code) {
        // Apply domain on the fly to list view based on currency selection
        const model = this.model;
        const currentDomain = model.root && model.root.domain ? [...model.root.domain] : [];
        // remove any previous currency filter for activity lines
        const filtered = currentDomain.filter((d) => !(Array.isArray(d) && d[0] === 'file_currency'));
        if (code) {
            filtered.push(['file_currency', 'ilike', code.toUpperCase()]);
        }
        model.root.domain = filtered;
        model.load().then(() => {
            model.notify();
        });
    }
}

ActivityListController.template = "web.ListView";
ActivityListController.components = {
    ...ListController.components,
};
ActivityListController.buttonTemplate = "SGL.ActivityList.Buttons";

export const ActivityListView = {
    ...listView,
    Controller: ActivityListController,
};

registry.category("views").add("activity_list", ActivityListView);
