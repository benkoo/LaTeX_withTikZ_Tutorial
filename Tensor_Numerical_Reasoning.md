# Abstract

We propose a novel synthesis of Petri Nets and tensor algebra, arguing that Petri Nets can leverage the mathematical formalism of tensors to represent topologically related operands and their interactions. Drawing on David Spivak’s theory of polynomial functors, we introduce the concept of a Tensorized Petri Net, where each element can act simultaneously as an operand and an operator. We illustrate this framework using digit-wise arithmetic, showing how it enables compositional, interpretable, and parallelizable symbolic computation.

# 1. Introduction

Petri Nets are a foundational tool for modeling distributed and concurrent systems, providing a graphical and mathematical language for representing state, transitions, and resource flow. Traditionally, Petri Nets are used to model discrete events and token flows, but recent advances in neural-symbolic computation and category theory suggest new ways to enrich their expressive power.

In this work, we argue that Petri Nets can be “tensorized”—that is, their places, transitions, and token flows can be represented and manipulated using tensor algebra. This enables the explicit modeling of topological relationships among operands, such as those found in digit-wise arithmetic or spatially structured data. Furthermore, by leveraging David Spivak’s ideas on polynomial functors, we can treat every element in the net as both an operand and an operator, capturing higher-order compositionality and self-similarity.

# 2. Related Work

## 2.1 Petri Nets and Tensor Algebra

Petri Nets have been extended in various ways to model complex systems, but their integration with tensor algebra is relatively unexplored. Tensors provide a natural language for encoding multidimensional relationships and parallel computations, making them ideal for representing the state and evolution of Petri Nets with topological structure.

## 2.2 Polynomial Functors and Compositionality

David Spivak’s work on polynomial functors provides a categorical framework for modeling data types and processes as compositional, tree-like structures. This perspective aligns naturally with Petri Nets, where transitions can be seen as functorial operations on collections of tokens, and places as objects in a category.

## 2.3 Digit-wise Arithmetic and Neural-Symbolic Systems

Digit-wise arithmetic is a canonical example of a computation that is both highly structured and parallelizable. Neural-symbolic systems have struggled to capture such computations in a transparent and generalizable way. By modeling digit-wise arithmetic as a tensorized Petri Net, we can make explicit the flow of information and the compositional structure of the computation.

# 3. Methodology: Tensorized Petri Nets via Polynomial Functors

## 3.1 Tensor Representation of Petri Nets

- **Places as Tensor Indices:** Each place in a Petri Net corresponds to an index in a tensor, representing a position (e.g., a digit in a number, or a cell in a grid).
- **Tokens as Tensor Entries:** The state of the net is encoded as a tensor, with entries indicating the presence or value of tokens at each place.
- **Transitions as Tensor Operations:** Transitions correspond to multilinear maps or contractions, updating the tensor state according to the net’s rules.

## 3.2 Polynomial Functors for Compositionality

- **Elements as Operators and Operands:** Inspired by polynomial functors, each element (place or transition) can act as both an operand (receiving tokens) and an operator (transforming tokens).
- **Functorial Structure:** The wiring of the Petri Net encodes a functorial mapping from input tensors (operands) to output tensors (results), supporting modular and hierarchical composition.

## 3.3 Example: Digit-wise Arithmetic

- **Digit Positions as Places:** Each digit position in a number is a place in the Petri Net.
- **Carry and Sum as Transitions:** Transitions implement digit-wise addition, carry propagation, and modular reduction, all as tensor operations.
- **Topological Relationships:** The tensor structure captures the adjacency of digits and the flow of carries, enabling parallel and interpretable computation.

# 4. Results and Discussion

The Tensorized Petri Net formalism offers several advantages:

- **Parallelism:** Tensor operations enable efficient, parallel updates of the Petri Net state, mirroring the inherent concurrency of the net.
- **Compositionality:** Polynomial functors provide a principled way to compose and decompose Petri Net modules, supporting scalable and reusable designs.
- **Interpretability:** The explicit representation of operands, operators, and their topological relationships makes the computation transparent and analyzable.
- **Expressiveness:** This framework generalizes naturally to other structured computations, such as cellular automata, graph algorithms, and symbolic reasoning tasks.

# 5. Conclusion and Future Work

We have introduced a new perspective on Petri Nets, showing how tensor algebra and polynomial functors can be used to model topologically structured, compositional computations. The Tensorized Petri Net formalism unifies symbolic and neural approaches, enabling efficient, interpretable, and modular computation. Future work will explore applications to neural-symbolic integration, automated reasoning, and the design of new computational architectures for arithmetic and beyond.

# References

*References to foundational Petri Net literature, tensor algebra, polynomial functors, and neural-symbolic computation should be included here.*