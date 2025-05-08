# Introduction

We propose a novel synthesis of Petri Nets and tensor algebra, arguing that Petri Nets can leverage the mathematical formalism of tensors to represent topologically related operands and their interactions. Drawing on David Spivak’s theory of polynomial functors, we introduce the concept of a Tensorized Petri Net, where each element can act simultaneously as an operand and an operator. We illustrate this framework using digit-wise arithmetic, showing how it enables compositional, interpretable, and parallelizable symbolic computation.

Petri Nets are a foundational tool for modeling distributed and concurrent systems, providing a graphical and mathematical language for representing state, transitions, and resource flow. Traditionally, Petri Nets are used to model discrete events and token flows, but recent advances in neural-symbolic computation and category theory suggest new ways to enrich their expressive power.

In this work, we argue that Petri Nets can be “tensorized”—that is, their places, transitions, and token flows can be represented and manipulated using tensor algebra. Tensors, as multi-dimensional arrays, provide a powerful language for encoding the state of complex systems, capturing not only the presence of tokens but also their relationships and interactions across multiple dimensions. By mapping Petri Net components to tensor indices and operations, we can efficiently model the evolution of distributed systems, exploit parallel computation, and reveal underlying topological structures. This approach is particularly advantageous for systems where locality, adjacency, or compositionality play a central role, such as in digit-wise arithmetic or spatially structured processes.

Furthermore, by leveraging David Spivak’s ideas on polynomial functors, we can treat every element in the net as both an operand and an operator, capturing higher-order compositionality and self-similarity. This categorical perspective allows us to formalize the ways in which Petri Nets and tensors interact, supporting modular design and scalable reasoning.

The main components of Petri Nets include:
- Places (represented as circles)
- Transitions (represented as rectangles)
- Arcs (directed edges connecting places to transitions or transitions to places)
- Tokens (represented as dots within places)

In this paper, we explore the application of Petri Nets to model [specific system or process], with a focus on [specific aspect or property].

**Our contributions include:**
- **Contribution 1:** A novel approach to modeling concurrent processes using Petri Nets.
- **Contribution 2:** Analysis of deadlock properties in the context of resource allocation.
- **Contribution 3:** Implementation and evaluation of the proposed model using simulation.

The remainder of this paper is organized as follows: Section 2 provides background information and related work. Section 3 describes our methodology and the proposed Petri Net model. Section 4 presents the results and analysis. Finally, Section 5 concludes the paper and discusses future work.

# Background and Related Work

## Petri Net Fundamentals

Formally, a Petri Net is a tuple (P, T, F, M₀) where:
- P is a finite set of places
- T is a finite set of transitions
- F ⊆ (P × T) ∪ (T × P) is a set of arcs
- M₀: P → ℕ is the initial marking

The dynamics of Petri Nets are governed by the firing of transitions. A transition t is enabled if each input place p has at least as many tokens as the weight of the arc from p to t. When a transition fires, it consumes tokens from its input places and produces tokens in its output places according to the weights of the corresponding arcs.

### Types of Petri Nets

Several extensions to the basic Petri Net model have been proposed to enhance its modeling power:
- **Colored Petri Nets:** Extend the basic model by allowing tokens to have data values (colors).
- **Timed Petri Nets:** Incorporate time into the model, allowing for the analysis of temporal properties.
- **Stochastic Petri Nets:** Introduce probabilistic elements to model random behavior.
- **Hierarchical Petri Nets:** Allow for the decomposition of complex models into simpler submodels.

### Applications of Petri Nets

Petri Nets have been applied to various domains, including:
- **Workflow Management:** Modeling and analyzing business processes.
- **Manufacturing Systems:** Modeling production lines and resource allocation.
- **Communication Protocols:** Analyzing the behavior of network protocols.
- **Software Design:** Modeling concurrent and distributed software systems.

## Related Work

Petri Nets have been extended in various ways to model complex systems, but their integration with tensor algebra is relatively unexplored. Tensors provide a natural language for encoding multidimensional relationships and parallel computations, making them ideal for representing the state and evolution of Petri Nets with topological structure.

David Spivak’s work on polynomial functors provides a categorical framework for modeling data types and processes as compositional, tree-like structures. This perspective aligns naturally with Petri Nets, where transitions can be seen as functorial operations on collections of tokens, and places as objects in a category.

Digit-wise arithmetic is a canonical example of a computation that is both highly structured and parallelizable. Neural-symbolic systems have struggled to capture such computations in a transparent and generalizable way. By modeling digit-wise arithmetic as a tensorized Petri Net, we can make explicit the flow of information and the compositional structure of the computation.

# Methodology

## Tensorized Petri Nets via Polynomial Functors

### Tensor Representation of Petri Nets

- **Places as Tensor Indices:** Each place in a Petri Net corresponds to an index in a tensor, representing a position (e.g., a digit in a number, or a cell in a grid).
- **Tokens as Tensor Entries:** The state of the net is encoded as a tensor, with entries indicating the presence or value of tokens at each place.
- **Transitions as Tensor Operations:** Transitions correspond to multilinear maps or contractions, updating the tensor state according to the net’s rules.

### Polynomial Functors for Compositionality

- **Elements as Operators and Operands:** Inspired by polynomial functors, each element (place or transition) can act as both an operand (receiving tokens) and an operator (transforming tokens).
- **Functorial Structure:** The wiring of the Petri Net encodes a functorial mapping from input tensors (operands) to output tensors (results), supporting modular and hierarchical composition.

### Example: Digit-wise Arithmetic

- **Digit Positions as Places:** Each digit position in a number is a place in the Petri Net.
- **Carry and Sum as Transitions:** Transitions implement digit-wise addition, carry propagation, and modular reduction, all as tensor operations.
- **Topological Relationships:** The tensor structure captures the adjacency of digits and the flow of carries, enabling parallel and interpretable computation.

# Results and Discussion

The Tensorized Petri Net formalism offers several advantages:

- **Parallelism:** Tensor operations enable efficient, parallel updates of the Petri Net state, mirroring the inherent concurrency of the net.
- **Compositionality:** Polynomial functors provide a principled way to compose and decompose Petri Net modules, supporting scalable and reusable designs.
- **Interpretability:** The explicit representation of operands, operators, and their topological relationships makes the computation transparent and analyzable.
- **Expressiveness:** This framework generalizes naturally to other structured computations, such as cellular automata, graph algorithms, and symbolic reasoning tasks.

# Conclusion and Future Work

We have introduced a new perspective on Petri Nets, showing how tensor algebra and polynomial functors can be used to model topologically structured, compositional computations. The Tensorized Petri Net formalism unifies symbolic and neural approaches, enabling efficient, interpretable, and modular computation. Future work will explore applications to neural-symbolic integration, automated reasoning, and the design of new computational architectures for arithmetic and beyond.



