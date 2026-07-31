
<template>
  <div>
    <h1>
      属性绑定指令和事件绑定指令
    </h1>
    <!-- 表单通常用于用户需要进行输入的时候-->
    <form>
      <!-- 一个输入框，类型为文本，即字符串-->
      <!--
                - 作用：可以为 html 标签中的属性，绑定一个变量【也可以是常量】，从而通过变量【常量】的值来控制这个属性的内容
                - 语法：
                <标签 v-bind:属性名="变量【常量】"></标签>
                - 语法解释：
                  - 标签 --- html 中的标签名称
                  - v-bind:  --- 指令名称，叫做属性绑定指令
                  - 属性名 --- html 中的标签中的属性
                  - 变量【常量】 --- 变量定义在 js 中，常量就直接写
                - 语法糖：对于语法的简化版本
                <标签 :属性名="变量【常量】"></标签>
            -->
        账号：<input type="text" v-bind:disabled="isDisabled">
      <!-- 换行标签-->
      <br>
        密码：<input type='password'>
      <br>
      <!--
                点击按钮之后，需要去修改某个变量的值，通常情况我们在函数中来实现
                即点击按钮之后就应该去执行修改变量的值的函数 --- 等价于python中调用函数
                这个过程叫做事件绑定 --- 完成事件绑定的事件名称非常多，比如click【单击事件、用得最多的】、dblclick【双击事件】
                在vue中，如果想要点击按钮或者其他标签时去调用函数的执行，就需要使用语法指令 --- v-on:事件名称=函数名称(形参)
                语法糖：
                    1、如果函数没有参数，就可以去掉函数名称的括号  --- v-on:事件名称=函数名称
                    2、v-on: 可以缩写为 @ --- @事件名称=函数名称【我们使用的版本】
      -->
      <button type="button" @click="changeInput">登录</button>
    </form>
    <h1>
      控制内容显示与隐藏指令
    </h1>
    <!-- 控制内容显示与隐藏指令 v-if, v-show都可以实现，我们选择v-show
    v-show指令语法：
      <标签 v-show=布尔值></标签>
    通过布尔值来控制这个标签是否显示在页面上，如果为true，则显示，为false则隐藏
    -->
    <div v-show="isShow" style="border: 1px solid red; width: 100%;height: 30px">
      我显示了1
    </div>
    <div v-show="!isShow" style="border: 1px solid red; width: 100%;height: 30px">
      我显示了2
    </div>
    <button type="button" @click="isShow = !isShow">点我</button>
    <h1>双向绑定指令</h1>
    <!--
      双向绑定指令 --- v-model='变量名称'
      作用：它可以使html中的标签中的内容【一般都是输入，选择】，始终和绑定的变量是同一个值
      即：输入内容变量 = 变量变化，变量变化 = 输入内容变量
    -->
    <form>
      邮箱号：<input type="text":disabled="!isCode" id="email" v-model="email">
      <br>
      验证码：<input type="text":disabled="isCode" v-model="code">
      <br>
      <button type="button" @click="sendEmail" v-show="isCode">发送验证码</button>
      <button type="button" @click="checkCode" v-show="!isCode">验证验证码</button>
    </form>
    <h1>
      循环指令
    </h1>
    <!--循环指令 v-for ，用法和for循环雷同
        语法格式：
          <标签 v-for=(每次得到的内容, index) in 变量对象变量名称></标签>

        展示数据：
          在html中用表格，表格的基本组成：
            <table>
              <tr>
                <td></td>
                <td></td>
                <td></td>
              <tr>
            <table>
    -->
    <div>
      <table>
        <tr v-for="(item,index) in message">
            <!-- 在页面中起初js定义的变量,v-for循环中的变量等，直接用{{}}插值表达式 -->
            {{item.content}}
        </tr>
      </table>
    </div>
    <hr>
    <div v-for="(item,index) in message">
      <!-- 在页面中起初js定义的变量,v-for循环中的变量等，直接用{{}}插值表达式 -->
      {{item.content}}>
    </div>
  </div>
</template>

<script setup>
//导入响应式数据 --- 用于定义变量
import {ref} from "vue"
//定义一个变量， 类型为bool类型，默认为false
//let: JavaScript中的变量标识符，isDisabled为变量名称, ref定义变量的函数，false为变量的默认值
let isDisabled = ref(false)
//定义一个函数 --- 规则 --- function 函数名称(形参){函数体}
function changeInput(){
  //js中输出语句：console.log("输出语句")，等价于python中的print
  //js中的输出语句输出结果在浏览器的console【控制台】中而不是在IDE工具中
  //在函数中想要访问定义的变量的值 --- 变量名称.value
  isDisabled.value = !isDisabled.value;
}

//定义控制div显示与隐藏的变量
let isShow = ref(true);

//定义控制验证码输入的框是否可以输入的变量
let isCode = ref(true);

//定义保留邮箱号，验证码的变量
let email = ref("")
let code = ref("")

//定义登陆函数
function sendEmail(){
  isCode.value = !isCode.value;
  console.log(email.value);
}

//定义验证码函数
function checkCode(){
  console.log(email.value, code.value);
}

// 定义一个用户和AI问答的变量 --- 是一个数组，数组里面的元素就是一个js对象
let message = ref([
  {role: 'assistant', content: '你好，我是AI，你可以向我提问任何问题'},
  {role: 'user', content: '你叫什么名字？'},
  {role: 'assistant', content: '我叫ChatPT，一个基于GPT3.5的AI模型'},
  {role: 'user', content: '你喜欢什么书'},
  {role: 'assistant', content: '我喜欢《三体》'},
  {role: 'user', content: '你喜欢什么电影'},
  {role: 'assistant', content: '我喜欢《唐顿庄园》'},
])

</script>

<style scoped>

</style>