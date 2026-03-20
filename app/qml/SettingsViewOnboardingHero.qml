import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

SettingsSection {
    id: root

    required property var rootView

    visible: rootView.onboardingMode
    title: rootView.tr("把 Bao 准备好，然后直接开始聊天", "Set up Bao, then jump straight into chat")
    description: rootView.tr(
        "首次使用只保留一条主路径：选语言、连服务、定默认模型。页面里的每一块都围绕这三步，不再重复解释同一件事。",
        "First launch now follows one clear path: choose a language, connect one service, and confirm the default model. Every block on this page serves those three steps without repeating the same explanation."
    )

    ColumnLayout {
        width: parent.width
        spacing: spacingMd

        CalloutPanel {
            Layout.fillWidth: true
            radius: radiusLg
            padding: 18
            panelColor: isDark ? "#15110D" : "#FFF8F1"
            panelBorderColor: isDark ? "#26FFB33D" : "#18A8641F"
            overlayVisible: true
            overlayColor: isDark ? "#04FFFFFF" : "#08FFFFFF"
            sideGlowVisible: true
            sideGlowColor: isDark ? "#14FFB33D" : "#12FFC38A"
            sideGlowWidthFactor: 0.22
            accentBlobVisible: true
            accentBlobColor: isDark ? "#16FFB33D" : "#18FFB33D"
            accentBlobWidthFactor: 0.16

            ColumnLayout {
                width: parent.width
                spacing: spacingMd

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Rectangle {
                        implicitWidth: introBadge.implicitWidth + 18
                        implicitHeight: 26
                        radius: 13
                        color: isDark ? "#20FFB33D" : "#18FFB33D"
                        border.color: isDark ? "#2EFFB33D" : "#20A8641F"
                        border.width: 1

                        Text {
                            id: introBadge
                            anchors.centerIn: parent
                            text: rootView.tr("安装后首次配置", "First-run setup")
                            color: accent
                            font.pixelSize: typeMeta
                            font.weight: Font.DemiBold
                            font.letterSpacing: letterWide
                        }
                    }

                    Item { Layout.fillWidth: true }

                    Text {
                        text: rootView.onboardingCompletedCount + "/3"
                        color: textTertiary
                        font.pixelSize: typeLabel
                        font.weight: weightDemiBold
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: spacingLg

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        Text {
                            Layout.fillWidth: true
                            text: rootView.onboardingCurrentTitle
                            color: textPrimary
                            font.pixelSize: typeTitle
                            font.weight: Font.Bold
                            wrapMode: Text.WordWrap
                        }

                        Text {
                            Layout.fillWidth: true
                            text: rootView.onboardingCurrentBody
                            color: textSecondary
                            font.pixelSize: typeLabel
                            wrapMode: Text.WordWrap
                        }

                        Flow {
                            Layout.fillWidth: true
                            spacing: spacingSm

                            Repeater {
                                model: [
                                    rootView.tr("单一路径", "One clear path"),
                                    rootView.tr("支持 Win / mac", "Works cleanly on Win / mac"),
                                    rootView.tr("完成后直接进入聊天", "Drops into chat when done")
                                ]

                                delegate: Rectangle {
                                    required property string modelData

                                    implicitWidth: chipLabel.implicitWidth + 18
                                    implicitHeight: 26
                                    radius: 14
                                    color: isDark ? "#10FFFFFF" : "#0B000000"
                                    border.color: borderSubtle
                                    border.width: 1

                                    Text {
                                        id: chipLabel
                                        anchors.centerIn: parent
                                        text: modelData
                                        color: textSecondary
                                        font.pixelSize: typeMeta
                                        font.weight: Font.DemiBold
                                    }
                                }
                            }
                        }
                    }

                    Rectangle {
                        Layout.alignment: Qt.AlignVCenter
                        Layout.preferredWidth: 112
                        Layout.preferredHeight: 112
                        radius: 28
                        color: isDark ? "#12000000" : "#FFFFFFFF"
                        border.color: isDark ? "#18FFFFFF" : "#12000000"
                        border.width: 1

                        Rectangle {
                            width: 72
                            height: 72
                            radius: 24
                            anchors.centerIn: parent
                            color: isDark ? "#1AFFB33D" : "#16FFB33D"
                        }

                        Image {
                            anchors.centerIn: parent
                            width: 58
                            height: 58
                            source: "../resources/logo-circle.png"
                            fillMode: Image.PreserveAspectFit
                            smooth: true
                            antialiasing: true
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 6
                    radius: 3
                    color: isDark ? "#0EFFFFFF" : "#10000000"

                    Rectangle {
                        height: parent.height
                        width: parent.width * rootView.onboardingProgress
                        radius: parent.radius
                        color: accent
                        Behavior on width { NumberAnimation { duration: motionPanel; easing.type: easeEmphasis } }
                    }
                }
            }
        }

        Flow {
            Layout.fillWidth: true
            spacing: spacingSm

            Repeater {
                model: rootView.onboardingStepSpecs

                delegate: OnboardingStepCard {
                    required property int index
                    required property var modelData

                    width: rootView._flowItemWidth(parent.width, 210, 3, spacingSm)
                    stepNumber: index
                    title: modelData.title || ""
                    description: modelData.body || ""
                    ctaText: modelData.cta || ""
                    done: index < rootView.onboardingStepIndex
                    current: index === rootView.onboardingStepIndex
                    onClicked: rootView._openOnboardingStep(index)
                }
            }
        }
    }
}
