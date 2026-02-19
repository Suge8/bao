import { execFile } from 'child_process';
import os from 'os';
import path from 'path';
import { promisify } from 'util';

import Database from 'better-sqlite3';

import { ASSISTANT_HAS_OWN_NUMBER, ASSISTANT_NAME } from '../config.js';
import { getRouterState, setRouterState } from '../db.js';
import { logger } from '../logger.js';
import {
  Channel,
  OnChatMetadata,
  OnInboundMessage,
  RegisteredGroup,
} from '../types.js';

const execFileAsync = promisify(execFile);
const POLL_INTERVAL_MS = 2000;
const BATCH_SIZE = 500;
const CURSOR_KEY = 'imessage_last_rowid';
const APPLE_EPOCH_OFFSET = 978307200;

interface IMessageChannelOpts {
  onMessage: OnInboundMessage;
  onChatMetadata: OnChatMetadata;
  registeredGroups: () => Record<string, RegisteredGroup>;
}

interface ChatDbRow {
  message_rowid: number;
  message_guid: string | null;
  text: string | null;
  is_from_me: number;
  apple_date_raw: number | null;
  sender_handle: string | null;
  chat_rowid: number;
  chat_guid: string | null;
  chat_display_name: string | null;
}

function appleTimestampToISO(appleDate: number): string {
  const unixSeconds = appleDate / 1_000_000_000 + APPLE_EPOCH_OFFSET;
  return new Date(unixSeconds * 1000).toISOString();
}

function escapeAppleScriptString(value: string): string {
  return value
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\n/g, '\\n');
}

function parseHandleFromChatGuid(chatGuid: string | null): string | null {
  if (!chatGuid) return null;
  const match = /^iMessage;[-+]?;(.+)$/.exec(chatGuid);
  return match?.[1] ?? null;
}

function isGroupChat(
  chatGuid: string | null,
  participantCount: number,
): boolean {
  if (chatGuid?.startsWith('chat')) return true;
  return participantCount > 1;
}

export class IMessageChannel implements Channel {
  name = 'imessage';

  private opts: IMessageChannelOpts;
  private connected = false;
  private lastRowId = 0;
  private pollTimer: ReturnType<typeof setInterval> | null = null;
  private polling = false;
  private chatDb: Database.Database | null = null;

  constructor(opts: IMessageChannelOpts) {
    this.opts = opts;
  }

  async connect(): Promise<void> {
    if (process.platform !== 'darwin') {
      logger.warn('iMessage channel is only available on macOS');
      return;
    }

    const chatDbPath = path.join(
      os.homedir(),
      'Library',
      'Messages',
      'chat.db',
    );

    try {
      this.chatDb = new Database(chatDbPath, {
        readonly: true,
        fileMustExist: true,
      });
      this.chatDb.prepare('SELECT 1').get();
    } catch (err) {
      logger.error(
        { err, chatDbPath },
        'Failed to open iMessage chat.db. Grant Full Disk Access to Terminal/Node and retry.',
      );
      this.connected = false;
      return;
    }

    await this.ensureMessagesAppRunning();
    this.initializeCursor();

    this.pollTimer = setInterval(() => {
      this.pollNewMessages().catch((err) => {
        logger.error({ err }, 'iMessage poll failed');
      });
    }, POLL_INTERVAL_MS);

    this.connected = true;
    logger.info({ lastRowId: this.lastRowId }, 'Connected to iMessage channel');
  }

  async sendMessage(jid: string, text: string): Promise<void> {
    if (!this.connected) {
      throw new Error('iMessage channel is not connected');
    }

    const target = this.parseJid(jid);
    if (!target) {
      throw new Error(`Invalid iMessage JID: ${jid}`);
    }

    const prefixed = ASSISTANT_HAS_OWN_NUMBER
      ? text
      : `${ASSISTANT_NAME}: ${text}`;

    if (target.type === 'group') {
      await this.sendToGroup(target.value, prefixed);
    } else {
      await this.sendToBuddy(target.value, prefixed);
    }
  }

  isConnected(): boolean {
    return this.connected;
  }

  ownsJid(jid: string): boolean {
    return jid.startsWith('imsg:');
  }

  async disconnect(): Promise<void> {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
    this.chatDb?.close();
    this.chatDb = null;
    this.connected = false;
  }

  private initializeCursor(): void {
    const cursorFromState = getRouterState(CURSOR_KEY);
    if (cursorFromState) {
      const parsed = Number.parseInt(cursorFromState, 10);
      this.lastRowId = Number.isFinite(parsed) ? parsed : 0;
      return;
    }

    const row = this.chatDb
      ?.prepare('SELECT IFNULL(MAX(ROWID), 0) AS max_rowid FROM message')
      .get() as { max_rowid: number } | undefined;

    this.lastRowId = row?.max_rowid ?? 0;
    setRouterState(CURSOR_KEY, String(this.lastRowId));
  }

