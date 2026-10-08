# JSON、路由与嵌入

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/json)**

[上一章](https://github.com/quii/learn-go-with-tests/blob/main/http-server.md)（英文原版）里，我们创建了一个 Web 服务器，用来记录玩家赢了多少场比赛。

产品负责人提了个新需求：新增一个名为 `/league` 的端点，返回已存储的所有玩家的列表。她希望这个列表以 JSON 格式返回。

## 目前的代码

```go
// server.go
package main

import (
	"fmt"
	"net/http"
	"strings"
)

type PlayerStore interface {
	GetPlayerScore(name string) int
	RecordWin(name string)
}

type PlayerServer struct {
	store PlayerStore
}

func (p *PlayerServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	player := strings.TrimPrefix(r.URL.Path, "/players/")

	switch r.Method {
	case http.MethodPost:
		p.processWin(w, player)
	case http.MethodGet:
		p.showScore(w, player)
	}
}

func (p *PlayerServer) showScore(w http.ResponseWriter, player string) {
	score := p.store.GetPlayerScore(player)

	if score == 0 {
		w.WriteHeader(http.StatusNotFound)
	}

	fmt.Fprint(w, score)
}

func (p *PlayerServer) processWin(w http.ResponseWriter, player string) {
	p.store.RecordWin(player)
	w.WriteHeader(http.StatusAccepted)
}
```

```go
// in_memory_player_store.go
package main

func NewInMemoryPlayerStore() *InMemoryPlayerStore {
	return &InMemoryPlayerStore{map[string]int{}}
}

type InMemoryPlayerStore struct {
	store map[string]int
}

func (i *InMemoryPlayerStore) RecordWin(name string) {
	i.store[name]++
}

func (i *InMemoryPlayerStore) GetPlayerScore(name string) int {
	return i.store[name]
}

```

```go
// main.go
package main

import (
	"log"
	"net/http"
)

func main() {
	server := &PlayerServer{NewInMemoryPlayerStore()}
	log.Fatal(http.ListenAndServe(":5000", server))
}
```

对应的测试代码可以在本章开头的链接里找到。

我们先来做联盟积分表（league table）这个端点。

## 先写测试

我们就在现有的测试套件上扩展，好用的测试辅助函数和一个 fake `PlayerStore` 都是现成的。

```go
//server_test.go
func TestLeague(t *testing.T) {
	store := StubPlayerStore{}
	server := &PlayerServer{&store}

	t.Run("it returns 200 on /league", func(t *testing.T) {
		request, _ := http.NewRequest(http.MethodGet, "/league", nil)
		response := httptest.NewRecorder()

		server.ServeHTTP(response, request)

		assertStatus(t, response.Code, http.StatusOK)
	})
}
```

先不考虑真正的得分数据和 JSON，我们尽量让改动小一点，计划朝着目标一步步迭代。最简单的起点是：确认请求 `/league` 能拿回一个 `OK`。

## 试着运行测试

```
    --- FAIL: TestLeague/it_returns_200_on_/league (0.00s)
        server_test.go:101: status code is wrong: got 404, want 200
FAIL
FAIL	playerstore	0.221s
FAIL
```

`PlayerServer` 返回了 `404 Not Found`，就好像我们在查询一个不存在的玩家的胜场数。看看 `server.go` 里 `ServeHTTP` 的实现就会发现，它总是假定进来的 URL 指向某个具体的玩家：

```go
player := strings.TrimPrefix(r.URL.Path, "/players/")
```

上一章我们就提过，这种路由写法相当天真。测试正确地提醒了我们：我们需要一种机制来处理不同的请求路径。

## 写足够的代码让测试通过

Go 内置了一个路由机制，叫 [`ServeMux`](https://golang.org/pkg/net/http/#ServeMux)（请求多路复用器），它可以把 `http.Handler` 绑定到特定的请求路径上。

我们先造点孽，用最快的速度让测试通过——反正等测试绿了，再放心地重构也不迟。

```go
//server.go
func (p *PlayerServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {

	router := http.NewServeMux()

	router.Handle("/league", http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))

	router.Handle("/players/", http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		player := strings.TrimPrefix(r.URL.Path, "/players/")

		switch r.Method {
		case http.MethodPost:
			p.processWin(w, player)
		case http.MethodGet:
			p.showScore(w, player)
		}
	}))

	router.ServeHTTP(w, r)
}
```

- 请求进来时我们先创建一个路由器，然后告诉它：路径 `x` 用 `y` 这个 handler 来处理。
- 对于新端点，我们用 `http.HandlerFunc` 包了一个*匿名函数*，请求 `/league` 时执行 `w.WriteHeader(http.StatusOK)`，让新测试通过。
- 至于 `/players/` 这条路由，只是把原来的代码剪切粘贴进了另一个 `http.HandlerFunc`。
- 最后，调用新路由器的 `ServeHTTP` 来处理进来的请求（注意到了吗，`ServeMux` *本身也是*一个 `http.Handler`）。

测试现在应该能过了。

## 重构

`ServeHTTP` 看着有点臃肿了，我们可以把各个 handler 重构成独立的方法，让代码各归各位。

```go
//server.go
func (p *PlayerServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {

	router := http.NewServeMux()
	router.Handle("/league", http.HandlerFunc(p.leagueHandler))
	router.Handle("/players/", http.HandlerFunc(p.playersHandler))

	router.ServeHTTP(w, r)
}

func (p *PlayerServer) leagueHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
}

func (p *PlayerServer) playersHandler(w http.ResponseWriter, r *http.Request) {
	player := strings.TrimPrefix(r.URL.Path, "/players/")

	switch r.Method {
	case http.MethodPost:
		p.processWin(w, player)
	case http.MethodGet:
		p.showScore(w, player)
	}
}
```

每来一个请求都要现搭一个路由器然后再调用它，这相当奇怪（效率也低）。理想的做法是提供一个类似 `NewPlayerServer` 的函数，接收我们的依赖，并完成创建路由器这类只需做一次的设置。之后每个请求复用同一个路由器实例就可以了。

```go
//server.go
type PlayerServer struct {
	store  PlayerStore
	router *http.ServeMux
}

func NewPlayerServer(store PlayerStore) *PlayerServer {
	p := &PlayerServer{
		store,
		http.NewServeMux(),
	}

	p.router.Handle("/league", http.HandlerFunc(p.leagueHandler))
	p.router.Handle("/players/", http.HandlerFunc(p.playersHandler))

	return p
}

func (p *PlayerServer) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	p.router.ServeHTTP(w, r)
}
```

- `PlayerServer` 现在需要保存一个路由器。
- 我们把创建路由器的逻辑从 `ServeHTTP` 挪进了 `NewPlayerServer`，这样只需要做一次，而不是每个请求都做一遍。
- 之前所有写 `PlayerServer{&store}` 的测试代码和生产代码，你都需要改成 `NewPlayerServer(&store)`。

### 最后一次重构

试着把代码改成下面这样。

```go
type PlayerServer struct {
	store PlayerStore
	http.Handler
}

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

然后在 `server_test.go`、`server_integration_test.go` 和 `main.go` 里，把 `server := &PlayerServer{&store}` 换成 `server := NewPlayerServer(&store)`。

最后，一定记得**删掉** `func (p *PlayerServer) ServeHTTP(w http.ResponseWriter, r *http.Request)`，它已经没用了！

## 嵌入

我们改动了 `PlayerServer` 的第二个属性：去掉了具名属性 `router http.ServeMux`，换成了 `http.Handler`；这就叫*嵌入*（embedding）。

> Go 没有提供典型的、由类型驱动的子类化概念，但它支持把类型嵌入结构体或接口，从而"借用"一部分现成的实现。

[Effective Go - Embedding](https://golang.org/doc/effective_go.html#embedding)

这意味着 `PlayerServer` 现在拥有了 `http.Handler` 的全部方法——其实就一个 `ServeHTTP`。

要"填上"这个 `http.Handler`，只需把它赋值成我们在 `NewPlayerServer` 里创建的 `router`。可以这么做，是因为 `http.ServeMux` 有 `ServeHTTP` 这个方法。

这样一来，我们就可以删掉自己的 `ServeHTTP` 方法了，因为嵌入的类型已经替我们暴露了一个。

嵌入是个非常有趣的语言特性。把接口嵌进接口，就能组合出新接口。

```go
type Animal interface {
	Eater
	Sleeper
}
```

具体类型也能嵌入，不只是接口。可以想见，嵌入一个具体类型后，你就能访问它所有公开的方法和字段。

### 有什么缺点吗？

使用嵌入必须小心，因为你会暴露被嵌入类型的全部公开方法和字段。我们的场景没问题，因为嵌入的正是我们想暴露的那个*接口*（`http.Handler`）。

如果当初图省事，嵌入的是 `http.ServeMux`（具体类型），程序照样能跑，*但* `PlayerServer` 的使用者就能往我们的服务器上添加新路由了，因为 `Handle(path, handler)` 会是公开的。

**嵌入类型时，认真想想它会对你的公开 API 造成什么影响。**

滥用嵌入、最后污染了 API、把类型的内部细节暴露出去，是*非常*常见的错误。

现在应用的结构已经理顺，新增路由变得很容易，`/league` 端点也有了个开头。接下来要让它返回有用的信息。

我们要返回的 JSON 大概长这样。

```json
[
   {
      "Name":"Bill",
      "Wins":10
   },
   {
      "Name":"Alice",
      "Wins":15
   }
]
```

## 先写测试

第一步，我们先把响应解析成有意义的东西。

```go
//server_test.go
func TestLeague(t *testing.T) {
	store := StubPlayerStore{}
	server := NewPlayerServer(&store)

	t.Run("it returns 200 on /league", func(t *testing.T) {
		request, _ := http.NewRequest(http.MethodGet, "/league", nil)
		response := httptest.NewRecorder()

		server.ServeHTTP(response, request)

		var got []Player

		err := json.NewDecoder(response.Body).Decode(&got)

		if err != nil {
			t.Fatalf("Unable to parse response from server %q into slice of Player, '%v'", response.Body, err)
		}

		assertStatus(t, response.Code, http.StatusOK)
	})
}
```

### 为什么不直接测试 JSON 字符串？

你可能会说，更简单的第一步是直接断言响应体等于某个特定的 JSON 字符串。

以我的经验，针对 JSON 字符串做断言的测试有这么几个问题。

- *脆弱*。数据模型一改，测试就挂。
- *难以调试*。比较两个 JSON 字符串时，很难搞清楚真正的问题出在哪。
- *意图不清*。输出固然应该是 JSON，但真正重要的是数据到底是什么，而不是它怎么编码。
- *重复测试标准库*。标准库怎么输出 JSON 不用你测，人家早就测过了。别测试别人的代码。

正确的做法是，把 JSON 解析成对测试有意义的数据结构。

### 数据建模

从 JSON 的数据模型看，我们需要一个由 `Player` 组成的数组，每个 `Player` 带几个字段，所以我们新建了一个类型来描述它。

```go
//server.go
type Player struct {
	Name string
	Wins int
}
```

### JSON 解码

```go
//server_test.go
var got []Player
err := json.NewDecoder(response.Body).Decode(&got)
```

要把 JSON 解析进我们的数据模型，需要用 `encoding/json` 包创建一个 `Decoder`（解码器），然后调用它的 `Decode` 方法。创建 `Decoder` 需要一个 `io.Reader` 作为读取来源，在我们的场景里就是响应 spy 的 `Body`。

`Decode` 接收的是解码目标变量的地址，所以我们提前一行声明了一个空的 `Player` 切片。

JSON 解析可能失败，所以 `Decode` 会返回 `error`。要是解析就失败了，测试再跑下去也没意义，所以我们检查这个错误，一旦发生就用 `t.Fatalf` 终止测试。注意我们把响应体和错误一起打印了出来——让跑测试的人看到到底是哪个字符串解析不了，这一点很重要。

## 试着运行测试

```
=== RUN   TestLeague/it_returns_200_on_/league
    --- FAIL: TestLeague/it_returns_200_on_/league (0.00s)
        server_test.go:107: Unable to parse response from server '' into slice of Player, 'unexpected end of JSON input'
```

我们的端点目前不返回响应体，自然没法解析成 JSON。

## 写足够的代码让测试通过

```go
//server.go
func (p *PlayerServer) leagueHandler(w http.ResponseWriter, r *http.Request) {
	leagueTable := []Player{
		{"Chris", 20},
	}

	json.NewEncoder(w).Encode(leagueTable)

	w.WriteHeader(http.StatusOK)
}
```

测试现在通过了。

### 编码与解码

注意标准库里这组可爱的对称。

- 创建 `Encoder`（编码器）需要 `io.Writer`，`http.ResponseWriter` 实现的正是它。
- 创建 `Decoder` 需要 `io.Reader`，响应 spy 的 `Body` 字段实现的正是它。

整本书我们一直在用 `io.Writer`，这又一次证明了它在标准库里无处不在，也说明了为什么那么多库都能轻松跟它配合。

## 重构

最好把 handler 和获取 `leagueTable` 的关注点分开——我们很清楚，用不了多久就不会再硬编码这份数据了。

```go
//server.go
func (p *PlayerServer) leagueHandler(w http.ResponseWriter, r *http.Request) {
	json.NewEncoder(w).Encode(p.getLeagueTable())
	w.WriteHeader(http.StatusOK)
}

func (p *PlayerServer) getLeagueTable() []Player {
	return []Player{
		{"Chris", 20},
	}
}
```

接下来我们要扩展测试，做到能精确控制想拿回什么数据。

## 先写测试

我们可以更新测试，断言联盟积分表里包含一些预置（stub）到 store 里的玩家。

更新 `StubPlayerStore`，让它能存一个 league（联盟）——其实就是一个 `Player` 切片。我们把期望的数据存在里面。

```go
//server_test.go
type StubPlayerStore struct {
	scores   map[string]int
	winCalls []string
	league   []Player
}
```

接着更新现有的测试：往 stub 的 league 属性里放几个玩家，断言服务器返回的就是他们。

```go
//server_test.go
func TestLeague(t *testing.T) {

	t.Run("it returns the league table as JSON", func(t *testing.T) {
		wantedLeague := []Player{
			{"Cleo", 32},
			{"Chris", 20},
			{"Tiest", 14},
		}

		store := StubPlayerStore{nil, nil, wantedLeague}
		server := NewPlayerServer(&store)

		request, _ := http.NewRequest(http.MethodGet, "/league", nil)
		response := httptest.NewRecorder()

		server.ServeHTTP(response, request)

		var got []Player

		err := json.NewDecoder(response.Body).Decode(&got)

		if err != nil {
			t.Fatalf("Unable to parse response from server %q into slice of Player, '%v'", response.Body, err)
		}

		assertStatus(t, response.Code, http.StatusOK)

		if !reflect.DeepEqual(got, wantedLeague) {
			t.Errorf("got %v want %v", got, wantedLeague)
		}
	})
}
```

## 试着运行测试

```
./server_test.go:33:3: too few values in struct initializer
./server_test.go:70:3: too few values in struct initializer
```

## 写最少的代码让测试能运行，并检查失败的测试输出

`StubPlayerStore` 多了一个新字段，其他测试也得跟着更新：把它们那里的这个字段设为 nil。

再跑一次测试，应该会看到

```
=== RUN   TestLeague/it_returns_the_league_table_as_JSON
    --- FAIL: TestLeague/it_returns_the_league_table_as_JSON (0.00s)
        server_test.go:124: got [{Chris 20}] want [{Cleo 32} {Chris 20} {Tiest 14}]
```

## 写足够的代码让测试通过

我们知道数据就在 `StubPlayerStore` 里，而且已经把它抽象成了接口 `PlayerStore`。现在要更新这个接口，让任何传给我们 `PlayerStore` 的调用方都能提供联盟数据。

```go
//server.go
type PlayerStore interface {
	GetPlayerScore(name string) int
	RecordWin(name string)
	GetLeague() []Player
}
```

现在可以更新 handler 了，改为调用接口方法，而不是返回硬编码的列表。删掉 `getLeagueTable()` 方法，然后让 `leagueHandler` 改调 `GetLeague()`。

```go
//server.go
func (p *PlayerServer) leagueHandler(w http.ResponseWriter, r *http.Request) {
	json.NewEncoder(w).Encode(p.store.GetLeague())
	w.WriteHeader(http.StatusOK)
}
```

试着跑一下测试。

```
# github.com/quii/learn-go-with-tests/json-and-io/v4
./main.go:9:50: cannot use NewInMemoryPlayerStore() (type *InMemoryPlayerStore) as type PlayerStore in argument to NewPlayerServer:
    *InMemoryPlayerStore does not implement PlayerStore (missing GetLeague method)
./server_integration_test.go:11:27: cannot use store (type *InMemoryPlayerStore) as type PlayerStore in argument to NewPlayerServer:
    *InMemoryPlayerStore does not implement PlayerStore (missing GetLeague method)
./server_test.go:36:28: cannot use &store (type *StubPlayerStore) as type PlayerStore in argument to NewPlayerServer:
    *StubPlayerStore does not implement PlayerStore (missing GetLeague method)
./server_test.go:74:28: cannot use &store (type *StubPlayerStore) as type PlayerStore in argument to NewPlayerServer:
    *StubPlayerStore does not implement PlayerStore (missing GetLeague method)
./server_test.go:106:29: cannot use &store (type *StubPlayerStore) as type PlayerStore in argument to NewPlayerServer:
    *StubPlayerStore does not implement PlayerStore (missing GetLeague method)
```

编译器在抱怨：`InMemoryPlayerStore` 和 `StubPlayerStore` 还没有实现我们新加进接口的方法。

`StubPlayerStore` 很好办，把之前加的 `league` 字段返回就行。

```go
//server_test.go
func (s *StubPlayerStore) GetLeague() []Player {
	return s.league
}
```

再看一眼 `InMemoryStore` 的实现。

```go
//in_memory_player_store.go
type InMemoryPlayerStore struct {
	store map[string]int
}
```

虽然遍历 map 把 `GetLeague` "正经地"实现出来并不难，但别忘了，我们要的是*写最少的代码让测试通过*。

所以先哄得编译器开心就好，忍着 `InMemoryStore` 实现不完整带来的那股别扭劲儿。

```go
//in_memory_player_store.go
func (i *InMemoryPlayerStore) GetLeague() []Player {
	return nil
}
```

这其实是在提醒我们：*以后*我们得给这段代码补上测试，但眼下先搁置。

再跑一次测试，编译应该能过，测试也应该全绿了！

## 重构

现在的测试代码不太能表达我们的意图，而且有一堆可以重构掉的样板代码。

```go
//server_test.go
t.Run("it returns the league table as JSON", func(t *testing.T) {
	wantedLeague := []Player{
		{"Cleo", 32},
		{"Chris", 20},
		{"Tiest", 14},
	}

	store := StubPlayerStore{nil, nil, wantedLeague}
	server := NewPlayerServer(&store)

	request := newLeagueRequest()
	response := httptest.NewRecorder()

	server.ServeHTTP(response, request)

	got := getLeagueFromResponse(t, response.Body)
	assertStatus(t, response.Code, http.StatusOK)
	assertLeague(t, got, wantedLeague)
})
```

以下是新的辅助函数

```go
//server_test.go
func getLeagueFromResponse(t testing.TB, body io.Reader) (league []Player) {
	t.Helper()
	err := json.NewDecoder(body).Decode(&league)

	if err != nil {
		t.Fatalf("Unable to parse response from server %q into slice of Player, '%v'", body, err)
	}

	return
}

func assertLeague(t testing.TB, got, want []Player) {
	t.Helper()
	if !reflect.DeepEqual(got, want) {
		t.Errorf("got %v want %v", got, want)
	}
}

func newLeagueRequest() *http.Request {
	req, _ := http.NewRequest(http.MethodGet, "/league", nil)
	return req
}
```

要让服务器真正可用，还差最后一件事：确保响应里返回 `content-type` 响应头，让机器能认出我们返回的是 `JSON`。

## 先写测试

在现有测试里加上这条断言

```go
//server_test.go
if response.Result().Header.Get("content-type") != "application/json" {
	t.Errorf("response did not have content-type of application/json, got %v", response.Result().Header)
}
```

## 试着运行测试

```
=== RUN   TestLeague/it_returns_the_league_table_as_JSON
    --- FAIL: TestLeague/it_returns_the_league_table_as_JSON (0.00s)
        server_test.go:124: response did not have content-type of application/json, got map[Content-Type:[text/plain; charset=utf-8]]
```

## 写足够的代码让测试通过

更新 `leagueHandler`

```go
//server.go
func (p *PlayerServer) leagueHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("content-type", "application/json")
	json.NewEncoder(w).Encode(p.store.GetLeague())
}
```

测试应该能过了。

## 重构

给 "application/json" 建一个常量，在 `leagueHandler` 里使用

```go
//server.go
const jsonContentType = "application/json"

func (p *PlayerServer) leagueHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("content-type", jsonContentType)
	json.NewEncoder(w).Encode(p.store.GetLeague())
}
```

然后添加一个 `assertContentType` 辅助函数。

```go
//server_test.go
func assertContentType(t testing.TB, response *httptest.ResponseRecorder, want string) {
	t.Helper()
	if response.Result().Header.Get("content-type") != want {
		t.Errorf("response did not have content-type of %s, got %v", want, response.Result().Header)
	}
}
```

在测试里用上它。

```go
//server_test.go
assertContentType(t, response, jsonContentType)
```

`PlayerServer` 眼下算是收拾妥当了，接下来可以把注意力转向 `InMemoryPlayerStore`——不然拿去给产品负责人演示的话，`/league` 是跑不起来的。

最快建立信心的办法是往集成测试里加东西：请求新端点，检查从 `/league` 拿回的响应是否正确。

## 先写测试

我们可以用 `t.Run` 把这个测试拆分一下，还能复用服务器测试里的那些辅助函数——这再次说明了重构测试的重要性。

```go
//server_integration_test.go
func TestRecordingWinsAndRetrievingThem(t *testing.T) {
	store := NewInMemoryPlayerStore()
	server := NewPlayerServer(store)
	player := "Pepper"

	server.ServeHTTP(httptest.NewRecorder(), newPostWinRequest(player))
	server.ServeHTTP(httptest.NewRecorder(), newPostWinRequest(player))
	server.ServeHTTP(httptest.NewRecorder(), newPostWinRequest(player))

	t.Run("get score", func(t *testing.T) {
		response := httptest.NewRecorder()
		server.ServeHTTP(response, newGetScoreRequest(player))
		assertStatus(t, response.Code, http.StatusOK)

		assertResponseBody(t, response.Body.String(), "3")
	})

	t.Run("get league", func(t *testing.T) {
		response := httptest.NewRecorder()
		server.ServeHTTP(response, newLeagueRequest())
		assertStatus(t, response.Code, http.StatusOK)

		got := getLeagueFromResponse(t, response.Body)
		want := []Player{
			{"Pepper", 3},
		}
		assertLeague(t, got, want)
	})
}
```

## 试着运行测试

```
=== RUN   TestRecordingWinsAndRetrievingThem/get_league
    --- FAIL: TestRecordingWinsAndRetrievingThem/get_league (0.00s)
        server_integration_test.go:35: got [] want [{Pepper 3}]
