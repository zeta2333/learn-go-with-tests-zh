# IO 与排序

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/io)**

[上一章](https://github.com/quii/learn-go-with-tests/blob/main/json.md)（英文原版）里，我们给应用加了新的 `/league` 端点，继续迭代。一路走来，我们学习了如何处理 JSON、如何嵌入类型（embedding）以及如何实现路由。

我们的产品负责人相当恼火：服务器一重启，大家的得分就全丢了。原因在于我们的 store 是存在内存里的。她还有点不高兴——我们居然没领会到，`/league` 端点返回的玩家应该按胜场数排好序！

## 目前的代码

```go
// server.go
package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
)

// PlayerStore 存储玩家的得分信息
type PlayerStore interface {
	GetPlayerScore(name string) int
	RecordWin(name string)
	GetLeague() []Player
}

// Player 记录玩家的名字和胜场数
type Player struct {
	Name string
	Wins int
}

// PlayerServer 是玩家信息的 HTTP 接口
type PlayerServer struct {
	store PlayerStore
	http.Handler
}

const jsonContentType = "application/json"

// NewPlayerServer 创建一个配置好路由的 PlayerServer
func NewPlayerServer(store PlayerStore) *PlayerServer {
	p := new(PlayerServer)

	p.store = store

	router := http.NewServeMux()
	router.Handle("/league", http.HandlerFunc(p.leagueHandler))
	router.Handle("/players/", http.HandlerFunc(p.playersHandler))

	p.Handler = router

	return p
}

func (p *PlayerServer) leagueHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("content-type", jsonContentType)
	json.NewEncoder(w).Encode(p.store.GetLeague())
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

func (i *InMemoryPlayerStore) GetLeague() []Player {
	var league []Player
	for name, wins := range i.store {
		league = append(league, Player{name, wins})
	}
	return league
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
	server := NewPlayerServer(NewInMemoryPlayerStore())
	log.Fatal(http.ListenAndServe(":5000", server))
}
```

各测试的完整代码可以在本章开头的链接里找到。

## 存储数据

能胜任这件事的数据库一抓一大把，但我们打算走一条极简路线：把应用的数据以 JSON 形式存进一个文件。

这样数据非常好搬运，实现起来也相对简单。

它的扩展性说不上好，但既然只是个原型，眼下完全够用。万一情况有变、它不再合适，凭借我们已有的 `PlayerStore` 抽象，换掉它也很容易。

我们暂时保留 `InMemoryPlayerStore`，这样在开发新 store 的整个过程中，集成测试（integration test）都能保持通过。等我们有信心新实现足以让集成测试通过，再把它换上，然后删掉 `InMemoryPlayerStore`。

## 先写测试

到这一步，你应该已经熟悉了标准库里负责读取数据（`io.Reader`）和写入数据（`io.Writer`）的几个接口，也见识过如何借助标准库、不动真格的文件来测试这类函数。

要把这件事做完整，我们就得实现 `PlayerStore`，所以接下来会给 store 写测试，调用那些待实现的方法。先从 `GetLeague` 开始。

```go
//file_system_store_test.go
func TestFileSystemStore(t *testing.T) {

	t.Run("league from a reader", func(t *testing.T) {
		database := strings.NewReader(`[
			{"Name": "Cleo", "Wins": 10},
			{"Name": "Chris", "Wins": 33}]`)

		store := FileSystemPlayerStore{database}

		got := store.GetLeague()

		want := []Player{
			{"Cleo", 10},
			{"Chris", 33},
		}

		assertLeague(t, got, want)
	})
}
```

这里用的 `strings.NewReader` 会返回一个 `Reader`，而 `FileSystemPlayerStore` 要读数据靠的正是它。等到 `main` 里，我们会打开一个文件，文件同样是一个 `Reader`。

## 试着运行测试

```
# github.com/quii/learn-go-with-tests/io/v1
./file_system_store_test.go:15:12: undefined: FileSystemPlayerStore
```

## 写最少的代码让测试能运行，并检查失败的测试输出

在一个新文件里定义 `FileSystemPlayerStore`

```go
//file_system_store.go
type FileSystemPlayerStore struct{}
```

再试一次

```
# github.com/quii/learn-go-with-tests/io/v1
./file_system_store_test.go:15:28: too many values in struct initializer
./file_system_store_test.go:17:15: store.GetLeague undefined (type FileSystemPlayerStore has no field or method GetLeague)
```

编译器在抱怨：我们传进去了 `Reader`，结构体却不接收；`GetLeague` 也还没定义。

```go
//file_system_store.go
type FileSystemPlayerStore struct {
	database io.Reader
}

func (f *FileSystemPlayerStore) GetLeague() []Player {
	return nil
}
```

再来一次……

```
=== RUN   TestFileSystemStore//league_from_a_reader
    --- FAIL: TestFileSystemStore//league_from_a_reader (0.00s)
        file_system_store_test.go:24: got [] want [{Cleo 10} {Chris 33}]
```

## 写足够的代码让测试通过

从 `Reader` 里读 JSON 这活儿我们之前干过

```go
//file_system_store.go
func (f *FileSystemPlayerStore) GetLeague() []Player {
	var league []Player
	json.NewDecoder(f.database).Decode(&league)
	return league
}
```

测试应该通过了。

## 重构

这事儿我们*真的*做过！服务器那边的测试代码就得从响应里解码 JSON。

我们来 DRY（Don't Repeat Yourself，别重复自己）一下，把它抽成一个函数。

新建一个 `league.go` 文件，放入下面的代码。

```go
//league.go
func NewLeague(rdr io.Reader) ([]Player, error) {
	var league []Player
	err := json.NewDecoder(rdr).Decode(&league)
	if err != nil {
		err = fmt.Errorf("problem parsing league, %v", err)
	}

	return league, err
}
```

在我们的实现里，以及 `server_test.go` 中的测试辅助函数 `getLeagueFromResponse` 里，都改为调用它。

```go
//file_system_store.go
func (f *FileSystemPlayerStore) GetLeague() []Player {
	league, _ := NewLeague(f.database)
	return league
}
```

解析出错该怎么办，我们还没想好策略，但先继续往下走。

### Seek 带来的问题

我们的实现里藏着一个缺陷。先来复习一下 `io.Reader` 的定义。

```go
type Reader interface {
	Read(p []byte) (n int, err error)
}
```

就拿文件来说，你可以想象它一个字节一个字节地往后读，一直读到末尾。那如果再 `Read` 一次，会发生什么？

在现有测试的末尾加上下面这段。

```go
//file_system_store_test.go

// 再读一次
got = store.GetLeague()
assertLeague(t, got, want)
```

我们希望它能通过，但一跑测试就发现：过不了。

问题在于 `Reader` 已经到了末尾，再无可读之物。我们需要一种办法，让它回到开头。

标准库里还有一个接口能帮上忙：[ReadSeeker](https://golang.org/pkg/io/#ReadSeeker)。

```go
type ReadSeeker interface {
	Reader
	Seeker
}
```

还记得嵌入吗？这是一个由 `Reader` 和 [`Seeker`](https://golang.org/pkg/io/#Seeker) 组合而成的接口。

```go
type Seeker interface {
	Seek(offset int64, whence int) (int64, error)
}
```

听起来正合适，那我们把 `FileSystemPlayerStore` 改成接收这个接口如何？

```go
//file_system_store.go
type FileSystemPlayerStore struct {
	database io.ReadSeeker
}

func (f *FileSystemPlayerStore) GetLeague() []Player {
	f.database.Seek(0, io.SeekStart)
	league, _ := NewLeague(f.database)
	return league
}
```

跑一下测试，过了！运气不错，我们测试里用的 `strings.NewReader` 同样实现了 `ReadSeeker`，其他代码一行都不用改。

接下来实现 `GetPlayerScore`。

## 先写测试

```go
//file_system_store_test.go
t.Run("get player score", func(t *testing.T) {
	database := strings.NewReader(`[
		{"Name": "Cleo", "Wins": 10},
		{"Name": "Chris", "Wins": 33}]`)

	store := FileSystemPlayerStore{database}

	got := store.GetPlayerScore("Chris")

	want := 33

	if got != want {
		t.Errorf("got %d want %d", got, want)
	}
})
```

## 试着运行测试

```
./file_system_store_test.go:38:15: store.GetPlayerScore undefined (type FileSystemPlayerStore has no field or method GetPlayerScore)
```

## 写最少的代码让测试能运行，并检查失败的测试输出

得给新类型加上这个方法，测试才能编译。

```go
//file_system_store.go
func (f *FileSystemPlayerStore) GetPlayerScore(name string) int {
	return 0
}
```

现在能编译了，测试失败

```
=== RUN   TestFileSystemStore/get_player_score
    --- FAIL: TestFileSystemStore//get_player_score (0.00s)
        file_system_store_test.go:43: got 0 want 33
```

## 写足够的代码让测试通过

遍历联赛找出这名玩家，返回他的得分即可

```go
//file_system_store.go
func (f *FileSystemPlayerStore) GetPlayerScore(name string) int {

	var wins int

	for _, player := range f.GetLeague() {
		if player.Name == name {
			wins = player.Wins
			break
		}
	}

	return wins
}
```

## 重构

测试辅助函数的重构你已经见过十几次了，这次就留给你自己动手

```go
//file_system_store_test.go
t.Run("get player score", func(t *testing.T) {
	database := strings.NewReader(`[
		{"Name": "Cleo", "Wins": 10},
		{"Name": "Chris", "Wins": 33}]`)

	store := FileSystemPlayerStore{database}

	got := store.GetPlayerScore("Chris")
	want := 33
	assertScoreEquals(t, got, want)
})
```

最后，该用 `RecordWin` 记录得分了。

## 先写测试

对写入来说，我们这套方案相当短视。文件里 JSON 的某一"行"，我们没法（轻易地）单独更新；每次写入都得把数据库的*整个*新样子重新存一遍。

怎么写呢？按惯例该用 `Writer`，可我们手里已经有 `ReadSeeker` 了。搞两个依赖也不是不行，但标准库早就为我们备好了 `ReadWriteSeeker`，对文件要做的事情它全都能干。

更新一下我们的类型

```go
//file_system_store.go
type FileSystemPlayerStore struct {
	database io.ReadWriteSeeker
}
```

看看能不能编译

```
./file_system_store_test.go:15:34: cannot use database (type *strings.Reader) as type io.ReadWriteSeeker in field value:
    *strings.Reader does not implement io.ReadWriteSeeker (missing Write method)
./file_system_store_test.go:36:34: cannot use database (type *strings.Reader) as type io.ReadWriteSeeker in field value:
    *strings.Reader does not implement io.ReadWriteSeeker (missing Write method)
```

`strings.Reader` 没实现 `ReadWriteSeeker`，这不算意外。那怎么办？

我们有两条路

- 为每个测试创建一个临时文件。`*os.File` 实现了 `ReadWriteSeeker`。好处是这样更接近集成测试，我们真正在读写文件系统，信心会非常足。坏处是我们更偏爱单元测试，它们更快、通常也更简单；而且围绕临时文件还得做更多工作：创建它，还得确保测试结束后把它删掉。
- 用第三方库。[Mattetti](https://github.com/mattetti) 写过一个 [filebuffer](https://github.com/mattetti/filebuffer) 库，实现了我们需要的接口，而且完全不碰文件系统。

这两个答案都说不上错，但选第三方库的话，我就得解释一遍依赖管理了！所以我们还是用文件。

在添加新测试之前，得先让其他测试能编译：把 `strings.Reader` 换成 `os.File`。

我们来写几个辅助函数：一个负责创建临时文件并写入初始数据，顺便把得分相关的测试抽象一下

```go
//file_system_store_test.go
func createTempFile(t testing.TB, initialData string) (io.ReadWriteSeeker, func()) {
	t.Helper()

	tmpfile, err := os.CreateTemp("", "db")

	if err != nil {
		t.Fatalf("could not create temp file %v", err)
	}

	tmpfile.Write([]byte(initialData))

	removeFile := func() {
		tmpfile.Close()
		os.Remove(tmpfile.Name())
	}

	return tmpfile, removeFile
}

func assertScoreEquals(t testing.TB, got, want int) {
	t.Helper()
	if got != want {
		t.Errorf("got %d want %d", got, want)
	}
}
```

[CreateTemp](https://pkg.go.dev/os#CreateTemp) 会创建一个供我们使用的临时文件。传入的 `"db"` 是个前缀，会加在它生成的随机文件名前面，免得碰巧跟其他文件撞名。

你会注意到，我们返回的不只是 `ReadWriteSeeker`（那个文件），还有一个函数。我们得保证测试结束后文件被删掉。可我们又不想把这些文件操作的细节泄漏到测试里——那样容易出错，读者看着也索然无味。返回一个 `removeFile` 函数，细节就都收在辅助函数里，调用方只需一句 `defer removeFile()`。

```go
//file_system_store_test.go
func TestFileSystemStore(t *testing.T) {

	t.Run("league from a reader", func(t *testing.T) {
		database, removeFile := createTempFile(t, `[
			{"Name": "Cleo", "Wins": 10},
			{"Name": "Chris", "Wins": 33}]`)
		defer removeFile()

		store := FileSystemPlayerStore{database}

		got := store.GetLeague()

		want := []Player{
			{"Cleo", 10},
			{"Chris", 33},
		}

		assertLeague(t, got, want)

		// 再读一次
		got = store.GetLeague()
		assertLeague(t, got, want)
	})

	t.Run("get player score", func(t *testing.T) {
		database, removeFile := createTempFile(t, `[
			{"Name": "Cleo", "Wins": 10},
			{"Name": "Chris", "Wins": 33}]`)
		defer removeFile()

		store := FileSystemPlayerStore{database}

		got := store.GetPlayerScore("Chris")
		want := 33
		assertScoreEquals(t, got, want)
	})
}
```

跑一下测试，应该全过了！改动是不少，但到此为止，接口的定义感觉已经齐活，以后加新测试会非常轻松。

先来做第一版：给已有玩家记一次胜场

```go
//file_system_store_test.go
t.Run("store wins for existing players", func(t *testing.T) {
	database, removeFile := createTempFile(t, `[
		{"Name": "Cleo", "Wins": 10},
		{"Name": "Chris", "Wins": 33}]`)
	defer removeFile()

	store := FileSystemPlayerStore{database}

	store.RecordWin("Chris")

	got := store.GetPlayerScore("Chris")
	want := 34
	assertScoreEquals(t, got, want)
})
```

## 试着运行测试

`./file_system_store_test.go:67:8: store.RecordWin undefined (type FileSystemPlayerStore has no field or method RecordWin)`

## 写最少的代码让测试能运行，并检查失败的测试输出

加上新方法

```go
//file_system_store.go
func (f *FileSystemPlayerStore) RecordWin(name string) {

}
```

```
=== RUN   TestFileSystemStore/store_wins_for_existing_players
    --- FAIL: TestFileSystemStore/store_wins_for_existing_players (0.00s)
        file_system_store_test.go:71: got 33 want 34
```

实现是空的，所以返回的还是旧分数。

## 写足够的代码让测试通过

```go
//file_system_store.go
func (f *FileSystemPlayerStore) RecordWin(name string) {
	league := f.GetLeague()

	for i, player := range league {
		if player.Name == name {
			league[i].Wins++
		}
	}

	f.database.Seek(0, io.SeekStart)
	json.NewEncoder(f.database).Encode(league)
}
```

你可能想问：为什么写的是 `league[i].Wins++`，而不是 `player.Wins++`？

对切片做 `range` 时，你拿到的是循环当前的下标（在我们这里是 `i`）以及该位置元素的*副本*。改副本的 `Wins`，对我们正在遍历的 `league` 切片毫无影响。所以必须通过 `league[i]` 拿到真实值的引用，再去改它。

再跑测试，现在应该全过了。

## 重构

在 `GetPlayerScore` 和 `RecordWin` 里，我们都在遍历 `[]Player` 按名字找玩家。

这段重复代码可以就地在 `FileSystemStore` 内部重构，但在我看来，它更像一段大有可为的代码，值得提升为一个新类型。到目前为止，"League" 一直以 `[]Player` 的面目出现，我们完全可以新建一个叫 `League` 的类型。其他开发者会更容易理解，而且往后还能往这个类型上挂各种好用的方法。

在 `league.go` 里加上

```go
//league.go
type League []Player

func (l League) Find(name string) *Player {
	for i, p := range l {
		if p.Name == name {
			return &l[i]
		}
	}
	return nil
}
```

这样一来，谁手里有一个 `League`，都能轻松找到指定玩家。

把 `PlayerStore` 接口改成返回 `League` 而不是 `[]Player`。再跑一次测试，会碰上编译问题——毕竟接口变了——但修起来非常简单：把返回类型从 `[]Player` 改成 `League` 即可。

于是 `file_system_store` 里的方法可以简化成这样。

```go
//file_system_store.go
func (f *FileSystemPlayerStore) GetPlayerScore(name string) int {

	player := f.GetLeague().Find(name)

	if player != nil {
		return player.Wins
	}

	return 0
}

func (f *FileSystemPlayerStore) RecordWin(name string) {
	league := f.GetLeague()
	player := league.Find(name)

	if player != nil {
		player.Wins++
	}

	f.database.Seek(0, io.SeekStart)
	json.NewEncoder(f.database).Encode(league)
}
```

看起来好多了。而且可以想见，围绕 `League` 还有不少实用功能等着被重构出来。

接下来要处理的是：给新玩家记胜场。

## 先写测试

```go
//file_system_store_test.go
t.Run("store wins for new players", func(t *testing.T) {
	database, removeFile := createTempFile(t, `[
		{"Name": "Cleo", "Wins": 10},
		{"Name": "Chris", "Wins": 33}]`)
	defer removeFile()

	store := FileSystemPlayerStore{database}

	store.RecordWin("Pepper")

	got := store.GetPlayerScore("Pepper")
	want := 1
	assertScoreEquals(t, got, want)
})
```

## 试着运行测试

```
=== RUN   TestFileSystemStore/store_wins_for_new_players#01
    --- FAIL: TestFileSystemStore/store_wins_for_new_players#01 (0.00s)
        file_system_store_test.go:86: got 0 want 1
```

## 写足够的代码让测试通过

只需处理一种情况：`Find` 找不到玩家、返回 `nil`。

```go
//file_system_store.go
func (f *FileSystemPlayerStore) RecordWin(name string) {
	league := f.GetLeague()
	player := league.Find(name)

	if player != nil {
		player.Wins++
	} else {
		league = append(league, Player{name, 1})
	}

	f.database.Seek(0, io.SeekStart)
	json.NewEncoder(f.database).Encode(league)
}
```

正常路径看起来没问题了，现在可以在集成测试里换上新的 `Store` 试试。这会让我们对软件更有信心，然后就能删掉多余的 `InMemoryPlayerStore`。

在 `TestRecordingWinsAndRetrievingThem` 里换掉旧的 store。

```go
//server_integration_test.go
database, removeFile := createTempFile(t, "")
defer removeFile()
store := &FileSystemPlayerStore{database}
```

跑一下测试，应该通过。现在可以删掉 `InMemoryPlayerStore` 了。`main.go` 随之出现编译问题，这正好逼着我们在"真实"代码里用上新 store。

```go
// main.go
package main

import (
	"log"
	"net/http"
	"os"
)

const dbFileName = "game.db.json"

func main() {
	db, err := os.OpenFile(dbFileName, os.O_RDWR|os.O_CREATE, 0666)

	if err != nil {
		log.Fatalf("problem opening %s %v", dbFileName, err)
	}

	store := &FileSystemPlayerStore{db}
	server := NewPlayerServer(store)

	if err := http.ListenAndServe(":5000", server); err != nil {
		log.Fatalf("could not listen on port 5000 %v", err)
	}
}
```

- 我们为数据库创建一个文件。
- `os.OpenFile` 的第二个参数定义打开文件的权限：这里的 `O_RDWR` 表示我们既要读也要写，`os.O_CREATE` 则表示文件不存在就创建。
- 第三个参数设置文件的权限：这里所有用户都可以读写这个文件。（更详细的解释见 [superuser.com](https://superuser.com/questions/295591/what-is-the-meaning-of-chmod-666)）。

现在再运行程序，数据就能在重启之间保存在文件里了，万岁！

## 更多重构与性能考量

现在每次有人调用 `GetLeague()` 或 `GetPlayerScore()`，我们都要把整个文件读进来、解析成 JSON。这本来没必要：联赛的状态完全由 `FileSystemStore` 负责，程序启动时读一次文件、数据变化时更新一次文件，就够了。

我们可以写一个构造函数替我们完成这些初始化，并把联赛作为字段存进 `FileSystemStore`，读取时直接用它。

```go
//file_system_store.go
type FileSystemPlayerStore struct {
	database io.ReadWriteSeeker
	league   League
}

func NewFileSystemPlayerStore(database io.ReadWriteSeeker) *FileSystemPlayerStore {
	database.Seek(0, io.SeekStart)
	league, _ := NewLeague(database)
	return &FileSystemPlayerStore{
		database: database,
		league:   league,
	}
}
```

这样磁盘只需要读一次。之前那些"从磁盘取联赛"的调用统统可以换成直接用 `f.league`。

```go
//file_system_store.go
func (f *FileSystemPlayerStore) GetLeague() League {
	return f.league
}

func (f *FileSystemPlayerStore) GetPlayerScore(name string) int {

	player := f.league.Find(name)

	if player != nil {
		return player.Wins
	}

	return 0
}

func (f *FileSystemPlayerStore) RecordWin(name string) {
	player := f.league.Find(name)

	if player != nil {
		player.Wins++
	} else {
		f.league = append(f.league, Player{name, 1})
	}

	f.database.Seek(0, io.SeekStart)
	json.NewEncoder(f.database).Encode(f.league)
}
```

试着跑测试，它会抱怨 `FileSystemPlayerStore` 的初始化方式，改成调用新构造函数即可。

### 又一个问题

我们处理文件的方式还有一处天真，*有朝一日*可能酿成非常恶心的 bug。

调用 `RecordWin` 时，我们先 `Seek` 回文件开头，再写入新数据——可要是新数据比原来的短呢？

就目前而言这不可能发生：我们从不编辑或删除得分，数据只会越变越大。但把代码就这么放着是不负责任的——谁能保证以后不会冒出删除的场景呢？

可这该怎么测？我们需要先重构代码，把"写入*什么样的数据*"与"写入"这个动作分开，然后单独测试前者，验证它符合预期。

我们新建一个类型，把"一写就从头写"的语义封装起来。我打算叫它 `Tape`。新建一个文件，写入以下内容：

```go
// tape.go
package main

import "io"

type tape struct {
	file io.ReadWriteSeeker
}

func (t *tape) Write(p []byte) (n int, err error) {
	t.file.Seek(0, io.SeekStart)
	return t.file.Write(p)
}
```

注意现在只实现了 `Write`，`Seek` 那部分被封装在里面了。这意味着 `FileSystemStore` 只需持有一个 `Writer` 的引用即可。

```go
//file_system_store.go
type FileSystemPlayerStore struct {
	database io.Writer
	league   League
}
```

更新构造函数，用上 `Tape`

```go
//file_system_store.go
func NewFileSystemPlayerStore(database io.ReadWriteSeeker) *FileSystemPlayerStore {
	database.Seek(0, io.SeekStart)
	league, _ := NewLeague(database)

	return &FileSystemPlayerStore{
		database: &tape{database},
		league:   league,
	}
}
```

终于，我们迎来了期盼已久的丰厚回报：从 `RecordWin` 里删掉 `Seek` 调用。是的，感觉没多大点儿事，但至少从此以后，任何其他类型的写入都可以指望 `Write` 按我们需要的方式工作。何况这还让我们能够单独测试那段潜在的问题代码，进而修复它。

来写这样一个测试：用比原内容更短的新内容，覆盖文件的整个内容。

## 先写测试

我们的测试会创建一个有内容的文件，用 `tape` 往里写点东西，然后把文件整个读回来，看看里面到底是什么。在 `tape_test.go` 中：

```go
//tape_test.go
func TestTape_Write(t *testing.T) {
	file, clean := createTempFile(t, "12345")
	defer clean()

	tape := &tape{file}

	tape.Write([]byte("abc"))

	file.Seek(0, io.SeekStart)
	newFileContents, _ := io.ReadAll(file)

	got := string(newFileContents)
	want := "abc"

	if got != want {
		t.Errorf("got %q want %q", got, want)
	}
}
```

## 试着运行测试

```
=== RUN   TestTape_Write
--- FAIL: TestTape_Write (0.00s)
    tape_test.go:23: got 'abc45' want 'abc'
```

跟我们预想的一样！想要的数据写进去了，但原数据的尾巴还留在那儿。

## 写足够的代码让测试通过

`os.File` 有一个截断（truncate）函数，能把文件有效地清空。调用它应该就能得到我们想要的结果。

把 `tape` 改成下面这样：

```go
//tape.go
type tape struct {
	file *os.File
}

func (t *tape) Write(p []byte) (n int, err error) {
	t.file.Truncate(0)
	t.file.Seek(0, io.SeekStart)
	return t.file.Write(p)
}
```

编译器会在若干地方报错——那些地方原本期望 `io.ReadWriteSeeker`，而我们现在传入的是 `*os.File`。到这个阶段，这些问题你应该能自己搞定；实在卡住了就翻翻源代码。

重构完成后，`TestTape_Write` 测试就应该能通过了！

### 另一个小重构

`RecordWin` 里有这么一行：`json.NewEncoder(f.database).Encode(f.league)`。

没必要每次写入都新建一个 encoder，完全可以在构造函数里初始化一个，之后一直用它。

在类型里存一个 `Encoder` 引用，并在构造函数里初始化它：

```go
//file_system_store.go
type FileSystemPlayerStore struct {
	database *json.Encoder
	league   League
}

func NewFileSystemPlayerStore(file *os.File) *FileSystemPlayerStore {
	file.Seek(0, io.SeekStart)
	league, _ := NewLeague(file)

	return &FileSystemPlayerStore{
		database: json.NewEncoder(&tape{file}),
		league:   league,
	}
}
```

`tape.Write` *每一次*被调用都会先寻位到文件开头，所以值得停下来确认一下：这个组合真的安全吗？假如 `Encode` 在一次调用中调用了不止一次 `Write`，那么后续每次写入都会先跳回文件开头、覆盖上一次的写入，把输出搅得一团糟。不过它不会——`Encoder.Encode` 总是先把整个值序列化进内存，再通过*一次* `Write` 调用交给底层的 `Writer`，所以 `tape` 每次 `Encode` 只会寻位一次。这恰好就是我们想要的"每次都从头覆盖"的行为。

在 `RecordWin` 里用上它。

```go
func (f *FileSystemPlayerStore) RecordWin(name string) {
	player := f.league.Find(name)

	if player != nil {
		player.Wins++
	} else {
		f.league = append(f.league, Player{name, 1})
	}

	f.database.Encode(f.league)
}
```

## 我们这不是刚坏了规矩吗？测试私有类型？不用接口？

### 关于测试私有类型

的确，*一般来说*最好不要测试私有内容，因为测试有时会因此跟实现耦合得过紧，妨碍日后的重构。

然而，别忘了测试的存在是为了给我们*信心*。

要是给实现加上任何编辑或删除功能，我们心里并没有底。我们不能让代码就这样裸奔，尤其当这个项目不止一个人在维护，而别人未必清楚我们最初方案的缺陷。

再说了，这只是一个测试而已！哪天我们改变主意、换了实现方式，把它删掉也不是什么灾难；但至少，我们为未来的维护者把这条需求记录在案了。

### 关于接口

我们一开始用的是 `io.Reader`，因为那是单元测试新 `PlayerStore` 最省事的路子。随着代码演进，我们换成了 `io.ReadWriter`，接着又是 `io.ReadWriteSeeker`。随后我们发现，除了 `*os.File`，标准库里根本没有其他类型实现它。我们本可以自己写一个实现，或者找个开源的，但对测试来说，直接用临时文件显得更务实。

最后，我们还需要 `Truncate`，而它同样长在 `*os.File` 上。自己定义一个接口来概括这些需求，本来也是一个选项。

```go
type ReadWriteSeekTruncate interface {
	io.ReadWriteSeeker
	Truncate(size int64) error
}
```

可它真能带来什么？记住我们*没有做 mock*，而且指望一个**文件系统** store 接收 `*os.File` 之外的其他类型并不现实，所以接口带来的多态（polymorphism）我们并不需要。

大胆地反复更换类型、像本章这样放手试验吧。静态类型语言的一大妙处就是：每一次改动，编译器都会扶着你。

## 错误处理

在着手排序之前，我们应当确认对现有代码满意，并清掉可能欠下的技术债。尽快让软件跑起来（别让自己停在红灯状态）是条重要原则，但这不等于可以无视错误场景！

回看 `file_system_store.go`，我们的构造函数里有这么一句：`league, _ := NewLeague(file)`。

如果没法从我们给的 `*os.File` 里解析出联赛，`NewLeague` 会返回一个错误。

当时无视它是务实的：手头已经有失败的测试了，若再同时处理这个，就是一心二用。

我们让构造函数也能返回错误。

```go
//file_system_store.go
func NewFileSystemPlayerStore(file *os.File) (*FileSystemPlayerStore, error) {
	file.Seek(0, io.SeekStart)
	league, err := NewLeague(file)

	if err != nil {
		return nil, fmt.Errorf("problem loading player store from file %s, %v", file.Name(), err)
	}

	return &FileSystemPlayerStore{
		database: json.NewEncoder(&tape{file}),
		league:   league,
	}, nil
}
```

记住，给出有用的错误信息非常重要（跟你的测试一个道理）。网上有人开玩笑说，大多数 Go 代码都长这样：

```go
if err != nil {
	return err
}
```

**这绝对不是惯用写法。**在错误信息里附上上下文（也就是你当时在做什么才触发了这个错误），会让软件的运维省心得多。

试着编译，会得到一些错误。

```
./main.go:18:35: multiple-value NewFileSystemPlayerStore() in single-value context
./file_system_store_test.go:35:36: multiple-value NewFileSystemPlayerStore() in single-value context
./file_system_store_test.go:57:36: multiple-value NewFileSystemPlayerStore() in single-value context
./file_system_store_test.go:70:36: multiple-value NewFileSystemPlayerStore() in single-value context
./file_system_store_test.go:85:36: multiple-value NewFileSystemPlayerStore() in single-value context
./server_integration_test.go:12:35: multiple-value NewFileSystemPlayerStore() in single-value context
```

在 `main` 里，我们想打印错误然后退出程序。

```go
//main.go
store, err := NewFileSystemPlayerStore(db)

if err != nil {
	log.Fatalf("problem creating file system player store, %v ", err)
}
```

在测试里，我们应当断言没有发生错误。可以写一个辅助函数来干这个。

```go
//file_system_store_test.go
func assertNoError(t testing.TB, err error) {
	t.Helper()
	if err != nil {
		t.Fatalf("didn't expect an error but got one, %v", err)
	}
}
```

用这个辅助函数把其他编译问题一一解决。最后，你会看到一个失败的测试：

```
=== RUN   TestRecordingWinsAndRetrievingThem
--- FAIL: TestRecordingWinsAndRetrievingThem (0.00s)
    server_integration_test.go:14: didn't expect an error but got one, problem loading player store from file /var/folders/nj/r_ccbj5d7flds0sf63yy4vb80000gn/T/db841037437, problem parsing league, EOF
```

联赛解析不了，因为文件是空的。之前没见到错误，不过是因为我们一直对它们视而不见。

我们来修一下那个大的集成测试，往里放一些合法的 JSON：

```go
//server_integration_test.go
func TestRecordingWinsAndRetrievingThem(t *testing.T) {
	database, removeFile := createTempFile(t, `[]`)
	// 等等……
}
```

现在测试全部通过了，接下来要处理文件为空的场景。

## 先写测试

```go
//file_system_store_test.go
t.Run("works with an empty file", func(t *testing.T) {
	database, removeFile := createTempFile(t, "")
	defer removeFile()

	_, err := NewFileSystemPlayerStore(database)

	assertNoError(t, err)
})
```

## 试着运行测试

```
=== RUN   TestFileSystemStore/works_with_an_empty_file
    --- FAIL: TestFileSystemStore/works_with_an_empty_file (0.00s)
        file_system_store_test.go:108: didn't expect an error but got one, problem loading player store from file /var/folders/nj/r_ccbj5d7flds0sf63yy4vb80000gn/T/db019548018, problem parsing league, EOF
```

## 写足够的代码让测试通过

把构造函数改成下面这样

```go
//file_system_store.go
func NewFileSystemPlayerStore(file *os.File) (*FileSystemPlayerStore, error) {

	file.Seek(0, io.SeekStart)

	info, err := file.Stat()

	if err != nil {
		return nil, fmt.Errorf("problem getting file info from file %s, %v", file.Name(), err)
	}

	if info.Size() == 0 {
		file.Write([]byte("[]"))
		file.Seek(0, io.SeekStart)
	}

	league, err := NewLeague(file)

	if err != nil {
		return nil, fmt.Errorf("problem loading player store from file %s, %v", file.Name(), err)
	}

	return &FileSystemPlayerStore{
		database: json.NewEncoder(&tape{file}),
		league:   league,
	}, nil
}
```

`file.Stat` 返回文件的统计信息，我们借此检查文件大小。如果是空的，就 `Write` 一个空的 JSON 数组，再 `Seek` 回开头，好让后续代码接着用。

## 重构

我们的构造函数现在有点乱，把初始化代码抽成一个函数吧：

```go
//file_system_store.go
func initialisePlayerDBFile(file *os.File) error {
	file.Seek(0, io.SeekStart)

	info, err := file.Stat()

	if err != nil {
		return fmt.Errorf("problem getting file info from file %s, %v", file.Name(), err)
	}

	if info.Size() == 0 {
		file.Write([]byte("[]"))
		file.Seek(0, io.SeekStart)
	}

	return nil
}
```

```go
//file_system_store.go
func NewFileSystemPlayerStore(file *os.File) (*FileSystemPlayerStore, error) {

	err := initialisePlayerDBFile(file)

	if err != nil {
		return nil, fmt.Errorf("problem initialising player db file, %v", err)
	}

	league, err := NewLeague(file)

	if err != nil {
		return nil, fmt.Errorf("problem loading player store from file %s, %v", file.Name(), err)
	}

	return &FileSystemPlayerStore{
		database: json.NewEncoder(&tape{file}),
		league:   league,
	}, nil
}
```

## 排序

产品负责人希望 `/league` 返回的玩家按得分从高到低排序。

这里的主要决策是：这件事该由软件里的哪一层来做。如果我们用的是"真正的"数据库，就会用 `ORDER BY` 之类的手段让排序快得飞起。基于同样的道理，让 `PlayerStore` 的各个实现来负责排序似乎更合适。

## 先写测试

我们可以把 `TestFileSystemStore` 里第一个测试的断言更新一下：

```go
//file_system_store_test.go
t.Run("league sorted", func(t *testing.T) {
	database, removeFile := createTempFile(t, `[
		{"Name": "Cleo", "Wins": 10},
		{"Name": "Chris", "Wins": 33}]`)
	defer removeFile()

	store, err := NewFileSystemPlayerStore(database)

	assertNoError(t, err)

	got := store.GetLeague()

	want := League{
		{"Chris", 33},
		{"Cleo", 10},
	}

	assertLeague(t, got, want)

	// 再读一次
	got = store.GetLeague()
	assertLeague(t, got, want)
})
```

传进来的 JSON 本身顺序是乱的，而我们的 `want` 会检查返回给调用方时顺序已经正确。

## 试着运行测试

```
=== RUN   TestFileSystemStore/league_from_a_reader,_sorted
    --- FAIL: TestFileSystemStore/league_from_a_reader,_sorted (0.00s)
        file_system_store_test.go:46: got [{Cleo 10} {Chris 33}] want [{Chris 33} {Cleo 10}]
        file_system_store_test.go:51: got [{Cleo 10} {Chris 33}] want [{Chris 33} {Cleo 10}]
```

## 写足够的代码让测试通过

```go
func (f *FileSystemPlayerStore) GetLeague() League {
	sort.Slice(f.league, func(i, j int) bool {
		return f.league[i].Wins > f.league[j].Wins
	})
	return f.league
}
```

[`sort.Slice`](https://golang.org/pkg/sort/#Slice)

> Slice 函数按照给定的 less 函数对给定的切片进行排序。

简单！

## 总结

### 本章覆盖的内容

- `Seeker` 接口，以及它与 `Reader`、`Writer` 的关系。
- 文件操作。
- 打造一个好用的测试辅助函数，把文件测试中所有脏活细节都藏起来。
- 用 `sort.Slice` 给切片排序。
- 借助编译器，安全地对应用做结构性改动。

### 打破规则

- 软件工程里的多数"规则"其实算不上规则，只是 80% 的情况下管用的最佳实践。
- 我们遇到了一个场景：先前"不测内部函数"的"规则"帮不到我们，于是我们把它打破了。
- 打破规则时，搞清楚自己付出的代价很重要。在我们的例子里，我们可以接受，因为这只是一个测试，而且除此之外很难覆盖到那个场景。
- 想要打破规则，**你必须先理解规则**。拿学吉他打比方：无论你自认为多有创造力，基本功都得先理解、勤练习。

### 我们的软件现状

- 我们有了一个 HTTP API，可以创建玩家、累加他们的得分。
- 能以 JSON 返回所有人的得分榜。
- 数据以 JSON 文件的形式持久化。