  private async ensureMessagesAppRunning(): Promise<void> {
    const script = 'tell application "Messages" to launch';
    try {
      await execFileAsync('osascript', ['-e', script]);
    } catch (err) {
      logger.warn(
        { err },
        'Failed to launch Messages.app; send may fail until app is available',
      );
    }
  }

  private async pollNewMessages(): Promise<void> {
    if (!this.chatDb || this.polling) return;
    this.polling = true;

    try {
      while (true) {
        const rows = this.chatDb
          .prepare(
            `
            SELECT
              m.ROWID AS message_rowid,
              m.guid AS message_guid,
              m.text AS text,
              m.is_from_me AS is_from_me,
              m.date AS apple_date_raw,
              h.id AS sender_handle,
              c.ROWID AS chat_rowid,
              c.guid AS chat_guid,
              c.display_name AS chat_display_name
            FROM message m
            JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
            JOIN chat c ON c.ROWID = cmj.chat_id
            LEFT JOIN handle h ON h.ROWID = m.handle_id
            WHERE m.ROWID > ?
            ORDER BY m.ROWID ASC
            LIMIT ${BATCH_SIZE}
          `,
          )
          .all(this.lastRowId) as ChatDbRow[];

        if (rows.length === 0) break;

        for (const row of rows) {
          this.processRow(row);
          this.lastRowId = row.message_rowid;
        }

        setRouterState(CURSOR_KEY, String(this.lastRowId));

        if (rows.length < BATCH_SIZE) break;
      }
    } finally {
      this.polling = false;
    }
  }

  private processRow(row: ChatDbRow): void {
    const participantCount = this.getParticipantCount(row.chat_rowid);
    const group = isGroupChat(row.chat_guid, participantCount);

    const chatId = group
      ? row.chat_guid || `chat${row.chat_rowid}`
      : row.sender_handle || parseHandleFromChatGuid(row.chat_guid) || '';
    if (!chatId) return;

    const chatJid = `imsg:${chatId}`;
    const timestamp = row.apple_date_raw
      ? appleTimestampToISO(row.apple_date_raw)
      : new Date().toISOString();

    this.opts.onChatMetadata(
      chatJid,
      timestamp,
      row.chat_display_name || undefined,
      'imessage',
      group,
    );

    const groups = this.opts.registeredGroups();
    if (!groups[chatJid]) return;

    const content = row.text || '';
    const sender = row.sender_handle || (row.is_from_me ? 'me' : 'unknown');
    const fromMe = row.is_from_me === 1;
    const isBotMessage = ASSISTANT_HAS_OWN_NUMBER
      ? fromMe
      : content.startsWith(`${ASSISTANT_NAME}:`);

    this.opts.onMessage(chatJid, {
      id: row.message_guid || String(row.message_rowid),
      chat_jid: chatJid,
      sender,
      sender_name: sender,
      content,
      timestamp,
      is_from_me: fromMe,
      is_bot_message: isBotMessage,
    });
  }

  private getParticipantCount(chatRowId: number): number {
    if (!this.chatDb) return 0;
    const row = this.chatDb
      .prepare(
        'SELECT COUNT(*) AS participant_count FROM chat_handle_join WHERE chat_id = ?',
      )
      .get(chatRowId) as { participant_count: number } | undefined;
    return row?.participant_count ?? 0;
  }

  private parseJid(
    jid: string,
  ): { type: 'group' | 'individual'; value: string } | null {
    if (!jid.startsWith('imsg:')) return null;
    const value = jid.slice('imsg:'.length);
    if (!value) return null;
    const type = value.startsWith('chat') ? 'group' : 'individual';
    return { type, value };
  }

  private async sendToBuddy(handle: string, text: string): Promise<void> {
    const escapedText = escapeAppleScriptString(text);
    const escapedHandle = escapeAppleScriptString(handle);
    const script = `tell application "Messages" to send "${escapedText}" to buddy "${escapedHandle}" of (1st service whose service type = iMessage)`;
    await execFileAsync('osascript', ['-e', script]);
  }

  private async sendToGroup(chatGuid: string, text: string): Promise<void> {
    const escapedText = escapeAppleScriptString(text);
    const escapedGuid = escapeAppleScriptString(chatGuid);
    const script = `
      tell application "Messages"
        launch
        set targetChat to missing value
        repeat with c in chats
          try
            if (id of c as text) contains "${escapedGuid}" then
              set targetChat to c
              exit repeat
            end if
          end try
        end repeat
        if targetChat is missing value then error "Group chat not found: ${escapedGuid}"
        send "${escapedText}" to targetChat
      end tell
    `;
    await execFileAsync('osascript', ['-e', script]);
  }
}
