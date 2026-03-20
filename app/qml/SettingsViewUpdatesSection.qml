import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

SettingsSection {
    id: root

    required property var rootView

    visible: !rootView.onboardingMode && rootView._activeTab === 2
    title: strings.section_updates
    description: rootView.tr("这里控制桌面应用自己的更新检查，不影响聊天功能。", "These options control desktop app updates and do not affect chat behavior.")
    actionText: strings.settings_save
    actionHandler: function() {
        rootView._saveSection(updatesSectionBody, {"ui.update.autoCheck": rootView._updateAutoCheckDraft}, function() {
            rootView._reloadLocalState()
        })
    }

    RowLayout {
        id: updatesSectionBody
        width: parent.width
        Layout.fillWidth: true
        spacing: 14

        RowLayout {
            spacing: 10

            Text {
                text: strings.update_auto_check
                color: textSecondary
                font.pixelSize: typeLabel
                font.weight: weightMedium
            }

            ToggleSwitch {
                checked: rootView._updateAutoCheckDraft
                onToggled: function(checked) { rootView._updateAutoCheckDraft = checked }
            }
        }

        Item {
            Layout.fillWidth: true
        }

        RowLayout {
            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
            spacing: 12

            Text {
                text: strings.update_current_version + " " + (rootView.updateService ? rootView.updateService.currentVersion : "")
                color: textSecondary
                font.pixelSize: typeMeta
                verticalAlignment: Text.AlignVCenter
            }

            AsyncActionButton {
                text: rootView.updateActionText
                busy: rootView.updateBusy
                buttonEnabled: rootView.updateBridge !== null
                minHeight: 30
                horizontalPadding: 28
                onClicked: {
                    rootView._pendingManualUpdateCheck = true
                    rootView.updateBridge.checkRequested()
                }
            }
        }
    }
}
