<template>
  <div class="layout">
    <!-- ============================================================
         左侧边栏 - 历史记录
         ============================================================ -->
    <div class="sidebar">
      <!-- 新建对话按钮 -->
      <div class="sidebar-header">
        <span class="side-title">历史记录</span>
        <el-tooltip content="新建对话" placement="bottom">
          <el-button
            type="primary"
            :icon="Plus"
            circle
            size="small"
            @click="createNewConversation"
            :loading="isCreating"
          />
        </el-tooltip>
      </div>

      <!-- 搜索历史记录 -->
      <div class="search-area">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索历史记录..."
          size="default"
          clearable
          @input="filterHistory"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- 历史记录列表 -->
      <div class="history-list">
        <div
          class="history-item"
          v-for="(item, index) in filteredHistoryList"
          :key="index"
          :class="{ active: item.historyId === currentChatId }"
          @click="conversationLog(item.historyId)"
        >
          <el-icon class="history-icon"><ChatLineSquare /></el-icon>
          <span class="history-title">{{ item.title }}</span>
          <!-- 删除对话记录 -->
          <el-popconfirm
            title="确定删除该对话记录？"
            confirm-button-text="删除"
            cancel-button-text="取消"
            @confirm="deleteHistory(item.historyId)"
            @click.stop
          >
            <template #reference>
              <el-icon class="history-delete" @click.stop><Delete /></el-icon>
            </template>
          </el-popconfirm>
        </div>

        <!-- 无历史记录时的占位提示 -->
        <div class="history-empty" v-if="filteredHistoryList.length === 0">
          <el-icon :size="32" color="#c0c4cc"><Document /></el-icon>
          <p>{{ searchKeyword ? '未找到匹配记录' : '暂无历史记录' }}</p>
        </div>
      </div>
    </div>

    <!-- ============================================================
         右侧聊天主体
         ============================================================ -->
    <div class="chat-container">
      <!-- 顶部信息栏 -->
      <div class="header">
        <div class="header-left">
          <el-avatar :size="36" icon="UserFilled" />
          <span class="welcome-text">{{ username }}</span>
        </div>
        <div class="header-right">
          <el-tag size="small" type="info" effect="plain">AI助手</el-tag>
        </div>
      </div>

      <!-- 聊天消息区域 -->
      <div class="chat-box" ref="chatBoxRef">
        <!-- 空状态提示 -->
        <div class="chat-empty" v-if="messages.length === 0">
          <el-icon :size="48" color="#dcdfe6"><ChatLineSquare /></el-icon>
          <h3>开始新的检索</h3>
          <p>在下方输入您想要查询的内容，系统将在知识库中进行检索并返回结果</p>
        </div>

        <!-- 消息列表 -->
        <div
          v-for="(item, index) in messages"
          :key="index"
          :class="['message', item.role]"
        >
          <!-- 消息头像 -->
          <div class="msg-avatar">
            <el-avatar :size="32" v-if="item.role === 'user'" icon="UserFilled" />
            <el-avatar :size="32" v-else>
              <el-icon :size="18"><Search /></el-icon>
            </el-avatar>
          </div>

          <!-- 消息气泡 -->
          <div class="msg-body">
            <div class="msg-name">
              {{ item.role === 'user' ? username || '用户' : 'AI助手' }}
            </div>
            <div class="bubble" v-html="formatContent(item.content)">
            </div>
          </div>
        </div>

        <!-- 加载提示（流式输出中） -->
        <div class="typing-indicator" v-if="isStreaming">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      <!-- 底部输入区域 -->
      <div class="input-area">
        <el-input
          v-model="question"
          placeholder="输入查询内容，按回车发送"
          size="large"
          clearable
          @keyup.enter="chat"
          :disabled="isStreaming"
        >
          <template #suffix>
            <el-tooltip content="清空内容" placement="top" v-if="question">
              <el-icon
                class="clear-icon"
                @click="question = ''"
              >
                <CircleClose />
              </el-icon>
            </el-tooltip>
          </template>
        </el-input>

        <el-button
          type="primary"
          size="large"
          @click="chat"
          :disabled="isInput || isStreaming"
          class="send-btn"
        >
          <el-icon><Promotion /></el-icon>
        </el-button>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, getCurrentInstance, onMounted, watch, nextTick } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Plus,
  Search,
  ChatLineSquare,
  Document,
  Promotion,
  CircleClose,
  Delete,
} from "@element-plus/icons-vue";

