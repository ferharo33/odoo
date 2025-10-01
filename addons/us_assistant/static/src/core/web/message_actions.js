/* @odoo-module */

import { messageActionsRegistry } from "@mail/core/common/message_actions";
import { _t } from "@web/core/l10n/translation";

messageActionsRegistry
    .add("assistant-hint", {
        condition: (component) => component.canAssistantHint,
        icon: "fa-lightbulb-o",
        title: _t("Assistant Hint"),
        onClick: (component) => component.onClickAssistantEdit(),
        sequence: 90,
    });
