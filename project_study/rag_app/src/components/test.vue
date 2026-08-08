<template>
  <!-- 最外层容器，包裹整个对话框 -->
  <div>
    <!-- 遍历 messages 数组，把每一条消息渲染成一个 div -->
    <!-- msg 是当前消息内容，i 是索引（用作唯一 key） -->
    <div v-for="(msg, i) in messages" :key="i">{{ msg }}</div>

    <!-- 表单容器，@submit.prevent 阻止回车时刷新页面 -->
    <form @submit.prevent="getReply">
      <!-- 输入框，v-model 双向绑定 text 变量 -->
      <input v-model="question" placeholder="问点什么..." />
      <!-- 提交按钮，点击或回车都会触发 send 函数 -->
      <button>发送</button>
    </form>
  </div>
</template>

<script setup>
import {ref, getCurrentInstance} from "vue";

let question = ref("");
let message = ref("");
const messages = ref(['你好，我是AI测试助手'])

let proxy = getCurrentInstance().proxy;

function getReply() {
  proxy.$axios({
    url: '/users/aiReply',          // ① 加前导斜杠
    method: 'get',
    params: {
      question: question.value       // ② 取 .value
    }
  }).then(res => {
    console.log(res.data)            // 注意：响应数据在 res.data 里
    messages.value.push(question.value)
    messages.value.push(res.data.msg)
  })
}
</script>

<style scoped>

</style>