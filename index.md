---
layout: default
title: "Twinizer - Multi-Format Conversion and Analysis Tool"
description: "A comprehensive tool for converting between file formats, analyzing code, hardware schematics, and generating documentation"
---

{% include_relative README.md %}

<script type="module">    
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({
    startOnReady: true,
    theme: 'forest',
    flowchart: {
      useMaxWidth: false,
      htmlLabels: true
    }
  });
  mermaid.init(undefined, '.language-mermaid');
</script>