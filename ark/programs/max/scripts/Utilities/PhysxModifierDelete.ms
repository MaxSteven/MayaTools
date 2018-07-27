for o in objects do
(
  for m = 1 to o.modifiers.count do
  (
    if (classof o.modifiers[m] == PhysXModRB) then
    (
      print o.name
      deleteModifier o m
    )
  )
)