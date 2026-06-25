<template>
  <div class="chat-layout">
    <!-- 左侧会话列表 -->
    <aside class="chat-sidebar">
      <div class="sidebar-header">
        <h2>系统客服消息</h2>
        <span class="session-count">{{ sessions.length }}</span>
      </div>
      <div class="session-list">
        <div v-if="sessions.length === 0" class="empty-sessions">
          暂无会话
        </div>
        <div
          v-for="s in sessions"
          :key="s.id"
          class="session-item"
          :class="{ active: currentSessionId === s.id, unread: s.unread_count > 0 }"
          @click="selectSession(s)"
        >
          <div class="session-avatar">
            {{ (s.buyer_name || '买').charAt(0) }}
          </div>
          <div class="session-info">
            <div class="session-top">
              <span class="session-name">{{ s.buyer_name || '买家' + s.buyer_id }}</span>
              <span class="session-time">{{ formatTime(s.updated_at) }}</span>
            </div>
            <div class="session-bottom">
              <span class="session-last">{{ s.last_message || '暂无消息' }}</span>
              <span v-if="s.unread_count > 0" class="unread-badge">{{ s.unread_count }}</span>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- 右侧聊天区 -->
    <main class="chat-main">
      <div v-if="!currentSessionId" class="chat-empty">
        <div class="chat-empty-icon">💬</div>
        <p>选择左侧会话开始回复</p>
      </div>

      <template v-else>
        <div class="chat-header">
          <span class="chat-buyer-name">{{ currentSession?.buyer_name || '买家' }}</span>
          <span v-if="currentSession?.product_name" class="chat-product-tag">
            来自商品：{{ currentSession.product_name }}
          </span>
        </div>

        <div class="chat-body" ref="chatBodyRef">
          <div
            v-for="(msg, i) in chatMessages"
            :key="i"
            class="chat-msg"
            :class="msg.sender_role"
          >
            <div class="chat-msg-name">{{ msg.sender_role === 'buyer' ? '买家' : '我' }}</div>
            <div class="chat-msg-bubble">
              {{ msg.message }}
            </div>
            <div class="chat-msg-time">{{ formatTime(msg.created_at) }}</div>
          </div>
        </div>

        <div class="chat-footer">
          <input
            v-model="replyText"
            class="chat-input"
            placeholder="输入回复…"
            @keyup.enter="sendReply"
          />
          <button class="chat-send-btn" @click="sendReply" :disabled="!replyText.trim()">
            发送
          </button>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/utils/api'

const auth = useAuthStore()

const sessions = ref<any[]>([])
const currentSessionId = ref<number | null>(null)
const currentSession = ref<any>(null)
const chatMessages = ref<any[]>([])
const replyText = ref('')
const chatBodyRef = ref<HTMLElement | null>(null)

let pollTimer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  loadSessions()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})

async function loadSessions() {
  try {
    const res: any = await api.get('/admin-endpoint/chat/sessions')
    if (res.code === 0 && res.data) {
      sessions.value = res.data
      if (currentSessionId.value) {
        const found = res.data.find((s: any) => s.id === currentSessionId.value)
        if (found) currentSession.value = found
      }
    }
  } catch {}
}

async function selectSession(s: any) {
  currentSessionId.value = s.id
  currentSession.value = s
  await loadMessages()
  try {
    await api.post('/admin-endpoint/chat/mark-read', null, {
      params: { session_id: s.id },
    })
    s.unread_count = 0
  } catch {}
}

async function loadMessages() {
  if (!currentSessionId.value) return
  try {
    const res: any = await api.get('/admin-endpoint/chat/messages', {
      params: { session_id: currentSessionId.value },
    })
    if (res.code === 0 && res.data) {
      chatMessages.value = res.data
      await nextTick()
      scrollToBottom()
    }
  } catch {}
}

