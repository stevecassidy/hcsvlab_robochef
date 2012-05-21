def foo(bar, i):
  if i == 0:
    return 1
  else:
    return bar
    
def bar(i):
  return foo(bar,i)