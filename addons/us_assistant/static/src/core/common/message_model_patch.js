/* @odoo-module */

import { Message } from "@mail/core/common/message";

import { useState } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { convertBrToLineBreak, htmlToTextContentInline } from "@mail/utils/common/format";

patch(Message.prototype, {
    onClickAssistantEdit() {
        return this.enterAssisstantEditMode();
    },
    enterAssisstantEditMode() {
        const messageContent = convertBrToLineBreak(this.props.message.body);
        this.props.message.composer = {
            mentionedPartners: this.props.message.recipients,
            textInputContent: messageContent,
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
        return Boolean(!this.message.is_transient && this.message.res_id && this.message.type === "comment");
    }
});