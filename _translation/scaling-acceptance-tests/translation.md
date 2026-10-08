# 扩展验收测试

本章是[验收测试入门](intro-to-acceptance-tests.md)的后续。[本章的完整代码可以在 GitHub 上找到](https://github.com/quii/go-specs-greet)。

验收测试至关重要，它直接决定了你能否以合理的变更成本、有信心地持续演进你的系统。

验收测试还是对付遗留代码的利器。面对一个没有任何测试的糟糕代码库，请忍住直接动手重构的冲动。正确的做法是先写一些验收测试，给自己织一张安全网，这样你就可以放心地修改系统内部实现，而不用担心影响它对外的功能行为。验收测试（AT）不必关心内部质量，所以它们特别适合这种场景。

读完本章你会体会到：验收测试除了用于验证，还能用在开发过程中，帮助我们更有章法、更有条理地改造系统，少做无用功。

## 前置材料

写这一章的动力，来自我多年与验收测试搏斗积累的挫败感。推荐你看两个视频：

- Dave Farley - [How to write acceptance tests](https://www.youtube.com/watch?v=JDD5EEJgpHU)
- Nat Pryce - [E2E functional tests that can run in milliseconds](https://www.youtube.com/watch?v=Fk4rCn4YLLU)

《Growing Object Oriented Software》（GOOS）对包括我在内的许多软件工程师来说都是一本影响深远的书。它提出的方法，正是我辅导工程师时所倡导的。

- [GOOS](http://www.growing-object-oriented-software.com) - Nat Pryce & Steve Freeman

最后，我和 [Riya Dattani](https://twitter.com/dattaniriya) 曾在一场演讲中结合 BDD 聊过这个话题：[Acceptance tests, BDD and Go](https://www.youtube.com/watch?v=ZMWJCk_0WrY)。

## 回顾

我们讨论的是"黑盒"测试：从系统外部、从**业务视角**验证系统的行为符合预期。测试接触不到被测系统的内部；它们只关心你的系统**做什么**，而不是**怎么做**。

## 坏验收测试的解剖

这些年里，我待过好几家公司、好几个团队。每一家都意识到需要验收测试，都需要某种从用户视角测试系统、验证系统按预期工作的手段；但几乎无一例外，这些测试的成本最终都成了团队实实在在的麻烦：

- 跑得慢
- 脆弱
- 时灵时不灵
- 维护成本高，而且总让改软件变得比理应的更费劲
- 只能在某个特定环境里跑，反馈又慢又差

假设你想给你正在开发的网站写验收测试。你决定用无头浏览器（比如 [Selenium](https://www.selenium.dev)）模拟用户点击网站上的按钮，验证它做了该做的事。

随着时间推移，网站标记不得不随着新功能的发现而变化，工程师们为某个元素到底该用 `<article>` 还是 `<section>` 这种鸡毛蒜皮的事吵到第一亿次。

尽管团队对系统只做了些用户几乎察觉不到的小改动，你却发现自己把大把时间浪费在更新验收测试上。

### 紧耦合

想一想是什么会"惊动"验收测试，逼着它们改：

- 外部行为变化。如果你想改变系统做什么，修改验收测试套件就算不是求之不得，至少也是合理的。
- 实现细节变化／重构。理想情况下这不应该引起任何改动，就算要改，也该是小改。

但现实中，太经常是后者在逼着验收测试改。改到工程师甚至因为害怕更新测试的工作量，而不敢去改系统了！

![Riya 和我在演讲中讨论测试中的关注点分离](https://i.imgur.com/bbG6z57.png)

这些问题的根源，是没有践行上面提到的那些作者早已写明、也早已被验证过的工程习惯。**验收测试不能按单元测试的写法来写**；它们需要更多的思考，以及不同的实践。

## 好验收测试的解剖

如果我们希望验收测试只在行为变化时才改、而不是实现细节一变就跟着变，那么顺理成章地，我们需要把这两类关注点分开。

### 谈谈复杂性的种类

作为软件工程师，我们要跟两种复杂性打交道。

- **偶然复杂性**（accidental complexity）是因为我们跟计算机打交道而不得不应付的复杂性，比如网络、磁盘、API 之类的东西。

- **本质复杂性**（essential complexity）有时被称为"领域逻辑"。它是你的领域里那些特定的规则和事实。
  - 比如"账户所有者取出的钱超过余额时，就透支了"。这句话跟计算机没有任何关系；早在银行用上计算机之前，这句话就成立！

本质复杂性应该能讲给不懂技术的人听，把它在"领域"代码和验收测试中都建模出来，是很有价值的。

### 关注点分离

Dave Farley 在前面的视频里提出的、我和 Riya 也讨论过的想法是：我们应该有**规格**（specification）的概念。规格描述我们想要的系统行为，但不与偶然复杂性或实现细节耦合。

这个想法你应该觉得顺理成章。在生产代码里，我们经常努力分离关注点、解耦各个工作单元。你会毫不犹豫地引入一个接口（interface），让你的 `HTTP` 处理器与 HTTP 之外的事情解耦，对吧？把同样的思路用到验收测试上就行了。

Dave Farley 描述了一种具体的结构。

![Dave Farley 谈验收测试](https://i.imgur.com/nPwpihG.png)

在 GopherconUK 上，我和 Riya 把它翻译成了 Go 的说法。

![关注点分离](https://i.imgur.com/qdY4RJe.png)

### 打了鸡血的测试

把"规格如何被执行"解耦之后，我们就能在不同的场景里复用它。我们可以：

#### 让驱动器（driver）可配置

这意味着你可以在本地、预发布环境、以及（理想情况下）生产环境中运行你的验收测试。

- 太多团队把系统设计成验收测试根本没法在本地跑。这引入了一个慢到无法容忍的反馈回路。你难道不希望*在合并代码之前*就能确信验收测试会通过吗？如果测试挂了，却没法在本地复现失败，只能提交代码、然后祈祷 20 分钟后在另一个环境里它能过，这你能接受？
- 记住，测试在预发布环境里通过，不代表你的系统就能正常工作。开发环境与生产环境的一致性，充其量是个善意的谎言。[I test in prod](https://increment.com/testing/i-test-in-production/)。
- 环境之间的差异总会存在，而且会影响系统的*行为*。CDN 的缓存响应头可能配错了；你依赖的下游服务行为可能不一样；某个配置项可能不对。要是能在生产环境里跑你的规格、快速抓住这些问题，岂不美哉？

#### 接入*不同的*驱动器，测试系统的其他部分

这种灵活性让我们可以在不同的抽象层、架构层测试行为，从而在黑盒测试之外拥有更聚焦的测试。

- 比如，你可能有一个网页，背后还有一个 API。为什么不用同一份规格把两者都测了？网页用无头浏览器，API 用 HTTP 调用。
- 把这个想法再推一步：理想情况下，我们希望**用代码为本质复杂性建模**（也就是"领域"代码），所以我们也应该能把规格用在单元测试上。这能给我们快速的反馈，确认系统中的本质复杂性建模正确、行为无误。

### 验收测试只为正确的理由而变

采用这套方法，规格需要变化的唯一理由就是系统行为变了，这是合理的。

- 如果你的 HTTP API 要变，你有一个明确的地方去改：驱动器。
- 如果你的网页标记变了，同样，改对应的驱动器就行。

随着系统长大，你会发现自己在多个测试里复用同一个驱动器，这又意味着：实现细节一变，你只需要改一个通常很明显的位置。

做得好，这套方法给我们带来实现细节上的灵活性和规格上的稳定性。更重要的是，它为管理变更提供了一个简单、清晰的结构，当系统和团队规模增长时，这一点变得至关重要。

### 验收测试作为一种软件开发方法

在那场演讲里，我和 Riya 讨论了验收测试与 BDD 的关系。我们谈到，动手前先*理解你要解决的问题*，并把它表达成一份规格，有助于聚焦你的意图，是开启工作的好方式。

我最早是在 GOOS 里接触到这种工作方式的。前段时间，我在博客上总结过这些想法。下面摘自我那篇 [Why TDD](https://quii.dev/The_Why_of_TDD)

---

TDD 的关注点是让你以迭代的方式，精确地为恰好需要的行为做设计。开始一个新领域时，你必须识别出一个关键的、必要的行为，然后激进地砍范围。

采用"自顶向下"的方法，从一条从外部检验该行为的验收测试开始。它会成为你努力的北极星。你只需要专注于让这条测试通过。在你写出足够多的代码让它通过之前，这条测试很可能会失败一段时间。

![](https://i.imgur.com/pxTaYu4.png)

验收测试立起来之后，你就可以切入 TDD 流程，驱动出足够的单元让验收测试通过。诀窍是：这个阶段别太纠结设计；先弄出够用的代码让验收测试通过，因为你还在学习和探索问题。

这第一步往往比你以为的要大得多：搭 web 服务器、路由、配置等等，所以把工作范围切小至关重要。我们要在空白画布上迈出第一个坚实的小步，并让它有通过的验收测试撑腰，这样后续才能快速、安全地迭代。

![](https://i.imgur.com/t5y5opw.png)

开发过程中，倾听你的测试，它们会给你信号，帮你把设计推向更好的方向——当然，一切锚定在行为上，而不是我们的想象上。

通常，第一个扛起苦活让验收测试通过的"单元"会慢慢大到让你不舒服，哪怕它只承载了这么一点行为。这时你就可以开始思考怎么拆分问题、引入新的协作者了。

![](https://i.imgur.com/UYqd7Cq.png)

这正是测试替身（比如 fake、mock）大显身手的地方，因为软件内部的复杂性往往不在实现细节里，而在单元"之间"、在它们如何交互上。

#### 自底向上的风险

这是"自顶向下"的方法，而不是"自底向上"。自底向上自有其用处，但它带有风险。如果构建"服务"和代码时既不尽快集成到应用里、又不靠高层测试来验证，**你就要冒着在未经验证的想法上浪费大量精力的风险**。

这是验收测试驱动方法的一个关键属性：用测试来获得对代码的真正验证。

我见过太多次，工程师自底向上、孤立地写出一坨自以为能解决问题的代码，结果它：

- 不按我们想要的方式工作
- 做了一堆我们不需要的事
- 不容易集成
- 反正也得重写一大半

这就是浪费。

## 废话不多说，上代码

跟其他章节不同，你需要装好 [Docker](https://www.docker.com)，因为我们要在容器里运行应用。默认你已经读到了书的这个位置，写 Go 代码、从不同的包导入等操作都不在话下了。

用 `go mod init github.com/quii/go-specs-greet` 创建一个新项目（这里可以随便填，但如果你改了路径，就得把所有内部 import 相应改掉）。

建一个 `specifications` 文件夹存放我们的规格，在里面加一个 `greet.go` 文件：

```go
package specifications

import (
	"testing"

	"github.com/alecthomas/assert/v2"
)

type Greeter interface {
	Greet() (string, error)
}

func GreetSpecification(t testing.TB, greeter Greeter) {
	got, err := greeter.Greet()
	assert.NoError(t, err)
	assert.Equal(t, got, "Hello, world")
}
```

我的 IDE（Goland）帮我省掉了加依赖的琐事，不过如果你需要手动操作，执行：

`go get github.com/alecthomas/assert/v2`

按照 Farley 的验收测试设计（规格→DSL→驱动器→系统），我们已经有了一个与实现解耦的规格。它不知道也不关心我们*怎么* `Greet`；它只关心领域里的本质复杂性。诚然，眼下这点复杂性不太多，但后面迭代时我们会扩展规格、加入更多功能。从小处着手永远是对的！

你可以把这个接口看作 DSL 的第一步；随着项目长大，你可能会发现需要换个方式抽象，但眼下这样挺好。

到这一步，为了把规格从实现里解耦出来搞这么多仪式感，可能会有人指责我们"过度抽象"。**我向你保证：与实现耦合过紧的验收测试，才会真正成为工程团队的负担**。我确信，现实中的验收测试大多是因为这种不当耦合才维护成本高昂，而不是相反的"过度抽象"。

我们可以用这份规格去验证任何能 `Greet` 的"系统"。

### 第一个系统：HTTP API

我们需要通过 HTTP 提供一个"问候服务"。所以要创建：

1. 一个**驱动器**。这里，与 HTTP 系统打交道要靠**HTTP 客户端**。这段代码知道怎么跟我们的 API 交互。驱动器负责把 DSL 翻译成针对特定系统的调用；在我们这里，驱动器会实现规格定义的接口。
2. 一个带问候 API 的 **HTTP 服务器**
3. 一个**测试**，负责管理整个生命周期：把服务器跑起来，然后把驱动器插到规格上，当作测试来运行

## 先写测试

从零搭一个能编译并运行你的程序的黑盒测试——把程序跑起来、执行测试、再清理干净——这一套初始流程相当费事。所以最好在项目刚开始、功能最少的时候就把它做好。我自己的所有项目，通常都是从一个 "hello world" 服务器实现起步的，所有测试都就位，等着我快速填充真正的功能。

"规格""驱动器""验收测试"这套心智模型需要一点时间适应，所以请跟紧步骤。"倒着来"会很有帮助：先试着调用规格。

先建一个目录结构，装下我们打算发布的程序。

`mkdir -p cmd/httpserver`

在新文件夹里新建一个文件 `greeter_server_test.go`，写入以下内容。

```go
package main_test

import (
	"testing"

	"github.com/quii/go-specs-greet/specifications"
)

func TestGreeterServer(t *testing.T) {
	specifications.GreetSpecification(t, nil)
}
```

我们想在一个 Go 测试里运行规格。我们已经有一个 `*testing.T` 了，所以第一个参数是它，那第二个呢？

`specifications.Greeter` 是一个接口，我们会用一个 `Driver` 来实现它，把新的 TestGreeterServer 代码改成下面这样：

```go
import (
	go_specs_greet "github.com/quii/go-specs-greet"
)

func TestGreeterServer(t *testing.T) {
	driver := go_specs_greet.Driver{BaseURL: "http://localhost:8080"}
	specifications.GreetSpecification(t, driver)
}
```

我们的 `Driver` 最好可配置，这样它就能对着不同环境跑，包括本地环境，所以我们加了一个 `BaseURL` 字段。

## 试着运行测试

```
./greeter_server_test.go:46:12: undefined: go_specs_greet.Driver
```

我们仍在践行 TDD！这是绕不过去的一大步：我们要建几个文件，写的代码可能比平时习惯的要多，但刚开始时往往就是这样。此时我们务必记住红灯步骤的规矩：

> 为了让测试通过，需要犯多少罪就犯多少罪

## 写最少的代码让测试跑起来，检查失败的输出

捏住鼻子忍一忍；记住，测试通过之后随时可以重构。下面是驱动器的代码，放在项目根目录的 `driver.go` 里：

```go
package go_specs_greet

import (
	"io"
	"net/http"
)

type Driver struct {
	BaseURL string
}

func (d Driver) Greet() (string, error) {
	res, err := http.Get(d.BaseURL + "/greet")
	if err != nil {
		return "", err
	}
	defer res.Body.Close()
	greeting, err := io.ReadAll(res.Body)
	if err != nil {
		return "", err
	}
	return string(greeting), nil
}
```

几点说明：

- 你可以说我应该写测试来驱动出那些 `if err != nil`，但以我的经验，只要没对 `err` 做什么处理，"你返回了你收到的错误"这种测试价值相对有限。
- **你不该用默认的 HTTP 客户端**。后面我们会传入一个 HTTP 客户端，配置超时等等，但眼下我们只是想先让测试通过。
- 在 `greeter_server_test.go` 里我们调用了 `go_specs_greet` 包的 Driver，这个包现在才创建，别忘了把 `github.com/quii/go-specs-greet` 加进它的 import。

试着重跑测试；现在应该能编译，但还过不了。

```
Get "http://localhost:8080/greet": dial tcp [::1]:8080: connect: connection refused
```

我们有 `Driver` 了，但应用还没启动，所以它发不出 HTTP 请求。我们需要让验收测试来统筹"构建、运行、最后杀掉系统"这件事，测试才有得跑。

### 运行我们的应用

团队通常会把系统构建成 Docker 镜像再部署，所以我们的测试也这么做。

为了在测试里用 Docker，我们用 [Testcontainers](https://golang.testcontainers.org)。Testcontainers 给我们提供了一种编程方式来构建 Docker 镜像、管理容器生命周期。

`go get github.com/testcontainers/testcontainers-go`

现在把 `cmd/httpserver/greeter_server_test.go` 改成下面这样：

```go
package main_test

import (
	"context"
	"testing"

	"github.com/alecthomas/assert/v2"
	go_specs_greet "github.com/quii/go-specs-greet"
	"github.com/quii/go-specs-greet/specifications"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
)

func TestGreeterServer(t *testing.T) {
	ctx := context.Background()

	req := testcontainers.ContainerRequest{
		FromDockerfile: testcontainers.FromDockerfile{
			Context:    "../../.",
			Dockerfile: "./cmd/httpserver/Dockerfile",
			// 想少点刷屏就设成 false，不过遇到问题时它会很有用
			PrintBuildLog: true,
		},
		ExposedPorts: []string{"8080:8080"},
		WaitingFor:   wait.ForHTTP("/").WithPort("8080"),
	}
	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	assert.NoError(t, err)
	t.Cleanup(func() {
		assert.NoError(t, container.Terminate(ctx))
	})

	driver := go_specs_greet.Driver{BaseURL: "http://localhost:8080"}
	specifications.GreetSpecification(t, driver)
}
```

试着运行测试。

```
=== RUN   TestGreeterHandler
2022/09/10 18:49:44 Starting container id: 03e8588a1be4 image: docker.io/testcontainers/ryuk:0.3.3
2022/09/10 18:49:45 Waiting for container id 03e8588a1be4 image: docker.io/testcontainers/ryuk:0.3.3
2022/09/10 18:49:45 Container is ready id: 03e8588a1be4 image: docker.io/testcontainers/ryuk:0.3.3
    greeter_server_test.go:32: Did not expect an error but got:
        Error response from daemon: Cannot locate specified Dockerfile: ./cmd/httpserver/Dockerfile: failed to create container
--- FAIL: TestGreeterHandler (0.59s)
```

我们得给程序写一个 Dockerfile。在 `httpserver` 文件夹里创建一个 `Dockerfile`，内容如下。

```dockerfile
# Make sure to specify the same Go version as the one in the go.mod file.
# For example, golang:1.22.1-alpine.
FROM golang:1.18-alpine

WORKDIR /app

COPY go.mod ./

RUN go mod download

COPY . .

RUN go build -o svr cmd/httpserver/*.go

EXPOSE 8080
CMD [ "./svr" ]
```

这里的细节不用太纠结；它还可以继续打磨和优化，但就本例而言够用了。我们这种做法的好处是：以后可以继续改进 Dockerfile，而且有测试证明它确实按我们的意图工作。这正是黑盒测试的真正优势！

试着重跑测试；它应该会抱怨无法构建镜像。当然，因为我们压根还没有程序可构建！

要让测试完整跑通，我们需要一个监听 `8080` 端口的程序，但**仅此而已**。守住 TDD 的纪律：在确认测试按预期失败之前，别写会让测试通过的生产代码。

在 `httpserver` 文件夹里创建一个 `main.go`，内容如下：

```go
package main

import (
	"log"
	"net/http"
)

func main() {
	handler := http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
	})
	if err := http.ListenAndServe(":8080", handler); err != nil {
		log.Fatal(err)
	}
}
```

再跑一次测试，这次应该会这样失败：

```
    greet.go:16: Expected values to be equal:
        +Hello, World
        \ No newline at end of file
--- FAIL: TestGreeterHandler (2.09s)
```

## 写足够的代码让它通过

更新处理器，让它按规格想要的方式行事：

```go
import (
	"fmt"
	"log"
	"net/http"
)

func main() {
	handler := http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		fmt.Fprint(w, "Hello, world")
	})
	if err := http.ListenAndServe(":8080", handler); err != nil {
		log.Fatal(err)
	}
}
```

## 重构

虽然严格说这不算重构，但我们不该依赖默认的 HTTP 客户端，所以改一下驱动器，让它可以从外部传入 client，测试里会传一个给它。

```go
import (
	"io"
	"net/http"
)

type Driver struct {
	BaseURL string
	Client  *http.Client
}

func (d Driver) Greet() (string, error) {
	res, err := d.Client.Get(d.BaseURL + "/greet")
	if err != nil {
		return "", err
	}
	defer res.Body.Close()
	greeting, err := io.ReadAll(res.Body)
	if err != nil {
		return "", err
	}
	return string(greeting), nil
}
```

在 `cmd/httpserver/greeter_server_test.go` 的测试里，更新驱动器的创建，传入一个 client。

```go
client := http.Client{
	Timeout: 1 * time.Second,
}

driver := go_specs_greet.Driver{BaseURL: "http://localhost:8080", Client: &client}
specifications.GreetSpecification(t, driver)
```

保持 `main.go` 尽可能简单是好习惯；它只该负责把你造好的积木拼装成应用。

在项目根目录建一个 `handler.go`，把我们的代码挪进去。

```go
package go_specs_greet

import (
	"fmt"
	"net/http"
)

func Handler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprint(w, "Hello, world")
}
```

更新 `main.go`，导入并改用这个 handler。

```go
package main

import (
	"net/http"

	go_specs_greet "github.com/quii/go-specs-greet"
)

func main() {
	handler := http.HandlerFunc(go_specs_greet.Handler)
	http.ListenAndServe(":8080", handler)
}
```

## 复盘

第一步感觉挺费劲。我们建了好几个 `go` 文件，就为了创建并测试一个返回硬编码字符串的 HTTP 处理器。但这次"第 0 次迭代"的仪式和铺垫，会在后续迭代中持续帮到我们。

改功能应该简单而可控：通过规格驱动变更，然后处理规格迫使我们做的那些修改。现在 Dockerfile 和 testcontainers 已经为我们的验收测试搭好了；除非构建应用的方式变了，我们不应该再动这些文件。

接下来的新需求会印证这一点：向特定的人问候。

## 先写测试

编辑我们的规格：

```go
package specifications

import (
	"testing"

	"github.com/alecthomas/assert/v2"
)

type Greeter interface {
	Greet(name string) (string, error)
}

func GreetSpecification(t testing.TB, greeter Greeter) {
	got, err := greeter.Greet("Mike")
	assert.NoError(t, err)
	assert.Equal(t, got, "Hello, Mike")
}
```

要能向特定的人问候，我们得把系统的接口改成接收一个 `name` 参数。

## 试着运行测试

```
./greeter_server_test.go:48:39: cannot use driver (variable of type go_specs_greet.Driver) as type specifications.Greeter in argument to specifications.GreetSpecification:
	go_specs_greet.Driver does not implement specifications.Greeter (wrong type for Greet method)
		have Greet() (string, error)
		want Greet(name string) (string, error)
```

规格变了，驱动器也得跟着更新。

## 写最少的代码让测试跑起来，检查失败的输出

更新驱动器，让它在请求里带上 `name` 查询参数，指明要问候哪个 `name`。

```go
import "io"

func (d Driver) Greet(name string) (string, error) {
	res, err := d.Client.Get(d.BaseURL + "/greet?name=" + name)
	if err != nil {
		return "", err
	}
	defer res.Body.Close()
	greeting, err := io.ReadAll(res.Body)
	if err != nil {
		return "", err
	}
	return string(greeting), nil
}
```

测试现在应该能跑了，然后失败：

```
    greet.go:16: Expected values to be equal:
        -Hello, world
        \ No newline at end of file
        +Hello, Mike
        \ No newline at end of file
--- FAIL: TestGreeterHandler (1.92s)
```

## 写足够的代码让它通过

从请求里取出 `name`，然后问候它。

```go
import (
	"fmt"
	"net/http"
)

func Handler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello, %s", r.URL.Query().Get("name"))
}
```

测试现在应该过了。

## 重构

在[HTTP 处理器再谈](https://github.com/quii/learn-go-with-tests/blob/main/http-handlers-revisited.md)（英文原版）一章里，我们讨论过让 HTTP 处理器只负责处理 HTTP 相关的事有多重要；任何"领域逻辑"都应该活在处理器之外。这样我们就能脱离 HTTP 单独开发领域逻辑，测试和理解起来都更简单。

让我们把这些关注点拆开。

把 `./handler.go` 里的处理器更新成这样：

```go
func Handler(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")
	fmt.Fprint(w, Greet(name))
}
```

新建 `./greet.go`：

```go
package go_specs_greet

import "fmt"

func Greet(name string) string {
	return fmt.Sprintf("Hello, %s", name)
}
```

## 顺路小憩："适配器"设计模式

既然我们已经把问候人的领域逻辑拆到了单独的函数里，现在可以轻松地给 Greet 函数写单元测试了。这无疑比"通过一份规格、经由驱动器、打到 web 服务器、就为拿一个字符串"要简单得多！

如果规格在这里也能复用，岂不美哉？毕竟规格的意义就在于与实现细节解耦。既然规格捕捉的是我们的**本质复杂性**，而"领域"代码就该为它建模，那两者理应能配到一起。

来试试，按下面创建 `./greet_test.go`：

```go
package go_specs_greet_test

import (
	"testing"

	go_specs_greet "github.com/quii/go-specs-greet"
	"github.com/quii/go-specs-greet/specifications"
)

func TestGreet(t *testing.T) {
	specifications.GreetSpecification(t, go_specs_greet.Greet)
}

```

想法很美好，但它跑不通：

```
./greet_test.go:11:39: cannot use go_specs_greet.Greet (value of type func(name string) string) as type specifications.Greeter in argument to specifications.GreetSpecification:
	func(name string) string does not implement specifications.Greeter (missing Greet method)
```

我们的规格想要一个有 `Greet()` 方法的家伙，而不是一个函数。

这个编译错误让人郁闷：我们明明"知道"手里这东西是个 `Greeter`，但它的**形状**差了那么一点，编译器不让我们用。**适配器**（adapter）模式正是为这种情况准备的。

> 在[软件工程](https://en.wikipedia.org/wiki/Software_engineering)中，**适配器模式**（adapter pattern）是一种[软件设计模式](https://en.wikipedia.org/wiki/Software_design_pattern)（也称为[包装器](https://en.wikipedia.org/wiki/Wrapper_function)，与[装饰器模式](https://en.wikipedia.org/wiki/Decorator_pattern)共享这个别名），它允许把现有[类](https://en.wikipedia.org/wiki/Class_(computer_science))的[接口](https://en.wikipedia.org/wiki/Interface_(computer_science))当作另一个接口来用。[1](https://en.wikipedia.org/wiki/Adapter_pattern#cite_note-HeadFirst-1) 它常用于让现有的类无需修改其[源代码](https://en.wikipedia.org/wiki/Source_code)就能与其他类协作。

一堆花哨的词，说的其实是件挺简单的事。设计模式大抵如此，所以人们提起它们总爱翻白眼。设计模式的价值不在于具体的实现，而在于它是一门语言，用来描述工程师们面对常见问题时的特定解法。如果团队共享一套词汇，沟通的摩擦就会小很多。

把这段代码加到 `./specifications/adapters.go`：

```go
type GreetAdapter func(name string) string

func (g GreetAdapter) Greet(name string) (string, error) {
	return g(name), nil
}
```

现在我们可以在测试里用这个适配器，把 `Greet` 函数插到规格上。

```go
package go_specs_greet_test

import (
	"testing"

	gospecsgreet "github.com/quii/go-specs-greet"
	"github.com/quii/go-specs-greet/specifications"
)

func TestGreet(t *testing.T) {
	specifications.GreetSpecification(
		t,
		specifications.GreetAdapter(gospecsgreet.Greet),
	)
}
```

当你手里有一个类型，它具备接口想要的行为，但形状不对时，适配器模式就派上用场了。

## 复盘

这次行为变更感觉很简单，对吧？好吧，也许只是这个问题本身简单，但这种工作方式给了你纪律，给了你一条自上而下改造系统的简单、可复制的路子：

- 分析你的问题，找出一个能把系统推向正确方向的小改进
- 把新的本质复杂性写进规格
- 跟着编译错误走，直到验收测试能跑
- 更新实现，让系统按规格行事
- 重构

熬过第一次迭代的痛苦之后，我们再没动过验收测试代码，因为我们有了规格、驱动器与实现的分离。改规格要求我们更新驱动器，最后更新实现，但"如何把系统作为容器跑起来"的那堆样板代码完全不受影响。

即便算上为应用构建 docker 镜像、把容器跑起来的开销，测试**整个**应用的反馈回路也非常紧凑：

```
quii@Chriss-MacBook-Pro go-specs-greet % go test ./...
ok  	github.com/quii/go-specs-greet	0.181s
ok  	github.com/quii/go-specs-greet/cmd/httpserver	2.221s
?   	github.com/quii/go-specs-greet/specifications	[no test files]
```

现在，想象你的 CTO 宣布 gRPC 才是*未来*。她要你在保留现有 HTTP 服务器的同时，用 gRPC 服务器把同样的功能暴露出去。

这是**偶然复杂性**的一个例子。记住，偶然复杂性是因为我们跟计算机打交道才不得不应付的复杂性，比如网络、磁盘、API 之类。**本质复杂性没有变**，所以我们不应该需要改规格。

很多仓库结构和设计模式，主要干的就是分离不同种类的复杂性这件事。比如"端口与适配器"（ports and adapters）就要求你把领域代码与一切跟偶然复杂性沾边的东西分开；那部分代码住在"adapters"文件夹里。

### 先让改变变容易

有时候，在做出变更*之前*先做些重构，才是明智之举。

> First make the change easy, then make the easy change
> （先让改变变容易，再做那个容易的改变）

~Kent Beck

为此，我们把 `http` 相关代码——`driver.go` 和 `handler.go`——挪进 `adapters` 文件夹下一个叫 `httpserver` 的包，并把它们的包名改成 `httpserver`。

现在你得在 `handler.go` 里导入根包才能引用 Greet 方法……

```go
package httpserver

import (
	"fmt"
	"net/http"

	go_specs_greet "github.com/quii/go-specs-greet/domain/interactions"
)

func Handler(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("name")
	fmt.Fprint(w, go_specs_greet.Greet(name))
}

```

在 main.go 里导入你的 httpserver 适配器：

```go
package main

import (
	"net/http"

	"github.com/quii/go-specs-greet/adapters/httpserver"
)

func main() {
	handler := http.HandlerFunc(httpserver.Handler)
	http.ListenAndServe(":8080", handler)
}
```

再更新 greeter_server_test.go 里对 `Driver` 的导入和引用：

```go
driver := httpserver.Driver{BaseURL: "http://localhost:8080", Client: &client}
```

最后，把领域层的代码也收拢进它自己的文件夹，同样很有帮助。别犯懒，别在项目里搞一个塞满成百上千个毫不相干的类型和函数的 `domain` 文件夹。花点心思琢磨你的领域，把属于一起的想法归到一起。这会让项目更好理解，也会提升你 import 的质量。

与其看到

```go
domain.Greet
```

这么个有点怪的东西，不如选

```go
interactions.Greet
```

建一个 `domain` 文件夹装下所有领域代码，并在其中建一个 `interactions` 文件夹。取决于你的工具，你可能得更新一些 import 和代码。

我们的项目树现在应该长这样：

```
quii@Chriss-MacBook-Pro go-specs-greet % tree
.
├── Makefile
├── README.md
├── adapters
│   └── httpserver
│       ├── driver.go
│       └── handler.go
├── cmd
│   └── httpserver
|       ├── Dockerfile
│       ├── greeter_server_test.go
│       └── main.go
├── domain
│   └── interactions
│       ├── greet.go
│       └── greet_test.go
├── go.mod
├── go.sum
└── specifications
    └── adapters.go
    └── greet.go

```

我们的领域代码——**本质复杂性**——住在 go 模块的根部；让我们能在"真实世界"里用上它们的代码，归入**适配器**。`cmd` 文件夹则负责把这些逻辑分组组装成实际的应用，应用配有黑盒测试来验证一切正常。漂亮！

最后，我们可以对验收测试做一丁点整理。看看验收测试的高层步骤：

- 构建 docker 镜像
- 等它开始在*某个*端口上监听
- 创建一个懂"怎么把 DSL 翻译成系统特定调用"的驱动器
- 把驱动器插到规格上

……你会意识到，gRPC 服务器的验收测试需要的东西一模一样！

`adapters` 文件夹看上去就是个合适的地方，所以在名为 `docker.go` 的文件里，把前两步封装进一个函数，下一步就会复用它。

```go
package adapters

import (
	"context"
	"fmt"
	"testing"
	"time"

	"github.com/alecthomas/assert/v2"
	"github.com/docker/go-connections/nat"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"
)

func StartDockerServer(
	t testing.TB,
	port string,
	dockerFilePath string,
) {
	ctx := context.Background()
	t.Helper()
	req := testcontainers.ContainerRequest{
		FromDockerfile: testcontainers.FromDockerfile{
			Context:       "../../.",
			Dockerfile:    dockerFilePath,
			PrintBuildLog: true,
		},
		ExposedPorts: []string{fmt.Sprintf("%s:%s", port, port)},
		WaitingFor:   wait.ForListeningPort(nat.Port(port)).WithStartupTimeout(5 * time.Second),
	}
	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	assert.NoError(t, err)
	t.Cleanup(func() {
		assert.NoError(t, container.Terminate(ctx))
	})
}
```

这也给了我们一个机会，把验收测试清理一下：

```go
func TestGreeterServer(t *testing.T) {
	var (
		port           = "8080"
		dockerFilePath = "./cmd/httpserver/Dockerfile"
		baseURL        = fmt.Sprintf("http://localhost:%s", port)
		driver         = httpserver.Driver{BaseURL: baseURL, Client: &http.Client{
			Timeout: 1 * time.Second,
		}}
	)

	adapters.StartDockerServer(t, port, dockerFilePath)
	specifications.GreetSpecification(t, driver)
}
```

这样，写*下一个*测试就简单了。

## 先写测试

这个新功能可以通过创建一个新的适配器来跟领域代码交互来实现。所以我们应该：

- 不必改规格；
- 能够复用规格；
- 能够复用领域代码。

在 `cmd` 里新建一个 `grpcserver` 文件夹，装下我们的新程序和对应的验收测试。在 `cmd/grpc_server/greeter_server_test.go` 里加一个验收测试，它跟 HTTP 服务器测试长得非常像——这不是巧合，是设计使然。

```go
package main_test

import (
	"fmt"
	"testing"

	"github.com/quii/go-specs-greet/adapters"
	"github.com/quii/go-specs-greet/adapters/grpcserver"
	"github.com/quii/go-specs-greet/specifications"
)

func TestGreeterServer(t *testing.T) {
	var (
		port           = "50051"
		dockerFilePath = "./cmd/grpcserver/Dockerfile"
		driver         = grpcserver.Driver{Addr: fmt.Sprintf("localhost:%s", port)}
	)

	adapters.StartDockerServer(t, port, dockerFilePath)
	specifications.GreetSpecification(t, &driver)
}
```

仅有的区别是：

- 我们用了另一个 docker 文件，因为构建的是另一个程序
- 这意味着我们需要一个新的 `Driver`，它用 `gRPC` 跟新程序交互

## 试着运行测试

```
./greeter_server_test.go:26:12: undefined: grpcserver
```

我们还没创建 `Driver`，所以编译不过。

## 写最少的代码让测试跑起来，检查失败的输出

在 `adapters` 里建一个 `grpcserver` 文件夹，在里面创建 `driver.go`：

```go
package grpcserver

type Driver struct {
	Addr string
}

func (d Driver) Greet(name string) (string, error) {
	return "", nil
}
```

再跑一次，现在应该能*编译*了，但过不了，因为我们还没有 Dockerfile 和对应的程序。

在 `cmd/grpcserver` 里新建一个 `Dockerfile`。

```dockerfile
# Make sure to specify the same Go version as the one in the go.mod file.
FROM golang:1.18-alpine

WORKDIR /app

COPY go.mod ./

RUN go mod download

COPY . .

RUN go build -o svr cmd/grpcserver/*.go

EXPOSE 50051
CMD [ "./svr" ]
```

再加一个 `main.go`：

```go
package main

import "fmt"

func main() {
	fmt.Println("implement me")
}
```

你会发现测试失败了，因为我们的服务器还没监听端口。现在是时候用 gRPC 构建我们的客户端和服务器了。

## 写足够的代码让它通过

### gRPC

如果你不熟悉 gRPC，我建议先去 [gRPC 官网](https://grpc.io)看看。不过就本章而言，它只是接入我们系统的又一种适配器，是其他系统远程过程调用（**r**emote **p**rocedure **c**all）我们出色领域代码的一种方式。

特别之处在于：你要用 Protocol Buffers 定义一个"服务定义"，然后从这个定义生成服务器和客户端代码。这不但适用于 Go，也适用于大多数主流语言。这意味着你可以把定义分享给公司里可能根本不写 Go 的其他团队，服务间的通信照样顺畅。

如果你没用过 gRPC，需要安装一个 **Protocol buffer 编译器**和若干 **Go 插件**。[gRPC 官网有清晰的安装说明](https://grpc.io/docs/languages/go/quickstart/)。

在我们新驱动器所在的文件夹里，加一个 `greet.proto` 文件，内容如下：

```protobuf
syntax = "proto3";

option go_package = "github.com/quii/adapters/grpcserver";

package grpcserver;

service Greeter {
  rpc Greet (GreetRequest) returns (GreetReply) {}
}

message GreetRequest {
  string name = 1;
}

message GreetReply {
  string message = 1;
}
```

要看懂这个定义，你不需要成为 Protocol Buffers 专家。我们定义了一个带 Greet 方法的服务，然后描述了进出的消息类型。

在 `adapters/grpcserver` 里运行下面的命令，生成客户端和服务器代码：

```
protoc --go_out=. --go_opt=paths=source_relative \
    --go-grpc_out=. --go-grpc_opt=paths=source_relative \
    greet.proto
```

如果一切顺利，我们就有了可以使用的生成代码。先在 `Driver` 里用上生成的客户端代码。

```go
package grpcserver

import (
	"context"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type Driver struct {
	Addr string
}

func (d Driver) Greet(name string) (string, error) {
	//todo: 每次调用 greet 都重新拨号不对，等测试变绿后重构掉
	conn, err := grpc.Dial(d.Addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return "", err
	}
	defer conn.Close()

	client := NewGreeterClient(conn)
	greeting, err := client.Greet(context.Background(), &GreetRequest{
		Name: name,
	})
	if err != nil {
		return "", err
	}

	return greeting.Message, nil
}
```

有了客户端，接下来要更新 `main.go` 来创建服务器。记住，到了这一步我们只求测试通过，代码质量先放一边。

```go
package main

import (
	"context"
	"log"
	"net"

	"github.com/quii/go-specs-greet/adapters/grpcserver"
	"google.golang.org/grpc"
)

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatal(err)
	}
	s := grpc.NewServer()
	grpcserver.RegisterGreeterServer(s, &GreetServer{})

	if err := s.Serve(lis); err != nil {
		log.Fatal(err)
	}
}

type GreetServer struct {
	grpcserver.UnimplementedGreeterServer
}

func (g GreetServer) Greet(ctx context.Context, request *grpcserver.GreetRequest) (*grpcserver.GreetReply, error) {
	return &grpcserver.GreetReply{Message: "fixme"}, nil
}
```

要创建 gRPC 服务器，我们必须实现它为我们生成的那个接口：

```go
// GreeterServer 是 Greeter 服务的服务器端 API。
// 所有实现都必须内嵌 UnimplementedGreeterServer
// 以保证向前兼容
type GreeterServer interface {
	Greet(context.Context, *GreetRequest) (*GreetReply, error)
	mustEmbedUnimplementedGreeterServer()
}
```

我们的 `main` 函数：

- 监听一个端口
- 创建一个实现了该接口的 `GreetServer`，把它连同 `grpc.Server` 一起注册到 `grpcServer.RegisterGreeterServer`
- 用这个监听器跑起服务器

在 `greetServer.Greet` 里调用领域代码、而不是把 `fix-me` 硬编码在消息里，其实费不了多大事。但我想先跑一遍验收测试，确认传输层一切正常，顺便看看失败的测试输出。

```
greet.go:16: Expected values to be equal:
-fixme
\ No newline at end of file
+Hello, Mike
\ No newline at end of file
```

漂亮！可以看到，驱动器已经能在测试里连上我们的 gRPC 服务器了。

现在，在 `GreetServer` 里调用我们的领域代码：

```go
type GreetServer struct {
	grpcserver.UnimplementedGreeterServer
}

func (g GreetServer) Greet(ctx context.Context, request *grpcserver.GreetRequest) (*grpcserver.GreetReply, error) {
	return &grpcserver.GreetReply{Message: interactions.Greet(request.Name)}, nil
}
```

终于过了！我们有了一条验收测试，证明我们的 gRPC 问候服务器按我们想要的方式行事。

## 重构

为了让测试通过，我们犯下了不少罪过；但现在测试都绿了，我们就有了重构的安全网。

### 精简 main

跟之前一样，我们不希望 `main` 里塞太多代码。可以把新的 `GreetServer` 挪进 `adapters/grpcserver`，那才是它该住的地方。从内聚的角度讲，如果我们改了服务定义，我们希望变更的"爆炸半径"只波及代码的那一小块。

### 别在驱动器里每次都重新拨号

我们只有一条测试，但一旦扩展规格（我们会的），驱动器每次 RPC 调用都重新拨号就说不过去了。

```go
package grpcserver

import (
	"context"
	"sync"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type Driver struct {
	Addr string

	connectionOnce sync.Once
	conn           *grpc.ClientConn
	client         GreeterClient
}

func (d *Driver) Greet(name string) (string, error) {
	client, err := d.getClient()
	if err != nil {
		return "", err
	}

	greeting, err := client.Greet(context.Background(), &GreetRequest{
		Name: name,
	})
	if err != nil {
		return "", err
	}

	return greeting.Message, nil
}

func (d *Driver) getClient() (GreeterClient, error) {
	var err error
	d.connectionOnce.Do(func() {
		d.conn, err = grpc.Dial(d.Addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
		d.client = NewGreeterClient(d.conn)
	})
	return d.client, err
}
```

这里我们展示了如何用 [`sync.Once`](https://pkg.go.dev/sync#Once) 确保我们的 `Driver` 只尝试创建一次到服务器的连接。

继续之前，看看项目结构现在的样子。

```
quii@Chriss-MacBook-Pro go-specs-greet % tree
.
├── Makefile
├── README.md
├── adapters
│   ├── docker.go
│   ├── grpcserver
│   │   ├── driver.go
│   │   ├── greet.pb.go
│   │   ├── greet.proto
│   │   ├── greet_grpc.pb.go
│   │   └── server.go
│   └── httpserver
│       ├── driver.go
│       └── handler.go
├── cmd
│   ├── grpcserver
│   │   ├── Dockerfile
│   │   ├── greeter_server_test.go
│   │   └── main.go
│   └── httpserver
│       ├── Dockerfile
│       ├── greeter_server_test.go
│       └── main.go
├── domain
│   └── interactions
│       ├── greet.go
│       └── greet_test.go
├── go.mod
├── go.sum
└── specifications
    └── greet.go
```

- `adapters` 把内聚的功能单元归拢到一起
- `cmd` 放我们的应用和对应的验收测试
- 我们的代码与一切偶然复杂性彻底解耦

### 合并 `Dockerfile`

你可能已经注意到，两个 Dockerfile 几乎一模一样，只有要构建的二进制路径不同。

Dockerfile 可以接受参数，让我们在不同语境下复用同一个文件，这听上去正合适。删掉那两个 Dockerfile，在项目根目录放一个这样的：

```dockerfile
# Make sure to specify the same Go version as the one in the go.mod file.
FROM golang:1.18-alpine

WORKDIR /app

ARG bin_to_build

COPY go.mod ./

RUN go mod download

COPY . .

RUN go build -o svr cmd/${bin_to_build}/main.go

CMD [ "./svr" ]
```

我们得更新 `StartDockerServer` 函数，在构建镜像时传入参数：

```go
func StartDockerServer(
	t testing.TB,
	port string,
	binToBuild string,
) {
	ctx := context.Background()
	t.Helper()
	req := testcontainers.ContainerRequest{
		FromDockerfile: testcontainers.FromDockerfile{
			Context:    "../../.",
			Dockerfile: "Dockerfile",
			BuildArgs: map[string]*string{
				"bin_to_build": &binToBuild,
			},
			PrintBuildLog: true,
		},
		ExposedPorts: []string{fmt.Sprintf("%s:%s", port, port)},
		WaitingFor:   wait.ForListeningPort(nat.Port(port)).WithStartupTimeout(5 * time.Second),
	}
	container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
		ContainerRequest: req,
		Started:          true,
	})
	assert.NoError(t, err)
	t.Cleanup(func() {
		assert.NoError(t, container.Terminate(ctx))
	})
}
```

最后，更新我们的测试，传入要构建的目标名（另一个测试也要改，把 `grpcserver` 换成 `httpserver`）：

```go
func TestGreeterServer(t *testing.T) {
	var (
		port   = "50051"
		driver = grpcserver.Driver{Addr: fmt.Sprintf("localhost:%s", port)}
	)

	adapters.StartDockerServer(t, port, "grpcserver")
	specifications.GreetSpecification(t, &driver)
}
```

### 分开跑不同种类的测试

验收测试的好，在于它能以纯用户视角、纯行为视角验证整个系统都能工作；但跟单元测试比，它也有短板：

- 更慢
- 反馈的质量往往不如单元测试聚焦
- 帮不上内部质量和设计

[测试金字塔](https://martinfowler.com/articles/practical-test-pyramid.html)告诉我们测试套件该有什么样的配比；Fowler 那篇文章值得细读，这里只给一个极简的总结："大量单元测试，少量验收测试"。

因此，随着项目变大，你常常会碰到验收测试要跑好几分钟的情况。为了给检出你项目的人一个友好的开发者体验，你可以让开发者分开跑不同种类的测试。

理想情况是，工程师检出项目后不需要任何额外配置，`go test ./...` 就能直接跑，顶多需要一些关键依赖，比如 Go 编译器（这是必须的）和 Docker。

Go 提供了一个机制，让工程师只跑"短"测试，就是 [short 标志](https://pkg.go.dev/testing#Short)：

`go test -short ./...`

我们可以在验收测试里检查这个标志的值，看用户想不想跑验收测试：

```go
if testing.Short() {
	t.Skip()
}
```

我写了个 `Makefile` 来演示这种用法：

```makefile
build:
	golangci-lint run
	go test ./...

unit-tests:
	go test -short ./...
```

### 什么时候该写验收测试？

最佳实践是多写跑得快的单元测试、少写验收测试，但具体到某个场景，你怎么决定该写验收测试还是单元测试？

给出一条铁律很难，但我通常会问自己这些问题：

- 这是边界情况吗？我更倾向于用单元测试覆盖它们
- 这是业务人员经常念叨的事吗？这种关键的东西我希望有足够的把握它"真的"能工作，所以我会加验收测试
- 我描述的是一段用户旅程，还是一个具体函数？验收测试
- 单元测试能给我足够的信心吗？有时你面对的是一段已经有验收测试覆盖的用户旅程，只是因为不同的输入要多处理几种场景。这时再加一条验收测试成本不小、价值寥寥，我更倾向于写几个单元测试。

## 在已有成果上继续迭代

下了这么多功夫，你肯定希望现在扩展系统会变得简单。把系统做得好改，未必容易，但这时间花得值，而且在项目刚起步时就着手做，会容易得多。

让我们给 API 加一个"诅咒"（curse）功能。

## 先写测试

这是全新的行为，所以应该从验收测试开始。在我们的规格文件里加上：

```go
type MeanGreeter interface {
	Curse(name string) (string, error)
}

func CurseSpecification(t *testing.T, meany MeanGreeter) {
	got, err := meany.Curse("Chris")
	assert.NoError(t, err)
	assert.Equal(t, got, "Go to hell, Chris!")
}
```

随便挑一条验收测试，试着用上这份规格：

```go
func TestGreeterServer(t *testing.T) {
	if testing.Short() {
		t.Skip()
	}
	var (
		port   = "50051"
		driver = grpcserver.Driver{Addr: fmt.Sprintf("localhost:%s", port)}
	)

	t.Cleanup(driver.Close)
	adapters.StartDockerServer(t, port, "grpcserver")
	specifications.GreetSpecification(t, &driver)
	specifications.CurseSpecification(t, &driver)
}
```

## 试着运行测试

```
# github.com/quii/go-specs-greet/cmd/grpcserver_test [github.com/quii/go-specs-greet/cmd/grpcserver.test]
./greeter_server_test.go:27:39: cannot use &driver (value of type *grpcserver.Driver) as type specifications.MeanGreeter in argument to specifications.CurseSpecification:
	*grpcserver.Driver does not implement specifications.MeanGreeter (missing Curse method)
```

我们的 `Driver` 还不支持 `Curse`。

## 写最少的代码让测试跑起来，检查失败的输出

记住，我们只求测试能跑，所以给 `Driver` 加上方法：

```go
func (d *Driver) Curse(name string) (string, error) {
	return "", nil
}
```

再试一次，测试应该能编译、能跑，然后失败：

```
greet.go:26: Expected values to be equal:
+Go to hell, Chris!
\ No newline at end of file
```

## 写足够的代码让它通过

我们需要更新 protocol buffer 规格，给它加一个 `Curse` 方法，然后重新生成代码。

```protobuf
service Greeter {
  rpc Greet (GreetRequest) returns (GreetReply) {}
  rpc Curse (GreetRequest) returns (GreetReply) {}
}
```

你可以说复用 `GreetRequest` 和 `GreetReply` 这两个类型是不当耦合，但这个可以留到重构阶段处理。我一再强调：我们先求测试通过、验证软件能跑，*然后*再把它变漂亮。

（在 `adapters/grpcserver` 里）重新生成代码：

```
protoc --go_out=. --go_opt=paths=source_relative \
    --go-grpc_out=. --go-grpc_opt=paths=source_relative \
    greet.proto
```

### 更新驱动器

客户端代码更新好了，现在可以在 `Driver` 里调用 `Curse` 了：

```go
func (d *Driver) Curse(name string) (string, error) {
	client, err := d.getClient()
	if err != nil {
		return "", err
	}

	greeting, err := client.Curse(context.Background(), &GreetRequest{
		Name: name,
	})
	if err != nil {
		return "", err
	}

	return greeting.Message, nil
}
```

### 更新服务器

最后，给我们的 `Server` 加上 `Curse` 方法：

```go
package grpcserver

import (
	"context"
	"fmt"

	"github.com/quii/go-specs-greet/domain/interactions"
)

type GreetServer struct {
	UnimplementedGreeterServer
}

func (g GreetServer) Curse(ctx context.Context, request *GreetRequest) (*GreetReply, error) {
	return &GreetReply{Message: fmt.Sprintf("Go to hell, %s!", request.Name)}, nil
}

func (g GreetServer) Greet(ctx context.Context, request *GreetRequest) (*GreetReply, error) {
	return &GreetReply{Message: interactions.Greet(request.Name)}, nil
}
```

测试现在应该全过了。

## 重构

这部分自己动手试试。

- 像 `Greet` 那样，把 `Curse` 的"领域逻辑"从 grpc 服务器里抽出来。拿规格当作单元测试，对着你的领域逻辑跑
- 在 protobuf 里用不同的类型，确保 `Greet` 和 `Curse` 的消息类型解耦

## 给 HTTP 服务器实现 `Curse`

又是一道留给你的练习题。领域级规格和领域级逻辑我们已经分得清清楚楚，只要跟完了本章，这应该非常直白。

- 把规格加到 HTTP 服务器现有的验收测试里
- 更新你的 `Driver`
- 在服务器上加新的端点，复用领域代码实现功能。你可能想用 `http.NewServeMux` 来处理各端点间的路由

记得小步走，勤 commit，勤跑测试。如果实在卡住了，[GitHub 上有我的实现](https://github.com/quii/go-specs-greet)。

## 用单元测试更新领域逻辑，让两个系统同时受益

前面说过，不是对系统的每次修改都该由验收测试驱动。业务规则的排列组合和边界情况，只要关注点分得好，用单元测试驱动就应该很简单。

给我们的 `Greet` 函数加一个单元测试：`name` 为空时默认为 `World`。你会看到这有多简单，然后这条业务规则就"免费"地同时反映在两个应用里了。

## 收尾

构建一个变更成本合理的系统，需要你把验收测试打磨成帮手，而不是维护负担。你可以把它们当作引导软件的手段——用 GOOS 的话说，有章法地"培育"（growing）你的软件。

希望通过这个例子，你能看到我们驱动应用变更的那套可预测、结构化的工作流，以及如何把它用到你自己的工作中。

你可以想象跟一位干系人聊，他想以某种方式扩展你们在做的系统。把它以领域为中心、与实现无关的方式写进规格，作为你努力的北极星。我和 Riya 在[GopherconUK 的演讲](https://www.youtube.com/watch?v=ZMWJCk_0WrY)里介绍了如何借助"Example Mapping"等 BDD 技法，更深入地理解本质复杂性，写出更细致、更有意义的规格。

把本质复杂性和偶然复杂性的关注点分开，会让你的工作更少即兴发挥、更有结构、更有章法；这保证了验收测试的韧性，也让它们不再成为维护负担。

Dave Farley 给过一条极好的建议：

> 想象一个你能想到的、最不懂技术但理解这个问题领域的人，来读你的验收测试。这些测试应该能让那个人看明白。

这样，规格还能顺便当文档用。它们应该清楚地说明系统该怎么表现。[Cucumber](https://cucumber.io) 这类工具的立足点正是这个理念：它给你一套 DSL 来把行为捕捉成代码，然后你再把 DSL 转换成系统调用，跟我们这里做的一样。

### 本章覆盖了什么

- 编写抽象的规格，让你能表达所解决问题的本质复杂性、剔除偶然复杂性。这让你能在不同语境下复用规格。
- 如何用 [Testcontainers](https://golang.testcontainers.org) 为验收测试管理系统的生命周期。这让你能在自己的电脑上把打算发布的镜像测个透彻，反馈快、信心足。
- 简单介绍了如何用 Docker 容器化你的应用
- gRPC
- 与其追逐各种现成的文件夹结构教条，不如让你的开发方法自然地驱动出应用的结构，基于你自己的需要

### 延伸材料

- 在这个例子里，我们的"DSL"算不上真正的 DSL；我们只是用接口把规格从真实世界里解耦出来，让我们能干净地表达领域逻辑。随着系统长大，这个抽象层级可能会变得笨拙、含糊。如果你想找更多组织规格的思路，去读读 ["Screenplay Pattern"](https://cucumber.io/blog/bdd/understanding-screenplay-part-1/)。
- 再强调一次，[《Growing Object-Oriented Software, Guided by Tests》](http://www.growing-object-oriented-software.com)是一本经典。它演示了如何把这种"伦敦学派"的、"自顶向下"的软件开发方式付诸实践。喜欢《Learn Go with Tests》的人，读 GOOS 一定会大有收获。
- [在示例代码仓库](https://github.com/quii/go-specs-greet)里，还有一些本文没写到的代码和点子，比如多阶段 docker 构建，值得一看。
  - 尤其是，*为了好玩*，我做了**第三个程序**，一个带 HTML 表单的网站，可以 `Greet` 和 `Curse`。`Driver` 用上了出色的 [https://github.com/go-rod/rod](https://github.com/go-rod/rod) 模块，它能像真正的用户一样用浏览器操作网站。翻翻 git 历史，你能看到我是怎么先不用任何模板工具"让它先跑起来"的；等验收测试一过，我就有了放开手脚重构的自由，而不用怕弄坏东西。 -->