```

## 写足够的代码让测试通过

现在调用 `GetLeague()` 时 `InMemoryPlayerStore` 返回的是 `nil`，得把它修好。

```go
//in_memory_player_store.go
func (i *InMemoryPlayerStore) GetLeague() []Player {
	var league []Player
	for name, wins := range i.store {
		league = append(league, Player{name, wins})
	}
	return league
}
```

我们要做的只是遍历 map，把每一个键值对转换成一个 `Player`。

测试现在应该能过了。

## 总结

我们继续用 TDD 安全地迭代程序：借助路由器，以可维护的方式支持了新端点，程序现在能为调用方返回 JSON 了。下一章我们将讨论数据持久化和联盟排序。

本章涵盖的内容：

- **路由**。标准库提供了一个好用的路由类型。它完全拥抱 `http.Handler` 接口：路由挂到 `Handler` 上，而路由器本身也是一个 `Handler`。不过它缺少一些你可能期待的功能，比如路径变量（例如 `/users/{id}`）。这些信息自己解析也不难，但如果觉得是个负担，可以考虑看看别的路由库。流行的路由库大多恪守标准库的设计哲学，同样实现 `http.Handler`。
- **类型嵌入**。我们对这个技术只是浅尝辄止，你可以[去 Effective Go 进一步了解](https://golang.org/doc/effective_go.html#embedding)。如果只能带走一件事，那就是：嵌入极其有用，但*要时刻想着你的公开 API，只暴露该暴露的*。
- **JSON 的反序列化与序列化**。有了标准库，数据的序列化和反序列化变得非常简单。它还开放了配置，必要时你可以自定义这些数据转换的行为。
