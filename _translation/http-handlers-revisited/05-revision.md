# 再探 HTTP Handlers

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/q-and-a/http-handlers-revisited)**

本书已经有一章讲过[如何测试 HTTP 处理器](http-server.md)，但本章会对"如何设计处理器"作更宽泛的讨论，让它们变得简单易测。

我们会看一个真实的例子，看看如何运用单一职责原则（single responsibility principle）、关注点分离这类原则来改进它的设计。这些原则可以借助[接口](structs-methods-and-interfaces.md)和[依赖注入](dependency-injection.md)来落地。做到这些，你会看到测试处理器其实相当轻而易举。

![Go 社区常见问题图解](assets/amazing-art.png)

如何测试 HTTP 处理器，似乎是 Go 社区里反复出现的问题。我认为这指向一个更普遍的问题：大家没搞明白处理器该怎么设计。

很多时候，人们测试时遇到的困难源自代码的设计，而不是写测试这件事本身。正如我在本书里反复强调的：

> 如果你的测试让你痛苦，请倾听这个信号，去想想你的代码设计。

## 一个例子

[Santosh Kumar 发了条推文问我](https://twitter.com/sntshk/status/1255559003339284481)

> 我该怎么测试一个依赖 mongodb 的 http 处理器？

代码是这样的

```go
func Registration(w http.ResponseWriter, r *http.Request) {
	var res model.ResponseResult
	var user model.User

	w.Header().Set("Content-Type", "application/json")

	jsonDecoder := json.NewDecoder(r.Body)
	jsonDecoder.DisallowUnknownFields()
	defer r.Body.Close()

	// 检查请求体是不是合法的 JSON，或者有没有报错
	if err := jsonDecoder.Decode(&user); err != nil {
		res.Error = err.Error()
		// 返回 400 状态码
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(res)
		return
	}

	// 连接 mongodb
	client, _ := mongo.NewClient(options.Client().ApplyURI("mongodb://127.0.0.1:27017"))
	ctx, _ := context.WithTimeout(context.Background(), 10*time.Second)
	err := client.Connect(ctx)
	if err != nil {
		panic(err)
	}
	defer client.Disconnect(ctx)
	// 检查用户名是否已存在于 users 数据存储中，若存在则返回 400
	// 否则立即插入用户
	collection := client.Database("test").Collection("users")
	filter := bson.D{{"username", user.Username}}
	var foundUser model.User
	err = collection.FindOne(context.TODO(), filter).Decode(&foundUser)
	if foundUser.Username == user.Username {
		res.Error = UserExists
		// 返回 400 状态码
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(res)
		return
	}

	pass, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
	if err != nil {
		res.Error = err.Error()
		// 返回 400 状态码
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(res)
		return
	}
	user.Password = string(pass)

	insertResult, err := collection.InsertOne(context.TODO(), user)
	if err != nil {
		res.Error = err.Error()
		// 返回 400 状态码
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(res)
		return
	}

	// 返回 200
	w.WriteHeader(http.StatusOK)
	res.Result = fmt.Sprintf("%s: %s", UserCreated, insertResult.InsertedID)
	json.NewEncoder(w).Encode(res)
	return
}
```

我们来列一列，这一个函数都得干哪些事：

1. 写 HTTP 响应，发送响应头、状态码等
2. 把请求体解码成 `User`
3. 连接数据库（以及围绕它的种种细节）
4. 查询数据库，并根据查询结果应用一些业务逻辑
5. 生成密码
6. 插入一条记录

这也太多了吧。

## HTTP 处理器是什么？它该做什么？

先把 Go 的具体细节放到一边。不管用什么语言干活，[关注点分离](https://en.wikipedia.org/wiki/Separation_of_concerns)和[单一职责原则](https://en.wikipedia.org/wiki/Single-responsibility_principle)这两个思路一直让我受益匪浅。

这两条原则用起来可没那么容易，得看你手头在解决什么问题。职责到底*是*什么？

界线划在哪里，很大程度上取决于你想得多抽象，而且有时第一直觉并不可靠。

好在说到 HTTP 处理器，不管在哪个项目里，我对它该干什么都有相当清晰的答案：

1. 接收一个 HTTP 请求，解析并校验它。
2. 调用某个 `ServiceThing`，让它拿第 1 步得到的数据去完成 `ImportantBusinessLogic`。
3. 根据 `ServiceThing` 返回什么，发送合适的 `HTTP` 响应。

我不是说天底下每一个 HTTP 处理器*都*该大致长成这个形状，但对我经手的情况而言，一百次里有九十九次都是如此。

把这些关注点分开之后：

* 测试处理器变得轻而易举，而且只需聚焦于很少的几个关注点。
* 更重要的是，测试 `ImportantBusinessLogic` 时再也不必跟 `HTTP` 纠缠，你可以干干净净地测业务逻辑。
* 你可以在其他场景使用 `ImportantBusinessLogic`，无需修改它。
* 如果 `ImportantBusinessLogic` 改变了行为，只要接口不变，你的处理器就不必跟着改。

## Go 的处理器

[`http.HandlerFunc`](https://golang.org/pkg/net/http/#HandlerFunc)

> HandlerFunc 类型是一个适配器（adapter），让普通函数可以当作 HTTP 处理器来用。

`type HandlerFunc func(ResponseWriter, *Request)`

读者朋友，深呼吸，再看看前面那段代码。你注意到了什么？

**它就是一个接收若干参数的函数**

没有框架的魔法，没有注解，也没有魔法豆，什么都没有。

它就是个函数，*而我们知道怎么测函数*。

这跟前面的论述严丝合缝：

* 它接收一个 [`http.Request`](https://golang.org/pkg/net/http/#Request)，那不过是一捆绑好的数据，供我们检视、解析和校验。
* > [`http.ResponseWriter` 接口供 HTTP 处理器用来构造 HTTP 响应。](https://golang.org/pkg/net/http/#ResponseWriter)

### 一个超级基础的示例测试

```go
func Teapot(res http.ResponseWriter, req *http.Request) {
	res.WriteHeader(http.StatusTeapot)
}

func TestTeapotHandler(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/", nil)
	res := httptest.NewRecorder()

	Teapot(res, req)

	if res.Code != http.StatusTeapot {
		t.Errorf("got status %d but wanted %d", res.Code, http.StatusTeapot)
	}
}
```

要测试我们的函数？*调用*它就行了。

在测试里，我们传一个 `httptest.ResponseRecorder` 充当 `http.ResponseWriter` 参数，函数就会用它来写入 `HTTP` 响应。这个记录器会把它收到的写入内容一一记下（也就是 *spy* 一把），随后我们就能从容地下断言了。

## 在处理器里调用 `ServiceThing`

对 TDD 教程的一个常见抱怨是：它们总是"太简单"，不够"贴近真实世界"。我的回答是：

> 要是你所有的代码都能像你提到的那些例子一样简单易读、简单易测，那该多好？

这是我们面临的最大挑战之一，但值得我们不断追求。只要勤加练习、践行良好的软件工程原则，就*完全有可能*（尽管未必容易）设计出简单易读、简单易测的代码。

回顾一下前文那个处理器要做的事：

1. 写 HTTP 响应，发送响应头、状态码等
2. 把请求体解码成 `User`
3. 连接数据库（以及围绕它的种种细节）
4. 查询数据库，并根据查询结果应用一些业务逻辑
5. 生成密码
6. 插入一条记录

按照更理想的关注点分离的思路，我希望它更像这样：

1. 把请求体解码成 `User`
2. 调用 `UserService.Register(user)`（这就是我们的 `ServiceThing`）
3. 如果出错就处理错误（原例不论什么错都一律返回 `400 BadRequest`，我觉得并不妥），我*眼下*就先一律兜底返回一个 `500 Internal Server Error`。必须强调：所有错误都返回 `500`，做出来的会是一个糟糕透顶的 API！稍后我们可以把错误处理做得更精细，比如借助[错误类型](error-types.md)。
4. 如果没出错，就返回 `201 Created`，以 ID 作为响应体（依旧是为了从简——说白了就是犯懒）

为省篇幅，常规的 TDD 流程这里就不再走一遍了，具体示例可以翻翻其他章节。

### 新设计

```go
type UserService interface {
	Register(user User) (insertedID string, err error)
}

type UserServer struct {
	service UserService
}

func NewUserServer(service UserService) *UserServer {
	return &UserServer{service: service}
}

func (u *UserServer) RegisterUser(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()

	// 请求的解析与校验
	var newUser User
	err := json.NewDecoder(r.Body).Decode(&newUser)

	if err != nil {
		http.Error(w, fmt.Sprintf("could not decode user payload: %v", err), http.StatusBadRequest)
		return
	}

	// 调用某个 service，让它去干重活累活
	insertedID, err := u.service.Register(newUser)

	// 根据拿到的结果，作出相应的响应
	if err != nil {
		//todo: 区分不同种类的错误分别处理
		http.Error(w, fmt.Sprintf("problem registering new user: %v", err), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	fmt.Fprint(w, insertedID)
}
```

我们的 `RegisterUser` 方法与 `http.HandlerFunc` 的形状一致，万事俱备。我们把它作为方法挂在新类型 `UserServer` 上，`UserServer` 内部保存着一个 `UserService` 依赖，而这个依赖以接口的形式呈现。

接口是确保 `HTTP` 相关关注点与任何具体实现解耦的绝妙办法；我们只管调用依赖上的方法，完全不必关心用户是*如何*被注册的。

想沿着 TDD 的路子更深入地研究这套方法，请阅读[《依赖注入》](dependency-injection.md)一章，以及["构建一个应用"篇的《HTTP 服务器》一章](http-server.md)。

既然已经同注册相关的任何具体实现细节解耦，处理器代码写起来就直截了当了，完全遵循前面描述的那几条职责。

### 测试！

这份简洁也体现在我们的测试里。

```go
type MockUserService struct {
	RegisterFunc    func(user User) (string, error)
	UsersRegistered []User
}

func (m *MockUserService) Register(user User) (insertedID string, err error) {
	m.UsersRegistered = append(m.UsersRegistered, user)
	return m.RegisterFunc(user)
}

func TestRegisterUser(t *testing.T) {
	t.Run("can register valid users", func(t *testing.T) {
		user := User{Name: "CJ"}
		expectedInsertedID := "whatever"

		service := &MockUserService{
			RegisterFunc: func(user User) (string, error) {
				return expectedInsertedID, nil
			},
		}
		server := NewUserServer(service)

		req := httptest.NewRequest(http.MethodGet, "/", userToJSON(user))
		res := httptest.NewRecorder()

		server.RegisterUser(res, req)

		assertStatus(t, res.Code, http.StatusCreated)

		if res.Body.String() != expectedInsertedID {
			t.Errorf("expected body of %q but got %q", res.Body.String(), expectedInsertedID)
		}

		if len(service.UsersRegistered) != 1 {
			t.Fatalf("expected 1 user added but got %d", len(service.UsersRegistered))
		}

		if !reflect.DeepEqual(service.UsersRegistered[0], user) {
			t.Errorf("the user registered %+v was not what was expected %+v", service.UsersRegistered[0], user)
		}
	})

	t.Run("returns 400 bad request if body is not valid user JSON", func(t *testing.T) {
		server := NewUserServer(nil)

		req := httptest.NewRequest(http.MethodGet, "/", strings.NewReader("trouble will find me"))
		res := httptest.NewRecorder()

		server.RegisterUser(res, req)

		assertStatus(t, res.Code, http.StatusBadRequest)
	})

	t.Run("returns a 500 internal server error if the service fails", func(t *testing.T) {
		user := User{Name: "CJ"}

		service := &MockUserService{
			RegisterFunc: func(user User) (string, error) {
				return "", errors.New("couldn't add new user")
			},
		}
		server := NewUserServer(service)

		req := httptest.NewRequest(http.MethodGet, "/", userToJSON(user))
		res := httptest.NewRecorder()

		server.RegisterUser(res, req)

		assertStatus(t, res.Code, http.StatusInternalServerError)
	})
}
```

我们的处理器不再与某个具体的存储实现耦合，写一个 `MockUserService` 来帮我们做简单、快速的单元测试，覆盖它肩负的那几项具体职责，就再轻松不过了。

### 那数据库代码呢？你这是在作弊！

这一切都是有意为之。我们不想让 HTTP 处理器操心业务逻辑、数据库、连接这些事。

这样做，我们把处理器从乱七八糟的细节中解放了出来，*同时也*让持久层和业务逻辑更好测了，因为它们也不再和不相干的 HTTP 细节耦合。

剩下要做的，就是用我们想用的任何数据库去实现 `UserService`

```go
type MongoUserService struct {
}

func NewMongoUserService() *MongoUserService {
	//todo: 把数据库 URL 作为参数传进这个函数
	//todo: 连接数据库，创建连接池
	return &MongoUserService{}
}

func (m MongoUserService) Register(user User) (insertedID string, err error) {
	// 用 m.mongoConnection 执行查询
	panic("implement me")
}
```

我们可以单独测试它，等满意了，再到 `main` 里把这两个单元咔哒一声拼在一起，能工作的应用就出炉了。

```go
func main() {
	mongoService := NewMongoUserService()
	server := NewUserServer(mongoService)
	http.ListenAndServe(":8000", http.HandlerFunc(server.RegisterUser))
}
```

### 不费吹灰之力，换来更健壮、更易扩展的设计

这些原则不仅让我们眼下日子好过，还让系统将来更容易扩展。

这个系统往后迭代时，我们多半还想给用户发一封注册确认邮件，这不足为奇。

换作旧设计，我们就得同时改动处理器*和*它周边的测试。很多代码就是这样变得无法维护的：越来越多的功能悄悄爬进来，因为它*天生*就是这么设计的——让"HTTP 处理器"去处理……一切！

用接口把关注点分开之后，处理器*一行都不用改*，因为它根本不关心注册相关的业务逻辑。

## 总结

测试 Go 的 HTTP 处理器并不难，难的是设计出好的软件！

人们常犯的错误，是把 HTTP 处理器想得太特殊，写的时候就丢掉了良好的软件工程实践，测试起来于是变得困难。

再强调一次：**Go 的 HTTP 处理器就是函数**。像写其他函数一样去写它们——职责清晰、关注点分离得当——测试起来就不会有任何麻烦，你的代码库也会因此更加健康。
