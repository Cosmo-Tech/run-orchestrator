---
hide:
  - path
  - toc
  - navigation
---
# Semantic Validator

Simple semantic validator,

Paste your orchestration file in `text` mode and it will be semantically validated

<div id="jsoneditor"></div>

<script type="module" markdown>
      import { JSONEditor, createAjvValidator } from 'https://cdn.jsdelivr.net/npm/vanilla-jsoneditor/standalone.js';

      const schema = {
--8<-- "cosmotech/orchestrator/schema/run_template_json_schema.json:3"

      const schemaDefinitions = {

      }

      const content = {
        json:
--8<-- "examples/simple.json"
,
        text: undefined
      }

      // create the editor
      const target = document.getElementById('jsoneditor')
      const editor = new JSONEditor({
        target: document.getElementById('jsoneditor'),
        props: {
          content,
          onChange: (update) => console.log('onChange', update),
          validator: createAjvValidator({ schema, schemaDefinitions })
        }
      })
    </script>

> Page made with [https://github.com/josdejong/svelte-jsoneditor](https://github.com/josdejong/svelte-jsoneditor)