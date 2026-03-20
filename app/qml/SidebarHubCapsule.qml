import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    objectName: "hubCapsule"

    required property var sidebarRoot

    Layout.fillWidth: true
    Layout.leftMargin: 16
    Layout.rightMargin: 16
    Layout.topMargin: 16
    implicitHeight: sidebarRoot.sizeCapsuleHeight
    radius: height / 2
    visible: sidebarRoot.hasChatService
    activeFocusOnTab: true

    property string currentState: sidebarRoot.currentState
    property bool isRunning: sidebarRoot.isRunning
    property bool isStarting: sidebarRoot.isStarting
    property bool isError: sidebarRoot.isError
    property bool isIdleVisual: !isRunning && !isStarting && !isError
    property string previousState: currentState
    property bool isHovered: hoverArea.containsMouse
    property bool isPressed: hoverArea.pressed
    property real actionPulse: 0.0
    property real iconLift: 0.0
    property real iconPulse: 0.0
    property real iconTurn: 0.0
    property real pacmanMouth: 0.2
    property real pacmanPhase: 0.0
    readonly property int stateTransitionDuration: sidebarRoot.motionPanel + 40
    readonly property real pacmanMouthRest: 0.2
    readonly property real pacmanMouthWide: 0.34
    readonly property real pacmanMouthClosed: 0.06
    readonly property var hubStateSpecs: ({
        "running": { "surfaceColor": sidebarRoot.hubSurfaceRunningTop, "statusColor": sidebarRoot.hubTextRunning, "actionColor": sidebarRoot.statusSuccess, "dotColor": sidebarRoot.statusSuccess, "primaryLabel": sidebarRoot.strings.hub_running, "actionIconSource": "" },
        "error": { "surfaceColor": sidebarRoot.hubSurfaceErrorTop, "statusColor": sidebarRoot.statusError, "actionColor": sidebarRoot.statusError, "dotColor": sidebarRoot.statusError, "primaryLabel": sidebarRoot.strings.hub_error, "actionIconSource": "../resources/icons/hub-error.svg" },
        "starting": { "surfaceColor": sidebarRoot.hubSurfaceStartingTop, "statusColor": sidebarRoot.hubTextStarting, "actionColor": sidebarRoot.statusWarning, "dotColor": sidebarRoot.statusWarning, "primaryLabel": sidebarRoot.strings.hub_starting, "actionIconSource": "../resources/icons/hub-starting.svg" },
        "idle": { "surfaceColor": sidebarRoot.hubSurfaceIdleTop, "statusColor": sidebarRoot.hubTextIdle, "actionColor": sidebarRoot.accent, "dotColor": sidebarRoot.accent, "primaryLabel": sidebarRoot.strings.button_start_hub, "actionIconSource": "../resources/icons/hub-idle.svg" }
    })
    readonly property var stateSpec: hubStateSpecs[currentState] || hubStateSpecs.idle
    readonly property bool useRunningPacman: currentState === "running"
    property string displayedPrimaryLabel: primaryLabel
    property string outgoingPrimaryLabel: ""
    property real primaryLabelTransition: 1.0
    property color surfaceColor: stateSpec.surfaceColor
    property color statusColor: stateSpec.statusColor
    property color actionColor: stateSpec.actionColor
    property color dotColor: stateSpec.dotColor
    property string primaryLabel: stateSpec.primaryLabel
    property string actionIconSource: stateSpec.actionIconSource
    property string detailText: sidebarRoot.hasChatService ? (sidebarRoot.chatService.hubDetail || "") : ""
    property var hubChannels: sidebarRoot.hasChatService ? (sidebarRoot.chatService.hubChannels || []) : []
    property bool hasErrorDetail: sidebarRoot.hasChatService ? Boolean(sidebarRoot.chatService.hubDetailIsError) : false
    z: 6

    function resetVisualState() {
        actionPulse = 0.0
        iconLift = 0.0
        iconPulse = 0.0
        iconTurn = 0.0
        pacmanMouth = pacmanMouthRest
        pacmanPhase = 0.0
    }

    function transitionPrimaryLabel(nextLabel) {
        if (displayedPrimaryLabel === nextLabel)
            return
        outgoingPrimaryLabel = displayedPrimaryLabel
        displayedPrimaryLabel = nextLabel
        primaryLabelTransition = 0.0
        primaryLabelTransitionAnim.restart()
    }

    function handoffVisualState() {
        if (previousState === currentState)
            return
        if (previousState === "starting" && currentState === "running") {
            actionPulse = Math.max(actionPulse, 0.03)
            iconLift = -0.18
            iconPulse = Math.max(iconPulse, 0.05)
            iconTurn = 2.2
            pacmanMouth = 0.26
        } else if (previousState === "starting") {
            actionPulse = Math.max(actionPulse, 0.02)
            iconPulse = Math.max(iconPulse, 0.03)
            iconLift = 0.0
            iconTurn = 0.0
        } else if (currentState === "starting") {
            actionPulse = Math.max(actionPulse, 0.04)
            iconPulse = Math.max(iconPulse, 0.04)
        } else {
            resetVisualState()
        }
        previousState = currentState
    }

    function triggerHubAction() {
        if (!sidebarRoot.hasChatService || isStarting)
            return
        if (isRunning)
            sidebarRoot.chatService.stop()
        else
            sidebarRoot.chatService.start()
    }

    onCurrentStateChanged: handoffVisualState()
    onPrimaryLabelChanged: transitionPrimaryLabel(primaryLabel)
    Component.onCompleted: displayedPrimaryLabel = primaryLabel
    Keys.onPressed: function(event) {
        if (event.key === Qt.Key_Space || event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
            root.triggerHubAction()
            event.accepted = true
        }
    }

    color: surfaceColor
    border.width: activeFocus ? 1.5 : 0
    border.color: activeFocus ? sidebarRoot.borderFocus : "transparent"
    scale: isPressed ? 0.985 : (isHovered ? sidebarRoot.motionHoverScaleSubtle : 1.0)
    Behavior on actionPulse { NumberAnimation { duration: stateTransitionDuration; easing.type: sidebarRoot.easeSoft } }
    Behavior on iconLift { NumberAnimation { duration: stateTransitionDuration; easing.type: sidebarRoot.easeSoft } }
    Behavior on iconPulse { NumberAnimation { duration: stateTransitionDuration; easing.type: sidebarRoot.easeSoft } }
    Behavior on iconTurn { NumberAnimation { duration: stateTransitionDuration; easing.type: sidebarRoot.easeSoft } }
    Behavior on color { ColorAnimation { duration: stateTransitionDuration; easing.type: sidebarRoot.easeStandard } }
    Behavior on border.color { ColorAnimation { duration: stateTransitionDuration; easing.type: sidebarRoot.easeStandard } }
    Behavior on scale { NumberAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeEmphasis } }

    NumberAnimation {
        id: primaryLabelTransitionAnim
        target: root
        property: "primaryLabelTransition"
        from: 0.0
        to: 1.0
        duration: stateTransitionDuration
        easing.type: sidebarRoot.easeSoft
    }

    Item {
        anchors.fill: parent

        SidebarHubAction {
            id: hubAction
            anchors.right: parent.right
            anchors.rightMargin: 22
            anchors.verticalCenter: parent.verticalCenter
            sidebarRoot: root.sidebarRoot
            capsule: root
        }

        Column {
            anchors.left: parent.left
            anchors.leftMargin: 22
            anchors.right: hubAction.left
            anchors.rightMargin: 22
            anchors.verticalCenter: parent.verticalCenter
            spacing: 1

            Row {
                id: hubSecondaryRow
                objectName: "hubSecondaryRow"
                spacing: 7
                opacity: 0.58 + root.primaryLabelTransition * 0.14
                y: 2 * (1.0 - root.primaryLabelTransition)

                Behavior on opacity { NumberAnimation { duration: root.stateTransitionDuration; easing.type: sidebarRoot.easeSoft } }
                Behavior on y { NumberAnimation { duration: root.stateTransitionDuration; easing.type: sidebarRoot.easeSoft } }

                Rectangle {
                    id: gwDot
                    width: 6
                    height: 6
                    radius: 3
                    anchors.verticalCenter: parent.verticalCenter
                    color: root.dotColor
                    Behavior on color { ColorAnimation { duration: root.stateTransitionDuration; easing.type: sidebarRoot.easeStandard } }
                    Behavior on opacity { NumberAnimation { duration: sidebarRoot.motionUi + 20; easing.type: sidebarRoot.easeSoft } }
                    Behavior on scale { NumberAnimation { duration: sidebarRoot.motionUi + 20; easing.type: sidebarRoot.easeSoft } }
                    SequentialAnimation on scale {
                        running: root.isRunning
                        loops: Animation.Infinite
                        NumberAnimation { to: sidebarRoot.motionDotPulseScaleMax; duration: sidebarRoot.motionBreath - sidebarRoot.motionFast; easing.type: sidebarRoot.easeSoft }
                        NumberAnimation { to: 1.0; duration: sidebarRoot.motionBreath - sidebarRoot.motionFast; easing.type: sidebarRoot.easeSoft }
                    }
                    SequentialAnimation {
                        running: root.isStarting
                        loops: Animation.Infinite
                        NumberAnimation { target: gwDot; property: "opacity"; from: 1.0; to: 0.42; duration: sidebarRoot.motionAmbient; easing.type: sidebarRoot.easeSoft }
                        NumberAnimation { target: gwDot; property: "opacity"; from: 0.42; to: 1.0; duration: sidebarRoot.motionAmbient; easing.type: sidebarRoot.easeSoft }
                    }
                    SequentialAnimation {
                        running: root.isError
                        loops: Animation.Infinite
                        NumberAnimation { target: gwDot; property: "opacity"; from: 1.0; to: sidebarRoot.motionDotPulseMinOpacity; duration: sidebarRoot.motionStatusPulse; easing.type: sidebarRoot.easeSoft }
                        NumberAnimation { target: gwDot; property: "opacity"; from: sidebarRoot.motionDotPulseMinOpacity; to: 1.0; duration: sidebarRoot.motionStatusPulse; easing.type: sidebarRoot.easeSoft }
                    }
                }

                Text {
                    text: sidebarRoot.strings.chat_hub
                    color: root.statusColor
                    font.pixelSize: sidebarRoot.typeCaption
                    font.weight: sidebarRoot.weightDemiBold
                    font.letterSpacing: sidebarRoot.letterWide
                    Behavior on color { ColorAnimation { duration: root.stateTransitionDuration; easing.type: sidebarRoot.easeStandard } }
                }
            }

            Item {
                objectName: "hubPrimaryLabelWrap"
                width: parent.width
                implicitHeight: Math.max(outgoingLabel.implicitHeight, incomingLabel.implicitHeight)
                height: implicitHeight

                Text {
                    id: outgoingLabel
                    objectName: "hubPrimaryLabelOutgoing"
                    width: parent.width
                    visible: root.outgoingPrimaryLabel !== "" && opacity > 0.01
                    text: root.outgoingPrimaryLabel
                    color: root.statusColor
                    font.pixelSize: sidebarRoot.typeButton + 1
                    font.weight: sidebarRoot.weightBold
                    font.letterSpacing: sidebarRoot.letterTight
                    opacity: 1.0 - root.primaryLabelTransition
                    y: -4 * root.primaryLabelTransition
                    Behavior on color { ColorAnimation { duration: root.stateTransitionDuration; easing.type: sidebarRoot.easeStandard } }
                }

                Text {
                    id: incomingLabel
                    objectName: "hubPrimaryLabelIncoming"
                    width: parent.width
                    text: root.displayedPrimaryLabel
                    color: root.statusColor
                    font.pixelSize: sidebarRoot.typeButton + 1
                    font.weight: sidebarRoot.weightBold
                    font.letterSpacing: sidebarRoot.letterTight
                    opacity: root.primaryLabelTransition
                    y: 4 * (1.0 - root.primaryLabelTransition)
                    Behavior on color { ColorAnimation { duration: root.stateTransitionDuration; easing.type: sidebarRoot.easeStandard } }
                }
            }
        }

        HubStatusOrb {
            id: hubStatusOrb
            objectName: "hubStatusOrb"
            anchors.fill: parent
            channels: root.hubChannels
            detailText: root.detailText
            detailIsError: root.hasErrorDetail
            parentHovered: hoverArea.containsMouse
            parentFocused: root.activeFocus
            isDark: sidebarRoot.uiIsDark
            bgCanvas: sidebarRoot.uiBgCanvas
            textSecondary: sidebarRoot.uiTextSecondary
            textPrimary: sidebarRoot.uiTextPrimary
            statusSuccess: sidebarRoot.uiStatusSuccess
            statusError: sidebarRoot.uiStatusError
            statusWarning: sidebarRoot.uiStatusWarning
            typeCaption: sidebarRoot.typeCaption
            weightBold: sidebarRoot.weightBold
            weightMedium: sidebarRoot.weightMedium
            motionFast: sidebarRoot.motionFast
            motionUi: sidebarRoot.motionUi
            channelIconSource: sidebarRoot.channelIconSource
            channelFilledIconSource: sidebarRoot.channelFilledIconSource
            channelAccent: sidebarRoot.channelAccent
        }
    }

    MouseArea {
        id: hoverArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: root.isStarting ? Qt.ArrowCursor : Qt.PointingHandCursor
        onClicked: {
            root.forceActiveFocus()
            root.triggerHubAction()
        }
    }
}
