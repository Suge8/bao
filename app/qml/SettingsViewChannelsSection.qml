import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "SettingsViewHelp.js" as Help
import "SettingsViewChannelsData.js" as ChannelData

SettingsSection {
    id: root

    required property var rootView

    visible: !rootView.onboardingMode && rootView._activeTab === 1
    title: strings.section_channels
    description: rootView.tr("只有你真正要接入的平台才需要配置；不使用的渠道可以完全不动。", "Only configure the platforms you actually plan to use; unused channels can stay untouched.")
    actionText: strings.settings_save
    actionHandler: function() { rootView._saveSection(channelsSectionBody) }
    helpVisible: true
    helpHandler: function() {
        rootView._openHelp(rootView.tr("渠道接入说明", "Channel Setup Guide"), Help.channelSections(rootView))
    }

    ColumnLayout {
        id: channelsSectionBody
        anchors.left: parent.left
        anchors.right: parent.right
        spacing: 18

        Repeater {
            model: ChannelData.rows(rootView)

            delegate: ChannelRow {
                required property var modelData

                configService: rootView.configService
                Layout.fillWidth: true
                rowObjectName: String(modelData.rowObjectName || "")
                headerObjectName: String(modelData.headerObjectName || "")
                channelName: String(modelData.channelName || "")
                enabledPath: String(modelData.enabledPath || "")
                fields: modelData.fields || []
                advancedFields: modelData.advancedFields || []
            }
        }
    }
}
