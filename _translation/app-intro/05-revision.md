# 构建一个应用

希望你把*Go 基础*篇消化得差不多了——经过前面的学习，你已经对 Go 的大部分语言特性有了扎实的掌握，也知道 TDD 该怎么做。

接下来这一篇，我们要动手构建一个应用。

每一章都会在前一章的基础上继续迭代：产品负责人（product owner）发话要什么功能，我们就给应用加上什么功能。

过程中会引入一些新概念，帮我们写出更好的代码；不过大部分新东西，还是学习如何用好 Go 的标准库。

到这一篇结束的时候，你应该就能牢牢掌握：如何在 Go 里写一个有测试护航的应用，而且是一步一步迭代出来的。

- [HTTP 服务器](https://github.com/quii/learn-go-with-tests/blob/main/http-server.md)（英文原版）——我们将创建一个监听 HTTP 请求并作出响应的应用。
- [JSON、路由与嵌入](https://github.com/quii/learn-go-with-tests/blob/main/json.md)（英文原版）——我们会让端点返回 JSON，并探索如何实现路由。
- [IO 与排序](https://github.com/quii/learn-go-with-tests/blob/main/io.md)（英文原版）——我们会把数据持久化到磁盘、再从磁盘读回来，还会讲到数据排序。
- [命令行与项目结构](https://github.com/quii/learn-go-with-tests/blob/main/command-line.md)（英文原版）——用同一份代码库支持多个应用，并从命令行读取输入。
- [Time](https://github.com/quii/learn-go-with-tests/blob/main/time.md)（英文原版）——用 `time` 包来安排定时活动。
- [WebSockets](https://github.com/quii/learn-go-with-tests/blob/main/websockets.md)（英文原版）——学习如何编写并测试一个使用 WebSockets 的服务器。

*译注：以上各章尚未译出，链接暂指向英文原版；对应章节收入中译后，这里的链接会切换为本站译文。*
