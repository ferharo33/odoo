/* @odoo-module */

import { ActionPanel } from "@mail/discuss/core/common/action_panel";
import { _t } from "@web/core/l10n/translation";

import { Component, onWillStart, onWillUpdateProps, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

/**
 * @typedef {Object} Props
 * @property {import("models").Thread} thread
 */
export class AssistantPanel extends Component {
    static components = { ActionPanel };
    static props = ["thread"];
    static template = "us_assistant.AssistantPanel";

    setup() {
        this.store = useState(useService("mail.store"));
        this.rpc = useService("rpc");
        onWillStart(() => {
            if (this.props.thread.fetchMembersState === "not_fetched") {
                this.props.thread.fetchChannelMembers();
            }
        });
        onWillUpdateProps((nextProps) => {
            if (nextProps.thread.fetchMembersState === "not_fetched") {
                nextProps.thread.fetchChannelMembers();
            }
        });
    }

    get assistantMembers() {
        return this.props.thread.assistantMembers;
    }

    canOpenChatWith(member) {
        if (this.store.inPublicPage) {
            return false;
        }
        if (member.persona?.eq(this.store.self)) {
            return false;
        }
        if (member.persona?.type === "guest") {
            return false;
        }
        return true;
    }

    openChatAvatar(member) {
        if (!this.canOpenChatWith(member)) {
            return;
        }
        this.store.openChat({ partnerId: member.persona.id });
    }

    async onChangeUseAssistant(ev) {
        const res = await this.rpc("/mail/channel_assistant_condition", {
            channel_id: this.props.thread.id,
            channel_toggle: !this.props.thread.assistant_toggle_status,
        });
        if (res.error) {
            this.env.services.notification.add(_t(res.error), {
                type: "warning",
            });
            if (ev.target.checked) {
                ev.target.checked = false;
            }
        } else {
            this.props.thread.assistant_toggle_status = !this.props.thread.assistant_toggle_status;
        }
    }
}