// ============================================================
// 全局代理对象
// ============================================================

// 创建代理对象，用于访问挂载在全局属性上的 axios
let proxy = getCurrentInstance().proxy;

// ============================================================
// 响应式状态定义
// ============================================================

// 当前用户名（从 sessionStorage 读取）
let username = ref(sessionStorage.getItem("username"));

// 用户输入的问题
let question = ref("");

// 保存聊天消息的对象数组，每项包含 role 和 content
// role: 'user' → 用户消息；'assistant' → 检索结果
let messages = ref([]);

// 输入框禁用状态：内容为空时禁用发送按钮
let isInput = ref(true);

// 流式输出状态标记
let isStreaming = ref(false);

// 历史记录菜单列表
let historyList = ref([]);

// 过滤后的历史记录列表（用于搜索展示）
let filteredHistoryList = ref([]);

// 搜索关键词
let searchKeyword = ref("");

// 新建对话加载状态
let isCreating = ref(false);

// 当前选中的对话窗口 historyId
const currentChatId = ref(0);

// 聊天区域 DOM 引用，用于自动滚动到底部
const chatBoxRef = ref(null);

// ============================================================
// 实时监听输入框状态
// 使用 watch 监听输入框变化，输入框内容为空时禁用发送按钮
// ============================================================
watch(question, (newVal) => {
  isInput.value = newVal.trim().length === 0;
});

// ============================================================
// 核心：发送消息并与后端进行 SSE 流式通信
// ============================================================
function chat() {
  let myQuestion = question.value.trim();

  // 将用户的问题赋给 myQuestion 变量，然后清空输入框
  // trim() 函数去掉字符串首尾的空格
  question.value = "";

  // 空内容拦截
  if (myQuestion.length === 0) {
    ElMessage.warning("请输入查询内容");
    return;
  }

  // 标记流式输出开始
  isStreaming.value = true;

  // 将用户消息追加到消息列表
  messages.value.push({
    role: "user",
    content: myQuestion,
  });

  // 先追加一条占位消息，后续用流式结果替换
  messages.value.push({
    role: "assistant",
    content: "正在生成回复中...",
  });

  // -------- 构造 SSE 请求 --------

  // 创建查询参数对象
  let urlSearchParams = new URLSearchParams({
    question: myQuestion,
    historyId: currentChatId.value,
    // 这里的 key 一定要是 question，前后端保持一致
  });

  // 创建 EventSource 请求对象，与后端 SSE 接口建立长连接
  let es = new EventSource(
    "http://localhost:8000/chat/chat?" + urlSearchParams.toString()
  );

  // 用于累积流式返回的文本片段
  // 定义一个变量 --- 拼接结果
  let s = "";

  // -------- SSE 事件监听 --------

  // 1. onmessage：每次收到服务器推送的数据时触发
  es.onmessage = (e) => {
    // 解析服务器返回的 JSON 数据
    let data = JSON.parse(e.data).content;

    // 如果收到结束标记 [DONE]，关闭连接并结束流式输出
    if (data === "[DONE]") {
      es.close();
      isStreaming.value = false;
      // 调用保存聊天记录的方法
      saveConversationResult(myQuestion, s)


      // 新对话创建后，刷新历史记录菜单
      query_history_menu();
      return;
    }

    // 拼接流式文本片段
    s += data;

    // 替换消息列表中最后一条（占位消息）的内容为实时拼接结果
    messages.value[messages.value.length - 1].content = s;

    // 自动滚动到最新消息
    scrollToBottom();
  };

  // 2. onerror：连接出错时触发
  es.onerror = (e) => {
    console.error("SSE 连接异常:", e);
    es.close();
    isStreaming.value = false;

    // 如果流式输出中断且没有内容，给出错误提示
    if (s.length === 0) {
      messages.value[messages.value.length - 1].content =
        "服务器繁忙，请稍后再试";
    }
  };
}

// ============================================================
// 滚动到聊天区域底部
// ============================================================
function scrollToBottom() {
  nextTick(() => {
    if (chatBoxRef.value) {
      chatBoxRef.value.scrollTop = chatBoxRef.value.scrollHeight;
    }
  });
}

