import QtQuick 2.15
import QtQuick.Controls 2.15
import "HubStatusOrbLogic.js" as Logic

Item {
    id: root

    property var channels: []
    property string detailText: ""
    property bool detailIsError: false
    property bool parentHovered: false
    property bool parentFocused: false
    property bool isDark: true
    property color bgCanvas: "transparent"
    property color textSecondary: "#FFFFFF"
    property color textPrimary: "#FFFFFF"
    property color statusSuccess: "#22C55E"
    property color statusError: "#EF4444"
    property color statusWarning: "#F59E0B"
    property int typeCaption: 12
    property int weightBold: Font.Bold
    property int weightMedium: Font.Medium
    property int motionFast: 160
    property int motionUi: 200
    property var channelIconSource: null
    property var channelFilledIconSource: null
    property var channelAccent: null

    readonly property int channelCount: channels && channels.length !== undefined ? channels.length : 0
    readonly property bool hasChannels: channelCount > 0
    readonly property bool hasDetail: detailText !== "" || hasChannels
    readonly property bool hasErrorState: detailIsError || hasState("error")
    readonly property bool hasStartingState: hasState("starting")
    readonly property bool hasRunningState: hasState("running")
    readonly property var orbChannels: buildOrbChannels()
    readonly property int overflowCount: hasChannels ? Math.max(0, channelCount - 2) : 0
    readonly property bool showBubble: hasDetail && (parentHovered || orbHoverProxy.containsMouse || bubbleHoverProxy.containsMouse)
    readonly property real orbMinWidth: 30
    readonly property real orbPaddingX: hasChannels ? 4 : 0
    readonly property color orbSurface: Logic.orbSurface(root)
    readonly property color bubbleSurface: Logic.bubbleSurface(root)
    readonly property color bubbleBorder: Logic.bubbleBorder(root)
    readonly property string bubbleHeading: detailText !== "" ? detailText : defaultSummary()
    readonly property color bubbleHeadingColor: hasErrorState ? statusError : textPrimary
    readonly property real bubbleHeadingSize: hasErrorState ? typeCaption + 1 : typeCaption
    readonly property int bubbleHeadingWeight: hasErrorState ? weightBold : weightMedium
    readonly property real bubbleHeadingOpacity: hasErrorState ? 1.0 : 0.94
    readonly property real bubbleBodyWidth: hasChannels ? 168 : headingMeasureProxy.implicitWidth
    readonly property color chipSurface: isDark ? Qt.rgba(1, 1, 1, 0.08) : Qt.rgba(1, 1, 1, 0.92)
    readonly property color rowIconSurface: isDark ? Qt.rgba(1, 1, 1, 0.08) : Qt.rgba(1, 1, 1, 0.90)
    readonly property var orbHoverProxy: orbItem ? orbItem.hoverArea : null
    readonly property var bubbleHoverProxy: bubbleItem ? bubbleItem.hoverArea : null
    readonly property var headingMeasureProxy: bubbleItem ? bubbleItem.headingMeasure : null
    readonly property var orbItem: hubOrbItem
    readonly property var bubbleItem: hubBubbleItem

    visible: hasDetail
    anchors.fill: parent
    z: 10

    function hasState(state) { return Logic.hasState(root, state) }
    function buildOrbChannels() { return Logic.buildOrbChannels(root) }
    function iconSource(channel) { return Logic.iconSource(root, channel) }
    function iconAccent(channel, state) { return Logic.iconAccent(root, channel, state) }
    function channelLabel(channel) { return Logic.channelLabel(root, channel) }
    function channelStateText(state) { return Logic.channelStateText(root, state) }
    function defaultSummary() { return Logic.defaultSummary(root) }

    HubStatusOrbButton { id: hubOrbItem; workspaceRoot: root }
    HubStatusOrbBubble { id: hubBubbleItem; workspaceRoot: root }
}
