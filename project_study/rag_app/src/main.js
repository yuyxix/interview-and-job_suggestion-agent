import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// 注册路由对象
import router from './router'

// 注册element-plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// axios 配置
import axios from 'axios'  // 导入axios包
axios.defaults.baseURL = 'http://localhost:8000/' //服务器请求路径公共部分
axios.defaults.headers.post['Content-Type'] = 'application/json'  // post请求发送json数据给服务器
axios.defaults.headers.put['Content-Type'] = 'application/json'  //put请求发送json数据给服务器

// 创建对象
const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.config.globalProperties.$axios = axios  // 挂载axios，使用 对象.$axios 代替原生的axios
app.mount('#app')




