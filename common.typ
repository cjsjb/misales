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

#let con_respuestas(contenido) = {
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
      salida.push(respuesta(cuerpo))
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
