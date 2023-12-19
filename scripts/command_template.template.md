---
description: Full description of the command template "$id"
hide:
  - toc
---
# $id

<div class="tpl_table" markdown>
<div class="tpl_row $has_desc" markdown>
<div class="joined" markdown>
<div class="tpl_head title_cmd" markdown>
__Description__
</div>
<div class="tpl_cell body_cmd" markdown>
$description
</div>
</div>
</div>
<div class="tpl_row" markdown>
<div class="joined" markdown>
<div class="tpl_head title_cmd" markdown>
__Command__
</div>
<div class="tpl_cell body_cmd" markdown>
`#!bash $command $arguments`
</div>
</div>
</div>
<div class="tpl_row $has_env" markdown>
<div class="tpl_cell" markdown>
???+ info "Defined Environment"
$env
</div>
</div>
<div class="tpl_row $use_sys_env" markdown>
<div class="tpl_head" markdown>
Will be passed **all system `Environment Variables`** as well as the defined `Environment`
</div>
</div>
</div>