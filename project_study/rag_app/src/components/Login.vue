<template>
  <div class="login-container">
    <!-- 登录卡片 -->
    <el-card class="login-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="logo-area">
            <!-- 系统图标 -->
            <el-icon :size="36" color="#409eff">
              <ChatDotRound />
            </el-icon>
          </div>
          <h2 class="title">知识库问答系统</h2>
          <p class="subtitle">请输入邮箱地址，验证后即可使用</p>
        </div>
      </template>

      <!-- 登录表单 -->
      <el-form label-position="top" :model="formData">
        <!-- 邮箱输入框 -->
        <el-form-item label="邮箱地址">
          <el-input
            v-model="email"
            id="email"
            :disabled="!isCode"
            placeholder="请输入邮箱地址"
            size="large"
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <!-- 验证码输入框 -->
        <el-form-item label="验证码">
          <el-input
            v-model="code"
            :disabled="isCode"
            placeholder="请输入4位验证码"
            size="large"
            maxlength="6"
          >
            <template #prefix>
              <el-icon><Key /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <!-- 操作按钮区域 -->
        <el-form-item>
          <!-- 发送验证码按钮：在未发送验证码时显示 -->
          <el-button
            type="primary"
            class="submit-btn"
            size="large"
            @click="sendEmail"
            v-show="isCode"
            :loading="isSending"
          >
            <el-icon><Promotion /></el-icon>
            <span>发送验证码</span>
          </el-button>

          <!-- 验证验证码按钮：在已发送验证码后显示 -->
          <el-button
            type="success"
            class="submit-btn"
            size="large"
            @click="checkCode"
            v-show="!isCode"
            :loading="isVerifying"
          >
            <el-icon><Select /></el-icon>
            <span>验证并登录</span>
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 底部提示 -->
      <div class="footer-tip">
        <span>首次使用？验证码将发送至您填写的邮箱</span>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, getCurrentInstance } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Message, Key, ChatDotRound, Promotion, Select } from "@element-plus/icons-vue";

// ============================================================
// 路由与全局变量
// ============================================================
const router = useRouter();
let proxy = getCurrentInstance().proxy;

// ============================================================
// 响应式状态定义
// ============================================================

// isCode: true → 显示"发送验证码"按钮，邮箱可编辑
// isCode: false → 显示"验证验证码"按钮，验证码可编辑
let isCode = ref(true);

// 登录状态标记
let isLogin = ref(false);

// 邮箱地址
let email = ref("");

// 验证码
let code = ref("");

// 发送按钮加载状态
let isSending = ref(false);

// 验证按钮加载状态
let isVerifying = ref(false);

// ============================================================
// 发送验证码
// 调用后端接口 /users/sendEmail 发送验证码到指定邮箱
// ============================================================
function sendEmail() {
  // 基础校验：邮箱不能为空
  if (!email.value.trim()) {
    ElMessage.warning("请先输入邮箱地址");
    return;
  }

  let sendEmailAddr = email.value;
  isSending.value = true;

  proxy.$axios({
    url: "users/sendEmail",
    method: "get",
    params: {
      email: sendEmailAddr,
    },
  })
    .then((res) => {
      console.log(res);
      let codeVal = res.data.code;
      let msg = res.data.msg;
      let username = res.data.data;

      if (codeVal === 200) {
        // 切换表单状态：邮箱不可编辑，验证码可编辑
        isCode.value = !isCode.value;
        // 将用户名信息存储到 sessionStorage 中 --- getItem(key) 取出
        sessionStorage.setItem("username", username);
        ElMessage.success(msg || "验证码已发送，请查收邮箱");
      } else {
        ElMessage.error(msg || "发送失败");
      }
    })
    .catch((err) => {
      console.error("发送验证码失败:", err);
      ElMessage.error("网络异常，请稍后重试");
    })
    .finally(() => {
      isSending.value = false;
    });
}

// ============================================================
// 验证验证码并登录
// 调用后端接口 /users/Verification_Module 校验验证码
// ============================================================
function checkCode() {
  // 基础校验：验证码不能为空
  if (!code.value.trim()) {
    ElMessage.warning("请先输入验证码");
    return;
  }

  let checkEmail = {
    email: email.value,
    code: code.value,
  };

  isVerifying.value = true;

  proxy
    .$axios({
      url: "users/Verification_Module",
      method: "post",
      // 如果后端（FastAPI）用 Body() 或 Pydantic 模型接收 → 必须用 data
      // 如果后端用 Query() 接收 → 必须用 params
      data: JSON.stringify(checkEmail),
    })
    .then((res) => {
      console.log(res.data);
      let codeVal = res.data.code;
      let msg = res.data.msg;

      if (codeVal === 200) {
        isLogin.value = !isLogin.value;
        ElMessage.success("登录成功，正在跳转...");

        // 延迟跳转，给用户一个反馈时间
        setTimeout(() => {
          router.push("/Chat");
        }, 800);
      } else {
        ElMessage.error(msg || "验证失败");
      }
    })
    .catch((err) => {
      console.error("验证失败:", err);
      ElMessage.error("网络异常，请稍后重试");
    })
    .finally(() => {
      isVerifying.value = false;
    });
}
</script>

<style scoped>
/* ============================================================
   登录页面整体布局
   ============================================================ */
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  /* 使用柔和的专业配色替代强烈的渐变，降低 AI 感 */
  background: #f0f4f8;
  background-image:
    radial-gradient(ellipse at 20% 50%, rgba(64, 158, 255, 0.06) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 50%, rgba(64, 158, 255, 0.04) 0%, transparent 50%);
}

/* ============================================================
   登录卡片
   ============================================================ */
.login-card {
  width: 420px;
  padding: 10px;
  border-radius: 12px;
  border: 1px solid #e8ecf1;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  background: #ffffff;
}

/* 卡片头部去除默认边框 */
:deep(.el-card__header) {
  border-bottom: none;
  padding-bottom: 0;
}

/* ============================================================
   卡片头部内容
   ============================================================ */
.card-header {
  text-align: center;
}

.logo-area {
  margin-bottom: 12px;
  display: flex;
  justify-content: center;
}

.title {
  margin: 0 0 8px 0;
  font-size: 22px;
  font-weight: 600;
  color: #1a1a2e;
  letter-spacing: 0.5px;
}

.subtitle {
  margin: 0;
  color: #8c8c8c;
  font-size: 14px;
  line-height: 1.5;
}

/* ============================================================
   表单样式
   ============================================================ */
.el-form-item {
  margin-bottom: 20px;
}

/* 输入框圆角统一 */
:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  transition: box-shadow 0.25s;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset;
}

/* ============================================================
   提交按钮
   ============================================================ */
.submit-btn {
  width: 100%;
  height: 44px;
  border-radius: 8px;
  font-size: 15px;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

/* ============================================================
   底部提示
   ============================================================ */
.footer-tip {
  text-align: center;
  color: #b0b0b0;
  font-size: 12px;
  padding: 8px 0 4px;
}

/* ============================================================
   响应式适配 - 小屏幕
   ============================================================ */
@media (max-width: 480px) {
  .login-card {
    width: 92%;
    margin: 0 16px;
  }

  .title {
    font-size: 20px;
  }
}
</style>
