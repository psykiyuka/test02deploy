<template>
  <!-- 仅 C 端用户可见 -->
  <div v-if="showFab">
    <!-- 悬浮按钮：面板打开时隐藏 -->
    <button v-if="!open" class="ai-fab" @click="open = true" title="客服">
      <MessageCircle class="w-6 h-6" />
      <span v-if="unread" class="ai-fab-badge">{{ unread }}</span>
    </button>
  </div>

  <!-- 聊天面板 -->
  <div v-if="open" class="ai-overlay" @click.self="open = false">
    <div class="ai-panel">
      <!-- 头部 -->
      <div class="ai-panel-header">
        <div class="ai-header-left">
          <span class="ai-panel-title">{{ mode === 'ai' ? 'AI 客服' : '人工客服' }}</span>
          <span v-if="mode === 'human' && sessionStatus === 'waiting'" class="ai-status-dot waiting" title="等待客服接入">●</span>
          <span v-if="mode === 'human' && sessionStatus === 'active'" class="ai-status-dot active" title="客服已接入">●</span>
        </div>
        <div class="ai-header-actions">
          <!-- AI/人工切换 -->
          <button class="ai-mode-btn" @click="toggleMode">
            {{ mode === 'ai' ? '转人工' : '转AI' }}
          </button>
          <button class="ai-panel-close" @click="open = false">✕</button>
        </div>
      </div>

      <!-- 人工客服：未建立会话时 -->
      <div v-if="mode === 'human' && !sessionId" class="ai-panel-body">
        <div class="ai-welcome">
          您好！需要人工客服帮助吗？
        </div>
        <div class="ai-connect-row">
          <button class="ai-connect-btn" @click="connectHuman" :disabled="connecting">
            {{ connecting ? '连接中…' : '连接人工客服' }}
          </button>
        </div>
      </div>

      <!-- 消息区 -->
      <div
        v-if="messages.length > 0 || loading"
        class="ai-panel-body"
        ref="bodyRef"
      >
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="ai-msg"
          :class="msg.role"
        >
          <div class="ai-msg-bubble">
            {{ msg.content }}
            <div v-if="msg.sources?.length" class="ai-sources">
              参考：{{ msg.sources.map(s => s.question).join(' / ') }}
            </div>
          </div>
        </div>
        <div v-if="loading" class="ai-msg assistant">
          <div class="ai-msg-bubble ai-typing">正在思考…</div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="mode === 'ai' && messages.length === 0 && !loading" class="ai-panel-body">
        <div class="ai-welcome">
          你好！我是 AI 客服助手，有什么可以帮您的？
        </div>
      </div>

      <!-- 输入区 -->
      <div class="ai-panel-footer">
        <template v-if="mode === 'ai'">
          <label class="ai-rewrite-label">
            <input type="checkbox" v-model="rewrite" />
            AI 帮我润色问题
          </label>
        </template>
        <template v-if="mode === 'human' && !sessionId">
          <div class="ai-connect-hint">请先点击"连接人工客服"建立会话</div>
        </template>
        <div class="ai-input-row">
          <input
            v-model="input"
            class="ai-input"
            :placeholder="mode === 'ai' ? '输入您的问题…' : '输入消息…'"
            @keyup.enter="send"
            :disabled="loading || (mode === 'human' && !sessionId)"
          />
          <button
            class="ai-send-btn"
            @click="send"
            :disabled="loading || !input.trim() || (mode === 'human' && !sessionId)"
          >
            发送
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import { api } from "@/utils/api";
import { MessageCircle } from "lucide-vue-next";

const route = useRoute();
const auth = useAuthStore();

const open = ref(false);
const input = ref("");
const loading = ref(false);
const rewrite = ref(false);
const unread = ref(0);
const messages = ref<{ role: "user" | "assistant"; content: string; sources?: any[] }[]>([]);
const bodyRef = ref<HTMLElement | null>(null);
const currentMerchantId = ref<number | null>(null);
const currentProductId = ref<number | null>(null);

