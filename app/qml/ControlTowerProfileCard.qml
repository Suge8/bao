import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: card

    required property var workspaceRoot
    required property int minimumCardHeight
    required property var itemData
    required property bool isDark
    required property color textPrimary
    required property color textSecondary
    required property color textTertiary
    required property color tileFill
    required property color tileHover
    required property color tileActive
    required property color actionAccent
    required property color actionCurrentHoverFill
    required property color statusSuccess
    required property color statusError
    required property real motionFast
    required property int easeStandard
    required property int typeBody
    required property int typeCaption
    required property int weightBold
    required property int weightMedium
    readonly property string profileId: String(itemData.id || "")
    readonly property string displayName: String(itemData.displayName || "")
    readonly property string avatarSource: String(itemData.avatarSource || "")
    readonly property string statusSummary: String(itemData.statusSummary || "")
    readonly property var channelKeys: itemData.channelKeys || []
    readonly property int attentionCount: Number(itemData.attentionCount || 0)
    readonly property int totalSessionCount: Number(itemData.totalSessionCount || 0)
    readonly property int workingCount: Number(itemData.workingCount || 0)
    readonly property int automationCount: Number(itemData.automationCount || 0)
    readonly property int totalChildSessionCount: Number(itemData.totalChildSessionCount || 0)
    readonly property bool isHubLive: Boolean(itemData.isHubLive)
    readonly property bool isSelected: workspaceRoot.profileIsSelected(itemData)
    readonly property bool isCurrent: workspaceRoot.profileIsCurrent(itemData)
    readonly property string accentKey: workspaceRoot.profileAccentKey(itemData)
    readonly property color accentColor: workspaceRoot.accentColor(accentKey)
    readonly property string primaryChannelKey: channelKeys.length > 0 ? String(channelKeys[0] || "") : "desktop"
    readonly property string statusKey: attentionCount > 0 ? "error" : (isHubLive ? "running" : "idle")
    readonly property string timeLabel: workspaceRoot.profileTimeLabel(itemData)
    readonly property string actionText: workspaceRoot.profileActionText(itemData)
    readonly property string channelsLabel: workspaceRoot.isChinese ? "渠道" : "Channels"
    readonly property string sessionsLabel: workspaceRoot.isChinese ? "会话" : "Sessions"
    readonly property string workingLabel: workspaceRoot.isChinese ? "工作中" : "Working"
    readonly property string automationLabel: workspaceRoot.isChinese ? "自动化" : "Automation"
    readonly property string childSessionLabel: workspaceRoot.isChinese
        ? totalChildSessionCount + " 个子代理"
        : totalChildSessionCount + " subagents"
    readonly property string attentionLabel: workspaceRoot.isChinese
        ? attentionCount + " 个待处理"
        : attentionCount + " need review"
    readonly property int cardPadding: 16
    readonly property int cardSpacing: 12

    objectName: "profileCard_" + profileId
    width: ListView.view ? ListView.view.width : 0
    height: implicitHeight
    implicitHeight: Math.max(minimumCardHeight, cardContent.implicitHeight + cardPadding * 2)
    radius: 22
    color: isSelected
           ? tileActive
           : (profileMouse.containsMouse ? tileHover : tileFill)
    border.width: isSelected ? 1.5 : 1
    border.color: isSelected
                  ? accentColor
                  : (isDark ? "#16FFFFFF" : "#12000000")

    Behavior on color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }
    Behavior on border.color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }

    MouseArea {
        id: profileMouse
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: workspaceRoot.selectProfile(profileId)
    }

    ColumnLayout {
        id: cardContent
        anchors.fill: parent
        anchors.margins: cardPadding
        spacing: cardSpacing

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            WorkerToken {
                avatarSource: card.avatarSource
                variant: "primary"
                ringColor: accentColor
                glyphSource: workspaceRoot.channelIconSource(primaryChannelKey)
                statusKey: card.statusKey
                active: isSelected
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Text {
                        Layout.fillWidth: true
                        text: displayName
                        color: textPrimary
                        font.pixelSize: typeBody
                        font.weight: weightBold
                        textFormat: Text.PlainText
                        elide: Text.ElideRight
                    }

                    Text {
                        visible: timeLabel !== ""
                        text: timeLabel
                        Layout.maximumWidth: Math.max(72, cardContent.width * 0.32)
                        color: textTertiary
                        font.pixelSize: typeCaption
                        font.weight: weightMedium
                        textFormat: Text.PlainText
                        elide: Text.ElideRight
                    }

                    PillActionButton {
                        objectName: "profileActivateButton_" + profileId
                        text: actionText
                        buttonEnabled: !isCurrent
                        fillColor: isCurrent ? "transparent" : card.actionAccent
                        hoverFillColor: isCurrent ? card.actionCurrentHoverFill : card.accentColor
                        outlineColor: isCurrent ? card.statusSuccess : card.actionAccent
                        hoverOutlineColor: isCurrent ? card.statusSuccess : card.accentColor
                        textColor: isCurrent ? card.statusSuccess : "#FFFFFFFF"
                        outlined: isCurrent
                        horizontalPadding: 16
                        minHeight: 28
                        onClicked: workspaceRoot.activateProfile(profileId)
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: statusSummary
                    color: textSecondary
                    font.pixelSize: typeCaption
                    font.weight: weightMedium
                    textFormat: Text.PlainText
                    wrapMode: Text.WordWrap
                    maximumLineCount: 2
                    elide: Text.ElideRight
                }
            }
        }

        Flow {
            id: metricsFlow
            objectName: "profileMetrics_" + profileId
            Layout.fillWidth: true
            spacing: 10

            ControlTowerMetricBadge {
                valueText: String(totalSessionCount)
                labelText: sessionsLabel
                isDark: card.isDark
                textPrimary: card.textPrimary
                textSecondary: card.textSecondary
                fontPixelSize: card.typeCaption
                weightBold: card.weightBold
                weightMedium: card.weightMedium
                maximumWidth: metricsFlow.width
            }

            ControlTowerMetricBadge {
                valueText: String(workingCount)
                labelText: workingLabel
                isDark: card.isDark
                textPrimary: card.textPrimary
                textSecondary: card.textSecondary
                fontPixelSize: card.typeCaption
                weightBold: card.weightBold
                weightMedium: card.weightMedium
                maximumWidth: metricsFlow.width
            }

            ControlTowerMetricBadge {
                valueText: String(automationCount)
                labelText: automationLabel
                isDark: card.isDark
                textPrimary: card.textPrimary
                textSecondary: card.textSecondary
                fontPixelSize: card.typeCaption
                weightBold: card.weightBold
                weightMedium: card.weightMedium
                maximumWidth: metricsFlow.width
            }
        }

        Flow {
            id: metaFlow
            objectName: "profileMeta_" + profileId
            Layout.fillWidth: true
            spacing: 8

            Text {
                visible: channelKeys.length > 0
                text: channelsLabel
                color: textTertiary
                font.pixelSize: typeCaption
                font.weight: weightMedium
                textFormat: Text.PlainText
            }

            Repeater {
                model: channelKeys

                delegate: Rectangle {
                    required property var modelData
                    readonly property string channelKey: String(modelData || "")
                    readonly property color channelAccent: workspaceRoot.accentColor(channelKey)
                    width: 24
                    height: 24
                    radius: 12
                    color: Qt.rgba(channelAccent.r, channelAccent.g, channelAccent.b, isDark ? 0.18 : 0.12)
                    border.width: 1
                    border.color: channelAccent

                    AppIcon {
                        anchors.centerIn: parent
                        width: 14
                        height: 14
                        source: workspaceRoot.channelIconSource(channelKey)
                        sourceSize: Qt.size(width, height)
                    }

                    ToolTip.visible: channelMouse.containsMouse
                    ToolTip.text: workspaceRoot.channelLabel(channelKey)

                    MouseArea {
                        id: channelMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        acceptedButtons: Qt.NoButton
                    }
                }
            }

            ControlTowerInfoChip {
                visible: totalChildSessionCount > 0
                chipId: profileId + "_children"
                labelText: childSessionLabel
                isDark: card.isDark
                fillColor: card.isDark ? "#18120E" : "#FFF6EA"
                borderColor: workspaceRoot.accentColor("subagent")
                textColor: card.textSecondary
                fontPixelSize: card.typeCaption
                fontWeight: card.weightMedium
                maximumWidth: metaFlow.width
            }

            ControlTowerInfoChip {
                visible: attentionCount > 0
                chipId: profileId + "_attention"
                labelText: attentionLabel
                isDark: card.isDark
                fillColor: card.isDark ? "#24130F" : "#FFF1E8"
                borderColor: card.statusError
                textColor: card.statusError
                fontPixelSize: card.typeCaption
                fontWeight: card.weightMedium
                maximumWidth: metaFlow.width
            }
        }
    }
}
