/-
  NonLinearNumberSystems
  ======================
  Root module. Importing this gives the whole development.

  The `lean_lib` glob in `lakefile.lean` is `.andSubmodules`, which means the
  root module itself plus every submodule — so this file must exist for the
  build to resolve.
-/

import NonLinearNumberSystems.Basic
import NonLinearNumberSystems.Numeration
import NonLinearNumberSystems.Completeness
import NonLinearNumberSystems.Bounds
import NonLinearNumberSystems.Zeckendorf
import NonLinearNumberSystems.Theorems
