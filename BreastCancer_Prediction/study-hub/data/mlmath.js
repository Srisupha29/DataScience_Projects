window.TOPICS = (window.TOPICS || []).concat([
  {
    id: "mm-vectors", area: "mlmath", title: "Vectors, dot products and cosine similarity", mins: 25, level: 1, light: true,
    res: { label: "3Blue1Brown: essence of linear algebra", url: "https://www.3blue1brown.com/topics/linear-algebra", src: "free" },
    aloud: "Explain what the dot product measures, and why cosine similarity ignores the length of the vectors.",
    interviewQ: "Two document embeddings have a dot product of 0. What does that tell you?",
    quiz: [
      { q: "What is the dot product of [1, 2] and [3, 4]?",
        options: ["10", "11", "14", "7"],
        answer: 1, why: "1×3 + 2×4 = 3 + 8 = 11." },
      { q: "The dot product of two non-zero vectors is 0. What does that mean?",
        options: ["They are parallel", "They are identical", "They are orthogonal (perpendicular)", "They both have length 1"],
        answer: 2, why: "The dot product equals |a||b|cos(angle), so it is 0 when the angle is 90 degrees." },
      { q: "What is the cosine similarity of [1, 0] and [2, 0]?",
        options: ["1", "0", "0.5", "2"],
        answer: 0, why: "They point in exactly the same direction, so the angle is 0 and cos(0) = 1. Length does not matter." }
    ]
  },
  {
    id: "mm-matrices", area: "mlmath", title: "Matrix multiplication and shapes", mins: 30, level: 2, light: false,
    res: { label: "Mathematics for Machine Learning (free book)", url: "https://mml-book.github.io/", src: "free" },
    aloud: "Say what shape (n×d)·(d×k) gives, and explain how a neural network layer is a matrix multiplication.",
    interviewQ: "A batch X is 32×100 and a layer takes 100 inputs and gives 64 outputs. What are the shapes of the weight matrix and the output?",
    quiz: [
      { q: "A 3×4 matrix is multiplied by a 4×2 matrix. What is the shape of the result?",
        options: ["3×2", "4×4", "3×4", "It is undefined"],
        answer: 0, why: "The inner dimensions (4 and 4) must match and disappear, leaving 3×2." },
      { q: "Is matrix multiplication commutative, meaning AB = BA?",
        options: ["Yes, always", "No, in general AB ≠ BA", "Yes, but only for 2×2 matrices", "Only when the matrices contain integers"],
        answer: 1, why: "Order matters. Often one of the two products is not even defined." },
      { q: "A batch of 32 examples with 100 features goes through a linear layer with 64 outputs, computed as X·W. What are the shapes of W and the output?",
        options: ["W is 64×100, output is 32×100", "W is 32×64, output is 100×64", "W is 100×32, output is 64×64", "W is 100×64, output is 32×64"],
        answer: 3, why: "(32×100)·(100×64) gives 32×64: one row of 64 outputs per example." }
    ]
  },
  {
    id: "mm-derivatives", area: "mlmath", title: "Derivatives and the chain rule", mins: 30, level: 2, light: false,
    res: { label: "3Blue1Brown: essence of calculus", url: "https://www.3blue1brown.com/topics/calculus", src: "free" },
    aloud: "Explain a derivative as 'how much the output changes per tiny change in the input', then walk through the chain rule on f(g(x)).",
    interviewQ: "The derivative of the sigmoid can be written using the sigmoid itself. What is it, and why is that handy for backpropagation?",
    quiz: [
      { q: "What is the derivative of x³?",
        options: ["x²", "3x²", "3x", "x⁴/4"],
        answer: 1, why: "Power rule: bring the exponent down and subtract one." },
      { q: "For y = f(g(x)), the chain rule says dy/dx equals:",
        options: ["f'(x) · g'(x)", "f'(g(x)) · g'(x)", "f(g'(x))", "f'(x) + g'(x)"],
        answer: 1, why: "Differentiate the outer function at the inner value, then multiply by the derivative of the inner function." },
      { q: "What is the derivative of (2x + 1)²?",
        options: ["2(2x + 1)", "2x + 1", "4(2x + 1)", "2(2x)"],
        answer: 2, why: "Outer: 2(2x + 1). Inner: 2. Multiply to get 4(2x + 1)." }
    ]
  },
  {
    id: "mm-gradients", area: "mlmath", title: "Gradients and why gradient descent works", mins: 30, level: 2, light: false,
    res: { label: "3Blue1Brown: gradient descent", url: "https://www.3blue1brown.com/lessons/gradient-descent", src: "free" },
    aloud: "Explain what a gradient is, why it points uphill, and why we subtract it to reduce the loss.",
    interviewQ: "For L(w) = (w − 3)², what is the gradient at w = 5, and which way does gradient descent move w?",
    quiz: [
      { q: "What does the gradient of a function point toward?",
        options: ["The steepest decrease", "The steepest increase", "The minimum", "A direction of no change"],
        answer: 1, why: "That is why gradient descent moves in the opposite direction." },
      { q: "For L(w) = (w − 3)², what is the gradient at w = 5?",
        options: ["2", "10", "4", "−4"],
        answer: 2, why: "dL/dw = 2(w − 3), which is 2(5 − 3) = 4." },
      { q: "One gradient descent step from w = 5 with learning rate 0.25 on L(w) = (w − 3)². What is the new w?",
        options: ["4", "4.75", "6", "3"],
        answer: 0, why: "w_new = 5 − 0.25 × 4 = 4, closer to the minimum at 3." }
    ]
  },
  {
    id: "mm-eigen", area: "mlmath", title: "Eigenvalues and eigenvectors", mins: 35, level: 3, light: false,
    res: { label: "3Blue1Brown: eigenvectors and eigenvalues", url: "https://www.3blue1brown.com/lessons/eigenvalues", src: "free" },
    aloud: "Explain an eigenvector as a direction that a matrix only stretches, and say what the eigenvalue tells you.",
    interviewQ: "How are the eigenvectors of the covariance matrix related to PCA?",
    quiz: [
      { q: "If Av = λv for a non-zero vector v, what is v?",
        options: ["An eigenvector of A: a direction that A only scales, by the factor λ", "The inverse of A", "A row of A", "Always the zero vector"],
        answer: 0, why: "A does not rotate v. It only stretches or flips it by λ." },
      { q: "What are the eigenvalues of the diagonal matrix diag(3, 1)?",
        options: ["4 and 0", "3 and 3", "1 and 1", "3 and 1"],
        answer: 3, why: "For a diagonal matrix the eigenvalues are the diagonal entries." },
      { q: "In PCA, the eigenvector of the covariance matrix with the largest eigenvalue points:",
        options: ["Along the direction of least variance", "At the data mean", "Along the direction of greatest variance", "Along the target"],
        answer: 2, why: "The eigenvalue equals the variance of the data along that direction." }
    ]
  },
  {
    id: "mm-entropy", area: "mlmath", title: "Entropy, cross-entropy and KL divergence", mins: 35, level: 3, light: false,
    res: { label: "Wikipedia: cross-entropy", url: "https://en.wikipedia.org/wiki/Cross-entropy", src: "free" },
    aloud: "Explain entropy as average surprise, and say how cross-entropy loss relates to the true and predicted distributions.",
    interviewQ: "Why is cross-entropy the standard loss for classification instead of mean squared error?",
    quiz: [
      { q: "What is the entropy of a fair coin flip, in bits?",
        options: ["0", "0.5", "1", "2"],
        answer: 2, why: "Two equally likely outcomes need exactly 1 bit to describe." },
      { q: "A classifier gives probability 0.9 to the true class on one example and 0.1 on another. Which example has the larger cross-entropy loss (−log p)?",
        options: ["The example with 0.9", "The example with 0.1", "They are equal", "Both are zero"],
        answer: 1, why: "−log(0.1) is much larger than −log(0.9). Confident wrong answers are punished hard." },
      { q: "Which statement about KL divergence D(P‖Q) is correct?",
        options: ["It is symmetric", "It is always negative", "It is the same as cross-entropy", "It is zero only when P and Q are identical, and it is not symmetric"],
        answer: 3, why: "KL is non-negative and asymmetric. Cross-entropy equals entropy plus KL." }
    ]
  },
  {
    id: "mm-softmax", area: "mlmath", title: "Sigmoid, softmax and log-odds", mins: 25, level: 2, light: true,
    res: { label: "Wikipedia: softmax function", url: "https://en.wikipedia.org/wiki/Softmax_function", src: "free" },
    aloud: "Explain how the sigmoid squashes any number into (0, 1), how softmax extends that to many classes, and what log-odds are.",
    interviewQ: "A logistic regression coefficient is 0.7. What does that mean for the odds of the positive class?",
    quiz: [
      { q: "What is softmax of the scores [1, 1, 1]?",
        options: ["[1, 1, 1]", "[1/3, 1/3, 1/3]", "[0, 0, 1]", "[0.5, 0.25, 0.25]"],
        answer: 1, why: "Equal scores give equal probabilities, and they must sum to 1." },
      { q: "What is sigmoid(0)?",
        options: ["0", "1", "−1", "0.5"],
        answer: 3, why: "1 / (1 + e⁰) = 1 / 2." },
      { q: "In logistic regression a feature has coefficient 0.7. Increasing that feature by 1 multiplies the odds of the positive class by about:",
        options: ["0.7", "1.7", "e^0.7, roughly 2.0", "0.5"],
        answer: 2, why: "The coefficient is a change in log-odds, so the odds change by a factor of e^0.7 ≈ 2.01." }
    ]
  },
  {
    id: "mm-deep-backprop", area: "mlmath", deep: true, title: "Deep dive: backpropagation by hand", mins: 80, level: 3, light: false,
    res: { label: "Dive into Deep Learning: forward and backward propagation", url: "https://d2l.ai/chapter_multilayer-perceptrons/backprop.html", src: "free" },
    aloud: "Take a tiny network with one hidden unit, then walk the chain rule backward from the loss to the first weight, writing every number.",
    interviewQ: "Why does backpropagation run backward, and why is it much cheaper than computing each weight's derivative separately?",
    quiz: [
      { q: "A tiny network has h = w1·x and ŷ = w2·h, with x = 2, w1 = 3, w2 = 0.5 and target y = 4. The loss is L = ½(ŷ − y)². What is L?",
        options: ["0.5", "1", "2", "4.5"],
        answer: 0, why: "h = 6, ŷ = 3, so L = ½(3 − 4)² = 0.5." },
      { q: "Same network (x = 2, w1 = 3, w2 = 0.5, y = 4, L = ½(ŷ − y)²). What is ∂L/∂w2?",
        options: ["−1", "−3", "6", "−6"],
        answer: 3, why: "∂L/∂w2 = (ŷ − y)·h = (−1)(6) = −6." },
      { q: "Same network. What is ∂L/∂w1?",
        options: ["−6", "−0.5", "−1", "−2"],
        answer: 2, why: "Chain rule: (ŷ − y)·w2·x = (−1)(0.5)(2) = −1." },
      { q: "Why does backpropagation work backward from the loss?",
        options: ["Forward computation is impossible", "It avoids using the chain rule", "Each layer's gradient is built from the gradient already computed for the layer after it, so everything is obtained in one backward pass", "It makes the loss smaller by itself"],
        answer: 2, why: "Reusing the downstream gradient is what makes the cost about the same as one extra forward pass." },
      { q: "A sigmoid unit saturates, with an output near 0 or 1. What happens to the gradient passing through it?",
        options: ["It becomes very large", "It becomes close to zero, which can cause vanishing gradients in deep networks", "It always becomes negative", "Nothing changes"],
        answer: 1, why: "The sigmoid's derivative is σ(1 − σ), which is close to 0 when σ is near 0 or 1." }
    ]
  },
  {
    id: "mm-deep-svd", area: "mlmath", deep: true, title: "Deep dive: SVD and PCA from the math", mins: 75, level: 3, light: false,
    res: { label: "Wikipedia: singular value decomposition", url: "https://en.wikipedia.org/wiki/Singular_value_decomposition", src: "free" },
    aloud: "State A = UΣVᵀ, explain what each part means, and show how PCA on centered data connects to the SVD.",
    interviewQ: "How do you use the SVD to build the best rank-k approximation of a matrix, and how does that help compress an image or an embedding table?",
    quiz: [
      { q: "In A = UΣVᵀ, what is Σ?",
        options: ["A full dense matrix", "The inverse of A", "A diagonal matrix of non-negative singular values, usually sorted from largest to smallest", "An orthogonal matrix"],
        answer: 2, why: "The singular values say how much A stretches along each pair of directions." },
      { q: "What are U and V in the SVD?",
        options: ["Diagonal matrices", "Orthogonal matrices (their columns are orthonormal)", "Random matrices", "Singular matrices"],
        answer: 1, why: "They are rotations or reflections, so they preserve lengths and angles." },
      { q: "How do you get the best rank-k approximation of A (in Frobenius norm)?",
        options: ["Keep the k smallest singular values", "Randomly drop k columns", "Average U and V", "Keep the k largest singular values and their vectors (Eckart–Young theorem)"],
        answer: 3, why: "The largest singular values carry the most of the matrix's 'energy'." },
      { q: "For a centered data matrix X (rows are samples), the principal directions are:",
        options: ["The columns of U", "The right singular vectors (the columns of V)", "The diagonal of Σ", "The rows of X"],
        answer: 1, why: "XᵀX = VΣ²Vᵀ, so V holds the eigenvectors of the covariance matrix." },
      { q: "A singular value σ of centered X (n samples) corresponds to variance along that component of:",
        options: ["σ", "1/σ", "σ² / (n − 1)", "σ / n²"],
        answer: 2, why: "The covariance matrix is XᵀX / (n − 1) = V(Σ² / (n − 1))Vᵀ." }
    ]
  },
  {
    id: "mm-deep-mle-loss", area: "mlmath", deep: true, title: "Deep dive: from likelihood to loss functions", mins: 70, level: 3, light: false,
    res: { label: "Wikipedia: maximum likelihood estimation", url: "https://en.wikipedia.org/wiki/Maximum_likelihood_estimation", src: "free" },
    aloud: "Show that maximizing likelihood under Gaussian noise gives mean squared error, and under a Bernoulli model gives log loss.",
    interviewQ: "Which assumption about the noise is hidden inside using MSE, and what would you use if the noise has heavy tails?",
    quiz: [
      { q: "Maximum likelihood estimation chooses the parameters that:",
        options: ["Minimize the prior", "Maximize the probability of the observed data given the parameters", "Maximize the number of parameters", "Match the mean of the labels"],
        answer: 1, why: "It asks which parameter values make the data we actually saw most probable." },
      { q: "Why maximize the log-likelihood instead of the likelihood?",
        options: ["It changes the optimum", "It removes the need for data", "It makes probabilities larger than 1", "The log turns a product over independent examples into a sum, which is easier and numerically stabler, and the maximizer does not change"],
        answer: 3, why: "Log is increasing, so the best parameters are the same, but sums are far easier to work with." },
      { q: "Assume y = wᵀx + ε with Gaussian noise of fixed variance. Maximum likelihood for w is equivalent to minimizing:",
        options: ["Absolute error", "Hinge loss", "The sum of squared errors", "Log loss"],
        answer: 2, why: "The Gaussian log-density contains −(y − wᵀx)², so maximizing it means minimizing squared error." },
      { q: "Binary labels with p = σ(wᵀx) are modelled as Bernoulli. The negative log-likelihood is:",
        options: ["Mean squared error", "Log loss (binary cross-entropy)", "Hinge loss", "Huber loss"],
        answer: 1, why: "−[y log p + (1 − y) log(1 − p)] is exactly the log loss." },
      { q: "If you assume Laplace-distributed noise instead of Gaussian, maximum likelihood leads you to minimize:",
        options: ["Squared error", "Log loss", "Absolute error (L1), which is less sensitive to outliers", "Zero-one loss"],
        answer: 2, why: "The Laplace density contains |y − wᵀx|, and heavy tails mean outliers are less surprising." }
    ]
  }
]);
