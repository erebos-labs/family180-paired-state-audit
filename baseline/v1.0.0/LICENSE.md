# License and attribution

## Newly written audit material

The new checker, fixture generator, tests, literal fixtures, certificates and
accompanying audit text in this handoff are supplied under the MIT License
below. This licensing statement is not authorization to publish the research or
to claim a new theorem. No external release has been made.

MIT License

Copyright (c) 2026 Erebos Labs audit contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

## Inherited mathematics and source references

The paired-state definitions, disk identity, involution, circulation argument,
and cycle-product mechanism are inherited from the OpenAI paper and its cited
literature. The unrestricted proof and Lean implementation are not contributions
of this handoff. Source pointers and audit scope are in SOURCE_AUDIT.md.

The pinned openai/math repository's LICENSE identifies Apache License 2.0.
Its Git blob is `261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64`.
No upstream source files are bundled verbatim. An optional pinned downloader
retrieves that license alongside the referenced upstream files; such retrieved
files retain their upstream terms, not the MIT license above.

The examined cjnott1999/barnette-conjecture README explicitly states that no
license has yet been chosen and default copyright applies. None of its code is
included, adapted into the checker, or relicensed. Its exact C6 arithmetic and
forest-construction work are credited in the source audit. It was read for
prior-work comparison, not used as an executable dependency.

The running Python standard library is an external system dependency and is not
redistributed in this package. No fonts, solver binaries, or third-party
packages are included.
