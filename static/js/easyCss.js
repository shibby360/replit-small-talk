var globals = {}
globals.CssSize = function(size, unit) {
  if(unit === undefined) {
    unit = 'px'
  }
  this.measure = size.toString() + unit
  this.toString = function() {
    return this.measure
  }
}
globals.addCssToSingleElement = function(el, css) {
  var ogvals = {}
  for(var i in css) {
    ogvals[i] = getComputedStyle(el)[i]
    el.style[i] = css[i]
  }
}
globals.addCssByQuery = function(queries, css) {
  var els = document.querySelectorAll(queries)
  for(var i in css) {
    for(var j in Array.from(els)) {
      els[j].style[i] = css[i]
    }
  }
}
globals.cs = globals.CssSize
globals.gridTempSize = function(size, unit, amount) {
  if(amount === undefined) {
    amount = unit
    unit = 'px'
  }
  return (new CssSize(size, unit).measure+' ').repeat(amount)
}
globals.grid = function(container, children, options) {
  container.style.display = 'grid'
  var rowsizes = []
  var colsizes = []
  for(var j in children) {
    var i = children[j]
    i.el.style.gridRowStart = i.row+1
    i.el.style.gridColumnStart = i.column+1
    i.el.style.gridRowEnd = i.rowspan ? i.rowspan+i.row+1 : ''
    i.el.style.gridColumnEnd = i.columnspan ? i.columnspan+i.column+1 : ''
    rowsizes.push(i.row+1+Number(Boolean(i.rowspan)))
    colsizes.push(i.column+1+Number(Boolean(i.columnspan)))
  }
  if(options) {
    container.style.gridTemplateRows = options.rowSizes
    container.style.gridTemplateColumns = options.columnSizes
    if(options.cellSize) {
      container.style.gridTemplateRows = (options.cellSize.measure+' ').repeat(Math.max(...rowsizes))
      container.style.gridTemplateColumns = (options.cellSize.measure+' ').repeat(Math.max(...colsizes))
    }
  }
}
globals.flex = function(container, children, options) {
  container.style.display = 'flex'
  if(options) {
    container.style.flexDirection = options.direction
    container.style.flexWrap = options.wrap
    var valstojusts = {middle:'center', start:'flex-start', end:'flex-end', around:'space-around', between:'space-between'}
    container.style.justifyContent = valstojusts[options.justify]
    var valstoaligns = {middle:'center', top:'flex-start', bottom:'flex-end', stretch:'stretch', baseline:'baseline', around:'space-around', between:'space-between'}
    container.style.alignItems = valstoaligns[options.itemAlign]
    container.style.alignContent = valstoaligns[options.contentAlign]
  }
  for(var j in children) {
    var i = children[j]
    i.el.style.order = i.order
    i.el.style.flexGrow = i.grow
    i.el.style.flexShrink = i.shrink
    if(i.length) {
      i.el.style.flexBasis = i.length.measure
    }
    var valstoaligns = {middle:'center', top:'flex-start', bottom:'flex-end', stretch:'stretch', baseline:'baseline', around:'space-around', between:'space-between'}
    i.el.style.alignSelf = valstoaligns[i.align]
  }
}
globals.place = function(el, x, y) {
  el.style.position = 'absolute'
  el.style.top = y.measure
  el.style.left = x.measure
}
globals.squared = function(el, dimension) {
  el.style.width = dimension.measure
  el.style.height = dimension.measure
}
globals.media = function(query, onmatch, onelse) {
  var y = window.matchMedia(query)
  var x = function(xx) {
    if(xx.matches) {
      onmatch()
    } else {
      onelse()
    }
  }
  x(y)
  y.addListener(x)
}
globals.fillScreen = function(el, multiplier=1) {
  el.style.height = '100vh'
  el.style.width = '100vw'
}
globals.invertTextColors = function(el=document.body) {
  var style = getComputedStyle(el)
  /**color */
  var justrgb = style.color.replace('rgb(', '').replace(')', '').split(',')
  el.style.color = `rgb(${255-justrgb[0]}, ${255-justrgb[1]}, ${255-justrgb[2]})`
  /**backgroundColor */
  var justrgb2 = style.backgroundColor.replace('rgb(', '').replace(')', '').split(',')
  el.style.backgroundColor = `rgb(${255-justrgb2[0]}, ${255-justrgb2[1]}, ${255-justrgb2[2]})`
}
function easyCss(varname) {
  if(varname === undefined) {
    varname = window
  }
  Object.assign(varname, globals)
  globals = undefined
}