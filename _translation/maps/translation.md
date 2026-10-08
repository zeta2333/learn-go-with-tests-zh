# Map

**[本章的所有代码都可以在这里找到](https://github.com/quii/learn-go-with-tests/tree/main/maps)**

在[数组和切片](arrays-and-slices.md)一章，你已经见过如何按顺序存储值。现在我们来看另一种存储方式：按照键（key）来存放条目，并能快速查找。

map 让你可以像词典那样存储条目。你可以把键想成单词，把值（value）想成释义。还有什么比亲手做一个词典更好的学 map 的方式呢？

第一步，先假设词典里已经有了一些单词和它们的释义，那么当我们查一个单词时，应该返回它的释义。

## 先写测试

在 `dictionary_test.go` 中

```go
package main

import "testing"

func TestSearch(t *testing.T) {
	dictionary := map[string]string{"test": "this is just a test"}

	got := Search(dictionary, "test")
	want := "this is just a test"

	if got != want {
		t.Errorf("got %q want %q given, %q", got, want, "test")
	}
}
```

声明 map 的写法跟数组有点像。区别在于它以 `map` 关键字开头，而且需要两个类型。第一个是键的类型，写在 `[]` 里面；第二个是值的类型，紧跟在 `[]` 后面。

键的类型比较特殊：它只能是可比较（comparable）的类型。因为如果没法判断两个键是否相等，我们就无法保证取到的是正确的值。可比较类型在[语言规范](https://golang.org/ref/spec#Comparison_operators)里有深入讲解。

而值的类型就随便你了，想要什么类型都行，甚至可以是另一个 map。

这个测试里的其他东西你应该都眼熟了。

## 试着运行测试

运行 `go test`，编译器会报错：`./dictionary_test.go:8:9: undefined: Search`。

## 写最少的代码让测试能运行，并检查输出

在 `dictionary.go` 中

```go
package main

func Search(dictionary map[string]string, word string) string {
	return ""
}
```

现在测试应该会失败，并给出一条*清晰的错误信息*

`dictionary_test.go:12: got '' want 'this is just a test' given, 'test'`.

## 写足够的代码让测试通过

```go
func Search(dictionary map[string]string, word string) string {
	return dictionary[word]
}
```

从 map 里取值跟从数组里取值一样，都是 `map[key]`。

## 重构

```go
func TestSearch(t *testing.T) {
	dictionary := map[string]string{"test": "this is just a test"}

	got := Search(dictionary, "test")
	want := "this is just a test"

	assertStrings(t, got, want)
}

func assertStrings(t testing.TB, got, want string) {
	t.Helper()

	if got != want {
		t.Errorf("got %q want %q", got, want)
	}
}
```

我决定创建一个 `assertStrings` 辅助函数，让这套写法更通用一些。

### 使用自定义类型

我们可以在 map 外面包一层新类型，并把 `Search` 变成方法，这样词典用起来更顺手。

在 `dictionary_test.go` 中：

```go
func TestSearch(t *testing.T) {
	dictionary := Dictionary{"test": "this is just a test"}

	got := dictionary.Search("test")
	want := "this is just a test"

	assertStrings(t, got, want)
}
```

我们开始使用 `Dictionary` 类型——它还没定义呢——然后在这个 `Dictionary` 实例上调用了 `Search`。

`assertStrings` 则不需要任何改动。

在 `dictionary.go` 中：

```go
type Dictionary map[string]string

func (d Dictionary) Search(word string) string {
	return d[word]
}
```

这里我们创建了 `Dictionary` 类型，它是 `map` 的一层薄封装。自定义类型有了，就可以在上面创建 `Search` 方法了。

## 先写测试

基本的搜索实现起来非常简单，但如果我们查的词不在词典里，会发生什么？

实际上你什么都得不到。这也有好处——程序还能继续跑，但有更好的做法：让函数报告这个词不在词典里。这样用户就不必纠结到底是词不存在，还是只是没有释义（对词典来说，这一点似乎没什么用；但在其他场景中，它可能恰恰是 key——关键所在）。

```go
func TestSearch(t *testing.T) {
	dictionary := Dictionary{"test": "this is just a test"}

	t.Run("known word", func(t *testing.T) {
		got, _ := dictionary.Search("test")
		want := "this is just a test"

		assertStrings(t, got, want)
	})

	t.Run("unknown word", func(t *testing.T) {
		_, err := dictionary.Search("unknown")
		want := "could not find the word you were looking for"

		if err == nil {
			t.Fatal("expected to get an error.")
		}

		assertStrings(t, err.Error(), want)
	})
}
```

在 Go 里，处理这种场景的办法是返回第二个参数，一个 `Error` 类型。

注意，正如我们在[指针和错误](./pointers-and-errors.md)一节中见过的：这里为了对错误信息做断言，我们先检查错误不是 `nil`，然后用 `.Error()` 方法拿到字符串，再把它传给断言。

## 试着运行测试

这段代码编译不过

```
./dictionary_test.go:18:10: assignment mismatch: 2 variables but 1 values
```

## 写最少的代码让测试能运行，并检查输出

```go
func (d Dictionary) Search(word string) (string, error) {
	return d[word], nil
}
```

现在测试应该会失败，错误信息也清晰得多。

`dictionary_test.go:22: expected to get an error.`

## 写足够的代码让测试通过

```go
func (d Dictionary) Search(word string) (string, error) {
	definition, ok := d[word]
	if !ok {
		return "", errors.New("could not find the word you were looking for")
	}

	return definition, nil
}
```

为了让测试通过，我们用上了 map 取值的一个有趣特性：它可以返回两个值。第二个值是个布尔值，表示键是否查找成功。

有了这个特性，我们就能区分"单词不存在"和"单词存在但没有释义"这两种情况。

## 重构

```go
var ErrNotFound = errors.New("could not find the word you were looking for")

func (d Dictionary) Search(word string) (string, error) {
	definition, ok := d[word]
	if !ok {
		return "", ErrNotFound
	}

	return definition, nil
}
```

把写死的错误从 `Search` 函数里抽出来，收进一个变量。这还让我们能写出更好的测试。

```go
t.Run("unknown word", func(t *testing.T) {
	_, got := dictionary.Search("unknown")
	if got == nil {
		t.Fatal("expected to get an error.")
	}
	assertError(t, got, ErrNotFound)
})
```
```go
func assertError(t testing.TB, got, want error) {
	t.Helper()

	if !errors.Is(got, want) {
		t.Errorf("got error %q want %q", got, want)
	}
}
```

新建这个辅助函数之后，测试简化了，我们还用上了 `ErrNotFound` 变量——以后就算改了错误文本，测试也不会跟着挂掉。

## 先写测试

搜索词典的办法很棒了，可我们还没法往词典里添加新单词。

```go
func TestAdd(t *testing.T) {
	dictionary := Dictionary{}
	dictionary.Add("test", "this is just a test")

	want := "this is just a test"
	got, err := dictionary.Search("test")
	if err != nil {
		t.Fatal("should find added word:", err)
	}

	assertStrings(t, got, want)
}
```

在这个测试里，我们借助 `Search` 函数来做验证，让这件事省力一点。

## 写最少的代码让测试能运行，并检查输出

在 `dictionary.go` 中

```go
func (d Dictionary) Add(word, definition string) {
}
```

现在测试应该会失败

```
dictionary_test.go:31: should find added word: could not find the word you were looking for
```

## 写足够的代码让测试通过

```go
func (d Dictionary) Add(word, definition string) {
	d[word] = definition
}
```

往 map 里添加元素也跟数组类似：指定一个键，把它赋成一个值就行。

### 指针、拷贝，诸如此类

map 有个有趣的特性：不需要传它的地址（比如 `&myMap`），你也能修改它。

这可能会让人*感觉* map 是一种"引用类型"（reference type），[但正如 Dave Cheney 所描述的](https://dave.cheney.net/2017/04/30/if-a-map-isnt-a-reference-variable-what-is-it)，它们并不是。

> map 的值是一个指向 `runtime.hmap` 结构的指针。

所以，当你把 map 传给函数或方法时，你确实是在拷贝它——但拷贝的只是指针那部分，并不包括承载数据的底层数据结构。

map 有个容易踩的坑：它的值可能是 `nil`。读一个 `nil` map 时，它的表现就像空 map；但往 `nil` map 里写，会触发运行时 panic（程序崩溃）。关于 map 的更多内容可以在[这里](https://blog.golang.org/go-maps-in-action)读到。

所以，永远不要像下面这样把 map 变量留在 nil 零值态：

```go
var m map[string]string
```

作为替代，你可以初始化一个空 map，或者用 `make` 关键字来帮你创建一个 map：

```go
var dictionary = map[string]string{}

// 或者

var dictionary = make(map[string]string)
```

两种写法都会创建一个空的 `hash map`（哈希表），并让 `dictionary` 指向它。这样就能保证你永远不会碰到运行时 panic。

## 重构

我们的实现没什么可重构的，不过测试还可以再简化一点。

```go
func TestAdd(t *testing.T) {
	dictionary := Dictionary{}
	word := "test"
	definition := "this is just a test"

	dictionary.Add(word, definition)

	assertDefinition(t, dictionary, word, definition)
}

func assertDefinition(t testing.TB, dictionary Dictionary, word, definition string) {
	t.Helper()

	got, err := dictionary.Search(word)
	if err != nil {
		t.Fatal("should find added word:", err)
	}
	assertStrings(t, got, definition)
}
```

我们把单词和释义抽成了变量，并把释义断言挪进了独立的辅助函数。

我们的 `Add` 看起来相当不错了。只是——我们还没考虑过：要添加的值已经存在时会发生什么！

如果值已经存在，map 并不会报错，而是直接用新提供的值把它覆盖掉。这在实践中可能很方便，但也让我们的函数名变得不那么名副其实了。`Add` 不应该修改已有的值，它只应该往词典里添加新单词。

## 先写测试

```go
func TestAdd(t *testing.T) {
	t.Run("new word", func(t *testing.T) {
		dictionary := Dictionary{}
		word := "test"
		definition := "this is just a test"

		err := dictionary.Add(word, definition)

		assertError(t, err, nil)
		assertDefinition(t, dictionary, word, definition)
	})

	t.Run("existing word", func(t *testing.T) {
		word := "test"
		definition := "this is just a test"
		dictionary := Dictionary{word: definition}
		err := dictionary.Add(word, "new test")

		assertError(t, err, ErrWordExists)
		assertDefinition(t, dictionary, word, definition)
	})
}
```

在这个测试里，我们让 `Add` 返回一个错误，并用一个新的错误变量 `ErrWordExists` 来做断言。我们还改了前面那个测试，让它检查错误是 `nil`。

## 试着运行测试

编译会失败，因为我们的 `Add` 没有返回值。

```
./dictionary_test.go:30:13: dictionary.Add(word, definition) used as value
./dictionary_test.go:41:13: dictionary.Add(word, "new test") used as value
```

## 写最少的代码让测试能运行，并检查输出

在 `dictionary.go` 中

```go
var (
	ErrNotFound   = errors.New("could not find the word you were looking for")
	ErrWordExists = errors.New("cannot add word because it already exists")
)

func (d Dictionary) Add(word, definition string) error {
	d[word] = definition
	return nil
}
```

现在我们又多了两个失败：值仍然被我们修改，返回的却是 `nil` 错误。

```
dictionary_test.go:43: got error '%!q(<nil>)' want 'cannot add word because it already exists'
dictionary_test.go:44: got 'new test' want 'this is just a test'
```

## 写足够的代码让测试通过

```go
func (d Dictionary) Add(word, definition string) error {
	_, err := d.Search(word)

	switch err {
	case ErrNotFound:
		d[word] = definition
	case nil:
		return ErrWordExists
	default:
		return err
	}

	return nil
}
```

这里我们用 `switch` 语句来对错误做匹配。有了这样一个 `switch`，就多了一层安全网：万一 `Search` 返回的不是 `ErrNotFound` 而是别的错误，也能兜得住。

## 重构

可重构的东西不多，不过随着错误用得越来越多，我们可以做几处调整。

```go
const (
	ErrNotFound   = DictionaryErr("could not find the word you were looking for")
	ErrWordExists = DictionaryErr("cannot add word because it already exists")
)

type DictionaryErr string

func (e DictionaryErr) Error() string {
	return string(e)
}
```

我们把错误做成了常量；这就要求我们创建自己的 `DictionaryErr` 类型，让它实现 `error` 接口。细节可以读 [Dave Cheney 的这篇精彩文章](https://dave.cheney.net/2016/04/07/constant-errors)。简单来说，这样做让错误更可复用，也更不可变。

接下来，我们来创建一个 `Update` 函数，用来更新单词的释义。

## 先写测试

```go
func TestUpdate(t *testing.T) {
	word := "test"
	definition := "this is just a test"
	dictionary := Dictionary{word: definition}
	newDefinition := "new definition"

	dictionary.Update(word, newDefinition)

	assertDefinition(t, dictionary, word, newDefinition)
}
```

`Update` 跟 `Add` 关系非常紧密，它就是我们下一个要实现的方法。

## 试着运行测试

```
./dictionary_test.go:53:2: dictionary.Update undefined (type Dictionary has no field or method Update)
```

## 写最少的代码让测试能运行，并检查失败的测试输出

这种错误我们已经知道怎么对付了：把函数定义出来。

```go
func (d Dictionary) Update(word, definition string) {}
```

有了它，测试就能告诉我们：需要改动这个单词的释义。

```
dictionary_test.go:55: got 'this is just a test' want 'new definition'
```

## 写足够的代码让测试通过

这个问题我们在修 `Add` 的时候已经见过解法了。那就来实现一个跟它非常相似的东西吧。

```go
func (d Dictionary) Update(word, definition string) {
	d[word] = definition
}
```

这次改动很简单，没什么需要重构的。不过，我们又要面对跟 `Add` 一样的问题了：如果传入一个新单词，`Update` 会把它加进词典。

## 先写测试

```go
t.Run("existing word", func(t *testing.T) {
	word := "test"
	definition := "this is just a test"
	dictionary := Dictionary{word: definition}
	newDefinition := "new definition"

	err := dictionary.Update(word, newDefinition)

	assertError(t, err, nil)
	assertDefinition(t, dictionary, word, newDefinition)
})

t.Run("new word", func(t *testing.T) {
	word := "test"
	definition := "this is just a test"
	dictionary := Dictionary{}

	err := dictionary.Update(word, definition)

	assertError(t, err, ErrWordDoesNotExist)
})
```

我们又加了一个新的错误类型，用于单词不存在的情况。我们还让 `Update` 返回一个 `error` 值。

## 试着运行测试

```
./dictionary_test.go:53:16: dictionary.Update(word, newDefinition) used as value
./dictionary_test.go:64:16: dictionary.Update(word, definition) used as value
./dictionary_test.go:66:23: undefined: ErrWordDoesNotExist
```

这次我们收到 3 个错误，但怎么处理我们心里有数。

## 写最少的代码让测试能运行，并检查失败的测试输出

```go
const (
	ErrNotFound         = DictionaryErr("could not find the word you were looking for")
	ErrWordExists       = DictionaryErr("cannot add word because it already exists")
	ErrWordDoesNotExist = DictionaryErr("cannot perform operation on word because it does not exist")
)

func (d Dictionary) Update(word, definition string) error {
	d[word] = definition
	return nil
}
```

我们添加了自己的错误类型，并返回 `nil` 错误。

改完之后，我们得到了一个非常清晰的错误：

```
dictionary_test.go:66: got error '%!q(<nil>)' want 'cannot perform operation on word because it does not exist'
```

## 写足够的代码让测试通过

```go
func (d Dictionary) Update(word, definition string) error {
	_, err := d.Search(word)

	switch err {
	case ErrNotFound:
		return ErrWordDoesNotExist
	case nil:
		d[word] = definition
	default:
		return err
	}

	return nil
}
```

这个函数看起来几乎跟 `Add` 一模一样，只是 `switch` 里干的活正好对调了：何时更新 `dictionary`、何时返回错误。

### 关于为 Update 声明新错误的说明

我们其实可以复用 `ErrNotFound`，不必新增一个错误。但通常来说，更新失败时给出一个精确的错误是更好的做法。

具体的错误能提供更多线索，帮你搞清楚到底哪里出了问题。以一个 web 应用为例：

> 遇到 `ErrNotFound` 时，你可以把用户重定向到别处；而遇到 `ErrWordDoesNotExist` 时，则显示一条错误信息。

接下来，我们来创建一个 `Delete` 函数，从词典里删除单词。

## 先写测试

```go
func TestDelete(t *testing.T) {
	word := "test"
	dictionary := Dictionary{word: "test definition"}

	dictionary.Delete(word)

	_, err := dictionary.Search(word)
	assertError(t, err, ErrNotFound)
}
```

测试先创建了一个 `Dictionary`，里面放着一个单词，然后检查这个单词是否已被移除。

## 试着运行测试

运行 `go test`，得到：

```
./dictionary_test.go:74:6: dictionary.Delete undefined (type Dictionary has no field or method Delete)
```

## 写最少的代码让测试能运行，并检查失败的测试输出

```go
func (d Dictionary) Delete(word string) {

}
```

加上它之后，测试告诉我们：单词并没有被删掉。

```
dictionary_test.go:78: got error '%!q(<nil>)' want 'could not find the word you were looking for'
```

## 写足够的代码让测试通过

```go
func (d Dictionary) Delete(word string) {
	delete(d, word)
}
```

Go 有一个作用于 map 的内置函数 `delete`。它接收两个参数，不返回任何东西：第一个参数是 map，第二个是要移除的键。

## 重构

没什么可重构的，不过我们可以照搬 `Update` 里的那套逻辑，来处理单词不存在的情况。

```go
func TestDelete(t *testing.T) {
	t.Run("existing word", func(t *testing.T) {
		word := "test"
		dictionary := Dictionary{word: "test definition"}

		err := dictionary.Delete(word)

		assertError(t, err, nil)

		_, err = dictionary.Search(word)

		assertError(t, err, ErrNotFound)
	})

	t.Run("non-existing word", func(t *testing.T) {
		word := "test"
		dictionary := Dictionary{}

		err := dictionary.Delete(word)

		assertError(t, err, ErrWordDoesNotExist)
	})
}
```

## 试着运行测试

编译会失败，因为我们的 `Delete` 没有返回值。

```
./dictionary_test.go:77:10: dictionary.Delete(word) (no value) used as value
./dictionary_test.go:90:10: dictionary.Delete(word) (no value) used as value
```

## 写足够的代码让测试通过

```go
func (d Dictionary) Delete(word string) error {
	_, err := d.Search(word)

	switch err {
	case ErrNotFound:
		return ErrWordDoesNotExist
	case nil:
		delete(d, word)
	default:
		return err
	}

	return nil
}
```

当试图删除一个不存在的单词时，我们又一次用 `switch` 语句来对错误做匹配。

## 总结

这一章讲了不少东西。我们为词典做了一个完整的 CRUD（增删改查）API。一路走来，我们学会了：

* 创建 map
* 在 map 中查找条目
* 向 map 中添加新条目
* 更新 map 中的条目
* 从 map 中删除条目
* 深入了解了错误
  * 如何创建常量形式的错误
  * 编写错误包装类型
