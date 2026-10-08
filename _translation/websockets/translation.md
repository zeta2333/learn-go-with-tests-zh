# WebSockets

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/websockets)**

本章我们来看看怎么用 WebSocket 改进我们的应用。

## 项目回顾

我们的扑克代码库里目前有两个应用

* _命令行应用_。提示用户输入一局比赛的玩家数量，从那时起不断向玩家播报“盲注”（blind bet）值——这个值会随时间增长。玩家随时可以输入 `"{Playername} wins"` 来结束比赛，把胜者记录进 store。
* _Web 应用_。让用户记录各场比赛的胜者，并展示联盟积分表。它与命令行应用共用同一个 store。

## 下一步

产品负责人对命令行应用满意得很，但她更希望我们能把这些功能搬进浏览器。她设想了这样一个网页：有个文本框让用户输入玩家数量；提交表单后，页面显示出盲注值，并且到了该涨的时候自动更新。跟命令行应用一样，用户可以宣布胜者，然后保存进数据库。

乍一听相当简单，但跟往常一样，我们必须强调用_迭代_的方式写软件。

首先我们得能把 HTML 返回给用户。到目前为止，我们的 HTTP 端点返回的要么是纯文本，要么是 JSON。我们_可以_继续用已掌握的那些招数（反正说到底都是字符串），但用 [html/template](https://golang.org/pkg/html/template/) 包会有更干净的方案。

我们还需要能异步地给用户发消息，告诉他们 `The blind is now *y*`，而不必刷新浏览器。这可以借助 [WebSockets](https://en.wikipedia.org/wiki/WebSocket) 来实现。

> WebSocket 是一种计算机通信协议，在单个 TCP 连接上提供全双工（full-duplex）通信通道。

一次要上手的新东西这么多，就更有必要先做最少量的有用工作，然后再迭代。

因此我们要做的第一件事，是创建一个带表单的网页，让用户能记录胜者。我们不打算用普通的表单，而是用 WebSocket 把数据发给服务器去记录。

之后我们再处理盲注提醒，到那时手上已经有一些基础设施代码了。

### 那 JavaScript 的测试呢？

我们确实会写一些 JavaScript 来实现这些功能，但不会展开讲怎么为它写测试。

当然这是可以做到的，不过为了控制篇幅，我在这方面不做展开。

抱歉了各位。大家去游说 O'Reilly 出钱请我写一本《Learn JavaScript with tests》吧。

## 先写测试

第一件事，是当用户访问 `/game` 时给他们返回一些 HTML。

先回顾一下 web 服务器里相关的代码

```go
type PlayerServer struct {
	store PlayerStore
	http.Handler
}

const jsonContentType = "application/json"

func NewPlayerServer(store PlayerStore) *PlayerServer {
	p := new(PlayerServer)

	p.store = store

	router := http.NewServeMux()
	router.Handle("/league", http.HandlerFunc(p.leagueHandler))
	router.Handle("/players/", http.HandlerFunc(p.playersHandler))

	p.Handler = router

	return p
}
```

眼下我们能做的_最简单_的事，就是确认请求 `GET /game` 能拿到一个 `200`。

```go
func TestGame(t *testing.T) {
	t.Run("GET /game returns 200", func(t *testing.T) {
		server := NewPlayerServer(&StubPlayerStore{})

		request, _ := http.NewRequest(http.MethodGet, "/game", nil)
		response := httptest.NewRecorder()

		server.ServeHTTP(response, request)

		assertStatus(t, response.Code, http.StatusOK)
	})
}
```

## 试着运行测试

```
--- FAIL: TestGame (0.00s)
=== RUN   TestGame/GET_/game_returns_200
    --- FAIL: TestGame/GET_/game_returns_200 (0.00s)
    	server_test.go:109: did not get correct status, got 404, want 200
```

## 写足够的代码让测试通过

我们的服务器已经搭好了路由，所以修起来相对容易。

往路由里加一条

```go
router.Handle("/game", http.HandlerFunc(p.game))
```

然后写 `game` 方法

```go
func (p *PlayerServer) game(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
}
```

## 重构

现有的代码划分得当，新代码很容易就插了进去，服务器这边已经没什么可挑剔的了。

测试这边还可以再收拾一下：加一个辅助函数 `newGameRequest`，专门负责构造对 `/game` 的请求。不妨自己动手试试。

```go
func TestGame(t *testing.T) {
	t.Run("GET /game returns 200", func(t *testing.T) {
		server := NewPlayerServer(&StubPlayerStore{})

		request := newGameRequest()
		response := httptest.NewRecorder()

		server.ServeHTTP(response, request)

		assertStatus(t, response, http.StatusOK)
	})
}
```

你可能还注意到，我把 `assertStatus` 改成了接收 `response` 而不是 `response.Code`，我觉得这样读起来更顺。

现在要让这个端点返回一些 HTML 了，内容如下

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Let's play poker</title>
</head>
<body>
<section id="game">
    <div id="declare-winner">
        <label for="winner">Winner</label>
        <input type="text" id="winner"/>
        <button id="winner-button">Declare winner</button>
    </div>
</section>
</body>
<script type="application/javascript">

    const submitWinnerButton = document.getElementById('winner-button')
    const winnerInput = document.getElementById('winner')

    if (window['WebSocket']) {
        const conn = new WebSocket('ws://' + document.location.host + '/ws')

        submitWinnerButton.onclick = event => {
            conn.send(winnerInput.value)
        }
    }
</script>
</html>
```

我们有了一个非常简单的网页

* 一个文本输入框，用户在里面填入胜者
* 一个按钮，点击即宣布胜者
* 一些 JavaScript，负责打开一条连到服务器的 WebSocket 连接，并处理提交按钮的点击

`WebSocket` 内置于大多数现代浏览器，我们不必引入任何库。这个网页在老浏览器上跑不起来，不过在当前场景下我们无所谓。

### 怎么测试我们返回的标记是对的？

办法有好几种。正像全书反复强调的：你写的测试必须物有所值，收益要配得上成本。

1. 写基于浏览器的测试，比如用 Selenium 这类工具。这类测试在所有方案里最“真实”，因为它们会真的启动某种浏览器，模拟用户与它交互。这种测试能给你很大的信心，但比单元测试难写，跑起来也慢得多。就我们这款产品而言，这属于杀鸡用牛刀。
2. 做精确的字符串比对。这_有时候_也行，但这类测试往往非常脆弱：只要有人动了标记，测试就挂，而实际上根本没_真的_坏掉什么。
3. 检查我们调用的是正确的模板。我们将用标准库的模板库来返回 HTML（稍后讨论），可以把生成 HTML 的那个_东西_注入进来，spy 它的调用，确认我们做得对。这会影响代码的设计，却又验不出太多东西——顶多证明我们用了正确的模板文件。鉴于整个项目只会有这一个模板，这里出岔子的概率看起来很低。

所以在《Learn Go with Tests》这本书里，我们将头一次不写测试。

把上面的标记存进一个名为 `game.html` 的文件

接着把我们刚写的端点改成下面这样

```go
func (p *PlayerServer) game(w http.ResponseWriter, r *http.Request) {
	tmpl, err := template.ParseFiles("game.html")

	if err != nil {
		http.Error(w, fmt.Sprintf("problem loading template %s", err.Error()), http.StatusInternalServerError)
		return
	}

	tmpl.Execute(w, nil)
}
```

[`html/template`](https://golang.org/pkg/html/template/) 是一个用来生成 HTML 的 Go 包。这里我们调用 `template.ParseFiles`，传入 html 文件的路径。只要没有错误，接下来就可以对模板执行 `Execute`，它会把内容写进一个 `io.Writer`。我们这里想让它 `Write` 到互联网上，所以把 `http.ResponseWriter` 交给它。

既然没写测试，稳妥起见还是手动跑一下 web 服务器，确认一切符合预期。进入 `cmd/webserver` 目录运行 `main.go`，然后访问 `http://localhost:5000/game`。

你_应该_会看到一个找不到模板的报错。你可以把路径改成相对当前目录的路径，也可以往 `cmd/webserver` 目录里放一份 `game.html`。我的选择是给项目根目录里的那份文件建一个符号链接（`ln -s ../../game.html game.html`），这样模板一有改动，运行服务器时就能直接生效。

改完再跑一次，你应该就能看到我们的界面了。

接下来我们要测试：当一条字符串通过 WebSocket 连接发到我们的服务器时，我们会把它宣布为一场比赛的胜者。

## 先写测试

我们将头一次引入外部库，用来处理 WebSocket。

运行 `go get github.com/gorilla/websocket`

这会拉取出色的 [Gorilla WebSocket](https://github.com/gorilla/websocket) 库的代码。现在可以按新需求更新我们的测试了。

```go
t.Run("when we get a message over a websocket it is a winner of a game", func(t *testing.T) {
	store := &StubPlayerStore{}
	winner := "Ruth"
	server := httptest.NewServer(NewPlayerServer(store))
	defer server.Close()

	wsURL := "ws" + strings.TrimPrefix(server.URL, "http") + "/ws"

	ws, _, err := websocket.DefaultDialer.Dial(wsURL, nil)
	if err != nil {
		t.Fatalf("could not open a ws connection on %s %v", wsURL, err)
	}
	defer ws.Close()

	if err := ws.WriteMessage(websocket.TextMessage, []byte(winner)); err != nil {
		t.Fatalf("could not send message over ws connection %v", err)
	}

	AssertPlayerWin(t, store, winner)
})
```

记得给 `websocket` 库加上 import。我的 IDE 自动画好了，你的应该也行。

要测试浏览器那头会发生什么，我们得自己开一条 WebSocket 连接，往里写数据。

之前针对服务器的测试只是直接调用服务器的方法，而现在我们需要一条到服务器的持久连接。为此我们用 `httptest.NewServer`，它接收一个 `http.Handler`，会把它跑起来监听连接。

用 `websocket.DefaultDialer.Dial` 尝试拨号连到我们的服务器，然后把 `winner` 作为消息发过去。

最后，我们对 player store 做断言，确认胜者已被记录。

## 试着运行测试

```
=== RUN   TestGame/when_we_get_a_message_over_a_websocket_it_is_a_winner_of_a_game
    --- FAIL: TestGame/when_we_get_a_message_over_a_websocket_it_is_a_winner_of_a_game (0.00s)
        server_test.go:124: could not open a ws connection on ws://127.0.0.1:55838/ws websocket: bad handshake
```

我们还没有改服务器去接受 `/ws` 路径上的 WebSocket 连接，所以握手（handshake）还没发生。

## 写足够的代码让测试通过

再往路由里加一条

```go
router.Handle("/ws", http.HandlerFunc(p.webSocket))
```

然后写新的 `webSocket` 处理器

```go
func (p *PlayerServer) webSocket(w http.ResponseWriter, r *http.Request) {
	upgrader := websocket.Upgrader{
		ReadBufferSize:  1024,
		WriteBufferSize: 1024,
	}
	upgrader.Upgrade(w, r, nil)
}
```

要接受 WebSocket 连接，需要对请求做升级（`Upgrade`）。现在重跑测试，应该会跳到下一个错误。

```
=== RUN   TestGame/when_we_get_a_message_over_a_websocket_it_is_a_winner_of_a_game
    --- FAIL: TestGame/when_we_get_a_message_over_a_websocket_it_is_a_winner_of_a_game (0.00s)
        server_test.go:132: got 0 calls to RecordWin want 1
```

连接已经打开了，接下来我们要监听消息，把它记录为胜者。

```go
func (p *PlayerServer) webSocket(w http.ResponseWriter, r *http.Request) {
	upgrader := websocket.Upgrader{
		ReadBufferSize:  1024,
		WriteBufferSize: 1024,
	}
	conn, _ := upgrader.Upgrade(w, r, nil)
	_, winnerMsg, _ := conn.ReadMessage()
	p.store.RecordWin(string(winnerMsg))
}
```

（没错，我们现在忽略了一堆错误！）

`conn.ReadMessage()` 会阻塞着等待连接上的消息。拿到消息后我们就用它来 `RecordWin`。随后这条 WebSocket 连接也就关闭了。

再跑测试，还是挂。

问题出在时序上。从 WebSocket 连接读到消息、到把胜局记录下来，中间有延迟，而测试在这件事发生之前就结束了。你可以在最后一条断言前面加一个短暂的 `time.Sleep` 来验证这一点。

我们先暂且这么办，但必须承认：往测试里塞拍脑袋的 sleep **是非常糟糕的做法**。

```go
time.Sleep(10 * time.Millisecond)
AssertPlayerWin(t, store, winner)
```

## 重构

为了让测试跑起来，我们在服务器代码和测试代码里都犯下了不少“罪行”，但记住，这就是对我们来说最省事的工作方式。

我们手里有了又糟又烂、但_能跑_的软件，背后还有测试撑腰。现在可以放心把它打磨漂亮，并且确信不会一不小心弄坏什么。

先从服务器代码开始。

我们可以把 `upgrader` 挪成包内的一个私有值，因为没必要每来一个 WebSocket 连接请求都重新声明一遍

```go
var wsUpgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
}

func (p *PlayerServer) webSocket(w http.ResponseWriter, r *http.Request) {
	conn, _ := wsUpgrader.Upgrade(w, r, nil)
	_, winnerMsg, _ := conn.ReadMessage()
	p.store.RecordWin(string(winnerMsg))
}
```

对 `template.ParseFiles("game.html")` 的调用会发生在每一次 `GET /game` 上，这意味着每个请求都要跑一趟文件系统，尽管模板根本没必要反复解析。我们来重构：把解析挪到 `NewPlayerServer` 里只做一次。这也意味着这个函数得能返回错误，以防从磁盘读取模板或解析模板时出问题。

下面是 `PlayerServer` 的相关改动

```go
type PlayerServer struct {
	store PlayerStore
	http.Handler
	template *template.Template
}

const htmlTemplatePath = "game.html"

func NewPlayerServer(store PlayerStore) (*PlayerServer, error) {
	p := new(PlayerServer)

	tmpl, err := template.ParseFiles(htmlTemplatePath)

	if err != nil {
		return nil, fmt.Errorf("problem opening %s %v", htmlTemplatePath, err)
	}

	p.template = tmpl
	p.store = store

	router := http.NewServeMux()
	router.Handle("/league", http.HandlerFunc(p.leagueHandler))
	router.Handle("/players/", http.HandlerFunc(p.playersHandler))
	router.Handle("/game", http.HandlerFunc(p.game))
	router.Handle("/ws", http.HandlerFunc(p.webSocket))

	p.Handler = router

	return p, nil
}

func (p *PlayerServer) game(w http.ResponseWriter, r *http.Request) {
	p.template.Execute(w, nil)
}
```

改了 `NewPlayerServer` 的签名，编译错误就来了。自己试着修一修，实在卡住就参考源代码。

测试代码这边，我写了一个辅助函数 `mustMakePlayerServer(t *testing.T, store PlayerStore) *PlayerServer`，好把报错的噪音从测试里藏起来。

```go
func mustMakePlayerServer(t *testing.T, store PlayerStore) *PlayerServer {
	server, err := NewPlayerServer(store)
	if err != nil {
		t.Fatal("problem creating player server", err)
	}
	return server
}
```

类似地，我又写了另一个辅助函数 `mustDialWS`，把创建 WebSocket 连接时讨厌的报错噪音也藏起来。

```go
func mustDialWS(t *testing.T, url string) *websocket.Conn {
	ws, _, err := websocket.DefaultDialer.Dial(url, nil)

	if err != nil {
		t.Fatalf("could not open a ws connection on %s %v", url, err)
	}

	return ws
}
```

最后，测试代码里再加一个辅助函数，把发送消息这件事也收拾利索

```go
func writeWSMessage(t testing.TB, conn *websocket.Conn, message string) {
	t.Helper()
	if err := conn.WriteMessage(websocket.TextMessage, []byte(message)); err != nil {
		t.Fatalf("could not send message over ws connection %v", err)
	}
}
```

现在测试都过了，试着把服务器跑起来，在 `/game` 页面上宣布几个胜者。你应该能在 `/league` 里看到记录。记住：每收到一个胜者我们就会_关闭连接_，你得刷新页面才能重新建立连接。

我们做出了一个不起眼但能用的网页表单，让用户可以记录比赛的胜者。接下来在它上面继续迭代：让用户输入玩家数量来开局，服务器则随时间推移向客户端推送消息，告知当前的盲注值。

首先更新 `game.html`，按新需求改写客户端代码

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Lets play poker</title>
</head>
<body>
<section id="game">
    <div id="game-start">
        <label for="player-count">Number of players</label>
        <input type="number" id="player-count"/>
        <button id="start-game">Start</button>
    </div>

    <div id="declare-winner">
        <label for="winner">Winner</label>
        <input type="text" id="winner"/>
        <button id="winner-button">Declare winner</button>
    </div>

    <div id="blind-value"/>
</section>

<section id="game-end">
    <h1>Another great game of poker everyone!</h1>
    <p><a href="/league">Go check the league table</a></p>
</section>

</body>
<script type="application/javascript">
    const startGame = document.getElementById('game-start')

    const declareWinner = document.getElementById('declare-winner')
    const submitWinnerButton = document.getElementById('winner-button')
    const winnerInput = document.getElementById('winner')

    const blindContainer = document.getElementById('blind-value')

    const gameContainer = document.getElementById('game')
    const gameEndContainer = document.getElementById('game-end')

    declareWinner.hidden = true
    gameEndContainer.hidden = true

    document.getElementById('start-game').addEventListener('click', event => {
        startGame.hidden = true
        declareWinner.hidden = false

        const numberOfPlayers = document.getElementById('player-count').value

        if (window['WebSocket']) {
            const conn = new WebSocket('ws://' + document.location.host + '/ws')

            submitWinnerButton.onclick = event => {
                conn.send(winnerInput.value)
                gameEndContainer.hidden = false
                gameContainer.hidden = true
            }

            conn.onclose = evt => {
                blindContainer.innerText = 'Connection closed'
            }

            conn.onmessage = evt => {
                blindContainer.innerText = evt.data
            }

            conn.onopen = function () {
                conn.send(numberOfPlayers)
            }
        }
    })
</script>
</html>
```

主要改动是新增了一个输入玩家数量的区块和一个展示盲注值的区块，另外写了一点根据比赛阶段显示/隐藏界面的逻辑。

凡是通过 `conn.onmessage` 收到的消息，我们都当作盲注提醒，相应地设置 `blindContainer.innerText`。

那么盲注提醒该怎么发呢？上一章我们引入了 `Game` 的概念，让 CLI 代码调用一个 `Game`，其余的事情——包括安排盲注提醒——都由它包办。事后来看，这是一次不错的关注点分离。

```go
type Game interface {
	Start(numberOfPlayers int)
	Finish(winner string)
}
```

用户在 CLI 里按提示输入玩家数量后就 `Start` 比赛，盲注提醒随之启动；用户宣布胜者时就 `Finish`。这与我们现在面对的是同一套需求，只是获取输入的途径不同；所以只要能复用，就应该复用这个概念。

`Game` 的“真正”实现是 `TexasHoldem`

```go
type TexasHoldem struct {
	alerter BlindAlerter
	store   PlayerStore
}
```

通过传入一个 `BlindAlerter`，`TexasHoldem` 就能把盲注提醒安排发往_任何地方_

```go
type BlindAlerter interface {
	ScheduleAlertAt(duration time.Duration, amount int)
}
```

顺便回顾一下，这是我们在 CLI 里用的 `BlindAlerter` 实现。

```go
func StdOutAlerter(duration time.Duration, amount int) {
	time.AfterFunc(duration, func() {
		fmt.Fprintf(os.Stdout, "Blind is now %d\n", amount)
	})
}
```

它在 CLI 里行得通，是因为我们_始终想把提醒发给 `os.Stdout`_，但这对我们的 web 服务器行不通：每来一个请求，都会拿到一个新的 `http.ResponseWriter`，随后被升级为 `*websocket.Conn`。所以在组装依赖的那一刻，我们无从知道提醒该发往何处。

因此我们需要修改 `BlindAlerter.ScheduleAlertAt`，让它接收一个提醒的目的地，这样才能在 web 服务器里复用。

打开 `blind_alerter.go`，给接口加上 `io.Writer` 参数

```go
type BlindAlerter interface {
	ScheduleAlertAt(duration time.Duration, amount int, to io.Writer)
}

type BlindAlerterFunc func(duration time.Duration, amount int, to io.Writer)

func (a BlindAlerterFunc) ScheduleAlertAt(duration time.Duration, amount int, to io.Writer) {
	a(duration, amount, to)
}
```

`StdoutAlerter` 这个叫法已经不贴合新模型了，直接改名为 `Alerter`

```go
func Alerter(duration time.Duration, amount int, to io.Writer) {
	time.AfterFunc(duration, func() {
		fmt.Fprintf(to, "Blind is now %d\n", amount)
	})
}
```

这时编译会在 `TexasHoldem` 上失败，因为它调用 `ScheduleAlertAt` 时没有给目的地；_眼下_为了让编译先过，把它硬编码成 `os.Stdout`。

跑一下测试，会失败，因为 `SpyBlindAlerter` 不再实现 `BlindAlerter` 了；更新 `ScheduleAlertAt` 的签名修好它，再跑测试，我们应该还是绿的。

让 `TexasHoldem` 知道盲注提醒发往哪里并不合理。现在来改 `Game`，让你在开局时声明提醒应该发到_哪儿_。

```go
type Game interface {
	Start(numberOfPlayers int, alertsDestination io.Writer)
	Finish(winner string)
}
```

让编译器告诉你需要修什么。改动不算糟：

* 更新 `TexasHoldem`，让它正确实现 `Game`
* 在 `CLI` 里开始比赛时，把 `out` 属性传进去（`cli.game.Start(numberOfPlayers, cli.out)`）
* 在 `TexasHoldem` 的测试里，我用 `game.Start(5, io.Discard)` 修好编译问题，同时把提醒输出丢弃掉

都改对的话，一切应该重新变绿！现在可以试着在 `Server` 里用上 `Game` 了。

## 先写测试

`CLI` 和 `Server` 的需求是一样的！只是消息的送达机制不同。

来看看 `CLI` 的测试找找灵感。

```go
t.Run("start game with 3 players and finish game with 'Chris' as winner", func(t *testing.T) {
	game := &GameSpy{}

	out := &bytes.Buffer{}
	in := userSends("3", "Chris wins")

	poker.NewCLI(in, out, game).PlayPoker()

	assertMessagesSentToUser(t, out, poker.PlayerPrompt)
	assertGameStartedWith(t, game, 3)
	assertFinishCalledWith(t, game, "Chris")
})
```

看起来我们应该能用 `GameSpy` 测试驱动出类似的效果

把旧的 WebSocket 测试换成下面这个

```go
t.Run("start a game with 3 players and declare Ruth the winner", func(t *testing.T) {
	game := &poker.GameSpy{}
	winner := "Ruth"
	server := httptest.NewServer(mustMakePlayerServer(t, dummyPlayerStore, game))
	ws := mustDialWS(t, "ws"+strings.TrimPrefix(server.URL, "http")+"/ws")

	defer server.Close()
	defer ws.Close()

	writeWSMessage(t, ws, "3")
	writeWSMessage(t, ws, winner)

	time.Sleep(10 * time.Millisecond)
	assertGameStartedWith(t, game, 3)
	assertFinishCalledWith(t, game, winner)
})
```

* 如前所述，我们创建一个 spy `Game` 传给 `mustMakePlayerServer`（记得更新那个辅助函数来支持这一点）。
* 然后通过 WebSocket 发送开局所需的消息。
* 最后断言比赛按我们的预期开始并结束。

## 试着运行测试

其他测试里会冒出一堆与 `mustMakePlayerServer` 相关的编译错误。引入一个未导出的变量 `dummyGame`，在所有编译不过的测试里都用上它

```go
var (
	dummyGame = &GameSpy{}
)
```

最后一个错误是：我们想把 `Game` 传给 `NewPlayerServer`，但它还不支持

```
./server_test.go:21:38: too many arguments in call to "github.com/quii/learn-go-with-tests/WebSockets/v2".NewPlayerServer
	have ("github.com/quii/learn-go-with-tests/WebSockets/v2".PlayerStore, "github.com/quii/learn-go-with-tests/WebSockets/v2".Game)
	want ("github.com/quii/learn-go-with-tests/WebSockets/v2".PlayerStore)
```

## 写最少的代码让测试能运行，并检查失败的测试输出

先把它加成参数，能让测试跑起来就行

```go
func NewPlayerServer(store PlayerStore, game Game) (*PlayerServer, error)
```

终于！

```
=== RUN   TestGame/start_a_game_with_3_players_and_declare_Ruth_the_winner
--- FAIL: TestGame (0.01s)
    --- FAIL: TestGame/start_a_game_with_3_players_and_declare_Ruth_the_winner (0.01s)
    	server_test.go:146: wanted Start called with 3 but got 0
    	server_test.go:147: expected finish called with 'Ruth' but got ''
FAIL
```

## 写足够的代码让测试通过

我们需要把 `Game` 加为 `PlayerServer` 的一个字段，这样它在收到请求时才能用上它。

```go
type PlayerServer struct {
	store PlayerStore
	http.Handler
	template *template.Template
	game     Game
}
```

（我们已经有一个叫 `game` 的方法了，把它改名为 `playGame`）

接着在构造函数里给它赋值

```go
func NewPlayerServer(store PlayerStore, game Game) (*PlayerServer, error) {
	p := new(PlayerServer)

	tmpl, err := template.ParseFiles(htmlTemplatePath)

	if err != nil {
		return nil, fmt.Errorf("problem opening %s %v", htmlTemplatePath, err)
	}

	p.game = game

	// 其余不变
}
```

现在可以在 `webSocket` 里用上我们的 `Game` 了。

```go
func (p *PlayerServer) webSocket(w http.ResponseWriter, r *http.Request) {
	conn, _ := wsUpgrader.Upgrade(w, r, nil)

	_, numberOfPlayersMsg, _ := conn.ReadMessage()
	numberOfPlayers, _ := strconv.Atoi(string(numberOfPlayersMsg))
	p.game.Start(numberOfPlayers, io.Discard) //todo: 别把盲注消息丢掉了！

	_, winner, _ := conn.ReadMessage()
	p.game.Finish(string(winner))
}
```

万岁！测试全过了。

我们_暂时_还不打算把盲注消息发到任何地方，因为这事儿得先好好想想。调用 `game.Start` 时我们传的是 `io.Discard`，凡是写进它的消息都会被丢掉。

眼下先把 web 服务器跑起来。你需要更新 `main.go`，把一个 `Game` 传给 `PlayerServer`

```go
func main() {
	db, err := os.OpenFile(dbFileName, os.O_RDWR|os.O_CREATE, 0666)

	if err != nil {
		log.Fatalf("problem opening %s %v", dbFileName, err)
	}

	store, err := poker.NewFileSystemPlayerStore(db)

	if err != nil {
		log.Fatalf("problem creating file system player store, %v ", err)
	}

	game := poker.NewTexasHoldem(poker.BlindAlerterFunc(poker.Alerter), store)

	server, err := poker.NewPlayerServer(store, game)

	if err != nil {
		log.Fatalf("problem creating player server %v", err)
	}

	log.Fatal(http.ListenAndServe(":5000", server))
}
```

先不提还收不到盲注提醒这件事，应用确实能跑了！我们成功地在 `PlayerServer` 里复用了 `Game`，所有细节都由它打理。等我们弄清楚怎么把盲注提醒经由 WebSocket 发出去而不是一丢了之，一切_应该_就都通了。

不过在那之前，先收拾一下代码。

## 重构

我们对 WebSocket 的用法相当初级，错误处理也相当天真，所以我想把这些封装进一个类型，把这份凌乱从服务器代码里剥离出去。以后也许会回头再改，但眼下这能让代码整洁一些

```go
type playerServerWS struct {
	*websocket.Conn
}

func newPlayerServerWS(w http.ResponseWriter, r *http.Request) *playerServerWS {
	conn, err := wsUpgrader.Upgrade(w, r, nil)

	if err != nil {
		log.Printf("problem upgrading connection to WebSockets %v\n", err)
	}

	return &playerServerWS{conn}
}

func (w *playerServerWS) WaitForMsg() string {
	_, msg, err := w.ReadMessage()
	if err != nil {
		log.Printf("error reading from websocket %v\n", err)
	}
	return string(msg)
}
```

现在服务器代码简化了一点

```go
func (p *PlayerServer) webSocket(w http.ResponseWriter, r *http.Request) {
	ws := newPlayerServerWS(w, r)

	numberOfPlayersMsg := ws.WaitForMsg()
	numberOfPlayers, _ := strconv.Atoi(numberOfPlayersMsg)
	p.game.Start(numberOfPlayers, io.Discard) //todo: 别把盲注消息丢掉了！

	winner := ws.WaitForMsg()
	p.game.Finish(winner)
}
```

等我们搞定“不丢弃盲注消息”这件事，就大功告成了。

### 这次我们_偏不_写测试！

有些时候，对一件事该怎么做没把握，最好的办法就是上手玩一玩、试一试！先确保手头的代码已经 commit，因为一旦摸索出思路，我们就该通过测试把它正式驱动出来。

惹麻烦的就是这行代码

```go
p.game.Start(numberOfPlayers, io.Discard) //todo: 别把盲注消息丢掉了！
```

我们需要传给游戏一个 `io.Writer`，让它把盲注提醒写进去。

要是能把之前那个 `playerServerWS` 传进去岂不美哉？它是我们对 WebSocket 的包装，_感觉上_就应该能把它交给 `Game`，让消息发往那里。

试试看：

```go
func (p *PlayerServer) webSocket(w http.ResponseWriter, r *http.Request) {
	ws := newPlayerServerWS(w, r)

	numberOfPlayersMsg := ws.WaitForMsg()
	numberOfPlayers, _ := strconv.Atoi(numberOfPlayersMsg)
	p.game.Start(numberOfPlayers, ws)
	// 其余省略……
}
```

编译器抱怨了

```
./server.go:71:14: cannot use ws (type *playerServerWS) as type io.Writer in argument to p.game.Start:
	*playerServerWS does not implement io.Writer (missing Write method)
```

顺理成章的做法，似乎就是让 `playerServerWS` _真正_实现 `io.Writer`。为此，我们用底层的 `*websocket.Conn`，通过 `WriteMessage` 把消息顺着这条 websocket 发出去

```go
func (w *playerServerWS) Write(p []byte) (n int, err error) {
	err = w.WriteMessage(websocket.TextMessage, p)

	if err != nil {
		return 0, err
	}

	return len(p), nil
}
```

这也太简单了吧！跑一下应用，看看是不是真的能用。

事先把 `TexasHoldem` 里的盲注增长间隔改短一点，方便看到实际效果

```go
blindIncrement := time.Duration(5+numberOfPlayers) * time.Second // 而不是一分钟
```

应该能看到它跑起来了！盲注金额在浏览器里自己往上涨，像变魔法一样。

现在把代码还原，想想怎么测试它。刚才为了_实现_这个功能，我们所做的一切就是把传给 `Start` 的参数从 `io.Discard` 换成了 `playerServerWS`，这也许会让你想到：或许可以 spy 那次调用，验证它真的发生了。

Spy 很好用，能帮我们检查实现细节，但只要条件允许，我们总应优先测试_真实行为_。因为等你决定重构时，往往正是 spy 测试最先挂掉——它们检查的通常恰恰是你要改掉的实现细节。

我们的测试目前是开一条 websocket 连接连到运行中的服务器，然后发消息让它干活。同样地，我们也应该能测试服务器通过这条 websocket 连接发回来的消息。

## 先写测试

我们来修改现有的测试。

目前，调用 `GameSpy` 的 `Start` 时它不会向 `out` 发送任何数据。我们把它改成可以配置为发送一条预设消息，然后检查这条消息有没有被送到 websocket。这样既能让我们确信配置无误，又切实覆盖了我们想测的真实行为。

```go
type GameSpy struct {
	StartCalled     bool
	StartCalledWith int
	BlindAlert      []byte

	FinishedCalled   bool
	FinishCalledWith string
}
```

加上 `BlindAlert` 字段。

更新 `GameSpy` 的 `Start`，把预设消息写到 `out`。

```go
func (g *GameSpy) Start(numberOfPlayers int, out io.Writer) {
	g.StartCalled = true
	g.StartCalledWith = numberOfPlayers
	out.Write(g.BlindAlert)
}
```

这样一来，当我们驱动 `PlayerServer` 去 `Start` 比赛时，只要一切正常，消息最终就应该经由 websocket 发送出去。

最后，我们可以更新测试了

```go
t.Run("start a game with 3 players, send some blind alerts down WS and declare Ruth the winner", func(t *testing.T) {
	wantedBlindAlert := "Blind is 100"
	winner := "Ruth"

	game := &GameSpy{BlindAlert: []byte(wantedBlindAlert)}
	server := httptest.NewServer(mustMakePlayerServer(t, dummyPlayerStore, game))
	ws := mustDialWS(t, "ws"+strings.TrimPrefix(server.URL, "http")+"/ws")

	defer server.Close()
	defer ws.Close()

	writeWSMessage(t, ws, "3")
	writeWSMessage(t, ws, winner)

	time.Sleep(10 * time.Millisecond)
	assertGameStartedWith(t, game, 3)
	assertFinishCalledWith(t, game, winner)

	_, gotBlindAlert, _ := ws.ReadMessage()

	if string(gotBlindAlert) != wantedBlindAlert {
		t.Errorf("got blind alert %q, want %q", string(gotBlindAlert), wantedBlindAlert)
	}
})
```

* 我们加了 `wantedBlindAlert`，并配置 `GameSpy` 在 `Start` 被调用时把它写给 `out`。
* 我们期望它经由这条 websocket 连接发送出去，所以加了 `ws.ReadMessage()` 调用，等一条消息送达，再检查它是不是我们期望的那条。

## 试着运行测试

你会发现测试永远卡住不动。这是因为 `ws.ReadMessage()` 会阻塞到收到一条消息为止，而它永远等不来。

## 写最少的代码让测试能运行，并检查失败的测试输出

我们不该留着会无限挂起的测试，所以来引入一种处理超时的手段。

```go
func within(t testing.TB, d time.Duration, assert func()) {
	t.Helper()

	done := make(chan struct{}, 1)

	go func() {
		assert()
		done <- struct{}{}
	}()

	select {
	case <-time.After(d):
		t.Error("timed out")
	case <-done:
	}
}
```

`within` 做的事情是：接收一个 `assert` 函数作为参数，然后把它放进 goroutine 里运行。函数一旦跑完，就会通过 `done` channel 发信号说自己完成了。

与此同时，我们用一条 `select` 语句等待某个 channel 发来消息。接下来就是一场赛跑：一边是 `assert` 函数，另一边是 `time.After`——后者会在时限到达时发出信号。

最后，我为断言又写了一个辅助函数，让代码更整洁一点

```go
func assertWebsocketGotMsg(t *testing.T, ws *websocket.Conn, want string) {
	_, msg, _ := ws.ReadMessage()
	if string(msg) != want {
		t.Errorf(`got "%s", want "%s"`, string(msg), want)
	}
}
```

现在这个测试读起来是这样

```go
t.Run("start a game with 3 players, send some blind alerts down WS and declare Ruth the winner", func(t *testing.T) {
	wantedBlindAlert := "Blind is 100"
	winner := "Ruth"

	game := &GameSpy{BlindAlert: []byte(wantedBlindAlert)}
	server := httptest.NewServer(mustMakePlayerServer(t, dummyPlayerStore, game))
	ws := mustDialWS(t, "ws"+strings.TrimPrefix(server.URL, "http")+"/ws")

	defer server.Close()
	defer ws.Close()

	writeWSMessage(t, ws, "3")
	writeWSMessage(t, ws, winner)

	time.Sleep(tenMS)

	assertGameStartedWith(t, game, 3)
	assertFinishCalledWith(t, game, winner)
	within(t, tenMS, func() { assertWebsocketGotMsg(t, ws, wantedBlindAlert) })
})
```

现在再跑测试……

```
=== RUN   TestGame
=== RUN   TestGame/start_a_game_with_3_players,_send_some_blind_alerts_down_WS_and_declare_Ruth_the_winner
--- FAIL: TestGame (0.02s)
    --- FAIL: TestGame/start_a_game_with_3_players,_send_some_blind_alerts_down_WS_and_declare_Ruth_the_winner (0.02s)
    	server_test.go:143: timed out
    	server_test.go:150: got "", want "Blind is 100"
```

## 写足够的代码让测试通过

终于可以改服务器代码了：开局时把我们的 WebSocket 连接交给游戏

```go
func (p *PlayerServer) webSocket(w http.ResponseWriter, r *http.Request) {
	ws := newPlayerServerWS(w, r)

	numberOfPlayersMsg := ws.WaitForMsg()
	numberOfPlayers, _ := strconv.Atoi(numberOfPlayersMsg)
	p.game.Start(numberOfPlayers, ws)

	winner := ws.WaitForMsg()
	p.game.Finish(winner)
}
```

## 重构

服务器代码只动了很小的一处，这里没什么可再改的；但测试代码里还留着一个 `time.Sleep` 调用，因为我们得等服务器异步把活干完。

我们可以重构辅助函数 `assertGameStartedWith` 和 `assertFinishCalledWith`，让它们在宣告失败之前，先对断言做一小段时间的重试。

下面是 `assertFinishCalledWith` 的写法，另一个辅助函数照同样的思路处理即可。

```go
func assertFinishCalledWith(t testing.TB, game *GameSpy, winner string) {
	t.Helper()

	passed := retryUntil(500*time.Millisecond, func() bool {
		return game.FinishCalledWith == winner
	})

	if !passed {
		t.Errorf("expected finish called with %q but got %q", winner, game.FinishCalledWith)
	}
}
```

`retryUntil` 的定义如下

```go
func retryUntil(d time.Duration, f func() bool) bool {
	deadline := time.Now().Add(d)
	for time.Now().Before(deadline) {
		if f() {
			return true
		}
	}
	return false
}
```

## 收尾

我们的应用至此完工。现在可以通过浏览器开局打扑克；随着时间推移，用户会经由 WebSocket 收到盲注值的播报；比赛结束后可以记录胜者，持久化用的正是我们几章之前写的代码。玩家们还能通过网站的 `/league` 端点一较高下，看看谁是最厉害（或者手气最好）的扑克玩家。

这一路我们犯过错，但靠着 TDD 的节奏，我们离能跑的软件从来都不远，可以放手持续迭代、持续试验。

最后一章会对这一路的方法、我们最终得到的设计做个回顾，并收掉一些没做完的尾巴。

本章我们收获了这些内容

### WebSockets

* 一种在客户端与服务器之间互发消息的便捷方式，客户端无需一直轮询服务器。我们的客户端和服务器代码都非常简单。
* 测试起来不难，但得留心测试固有的异步特性

### 处理测试中可能延迟、甚至永不结束的代码

* 编写辅助函数来重试断言、添加超时。
* 我们可以用 goroutine 保证断言不阻塞任何东西，再用 channel 让它们发信号表明自己是否完成。
* `time` 包有一些实用的函数，同样经由 channel 就时间相关的事件发信号，这样我们就能设置超时。
