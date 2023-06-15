/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { AccountFileUploader } from "@account/components/bills_upload/bills_upload";

patch(AccountFileUploader.prototype, "AccountFileUploader Upload Complete", {
        async onUploadComplete() {
        if (JSON.parse(sessionStorage.current_action)['name'] == 'Bills')
        {
            const action = await this.orm.call("master.india.instance", "get_data_from_attachment", ["", this.attachmentIdsToProcess], {
                context: { ...this.extraContext, ...this.env.searchModel.context },
            });
            this.attachmentIdsToProcess = [];
            if (action.context && action.context.notifications) {
                for (let [file, msg] of Object.entries(action.context.notifications)) {
                    this.notification.add(
                        msg,
                        {
                            title: file,
                            type: "info",
                            sticky: true,
                        });
                }
                delete action.context.notifications;
            }
            this.action.doAction(action);
            }
        else
        {
            const action = await this.orm.call("account.journal", "create_document_from_attachment", ["", this.attachmentIdsToProcess], {
            context: { ...this.extraContext, ...this.env.searchModel.context },
            });
            this.attachmentIdsToProcess = [];
            if (action.context && action.context.notifications) {
                for (let [file, msg] of Object.entries(action.context.notifications)) {
                    this.notification.add(
                        msg,
                        {
                            title: file,
                            type: "info",
                            sticky: true,
                        });
                }
                delete action.context.notifications;
            }
            this.action.doAction(action);
            }
    }
});