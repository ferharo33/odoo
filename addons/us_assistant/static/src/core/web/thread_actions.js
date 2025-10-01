/* @odoo-module */

import { threadActionsRegistry } from "@mail/core/common/thread_actions";

import { AssistantPanel } from "@us_assistant/discuss/core/common/assistant_panel";
import { _t } from "@web/core/l10n/translation";

threadActionsRegistry
    .add("assistant", {
        condition(component) {
            return(
                component.thread?.model === "discuss.channel" &&
                (!component.props.chatWindow || component.props.chatWindow.isOpen)
            );
        },
        component: AssistantPanel,
        icon: "fa fa-fw fa-lightbulb-o",
        iconLarge: "fa fa-fw fa-lg fa-lightbulb-o",
        name: _t("Assistant"),
        nameActive: _t("Asssistant"),
        sequence: 1,
        toggle: true,
    });

