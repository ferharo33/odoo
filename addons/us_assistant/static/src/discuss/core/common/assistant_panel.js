/* @odoo-module */

import { DateSection } from "@mail/core/common/date_section";
import { ActionPanel } from "@mail/discuss/core/common/action_panel";
import { AttachmentList } from "@mail/core/common/attachment_list";
import { _t } from "@web/core/l10n/translation";

import { Component, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { useSequential, useVisible } from "@mail/utils/common/hooks";

/**
 * @typedef {Object} Props
 * @property {import("models").Thread} thread
 */
export class AssistantPanel extends Component {
    static components = { ActionPanel };
    static props = ["thread"];
    static template = "us_assistant.AssistantPanel";

    setup() {
        this.store = useService("mail.store");
        this.rpc = useService("rpc");
        this.channelMemberService = useService("discuss.channel.member");
        this.threadService = useService("mail.thread");
        onWillStart(() => {
            this.threadService.fetchChannelMembers(this.props.thread);
        });
        onWillUpdateProps((nextProps) => {
            if (nextProps.thread.notEq(this.props.thread)) {
                this.threadService.fetchChannelMembers(nextProps.thread);
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
        if (member.persona.type === "guest") {
            return false;
        }
        return true;
    }

    openChatAvatar(member) {
        if (!this.canOpenChatWith(member)) {
            return;
        }
        this.threadService.openChat({ partnerId: member.persona.id });
    }

    async onChangeUseAssistant(ev) {
        const res = await this.rpc("/mail/channel_assistant_condition", {
            channel_id: this.props.thread.id,
            channel_toggle: !this.props.thread.assistant_toggle_status,
        });
        if (res.error) {
            this.env.services.notification.add(_t(res.error),{
                type: 'warning',
            });
            if (ev.target.checked) {
                ev.target.checked = false;
            }
        } else {
            this.props.thread.assistant_toggle_status = !this.props.thread.assistant_toggle_status;
        }

    }
}
