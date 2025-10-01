/* @odoo-module */

import { Thread } from "@mail/core/common/thread_model";

import { assignDefined } from "@mail/utils/common/misc";
import { patch } from "@web/core/utils/patch";
import { Record } from "@mail/core/common/record";

patch(Thread.prototype, {
    setup() {
        super.setup(...arguments);
        this.assistantMembers = Record.many("ChannelMember", {
            compute() {
                return this.channelMembers.filter((member) => member?.persona?.is_assistant === true);
            },
        });
    },
    update(data) {
        super.update(data);
        assignDefined(this, data, ["assistant_toggle_status"]);
    },
    get correspondents() {
        return super.correspondents.filter(
            (correspondent) => !correspondent.persona?.is_assistant
        );
    },
});
