/* @odoo-module */

import { Message } from "@mail/core/common/message";

import { patch } from "@web/core/utils/patch";
import { convertBrToLineBreak } from "@mail/utils/common/format";
import { toRaw } from "@odoo/owl";

patch(Message.prototype, {
    onClickAssistantEdit() {
        return this.enterAssistantEditMode();
    },
    enterAssistantEditMode() {
        const message = toRaw(this.props.message);
        const messageContent = convertBrToLineBreak(message.body);
        message.composer = {
            mentionedPartners: message.recipients,
            text: messageContent,
            isAssistantEditing: true,
            selection: {
                start: messageContent.length,
                end: messageContent.length,
                direction: "none",
            },
        };
        this.state.isEditing = true;
    },
    get canAssistantHint() {
        return Boolean(
            !this.message.is_transient && this.message.res_id && this.message.type === "comment"
        );
    }
});