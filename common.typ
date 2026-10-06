// common.typ

#let respuesta(texto) = {
  text(
    rgb("#5983b0"),
    weight: "bold",
    [#texto]
  )
}

#let empieza_con_todos(parrafo) = {
  let partes = ()
  for hijo in parrafo {
    let t = hijo.at("text", default: none)
    if t != none and type(t) == str {
      partes.push(t)
      if partes.len() >= 3 { break }
    }
  }
  partes.join("").starts-with("Todos:")
}

// El aspecto de cada respuesta lo pone respuesta_fn. En papel es respuesta()
// (text(fill:) + weight:); en la web es una variante que emite una clase,
// porque la exportación a HTML descarta el fill y el weight y el párrafo sale
// pelado. Se pasa desde la plantilla en vez de decidirlo aquí mirando el
// destino con target() a propósito: target() y el módulo html sólo existen si
// se compila con --features html, y sin esa opción nombrar html es un error de
// compilación («cannot access variable `html` because the `html` feature is not
// enabled»). Este archivo también lo compilan las plantillas de papel, que no
// pasan esa opción, así que la diferencia por destino tiene que elegirse desde
// la plantilla. La agrupación por párrafos, que es lo que se repetía, sí es
// común.
#let con_respuestas(contenido, respuesta_fn: respuesta) = {
  if contenido == none { return none }
  let hijos = if contenido.has("children") { contenido.children } else { (contenido,) }
  let parrafos = ()
  let actual = ()
  for hijo in hijos {
    if hijo.func() == parbreak {
      if actual.len() > 0 { parrafos.push(actual) }
      actual = ()
    } else {
      actual.push(hijo)
    }
  }
  if actual.len() > 0 { parrafos.push(actual) }

  let salida = ()
  for i in range(parrafos.len()) {
    let parrafo = parrafos.at(i)
    let cuerpo = parrafo.join()
    if i > 0 { salida.push(parbreak()) }
    if empieza_con_todos(parrafo) {
      salida.push(respuesta_fn(cuerpo))
    } else {
      salida.push(cuerpo)
    }
  }
  salida.join()
}

#let canto(contenido) = {
  if contenido == none { return none }
  let literal(t) = t.replace("_", "\\_").replace("{", "\\{").replace("}", "\\}")
  let estrofas = ()
  let actual = ()
  for linea in contenido.split("\n") {
    if linea.trim() == "" {
      if actual.len() > 0 { estrofas.push(actual) }
      actual = ()
    } else {
      actual.push(linea.trim())
    }
  }
  if actual.len() > 0 { estrofas.push(actual) }
  if estrofas.len() == 0 { return none }

  let verso_de(lineas) = {
    let r = ()
    for i in range(lineas.len()) {
      if i > 0 { r.push(linebreak()) }
      r.push(eval(literal(lineas.at(i)), mode: "markup"))
    }
    r.join()
  }

  let salida = ()
  for i in range(estrofas.len()) {
    let lineas = estrofas.at(i)
    if i == 0 {
      salida.push(text(eval(literal(lineas.at(0)), mode: "markup"), weight: "bold"))
      let resto = lineas.slice(1)
      if resto.len() > 0 {
        salida.push(parbreak())
        salida.push(verso_de(resto))
      }
    } else {
      salida.push(parbreak())
      salida.push(verso_de(lineas))
    }
  }

  block(
    salida.join(),
    width: 100%,
    fill: rgb("#eeeeee"),
    inset: (x: 0.7em, y: 0.5em),
    radius: 2pt,
    breakable: true,
  )
}