// 模式：ai | human
const mode = ref<"ai" | "human">("ai");
const sessionId = ref<number | null>(null);
const sessionStatus = ref<"waiting" | "active" | "closed">("waiting");
const receiverType = ref<"merchant" | "admin" | null>(null);
const receiverName = ref<string>("");
const connecting = ref(false);
let pollTimer: ReturnType<typeof setInterval> | null = null;

// 仅 C 端用户显示
const showFab = computed(() => auth.isLoggedIn && auth.user?.role === "user");

// 自动滚动到底部
watch(messages, async () => {
  await nextTick();
  if (bodyRef.value) {
    bodyRef.value.scrollTop = bodyRef.value.scrollHeight;
  }
});

// 页面加载时获取商家 ID 和商品 ID
onMounted(() => {
  detectMerchantId();
  currentProductId.value = detectProductId();
});

// 路由变化时重新检测
watch(() => route.fullPath, () => {
  detectMerchantId();
  currentProductId.value = detectProductId();
});

// 打开/关闭聊天框
watch(open, (val) => {
  if (val) {
    // 打开时：重新检测当前页面商品 ID
    currentProductId.value = detectProductId();
    if (mode.value === "human" && sessionId.value) {
      // 已有会话，显示接入状态
      const label = receiverType.value === "merchant"
        ? `您正在与商家「${receiverName.value}」聊天中`
        : "您正在与平台管理员聊天中";
      messages.value.push({ role: "assistant", content: label });
      startPolling();
    }
  } else {
    // 关闭时：停止轮询，并完全重置状态
    // 下次打开会重新判断路由（详情页 → 商家，其他页面 → 管理员）
    stopPolling();
    if (mode.value === "human") {
      sessionId.value = null;
      sessionStatus.value = "waiting";
      receiverType.value = null;
      receiverName.value = "";
      messages.value = [];
    }
  }
});

// 模式切换
async function toggleMode() {
  if (mode.value === "ai") {
    // 切换到人工：先尝试建立会话
    mode.value = "human";
    await connectHuman();
  } else {
    mode.value = "ai";
    stopPolling();
  }
}

// 连接人工客服
async function connectHuman() {
  if (connecting.value) return;

  // 每次连接时重新检测当前页面是否有关联商品
  currentProductId.value = detectProductId();

  if (sessionId.value) {
    // 已有会话，显示接入状态
    const label = receiverType.value === "merchant"
      ? `您正在与商家「${receiverName.value}」聊天中`
      : "您正在与平台管理员聊天中";
    messages.value.push({ role: "assistant", content: label });
    startPolling();
    return;
  }
  connecting.value = true;
  try {
    const res: any = await api.post("/c-endpoint/chat/session", {
      product_id: currentProductId.value,
    });
    if (res.code === 0 && res.data) {
      sessionId.value = res.data.session_id;
      sessionStatus.value = res.data.status || "waiting";
      receiverType.value = res.data.receiver_type || null;
      receiverName.value = res.data.receiver_name || "";

      // 显示接入提示
      const label = receiverType.value === "merchant"
        ? `商家「${receiverName.value}」已接入，现在开始聊天吧！`
        : "平台管理员已接入，现在开始聊天吧！";
      messages.value.push({ role: "assistant", content: label });

      // 加载历史消息
      await loadMessages();
      // 开始轮询
      startPolling();
    } else {
      // 显示错误原因
      messages.value.push({
        role: "assistant",
        content: "连接失败：" + (res.message || "未知错误"),
      });
    }
  } catch (e: any) {
    messages.value.push({
      role: "assistant",
      content: "连接人工客服失败，请稍后重试。" + (e?.message || ""),
    });
  } finally {
    connecting.value = false;
  }
}

// 发送消息
async function send() {
  const text = input.value.trim();
  if (!text || loading.value) return;

  if (mode.value === "ai") {
    await sendAi(text);
  } else {
    await sendHuman(text);
  }
}

