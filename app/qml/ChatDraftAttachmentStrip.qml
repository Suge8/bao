import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    objectName: "attachmentStrip"

    property var chatService: null
    property bool hasDraftAttachments: false

    width: parent ? parent.width : 0
    height: hasDraftAttachments ? 72 : 0
    radius: 22
    color: isDark ? "#E623170F" : "#F7FFFFFF"
    border.width: 1
    border.color: chipHover.containsMouse ? accent : borderSubtle
    opacity: hasDraftAttachments ? 1.0 : 0.0
    clip: true
    visible: opacity > 0
    Behavior on height { NumberAnimation { duration: motionUi; easing.type: easeStandard } }
    Behavior on opacity { NumberAnimation { duration: motionFast; easing.type: easeStandard } }
    Behavior on border.color { ColorAnimation { duration: motionFast; easing.type: easeStandard } }

    HoverHandler {
        id: chipHover
        readonly property bool containsMouse: hovered
    }

    Rectangle {
        anchors.fill: parent
        radius: parent.radius
        color: "transparent"
        border.width: 1
        border.color: isDark ? "#15FFFFFF" : "#22FFFFFF"
        opacity: root.hasDraftAttachments ? 1.0 : 0.0
    }

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: 28
        radius: parent.radius
        gradient: Gradient {
            GradientStop { position: 0.0; color: isDark ? "#20FFFFFF" : "#D9FFFFFF" }
            GradientStop { position: 1.0; color: "#00FFFFFF" }
        }
        opacity: 0.55
    }

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 20
        radius: parent.radius
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#00000000" }
            GradientStop { position: 1.0; color: "#99000000" }
        }
        opacity: isDark ? 0.18 : 0.08
    }

    ListView {
        id: attachmentList
        objectName: "attachmentList"
        anchors.fill: parent
        anchors.margins: 8
        orientation: ListView.Horizontal
        spacing: 8
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        model: root.chatService ? root.chatService.draftAttachments : null
        add: Transition {
            ParallelAnimation {
                NumberAnimation {
                    property: "opacity"
                    from: 0.0
                    to: 1.0
                    duration: motionUi
                    easing.type: easeStandard
                }
                NumberAnimation {
                    property: "scale"
                    from: 0.94
                    to: 1.0
                    duration: motionUi + 20
                    easing.type: easeEmphasis
                }
                NumberAnimation {
                    property: "x"
                    from: ViewTransition.item.x + 8
                    to: ViewTransition.item.x
                    duration: motionUi
                    easing.type: easeEmphasis
                }
            }
        }
        addDisplaced: Transition {
            NumberAnimation {
                properties: "x"
                duration: motionUi
                easing.type: easeEmphasis
            }
        }
        removeDisplaced: Transition {
            NumberAnimation {
                properties: "x"
                duration: motionUi
                easing.type: easeEmphasis
            }
        }

        delegate: AttachmentChip {
            required property int index
            required property string fileName
            required property string fileSizeLabel
            required property string previewUrl
            required property bool isImage
            required property string extensionLabel

            fileName: model.fileName ?? ""
            fileSizeLabel: model.fileSizeLabel ?? ""
            previewUrl: model.previewUrl ?? ""
            isImage: Boolean(model.isImage)
            extensionLabel: model.extensionLabel ?? "FILE"
            removable: true
            removeAction: function() {
                if (root.chatService)
                    root.chatService.removeDraftAttachment(index)
            }
        }
    }
}
