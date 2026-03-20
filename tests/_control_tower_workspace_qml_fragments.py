from __future__ import annotations


def wrapper_header(qml_dir: str) -> str:
    return f'''
import QtQuick 2.15
import QtQuick.Controls 2.15
import "{qml_dir}"

Item {{
    width: 1400
    height: 920

    property bool isDark: true
    property string effectiveLang: "zh"
    property string uiLanguage: "zh"
    property color accent: "#FFA11A"
    property color accentHover: "#FFB444"
    property color accentGlow: "#66FFA11A"
    property color borderSubtle: "#30FFFFFF"
    property color textPrimary: "#FFF6EA"
    property color textSecondary: "#C8B09A"
    property color textTertiary: "#9D8778"
    property color bgCard: "#1A120D"
    property color bgCardHover: "#23170F"
    property color statusSuccess: "#52D68A"
    property color statusError: "#F05A5A"
    property int typeTitle: 22
    property int typeBody: 16
    property int typeLabel: 14
    property int typeCaption: 11
    property int typeMeta: 12
    property int weightBold: Font.Bold
    property int weightDemiBold: Font.DemiBold
    property int weightMedium: Font.Medium
    property real motionHoverScaleSubtle: 1.0
    property int motionFast: 180
    property int motionUi: 220
    property int motionBreath: 1100
    property int easeStandard: Easing.OutCubic
    property int easeEmphasis: Easing.OutBack
    property int easeSoft: Easing.InOutSine
'''


def supervisor_overview_block() -> str:
    return '''

    QtObject {
        id: supervisor
        objectName: "supervisorHarness"
        property int selectCalls: 0
        property int activateCalls: 0
        property var overview: ({
            title: "指挥舱",
            liveProfileId: "default",
            profileCount: 2
        })
'''


def supervisor_profiles_block() -> str:
    return '''
        property var profiles: [
            {
                id: "default",
                displayName: "日常",
                avatarSource: "",
                statusSummary: "2 个会话 / 1 个子代理工作中",
                updatedLabel: "刚刚",
                totalSessionCount: 2,
                totalChildSessionCount: 1,
                workingCount: 2,
                automationCount: 2,
                attentionCount: 0,
                isHubLive: true,
                channelKeys: ["desktop", "telegram"]
            },
            {
                id: "work",
                displayName: "Work",
                avatarSource: "",
                statusSummary: "1 个自动化待命",
                updatedLabel: "3 分钟前",
                totalSessionCount: 3,
                totalChildSessionCount: 0,
                workingCount: 0,
                automationCount: 1,
                attentionCount: 1,
                isHubLive: false,
                channelKeys: ["telegram"]
            }
        ]
        property var profilesModel: profiles
        property int profileCount: profiles.length
'''


def working_lane_block() -> str:
    return '''
        property var workingItems: [
            {
                id: "default:session",
                profileId: "default",
                title: "Main Thread",
                summary: "回复中",
                updatedLabel: "刚刚",
                isLive: true,
                canOpen: true,
                avatarSource: "",
                personaVariant: "primary",
                accentKey: "desktop",
                glyphSource: "",
                statusKey: "running",
                statusLabel: "运行中"
            }
        ]
        property var workingModel: workingItems
        property int workingCount: workingItems.length
'''


def completed_lane_block() -> str:
    return '''
        property var completedItems: [
            {
                id: "default:start",
                profileId: "default",
                title: "AI 问候",
                summary: "刚发送完问候",
                updatedLabel: "刚刚",
                isLive: true,
                canOpen: true,
                avatarSource: "",
                personaVariant: "primary",
                accentKey: "desktop",
                glyphSource: "",
                statusKey: "completed",
                statusLabel: "已完成"
            }
        ]
        property var completedModel: completedItems
        property int completedCount: completedItems.length
'''


def automation_lane_block() -> str:
    return '''
        property var automationItems: [
            {
                id: "default:cron",
                profileId: "default",
                title: "Daily Review",
                summary: "每 30 分钟",
                updatedLabel: "2 小时后",
                isLive: true,
                canOpen: true,
                avatarSource: "",
                personaVariant: "automation",
                accentKey: "cron",
                glyphSource: "",
                statusKey: "scheduled",
                statusLabel: "已调度"
            }
        ]
        property var automationModel: automationItems
        property int automationCount: automationItems.length
'''


def attention_lane_block() -> str:
    return '''
        property var attentionItems: [
            {
                id: "work:issue",
                profileId: "work",
                title: "自动检查",
                summary: "缺少检查说明",
                updatedLabel: "3 分钟前",
                isLive: false,
                canOpen: false,
                avatarSource: "",
                personaVariant: "automation",
                accentKey: "heartbeat",
                glyphSource: "",
                statusKey: "error",
                statusLabel: "待处理"
            }
        ]
        property var attentionModel: attentionItems
        property int attentionCount: attentionItems.length
'''


def supervisor_actions_block(selected_profile_qml: str) -> str:
    return f'''
        property var selectedProfile: {selected_profile_qml}
        function refresh() {{}}
        function selectProfile(_profileId) {{ selectCalls += 1 }}
        function activateProfile(_profileId) {{ activateCalls += 1 }}
        function selectItem(_itemId) {{}}
        function openSelectedTarget() {{}}
    }}
'''


def wrapper_footer() -> str:
    return '''
    ControlTowerWorkspace {
        id: workspace
        anchors.fill: parent
        active: true
        supervisorService: supervisor
    }
}
'''