// AI 回复
async function sendAi(question: string) {
  messages.value.push({ role: "user", content: question });
  input.value = "";
  loading.value = true;

  try {
    const res: any = await api.post("/c-endpoint/ai-chat/ask", {
      merchant_id: currentMerchantId.value,
      product_id: currentProductId.value,
      question,
      rewrite: rewrite.value,
    });
    if (res.code === 0 && res.data) {
      messages.value.push({
        role: "assistant",
        content: res.data.answer || "抱歉，暂时无法回答。",
        sources: res.data.sources || [],
      });
    } else {
      messages.value.push({
        role: "assistant",
        content: res.message || "服务异常，请稍后再试。",
      });
    }
  } catch (e: any) {
    messages.value.push({
      role: "assistant",
      content: "网络异常，请稍后再试。" + (e?.message || ""),
    });
  } finally {
    loading.value = false;
  }
}

// 人工客服发送消息
async function sendHuman(text: string) {
  if (!sessionId.value) return;
  // 先本地追加（乐观更新），用 _id: -1 标记为"待确认"
  const localMsg: any = { role: "user", content: text, _id: -1 };
  messages.value.push(localMsg);
  input.value = "";
  try {
    const res: any = await api.post("/c-endpoint/chat/send", {
      session_id: sessionId.value,
      message: text,
    });
    if (res.code === 0 && res.data) {
      // 用服务端返回的真实 ID 替换占位
      localMsg._id = res.data.message_id;
    } else {
      // 发送失败，移除本地消息，显示错误提示
      const idx = messages.value.indexOf(localMsg);
      if (idx !== -1) messages.value.splice(idx, 1);
      messages.value.push({
        role: "assistant",
        content: "发送失败：" + (res.message || ""),
      });
    }
  } catch (e: any) {
    const idx = messages.value.indexOf(localMsg);
    if (idx !== -1) messages.value.splice(idx, 1);
    messages.value.push({
      role: "assistant",
      content: "发送失败，请重试。" + (e?.message || ""),
    });
  }
}

// 加载消息
async function loadMessages() {
  if (!sessionId.value) return;
  try {
    const res: any = await api.get("/c-endpoint/chat/messages", {
      params: { session_id: sessionId.value },
    });
    if (res.code === 0 && res.data) {
      messages.value = (res.data as any[]).map((m: any) => ({
        role: m.sender_role === "buyer" ? "user" : "assistant",
        content: m.message,
        _id: m.id,
      }));
    }
  } catch {}
}

// 轮询新消息
async function pollMessages() {
  if (!sessionId.value) return;
  // 只计算已确认的消息 ID（_id > 0，排除本地乐观更新的占位 _id=-1）
  const confirmedIds = (messages.value as any[])
    .map((m: any) => m._id || 0)
    .filter((id: number) => id > 0);
  const maxId = confirmedIds.length > 0 ? Math.max(...confirmedIds) : 0;
  try {
    const res: any = await api.get("/c-endpoint/chat/messages", {
      params: {
        session_id: sessionId.value,
        after_id: maxId > 0 ? maxId : undefined,
      },
    });
    if (res.code === 0 && res.data && (res.data as any[]).length > 0) {
      for (const m of res.data as any[]) {
        if (m.sender_role !== "buyer") {
          // 只追加客服/商家/管理员的回复，不重复添加买家自己的消息
          messages.value.push({
            role: "assistant",
            content: m.message,
            _id: m.id,
          });
        }
      }
    }
  } catch {}
}

