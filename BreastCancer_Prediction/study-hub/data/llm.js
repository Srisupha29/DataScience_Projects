window.TOPICS = (window.TOPICS || []).concat([
  {
    id: "llm-attention", area: "llm", title: "Self-attention and transformers", mins: 40, level: 3, light: false,
    res: { label: "Jay Alammar: The Illustrated Transformer", url: "https://jalammar.github.io/illustrated-transformer/", src: "free" },
    aloud: "Explain self-attention as if each word in a sentence gets to look at the other words to decide what matters.",
    interviewQ: "Why did transformers replace RNNs for language tasks, and what is the cost?",
    quiz: [
      { q: "What does self-attention let a token do?",
        options: ["Look only at the previous token", "Weigh all other tokens in the sequence when building its own representation", "Skip tokens it does not need", "Translate itself"],
        answer: 1, why: "Each token computes attention weights over the whole sequence and mixes information from the tokens that matter most to it." },
      { q: "Why do transformers add positional encodings?",
        options: ["To speed up training", "Attention by itself has no notion of word order", "To reduce the vocabulary", "To normalize the weights"],
        answer: 1, why: "Without position information, shuffling the words would give the same representation." },
      { q: "How does the cost of standard self-attention scale with sequence length n?",
        options: ["Linearly", "Quadratically, because every token attends to every other token", "Logarithmically", "It does not depend on n"],
        answer: 1, why: "An n by n attention matrix is why long contexts are expensive and why efficient attention is an active research area." }
    ]
  },
  {
    id: "llm-tokens", area: "llm", title: "Tokens, context windows and cost", mins: 25, level: 2, light: true,
    res: { label: "Hugging Face: tokenizer summary", url: "https://huggingface.co/docs/transformers/tokenizer_summary", src: "free" },
    aloud: "Explain what a token is, what the context window limits, and why prompts and answers both cost money.",
    interviewQ: "Your RAG app's costs doubled after you added more retrieved text. Explain why and how to cut them.",
    quiz: [
      { q: "What is a token in most modern language models?",
        options: ["Always exactly one word", "A piece of text, often a word or part of a word", "A single character", "A sentence"],
        answer: 1, why: "Tokenizers split text into subword units, so a long or rare word may be several tokens." },
      { q: "What does the context window limit?",
        options: ["The number of users", "The total number of tokens the model can consider at once, including input and output", "The size of the training data", "How many API keys you can create"],
        answer: 1, why: "Prompt, retrieved documents, conversation history and the generated answer all share the same window." },
      { q: "What is API pricing for language models usually based on?",
        options: ["The number of requests only", "The number of tokens processed, typically priced separately for input and output", "The time of day", "The length of the user's name"],
        answer: 1, why: "More tokens in or out means more cost, so trimming context directly reduces the bill." }
    ]
  },
  {
    id: "llm-embeddings", area: "llm", title: "Embeddings and similarity search", mins: 35, level: 2, light: false,
    res: { label: "Sentence Transformers documentation", url: "https://www.sbert.net/", src: "free" },
    aloud: "Explain what an embedding is and how cosine similarity helps find documents that mean the same thing.",
    interviewQ: "Why would a keyword search miss a result that an embedding search finds, and when might keyword search win?",
    quiz: [
      { q: "What does an embedding model do?",
        options: ["Compresses files", "Maps text to a vector so that similar meanings end up close together", "Translates text to another language", "Counts words"],
        answer: 1, why: "Nearby vectors correspond to similar meaning, which is what makes semantic search possible." },
      { q: "What does cosine similarity measure?",
        options: ["The distance between vector endpoints only", "The angle between two vectors, ignoring their length", "The number of shared words", "The vector's magnitude"],
        answer: 1, why: "A value near 1 means the vectors point in nearly the same direction." },
      { q: "Why do vector databases use approximate nearest neighbor search?",
        options: ["Exact search is impossible", "Exact search over millions of vectors is too slow, and approximate search is much faster with small accuracy loss", "It gives more accurate results", "It removes the need for embeddings"],
        answer: 1, why: "Approximate indexes trade a little recall for large speed gains at scale." }
    ]
  },
  {
    id: "llm-rag", area: "llm", title: "RAG: retrieval-augmented generation", mins: 40, level: 3, light: false,
    res: { label: "DataCamp: RAG with LangChain", url: "https://www.datacamp.com/courses/retrieval-augmented-generation-rag-with-langchain", src: "datacamp" },
    aloud: "Walk through a RAG pipeline from the user's question to the final answer, naming each step.",
    interviewQ: "Your RAG chatbot gives wrong answers even though the right document is in the database. How do you debug it?",
    quiz: [
      { q: "What does retrieval-augmented generation do?",
        options: ["Retrains the model on your documents for every question", "Retrieves relevant documents and adds them to the prompt so the model can answer from them", "Compresses the prompt", "Replaces the model with a search engine"],
        answer: 1, why: "The model's weights stay the same. Fresh, relevant context is supplied at question time." },
      { q: "The answers ignore a document that does contain the answer. What should you check first?",
        options: ["The model's temperature", "Whether the right chunks are actually being retrieved", "The font in the UI", "The number of users"],
        answer: 1, why: "Most RAG failures are retrieval failures. Inspect the retrieved chunks before changing the prompt or model." },
      { q: "Why split documents into chunks before embedding them?",
        options: ["Embedding models cannot read documents", "Focused chunks retrieve more precisely and fit into the context window", "Chunks make the model smarter", "It is required by law"],
        answer: 1, why: "A chunk about one idea matches a question better than a whole document, and several chunks fit in the prompt." }
    ]
  },
  {
    id: "llm-prompting", area: "llm", title: "Prompting patterns and structured output", mins: 30, level: 2, light: false,
    res: { label: "Anthropic docs: prompt engineering overview", url: "https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview", src: "free" },
    aloud: "Describe three prompt techniques and what each is good for, then say how you would make a model return reliable JSON.",
    interviewQ: "Your prompt returns inconsistent output formats. List the changes you try, in order.",
    quiz: [
      { q: "What is few-shot prompting?",
        options: ["Using very short prompts", "Including a few examples of the desired input and output in the prompt", "Fine-tuning on a few documents", "Asking the model to answer in few words"],
        answer: 1, why: "Examples show the model the format and style you want more clearly than description alone." },
      { q: "What is a reliable way to get structured JSON in an app?",
        options: ["Hope the model complies", "Specify the schema, show an example, validate the output in code and retry on failure", "Use a higher temperature", "Ask in capital letters"],
        answer: 1, why: "Treat model output as untrusted input: parse and validate, and handle failures." },
      { q: "What does lowering the temperature do?",
        options: ["Makes output more random", "Makes output more deterministic and repeatable", "Makes the model faster", "Increases the context window"],
        answer: 1, why: "Lower temperature concentrates probability on the most likely tokens, though it does not guarantee identical output." }
    ]
  },
  {
    id: "llm-eval", area: "llm", title: "Evaluating LLM applications", mins: 35, level: 3, light: false,
    res: { label: "Ragas documentation: evaluation metrics", url: "https://docs.ragas.io/", src: "free" },
    aloud: "Explain how you would know whether a change to your prompt or retriever made your app better and not just different.",
    interviewQ: "How would you build an evaluation set for a customer-support chatbot, and what would you measure?",
    quiz: [
      { q: "Why keep a fixed test set of questions with known good answers?",
        options: ["It trains the model", "It lets you compare versions fairly and catch regressions", "It makes the app faster", "It replaces user feedback"],
        answer: 1, why: "Without a stable benchmark you cannot tell if a change helped." },
      { q: "In RAG evaluation, what does faithfulness (groundedness) measure?",
        options: ["Whether the answer's claims are supported by the retrieved context", "How fast the answer arrives", "How long the answer is", "Whether the tone is friendly"],
        answer: 0, why: "It checks that the answer sticks to the provided sources and does not invent facts." },
      { q: "What is a known risk of using an LLM as a judge?",
        options: ["It cannot read text", "It can be biased, for example toward longer answers, so it should be calibrated against human labels", "It always agrees with humans", "It is too slow to run"],
        answer: 1, why: "LLM judges are useful and scalable, but their scores need spot-checking against human review." }
    ]
  },
  {
    id: "llm-choose", area: "llm", title: "Fine-tuning vs RAG vs prompting", mins: 30, level: 2, light: false,
    res: { label: "Hugging Face LLM course", url: "https://huggingface.co/learn/llm-course", src: "free" },
    aloud: "Explain when you would choose prompting, RAG or fine-tuning, and what you would try first.",
    interviewQ: "A company wants a model that answers questions about its internal policies, which change monthly. Which approach, and why?",
    quiz: [
      { q: "When is RAG a better choice than fine-tuning?",
        options: ["When knowledge changes often or answers must cite sources", "When you want to change the model's writing style permanently", "When you have no documents", "When latency does not matter"],
        answer: 0, why: "RAG reads current documents at question time, so updating knowledge means updating the index, not retraining." },
      { q: "What is fine-tuning generally best for?",
        options: ["Adding frequently changing facts", "Teaching consistent style, format or behavior", "Replacing a database", "Reducing the context window"],
        answer: 1, why: "Fine-tuning shapes how the model behaves. It is a poor way to store facts that change." },
      { q: "What is usually the cheapest first step before RAG or fine-tuning?",
        options: ["Training a new model", "Improving the prompt with clear instructions and examples, and measuring the result", "Buying more GPUs", "Switching databases"],
        answer: 1, why: "Prompt changes are fast and free to test, and they tell you whether a heavier approach is even needed." }
    ]
  }
]);
