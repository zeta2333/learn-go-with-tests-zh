# 前言翻译分析（gb-readme.md → 站点首页）

## 定位
Gitbook 封面页：书名 + 封面插画 + 支持作者 + 本书理念 + 作者带团队学 Go 的方法论复盘 + 适合谁/需要什么/反馈。614 词。

## 本地化决策（已与项目所有者确认）
1. **Translations 节**：原版"中文"链接指向过时的 studygolang 版，替换为译注说明本站是跟随上游更新的中文版；其余 9 个语言链接照留。
2. **封面插画**：拷贝 `red-green-blue-gophers-smaller.png` 到 `docs/assets/`，署名链接保留。
3. **"Support me" 节**：保留（MIT 项目应保留作者的致谢渠道），措辞本地化。
4. **LICENSE.md 相对链接**：改为上游仓库的 LICENSE 链接；本仓库根目录已附 MIT LICENSE 文件（原作 + 译者双重署名）。
5. 其余正文全译，不作删减；"the blue book" 保留 Amazon 链接并按社区习惯译作《The Go Programming Language》（"蓝皮书"）。

## 术语与语气
- "a grounding with TDD" → "打下 TDD 的底子"
- "katas" → 编程套路题（kata），首现加注
- "practicing scales" → 吉他音阶练习的类比，保留
- 语气：conversational，作者自嘲与坦率的复盘语气要保住
