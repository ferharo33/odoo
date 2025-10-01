/* @odoo-module */

import { Composer } from "@mail/core/common/composer";

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

patch(Composer.prototype, {
    setup() {
        super.setup();
        this.isAssisatantEditing = false;
    },
    get HINT_TEXT() {
        return _t("Hint");
    },
    async rpcAssistantHint() {
        const res = await this.rpc("/mail/channel_assistant_hint",{
            message_id: this.message.id,
            hint: this.props.composer.textInputContent,
        });
        if (!res.success) {
            this.env.services.notification.add(res.error,{
                type: 'warning',
            });
            return;
        }
        this.props.composer.message.originThread.composer.textInputContent = res.hint;
        if (this.props.onPostCallback) {
            this.props.onPostCallback();
        }
    },
    async editMessage() {
        if (this.props.composer.isAssistantEditing === true) {
            await this.rpcAssistantHint();
        }
        else {
            await super.editMessage();
        }
    },
});
