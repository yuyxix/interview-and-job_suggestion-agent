import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'


// 创建对象
const app = createApp(App)
app.use(router)
app.mount('#app')

// axios 配置
import axios from 'axios'  // 导入axios包
axios.defaults.baseURL = 'http://localhost:8000/' //服务器请求路径公共部分
axios.defaults.headers.post['Content-Type'] = 'application/json'  // post请求发送json数据给服务器
axios.defaults.headers.put['Content-Type'] = 'application/json'  //put请求发送json数据给服务器
app.config.globalProperties.$axios = axios  // 挂载axios，使用 对象.$axios 代替原生的axios
