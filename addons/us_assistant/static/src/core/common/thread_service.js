/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { ThreadService } from "@mail/core/common/thread_service";
import { patch } from "@web/core/utils/patch";

patch(ThreadService.prototype, {
    async post(
        thread,
        body,
        {
            attachments = [],
            isNote = false,
            parentId,
            mentionedChannels = [],
            mentionedPartners = [],
            cannedResponseIds,
        } = {}
    ) {
        const message = await super.post(thread, body, {attachments,isNote,parentId,mentionedChannels,mentionedPartners,cannedResponseIds});
        if (thread.assistant_toggle_status === true) {
            thread.messages.sort((m1, m2) => m1.id - m2.id);
        }
        if (thread.composer){thread.composer.textInputContent = "";}
        let result_typing = false;
        if (thread.model == "discuss.channel") {
          result_typing = await this.rpc("/mail/typing_status", { channel_id: message.res_id, is_typing: true });
        }
        if (message && result_typing && thread.model == "discuss.channel") {
            const params = await this.getMessagePostParams({
                attachments,
                body,
                cannedResponseIds,
                isNote,
                mentionedChannels,
                mentionedPartners,
                thread,
            });
            Object.assign(params, {thread_id:message.res_id});
            try {
                await this.rpc("/mail/assistant_message_post", { message_text: body, params:params });
            } catch (_err) {
                console.log(_err);
            } finally {
                await this.rpc("/mail/typing_status", { channel_id: message.res_id, is_typing: false });
            }
        }
        return message;
    },
});