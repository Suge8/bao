import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

SettingsSection {
    id: root

    required property var rootView

    visible: !rootView.onboardingMode && rootView._activeTab === 2
    title: rootView.tr("配置文件", "Configuration")
    description: rootView.tr("Bao 的桌面配置保存在这里。需要手动编辑 JSONC 或排查问题时，可以直接打开目录。", "Bao stores its desktop configuration here. Open the folder when you need to edit the JSONC manually or inspect setup issues.")
    actionText: rootView.tr("打开配置目录", "Open Config Folder")
    actionEnabled: rootView.configFilePath !== ""
    actionHandler: function() { rootView.configService.openConfigDirectory() }

    ColumnLayout {
        width: parent.width
        spacing: 8

        Text {
            text: rootView.tr("当前配置文件", "Current config file")
            color: textSecondary
            font.pixelSize: 13
            font.weight: Font.DemiBold
        }

        Rectangle {
            Layout.fillWidth: true
            radius: radiusMd
            color: isDark ? "#0DFFFFFF" : "#06000000"
            border.color: borderSubtle
            border.width: 1
            implicitHeight: configPathText.implicitHeight + 24

            Text {
                id: configPathText
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: 12
                text: rootView.configFilePath
                color: textPrimary
                font.pixelSize: typeLabel
                wrapMode: Text.WrapAnywhere
            }
        }
    }
}
