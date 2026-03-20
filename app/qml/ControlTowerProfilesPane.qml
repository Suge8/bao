import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: pane
    objectName: "controlTowerProfilesPane"

    required property var workspaceRoot
    required property var profilesModel
    required property int profileCount
    required property bool compactLayout
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
    readonly property int profileListSpacing: compactLayout ? 12 : 14
    readonly property int minimumProfileCardHeight: compactLayout ? 148 : 160
    readonly property int profileListCacheItems: 5
    readonly property int profileListCacheBuffer: (minimumProfileCardHeight + profileListSpacing) * profileListCacheItems
    readonly property int compactPaneHeight: 338
    readonly property string profileCountLabel: String(
        workspaceRoot && workspaceRoot.strings
        ? (workspaceRoot.strings.profile_count_badge || "%1")
        : "%1"
    ).replace("%1", String(profileCount))

    SplitView.preferredWidth: 296
    SplitView.minimumWidth: 272
    SplitView.maximumWidth: 328
    SplitView.preferredHeight: compactLayout ? compactPaneHeight : 0
    SplitView.minimumHeight: compactLayout ? compactPaneHeight : 0
    SplitView.maximumHeight: compactLayout ? compactPaneHeight : 0
    SplitView.fillWidth: compactLayout
    SplitView.fillHeight: !compactLayout

    ColumnLayout {
        anchors.fill: parent
        spacing: 14

        RowLayout {
            Layout.fillWidth: true

            Text {
                objectName: "controlTowerProfilesTitle"
                text: workspaceRoot.isChinese ? "分身列表" : "Profiles"
                color: textPrimary
                font.pixelSize: typeBody
                font.weight: weightBold
            }

            Item { Layout.fillWidth: true }

            ProfileCountBadge {
                count: profileCount
                labelText: pane.profileCountLabel
                isDark: isDark
                borderColor: workspaceRoot.sectionBorder
                textColor: textSecondary
                fontPixelSize: typeCaption
                fontWeight: weightMedium
            }
        }

        ListView {
            id: profileList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: pane.profileListSpacing
            reuseItems: true
            cacheBuffer: pane.profileListCacheBuffer
            model: profilesModel
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

            delegate: ControlTowerProfileCard {
                required property var modelData
                minimumCardHeight: pane.minimumProfileCardHeight
                workspaceRoot: pane.workspaceRoot
                itemData: modelData
                isDark: pane.isDark
                textPrimary: pane.textPrimary
                textSecondary: pane.textSecondary
                textTertiary: pane.textTertiary
                tileFill: pane.tileFill
                tileHover: pane.tileHover
                tileActive: pane.tileActive
                actionAccent: pane.actionAccent
                actionCurrentHoverFill: pane.actionCurrentHoverFill
                statusSuccess: pane.statusSuccess
                statusError: pane.statusError
                motionFast: pane.motionFast
                easeStandard: pane.easeStandard
                typeBody: pane.typeBody
                typeCaption: pane.typeCaption
                weightBold: pane.weightBold
                weightMedium: pane.weightMedium
            }
        }
    }
}
