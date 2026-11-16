window.TOPICS = (window.TOPICS || []).concat([
  {
    id: "py-generators", area: "python", title: "Generators and iterators", mins: 30, level: 2, light: false,
    res: { label: "Python docs: functional programming HOWTO (generators)", url: "https://docs.python.org/3/howto/functional.html", src: "free" },
    aloud: "Explain what yield does and why a generator can handle a file bigger than memory.",
    interviewQ: "You need to process a 20 GB log file line by line. How do you write it so it does not run out of memory?",
    quiz: [
      { q: "What does a generator do?",
        options: ["Builds the full list of results up front", "Produces values one at a time, on demand", "Runs code in parallel", "Caches every value forever"],
        answer: 1, why: "A generator pauses at each yield and resumes when the next value is requested, so only one item is in memory at a time." },
      { q: "How does (x * x for x in range(10**9)) differ from [x * x for x in range(10**9)]?",
        options: ["No difference", "The generator expression does not build the whole list in memory", "The list is lazy", "The generator is slower to create"],
        answer: 1, why: "The list comprehension tries to hold a billion numbers at once. The generator expression yields them as you loop." },
      { q: "You loop over a generator to the end and then loop over it again. What happens on the second loop?",
        options: ["It restarts from the beginning", "It yields nothing, because the generator is exhausted", "It raises a syntax error", "It doubles the values"],
        answer: 1, why: "Generators are single-use. Create a new one if you need to iterate again." }
    ]
  },
  {
    id: "py-decorators", area: "python", title: "Decorators", mins: 30, level: 3, light: false,
    res: { label: "Real Python: primer on decorators", url: "https://realpython.com/primer-on-python-decorators/", src: "free" },
    aloud: "Explain a decorator as a function that wraps another function, and write a simple timing decorator out loud.",
    interviewQ: "Write a decorator that retries a function up to three times if it raises an exception.",
    quiz: [
      { q: "What is a decorator?",
        options: ["A comment style", "A function that takes a function and returns a new, usually wrapped, function", "A type of class", "A built-in loop"],
        answer: 1, why: "Decorators let you add behavior such as timing, logging or caching around a function without changing its code." },
      { q: "Why use functools.wraps inside a decorator?",
        options: ["It makes the function faster", "It preserves the wrapped function's name and docstring", "It prevents errors", "It is required for the code to run"],
        answer: 1, why: "Without it, the decorated function appears under the wrapper's name, which confuses debugging and documentation." },
      { q: "The syntax @timer above def f() is equivalent to:",
        options: ["f = timer", "f = timer(f)", "timer = f(timer)", "f(timer)"],
        answer: 1, why: "The decorator is called with the function and its return value replaces the original name." }
    ]
  },
  {
    id: "py-mutable", area: "python", title: "Mutable default arguments and copying", mins: 25, level: 2, light: true,
    res: { label: "Python docs: default argument values", url: "https://docs.python.org/3/tutorial/controlflow.html#default-argument-values", src: "free" },
    aloud: "Explain why a list used as a default argument can keep its old contents between calls, and give the standard fix.",
    interviewQ: "What does this print: def add(x, items=[]): items.append(x); return items, then add(1) followed by add(2)?",
    quiz: [
      { q: "def add(x, items=[]): items.append(x); return items. What does add(1) followed by add(2) return the second time?",
        options: ["[2]", "[1, 2]", "[1]", "An error"],
        answer: 1, why: "The default list is created once, when the function is defined, and shared by every call that uses the default." },
      { q: "What is the standard fix for a mutable default argument?",
        options: ["Use a tuple everywhere", "Default to None and create the list inside the function", "Delete the default", "Use a global variable"],
        answer: 1, why: "Write items=None, then 'if items is None: items = []' so each call gets a fresh list." },
      { q: "a = [[1], [2]]; b = a.copy(); b[0].append(9). What is a[0] afterwards?",
        options: ["[1]", "[1, 9]", "[9]", "An error"],
        answer: 1, why: "copy() makes a shallow copy: the outer list is new, but the inner lists are shared. Use copy.deepcopy to copy nested objects." }
    ]
  },
  {
    id: "py-pandas", area: "python", title: "pandas: groupby, merge and transform", mins: 35, level: 2, light: false,
    res: { label: "DataCamp: Data Manipulation with pandas", url: "https://www.datacamp.com/courses/data-manipulation-with-pandas", src: "datacamp" },
    aloud: "Explain the difference between agg and transform in groupby, and when a left merge drops or adds rows.",
    interviewQ: "Add a column showing each row's share of its group's total sales. Which pandas call do you use?",
    quiz: [
      { q: "What does df.groupby('city')['sales'].sum() return?",
        options: ["A DataFrame with one row per sale", "A Series with total sales for each city", "A single number", "A sorted copy of the data"],
        answer: 1, why: "It groups by city and aggregates the sales column, returning one value per group, indexed by city." },
      { q: "What does pd.merge(a, b, how='left', on='id') keep?",
        options: ["Only matching rows", "All rows from a, with NaN where b has no match", "All rows from b", "Only rows missing in b"],
        answer: 1, why: "A left merge keeps every row of the left DataFrame. If b has duplicate ids, rows from a can also repeat." },
      { q: "How does transform differ from agg in a groupby?",
        options: ["They are the same", "transform returns a result aligned with the original rows (same length), such as each row's group mean", "agg keeps all rows", "transform only works on strings"],
        answer: 1, why: "Use transform to broadcast a group statistic back onto every row, for example sales divided by the group total." }
    ]
  },
  {
    id: "py-bigo", area: "python", title: "Big-O in everyday Python", mins: 30, level: 3, light: false,
    res: { label: "Python wiki: time complexity of built-ins", url: "https://wiki.python.org/moin/TimeComplexity", src: "free" },
    aloud: "Explain why checking membership in a set is faster than in a list, and what the cost of a nested loop is.",
    interviewQ: "You check 'x in my_list' inside a loop over 100,000 items and it is slow. What do you change?",
    quiz: [
      { q: "What is the average time complexity of 'x in some_set' compared with 'x in some_list'?",
        options: ["Both O(1)", "Set is O(1) on average and list is O(n)", "Set is O(n) and list is O(1)", "Both O(n)"],
        answer: 1, why: "Sets use hashing for near-constant lookups. A list must scan its elements one by one." },
      { q: "What is the complexity of looping over n items with another full loop over n items inside?",
        options: ["O(n)", "O(n log n)", "O(n squared)", "O(log n)"],
        answer: 2, why: "n iterations times n iterations is n squared work, which grows quickly." },
      { q: "Which list operation is O(n) in Python?",
        options: ["Appending to the end (amortized)", "Reading an item by index", "Inserting at the front", "Getting the length"],
        answer: 2, why: "Inserting at index 0 shifts every other element. Appending is amortized O(1), and indexing and len are O(1)." }
    ]
  },
  {
    id: "py-classes", area: "python", title: "Classes and dataclasses", mins: 30, level: 2, light: false,
    res: { label: "Python docs: dataclasses", url: "https://docs.python.org/3/library/dataclasses.html", src: "free" },
    aloud: "Explain what a dataclass saves you from writing and when a plain class or a dict is the better choice.",
    interviewQ: "What is the difference between a class attribute and an instance attribute, and what bug can a mutable class attribute cause?",
    quiz: [
      { q: "What does the @dataclass decorator generate for you by default?",
        options: ["__init__, __repr__ and __eq__", "A database table", "Type checking at runtime", "Thread safety"],
        answer: 0, why: "It writes the boilerplate methods from the annotated fields." },
      { q: "What does self refer to in an instance method?",
        options: ["The class itself", "The specific instance the method was called on", "The parent class", "The module"],
        answer: 1, why: "Python passes the instance as the first argument, and by convention it is named self." },
      { q: "A class defines items = [] at class level, and two objects both append to self.items. What happens?",
        options: ["Each object has its own list", "Both objects share one list", "An error is raised", "The list is copied on write"],
        answer: 1, why: "A class attribute belongs to the class, so mutating it affects every instance. Create the list in __init__ instead." }
    ]
  },
  {
    id: "py-errors", area: "python", title: "Exceptions and context managers", mins: 25, level: 2, light: true,
    res: { label: "Python docs: errors and exceptions", url: "https://docs.python.org/3/tutorial/errors.html", src: "free" },
    aloud: "Explain try, except, else and finally, and why 'with open(...)' is safer than opening and closing a file by hand.",
    interviewQ: "Why is a bare 'except:' considered bad practice, and what should you write instead?",
    quiz: [
      { q: "What does 'with open(path) as f:' guarantee?",
        options: ["The file is read faster", "The file is closed when the block ends, even if an exception occurs", "The file is created if missing", "The file is locked forever"],
        answer: 1, why: "A context manager runs its cleanup code whether the block finishes normally or raises." },
      { q: "Why is a bare 'except:' risky?",
        options: ["It is a syntax error", "It also catches things like KeyboardInterrupt and hides real bugs", "It slows the program down", "It only works in functions"],
        answer: 1, why: "Catch the specific exceptions you expect, and let unexpected ones surface." },
      { q: "When does a 'finally' block run?",
        options: ["Only when an exception occurs", "Only when no exception occurs", "In both cases", "Never in functions"],
        answer: 2, why: "finally always runs, which makes it the right place for cleanup." }
    ]
  }
]);
