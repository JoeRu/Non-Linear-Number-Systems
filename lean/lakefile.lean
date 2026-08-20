import Lake
open Lake DSL

package «NonLinearNumberSystems» where
  -- the package name comes from the «...» above; an explicit `name :=` field
  -- expects a `Lean.Name`, not a `String`, and is redundant here

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.14.0"

@[default_target]
lean_lib «NonLinearNumberSystems» where
  -- add any library configuration options here
  globs := #[.andSubmodules `NonLinearNumberSystems]
