/** @odoo-module */

import { Thread } from "@mail/core/common/thread_model";
import { patch } from "@web/core/utils/patch";

patch(Thread.prototype, {
    async post(body, postData = {}, extraData = {}) {
        const assistantPostData = {
            attachments: postData.attachments ? [...postData.attachments] : [],
            cannedResponseIds: postData.cannedResponseIds,
            emailAddSignature: postData.emailAddSignature,
            isNote: postData.isNote,
            mentionedChannels: postData.mentionedChannels ? [...postData.mentionedChannels] : [],
            mentionedPartners: postData.mentionedPartners ? [...postData.mentionedPartners] : [],
        };
        const message = await super.post(body, postData, extraData);
        if (!message) {
            return message;
        }
        if (this.assistant_toggle_status === true) {
            this.messages.sort((m1, m2) => m1.id - m2.id);
        }
        if (this.composer && !this.composer.message) {
            this.composer.text = "";
        }
        if (this.model !== "discuss.channel") {
            return message;
        }
        const rpc = this.store.env.services.rpc;
        let typingResult = false;
        try {
            typingResult = await rpc("/mail/typing_status", {
                channel_id: message.res_id,
                is_typing: true,
            });
        } catch (err) {
            console.error(err);
        }
        if (typingResult) {
            const params = await this.store.getMessagePostParams({
                body,
                postData: assistantPostData,
                thread: this,
            });
            Object.assign(params, extraData, { thread_id: message.res_id });
            try {
                await rpc("/mail/assistant_message_post", {
                    message_text: body,
                    params,
                });
            } catch (err) {
                console.error(err);
            } finally {
                try {
                    await rpc("/mail/typing_status", {
                        channel_id: message.res_id,
                        is_typing: false,
                    });
                } catch (err) {
                    console.error(err);
                }
            }
        }
        return message;
    },
});