---
title: A Spatial Reasoning Benchmark for Multimodal Language Models

exports:
    - format: pdf
      template: arxiv_nips
date: 2026-03-04
authors:
  - name: Emily Light
    affiliations:
      - University of Rhode Island
  - name: Ethen Puls
    affiliations:
      - University of Rhode Island
  - name: Alex Garcia
    affiliations:
      - University of Rhode Island
  - name: Jack Lanoie
    affiliations:
      - University of Rhode Island
  - name: Cody Giroux
    affiliations:
      - University of Rhode Island

---
# Introduction

# Concept & Operationalization
This benchmark will have several exercises to measure LLM's ability to use common-sense spatial reasoning. We define common-sense reasoning as the ability to correctly infer relative orientation, rotation, and spatial displacement of objects under geometric transformations, using either textual descriptions alone or text grounded in visual input. This includes; mental rotation, relative positioning, directional movement inference, and transformation composition. 
* *Mental transformation* is the ability to infer an object orientation after rotation, sequential composition of transformation. This includes both single-step transformations (e.g., rotate 90° clockwise) and sequential composition of transformations (e.g., rotate 90° clockwise and then 180°). Correctly completing these types of exercises requires maintaining an internal representation of orientation and correctly updating it under rule-based operations.
* *Relative positioning* is the ability to define an object’s spatial location with respect to another object or reference point. For example, in the statement “The ball is to the left of the chair.”, the model must correctly interpret directional relationships within a shared coordinate frame. This includes reasoning about object-centered versus global reference frames and maintaining consistency when the reference object changes.
* *Directional movement* is the ability to interpret and apply movement commands, such as up, forward, clockwise, or counterclockwise. These tasks require mapping keywords to geometric operations and updating positional states accordingly. Movement reasoning may involve translating a point across a grid, following the direction of an arrow, or applying rotation to a facing object.
* *Transformation composition* is the ability to apply multiple spatial transformations sequentially to one object and identify its final state. This tests whether the models are  performing true compositional reasoning or relying on shallow pattern recognition. For example, combining rotation and translation requires maintaining intermediate state representations and applying transformation rules in order.
Including these four categories of capabilities will evaluate whether a model maintains internally consistent spatial representations that are stable across textual and visual modalities.
Our tasks for this benchmark will be split into two types of exercises; text-only spatial reasoning tasks and image + text multimodal tasks. Each task will have a standardized input-output structure, meaning that all tasks will follow a uniform prompt template. Each task will explicitly instruct the model to select a single-word answer from a predefined answer bank.
This benchmark will test models performance on these topics using various exercises. We will construct it as a controlled benchmark composed of discrete tasks across multimodal settings. Each task will evaluate a specific skill under the large umbrella of spatial reasoning.  By using this benchmark, we will evaluate how effectively large language models understand and manipulate physical space layouts, and object relationships. 

# Related Benchmarks

Other benchmarks have previously tried measuring  LLM's consistency when it comes to true spatial intelligence/awareness. A model is able to detect a car in a photo, but it often cannot truly "think" about how that car would interact within a three dimensional context. What would a car look like if it was rotated 90 degress in a 3d space or such as, "what if a person moved between rooms?" Would the model understand the objects in the old room are no longer in the person's field of view? 

Our benchmark wants to shift the focus towards active spatial reasoning, mental manipulation of objects, predict the outcomes of said movement, and then understand how those changes would affect its real-world use. Comparing to past benchmarks showcases a perspective on where models currently succeed and where our benchmark will provide a new test for artificial common sense. 

1) Mental Rotation
   Focus Benchmark: [SpatialViz-Bench (2026)](https://arxiv.org/pdf/2507.07610)
   * Importance: Asks models to perform "unseen relationship interference" on programmatically generated 3D objects. Results determined that the models were great at identifying 2D patterns but struggle when a task require a mental volume in regards to 3D manipulation. Most models defaulted to making guesses based off of 2D textures rather than building a 3D mental image.
   * Relevance: Our model intends to expand upon this by moving from abstract shapes to functional objects to see if common sense with help overcome this type of 3D cliff the model finds itself on.
     
2) Step By Step Movement
   Focus Benchmark: [StepGame (2025)](https://arxiv.org/pdf/2503.05439?)
   * Importance: Creates a story regarding an arbitrary amount of entity relations, "A is left of B, B is below C" and tests the model on the relationship between the first and last entities. The difficulty  was scaled exponentially depending on how many entities were added. Sharp decline in accuracy when a relationship exceeded 3-4 steps, showing that most models lack persistent  spatial memory. A sentence can be processed individually but it can't update a unified map mentally
   * Relevance: Our benchmark intends to test if a visual grounding (allowing the model to see the map while reading the steps) will fix this lapse in memory
   
3) Common Sense Interaction
   Focus Benchmark: [SpaCE-Eval (2025)](https://openreview.net/pdf?id=VAEkLS9VBr)
   * Importance: Used over 1000 human made diagrams to test physical common sense. Questions model on environmental interaction such as "what would these two 3D shapes look like if they were combined together." Models struggle with spatial simulation, and predicting how an action changes the possibilities in the environment
   * Relevance: Common sense-esque questions target a usability gap as to whether or not a transformation makes an object or functional. 

# Structure
The benchmark will contain two broad categories of tasks:
1. Generic Transformations, as well as and "common sense" style questions as to how transformations alter the interactivity or functionality of objects.
2. Pattern and algorithmic style questions, in an attempt to measure more complex spatial awareness and competence.

## Generic Transformations
A series of templated spatial tasks will be presented to the model, with an answer bank containing valid answers. Models will be prompted to respond with a single word from the answer bank. Scoring is binary, questions given the correct answer from the given answer bank are correct. Incorrect answers, or answers containing words from outside of the answer bank are marked incorrect. Scoring will be displayed as total correct/incorrect, as well as by tags (2-Dimensional, 3-Dimensional, transformation only, "common selse" style question, specific object transformed).
These questions will be either multi modal (image + text) or text-based, and will fit four categories:
1. 2D Spatial Transformations
2. 3D Spatial Transformations
3. 2D Spatial Transformations + Common Sense Style Question
4. 3D Spatial Transformations + Common Sense Style Question

### Sample Tasks

```{figure} /content/images/figures/prop_fig1.png
:label: fig1
:alt: A multimodal question example
:align: center

A sample multimodal question. The image, along with words in brackets, will be swapped to create a wide variety of generic questions. Tags for scoring display would be: multimodal, 2d, transformation_only, arrow

```

```{figure} /content/images/figures/prop_fig2.png
:label: fig2
:alt: A text based question example
:align: center

A sample text-based question, focusing on "common-sense" usability of objects after applying transformations to their positions. Tags for scoring display would be: 3d, text_based, common_sense, car

```

### Task Generation Strategy
Demonstrated in [](#fig1) and [](#fig2), 5-10 generic "template" questions will be designed, and then populated with values to create at least 50 questions. Large language models may be used to generate more questions, and if done, each question will be reviewed for accuracy and the answer will be answered manually by a team member.

## Algorithmic/Pattern Matching
### Sample Task
### Task Generation Strategy


