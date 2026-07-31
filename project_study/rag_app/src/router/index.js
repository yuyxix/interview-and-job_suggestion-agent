// 引入路由配置文件
import {createRouter, createWebHistory} from "vue-router";

//定义路由配置对象 --- 数组
const routes = [
    {// 一个页面的访问路径就是一格js对象，至少包含2个属性：path,component
        path: '/TestOne', // 访问路径，和服务器的请求路径访问规则一致
        component:()=>import('../components/TestOne.vue')
    },
    {
        path: '/TestTwo', // 访问路径，和服务器的请求路径访问规则一致
        component:()=>import('../components/TestTwo.vue')
    },
    {
        path: '', // 访问路径，和服务器的请求路径访问规则一致
        component:()=>import('../components/Login.vue')
    }
]
//设置路由模式为history模式 --- 默认为hash模式，访问路径中有一个#号
const router = createRouter({
    history: createWebHistory(),
    routes

})

// 导出路由实例
export default router