// ============================================================
// 格式化消息内容（支持简单的 Markdown 换行）
// ============================================================
function formatContent(content) {
  if (!content) return "";
  // 将换行符转为 HTML 换行标签
  return content.replace(/\n/g, "<br>");
}

// ============================================================
// 创建新对话
// 调用后端接口 /history/newConversation 新建一个对话窗口
// ============================================================
function createNewConversation() {
  isCreating.value = true;

  proxy
    .$axios({
      url: "history/newConversation",
      method: "post",
      data: JSON.stringify({
        username: username.value,
      }),
    })
    .then((res) => {
      console.log("新建对话:", res.data);
      let codeVal = res.data.code;
      let data = res.data.data;

      if (codeVal === 200) {
        // 清空当前消息列表
        messages.value = [];
        // 重置当前对话 ID
        currentChatId.value = data.historyId || 0;
        // 刷新历史记录菜单
        query_history_menu();
        ElMessage.success("新对话已创建");
      } else {
        ElMessage.error(res.data.msg || "创建失败");
      }
    })
    .catch((err) => {
      console.error("创建新对话失败:", err);
      // 即使接口不可用，也允许在前端清空对话区域
      messages.value = [];
      currentChatId.value = 0;
      ElMessage.info("已开启新对话");
    })
    .finally(() => {
      isCreating.value = false;
    });
}

// ============================================================
// 搜索过滤历史记录
// 优先使用客户端本地过滤；当关键词长度 >= 2 时也调用后端搜索接口
// ============================================================
function filterHistory() {
  let keyword = searchKeyword.value.trim().toLowerCase();

  if (!keyword) {
    // 无搜索关键词时展示全部历史记录
    filteredHistoryList.value = historyList.value;
    return;
  }

  // 客户端过滤：按标题模糊匹配
  filteredHistoryList.value = historyList.value.filter((item) => {
    return item.title && item.title.toLowerCase().includes(keyword);
  });

  // 同时调用后端搜索接口（异步补充结果）
  if (keyword.length >= 2) {
    searchHistoryFromServer(keyword);
  }
}

// ============================================================
// 后端搜索历史记录（可选接口）
// 调用 /history/searchHistory 获取服务端搜索结果
// ============================================================
function searchHistoryFromServer(keyword) {
  proxy
    .$axios({
      url: "chat/searchHistory",
      method: "get",
      params: {
        username: username.value,
        keyword: keyword,
      },
    })
    .then((res) => {
      console.log("搜索结果:", res.data);
      if (res.data.code === 200 && res.data.data) {
        // 后端搜索结果与前端过滤结果合并去重
        let serverResults = res.data.data;
        let existingIds = new Set(
          filteredHistoryList.value.map((item) => item.historyId)
        );
        serverResults.forEach((item) => {
          if (!existingIds.has(item.historyId)) {
            filteredHistoryList.value.push(item);
          }
        });
      }
    })
    .catch((err) => {
      // 搜索接口不可用时静默处理，前端过滤已生效
      console.warn("后端搜索接口不可用，使用本地过滤:", err.message);
    });
}

// ============================================================
// 查询聊天历史记录菜单栏
// 调用后端接口 /history/queryHistoryMenu 获取当前用户的历史对话列表
// ============================================================
function query_history_menu() {
  proxy
    .$axios({
      url: "history/queryHistoryMenu",
      method: "get",
      params: {
        username: username.value,
      },
    })
    .then((res) => {
      historyList.value = res.data.data || [];
      // 同步更新过滤列表
      filteredHistoryList.value = historyList.value;
      console.log("历史记录菜单:", res.data.data);
    })
    .catch((err) => {
      console.error("获取历史记录失败:", err);
    });
}

// ============================================================
// 点击历史记录项，加载对应对话内容
// 调用后端接口 /history/conversationLog 获取指定对话的完整消息
// ============================================================
function conversationLog(historyId) {
  // 更新当前选中的对话 ID
  currentChatId.value = historyId;

  proxy
    .$axios({
      url: "history/conversationLog",
      method: "get",
      params: {
        historyId: historyId,
      },
    })
    .then((res) => {
      messages.value = res.data.data || [];
      // 加载完成后滚动到底部
      scrollToBottom();
    })
    .catch((err) => {
      console.error("加载对话记录失败:", err);
      ElMessage.error("加载对话记录失败");
    });
}

