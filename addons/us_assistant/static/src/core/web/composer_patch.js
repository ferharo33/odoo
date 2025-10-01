/* @odoo-module */

import { Composer } from "@mail/core/common/composer";

import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(Composer.prototype, {
    setup() {
        super.setup(...arguments);
        this.rpcService = useService("rpc");
    },
    get HINT_TEXT() {
        return _t("Hint");
    },
    async rpcAssistantHint() {
        const composer = this.props.composer;
        if (!composer?.message) {
            return;
        }
        const res = await this.rpcService("/mail/channel_assistant_hint", {
            message_id: composer.message.id,
            hint: composer.text,
        });
        if (!res.success) {
            this.env.services.notification.add(res.error, {
                type: "warning",
            });
            return;
        }
        composer.text = res.hint;
        composer.selection = {
            start: res.hint.length,
            end: res.hint.length,
            direction: "none",
        };
        if (this.props.onPostCallback) {
            this.props.onPostCallback();
        }
    },
    async editMessage() {
        if (this.props.composer.isAssistantEditing) {
            await this.rpcAssistantHint();
        } else {
            await super.editMessage();
        }
    },
});
