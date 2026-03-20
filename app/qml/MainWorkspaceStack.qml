import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

StackLayout {
    id: root

    required property var appRoot

    currentIndex: appRoot.activeWorkspaceIndex

    SessionsWorkspace {
        Layout.fillWidth: true
        Layout.fillHeight: true
        active: appRoot.activeWorkspace === "sessions"
        chatService: appRoot.chatService
        sessionService: appRoot.sessionService
        configService: appRoot.configService
    }

    Loader {
        id: controlTowerWorkspaceLoader
        objectName: "controlTowerWorkspaceLoader"
        Layout.fillWidth: true
        Layout.fillHeight: true
        property bool cached: false
        readonly property bool currentWorkspace: appRoot.activeWorkspace === "control_tower"
        active: cached || currentWorkspace
        Component.onCompleted: if (currentWorkspace) cached = true
        onCurrentWorkspaceChanged: if (currentWorkspace) cached = true
        sourceComponent: ControlTowerWorkspace {
            active: controlTowerWorkspaceLoader.currentWorkspace
            appRoot: root.appRoot
            supervisorService: root.appRoot.profileSupervisorService
        }
    }

    Loader {
        id: memoryWorkspaceLoader
        objectName: "memoryWorkspaceLoader"
        Layout.fillWidth: true
        Layout.fillHeight: true
        property bool cached: false
        readonly property bool currentWorkspace: appRoot.activeWorkspace === "memory"
        active: cached || currentWorkspace
        asynchronous: true
        Component.onCompleted: if (currentWorkspace) cached = true
        onCurrentWorkspaceChanged: {
            if (!currentWorkspace)
                return
            cached = true
            if (root.appRoot.memoryService && root.appRoot.memoryService.ensureHydrated)
                root.appRoot.memoryService.ensureHydrated()
        }
        sourceComponent: MemoryWorkspace {
            active: memoryWorkspaceLoader.currentWorkspace
            memoryService: root.appRoot.memoryService
        }
    }

    Loader {
        id: skillsWorkspaceLoader
        objectName: "skillsWorkspaceLoader"
        Layout.fillWidth: true
        Layout.fillHeight: true
        property bool cached: false
        readonly property bool currentWorkspace: appRoot.activeWorkspace === "skills"
        active: cached || currentWorkspace
        asynchronous: true
        Component.onCompleted: if (currentWorkspace) cached = true
        onCurrentWorkspaceChanged: {
            if (!currentWorkspace)
                return
            cached = true
            if (root.appRoot.skillsService && root.appRoot.skillsService.hydrateIfNeeded)
                root.appRoot.skillsService.hydrateIfNeeded()
        }
        sourceComponent: SkillsWorkspace {
            active: skillsWorkspaceLoader.currentWorkspace
            skillsService: root.appRoot.skillsService
        }
    }

    Loader {
        id: toolsWorkspaceLoader
        objectName: "toolsWorkspaceLoader"
        Layout.fillWidth: true
        Layout.fillHeight: true
        property bool cached: false
        readonly property bool currentWorkspace: appRoot.activeWorkspace === "tools"
        active: cached || currentWorkspace
        asynchronous: true
        Component.onCompleted: if (currentWorkspace) cached = true
        onCurrentWorkspaceChanged: if (currentWorkspace) cached = true
        sourceComponent: ToolsWorkspace {
            active: toolsWorkspaceLoader.currentWorkspace
            toolsService: root.appRoot.toolsService
            configService: root.appRoot.configService
            uiLanguage: root.appRoot.uiLanguage
            autoLanguage: root.appRoot.autoLanguage
        }
    }

    Loader {
        id: cronWorkspaceLoader
        objectName: "cronWorkspaceLoader"
        Layout.fillWidth: true
        Layout.fillHeight: true
        property bool cached: false
        readonly property bool currentWorkspace: appRoot.activeWorkspace === "cron"
        active: cached || currentWorkspace
        Component.onCompleted: if (currentWorkspace) cached = true
        onCurrentWorkspaceChanged: if (currentWorkspace) cached = true
        sourceComponent: CronWorkspace {
            active: cronWorkspaceLoader.currentWorkspace
            appRoot: root.appRoot
            cronService: root.appRoot.cronService
            heartbeatService: root.appRoot.heartbeatService
        }
    }
}