// 增量轮询：只拉取新消息，不全量覆盖
async function pollNewMessages() {
  if (!currentSessionId.value) return
  const confirmedIds = chatMessages.value
    .map((m: any) => m.id || 0)
    .filter((id: number) => id > 0)
  const maxId = confirmedIds.length > 0 ? Math.max(...confirmedIds) : 0
  try {
    const res: any = await api.get('/admin-endpoint/chat/messages', {
      params: {
        session_id: currentSessionId.value,
        after_id: maxId > 0 ? maxId : undefined,
      },
    })
    if (res.code === 0 && res.data && (res.data as any[]).length > 0) {
      chatMessages.value.push(...(res.data as any[]))
      await nextTick()
      scrollToBottom()
    }
  } catch {}
}

async function sendReply() {
  const text = replyText.value.trim()
  if (!text || !currentSessionId.value) return
  try {
    const res: any = await api.post('/admin-endpoint/chat/reply', {
      session_id: currentSessionId.value,
      message: text,
    })
    if (res.code === 0) {
      replyText.value = ''
      chatMessages.value.push({
        id: res.data?.message_id || 0,
        sender_role: 'admin',
        message: text,
        created_at: new Date().toISOString(),
      })
      await nextTick()
      scrollToBottom()
    }
  } catch {}
}

async function pollMessages() {
  await loadSessions()
  if (currentSessionId.value) {
    await pollNewMessages()
  }
}

function startPolling() {
  stopPolling()
  pollTimer = setInterval(pollMessages, 5000)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function scrollToBottom() {
  if (chatBodyRef.value) {
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
  }
}

function formatTime(t: string | null): string {
  if (!t) return ''
  const d = new Date(t)
  const now = new Date()
  const isToday = d.toDateString() === now.toDateString()
  if (isToday) {
    return d.toLocaleTimeString()
  }
  return d.toLocaleDateString()
}
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: calc(100vh - 64px);
  background: #f5f5f5;
}
.chat-sidebar {
  width: 320px;
  background: #fff;
  border-right: 1px solid #e8e8e8;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.sidebar-header {
  padding: 20px 20px 16px;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.sidebar-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}
.session-count {
  background: #e8e8e8;
  color: #666;
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 12px;
}
.session-list {
  flex: 1;
  overflow-y: auto;
}
.empty-sessions {
  text-align: center;
  color: #999;
  padding: 40px 0;
  font-size: 14px;
}
.session-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid #f0f0f0;
}
.session-item:hover { background: #fafafa; }
.session-item.active { background: #f0f4ff; }
.session-item.unread { background: #f0f4ff; }
.session-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}
.session-info { flex: 1; min-width: 0; }
.session-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}
.session-name { font-size: 14px; font-weight: 500; color: #1f2937; }
.session-time { font-size: 11px; color: #999; }
.session-bottom { display: flex; align-items: center; justify-content: space-between; }
.session-last {
  font-size: 13px;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 180px;
}
.unread-badge {
  background: #ef4444;
  color: #fff;
  font-size: 11px;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.chat-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #bbb;
}
.chat-empty-icon { font-size: 48px; margin-bottom: 16px; }
.chat-header {
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  gap: 12px;
}
.chat-buyer-name { font-size: 15px; font-weight: 600; }
.chat-product-tag {
  font-size: 12px;
  color: #6366f1;
  background: #eef2ff;
  padding: 3px 10px;
  border-radius: 12px;
}
.chat-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.chat-msg { display: flex; flex-direction: column; align-items: flex-start; }
.chat-msg.admin { align-items: flex-end; }
.chat-msg-name {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
  padding: 0 4px;
}
.chat-msg.admin .chat-msg-name { text-align: right; }
.chat-msg-bubble {
  max-width: 70%;
  padding: 10px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
}
.chat-msg.buyer .chat-msg-bubble {
  background: #fff;
  border: 1px solid #e8e8e8;
  border-bottom-left-radius: 4px;
}
.chat-msg.admin .chat-msg-bubble {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.chat-msg-time {
  font-size: 11px;
  color: #bbb;
  margin-top: 4px;
  text-align: center;
}
.chat-footer {
  padding: 16px 24px;
  background: #fff;
  border-top: 1px solid #e8e8e8;
  display: flex;
  gap: 12px;
}
.chat-input {
  flex: 1;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 14px;
  outline: none;
}
.chat-input:focus { border-color: #6366f1; }
.chat-send-btn {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 24px;
  font-size: 14px;
  cursor: pointer;
}
.chat-send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
