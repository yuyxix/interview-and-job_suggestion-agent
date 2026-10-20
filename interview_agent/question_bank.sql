/*
 Navicat Premium Dump SQL

 Source Server         : sanxia
 Source Server Type    : MySQL
 Source Server Version : 80300 (8.3.0)
 Source Host           : localhost:3306
 Source Schema         : agent_08_03

 Target Server Type    : MySQL
 Target Server Version : 80300 (8.3.0)
 File Encoding         : 65001

 Date: 15/09/2026 10:01:54
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for question_bank
-- ----------------------------
DROP TABLE IF EXISTS `question_bank`;
CREATE TABLE `question_bank`  (
  `question_id` bigint NOT NULL AUTO_INCREMENT COMMENT '题目ID',
  `question_title` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '题目',
  `answer` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '答案',
  `question_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '题目类型：技术知识/项目经历/场景题/行为题',
  `question_subject` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '题目科目：Java/前端/Python/算法/数据库/Spring',
  PRIMARY KEY (`question_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 131 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '题库表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of question_bank
-- ----------------------------
INSERT INTO `question_bank` VALUES (1, 'Java的基本数据类型有哪些？各自占多少字节？', 'byte(1字节)、short(2字节)、int(4字节)、long(8字节)、float(4字节)、double(8字节)、char(2字节)、boolean(1位)', '技术知识', 'Java');
INSERT INTO `question_bank` VALUES (2, 'HashMap的底层实现原理是什么？JDK1.7和1.8的区别？', 'JDK1.7：数组+链表，头插法；JDK1.8：数组+链表+红黑树，尾插法。当链表长度>8且数组长度>=64时转为红黑树，扩容时保持顺序', '技术知识', 'Java');
INSERT INTO `question_bank` VALUES (3, 'synchronized和ReentrantLock的区别？', '1.synchronized是关键字，Lock是接口；2.synchronized自动释放锁，Lock需手动释放；3.Lock可中断、可超时、可公平；4.synchronized支持锁升级', '技术知识', 'Java');
INSERT INTO `question_bank` VALUES (4, 'JVM内存模型包含哪些部分？', '堆（Heap）、方法区（Method Area）、虚拟机栈（VM Stack）、本地方法栈（Native Method Stack）、程序计数器（Program Counter Register）', '技术知识', 'Java');
INSERT INTO `question_bank` VALUES (5, 'Spring Boot自动配置的原理是什么？', '@EnableAutoConfiguration通过META-INF/spring.factories加载配置类，配合@Conditional条件注解实现按需加载', '技术知识', 'Java');
INSERT INTO `question_bank` VALUES (6, 'MySQL的索引类型有哪些？', '主键索引、唯一索引、普通索引、全文索引、组合索引。从数据结构分：B+树索引、Hash索引', '技术知识', '数据库');
INSERT INTO `question_bank` VALUES (7, '什么是线程池？ThreadPoolExecutor的核心参数？', 'corePoolSize核心线程数、maximumPoolSize最大线程数、keepAliveTime空闲时间、workQueue工作队列、threadFactory线程工厂、handler拒绝策略', '技术知识', 'Java');
INSERT INTO `question_bank` VALUES (8, 'Redis的数据类型有哪些？', 'String字符串、Hash哈希、List列表、Set集合、ZSet有序集合、HyperLogLog、Geo地理位置、Stream流', '技术知识', '数据库');
INSERT INTO `question_bank` VALUES (9, '什么是CAS？存在什么问题？', 'Compare And Swap比较并交换，乐观锁实现。问题：ABA问题、循环开销大、只能保证单个变量原子性', '技术知识', 'Java');
INSERT INTO `question_bank` VALUES (10, 'Spring IOC和AOP的原理？', 'IOC控制反转，通过反射创建对象并由容器管理；AOP面向切面，通过动态代理（JDK Proxy或CGLIB）实现横切逻辑', '技术知识', 'Java');
INSERT INTO `question_bank` VALUES (11, '请介绍一个你做过的最复杂的Java项目？', '可以从项目背景、技术栈、负责模块、技术难点、解决方案、项目成果几个方面回答。重点突出个人贡献和技术挑战', '项目经历', 'Java');
INSERT INTO `question_bank` VALUES (12, '你在项目中遇到过的技术难题是什么？如何解决的？', '例如：内存溢出问题、性能瓶颈、并发问题、数据一致性等。按照STAR法则描述：Situation背景、Task任务、Action行动、Result结果', '项目经历', 'Java');
INSERT INTO `question_bank` VALUES (13, '你们项目的架构是什么样的？为什么这样设计？', '可以描述：微服务/单体架构、分层设计、技术选型考虑、扩展性设计、高可用方案等，说明设计背后的思考', '项目经历', 'Java');
INSERT INTO `question_bank` VALUES (14, '项目中如何处理高并发场景？', '缓存（Redis）、异步（MQ）、限流（令牌桶/漏桶）、降级熔断（Hystrix/Sentinel）、数据库读写分离、分库分表等', '项目经历', 'Java');
INSERT INTO `question_bank` VALUES (15, '你们项目的数据库是怎么设计的？做了哪些优化？', '表结构设计原则、索引优化、慢SQL排查、分库分表策略、读写分离、数据归档等实践', '项目经历', '数据库');
INSERT INTO `question_bank` VALUES (16, '项目中如何保证数据一致性？', '本地事务、分布式事务（2PC/TCC/Seata）、最终一致性、消息事务、补偿机制等', '项目经历', 'Java');
INSERT INTO `question_bank` VALUES (17, '你们项目的缓存是如何设计的？', '缓存策略（旁路缓存/穿透/击穿/雪崩预防）、缓存更新策略、分布式缓存（Redis Cluster/Sentinel）、本地缓存（Caffeine）', '项目经历', 'Java');
INSERT INTO `question_bank` VALUES (18, '项目中用过哪些设计模式？在哪些场景？', '工厂模式（BeanFactory）、单例模式（Spring Bean）、策略模式（支付方式）、模板方法（JdbcTemplate）、观察者模式（事件监听）', '项目经历', 'Java');
INSERT INTO `question_bank` VALUES (19, '你们项目的权限管理是怎么实现的？', 'RBAC模型、Spring Security/Shiro、JWT/OAuth2、接口权限、数据权限、菜单权限等', '项目经历', 'Java');
INSERT INTO `question_bank` VALUES (20, '项目上线后遇到过的线上问题？如何排查的？', 'CPU飙升、内存泄漏、死锁、接口超时等问题，描述排查工具（jstack/jstat/arthas）和解决过程', '项目经历', 'Java');
INSERT INTO `question_bank` VALUES (21, '如何设计一个秒杀系统？', '1.前端限流（按钮置灰）2.CDN静态化 3.Redis预减库存 4.MQ异步下单 5.数据库乐观锁 6.限流降级 7.数据最终一致性', '场景题', 'Java');
INSERT INTO `question_bank` VALUES (22, '设计一个短链接生成系统？', '1.发号器生成唯一ID（雪花算法/Redis自增）2.转62进制缩短 3.缓存热点映射 4.过期策略 5.跳转302重定向', '场景题', 'Java');
INSERT INTO `question_bank` VALUES (23, '如何防止订单重复支付？', '1.前端防抖 2.幂等性设计（唯一索引/Token机制/状态机）3.数据库乐观锁 4.支付回调幂等处理', '场景题', 'Java');
INSERT INTO `question_bank` VALUES (24, '设计一个分布式锁，有哪些实现方式？', '1.Redis SETNX+Lua脚本 2.Redisson 3.ZooKeeper临时顺序节点 4.数据库乐观锁。需要考虑：死锁、重入、锁超时', '场景题', 'Java');
INSERT INTO `question_bank` VALUES (25, '如何实现一个延迟队列？', '1.Redis ZSet按时间戳排序 2.RabbitMQ死信队列 3.Redis过期通知 4.时间轮算法（Netty/HashedWheelTimer）', '场景题', 'Java');
INSERT INTO `question_bank` VALUES (26, '系统压力测试怎么做？指标有哪些？', '压测工具：JMeter/LoadRunner/Gatling。指标：QPS、TPS、响应时间、CPU/内存/IO使用率、错误率', '场景题', 'Java');
INSERT INTO `question_bank` VALUES (27, '如何设计一个日志监控系统？', 'ELK（Elasticsearch+Logstash+Kibana）、Filebeat采集、链路追踪（SkyWalking/Pinpoint）、告警机制', '场景题', 'Java');
INSERT INTO `question_bank` VALUES (28, '设计一个排行榜功能？', 'Redis ZSet存储、按分数排序、分页查询、定期合并更新、缓存热点数据', '场景题', '数据库');
INSERT INTO `question_bank` VALUES (29, '如何处理消息积压？', '1.临时扩容消费者 2.增加Topic分区 3.优化消费逻辑 4.降级处理 5.排查消费慢的原因（IO/网络/代码）', '场景题', 'Java');
INSERT INTO `question_bank` VALUES (30, '如何实现接口幂等性？', '1.唯一请求号 2.Token机制（预生成Token）3.数据库唯一约束 4.状态机校验 5.Redis分布式锁 6.乐观锁版本号', '场景题', 'Java');
INSERT INTO `question_bank` VALUES (31, '你为什么选择做Java后端开发？', '可以从兴趣驱动（热爱编程）、技术优势（Java生态完善）、职业规划（长期深耕）、成就感（解决问题）等方面回答', '行为题', 'Java');
INSERT INTO `question_bank` VALUES (32, '你遇到过最大的挑战是什么？如何克服的？', '举例说明困难情况，展示解决问题的思路、学习能力、坚持态度，最终获得成长', '行为题', 'Java');
INSERT INTO `question_bank` VALUES (33, '如果和同事有技术分歧，你会怎么处理？', '1.尊重沟通 2.数据说话（测试对比）3.参考最佳实践 4.如果时间紧迫可A/B测试 5.求同存异，目标一致', '行为题', 'Java');
INSERT INTO `question_bank` VALUES (34, '你平时如何学习新技术？', '官方文档、技术博客（CSDN/掘金）、GitHub开源项目、技术社群、付费课程、源码阅读、实践项目', '行为题', 'Java');
INSERT INTO `question_bank` VALUES (35, '对加班怎么看？', '理解项目需要，但注重效率；提升自身能力减少无效加班；平衡工作生活，保持长期可持续发展', '行为题', 'Java');
INSERT INTO `question_bank` VALUES (36, '你未来的职业规划是什么？', '技术深度（架构师方向）+ 业务广度（领域专家）+ 软技能提升（沟通/管理）的复合发展', '行为题', 'Java');
INSERT INTO `question_bank` VALUES (37, '为什么从上家公司离职？', '客观原因（职业发展、技术栈、业务方向）正面表达，不抱怨，展现进取心', '行为题', 'Java');
INSERT INTO `question_bank` VALUES (38, '你觉得自己最大的优点和缺点是什么？', '优点与岗位相关（学习能力强/责任心）；缺点说非核心短板且有改进方案（公开演讲少但主动参与技术分享）', '行为题', 'Java');
INSERT INTO `question_bank` VALUES (39, '在团队中你通常扮演什么角色？', '根据实际情况：技术攻坚者/协调沟通者/方案设计者/质量守护者，举例说明', '行为题', 'Java');
INSERT INTO `question_bank` VALUES (40, '你对薪资的期望是多少？', '结合市场行情、自身能力、公司平台综合考量，给出合理范围，表达可以协商的态度', '行为题', 'Java');
INSERT INTO `question_bank` VALUES (41, 'HTML5新增了哪些语义化标签？', '<header>、<nav>、<article>、<section>、<aside>、<footer>、<main>、<figure>、<figcaption>、<mark>、<time>等，使页面结构更清晰，有利于SEO和可访问性', '技术知识', '前端');
INSERT INTO `question_bank` VALUES (42, 'CSS盒模型是什么？标准盒模型和怪异盒模型的区别？', '盒模型由content、padding、border、margin组成。标准盒模型：width=content；怪异盒模型（IE盒模型）：width=content+padding+border。通过box-sizing切换', '技术知识', '前端');
INSERT INTO `question_bank` VALUES (43, 'JavaScript中let、const、var的区别？', '1.var有变量提升，let/const没有；2.var可重复声明，let/const不可；3.let/const有块级作用域；4.const声明常量必须初始化且不可变', '技术知识', '前端');
INSERT INTO `question_bank` VALUES (44, '什么是事件冒泡和事件捕获？如何阻止？', '事件冒泡：从目标元素向上传播；事件捕获：从根元素向下传播。阻止冒泡：e.stopPropagation()；阻止默认行为：e.preventDefault()', '技术知识', '前端');
INSERT INTO `question_bank` VALUES (45, 'CSS选择器的优先级如何计算？', '!important > 行内样式 > ID选择器 > 类选择器/属性选择器/伪类 > 元素选择器/伪元素 > 通配符。具体计算：(a,b,c,d)四位数', '技术知识', '前端');
INSERT INTO `question_bank` VALUES (46, '什么是闭包？有什么优缺点？', '闭包是函数和其周围状态的引用组合。优点：变量私有化、模拟块级作用域、实现模块化；缺点：内存泄漏、性能消耗', '技术知识', '前端');
INSERT INTO `question_bank` VALUES (47, 'Flex布局常用属性有哪些？', '容器属性：flex-direction、justify-content、align-items、flex-wrap、align-content；项目属性：flex、align-self、order、flex-grow、flex-shrink', '技术知识', '前端');
INSERT INTO `question_bank` VALUES (48, '==和===的区别是什么？', '==会进行类型转换后比较值；===严格比较，不转换类型，值和类型都必须相等。建议使用===避免意外错误', '技术知识', '前端');
INSERT INTO `question_bank` VALUES (49, '什么是原型链？如何实现继承？', '每个对象都有__proto__属性指向构造函数的prototype，形成链式结构。继承方式：原型链继承、构造函数继承、组合继承、ES6 class extends', '技术知识', '前端');
INSERT INTO `question_bank` VALUES (50, 'Promise是什么？有哪些常用方法？', 'Promise是异步编程的解决方案。方法：Promise.resolve()、Promise.reject()、Promise.all()、Promise.race()、Promise.allSettled()、.then()、.catch()、.finally()', '技术知识', '前端');
INSERT INTO `question_bank` VALUES (51, '请介绍一个你做过的最复杂的前端项目？', '可以从项目背景（什么类型的应用）、技术栈（Vue/React/Angular）、负责模块（组件开发/状态管理/性能优化）、遇到的挑战（兼容性问题/复杂交互）、解决方案和成果几个方面回答', '项目经历', '前端');
INSERT INTO `question_bank` VALUES (52, '你们项目的前端架构是怎么设计的？', '技术选型考虑、目录结构设计、组件化设计、状态管理方案（Vuex/Redux）、路由设计、API封装、工具函数、构建配置（Webpack/Vite）、代码规范（ESLint/Prettier）', '项目经历', '前端');
INSERT INTO `question_bank` VALUES (53, '项目中如何处理大规模数据展示？', '虚拟列表（react-window/vue-virtual-scroller）、分页加载、无限滚动、Web Worker处理数据、Canvas/WebGL渲染优化、懒加载、防抖节流', '项目经历', '前端');
INSERT INTO `question_bank` VALUES (54, '你们项目的性能优化做了哪些工作？', '打包优化（代码分割、Tree Shaking、压缩）、图片优化（WebP格式、懒加载）、CDN加速、缓存策略、SSR/SSG、减少重排重绘、路由懒加载、长列表优化', '项目经历', '前端');
INSERT INTO `question_bank` VALUES (55, '如何处理跨域问题？', '开发环境：proxy代理；生产环境：CORS（后端配置）、JSONP（只支持GET）、Nginx反向代理、postMessage、WebSocket、document.domain', '项目经历', '前端');
INSERT INTO `question_bank` VALUES (56, '项目中遇到过哪些兼容性问题？如何解决？', '例如：flex布局兼容、ES6语法兼容（Babel转译）、移动端点击延迟（fastclick）、iOS键盘问题、各种浏览器样式差异（normalize.css）、PC端IE兼容等', '项目经历', '前端');
INSERT INTO `question_bank` VALUES (57, '你们项目的权限控制是如何实现的？', '路由权限（动态路由）、按钮权限（自定义指令）、菜单权限（根据角色渲染）、接口权限（配合后端token/RBAC）、角色状态管理、401拦截处理', '项目经历', '前端');
INSERT INTO `question_bank` VALUES (58, '做过哪些移动端适配方案？', 'rem方案（设置根字体）、viewport方案（vw/vh）、flexible.js、媒体查询、postcss-px-to-viewport、移动端1px问题处理、触摸事件优化', '项目经历', '前端');
INSERT INTO `question_bank` VALUES (59, '项目中如何管理公共组件？', '组件分类（基础组件/业务组件/布局组件）、组件库封装（Storybook展示）、版本管理、文档维护、npm私有库发布、按需加载、组件测试', '项目经历', '前端');
INSERT INTO `question_bank` VALUES (60, '做过哪些安全防护措施？', 'XSS防御（转义输入、CSP）、CSRF防御（token验证、SameSite）、点击劫持（X-Frame-Options）、敏感信息加密存储、HTTPS、输入校验', '项目经历', '前端');
INSERT INTO `question_bank` VALUES (61, '设计一个图片懒加载组件？', '1.监听滚动事件 2.判断图片进入可视区域（getBoundingClientRect/IntersectionObserver）3.将data-src赋值给src 4.使用节流优化性能 5.加载失败重试机制', '场景题', '前端');
INSERT INTO `question_bank` VALUES (62, '如何实现一个搜索框的防抖功能？', 'function debounce(fn, delay) { let timer; return function() { clearTimeout(timer); timer = setTimeout(() => fn.apply(this, arguments), delay); } }，用于减少请求次数', '场景题', '前端');
INSERT INTO `question_bank` VALUES (63, '设计一个可复用的模态框组件？', '1.Props控制显隐、标题、宽度 2.slot插槽支持内容定制 3.事件emit关闭 4.遮罩层点击关闭 5.ESC键关闭 6.动画过渡 7.防止滚动穿透', '场景题', '前端');
INSERT INTO `question_bank` VALUES (64, '如何实现前端路由？两种模式的区别？', 'Hash模式：监听hashchange事件，兼容性好但URL带#；History模式：使用pushState/replaceState，需要后端配合防止404，URL美观', '场景题', '前端');
INSERT INTO `question_bank` VALUES (65, '实现一个图片上传组件有哪些考虑？', '1.文件格式/大小校验 2.预览功能 3.进度条显示 4.断点续传 5.图片压缩（canvas）6.多文件上传 7.上传失败重试 8.拖拽上传 9.裁剪功能', '场景题', '前端');
INSERT INTO `question_bank` VALUES (66, '如何实现一个无限滚动列表？', '1.监听滚动到底部 2.加载更多数据 3.使用虚拟列表优化性能 4.节流处理 5.加载状态提示 6.错误重试 7.数据缓存', '场景题', '前端');
INSERT INTO `question_bank` VALUES (67, '设计一个前端监控SDK需要哪些功能？', '1.错误监控（JS错误、资源加载错误、Promise错误）2.性能监控（FP/FCP/LCP）3.用户行为监控（PV/UV/点击）4.数据上报（图片/信标）5.采样率控制', '场景题', '前端');
INSERT INTO `question_bank` VALUES (68, '如何实现一个画板功能？', '1.Canvas获取上下文 2.监听鼠标/触摸事件 3.绘制路径 4.撤销重做（保存快照）5.颜色/粗细调节 6.清空画板 7.保存为图片', '场景题', '前端');
INSERT INTO `question_bank` VALUES (69, '设计一个登录页面的前端逻辑？', '1.表单验证（正则校验）2.密码加密传输 3.记住密码 4.图形验证码/滑块验证 5.登录状态保持（token）6.第三方登录 7.注册/忘记密码跳转', '场景题', '前端');
INSERT INTO `question_bank` VALUES (70, '如何实现一个拖拽排序功能？', '1.HTML5 Drag API 2.鼠标事件模拟（mousedown/mousemove/mouseup）3.排序算法 4.边界判断 5.动画效果 6.触摸屏支持 7.性能优化', '场景题', '前端');
INSERT INTO `question_bank` VALUES (71, '你为什么选择做前端开发？', '可以从兴趣驱动（喜欢可视化效果）、创造力（设计感）、成就感（用户交互）、技术发展（更新快有挑战）、前后端分离趋势等方面回答', '行为题', '前端');
INSERT INTO `question_bank` VALUES (72, '你对前端框架（Vue/React/Angular）的选型怎么看？', '根据项目需求：Vue轻量易上手适合中小项目；React生态丰富适合大型应用；Angular适合企业级规范项目。个人偏好结合技术栈学习', '行为题', '前端');
INSERT INTO `question_bank` VALUES (73, '你遇到过最难解决的前端bug是什么？', '举例说明，比如内存泄漏、滚动卡顿、兼容性问题。描述定位过程（调试工具、二分法排查）、解决方案、学到什么', '行为题', '前端');
INSERT INTO `question_bank` VALUES (74, '如何跟进前端新技术？', '关注技术博客（掘金/InfoQ）、GitHub趋势、参与开源社区、看官方文档、技术周刊（JavaScript Weekly）、参加技术会议/分享', '行为题', '前端');
INSERT INTO `question_bank` VALUES (75, 'UI设计师给你的设计稿实现不了怎么办？', '1.沟通解释技术限制 2.提供替代方案 3.评估实现成本和收益 4.折中方案（先上线再优化）5.学习新技术尝试实现', '行为题', '前端');
INSERT INTO `question_bank` VALUES (76, '你对前端工程化的理解？', '模块化开发、组件化设计、规范化（代码规范/Git规范）、自动化（CI/CD）、测试（单元测试/e2e）、性能监控、打包构建工具（Webpack/Vite）', '行为题', '前端');
INSERT INTO `question_bank` VALUES (77, '如何看待WebAssembly的未来？', '补充JS性能不足，适合复杂计算/游戏/音视频处理，不是替代而是增强，生态逐渐完善，未来可期', '行为题', '前端');
INSERT INTO `question_bank` VALUES (78, '你希望在前端领域达到什么高度？', '技术深度：成为领域专家（可视化/性能优化/框架开发）；技术广度：全栈发展；软实力：技术分享/团队带领', '行为题', '前端');
INSERT INTO `question_bank` VALUES (79, '平时用哪些开发工具和调试技巧？', '开发工具：VSCode插件、Chrome DevTools（断点调试/网络分析/性能分析）、Postman、React/Vue DevTools；调试技巧：console.table、debugger、sourcemap', '行为题', '前端');
INSERT INTO `question_bank` VALUES (80, '你怎么理解用户体验？', '性能体验（加载速度）、交互体验（流畅度/反馈）、视觉体验（美观/一致）、可访问性（无障碍）、跨端体验、容错处理（友好的错误提示）', '行为题', '前端');
INSERT INTO `question_bank` VALUES (81, 'Python的时间复杂度中，列表的append和insert操作各是多少？', 'append是O(1)均摊时间复杂度；insert是O(n)，因为需要移动后面的元素。pop()末尾是O(1)，pop(i)是O(n)', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (82, '解释Python中的GIL是什么？它对多线程程序有什么影响？', 'GIL是全局解释器锁，保证同一时刻只有一个线程执行Python字节码。影响：CPU密集型多线程程序无法利用多核优势，I/O密集型影响较小。解决方案：多进程、协程、使用C扩展', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (83, 'Python中装饰器的作用是什么？如何实现一个带参数的装饰器？', '装饰器用于在不修改函数代码的情况下增加功能。带参数装饰器需要三层嵌套：外层接收参数，中层接收函数，内层接收函数参数，执行增强逻辑', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (84, '生成器和迭代器的区别？yield关键字的作用？', '迭代器是实现了__iter__和__next__方法的对象；生成器是特殊的迭代器，使用yield返回值。yield暂停函数并保存状态，下次从该点继续执行', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (85, 'Python中浅拷贝和深拷贝的区别？如何实现？', '浅拷贝只拷贝对象本身，不拷贝子对象（copy.copy()）；深拷贝递归拷贝所有子对象（copy.deepcopy()）。对于不可变对象两者结果相同', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (86, '什么是Python的魔法方法？列举几个常用的？', '以双下划线开头和结尾的特殊方法，用于定制类行为。常用：__init__构造、__str__字符串表示、__len__长度、__getitem__索引访问、__call__使对象可调用', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (87, 'Python中列表和元组的区别？分别在什么场景使用？', '列表可变，元组不可变；列表用[]，元组用()。列表适合需要修改的数据集，元组适合固定数据（如坐标、数据库查询结果）、字典键、性能要求高的场景', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (88, '什么是Python的上下文管理器？如何使用？', '用于资源管理（文件、锁），确保使用后释放。实现方式：__enter__和__exit__方法，或使用contextlib.contextmanager装饰器。with语句调用', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (89, 'Python中多进程和多线程的区别？分别在什么场景使用？', '多进程：每个进程独立内存，适合CPU密集型，利用多核；多线程：共享内存，适合I/O密集型。Python中多线程受GIL限制，多进程通过multiprocessing实现', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (90, '什么是Python的垃圾回收机制？', '主要基于引用计数，当计数为0时回收。辅助机制：标记-清除解决循环引用，分代回收提高效率。可通过gc模块手动控制', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (91, '快速排序算法的原理和复杂度？用Python实现核心代码？', '原理：分治法，选择基准，分区后递归排序。时间复杂度平均O(nlogn)，最坏O(n²)。代码：def quick_sort(arr): if len(arr)<=1: return arr; pivot=arr[0]; left=[x for x in arr[1:] if x<=pivot]; right=[x for x in arr[1:] if x>pivot]; return quick_sort(left)+[pivot]+quick_sort(right)', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (92, '二分查找算法的前提条件和实现？', '前提：有序数组。实现：def binary_search(arr, target): left,right=0,len(arr)-1; while left<=right: mid=(left+right)//2; if arr[mid]==target: return mid; elif arr[mid]<target: left=mid+1; else: right=mid-1; return -1。时间复杂度O(logn)', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (93, '什么是动态规划？以斐波那契数列为例说明？', '将复杂问题分解为子问题，缓存子问题结果避免重复计算。斐波那契：def fib(n): dp=[0]*(n+1); dp[1]=1; for i in range(2,n+1): dp[i]=dp[i-1]+dp[i-2]; return dp[n]，空间可优化为O(1)', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (94, '链表反转的实现？', 'def reverseList(head): prev=None; curr=head; while curr: next_temp=curr.next; curr.next=prev; prev=curr; curr=next_temp; return prev。时间复杂度O(n)，空间O(1)', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (95, '如何判断一个字符串是否是回文串？', 'def isPalindrome(s): s=s.lower()，过滤非字母数字；return s==s[::-1]；或双指针：left,right=0,len(s)-1；while left<right: if s[left]!=s[right]: return False；left+=1；right-=1；return True', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (96, '什么是二叉树的前序、中序、后序遍历？用Python实现？', '前序：根左右；中序：左根右；后序：左右根。递归：def inorder(root): if root: inorder(root.left); print(root.val); inorder(root.right)。迭代用栈模拟', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (97, 'LRU缓存算法的实现思路？', '使用哈希表+双向链表。哈希表O(1)查找，链表维护访问顺序。get时移动节点到头部；put时若存在更新值并移动到头部，若不存在且容量满则删除尾部节点', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (98, '什么是堆排序？Python中如何实现？', '利用堆这种数据结构。Python用heapq模块：heapq.heapify()建堆，heapq.heappop()弹出最小元素。时间复杂度O(nlogn)，不稳定排序', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (99, '如何检测链表是否有环？', '快慢指针法：def hasCycle(head): slow=fast=head；while fast and fast.next: slow=slow.next；fast=fast.next.next；if slow==fast: return True；return False。时间复杂度O(n)，空间O(1)', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (100, '什么是拓扑排序？应用场景？', '对有向无环图的顶点线性排序，使得对每条边(u,v)，u在v之前。应用：任务调度、依赖解析、课程安排。实现：Kahn算法（BFS）或DFS', '技术知识', 'Python');
INSERT INTO `question_bank` VALUES (101, '请介绍一个你用Python开发的数据分析项目？', '可以从数据来源、数据清洗、分析目标、使用工具（pandas/numpy/matplotlib）、分析结果、业务价值等方面描述，重点说明数据处理流程和关键发现', '项目经历', 'Python');
INSERT INTO `question_bank` VALUES (102, '你在项目中如何优化Python代码的性能？', '1.使用合适的数据结构（set/dict）2.列表推导式代替循环 3.使用生成器节省内存 4.多进程/协程 5.关键代码用Cython/C扩展 6.性能分析工具cProfile定位瓶颈 7.缓存计算结果', '项目经历', 'Python');
INSERT INTO `question_bank` VALUES (103, '有没有做过爬虫项目？如何处理反爬？', '项目描述（目标网站/数据量/技术栈）。反爬策略：User-Agent轮换、IP代理池、请求延迟、模拟登录、验证码识别、动态渲染页面用Selenium/Pyppeteer、分布式爬虫', '项目经历', 'Python');
INSERT INTO `question_bank` VALUES (104, '做过哪些Web开发项目？用了什么框架？', 'Django/Flask/FastAPI选型考虑、项目架构、数据库设计、RESTful API设计、认证授权、部署方案（Gunicorn/Nginx/Docker）、性能优化', '项目经历', 'Python');
INSERT INTO `question_bank` VALUES (105, '项目中遇到过内存泄漏问题吗？如何定位和解决？', '使用tracemalloc/memory_profiler/guppy等工具分析内存使用，检查循环引用、全局变量、缓存未释放、文件句柄未关闭等问题，优化数据结构和释放资源', '项目经历', 'Python');
INSERT INTO `question_bank` VALUES (106, '如何设计一个数据处理管道？', 'ETL流程设计：数据抽取（多数据源）、数据清洗转换（pandas/Spark）、数据加载（数据库/数据仓库）。考虑数据质量监控、错误处理、增量更新、任务调度（Airflow）', '项目经历', 'Python');
INSERT INTO `question_bank` VALUES (107, '有没有做过机器学习项目？整个流程是怎样的？', '1.业务理解 2.数据收集 3.数据清洗/特征工程 4.模型选择（scikit-learn/TensorFlow）5.模型训练/调参 6.模型评估 7.部署上线（Flask API/ONNX）8.监控迭代', '项目经历', 'Python');
INSERT INTO `question_bank` VALUES (108, '如何保证Python项目的代码质量？', '1.代码规范（PEP8/Black/isort）2.静态检查（pylint/mypy）3.单元测试（pytest/unittest）4.代码审查 5.CI/CD自动化 6.文档（Sphinx）7.版本控制（Git flow）', '项目经历', 'Python');
INSERT INTO `question_bank` VALUES (109, '做过哪些自动化运维工具？', '1.自动化部署（Fabric/Ansible）2.监控脚本（系统指标/日志分析）3.定时任务（Celery/cron）4.数据库备份恢复 5.报警通知 6.批量服务器管理', '项目经历', 'Python');
INSERT INTO `question_bank` VALUES (110, '项目中如何处理大数据量？', '1.分块处理（pandas chunks）2.使用生成器 3.数据库优化（索引/分表）4.分布式计算（Spark/Dask）5.缓存策略 6.异步处理 7.数据采样/聚合 8.列式存储（Parquet）', '项目经历', 'Python');
INSERT INTO `question_bank` VALUES (111, '如何设计一个简单的Web爬虫系统？', '1.URL管理器（待爬/已爬队列）2.网页下载器（requests/aiohttp）3.解析器（BeautifulSoup/lxml）4.数据存储（MongoDB/MySQL）5.调度器控制并发 6.异常处理 7.去重策略（布隆过滤器）', '场景题', 'Python');
INSERT INTO `question_bank` VALUES (112, '设计一个Python的日志记录系统需要考虑什么？', '1.日志级别（DEBUG/INFO/WARNING/ERROR）2.输出格式（时间/级别/模块/行号）3.输出目标（文件/控制台/远程）4.日志轮转（按大小/时间）5.性能影响（异步写入）6.敏感信息过滤 7.多进程安全', '场景题', 'Python');
INSERT INTO `question_bank` VALUES (113, '如何实现一个Python的任务调度器？', '1.时间轮算法 2.优先级队列（heapq）3.Celery/RQ分布式任务队列 4.APScheduler库 5.cron表达式解析 6.持久化存储 7.失败重试机制 8.任务依赖管理', '场景题', 'Python');
INSERT INTO `question_bank` VALUES (114, '设计一个限流器，限制API调用频率？', '1.令牌桶算法：以固定速率添加令牌 2.漏桶算法：恒定速率处理请求 3.计数器：时间窗口计数 4.Redis实现分布式限流 5.装饰器封装 6.返回429状态码 7.队列缓冲', '场景题', 'Python');
INSERT INTO `question_bank` VALUES (115, '如何实现一个Python的配置管理中心？', '1.多环境支持（dev/test/prod）2.配置格式（YAML/JSON/TOML）3.动态加载/热更新 4.配置验证（pydantic）5.敏感信息加密 6.配置继承/覆盖 7.从远程拉取（etcd/consul）8.本地缓存', '场景题', 'Python');
INSERT INTO `question_bank` VALUES (116, '设计一个实时数据处理系统？', '1.数据接入（Kafka/RabbitMQ）2.流处理框架（Flink/Spark Streaming）3.Python处理（Faust/Streamz）4.窗口计算（滚动/滑动）5.状态管理 6.结果输出 7.水位线处理延迟 8.容错机制', '场景题', 'Python');
INSERT INTO `question_bank` VALUES (117, '如何实现一个Python的A/B测试框架？', '1.实验配置（YAML/DB）2.分流算法（hash一致性/随机）3.流量分配（百分比控制）4.参数覆盖 5.数据埋点 6.结果统计分析（t检验）7.实验隔离 8.用户ID一致性', '场景题', 'Python');
INSERT INTO `question_bank` VALUES (118, '设计一个Python代码审查工具？', '1.静态分析（ast解析）2.代码复杂度计算（McCabe）3.重复代码检测 4.命名规范检查 5.注释覆盖率 6.导入优化 7.自动化修复建议 8.集成到CI流程 9.生成报告', '场景题', 'Python');
INSERT INTO `question_bank` VALUES (119, '如何实现一个Python的缓存系统？', '1.缓存策略（LRU/LFU/TTL）2.多级缓存（本地+分布式）3.缓存穿透/击穿/雪崩防护 4.缓存更新机制（写直达/写回）5.装饰器封装 6.序列化（pickle/json）7.监控命中率 8.Redis/Memcached集成', '场景题', 'Python');
INSERT INTO `question_bank` VALUES (120, '设计一个Python的数据验证框架？', '1.定义验证规则（类型/范围/格式）2.嵌套对象验证 3.自定义验证器 4.错误信息收集 5.性能优化（缓存模式）6.集成ORM 7.异步支持 8.国际化错误提示 9.基于装饰器/类继承', '场景题', 'Python');
INSERT INTO `question_bank` VALUES (121, '你为什么选择Python作为主要开发语言？', '可以从Python的优势回答：语法简洁易上手、生态丰富（数据科学/Web/自动化）、开发效率高、社区活跃、跨平台性好、适合快速迭代。结合个人兴趣和职业规划', '行为题', 'Python');
INSERT INTO `question_bank` VALUES (122, '你如何保持对Python新特性的学习？', '关注PEP提案、阅读官方文档（What\'s New）、订阅Python周刊、参与社区讨论（Stack Overflow/Reddit）、看源码、尝试新版本特性（如3.10的模式匹配、3.11的性能提升）', '行为题', 'Python');
INSERT INTO `question_bank` VALUES (123, '遇到过印象深刻的Python坑是什么？如何解决的？', '例如：可变默认参数陷阱、闭包延迟绑定、浅拷贝问题、循环引用、GIL限制等。描述问题现象、排查过程（调试工具/打印日志）、解决方案和学到什么', '行为题', 'Python');
INSERT INTO `question_bank` VALUES (124, '如何看待Python2和Python3的过渡？', 'Python3是大势所趋，性能更好、语法更现代、官方已停止支持Python2。迁移过程中主要挑战：库兼容性、编码处理、print函数、整除行为变化。建议新项目都用Python3', '行为题', 'Python');
INSERT INTO `question_bank` VALUES (125, '你在团队中如何推广Python最佳实践？', '1.制定代码规范（PEP8）2.引入代码审查 3.分享会讲解设计模式/性能优化 4.搭建CI自动检查 5.编写最佳实践文档 6.重构遗留代码示例 7.引入类型注解提高可维护性', '行为题', 'Python');
INSERT INTO `question_bank` VALUES (126, '对Python的未来发展怎么看？', '性能持续提升（3.11更快）、类型系统增强、异步编程生态完善、数据科学/AI领域主导地位稳固、WebAssembly支持、移动开发探索。Python在胶水语言地位不可替代', '行为题', 'Python');
INSERT INTO `question_bank` VALUES (127, '你用过哪些Python的IDE或调试工具？', 'IDE：PyCharm专业版/社区版、VSCode（Python插件）、Jupyter Notebook/Lab、Sublime Text。调试工具：pdb、ipdb、PyCharm调试器、logging模块、cProfile/profile性能分析、memory_profiler内存分析', '行为题', 'Python');
INSERT INTO `question_bank` VALUES (128, '如何平衡开发效率和代码质量？', '1.先快速实现原型，再重构优化 2.单元测试保障质量 3.代码审查发现问题 4.持续重构保持代码健康 5.技术债务管理 6.自动化工具辅助（linting/formatting）7.根据项目阶段调整平衡点', '行为题', 'Python');
INSERT INTO `question_bank` VALUES (129, '你参与过开源Python项目吗？收获是什么？', '可以描述参与的项目名称、贡献内容（bug修复/功能开发/文档）、PR过程、社区交流收获、代码规范学习、版本控制协作经验。没有的话可以谈学习开源项目源码的收获', '行为题', 'Python');
INSERT INTO `question_bank` VALUES (130, '你认为Python程序员最重要的软技能是什么？', '1.问题抽象能力（将业务转化为技术）2.沟通协作能力（与其他角色配合）3.持续学习态度（新技术跟进）4.代码审查同理心（建设性意见）5.业务理解能力（不只是写代码）', '行为题', 'Python');

SET FOREIGN_KEY_CHECKS = 1;
