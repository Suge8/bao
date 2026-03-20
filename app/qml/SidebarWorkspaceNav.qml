import QtQuick 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root

    required property var sidebarRoot
    signal sectionRequested(string section)

    property alias sessionsItem: sessionsNavItem
    property alias memoryItem: memoryNavItem
    property alias skillsItem: skillsNavItem
    property alias toolsItem: toolsNavItem
    property alias cronItem: cronNavItem
    property alias navContentItem: navContent

    Layout.fillWidth: true
    Layout.leftMargin: 12
    Layout.rightMargin: 12
    Layout.topMargin: 16
    implicitHeight: navContent.implicitHeight + 20
    radius: 22
    color: sidebarRoot.isDark ? "#15100D" : "#FAF4EE"
    border.width: 1
    border.color: sidebarRoot.isDark ? "#20FFFFFF" : "#14000000"

    Rectangle {
        id: navHighlight
        objectName: "sidebarNavHighlight"
        x: 8
        y: sidebarRoot.navHighlightY
        z: 1
        width: navContent.width + 4
        height: sidebarRoot.navHighlightHeight
        radius: 16
        color: sidebarRoot.isDark ? "#2A1C14" : "#F3E7D8"
        border.width: 1
        border.color: sidebarRoot.isDark ? "#3A2A20" : "#E9D6C0"
        opacity: sidebarRoot.navHighlightOpacity
        Behavior on y { NumberAnimation { duration: sidebarRoot.motionUi; easing.type: sidebarRoot.easeStandard } }
        Behavior on height { NumberAnimation { duration: sidebarRoot.motionUi; easing.type: sidebarRoot.easeStandard } }
        Behavior on opacity { NumberAnimation { duration: sidebarRoot.motionFast; easing.type: sidebarRoot.easeStandard } }

        Rectangle {
            anchors.left: parent.left
            anchors.leftMargin: 8
            anchors.verticalCenter: parent.verticalCenter
            width: 3
            height: 26
            radius: 1.5
            color: sidebarRoot.accent
        }

        Rectangle {
            anchors.fill: parent
            anchors.margins: 1
            radius: parent.radius - 1
            color: sidebarRoot.isDark ? "#08FFFFFF" : "#10FFFFFF"
            opacity: 0.8
        }
    }

    ColumnLayout {
        id: navContent
        anchors.fill: parent
        anchors.margins: 10
        spacing: 4
        z: 2

        Text {
            Layout.leftMargin: 8
            Layout.topMargin: 6
            text: sidebarRoot.strings.sidebar_library_title
            color: sidebarRoot.textSecondary
            font.pixelSize: sidebarRoot.typeMeta
            font.weight: sidebarRoot.weightBold
            font.letterSpacing: sidebarRoot.letterWide
        }

        SidebarNavItem { id: sessionsNavItem; Layout.fillWidth: true; label: sidebarRoot.strings.sidebar_sessions; iconSource: sidebarRoot.sectionIconSource("sessions"); active: sidebarRoot.selectionTarget === "sessions"; badgeCount: sidebarRoot.hasSessionService ? (sidebarRoot.sessionService.sidebarUnreadCount || 0) : 0; useAccentBadge: true; useExternalHighlight: true; onClicked: root.sectionRequested("sessions") }
        SidebarNavItem { id: memoryNavItem; Layout.fillWidth: true; label: sidebarRoot.strings.sidebar_memory; iconSource: sidebarRoot.sectionIconSource("memory"); active: sidebarRoot.selectionTarget === "memory"; useExternalHighlight: true; onClicked: root.sectionRequested("memory") }
        SidebarNavItem { id: skillsNavItem; Layout.fillWidth: true; label: sidebarRoot.strings.sidebar_skills; iconSource: sidebarRoot.sectionIconSource("skills"); active: sidebarRoot.selectionTarget === "skills"; useExternalHighlight: true; onClicked: root.sectionRequested("skills") }
        SidebarNavItem { id: toolsNavItem; Layout.fillWidth: true; label: sidebarRoot.strings.sidebar_tools_nav; iconSource: sidebarRoot.sectionIconSource("tools"); active: sidebarRoot.selectionTarget === "tools"; useExternalHighlight: true; onClicked: root.sectionRequested("tools") }
        SidebarNavItem { id: cronNavItem; Layout.fillWidth: true; label: sidebarRoot.strings.sidebar_cron; iconSource: sidebarRoot.sectionIconSource("cron"); active: sidebarRoot.selectionTarget === "cron"; useExternalHighlight: true; onClicked: root.sectionRequested("cron") }
    }
}