// 保存对话结果
function saveConversationResult(question, answer) {
  proxy.$axios({
    url: 'chat/saveConversationResult',
    method : 'post',
    data: JSON.stringify({
      question: question,
      username: username.value,
      parentId: currentChatId.value,
      answer: answer,
    })
    }).then(res => {
      // 只有当currentChatId=0时，才需要把新增的数据的hiestoryId赋值给它【表示一个新对话的开始】
      // 如果currentChatId!=0, 说明当前点击的是一个已有的对话窗口，那么就不需要再赋值了【因为新传过来的historyId是子对话的】
      if (currentChatId.value === 0) {
        currentChatId.value = res.data.data
      }
      // 重新加载菜单栏
      query_history_menu();
  });
}

// ============================================================
// 删除历史对话记录
// 调用后端接口 /history/deleteHistory 删除指定对话
// ============================================================
function deleteHistory(historyId) {
  proxy.$axios({
    url: 'chat/deleteConversationHistory',
    method: 'post',
    data: JSON.stringify({
      historyId: historyId,
    }),
  }).then(res => {
    if (res.data.code === 200) {
      // 从本地列表中移除该记录
      historyList.value = historyList.value.filter(item => item.historyId !== historyId);
      filteredHistoryList.value = filteredHistoryList.value.filter(item => item.historyId !== historyId);
      // 如果删除的是当前打开的对话，清空消息区
      if (currentChatId.value === historyId) {
        currentChatId.value = 0;
        messages.value = [];
      }
      ElMessage.success('删除成功');
    } else {
      ElMessage.error(res.data.msg || '删除失败');
    }
  }).catch(err => {
    console.error('删除记录失败:', err);
    ElMessage.error('删除失败，请稍后重试');
  });
}

// ============================================================
// 页面挂载时自动执行
// ============================================================
onMounted(() => {
  // 从 sessionStorage 读取用户名
  username.value = sessionStorage.getItem("username");

  // 获取历史记录菜单栏
  query_history_menu();
});
</script>

<style scoped>
/* ============================================================
   整体布局
   ============================================================ */
.layout {
  width: 90%;
  max-width: 1200px;
  height: 88vh;
  margin: 32px auto;
  display: flex;
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #e8ecf1;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
}

/* ============================================================
   左侧边栏 - 历史记录
   ============================================================ */
.sidebar {
  width: 280px;
  background: #fafbfc;
  border-right: 1px solid #e8ecf1;
  display: flex;
  flex-direction: column;
}

/* 侧边栏头部 */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 18px 12px;
}

.side-title {
  font-size: 17px;
  font-weight: 600;
  color: #1a1a2e;
}

/* 搜索区域 */
.search-area {
  padding: 0 16px 12px;
}

.search-area :deep(.el-input__wrapper) {
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 0 0 1px #e8ecf1 inset;
}

.search-area :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

/* 历史记录列表 */
.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 12px 16px;
}

/* 历史记录列表滚动条 */
.history-list::-webkit-scrollbar {
  width: 4px;
}

.history-list::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 4px;
}

/* 单条历史记录 */
.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  margin-bottom: 4px;
  border-radius: 8px;
  color: #4a5568;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.history-item:hover {
  background: #edf2f7;
  color: #1a1a2e;
}

.history-item.active {
  background: #e8f0fe;
  color: #1a56db;
}

.history-icon {
  flex-shrink: 0;
  color: #909399;
}

.history-item.active .history-icon {
  color: #1a56db;
}

.history-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 删除按钮：默认隐藏，hover 时显示 */
.history-delete {
  flex-shrink: 0;
  color: #c0c4cc;
  font-size: 15px;
  opacity: 0;
  transition: opacity 0.2s, color 0.2s;
}

.history-item:hover .history-delete {
  opacity: 1;
}

.history-delete:hover {
  color: #e64552;
}

/* 无历史记录占位 */
.history-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #c0c4cc;
  text-align: center;
}

.history-empty p {
  margin-top: 12px;
  font-size: 13px;
  color: #909399;
}

/* ============================================================
   聊天主体区域
   ============================================================ */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #ffffff;
}

