Changelog
#########

Release notes for d3blocks. Earlier releases are listed on the GitHub releases page:
https://github.com/d3blocks/d3blocks/releases


2.3.0 (unreleased)
******************

New blocks
==========

* ``d3.sequence()``: sequence diagrams from a Mermaid ``sequenceDiagram`` or a DataFrame of
  messages (participants and actors, calls and replies, ``rect`` regions, message variants).
* ``d3.erd()``: entity-relationship diagrams from a Mermaid ``erDiagram`` or a DataFrame of
  relationships (PK/FK/UK columns, crow's-foot cardinality, an all/keys/none columns toggle).

Flowgraph
=========

* Reads Mermaid ``stateDiagram`` / ``stateDiagram-v2``: start/end dots, labelled transitions,
  notes as tooltips, ``classDef`` colours and ``direction``.
* Flowgraph: links to and from subgraphs (Mermaid and DataFrame ``groups=``), drawn to the group
  box with dagre and ELK.
* Mermaid ``linkStyle``: edge colour and dashes.

All diagram blocks (flowgraph, sequence, erd)
==============================================

* Captioned walkthrough (``steps``): a caption bar with Prev / Play / Next, keyboard control and a
  camera that follows each step.
* ``dark_mode='auto'``: follows the operating system theme until the theme button is used.
* One rule for every Mermaid reader: each statement is understood, ignored (comments, init
  directives, ``accTitle`` / ``accDescr``) or raises a ``ValueError`` naming its line.

Behaviour changes
=================

* Flowgraph: a name passed in ``groups=`` that has member nodes and is used as an edge end, with no
  ``nodes=`` entry, is now a group endpoint instead of a node.
* Flowgraph: Mermaid flowchart statements that do not parse, ``click`` and a ``direction`` inside a
  subgraph now raise a ``ValueError`` instead of being skipped with a warning.
* Flowgraph: ``dark_mode`` accepts only ``True``, ``False`` or ``'auto'``.