function startPolling() {
  stopPolling();
  pollTimer = setInterval(pollMessages, 3000);
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

onUnmounted(() => {
  stopPolling();
});

function detectMerchantId() {
  // 优先从 URL 路径判断（最可靠，避免 localStorage 残留污染）
  const pathMatch = window.location.pathname.match(/\/products?\/(\d+)/);
  if (pathMatch) {
    // 如果在商品详情页，从全局变量或 URL 获取对应 merchant_id
    const wany = (window as any).__currentMerchantId;
    if (wany) {
      currentMerchantId.value = Number(wany);
      return;
    }
  } else {
    // 不在商品详情页，使用默认商家 ID（首页等场景）
    currentMerchantId.value = 1;
    return;
  }

  // 兜底：从 query 参数找
  const params = new URLSearchParams(window.location.search);
  const mid = params.get("merchant_id") || params.get("merchantId");
  if (mid) {
    currentMerchantId.value = Number(mid);
    return;
  }

  currentMerchantId.value = 1;
}

function detectProductId(): number | null {
  // 优先从 URL 路径判断（最可靠）
  // 匹配 /product/7 或 /products/7
  const match = window.location.pathname.match(/\/products?\/(\d+)/);
  if (match) return Number(match[1]);

  // 再从 query 参数找
  const params = new URLSearchParams(window.location.search);
  const pid = params.get("product_id") || params.get("productId");
  if (pid) return Number(pid);

  // 最后才看全局变量（不可靠，因为页面切换后可能不会清除）
  const wany = (window as any).__currentProductId;
  if (wany) return Number(wany);

  return null;
}
</script>

<style scoped>
.ai-overlay {
  position: fixed;
  inset: 0;
  z-index: 9998;
  background: rgba(0, 0, 0, 0.18);
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  padding: 24px;
}
.ai-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
  color: #fff;
}
.ai-fab:hover { transform: scale(1.08); }
.ai-fab-badge {
  position: absolute;
  top: -4px; right: -4px;
  background: #ef4444;
  color: #fff;
  font-size: 11px;
  width: 18px; height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ai-panel {
  width: 380px;
  height: 540px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.18);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.25s ease;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
.ai-panel-header {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.ai-header-left { display: flex; align-items: center; gap: 8px; }
.ai-header-actions { display: flex; align-items: center; gap: 8px; }
.ai-panel-title { font-weight: 600; font-size: 15px; }
.ai-mode-btn {
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  color: #fff;
  font-size: 12px;
  padding: 3px 10px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}
.ai-mode-btn:hover { background: rgba(255,255,255,0.35); }
.ai-panel-close { background: none; border: none; color: #fff; font-size: 18px; cursor: pointer; }
.ai-status-dot { font-size: 10px; }
.ai-status-dot.waiting { color: #fbbf24; }
.ai-status-dot.active { color: #34d399; }
.ai-panel-body {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #f8f8fc;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.ai-welcome {
  text-align: center;
  color: #888;
  font-size: 13px;
  margin-top: 40%;
}
.ai-connect-row { display: flex; justify-content: center; margin-top: 16px; }
.ai-connect-btn {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  border: none;
  border-radius: 20px;
  padding: 10px 24px;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s;
}
.ai-connect-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.ai-connect-hint { text-align: center; color: #aaa; font-size: 12px; padding: 8px; }
.ai-msg { display: flex; }
.ai-msg.user { justify-content: flex-end; }
.ai-msg.assistant { justify-content: flex-start; }
.ai-msg-bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}
.ai-msg.user .ai-msg-bubble {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.ai-msg.assistant .ai-msg-bubble {
  background: #fff;
  color: #1f2937;
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 4px;
}
.ai-typing::after {
  content: '…';
  animation: blink 1s infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
.ai-sources { margin-top: 6px; font-size: 11px; color: #9ca3af; }
.ai-panel-footer {
  padding: 12px;
  border-top: 1px solid #e5e7eb;
  background: #fff;
}
.ai-rewrite-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #6366f1;
  margin-bottom: 8px;
  cursor: pointer;
}
.ai-input-row { display: flex; gap: 8px; }
.ai-input {
  flex: 1;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 14px;
  outline: none;
}
.ai-input:focus { border-color: #6366f1; }
.ai-send-btn {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
}
.ai-send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