/* ============================================================
   顶部信息栏
   ============================================================ */
.header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.welcome-text {
  font-size: 15px;
  font-weight: 500;
  color: #1a1a2e;
}

/* ============================================================
   聊天消息区域
   ============================================================ */
.chat-box {
  flex: 1;
  padding: 24px 28px;
  overflow-y: auto;
  background: #fafbfc;
}

/* 聊天区域滚动条 */
.chat-box::-webkit-scrollbar {
  width: 5px;
}

.chat-box::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 6px;
}

/* 空状态 */
.chat-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #c0c4cc;
  text-align: center;
}

.chat-empty h3 {
  margin: 16px 0 8px;
  font-size: 17px;
  font-weight: 500;
  color: #909399;
}

.chat-empty p {
  margin: 0;
  font-size: 14px;
  color: #b0b0b0;
  max-width: 360px;
  line-height: 1.6;
}

/* ============================================================
   消息条目
   ============================================================ */
.message {
  display: flex;
  gap: 12px;
  margin-bottom: 22px;
  animation: msgIn 0.3s ease;
}

@keyframes msgIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

/* 用户消息靠右对齐 */
.message.user {
  flex-direction: row-reverse;
}

/* 消息头像 */
.msg-avatar {
  flex-shrink: 0;
}

.message.user .msg-avatar :deep(.el-avatar) {
  background: #e8f0fe;
  color: #1a56db;
}

.message.assistant .msg-avatar :deep(.el-avatar) {
  background: #f0f4f8;
  color: #4a5568;
}

/* 消息主体 */
.msg-body {
  max-width: 68%;
  min-width: 80px;
}

/* 消息发送者名称 */
.msg-name {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
  padding: 0 4px;
}

.message.user .msg-name {
  text-align: right;
}

/* 消息气泡 */
.bubble {
  padding: 12px 18px;
  border-radius: 10px;
  line-height: 1.65;
  font-size: 14px;
  color: #1a1a2e;
  word-break: break-word;
}

/* 用户消息气泡 - 蓝色系，简洁专业 */
.message.user .bubble {
  background: #1a56db;
  color: #ffffff;
  border-bottom-right-radius: 4px;
  box-shadow: 0 2px 8px rgba(26, 86, 219, 0.18);
}

/* 检索结果气泡 - 浅灰底，干净清晰 */
.message.assistant .bubble {
  background: #ffffff;
  border: 1px solid #e8ecf1;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

/* ============================================================
   流式输出加载指示器
   ============================================================ */
.typing-indicator {
  display: flex;
  gap: 5px;
  padding: 12px 18px;
}

.typing-indicator span {
  width: 7px;
  height: 7px;
  background: #c0c4cc;
  border-radius: 50%;
  animation: typingBounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typingBounce {
  0%,
  80%,
  100% {
    transform: scale(0.6);
  }
  40% {
    transform: scale(1);
  }
}

/* ============================================================
   底部输入区域
   ============================================================ */
.input-area {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  background: #ffffff;
}

.input-area :deep(.el-input__wrapper) {
  border-radius: 10px;
  padding: 4px 12px;
  box-shadow: 0 0 0 1px #e8ecf1 inset;
  transition: box-shadow 0.25s;
}

.input-area :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

.input-area :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #1a56db inset;
}

.clear-icon {
  cursor: pointer;
  color: #c0c4cc;
  transition: color 0.2s;
}

.clear-icon:hover {
  color: #909399;
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  flex-shrink: 0;
}

/* ============================================================
   响应式适配 - 平板
   ============================================================ */
@media (max-width: 900px) {
  .layout {
    width: 96%;
    margin: 16px auto;
  }

  .sidebar {
    width: 220px;
  }

  .msg-body {
    max-width: 80%;
  }

  .chat-box {
    padding: 16px 16px;
  }
}

/* ============================================================
   响应式适配 - 手机
   ============================================================ */
@media (max-width: 640px) {
  .layout {
    height: 100vh;
    margin: 0;
    border-radius: 0;
    border: none;
  }

  /* 移动端隐藏侧边栏 */
  .sidebar {
    display: none;
  }

  .msg-body {
    max-width: 88%;
  }

  .header {
    padding: 0 16px;
  }

  .input-area {
    padding: 12px 16px;
  }
}
</style>
