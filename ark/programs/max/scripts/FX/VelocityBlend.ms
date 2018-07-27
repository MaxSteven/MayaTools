fn animTime t =
(
  return int(t + (0 - animationRange.start + 1))
)
fn samePos p1 p2 =
(
  if ((close_enough p1.x p2.x 100) and (close_enough p1.y p2.y 100) and (close_enough p1.z p2.z 100)) then
    return true
  else
    return false
)
c = getCurrentSelection()
matOn = #()

for i = 1 to c.count do
(
  matKeyed = false
  for t = animationRange.start to animationRange.end while (not matKeyed) do
  (
    posOne = at time t c[i].pos
    posTwo = at time (t + 1) c[i].pos
    if (not(samePos posOne posTwo)) then
    (
      m1 = c[i].material.map1
      m2 = c[i].material.map2
      
      c[i].material = blend map1:m1 map2:m2
      with animate on
      (
        at time (t) c[i].material.mixAmount = 0
        at time (t+1) c[i].material.mixAmount = 100
      )
      matKeyed = true
    )
  )
)
